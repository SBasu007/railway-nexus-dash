from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.services.optimization_service import OptimizationService
from app.models.optimization_models import OptimizationRequest, OptimizationResult
from app.core.dependencies import get_current_user
from app.models.user_models import User

# Import service layer components

router = APIRouter(
    prefix="/optimizer",
    tags=["optimizer"]
)

class TrainRouteOptimizationRequest(BaseModel):
    source_station: str
    destination_station: str
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    optimization_criteria: str = "time"  # time, fuel, cost
    constraints: Optional[dict] = None

class ResourceOptimizationRequest(BaseModel):
    train_ids: List[int]
    time_period: dict  # start_date, end_date
    resource_type: str  # crew, equipment, etc.
    priority_factors: Optional[dict] = None

@router.post("/optimize-route", response_model=OptimizationResult)
async def optimize_train_route(
    request: TrainRouteOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize a railway route between two stations based on specified criteria
    """
    try:
        optimization_service = OptimizationService()
        result = await optimization_service.optimize_route(
            source=request.source_station,
            destination=request.destination_station,
            departure_time=request.departure_time,
            arrival_time=request.arrival_time,
            criteria=request.optimization_criteria,
            constraints=request.constraints,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route optimization failed: {str(e)}"
        )

@router.post("/optimize-resources", response_model=OptimizationResult)
async def optimize_resources(
    request: ResourceOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize resource allocation for specified trains and time period
    """
    try:
        optimization_service = OptimizationService()
        result = await optimization_service.optimize_resources(
            train_ids=request.train_ids,
            time_period=request.time_period,
            resource_type=request.resource_type,
            priority_factors=request.priority_factors,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resource optimization failed: {str(e)}"
        )

@router.post("/custom-optimization", response_model=OptimizationResult)
async def run_custom_optimization(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run a custom optimization with specialized parameters
    """
    try:
        optimization_service = OptimizationService()
        result = await optimization_service.run_custom_optimization(
            request=request,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Custom optimization failed: {str(e)}"
        )

@router.get("/algorithms", response_model=List[str])
async def get_available_algorithms():
    """
    Get list of available optimization algorithms
    """
    return OptimizationService.get_available_algorithms()