from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime


class OptimizationRequest(BaseModel):
    """Request model for optimization"""
    scenario_id: str
    time_limit_seconds: Optional[int] = 30


class OptimizationResultEvent(BaseModel):
    """An event in optimization results"""
    station: str
    platform: Optional[str] = None
    actual_arrival: int
    actual_departure: int


class OptimizationResultTrain(BaseModel):
    """Result for a single train"""
    train_id: str
    route: List[str]
    events: Dict[str, OptimizationResultEvent]


class OptimizationResult(BaseModel):
    """Result model for optimization"""
    scenario_id: str
    status: str
    solved_at: datetime
    objective_value: Optional[float] = None
    trains: Dict[str, Any]
    visualization_url: Optional[str] = None