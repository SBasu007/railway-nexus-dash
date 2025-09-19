// setup.js
// Run with: mongosh --eval 'var RESET_DB=true' setup.js

db = db.getSiblingDB("railwayDB");

// ------------------------------
// Safety: reset DB only if flag is set
// ------------------------------
if (typeof RESET_DB !== "undefined" && RESET_DB) {
  print("⚠️ Resetting database...");
  db.trains.drop();
  db.stations.drop();
  db.segments.drop();
  db.timetable.drop();
  db.constraints.drop();
  db.scenarios.drop();
  db.train_events.drop();
  db.platform_occupancy.drop();
}

// ------------------------------
// Create collections
// ------------------------------
["trains", "stations", "segments", "timetable",
 "constraints", "scenarios", "train_events", "platform_occupancy"]
.forEach(c => db.createCollection(c));

// ------------------------------
// Insert trains
// ------------------------------
db.trains.insertMany([
  { _id: "T001", type: "passenger", priority: 1, avg_speed_kmh: 100, length_m: 200 },
  { _id: "T002", type: "freight",   priority: 3, avg_speed_kmh: 60,  length_m: 500 },
  { _id: "T003", type: "express",   priority: 0, avg_speed_kmh: 120, length_m: 180 }
]);

// ------------------------------
// Insert stations
// ------------------------------
db.stations.insertMany([
  {
    _id: "S1",
    name: "Central",
    total_platforms: 4,
    platforms: [
      { _id: "S1P1", length_m: 250, electrified: true },
      { _id: "S1P2", length_m: 250, electrified: true },
      { _id: "S1P3", length_m: 300, electrified: true },
      { _id: "S1P4", length_m: 350, electrified: false }
    ]
  },
  {
    _id: "S2",
    name: "WestSide",
    total_platforms: 2,
    platforms: [
      { _id: "S2P1", length_m: 200, electrified: true },
      { _id: "S2P2", length_m: 250, electrified: false }
    ]
  },
  {
    _id: "S3",
    name: "EastEnd",
    total_platforms: 3,
    platforms: [
      { _id: "S3P1", length_m: 220, electrified: true },
      { _id: "S3P2", length_m: 220, electrified: true },
      { _id: "S3P3", length_m: 300, electrified: false }
    ]
  }
]);

// ------------------------------
// Insert segments
// ------------------------------
db.segments.insertMany([
  { _id: "seg_S1_S2", from: "S1", to: "S2", capacity: 1, travel_time_min: 20 },
  { _id: "seg_S2_S3", from: "S2", to: "S3", capacity: 1, travel_time_min: 25 }
]);

// ------------------------------
// Insert timetable (normalized dwell_sec + global event_id)
// ------------------------------
db.timetable.insertMany([
  {
    train_id: "T001",
    events: [
      {
        event_id: "T001_E1", type: "departure",
        station_id: "S1", platform_id: "S1P2",
        scheduled_time: ISODate("2025-09-20T08:00:00Z"),
        dwell_sec: 120
      },
      {
        event_id: "T001_E2", type: "arrival",
        station_id: "S2", platform_id: "S2P1",
        scheduled_time: ISODate("2025-09-20T08:20:00Z"),
        dwell_sec: 300
      }
    ]
  },
  {
    train_id: "T002",
    events: [
      {
        event_id: "T002_E1", type: "departure",
        station_id: "S2", platform_id: "S2P2",
        scheduled_time: ISODate("2025-09-20T08:10:00Z"),
        dwell_sec: 180
      },
      {
        event_id: "T002_E2", type: "arrival",
        station_id: "S3", platform_id: "S3P3",
        scheduled_time: ISODate("2025-09-20T08:35:00Z"),
        dwell_sec: 600
      }
    ]
  },
  {
    train_id: "T003",
    events: [
      {
        event_id: "T003_E1", type: "departure",
        station_id: "S1", platform_id: "S1P1",
        scheduled_time: ISODate("2025-09-20T08:15:00Z"),
        dwell_sec: 90
      },
      {
        event_id: "T003_E2", type: "arrival",
        station_id: "S2", platform_id: "S2P1",
        scheduled_time: ISODate("2025-09-20T08:35:00Z"),
        dwell_sec: 240
      }
    ]
  }
]);

// ------------------------------
// Insert constraints and capture IDs
// ------------------------------
let c1 = db.constraints.insertOne({
  type: "maintenance",
  segment_id: "seg_S1_S2",
  start: ISODate("2025-09-20T07:30:00Z"),
  end: ISODate("2025-09-20T07:50:00Z"),
  description: "Track closed for inspection"
}).insertedId;

let c2 = db.constraints.insertOne({
  type: "headway",
  segment_id: "seg_S2_S3",
  min_gap_sec: 300
}).insertedId;

let c3 = db.constraints.insertOne({
  type: "platform_maintenance",
  station_id: "S1",
  platform_id: "S1P3",
  start: ISODate("2025-09-20T08:00:00Z"),
  end: ISODate("2025-09-20T10:00:00Z"),
  description: "Platform renovation"
}).insertedId;

// ------------------------------
// Insert scenario referencing constraint IDs
// ------------------------------
db.scenarios.insertOne({
  _id: "scenario_01",
  description: "Morning traffic with mixed freight/passenger",
  trains: ["T001", "T002", "T003"],
  segments: ["seg_S1_S2", "seg_S2_S3"],
  constraints: [c1, c2, c3]
});

// ------------------------------
// Flatten timetable into train_events
// ------------------------------
db.timetable.aggregate([
  { $unwind: "$events" },
  {
    $project: {
      _id: 0,
      train_id: 1,
      event_id: "$events.event_id",
      type: "$events.type",
      station_id: "$events.station_id",
      platform_id: "$events.platform_id",
      scheduled_time: "$events.scheduled_time",
      dwell_sec: "$events.dwell_sec"
    }
  },
  {
    $merge: {
      into: "train_events",
      on: ["train_id", "event_id"],
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
]);

// ------------------------------
// Generate platform_occupancy
// ------------------------------
db.train_events.find().forEach(ev => {
  let train = db.trains.findOne({ _id: ev.train_id });
  if (!train) return;

  let startTime = ev.type === "arrival"
    ? ev.scheduled_time
    : new Date(ev.scheduled_time.getTime() - (ev.dwell_sec || 120) * 1000);

  let endTime = ev.type === "arrival"
    ? new Date(ev.scheduled_time.getTime() + (ev.dwell_sec || 300) * 1000)
    : ev.scheduled_time;

  // Validate: train length ≤ platform length
  let station = db.stations.findOne({ _id: ev.station_id });
  let platform = station.platforms.find(p => p._id === ev.platform_id);
  if (!platform || train.length_m > platform.length_m) {
    print(`⚠️ Skipping invalid occupancy for ${ev.train_id} at ${ev.platform_id}`);
    return;
  }

  db.platform_occupancy.insertOne({
    train_id: ev.train_id,
    train_type: train.type,
    train_length_m: train.length_m,
    station_id: ev.station_id,
    platform_id: ev.platform_id,
    start_time: startTime,
    end_time: endTime,
    duration_sec: (endTime - startTime) / 1000
  });
});

// ------------------------------
// Indexes
// ------------------------------
db.train_events.createIndex({ station_id: 1, platform_id: 1, scheduled_time: 1 });
db.platform_occupancy.createIndex({ station_id: 1, platform_id: 1, start_time: 1, end_time: 1 });
db.segments.createIndex({ from: 1, to: 1 });
db.constraints.createIndex({ segment_id: 1, start: 1, end: 1 });

print("✅ railwayDB setup complete with safer schema & validation");
