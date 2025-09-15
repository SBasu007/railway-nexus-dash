"""
Train Dispatch Optimizer with platform-level handling and Mongo adapter integration.
This file expects OR-Tools and pymongo adapter outputs.
"""
import math
import json
from ortools.sat.python import cp_model
from datetime import datetime, timedelta


class TrainDispatchOptimizer:
    def __init__(self, data=None):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # Data containers (populated from adapter)
        self.trains = []
        self.stations_data = {}  # station_id -> station doc (with platforms list)
        self.segments = {}
        self.constraints = []
        self.platform_occupancy = []  # pre-existing fixed occupancies
        self.origin_time = None

        # Internal
        self.blocks = {}
        self.variables = {}
        self.solution = {}
        self.platform_intervals = {}  # platform_id -> list(intervals)
        self.scenario = None

        # Constants (defaults; some may be overridden by DB constraints)
        self.BLOCK_SIZE = 400  # meters
        self.MIN_DWELL_MIN = 1  # minutes fallback
        self.MAX_EARLINESS = 5
        self.MAX_LATENESS = 60
        self.MIN_HEADWAY_MIN = 2
        self.MAX_SPEED = 60
        self.TIME_HORIZON = 24 * 60  # minutes default large horizon
        
        # Priority weights for delays
        self.PRIORITY_WEIGHTS = {
            'express': 10,
            'passenger': 8,
            'local': 5,
            'freight': 1
        }
        
        self.objective_value = None

        if data:
            self.load_from_adapter(data)

    def load_from_adapter(self, data):
        """Load normalized data from adapter (dict produced by load_from_mongo)."""
        self.trains = data.get('trains', [])
        self.stations_data = data.get('stations', {})
        self.segments = data.get('segments', {})
        self.constraints = data.get('constraints', [])
        self.platform_occupancy = data.get('platform_occupancy', [])
        self.origin_time = data.get('origin_time')
        self.scenario = data.get('scenario')

        # set TIME_HORIZON from latest planned time
        latest = 0
        for t in self.trains:
            if t['planned']:
                latest = max(latest, max(t['planned']))
        self.TIME_HORIZON = max(self.TIME_HORIZON, latest + 120)

        # Create blocks per segment (simple numeric blocks based on configured BLOCKS_PER_SEGMENT)
        # For simplicity we use 3 blocks per segment here
        for seg_id, seg_doc in self.segments.items():
            # create block ids
            self.blocks[seg_id] = [f"{seg_id}_B{i+1}" for i in range(3)]

    def _create_variables(self):
        for train in self.trains:
            train_id = train['train']
            self.variables[train_id] = {
                'arrival': {},
                'departure': {},
                'block_entry': {},
                'block_exit': {},
                'block_occupied': {},
                'delay': {},
                'platform_choice': {}
            }

            for i, station in enumerate(train['route']):
                # arrival/departure times
                self.variables[train_id]['arrival'][station] = self.model.NewIntVar(0, self.TIME_HORIZON, f'{train_id}_arr_{station}')
                self.variables[train_id]['departure'][station] = self.model.NewIntVar(0, self.TIME_HORIZON, f'{train_id}_dep_{station}')

                # delay variable
                self.variables[train_id]['delay'][station] = self.model.NewIntVar(-self.MAX_EARLINESS, self.MAX_LATENESS, f'{train_id}_delay_{station}')

                # platform choice booleans for each platform at this station
                station_doc = self.stations_data.get(station)
                platform_ids = []
                if station_doc:
                    platform_ids = [p['platform_id'] for p in station_doc.get('platforms', [])]
                if platform_ids:
                    self.variables[train_id]['platform_choice'][station] = {}
                    for p in platform_ids:
                        b = self.model.NewBoolVar(f'{train_id}_uses_{p}')
                        self.variables[train_id]['platform_choice'][station][p] = b

                    # If timetable provided a preassigned platform, fix it; else allow optimizer to choose
                    preassigned = None
                    if 'platforms' in train and len(train['platforms']) > i:
                        preassigned = train['platforms'][i]
                    if preassigned:
                        for p in platform_ids:
                            if p == preassigned:
                                self.model.Add(self.variables[train_id]['platform_choice'][station][p] == 1)
                            else:
                                self.model.Add(self.variables[train_id]['platform_choice'][station][p] == 0)
                    else:
                        # Exactly one platform must be chosen
                        self.model.Add(sum(self.variables[train_id]['platform_choice'][station].values()) == 1)

                # create block vars for segment to next station
                if i < len(train['route']) - 1:
                    next_station = train['route'][i+1]
                    # find segment id that connects station->next_station
                    seg_id = None
                    for sid, sdoc in self.segments.items():
                        if sdoc.get('from') == station and sdoc.get('to') == next_station:
                            seg_id = sid
                            break
                    if seg_id and seg_id in self.blocks:
                        for block in self.blocks[seg_id]:
                            self.variables[train_id]['block_entry'][block] = self.model.NewIntVar(0, self.TIME_HORIZON, f'{train_id}_entry_{block}')
                            self.variables[train_id]['block_exit'][block] = self.model.NewIntVar(0, self.TIME_HORIZON, f'{train_id}_exit_{block}')
                            self.variables[train_id]['block_occupied'][block] = self.model.NewBoolVar(f'{train_id}_occ_{block}')

    def _add_temporal_constraints(self):
        # Add temporal constraints per train/station
        for train in self.trains:
            train_id = train['train']
            for i, station in enumerate(train['route']):
                planned_time = train['planned'][i]
                # arrival window
                self.model.Add(self.variables[train_id]['arrival'][station] >= planned_time - self.MAX_EARLINESS)
                self.model.Add(self.variables[train_id]['arrival'][station] <= planned_time + self.MAX_LATENESS)

                # minimum dwell (use event min_dwell if provided in raw_events)
                min_dwell_min = self.MIN_DWELL_MIN
                raw_event = None
                try:
                    raw_event = train['raw_events'][i]
                    if raw_event and raw_event.get('min_dwell_sec'):
                        min_dwell_min = max(1, int(math.ceil(raw_event.get('min_dwell_sec')/60.0)))
                except Exception:
                    pass

                self.model.Add(self.variables[train_id]['departure'][station] >= self.variables[train_id]['arrival'][station] + min_dwell_min)

                # delay var
                self.model.Add(self.variables[train_id]['delay'][station] == self.variables[train_id]['arrival'][station] - planned_time)

                # travel between stations
                if i > 0:
                    prev_station = train['route'][i-1]
                    # compute min_travel
                    min_travel = max(1, int(math.ceil((train['planned'][i] - train['planned'][i-1]))))
                    self.model.Add(self.variables[train_id]['arrival'][station] >= self.variables[train_id]['departure'][prev_station] + min_travel)

                # block sequencing
                if i < len(train['route']) - 1:
                    next_station = train['route'][i+1]
                    seg_id = None
                    for sid, sdoc in self.segments.items():
                        if sdoc.get('from') == station and sdoc.get('to') == next_station:
                            seg_id = sid
                            break
                    if seg_id and seg_id in self.blocks:
                        blocks = self.blocks[seg_id]
                        # first block entry after departure
                        self.model.Add(self.variables[train_id]['block_entry'][blocks[0]] >= self.variables[train_id]['departure'][station])
                        # last block exit before next arrival
                        self.model.Add(self.variables[train_id]['block_exit'][blocks[-1]] <= self.variables[train_id]['arrival'][next_station])
                        # sequential block traversal
                        for j in range(len(blocks)-1):
                            self.model.Add(self.variables[train_id]['block_entry'][blocks[j+1]] >= self.variables[train_id]['block_exit'][blocks[j]])

                        # enforce minimum traverse time for each block
                        block_traverse_time = max(1, int(math.ceil((self.BLOCK_SIZE/1000) / (self.MAX_SPEED/60.0))))
                        for block in blocks:
                            self.model.Add(self.variables[train_id]['block_exit'][block] >= self.variables[train_id]['block_entry'][block] + block_traverse_time)

    def _add_spatial_constraints(self):
        # Block occupancy: no overlap between trains on same block
        for seg_id, blocks in self.blocks.items():
            for block in blocks:
                trains_using = []
                for t in self.trains:
                    tid = t['train']
                    if block in self.variables[tid]['block_entry']:
                        trains_using.append(tid)

                intervals = []
                for tid in trains_using:
                    size = self.model.NewIntVar(1, self.TIME_HORIZON, f'{tid}_{block}_size')
                    self.model.Add(size == self.variables[tid]['block_exit'][block] - self.variables[tid]['block_entry'][block])
                    interval = self.model.NewOptionalIntervalVar(self.variables[tid]['block_entry'][block], size, self.variables[tid]['block_exit'][block], self.variables[tid]['block_occupied'][block], f'{tid}_{block}_interval')
                    intervals.append(interval)

                if len(intervals) > 1:
                    self.model.AddNoOverlap(intervals)

        # Platform-level no-overlap per physical platform
        # First, create intervals per train-station-platform choice
        for train in self.trains:
            tid = train['train']
            for i, station in enumerate(train['route']):
                arrival = self.variables[tid]['arrival'][station]
                departure = self.variables[tid]['departure'][station]
                # compute size var
                size = self.model.NewIntVar(1, self.TIME_HORIZON, f'{tid}_{station}_plat_size')
                self.model.Add(size == departure - arrival)

                # if platform_choice exists for this station
                pchoices = self.variables[tid].get('platform_choice', {}).get(station)
                if pchoices:
                    for platform_id, bvar in pchoices.items():
                        interval = self.model.NewOptionalIntervalVar(arrival, size, departure, bvar, f'{tid}_{station}_{platform_id}_interval')
                        self.platform_intervals.setdefault(platform_id, []).append(interval)

        # Add fixed occupancy intervals (existing DB occupancy and platform maintenance) as non-optional intervals
        for rec in self.platform_occupancy:
            platform_id = rec.get('platform_id')
            start = rec.get('start_min')
            end = rec.get('end_min')
            if platform_id is None or start is None or end is None:
                continue
            size = max(1, end - start)
            fixed_interval = self.model.NewIntervalVar(start, size, end, f'fixed_{platform_id}_{start}')
            self.platform_intervals.setdefault(platform_id, []).append(fixed_interval)

        # now add no-overlap per platform
        for platform_id, intervals in self.platform_intervals.items():
            if len(intervals) > 1:
                self.model.AddNoOverlap(intervals)

    def _add_operational_constraints(self):
        # Example: connections (minimum transfer). Keep simple: min transfer 3 minutes.
        MIN_TRANSFER = 3
        # We will scan for trains that share a station and enforce ordering if they are connected (heuristic)
        for i in range(len(self.trains)):
            for j in range(i+1, len(self.trains)):
                t1 = self.trains[i]
                t2 = self.trains[j]
                # for each common station
                common = set(t1['route']).intersection(set(t2['route']))
                for station in common:
                    # ensure min headway on platform if same platform chosen
                    # This constraint is enforced by platform no-overlap & block no-overlap; keep additional headway per segment if specified in DB
                    pass

        # Apply per-segment headway from constraints collection if present
        for constr in self.constraints:
            if constr.get('type') == 'headway' and 'segment_id' in constr:
                seg = constr['segment_id']
                min_gap_sec = constr.get('min_gap_sec', None)
                if min_gap_sec is None:
                    continue
                min_gap_min = int(math.ceil(min_gap_sec/60.0))
                # for all trains that traverse this segment, enforce separation on first block
                blocks = self.blocks.get(seg, [])
                if not blocks:
                    continue
                block0 = blocks[0]
                trains_using = [t['train'] for t in self.trains if block0 in self.variables[t['train']]['block_entry']]
                # pairwise separation
                for a in range(len(trains_using)):
                    for b in range(a+1, len(trains_using)):
                        tA = trains_using[a]
                        tB = trains_using[b]
                        # ensure either A exits before B enters + headway or vice versa
                        boolAfirst = self.model.NewBoolVar(f'{tA}_{tB}_{seg}_Afirst')
                        self.model.Add(self.variables[tB]['block_entry'][block0] >= self.variables[tA]['block_exit'][block0] + min_gap_min).OnlyEnforceIf(boolAfirst)
                        self.model.Add(self.variables[tA]['block_entry'][block0] >= self.variables[tB]['block_exit'][block0] + min_gap_min).OnlyEnforceIf(boolAfirst.Not())

    def _define_objective(self):
        # minimize weighted sum of lateness (simple weights by type)
        total = []
        for train in self.trains:
            tid = train['train']
            weight = self.PRIORITY_WEIGHTS.get(train.get('type', 'local'), 5)
            for station in train['route']:
                delay = self.variables[tid]['delay'][station]
                late = self.model.NewIntVar(0, self.MAX_LATENESS*2, f'{tid}_{station}_late')
                neg_delay = self.model.NewIntVar(-self.MAX_LATENESS*2, 0, f'{tid}_{station}_neg')
                early = self.model.NewIntVar(0, self.MAX_EARLINESS, f'{tid}_{station}_early')
                self.model.Add(neg_delay == -delay)
                self.model.AddMaxEquality(late, [delay, 0])
                self.model.AddMaxEquality(early, [neg_delay, 0])
                total.append(weight * (2*late + early))
        self.model.Minimize(sum(total))

    def build_model(self):
        self._create_variables()
        self._add_temporal_constraints()
        self._add_spatial_constraints()
        self._add_operational_constraints()
        self._define_objective()

    def solve_model(self, time_limit=30):
        self.solver.parameters.max_time_in_seconds = time_limit
        self.solver.parameters.num_search_workers = 8
        status = self.solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self._extract_solution()
            self.objective_value = self.solver.ObjectiveValue()
            return True
        return False

    def _extract_solution(self):
        for train in self.trains:
            tid = train['train']
            self.solution[tid] = {
                'route': train['route'], 
                'actual_arrival': {}, 
                'actual_departure': {}, 
                'platform': {},
                'type': train.get('type', 'local')
            }
            for station in train['route']:
                self.solution[tid]['actual_arrival'][station] = self.solver.Value(self.variables[tid]['arrival'][station])
                self.solution[tid]['actual_departure'][station] = self.solver.Value(self.variables[tid]['departure'][station])
                # platform chosen
                pchoices = self.variables[tid].get('platform_choice', {}).get(station)
                if pchoices:
                    chosen = None
                    for p, b in pchoices.items():
                        if self.solver.Value(b) == 1:
                            chosen = p
                    self.solution[tid]['platform'][station] = chosen

    def get_solution(self):
        return {
            'trains': self.solution,
            'objective_value': self.objective_value,
            'scenario_id': self.scenario.get('_id') if self.scenario else None
        }
    
    def convert_solution_to_events(self):
        """Convert solution to train events format that can be stored back in MongoDB"""
        events = []
        
        if not self.solution or not self.origin_time:
            return events
            
        # For each train in the solution
        for train_id, train_data in self.solution.items():
            route = train_data.get('route', [])
            for station_id in route:
                # Create arrival event
                arrival_mins = train_data['actual_arrival'].get(station_id)
                if arrival_mins is not None:
                    arrival_time = self.origin_time + timedelta(minutes=arrival_mins)
                    platform_id = train_data['platform'].get(station_id)
                    
                    arrival_event = {
                        'train_id': train_id,
                        'event_id': f"{station_id}_arr",
                        'type': 'arrival',
                        'station_id': station_id,
                        'platform_id': platform_id,
                        'scheduled_time': arrival_time,
                        'actual_time': arrival_time,  # Initially same as scheduled
                        'status': 'scheduled'
                    }
                    events.append(arrival_event)
                
                # Create departure event
                departure_mins = train_data['actual_departure'].get(station_id)
                if departure_mins is not None:
                    departure_time = self.origin_time + timedelta(minutes=departure_mins)
                    platform_id = train_data['platform'].get(station_id)
                    
                    departure_event = {
                        'train_id': train_id,
                        'event_id': f"{station_id}_dep",
                        'type': 'departure',
                        'station_id': station_id,
                        'platform_id': platform_id,
                        'scheduled_time': departure_time,
                        'actual_time': departure_time,  # Initially same as scheduled
                        'status': 'scheduled'
                    }
                    events.append(departure_event)
                    
        return events

    def print_solution(self):
        print('\n' + '='*80)
        print('OPTIMIZATION RESULTS')
        print('='*80)
        for tid, sol in self.solution.items():
            print(f"Train {tid}:")
            for st in sol['route']:
                arr = sol['actual_arrival'][st]
                dep = sol['actual_departure'][st]
                plat = sol['platform'].get(st)
                print(f"  {st}: arr={arr} min, dep={dep} min, platform={plat}")