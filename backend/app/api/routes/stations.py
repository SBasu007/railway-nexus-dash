from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.db.mongodb import stations_collection
from app.models.stations import Station, StationResponse, StationList, Platform

router = APIRouter()


@router.get("/", response_model=StationList)
async def get_stations(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None
):
    """Get list of stations with optional filtering"""
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}  # Case-insensitive search
        
    total = await stations_collection.count_documents(query)
    cursor = stations_collection.find(query).skip(skip).limit(limit)
    stations = await cursor.to_list(length=limit)
    
    return StationList(
        stations=[StationResponse.from_mongo(station) for station in stations],
        total=total
    )


@router.get("/{station_id}", response_model=StationResponse)
async def get_station(station_id: str):
    """Get a specific station by ID"""
    station = await stations_collection.find_one({"_id": station_id})
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found"
        )
    
    return StationResponse.from_mongo(station)


@router.post("/", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
async def create_station(station: Station):
    """Create a new station"""
    # Check if station with this ID already exists
    if station._id:
        existing = await stations_collection.find_one({"_id": station._id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Station with ID {station._id} already exists"
            )
    
    station_dict = station.model_dump(by_alias=True)
    result = await stations_collection.insert_one(station_dict)
    
    # If _id wasn't provided, use the generated ObjectId
    if not station._id:
        station_dict["_id"] = str(result.inserted_id)
    
    return StationResponse.from_mongo(station_dict)


@router.put("/{station_id}", response_model=StationResponse)
async def update_station(station_id: str, station_update: Station):
    """Update an existing station"""
    existing = await stations_collection.find_one({"_id": station_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found"
        )
    
    update_data = station_update.model_dump(by_alias=True, exclude_unset=True)
    # Ensure _id is not changed
    if "_id" in update_data:
        del update_data["_id"]
    
    await stations_collection.update_one({"_id": station_id}, {"$set": update_data})
    
    updated_station = await stations_collection.find_one({"_id": station_id})
    return StationResponse.from_mongo(updated_station)


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(station_id: str):
    """Delete a station"""
    result = await stations_collection.delete_one({"_id": station_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found"
        )
    
    return None


@router.post("/{station_id}/platforms", response_model=StationResponse)
async def add_platform(station_id: str, platform: Platform):
    """Add a platform to a station"""
    station = await stations_collection.find_one({"_id": station_id})
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found"
        )
    
    # Check if platform with this ID already exists
    existing_platform = next(
        (p for p in station.get("platforms", []) if p.get("platform_id") == platform.platform_id), 
        None
    )
    if existing_platform:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {platform.platform_id} already exists at this station"
        )
    
    # Add the platform and increment total_platforms
    await stations_collection.update_one(
        {"_id": station_id},
        {
            "$push": {"platforms": platform.model_dump(by_alias=True)},
            "$inc": {"total_platforms": 1}
        }
    )
    
    updated_station = await stations_collection.find_one({"_id": station_id})
    return StationResponse.from_mongo(updated_station)