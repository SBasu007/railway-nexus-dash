from fastapi import APIRouter, HTTPException, status
from typing import Optional
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
        # allow filtering by either custom train_id field or _id
        query["$or"] = [{"train_id": train_id}, {"_id": train_id}]
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
    train = await trains_collection.find_one({"$or": [{"train_id": train_id}, {"_id": train_id}]})
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Train with ID {train_id} not found")
    
    return TrainResponse.from_mongo(train)


@router.post("/", response_model=TrainResponse, status_code=status.HTTP_201_CREATED)
async def create_train(train: Train):
    """Create a new train"""
    # Check if train with this ID already exists
    existing = await trains_collection.find_one({"$or": [{"train_id": train.train_id}, {"_id": train.train_id}]})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Train with ID {train.train_id} already exists"
        )
    
    train_dict = train.model_dump()
    # set _id to train_id for canonical identity
    train_dict.setdefault("_id", train.train_id)
    result = await trains_collection.insert_one(train_dict)
    
    # Return the created train with ID
    created_train = await trains_collection.find_one({"_id": train_dict["_id"]})
    return TrainResponse.from_mongo(created_train)


@router.put("/{train_id}", response_model=TrainResponse)
async def update_train(train_id: str, train_update: Train):
    """Update an existing train"""
    existing = await trains_collection.find_one({"$or": [{"train_id": train_id}, {"_id": train_id}]})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train with ID {train_id} not found"
        )
    
    update_data = train_update.model_dump(exclude_unset=True)
    # ensure we don't overwrite identity
    if "_id" in update_data:
        del update_data["_id"]
    await trains_collection.update_one({"_id": existing.get("_id", train_id)}, {"$set": update_data})
    
    updated_train = await trains_collection.find_one({"_id": existing.get("_id", train_id)})
    return TrainResponse.from_mongo(updated_train)


@router.delete("/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_train(train_id: str):
    """Delete a train"""
    result = await trains_collection.delete_one({"$or": [{"train_id": train_id}, {"_id": train_id}]})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train with ID {train_id} not found"
        )
    
    return None