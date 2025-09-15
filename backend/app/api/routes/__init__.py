from fastapi import APIRouter
from .trains import router as trains_router
from .stations import router as stations_router
from .segments import router as segments_router
from .timetable import router as timetable_router
from .scenarios import router as scenarios_router

api_router = APIRouter()
api_router.include_router(trains_router, prefix="/trains", tags=["trains"])
api_router.include_router(stations_router, prefix="/stations", tags=["stations"])
api_router.include_router(segments_router, prefix="/segments", tags=["segments"])
api_router.include_router(timetable_router, prefix="/timetable", tags=["timetable"])
api_router.include_router(scenarios_router, prefix="/scenarios", tags=["scenarios"])