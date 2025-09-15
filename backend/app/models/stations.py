from pydantic import BaseModel, Field
from typing import Optional, List


class Platform(BaseModel):
    """Platform model"""
    platform_id: str
    length_m: int
    electrified: bool


class Station(BaseModel):
    """Station model"""
    _id: Optional[str] = None  # Using as primary key
    name: str
    total_platforms: int
    platforms: List[Platform]
    
    class Config:
        schema_extra = {
            "example": {
                "_id": "S1",
                "name": "Central",
                "total_platforms": 4,
                "platforms": [
                    {"platform_id": "S1P1", "length_m": 250, "electrified": True},
                    {"platform_id": "S1P2", "length_m": 250, "electrified": True}
                ]
            }
        }


class StationResponse(Station):
    """Station response model"""
    id: Optional[str] = None  # Alias for _id

    @classmethod
    def from_mongo(cls, station_data):
        """Convert MongoDB document to StationResponse"""
        if not station_data:
            return None

        station_id = str(station_data.get("_id", "")) if station_data.get("_id") else None
        return cls(
            id=station_id,
            _id=station_id,
            name=station_data.get("name"),
            total_platforms=station_data.get("total_platforms"),
            platforms=[Platform(**p) for p in station_data.get("platforms", [])]
        )


class StationList(BaseModel):
    """List of stations response"""
    stations: List[StationResponse]
    total: int