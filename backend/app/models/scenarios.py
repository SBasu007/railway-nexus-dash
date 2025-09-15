from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Scenario(BaseModel):
    """Scenario model"""
    _id: Optional[str] = None
    description: str
    trains: List[str]
    segments: List[str]
    constraints: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "_id": "scenario_01",
                "description": "Morning traffic with mixed freight/passenger",
                "trains": ["T001", "T002", "T003"],
                "segments": ["seg_S1_S2", "seg_S2_S3"],
                "constraints": ["maintenance", "headway", "platform_maintenance"]
            }
        }


class ScenarioResponse(Scenario):
    """Scenario response model"""
    id: Optional[str] = None

    @classmethod
    def from_mongo(cls, scenario_data):
        """Convert MongoDB document to ScenarioResponse"""
        if not scenario_data:
            return None
            
        scenario_id = str(scenario_data.get("_id", "")) if scenario_data.get("_id") else None
        return cls(
            id=scenario_id,
            _id=scenario_id,
            description=scenario_data.get("description"),
            trains=scenario_data.get("trains", []),
            segments=scenario_data.get("segments", []),
            constraints=scenario_data.get("constraints", [])
        )


class ScenarioList(BaseModel):
    """List of scenarios response"""
    scenarios: List[ScenarioResponse]
    total: int