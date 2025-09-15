from fastapi import APIRouter
from app.api.routes import trains, stations, segments, timetable, constraints, scenarios, optimization

api_router = APIRouter()

api_router.include_router(trains.router, prefix="/trains", tags=["trains"])
api_router.include_router(stations.router, prefix="/stations", tags=["stations"])
api_router.include_router(segments.router, prefix="/segments", tags=["segments"])
api_router.include_router(timetable.router, prefix="/timetable", tags=["timetable"])
api_router.include_router(constraints.router, prefix="/constraints", tags=["constraints"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])