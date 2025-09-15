# Scenario schemas for FastAPI
from pydantic import BaseModel

class ScenarioCreate(BaseModel):
    name: str
    description: str = ""

class ScenarioResponse(BaseModel):
    id: str
    name: str
    description: str = ""

class ScenarioUpdate(BaseModel):
    name: str = None
    description: str = None

class ScenarioSimulationResult(BaseModel):
    scenario_id: str
    result: dict
