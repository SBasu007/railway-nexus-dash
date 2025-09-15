from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TimetableEvent(BaseModel):
    """Timetable event model"""
    event_id: str
    type: str
    station_id: str
    platform_id: Optional[str] = None
    scheduled_time: datetime
    earliness_sec: int
    lateness_sec: int
    min_dwell_sec: Optional[int] = None
    dwell_time_sec: Optional[int] = None


class Timetable(BaseModel):
    """Timetable model"""
    train_id: str
    events: List[TimetableEvent]
    
    class Config:
        schema_extra = {
            "example": {
                "train_id": "T001",
                "events": [
                    {
                        "event_id": "E1",
                        "type": "departure",
                        "station_id": "S1",
                        "platform_id": "S1P2",
                        "scheduled_time": "2025-09-20T08:00:00Z",
                        "earliness_sec": 60,
                        "lateness_sec": 300,
                        "min_dwell_sec": 120
                    }
                ]
            }
        }


class TimetableResponse(Timetable):
    """Timetable response model"""
    id: Optional[str] = None

    @classmethod
    def from_mongo(cls, timetable_data):
        """Convert MongoDB document to TimetableResponse"""
        if not timetable_data:
            return None
            
        # Convert events
        events = []
        for event_data in timetable_data.get("events", []):
            event = TimetableEvent(
                event_id=event_data.get("event_id"),
                type=event_data.get("type"),
                station_id=event_data.get("station_id"),
                platform_id=event_data.get("platform_id"),
                scheduled_time=event_data.get("scheduled_time"),
                earliness_sec=event_data.get("earliness_sec"),
                lateness_sec=event_data.get("lateness_sec"),
                min_dwell_sec=event_data.get("min_dwell_sec"),
                dwell_time_sec=event_data.get("dwell_time_sec")
            )
            events.append(event)
            
        timetable_id = str(timetable_data.get("_id", "")) if timetable_data.get("_id") else None
        return cls(
            id=timetable_id,
            train_id=timetable_data.get("train_id"),
            events=events
        )


class TimetableList(BaseModel):
    """List of timetables response"""
    timetables: List[TimetableResponse]
    total: int


class TrainEvent(BaseModel):
    """Train event model from train_events collection"""
    train_id: str
    event_id: str
    type: str
    station_id: str
    platform_id: Optional[str] = None
    scheduled_time: datetime
    earliness_sec: int
    lateness_sec: int
    min_dwell_sec: Optional[int] = None
    dwell_time_sec: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "train_id": "T001",
                "event_id": "E1",
                "type": "departure",
                "station_id": "S1",
                "platform_id": "S1P2",
                "scheduled_time": "2025-09-20T08:00:00Z",
                "earliness_sec": 60,
                "lateness_sec": 300,
                "min_dwell_sec": 120
            }
        }


class TrainEventResponse(TrainEvent):
    """TrainEvent response model"""
    id: Optional[str] = None

    @classmethod
    def from_mongo(cls, event_data):
        if not event_data:
            return None
            
        event_id = str(event_data.get("_id", "")) if event_data.get("_id") else None
        return cls(
            id=event_id,
            train_id=event_data.get("train_id"),
            event_id=event_data.get("event_id"),
            type=event_data.get("type"),
            station_id=event_data.get("station_id"),
            platform_id=event_data.get("platform_id"),
            scheduled_time=event_data.get("scheduled_time"),
            earliness_sec=event_data.get("earliness_sec"),
            lateness_sec=event_data.get("lateness_sec"),
            min_dwell_sec=event_data.get("min_dwell_sec"),
            dwell_time_sec=event_data.get("dwell_time_sec")
        )


class TrainEventList(BaseModel):
    """List of train events response"""
    events: List[TrainEventResponse]
    total: int