# Railway Nexus Dashboard API

FastAPI backend with MongoDB (Motor async for routes, PyMongo for optimizer) and an OR-Tools based train dispatch optimizer.

## Base URL

- Local development: `http://localhost:8010`

OpenAPI/Swagger UI is available at `http://localhost:8010/docs` and ReDoc at `http://localhost:8010/redoc` when the server is running.

## Authentication

- None. CORS is enabled for all origins by default in development.

## Health

- GET `/health`
  - 200 OK: `{ "status": "healthy", "service": "railway-nexus-dashboard" }`

## Trains

- GET `/api/trains/`
  - Query: `skip`, `limit`, `train_id`, `train_type`
  - 200: `{ trains: TrainResponse[], total: number }`
- GET `/api/trains/{train_id}`
  - 200: `TrainResponse`
- POST `/api/trains/`
  - Body: `Train`
  - 201: `TrainResponse`
- PUT `/api/trains/{train_id}`
  - Body: `Train`
  - 200: `TrainResponse`
- DELETE `/api/trains/{train_id}`
  - 204 No Content

Train model
```
Train {
  train_id: string,
  type: string,
  priority: number,
  avg_speed_kmh: number,
  length_m: number
}
```

## Stations

- GET `/api/stations/`
  - Query: `skip`, `limit`, `name`
  - 200: `{ stations: StationResponse[], total: number }`
- GET `/api/stations/{station_id}`
  - 200: `StationResponse`
- POST `/api/stations/`
  - Body: `Station`
  - 201: `StationResponse`
- PUT `/api/stations/{station_id}`
  - Body: `Station`
  - 200: `StationResponse`
- DELETE `/api/stations/{station_id}`
  - 204 No Content
- POST `/api/stations/{station_id}/platforms`
  - Body: `Platform`
  - 200: `StationResponse`

## Segments

- GET `/api/segments/`
  - Query: `skip`, `limit`, `from`, `to`
  - 200: `{ segments: SegmentResponse[], total: number }`
- GET `/api/segments/{segment_id}`
  - 200: `SegmentResponse`
- POST `/api/segments/`
  - Body: `Segment`
  - 201: `SegmentResponse`
- PUT `/api/segments/{segment_id}`
  - Body: `Segment`
  - 200: `SegmentResponse`
- DELETE `/api/segments/{segment_id}`
  - 204 No Content

Note: Currently, there is a known validation issue mapping `from`/`to` fields in response; returning raw docs with `id` normalized. This will be fixed shortly.

## Timetable & Train Events

- GET `/api/timetable/`
  - Query: `skip`, `limit`, `train_id`
  - 200: `{ timetables: TimetableResponse[], total: number }`
- GET `/api/timetable/{train_id}`
  - 200: `TimetableResponse`
- POST `/api/timetable/`
  - Body: `Timetable`
  - 201: `TimetableResponse`
- PUT `/api/timetable/{train_id}`
  - Body: `Timetable`
  - 200: `TimetableResponse`
- DELETE `/api/timetable/{train_id}`
  - 204 No Content (also deletes train_events for that train)

Train events
- GET `/api/timetable/events/`
  - Query: `skip`, `limit`, `train_id`, `station_id`
  - 200: `{ events: TrainEventResponse[], total: number }`
- POST `/api/timetable/events/`
  - Body: `TrainEvent`
  - 201: `TrainEventResponse`
- DELETE `/api/timetable/events/{event_id}`
  - 204 No Content
- NEW GET `/api/timetable/events/latest`
  - Query: `train_id` (optional), `limit` (default 100)
  - 200: `{ events: TrainEventResponse[], total: number }` sorted by `scheduled_time` desc
 - NEW GET `/api/timetable/events/window`
   - Query: `start` (ISO datetime), `end` (ISO datetime), optional `train_id`, optional `station_id`, `limit`
   - 200: `{ events: TrainEventResponse[], total: number }` filtered to scheduled_time within the window

## Scenarios & Optimizer

- GET `/api/scenarios/`
  - 200: `{ scenarios: ScenarioResponse[], total: number }`
- GET `/api/scenarios/{scenario_id}`
  - 200: `ScenarioResponse`
- POST `/api/scenarios/`
  - Body: `Scenario`
  - 201: `ScenarioResponse`
- PUT `/api/scenarios/{scenario_id}`
  - Body: `Scenario`
  - 200: `ScenarioResponse`
- DELETE `/api/scenarios/{scenario_id}`
  - 204 No Content

Run optimizer
- POST `/api/scenarios/{scenario_id}/run`
  - Query: optional `start`, `end` (ISO datetimes) to restrict the optimization window
  - Runs the optimizer and returns a solution JSON: route, arrivals/departures (minutes from origin), chosen platforms, and objective value.
- NEW POST `/api/scenarios/{scenario_id}/run/save`
  - Query: optional `start`, `end` (ISO datetimes) to restrict the optimization window
  - Runs optimizer and persists results into `train_events`; also derives and persists `platform_occupancy` from the results.
  - Response: `{ scenario_id, trains: string[], events_deleted: number, events_inserted: number, occupancy_inserted: number }`

## Models (summary)

- `TrainResponse`: Train with `id` (Mongo _id) and fields.
- `StationResponse`: Station with `id`, `platforms` (each with `_id` alias).
- `SegmentResponse`: Segment with `id`, fields include `from` and `to` in storage; mapping to safe names is in progress.
- `TimetableResponse`, `TrainEventResponse`: Timetable and flattened event entries.
- `ScenarioResponse`: Scenario with references to trains, segments, and constraints.

## Running locally

- Python: Use the project venv and install requirements
- Server:
```
./.venv/bin/uvicorn --app-dir backend app.main:app --host 0.0.0.0 --port 8010
```
- Seed DB (Mongo running locally):
```
cd backend
mongosh "mongodb://localhost:27017/railwayDB" db/setup.js
```

## Notes

- Routes use Motor (async) for API; optimizer uses PyMongo (sync).
- Pydantic v2 deprecation warnings (`schema_extra` → `json_schema_extra`, `allow_population_by_field_name` → `validate_by_name`) are non-breaking; cleanup planned.
- Legacy `app/api/routes/optimizer.py` is not mounted and references missing services—kept as non-active placeholder.
