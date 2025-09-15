from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import os
from typing import List
from dotenv import load_dotenv
from app.database.database import get_db, engine
from app.database import models
from app.routers import auth, users, trains, schedules, analytics

# Import database connection

# Import routers

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

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
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(trains.router, prefix="/api/trains", tags=["Trains"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["Schedules"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

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