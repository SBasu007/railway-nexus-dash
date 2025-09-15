from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.db import mongodb as mongo
from app.models.timetable import (
    Timetable, TimetableResponse, TimetableList,
    TrainEvent, TrainEventResponse, TrainEventList
)
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=TimetableList)
async def list_timetables(skip: int = 0, limit: int = 100, train_id: Optional[str] = None):
    query = {"train_id": train_id} if train_id else {}
    total = await mongo.timetable_collection.count_documents(query)
    cursor = mongo.timetable_collection.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return TimetableList(
        timetables=[TimetableResponse.from_mongo(d) for d in docs],
        total=total
    )


@router.get("/{train_id}", response_model=TimetableResponse)
async def get_timetable(train_id: str):
    doc = await mongo.timetable_collection.find_one({"train_id": train_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Timetable for train {train_id} not found")
    return TimetableResponse.from_mongo(doc)


@router.post("/", response_model=TimetableResponse, status_code=status.HTTP_201_CREATED)
async def create_timetable(timetable: Timetable):
    existing = await mongo.timetable_collection.find_one({"train_id": timetable.train_id})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timetable already exists for this train")
    data = timetable.model_dump()
    result = await mongo.timetable_collection.insert_one(data)
    created = await mongo.timetable_collection.find_one({"_id": result.inserted_id})
    return TimetableResponse.from_mongo(created)


@router.put("/{train_id}", response_model=TimetableResponse)
async def update_timetable(train_id: str, timetable_update: Timetable):
    existing = await mongo.timetable_collection.find_one({"train_id": train_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable not found")
    update_data = timetable_update.model_dump(exclude_unset=True)
    await mongo.timetable_collection.update_one({"train_id": train_id}, {"$set": update_data})
    updated = await mongo.timetable_collection.find_one({"train_id": train_id})
    return TimetableResponse.from_mongo(updated)


@router.delete("/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timetable(train_id: str):
    result = await mongo.timetable_collection.delete_one({"train_id": train_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable not found")
    # Also clean related train events optionally
    await mongo.train_events_collection.delete_many({"train_id": train_id})
    return None


# Train events endpoints
@router.get("/events/", response_model=TrainEventList)
async def list_events(skip: int = 0, limit: int = 100, train_id: Optional[str] = None, station_id: Optional[str] = None):
    query = {}
    if train_id:
        query["train_id"] = train_id
    if station_id:
        query["station_id"] = station_id
    total = await mongo.train_events_collection.count_documents(query)
    cursor = mongo.train_events_collection.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return TrainEventList(events=[TrainEventResponse.from_mongo(d) for d in docs], total=total)


@router.post("/events/", response_model=TrainEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: TrainEvent):
    data = event.model_dump()
    result = await mongo.train_events_collection.insert_one(data)
    created = await mongo.train_events_collection.find_one({"_id": result.inserted_id})
    return TrainEventResponse.from_mongo(created)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    result = await mongo.train_events_collection.delete_one({"event_id": event_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return None


@router.get("/events/latest", response_model=TrainEventList)
async def latest_schedule(train_id: Optional[str] = None, limit: int = 100):
    """Fetch the latest optimized schedule per train from train_events.

    If train_id is provided, returns all events for that train sorted by scheduled_time desc.
    If not provided, returns the most recent events across trains up to a limit.
    """
    query = {}
    if train_id:
        query["train_id"] = train_id

    cursor = mongo.train_events_collection.find(query).sort("scheduled_time", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    total = len(docs)
    return TrainEventList(events=[TrainEventResponse.from_mongo(d) for d in docs], total=total)


@router.get("/events/window", response_model=TrainEventList)
async def events_in_window(
    start: datetime = Query(..., description="Start of window (ISO-8601)"),
    end: datetime = Query(..., description="End of window (ISO-8601)"),
    train_id: Optional[str] = Query(default=None),
    station_id: Optional[str] = Query(default=None),
    limit: int = Query(default=500, le=5000)
):
    """Return events whose scheduled_time is within [start, end]."""
    query = {"scheduled_time": {"$gte": start, "$lte": end}}
    if train_id:
        query["train_id"] = train_id
    if station_id:
        query["station_id"] = station_id
    cursor = mongo.train_events_collection.find(query).sort("scheduled_time", 1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return TrainEventList(events=[TrainEventResponse.from_mongo(d) for d in docs], total=len(docs))