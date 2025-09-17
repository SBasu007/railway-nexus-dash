from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Railway Nexus API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for Railway Nexus Dashboard"
    
    # MongoDB settings
    # Prefer explicit loopback to avoid IPv6/localhost resolution issues
    MONGO_URI: str = "mongodb://127.0.0.1:27017"
    MONGO_DB: str = "railwayDB"
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    class Config:
        # Pydantic Settings v2 still supports this alias; we also load via dotenv in main
        env_file = ".env"


settings = Settings()

def resolved_env_summary() -> str:
    """Return a small summary string of critical envs for logs."""
    return f"MONGO_URI={settings.MONGO_URI} MONGO_DB={settings.MONGO_DB}"