from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
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