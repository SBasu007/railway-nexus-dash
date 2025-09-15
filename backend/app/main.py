from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import List
from dotenv import load_dotenv
from app.db.mongodb import get_db
from app.api.routes.trains import router as trains_router
from app.api.routes.stations import router as stations_router
from app.api.routes.segments import router as segments_router
from app.api.routes.timetable import router as timetable_router
from app.api.routes.scenarios import router as scenarios_router

# Load environment variables
load_dotenv()

## No SQLAlchemy table creation needed; using MongoDB

# Initialize FastAPI app
app = FastAPI(
    title="Railway Nexus Dashboard API",
    description="Backend API for Railway Nexus Dashboard",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default port
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trains_router, prefix="/api/trains", tags=["Trains"])
app.include_router(stations_router, prefix="/api/stations", tags=["Stations"])
app.include_router(segments_router, prefix="/api/segments", tags=["Segments"])
app.include_router(timetable_router, prefix="/api/timetable", tags=["Timetable"])
app.include_router(scenarios_router, prefix="/api/scenarios", tags=["Scenarios"])

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "railway-nexus-dashboard"}

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Railway Nexus Dashboard API"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)