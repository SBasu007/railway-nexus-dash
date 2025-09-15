from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings
import logging

# MongoDB client instances
motor_client = None  # Async client for API
pymongo_client = None  # Sync client for optimization

# Collections (async)
trains_collection = None
stations_collection = None
segments_collection = None
timetable_collection = None
constraints_collection = None
scenarios_collection = None
train_events_collection = None
platform_occupancy_collection = None


async def connect_to_mongo():
    """Create async MongoDB client connection"""
    global motor_client, trains_collection, stations_collection, segments_collection, \
           timetable_collection, constraints_collection, scenarios_collection, \
           train_events_collection, platform_occupancy_collection
    
    try:
        motor_client = AsyncIOMotorClient(settings.MONGO_URI)
        db = motor_client[settings.MONGO_DB]
        
        # Initialize collections
        trains_collection = db.trains
        stations_collection = db.stations
        segments_collection = db.segments
        timetable_collection = db.timetable
        constraints_collection = db.constraints
        scenarios_collection = db.scenarios
        train_events_collection = db.train_events
        platform_occupancy_collection = db.platform_occupancy
        
        logging.info("Connected to MongoDB")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close async MongoDB client connection"""
    global motor_client
    if motor_client:
        motor_client.close()
        logging.info("Closed MongoDB connection")


def get_sync_client():
    """Get synchronous MongoDB client for optimization"""
    global pymongo_client
    if not pymongo_client:
        pymongo_client = MongoClient(settings.MONGO_URI)
    return pymongo_client