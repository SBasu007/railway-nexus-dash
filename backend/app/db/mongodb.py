# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger("railway-nexus.db")

# Globals for clients / collections
motor_client: Optional[AsyncIOMotorClient] = None
pymongo_client: Optional[MongoClient] = None

# These will be set after connect_to_mongo
trains_collection = None
stations_collection = None
segments_collection = None
timetable_collection = None
constraints_collection = None
scenarios_collection = None
train_events_collection = None
platform_occupancy_collection = None

async def connect_to_mongo():
    """
    Initialize motor async client and set commonly used collection references.
    This should be called on FastAPI startup.
    """
    global motor_client, trains_collection, stations_collection, segments_collection
    global timetable_collection, constraints_collection, scenarios_collection
    global train_events_collection, platform_occupancy_collection

    if motor_client:
        logger.info("Motor client already initialized")
        return

    try:
        motor_client = AsyncIOMotorClient(settings.MONGO_URI)
        db = motor_client[settings.MONGO_DB]

        # collections
        trains_collection = db.trains
        stations_collection = db.stations
        segments_collection = db.segments
        timetable_collection = db.timetable
        constraints_collection = db.constraints
        scenarios_collection = db.scenarios
        train_events_collection = db.train_events
        platform_occupancy_collection = db.platform_occupancy

        logger.info("Connected to MongoDB (async motor)")
    except Exception as e:
        logger.exception("Failed to connect to MongoDB: %s", e)
        raise

async def close_mongo_connection():
    """
    Close the async motor client. Call on app shutdown.
    """
    global motor_client
    if motor_client:
        motor_client.close()
        motor_client = None
        logger.info("Closed MongoDB connection")

def get_sync_client():
    """
    Return a synchronous PyMongo client for synchronous usage (e.g., optimizer that expects blocking I/O).
    """
    global pymongo_client
    if not pymongo_client:
        pymongo_client = MongoClient(settings.MONGO_URI)
    return pymongo_client

def get_db():
    """
    Return the AsyncIOMotorClient instance (you can use get_db().<collection>).
    This is a lightweight accessor for code that expects an already-connected client.
    """
    global motor_client
    if not motor_client:
        raise RuntimeError("Motor client is not initialized. Ensure connect_to_mongo() was called on startup.")
    return motor_client
