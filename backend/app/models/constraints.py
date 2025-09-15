from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MaintenanceConstraint(BaseModel):
    """Maintenance constraint model"""
    type: str = "maintenance"
    segment_id: str
    start: datetime
    end: datetime
    description: str


class HeadwayConstraint(BaseModel):
    """Headway constraint model"""
    type: str = "headway"
    segment_id: str
    min_gap_sec: int


class PlatformMaintenanceConstraint(BaseModel):
    """Platform maintenance constraint model"""
    type: str = "platform_maintenance"
    station_id: str
    platform_id: str
    start: datetime
    end: datetime
    description: str


class ConstraintResponse(BaseModel):
    """Constraint response model"""
    id: Optional[str] = None
    type: str
    segment_id: Optional[str] = None
    station_id: Optional[str] = None
    platform_id: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    min_gap_sec: Optional[int] = None
    description: Optional[str] = None

    @classmethod
    def from_mongo(cls, constraint_data):
        """Convert MongoDB document to ConstraintResponse"""
        if not constraint_data:
            return None
            
        constraint_id = str(constraint_data.get("_id", "")) if constraint_data.get("_id") else None
        return cls(
            id=constraint_id,
            type=constraint_data.get("type"),
            segment_id=constraint_data.get("segment_id"),
            station_id=constraint_data.get("station_id"),
            platform_id=constraint_data.get("platform_id"),
            start=constraint_data.get("start"),
            end=constraint_data.get("end"),
            min_gap_sec=constraint_data.get("min_gap_sec"),
            description=constraint_data.get("description")
        )


class ConstraintList(BaseModel):
    """List of constraints response"""
    constraints: List[ConstraintResponse]
    total: int