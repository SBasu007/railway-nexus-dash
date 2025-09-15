# Scenario model stub for FastAPI
from pydantic import BaseModel

class Scenario(BaseModel):
    id: str
    name: str
    description: str = ""
