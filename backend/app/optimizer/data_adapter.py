"""
MongoDB data adapter for Train Dispatch Optimizer
Provides load_from_mongo() returning a structured dict used by the optimizer.
"""
from pymongo import MongoClient
from datetime import datetime, timezone
import math
from app.core.config import settings


def load_from_mongo(mongo_uri=None, dbname=None):
    """Load data from MongoDB and normalize into structures the optimizer expects.

    Returns a dict:
      {
        'trains': [ {train, route, planned (mins), platforms (per-stop), type, length_m, ...}, ... ],
        'stations': {station_id: station_doc, ...},
        'segments': {segment_id: segment_doc, ...},
        'constraints': list(...),
        'platform_occupancy': list(...),
        'origin_time': datetime origin used to convert datetimes to minutes
      }
    """
    mongo_uri = mongo_uri or settings.MONGO_URI
    dbname = dbname or settings.MONGO_DB
    
    client = MongoClient(mongo_uri)
    db = client[dbname]

    trains_coll = list(db.trains.find({}))
    stations_coll = {s['_id']: s for s in db.stations.find({})}
    segments_coll = {seg['_id']: seg for seg in db.segments.find({})}
    train_events = list(db.train_events.find({}))
    constraints = list(db.constraints.find({}))
    platform_occ = list(db.platform_occupancy.find({}))

    # Determine origin time (earliest scheduled_time in train_events)
    times = [ev['scheduled_time'] for ev in train_events if 'scheduled_time' in ev]
    if times:
        origin = min(times)
    else:
        origin = datetime.now(timezone.utc)

    def to_minutes(dt):
        return int(math.floor((dt - origin).total_seconds() / 60.0))

    # Map train_id -> train doc
    trains_map = {t['train_id']: t for t in trains_coll}

    # Group events by train and sort by scheduled_time
    trains_out = []
    for train_id in sorted(list({e['train_id'] for e in train_events})):
        evs = sorted([e for e in train_events if e['train_id'] == train_id], key=lambda x: x['scheduled_time'])
        route = [e['station_id'] for e in evs]
        planned = [to_minutes(e['scheduled_time']) for e in evs]
        platforms = [e.get('platform_id') for e in evs]
        # train meta
        train_doc = trains_map.get(train_id, {})
        train_type = train_doc.get('type', 'local')
        length_m = train_doc.get('length_m', train_doc.get('length', 200))

        trains_out.append({
            'train': train_id,
            'route': route,
            'planned': planned,
            'platforms': platforms,
            'type': train_type,
            'length_m': length_m,
            'raw_events': evs
        })

    # Convert platform_occupancy times to minutes too
    platform_occ_norm = []
    for p in platform_occ:
        # expect start_time and end_time to be datetimes
        start = p['start_time']
        end = p['end_time']
        platform_occ_norm.append({
            **p,
            'start_min': to_minutes(start),
            'end_min': to_minutes(end)
        })

    return {
        'trains': trains_out,
        'stations': stations_coll,
        'segments': segments_coll,
        'constraints': constraints,
        'platform_occupancy': platform_occ_norm,
        'origin_time': origin
    }


def load_scenario_data(scenario_id, mongo_uri=None, dbname=None):
    """Load data specific to a scenario"""
    mongo_uri = mongo_uri or settings.MONGO_URI
    dbname = dbname or settings.MONGO_DB
    
    client = MongoClient(mongo_uri)
    db = client[dbname]
    
    # Get scenario document
    scenario = db.scenarios.find_one({"_id": scenario_id})
    if not scenario:
        return None
    
    # Get trains in this scenario
    train_ids = scenario.get('trains', [])
    trains_coll = list(db.trains.find({"train_id": {"$in": train_ids}}))
    
    # Get segments in this scenario
    segment_ids = scenario.get('segments', [])
    segments_coll = {seg['_id']: seg for seg in db.segments.find({"_id": {"$in": segment_ids}})}
    
    # Get all stations referenced by segments
    station_ids = set()
    for seg in segments_coll.values():
        station_ids.add(seg.get('from'))
        station_ids.add(seg.get('to'))
    stations_coll = {s['_id']: s for s in db.stations.find({"_id": {"$in": list(station_ids)}})}
    
    # Get train events for these trains
    train_events = list(db.train_events.find({"train_id": {"$in": train_ids}}))
    
    # Get constraints of types in scenario's constraints list
    constraint_types = scenario.get('constraints', [])
    constraints = list(db.constraints.find({"type": {"$in": constraint_types}}))
    
    # Get platform occupancy for these trains
    platform_occ = list(db.platform_occupancy.find({"train_id": {"$in": train_ids}}))
    
    # Rest of processing is same as load_from_mongo
    times = [ev['scheduled_time'] for ev in train_events if 'scheduled_time' in ev]
    if times:
        origin = min(times)
    else:
        origin = datetime.now(timezone.utc)

    def to_minutes(dt):
        return int(math.floor((dt - origin).total_seconds() / 60.0))

    # Map train_id -> train doc
    trains_map = {t['train_id']: t for t in trains_coll}

    # Group events by train and sort by scheduled_time
    trains_out = []
    for train_id in train_ids:
        evs = sorted([e for e in train_events if e['train_id'] == train_id], key=lambda x: x['scheduled_time'])
        if not evs:  # Skip trains with no events
            continue
        route = [e['station_id'] for e in evs]
        planned = [to_minutes(e['scheduled_time']) for e in evs]
        platforms = [e.get('platform_id') for e in evs]
        # train meta
        train_doc = trains_map.get(train_id, {})
        train_type = train_doc.get('type', 'local')
        length_m = train_doc.get('length_m', train_doc.get('length', 200))

        trains_out.append({
            'train': train_id,
            'route': route,
            'planned': planned,
            'platforms': platforms,
            'type': train_type,
            'length_m': length_m,
            'raw_events': evs
        })

    # Convert platform_occupancy times to minutes too
    platform_occ_norm = []
    for p in platform_occ:
        # expect start_time and end_time to be datetimes
        start = p['start_time']
        end = p['end_time']
        platform_occ_norm.append({
            **p,
            'start_min': to_minutes(start),
            'end_min': to_minutes(end)
        })

    return {
        'trains': trains_out,
        'stations': stations_coll,
        'segments': segments_coll,
        'constraints': constraints,
        'platform_occupancy': platform_occ_norm,
        'origin_time': origin,
        'scenario': scenario
    }