from pydantic import BaseModel, Field
from typing import Optional, List


class SegmentBase(BaseModel):
    """Shared fields with safe Python names and aliases for JSON"""
    from_: str = Field(..., alias="from", validation_alias="from")
    to_: str = Field(..., alias="to", validation_alias="to")

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True,
    }


class Segment(SegmentBase):
    """Segment model"""
    _id: Optional[str] = None
    capacity: int
    travel_time_min: int
    
    # Pydantic v2 config
    model_config = {
        "populate_by_name": True,
        "validate_by_name": True,
        "json_schema_extra": {
            "example": {
                "_id": "seg_S1_S2",
                "from": "S1",
                "to": "S2",
                "capacity": 1,
                "travel_time_min": 20
            }
        }
    }


class SegmentResponse(SegmentBase):
    """Segment response model"""
    id: Optional[str] = None
    _id: Optional[str] = None
    capacity: int
    travel_time_min: int
    # Ensure alias/name population works reliably on subclass
    model_config = {
        "populate_by_name": True,
        "validate_by_name": True,
    }

    @classmethod
    def from_mongo(cls, segment_data):
        """Convert MongoDB document to SegmentResponse"""
        if not segment_data:
            return None
        # Start from the original Mongo document so alias keys ('from', 'to') map correctly
        data = dict(segment_data)
        # Map alias keys to field names explicitly to satisfy validation
        if "from" in data:
            data["from_"] = data.get("from")
        if "to" in data:
            data["to_"] = data.get("to")
        # Normalize ids
        seg_id = segment_data.get("_id")
        if seg_id is not None:
            data["_id"] = str(seg_id)
            data["id"] = str(seg_id)
        return cls.model_validate(data)


class SegmentList(BaseModel):
    """List of segments response"""
    segments: List[SegmentResponse]
    total: int