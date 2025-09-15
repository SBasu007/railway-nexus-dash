from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import trains_collection
from app.models.trains import Train, TrainResponse, TrainList

router = APIRouter()


@router.get("/", response_model=TrainList)
async def get_trains(
    skip: int = 0,
    limit: int = 100,
    train_id: Optional[str] = None,
    train_type: Optional[str] = None
):
    """Get list of trains with optional filtering"""
    query = {}
    if train_id:
        query["train_id"] = train_id
    if train_type:
        query["type"] = train_type
        
    total = await trains_collection.count_documents(query)
    cursor = trains_collection.find(query).skip(skip).limit(limit)
    trains = await cursor.to_list(length=limit)
    
    return TrainList(
        trains=[TrainResponse.from_mongo(train) for train in trains],
        total=total
    )


@router.get("/{train_id}", response_model=TrainResponse)
async def get_train(train_id: str):
    """Get a specific train by ID"""
    train = await trains_collection.find_one({"train_id": train_id})
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Train with ID {train_id} not found")
    
    return TrainResponse.from_mongo(train)


@router.post("/", response_model=TrainResponse, status_code=status.HTTP_201_CREATED)
async def create_train(train: Train):
    """Create a new train"""
    # Check if train with this ID already exists
    existing = await trains_collection.find_one({"train_id": train.train_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Train with ID {train.train_id} already exists"
        )
    
    train_dict = train.dict()
    result = await trains_collection.insert_one(train_dict)
    
    # Return the created train with ID
    created_train = await trains_collection.find_one({"_id": result.inserted_id})
    return TrainResponse.from_mongo(created_train)


@router.put("/{train_id}", response_model=TrainResponse)
async def update_train(train_id: str, train_update: Train):
    """Update an existing train"""
    existing = await trains_collection.find_one({"train_id": train_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train with ID {train_id} not found"
        )
    
    update_data = train_update.dict(exclude_unset=True)
    await trains_collection.update_one({"train_id": train_id}, {"$set": update_data})
    
    updated_train = await trains_collection.find_one({"train_id": train_id})
    return TrainResponse.from_mongo(updated_train)


@router.delete("/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_train(train_id: str):
    """Delete a train"""
    result = await trains_collection.delete_one({"train_id": train_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train with ID {train_id} not found"
        )
    
    return None