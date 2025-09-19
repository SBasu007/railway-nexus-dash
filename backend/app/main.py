# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging

# Load .env from project root if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("railway-nexus")
from app.core.config import settings, resolved_env_summary

app = FastAPI(title="Railway Nexus Dashboard API", version="0.1.0")

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and mount routers safely (so missing/unfinished route files don't crash import)
try:
    from app.api.routes.trains import router as trains_router
    app.include_router(trains_router, prefix="/api/trains", tags=["Trains"])
except Exception as e:
    logger.warning("Trains router not available: %s", e)

try:
    from app.api.routes.stations import router as stations_router
    app.include_router(stations_router, prefix="/api/stations", tags=["Stations"])
except Exception as e:
    logger.warning("Stations router not available: %s", e)

try:
    from app.api.routes.segments import router as segments_router
    app.include_router(segments_router, prefix="/api/segments", tags=["Segments"])
except Exception as e:
    logger.warning("Segments router not available: %s", e)

try:
    from app.api.routes.timetable import router as timetable_router
    app.include_router(timetable_router, prefix="/api/timetable", tags=["Timetable"])
except Exception as e:
    logger.warning("Timetable router not available: %s", e)

try:
    from app.api.routes.scenarios import router as scenarios_router
    app.include_router(scenarios_router, prefix="/api/scenarios", tags=["Scenarios"])
except Exception as e:
    logger.warning("Scenarios router not available: %s", e)

# DB lifecycle hooks
from app.db.mongodb import connect_to_mongo, close_mongo_connection

@app.on_event("startup")
async def on_startup():
    logger.info("Starting service — env: %s", resolved_env_summary())
    logger.info("Starting service — connecting to MongoDB...")
    await connect_to_mongo()
    logger.info("Startup finished.")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down service — closing MongoDB...")
    await close_mongo_connection()
    logger.info("Shutdown finished.")

# Basic endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "railway-nexus-dashboard"}

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Railway Nexus Dashboard API"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # generic fallback for unexpected exceptions
    return JSONResponse(status_code=500, content={"message": f"Internal server error: {str(exc)}"})

# Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000 (or python -m app.main for reload)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
