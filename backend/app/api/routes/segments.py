from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.db.mongodb import segments_collection
from app.models.segments import Segment, SegmentResponse, SegmentList

router = APIRouter()


@router.get("/", response_model=SegmentList)
async def get_segments(
    skip: int = 0,
    limit: int = 100,
    from_station: Optional[str] = Query(None, alias="from"),
    to_station: Optional[str] = Query(None, alias="to")
):
    """Get list of segments with optional filtering"""
    query = {}
    if from_station:
        query["from"] = from_station
    if to_station:
        query["to"] = to_station
    total = await segments_collection.count_documents(query)
    cursor = segments_collection.find(query).skip(skip).limit(limit)
    segs = await cursor.to_list(length=limit)

    return SegmentList(
        segments=[SegmentResponse.from_mongo(s) for s in segs],
        total=total
    )


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(segment_id: str):
    seg = await segments_collection.find_one({"_id": segment_id})
    if not seg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Segment {segment_id} not found")
    return SegmentResponse.from_mongo(seg)


@router.post("/", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
async def create_segment(segment: Segment):
    # If provided, ensure not duplicate _id
    if segment._id:
        existing = await segments_collection.find_one({"_id": segment._id})
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Segment {segment._id} already exists")

    data = segment.model_dump(by_alias=True)
    result = await segments_collection.insert_one(data)
    if not segment._id:
        data["_id"] = str(result.inserted_id)
    return SegmentResponse.from_mongo(data)


@router.put("/{segment_id}", response_model=SegmentResponse)
async def update_segment(segment_id: str, segment_update: Segment):
    existing = await segments_collection.find_one({"_id": segment_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Segment {segment_id} not found")

    update_data = segment_update.model_dump(by_alias=True, exclude_unset=True)
    if "_id" in update_data:
        del update_data["_id"]
    await segments_collection.update_one({"_id": segment_id}, {"$set": update_data})
    updated = await segments_collection.find_one({"_id": segment_id})
    return SegmentResponse.from_mongo(updated)


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_segment(segment_id: str):
    result = await segments_collection.delete_one({"_id": segment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Segment {segment_id} not found")
    return None