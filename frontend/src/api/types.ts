// Type definitions for API responses

// Train Types
export interface Train {
  train_id: string;
  name: string;
  type: string;
  max_speed: number;
  capacity: number;
  current_location?: {
    station_id?: string;
    segment_id?: string;
    position?: number;
  };
  status: string;
}

export interface TrainResponse extends Train {
  _id: string;
}

export interface TrainList {
  trains: TrainResponse[];
  total: number;
}

// Station Types
export interface Platform {
  platform_id: string;
  name: string;
  length: number;
  status: string;
}

export interface Station {
  _id?: string;
  name: string;
  code: string;
  location: {
    lat: number;
    lng: number;
  };
  platforms: Platform[];
  connections: string[]; // IDs of connected stations
  status: string;
}

export interface StationResponse extends Station {
  _id: string;
}

export interface StationList {
  stations: StationResponse[];
  total: number;
}

// Segment Types
export interface Segment {
  _id?: string;
  segment_id: string;
  start_station_id: string;
  end_station_id: string;
  length: number;
  max_speed: number;
  electrified: boolean;
  status: string;
}

export interface SegmentResponse extends Segment {
  _id: string;
}

export interface SegmentList {
  segments: SegmentResponse[];
  total: number;
}

// Timetable Types
export interface TimetableEntry {
  train_id: string;
  station_id: string;
  arrival_time: string;
  departure_time: string;
  platform_id?: string;
  status: string; // scheduled, delayed, cancelled, etc.
}

export interface TimetableResponse extends TimetableEntry {
  _id: string;
}

export interface TimetableList {
  entries: TimetableResponse[];
  total: number;
}

// Optimization Types
export interface OptimizationRequest {
  scenario_id?: string;
  constraints: Record<string, any>;
  priorities: Record<string, number>;
}

export interface OptimizationResult {
  _id: string;
  status: string;
  created_at: string;
  completed_at?: string;
  scenario_id?: string;
  original_timetable: TimetableResponse[];
  optimized_timetable: TimetableResponse[];
  metrics: {
    delay_reduction: number;
    capacity_utilization: number;
    energy_savings: number;
    conflict_resolution: number;
  };
}

// Scenario Types
export interface Scenario {
  _id?: string;
  name: string;
  description: string;
  created_at: string;
  created_by: string;
  status: string;
  parameters: Record<string, any>;
}

export interface ScenarioResponse extends Scenario {
  _id: string;
}

export interface ScenarioList {
  scenarios: ScenarioResponse[];
  total: number;
}