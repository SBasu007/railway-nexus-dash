from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.db.mongodb import scenarios_collection
from app.models.scenarios import Scenario, ScenarioResponse, ScenarioList
from app.schemas.scenario import ScenarioCreate, ScenarioResponse as RespSchema, ScenarioUpdate, ScenarioSimulationResult
from app.optimizer.data_adapter import load_scenario_data
from app.optimizer.train_dispatch_optimizer import TrainDispatchOptimizer

router = APIRouter()


@router.get("/", response_model=ScenarioList)
async def list_scenarios(skip: int = 0, limit: int = 100):
    total = await scenarios_collection.count_documents({})
    cursor = scenarios_collection.find({}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return ScenarioList(scenarios=[ScenarioResponse.from_mongo(d) for d in docs], total=total)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str):
    doc = await scenarios_collection.find_one({"_id": scenario_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return ScenarioResponse.from_mongo(doc)


@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(payload: Scenario):
    if payload._id:
        existing = await scenarios_collection.find_one({"_id": payload._id})
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scenario ID already exists")
    data = payload.model_dump()
    result = await scenarios_collection.insert_one(data)
    if not payload._id:
        data["_id"] = str(result.inserted_id)
    return ScenarioResponse.from_mongo(data)


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(scenario_id: str, payload: Scenario):
    existing = await scenarios_collection.find_one({"_id": scenario_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    update = payload.model_dump(exclude_unset=True)
    if "_id" in update:
        del update["_id"]
    await scenarios_collection.update_one({"_id": scenario_id}, {"$set": update})
    updated = await scenarios_collection.find_one({"_id": scenario_id})
    return ScenarioResponse.from_mongo(updated)


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(scenario_id: str):
    result = await scenarios_collection.delete_one({"_id": scenario_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return None


@router.post("/{scenario_id}/run", response_model=ScenarioSimulationResult)
async def run_scenario(scenario_id: str):
    # Load scenario-specific data synchronously (PyMongo inside adapter)
    data = load_scenario_data(scenario_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found or incomplete")

    optimizer = TrainDispatchOptimizer(data)
    optimizer.build_model()
    feasible = optimizer.solve_model(time_limit=10)
    if not feasible:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No feasible solution found")

    solution = optimizer.get_solution()
    return ScenarioSimulationResult(scenario_id=scenario_id, result=solution)