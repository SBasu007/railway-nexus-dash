from pydantic import BaseModel, Field
from typing import Optional, List


class Segment(BaseModel):
    """Segment model"""
    _id: Optional[str] = None
    from_station: str = Field(..., alias="from")
    to_station: str = Field(..., alias="to")
    capacity: int
    travel_time_min: int
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "seg_S1_S2",
                "from": "S1",
                "to": "S2",
                "capacity": 1,
                "travel_time_min": 20
            }
        }


class SegmentResponse(Segment):
    """Segment response model"""
    id: Optional[str] = None

    @classmethod
    def from_mongo(cls, segment_data):
        """Convert MongoDB document to SegmentResponse"""
        if not segment_data:
            return None

        segment_id = str(segment_data.get("_id", "")) if segment_data.get("_id") else None
        return cls(
            id=segment_id,
            _id=segment_id,
            from_station=segment_data.get("from"),
            to_station=segment_data.get("to"),
            capacity=segment_data.get("capacity"),
            travel_time_min=segment_data.get("travel_time_min")
        )


class SegmentList(BaseModel):
    """List of segments response"""
    segments: List[SegmentResponse]
    total: int