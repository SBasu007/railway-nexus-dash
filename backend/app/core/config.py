from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Railway Nexus API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for Railway Nexus Dashboard"

    # MongoDB settings — support both MONGO_* and legacy MONGODB_* env vars
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017",
        validation_alias=AliasChoices("MONGO_URI", "MONGODB_URI"),
    )
    MONGO_DB: str = Field(
        default="railwayDB",
        validation_alias=AliasChoices("MONGO_DB", "MONGODB_DB"),
    )

    # CORS settings
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"


settings = Settings()

def resolved_env_summary() -> str:
    """Return a small summary string of critical envs for logs."""
    return f"MONGO_URI={settings.MONGO_URI} MONGO_DB={settings.MONGO_DB}"