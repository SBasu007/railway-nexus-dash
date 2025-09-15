from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Railway Nexus API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for Railway Nexus Dashboard"
    
    # MongoDB settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "railwayDB"
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"


settings = Settings()