from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.db import mongodb as mongo
from app.models.scenarios import Scenario, ScenarioResponse, ScenarioList
from app.schemas.scenario import ScenarioCreate, ScenarioResponse as RespSchema, ScenarioUpdate, ScenarioSimulationResult
from app.optimizer.data_adapter import load_scenario_data
from app.optimizer.train_dispatch_optimizer import TrainDispatchOptimizer
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=ScenarioList)
async def list_scenarios(skip: int = 0, limit: int = 100):
    total = await mongo.scenarios_collection.count_documents({})
    cursor = mongo.scenarios_collection.find({}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return ScenarioList(scenarios=[ScenarioResponse.from_mongo(d) for d in docs], total=total)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str):
    doc = await mongo.scenarios_collection.find_one({"_id": scenario_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return ScenarioResponse.from_mongo(doc)


@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(payload: Scenario):
    if payload._id:
        existing = await mongo.scenarios_collection.find_one({"_id": payload._id})
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scenario ID already exists")
    data = payload.model_dump()
    result = await mongo.scenarios_collection.insert_one(data)
    if not payload._id:
        data["_id"] = str(result.inserted_id)
    return ScenarioResponse.from_mongo(data)


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(scenario_id: str, payload: Scenario):
    existing = await mongo.scenarios_collection.find_one({"_id": scenario_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    update = payload.model_dump(exclude_unset=True)
    if "_id" in update:
        del update["_id"]
    await mongo.scenarios_collection.update_one({"_id": scenario_id}, {"$set": update})
    updated = await mongo.scenarios_collection.find_one({"_id": scenario_id})
    return ScenarioResponse.from_mongo(updated)


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(scenario_id: str):
    result = await mongo.scenarios_collection.delete_one({"_id": scenario_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return None


@router.post("/{scenario_id}/run", response_model=ScenarioSimulationResult)
async def run_scenario(
    scenario_id: str,
    start: Optional[datetime] = Query(default=None, description="Start of optimization window (ISO-8601)"),
    end: Optional[datetime] = Query(default=None, description="End of optimization window (ISO-8601)")
):
    # Load scenario-specific data synchronously (PyMongo inside adapter)
    data = load_scenario_data(scenario_id, start=start, end=end)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found or incomplete")

    optimizer = TrainDispatchOptimizer(data)
    optimizer.build_model()
    feasible = optimizer.solve_model(time_limit=10)
    if not feasible:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No feasible solution found")

    solution = optimizer.get_solution()
    return ScenarioSimulationResult(scenario_id=scenario_id, result=solution)


@router.post("/{scenario_id}/run/save")
async def run_and_save_schedule(
    scenario_id: str,
    start: Optional[datetime] = Query(default=None, description="Start of optimization window (ISO-8601)"),
    end: Optional[datetime] = Query(default=None, description="End of optimization window (ISO-8601)")
):
    """Run the optimizer and persist generated schedule into train_events collection.

    Returns a summary with scenario_id, trains affected, and counts of events inserted.
    """
    data = load_scenario_data(scenario_id, start=start, end=end)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found or incomplete")

    optimizer = TrainDispatchOptimizer(data)
    optimizer.build_model()
    feasible = optimizer.solve_model(time_limit=10)
    if not feasible:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No feasible solution found")

    # Convert to events and save
    events = optimizer.convert_solution_to_events()
    trains = list(optimizer.solution.keys())

    # Remove existing events for these trains (to avoid duplicates)
    deleted = 0
    if trains:
        del_res = await mongo.train_events_collection.delete_many({"train_id": {"$in": trains}})
        deleted = del_res.deleted_count

    inserted = 0
    if events:
        insert_res = await mongo.train_events_collection.insert_many(events)
        inserted = len(insert_res.inserted_ids)

    # Also convert to platform occupancy and upsert
    occupancy = []
    origin = optimizer.origin_time
    # Build quick lookup for train lengths from adapter data
    lengths = {t['train']: t.get('length_m') for t in data.get('trains', [])}
    for ev in events:
        # Derive start/end per event type with fallbacks similar to seed script
        if ev['type'] == 'arrival':
            start_time = ev['scheduled_time']
            # find corresponding departure at same station (may not exist)
            end_time = start_time
            # try to find paired departure in current events
            for e2 in events:
                if e2['train_id'] == ev['train_id'] and e2['station_id'] == ev['station_id'] and e2['type'] == 'departure':
                    end_time = e2['scheduled_time']
                    break
            duration = int((end_time - start_time).total_seconds() / 1000) if hasattr(end_time, 'total_seconds') else 0
        else:  # departure
            end_time = ev['scheduled_time']
            # assume 2 minutes dwell before departure if paired arrival not found
            start_time = end_time
            # try to find paired arrival
            for e2 in events:
                if e2['train_id'] == ev['train_id'] and e2['station_id'] == ev['station_id'] and e2['type'] == 'arrival':
                    start_time = e2['scheduled_time']
                    break
            duration = int((end_time - start_time).total_seconds() / 1000) if hasattr(end_time, 'total_seconds') else 0

        if not ev.get('platform_id'):
            continue
        train_len = lengths.get(ev['train_id'])
        occupancy.append({
            'train_id': ev['train_id'],
            'train_type': optimizer.solution.get(ev['train_id'], {}).get('type'),
            'train_length_m': train_len,
            'station_id': ev['station_id'],
            'platform_id': ev['platform_id'],
            'start_time': start_time,
            'end_time': end_time,
            'duration_sec': int((end_time - start_time).total_seconds()) if hasattr(end_time, 'total_seconds') else 0
        })

    occ_inserted = 0
    if occupancy:
        # Remove overlapping old occupancy for these trains then insert new
        await mongo.platform_occupancy_collection.delete_many({"train_id": {"$in": trains}})
        res = await mongo.platform_occupancy_collection.insert_many(occupancy)
        occ_inserted = len(res.inserted_ids)

    return {
        "scenario_id": scenario_id,
        "start": start,
        "end": end,
        "trains": trains,
        "events_deleted": deleted,
        "events_inserted": inserted,
        "occupancy_inserted": occ_inserted
    }