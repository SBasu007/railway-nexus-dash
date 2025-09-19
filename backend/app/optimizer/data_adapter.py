"""
MongoDB data adapter for Train Dispatch Optimizer
Provides load_from_mongo() returning a structured dict used by the optimizer.
"""
from pymongo import MongoClient
from datetime import datetime, timezone
from typing import Optional
import math
from app.core.config import settings


def _normalize_window(start, end):
    """Ensure datetimes are timezone-aware (UTC) and ordered."""
    if start and start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end and end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    if start and end and end < start:
        # swap to be safe
        start, end = end, start
    return start, end


def load_from_mongo(mongo_uri=None, dbname=None, start: Optional[datetime] = None, end: Optional[datetime] = None):
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

    # Normalize window params
    start, end = _normalize_window(start, end)

    trains_coll = list(db.trains.find({}))
    stations_coll = {s['_id']: s for s in db.stations.find({})}
    # Normalize platform docs to have 'platform_id'
    for sid, sdoc in stations_coll.items():
        plats = []
        for p in sdoc.get('platforms', []):
            pid = p.get('platform_id') or p.get('_id')
            if pid is None:
                continue
            q = dict(p)
            q['platform_id'] = pid
            plats.append(q)
        sdoc['platforms'] = plats
    segments_coll = {seg['_id']: seg for seg in db.segments.find({})}
    # Apply time window filter to train events if provided
    ev_query = {}
    if start and end:
        ev_query["scheduled_time"] = {"$gte": start, "$lte": end}
    elif start:
        ev_query["scheduled_time"] = {"$gte": start}
    elif end:
        ev_query["scheduled_time"] = {"$lte": end}
    train_events = list(db.train_events.find(ev_query))
    constraints = list(db.constraints.find({}))
    # Platform occupancy: include records that overlap the window
    occ_query = {}
    if start or end:
        # overlap condition: start_time <= end AND end_time >= start
        conds = []
        if end:
            conds.append({"start_time": {"$lte": end}})
        if start:
            conds.append({"end_time": {"$gte": start}})
        if conds:
            occ_query = {"$and": conds}
    platform_occ = list(db.platform_occupancy.find(occ_query))

    # Determine origin time (earliest scheduled_time in train_events)
    times = [ev['scheduled_time'] for ev in train_events if 'scheduled_time' in ev]
    if start:
        origin = start
    elif times:
        origin = min(times)
    else:
        origin = datetime.now(timezone.utc)

    def to_minutes(dt):
        return int(math.floor((dt - origin).total_seconds() / 60.0))

    # Map train_id -> train doc (support both schemas: _id or train_id)
    trains_map = {}
    for t in trains_coll:
        key = t.get('train_id') or t.get('_id')
        if key:
            trains_map[key] = t

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


def load_scenario_data(
    scenario_id,
    mongo_uri=None,
    dbname=None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None
):
    """Load data specific to a scenario"""
    mongo_uri = mongo_uri or settings.MONGO_URI
    dbname = dbname or settings.MONGO_DB
    
    client = MongoClient(mongo_uri)
    db = client[dbname]
    # Normalize window params
    start, end = _normalize_window(start, end)
    
    # Get scenario document
    scenario = db.scenarios.find_one({"_id": scenario_id})
    if not scenario:
        return None
    
    # Get trains in this scenario
    train_ids = scenario.get('trains', [])
    # Trains collection uses _id as identifier in seed data
    trains_coll = list(db.trains.find({"_id": {"$in": train_ids}}))
    
    # Get segments in this scenario
    segment_ids = scenario.get('segments', [])
    segments_coll = {seg['_id']: seg for seg in db.segments.find({"_id": {"$in": segment_ids}})}
    
    # Get all stations referenced by segments
    station_ids = set()
    for seg in segments_coll.values():
        station_ids.add(seg.get('from'))
        station_ids.add(seg.get('to'))
    stations_coll = {s['_id']: s for s in db.stations.find({"_id": {"$in": list(station_ids)}})}
    # Normalize platform docs to have 'platform_id'
    for sid, sdoc in stations_coll.items():
        plats = []
        for p in sdoc.get('platforms', []):
            pid = p.get('platform_id') or p.get('_id')
            if pid is None:
                continue
            q = dict(p)
            q['platform_id'] = pid
            plats.append(q)
        sdoc['platforms'] = plats
    
    # Get train events for these trains
    ev_query = {"train_id": {"$in": train_ids}}
    if start and end:
        ev_query["scheduled_time"] = {"$gte": start, "$lte": end}
    elif start:
        ev_query["scheduled_time"] = {"$gte": start}
    elif end:
        ev_query["scheduled_time"] = {"$lte": end}
    train_events = list(db.train_events.find(ev_query))
    
    # Get constraints referenced by scenario. Seed stores ObjectIds; if strings, treat as types.
    constraint_refs = scenario.get('constraints', [])
    constraints = []
    if constraint_refs:
        # If any ref looks like an ObjectId (has attribute 'binary' or is not str), query by _id
        try:
            # simple heuristic: if not all are strings, assume _id list
            if not all(isinstance(x, str) for x in constraint_refs):
                constraints = list(db.constraints.find({"_id": {"$in": constraint_refs}}))
            else:
                constraints = list(db.constraints.find({"type": {"$in": constraint_refs}}))
        except Exception:
            # fallback to empty on error
            constraints = []
    
    # Get platform occupancy for these trains
    occ_query = {"train_id": {"$in": train_ids}}
    if start or end:
        and_conds = [occ_query]
        if end:
            and_conds.append({"start_time": {"$lte": end}})
        if start:
            and_conds.append({"end_time": {"$gte": start}})
        occ_query = {"$and": and_conds}
    platform_occ = list(db.platform_occupancy.find(occ_query))
    
    # Rest of processing is same as load_from_mongo
    times = [ev['scheduled_time'] for ev in train_events if 'scheduled_time' in ev]
    if start:
        origin = start
    elif times:
        origin = min(times)
    else:
        origin = datetime.now(timezone.utc)

    def to_minutes(dt):
        return int(math.floor((dt - origin).total_seconds() / 60.0))

    # Map train_id -> train doc (support both schemas: _id or train_id)
    trains_map = {}
    for t in trains_coll:
        key = t.get('train_id') or t.get('_id')
        if key:
            trains_map[key] = t

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