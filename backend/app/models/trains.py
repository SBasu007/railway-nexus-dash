from pydantic import BaseModel, Field
from typing import Optional, List


class Train(BaseModel):
    """Train model"""
    train_id: str
    type: str
    priority: int
    avg_speed_kmh: float
    length_m: int
    
    class Config:
        schema_extra = {
            "example": {
                "train_id": "T001",
                "type": "passenger",
                "priority": 1,
                "avg_speed_kmh": 100,
                "length_m": 200
            }
        }


class TrainResponse(Train):
    """Train response model with id field"""
    id: Optional[str] = None

    @classmethod
    def from_mongo(cls, train_data):
        """Convert MongoDB document to TrainResponse"""
        if not train_data:
            return None
        
        train_id = str(train_data.get("_id", "")) if train_data.get("_id") else None
        return cls(
            id=train_id,
            train_id=train_data.get("train_id") or train_data.get("_id"),
            type=train_data.get("type"),
            priority=train_data.get("priority"),
            avg_speed_kmh=train_data.get("avg_speed_kmh"),
            length_m=train_data.get("length_m")
        )


class TrainList(BaseModel):
    """List of trains response"""
    trains: List[TrainResponse]
    total: int