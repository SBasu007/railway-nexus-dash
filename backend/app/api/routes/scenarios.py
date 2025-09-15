from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.mongodb import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioCreate, ScenarioResponse, ScenarioUpdate, ScenarioSimulationResult
from app.api.deps import get_current_user
from app.services.scenario_service import ScenarioService

# Import project-specific dependencies

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

@router.get("/", response_model=List[ScenarioResponse])
def get_scenarios(
    skip: int = 0, 
    limit: int = 100,
    station_id: Optional[int] = None,
    train_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all railway scenarios with optional filtering."""
    return ScenarioService.get_scenarios(
        db, skip=skip, limit=limit,
        station_id=station_id, train_id=train_id,
        type=type, status=status
    )

@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(
    scenario: ScenarioCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new railway simulation scenario."""
    return ScenarioService.create_scenario(db, scenario=scenario, user_id=current_user.id)

@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(
    scenario_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific railway scenario by ID."""
    db_scenario = ScenarioService.get_scenario(db, scenario_id=scenario_id)
    if db_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return db_scenario

@router.put("/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(
    scenario_id: int, 
    scenario: ScenarioUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a railway scenario."""
    db_scenario = ScenarioService.get_scenario(db, scenario_id=scenario_id)
    if db_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if db_scenario.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return ScenarioService.update_scenario(db, scenario_id=scenario_id, scenario=scenario)

@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    scenario_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a railway scenario."""
    db_scenario = ScenarioService.get_scenario(db, scenario_id=scenario_id)
    if db_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    if db_scenario.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    ScenarioService.delete_scenario(db, scenario_id=scenario_id)
    return None

@router.post("/{scenario_id}/run", response_model=ScenarioSimulationResult)
def run_scenario(
    scenario_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Run a railway scenario simulation."""
    db_scenario = ScenarioService.get_scenario(db, scenario_id=scenario_id)
    if db_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioService.run_scenario(db, scenario_id=scenario_id)

@router.get("/{scenario_id}/results", response_model=ScenarioSimulationResult)
def get_scenario_results(
    scenario_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get results of a previously run railway scenario simulation."""
    results = ScenarioService.get_scenario_results(db, scenario_id=scenario_id)
    if results is None:
        raise HTTPException(status_code=404, detail="Scenario results not found")
    return results

@router.get("/templates", response_model=List[ScenarioResponse])
def get_scenario_templates(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get predefined railway scenario templates."""
    return ScenarioService.get_scenario_templates(db)

@router.post("/{scenario_id}/duplicate", response_model=ScenarioResponse)
def duplicate_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Duplicate an existing railway scenario."""
    original_scenario = ScenarioService.get_scenario(db, scenario_id=scenario_id)
    if original_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioService.duplicate_scenario(db, scenario_id=scenario_id, user_id=current_user.id)