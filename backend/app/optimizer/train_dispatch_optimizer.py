"""
Train Dispatch Optimizer with platform-level handling, Mongo adapter integration, and segment throughput analysis.
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
        print("\n" + "="*60)
        print("DEBUG: LOADING DATA FROM ADAPTER")
        print("="*60)
        
        self.trains = data.get('trains', [])
        self.stations_data = data.get('stations', {})
        self.segments = data.get('segments', {})
        self.constraints = data.get('constraints', [])
        self.platform_occupancy = data.get('platform_occupancy', [])
        self.origin_time = data.get('origin_time')
        self.scenario = data.get('scenario')

        print(f"DEBUG: Loaded {len(self.trains)} trains")
        print(f"DEBUG: Loaded {len(self.segments)} segments")
        print(f"DEBUG: Loaded {len(self.constraints)} constraints")

        # Process speed restrictions and update segment data
        speed_restrictions_found = 0
        print(f"\nDEBUG: PROCESSING SPEED RESTRICTIONS...")
        
        for constraint in self.constraints:
            if constraint.get('type') == 'speed_restriction':
                speed_restrictions_found += 1
                segment_id = constraint['segment_id']
                max_speed = constraint.get('max_speed_kmh')
                reason = constraint.get('reason', 'unknown')
                
                print(f"DEBUG: Found speed restriction #{speed_restrictions_found}:")
                print(f"       Segment: {segment_id}, Max Speed: {max_speed} km/h, Reason: {reason}")
                
                if segment_id in self.segments:
                    # Store speed restriction info in segment data
                    self.segments[segment_id]['speed_restriction'] = {
                        'max_speed_kmh': max_speed,
                        'reason': reason,
                        'active': True
                    }
                    print(f"       ✓ Applied to segment {segment_id}")
                else:
                    print(f"       ✗ WARNING - Segment {segment_id} not found")
        
        print(f"DEBUG: Found {speed_restrictions_found} speed restrictions")

        # set TIME_HORIZON from latest planned time
        latest = 0
        for t in self.trains:
            if t['planned']:
                latest = max(latest, max(t['planned']))
        self.TIME_HORIZON = max(self.TIME_HORIZON, latest + 120)

        # Create blocks per segment
        print(f"\nDEBUG: CREATING BLOCKS FOR SEGMENTS...")
        for seg_id, seg_doc in self.segments.items():
            # create block ids
            self.blocks[seg_id] = [f"{seg_id}_B{i+1}" for i in range(3)]
            print(f"DEBUG: Segment {seg_id} -> Blocks: {self.blocks[seg_id]}")
            
            # Show if speed restricted
            if seg_doc.get('speed_restriction', {}).get('active'):
                sr = seg_doc['speed_restriction']
                print(f"       ⚠️  SPEED RESTRICTED: {sr['max_speed_kmh']} km/h ({sr['reason']})")

        print("DEBUG: Data loading completed\n")

    def _uses_segment(self, train, segment_id):
        """Helper method to check if a train uses a specific segment"""
        train_id = train['train']
        blocks = self.blocks.get(segment_id, [])
        
        for block in blocks:
            if block in self.variables[train_id].get('block_entry', {}):
                return True
        return False

    def _create_variables(self):
        print("\nDEBUG: Creating optimization variables...")
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
        """Add temporal constraints per train/station"""
        print("\nDEBUG: Adding flexible temporal constraints...")
        
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

                # FIXED: Flexible travel between stations
                if i > 0:
                    prev_station = train['route'][i-1]
                    # Use minimum realistic travel time instead of rigid planned time
                    min_travel = 1  # Minimum 1 minute travel between stations
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

                        # **FIXED: Check if segment has speed restrictions**
                        segment_doc = self.segments[seg_id]
                        speed_restricted = segment_doc.get('speed_restriction', {}).get('active', False)
                        
                        if speed_restricted:
                            # Speed restriction exists - DON'T add individual block traverse times
                            # Let the speed restriction constraint handle the timing
                            restricted_speed = segment_doc['speed_restriction']['max_speed_kmh']
                            reason = segment_doc['speed_restriction']['reason']
                            print(f"DEBUG: Train {train_id} on segment {seg_id} - SPEED RESTRICTED to {restricted_speed} km/h ({reason})")
                            print(f"       Skipping individual block times - speed restriction will handle timing")
                            
                        else:
                            # FIXED: Use flexible block traverse time constraints
                            min_block_time = 1  # Minimum 1 minute per block for flexibility
                            print(f"DEBUG: Train {train_id} on segment {seg_id} - Flexible timing, min block time: {min_block_time} min each")
                            
                            # Add flexible block traverse time constraints
                            for block in blocks:
                                self.model.Add(self.variables[train_id]['block_exit'][block] >= 
                                             self.variables[train_id]['block_entry'][block] + min_block_time)

    def _add_spatial_constraints(self):
        print("\nDEBUG: Adding spatial constraints...")
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
        print("\nDEBUG: Adding operational constraints...")
        # Apply per-segment headway from constraints collection if present
        headway_constraints = 0
        for constr in self.constraints:
            if constr.get('type') == 'headway' and 'segment_id' in constr:
                headway_constraints += 1
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
        
        print(f"DEBUG: Added {headway_constraints} headway constraints")

    def _add_speed_restrictions(self):
        """Handle temporary and permanent speed restrictions on segments"""
        print("\n" + "="*60)
        print("DEBUG: ADDING SPEED RESTRICTION CONSTRAINTS")
        print("="*60)
        
        restrictions_applied = 0
        for constraint in self.constraints:
            if constraint.get('type') == 'speed_restriction':
                print(f"\nDEBUG: Processing speed restriction constraint #{restrictions_applied + 1}")
                
                segment_id = constraint['segment_id']
                max_speed_kmh = constraint.get('max_speed_kmh', self.MAX_SPEED)
                
                # Get segment details
                segment_doc = self.segments.get(segment_id)
                if not segment_doc:
                    print(f"       ✗ ERROR - Segment {segment_id} not found")
                    continue
                    
                # Calculate minimum traverse time based on speed restriction
                distance_m = segment_doc.get('distance_m', 1000)
                distance_km = distance_m / 1000.0
                
                min_traverse_hours = distance_km / max_speed_kmh
                min_traverse_min = max(1, int(math.ceil(min_traverse_hours * 60)))
                
                print(f"       Distance: {distance_km} km, Max speed: {max_speed_kmh} km/h")
                print(f"       Min traverse time: {min_traverse_min} minutes")
                
                # Apply to all trains using this segment
                blocks = self.blocks.get(segment_id, [])
                if not blocks:
                    continue
                    
                # Find all trains that traverse this segment
                affected_trains = []
                for train in self.trains:
                    train_id = train['train']
                    # Check if train uses any block in this segment
                    for block in blocks:
                        if block in self.variables[train_id].get('block_entry', {}):
                            affected_trains.append(train_id)
                            break
                
                print(f"       Affected trains: {affected_trains}")
                
                # Apply speed restriction to each affected train
                for train_id in affected_trains:
                    if len(blocks) > 0:
                        first_block = blocks[0]
                        last_block = blocks[-1]
                        
                        # Total segment traverse time must be >= min_traverse_min
                        self.model.Add(
                            self.variables[train_id]['block_exit'][last_block] >= 
                            self.variables[train_id]['block_entry'][first_block] + min_traverse_min
                        )
                        print(f"       Added constraint: {train_id} segment time >= {min_traverse_min} min")
                
                restrictions_applied += 1
        
        print(f"\nDEBUG: Applied {restrictions_applied} speed restriction constraints")
        print("="*60 + "\n")

    def _define_objective(self):
        print("\nDEBUG: Defining objective function...")
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
        print("\n" + "="*80)
        print("DEBUG: BUILDING OPTIMIZATION MODEL")
        print("="*80)
        
        self._create_variables()
        self._add_temporal_constraints()
        self._add_spatial_constraints()
        self._add_operational_constraints()
        self._add_speed_restrictions()  # Add speed restrictions
        self._define_objective()
        
        print("DEBUG: Model building completed")
        print("="*80)

    def solve_model(self, time_limit=300):
        print(f"\nDEBUG: Solving model with {time_limit}s time limit...")
        self.solver.parameters.max_time_in_seconds = time_limit
        self.solver.parameters.log_search_progress = True  # Enable detailed logs
        self.solver.parameters.num_search_workers = 1      # Single worker for clarity
        self.solver.parameters.random_seed = 1             # Reproducible results
        
        status = self.solver.Solve(self.model)
        
        if status == cp_model.INFEASIBLE:
            print("DEBUG: ❌ MODEL IS INFEASIBLE")
            print("Check the detailed solver output above for constraint violations")
        elif status == cp_model.OPTIMAL:
            print("DEBUG: ✅ OPTIMAL solution found")
        elif status == cp_model.FEASIBLE:
            print("DEBUG: ✅ FEASIBLE solution found")
        else:
            print(f"DEBUG: ❌ No solution found. Status code: {status}")
            
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

    # NEW: Calculate delay metrics after solving
    def calculate_delay_metrics(self):
        """Calculate comprehensive delay metrics after solving the optimization"""
        if not self.solution:
            return {}
        
        delays = []
        delays_by_type = {}
        delays_by_train = {}
        
        for train in self.trains:
            tid = train['train']
            train_type = train.get('type', 'local')
            train_delays = []
            
            for station in train['route']:
                # Extract the delay value from the solved model
                delay_val = self.solver.Value(self.variables[tid]['delay'][station])
                delays.append(delay_val)
                train_delays.append(delay_val)
                
                # Group by train type
                if train_type not in delays_by_type:
                    delays_by_type[train_type] = []
                delays_by_type[train_type].append(delay_val)
            
            delays_by_train[tid] = {
                'delays': train_delays,
                'avg_delay': sum(train_delays) / len(train_delays) if train_delays else 0,
                'max_delay': max(train_delays) if train_delays else 0,
                'type': train_type
            }
        
        # Calculate overall metrics
        metrics = {
            'overall_avg_delay': sum(delays) / len(delays) if delays else 0,
            'overall_max_delay': max(delays) if delays else 0,
            'overall_min_delay': min(delays) if delays else 0,
            'total_events': len(delays),
            'delays_by_type': {},
            'delays_by_train': delays_by_train
        }
        
        # Calculate averages by train type
        for train_type, type_delays in delays_by_type.items():
            metrics['delays_by_type'][train_type] = {
                'avg_delay': sum(type_delays) / len(type_delays),
                'max_delay': max(type_delays),
                'min_delay': min(type_delays),
                'count': len(type_delays)
            }
        
        return metrics

    # NEW: Calculate segment throughput metrics
    def calculate_segment_throughput(self):
        """Calculate comprehensive throughput metrics for each segment"""
        if not self.solution:
            return {}
            
        throughput = {}
        
        for seg_id in self.segments.keys():
            segment_data = {
                'total_trains': 0,
                'trains_by_type': {},
                'train_list': [],
                'avg_traverse_time': 0,
                'segment_utilization': 0
            }
            
            blocks = self.blocks.get(seg_id, [])
            traverse_times = []
            
            # Count trains using this segment
            for train in self.trains:
                tid = train['train']
                train_type = train.get('type', 'local')
                
                # Check if train uses any block in this segment
                uses_segment = False
                for block in blocks:
                    if block in self.variables[tid].get('block_entry', {}):
                        uses_segment = True
                        break
                
                if uses_segment:
                    segment_data['total_trains'] += 1
                    segment_data['train_list'].append(tid)
                    
                    # Count by train type
                    if train_type not in segment_data['trains_by_type']:
                        segment_data['trains_by_type'][train_type] = 0
                    segment_data['trains_by_type'][train_type] += 1
                    
                    # Calculate traverse time if blocks exist
                    if blocks:
                        first_block = blocks[0]
                        last_block = blocks[-1]
                        if (first_block in self.variables[tid].get('block_entry', {}) and 
                            last_block in self.variables[tid].get('block_exit', {})):
                            entry_time = self.solver.Value(self.variables[tid]['block_entry'][first_block])
                            exit_time = self.solver.Value(self.variables[tid]['block_exit'][last_block])
                            traverse_time = exit_time - entry_time
                            traverse_times.append(traverse_time)
            
            # Calculate average traverse time
            if traverse_times:
                segment_data['avg_traverse_time'] = sum(traverse_times) / len(traverse_times)
            
            # Calculate utilization as percentage of time horizon used
            if traverse_times and self.TIME_HORIZON > 0:
                total_usage_time = sum(traverse_times)
                segment_data['segment_utilization'] = (total_usage_time / self.TIME_HORIZON) * 100
            
            throughput[seg_id] = segment_data
        
        return throughput

    # NEW: Simple method to get real average delay
    def get_real_average_delay(self):
        """Get actual average delay in minutes (unweighted)"""
        if not hasattr(self, 'solver') or not self.solution:
            return 0
        
        total_delay = 0
        event_count = 0
        
        for train in self.trains:
            tid = train['train']
            for station in train['route']:
                # Raw delay value from solver (positive = late, negative = early)
                delay_minutes = self.solver.Value(self.variables[tid]['delay'][station])
                total_delay += delay_minutes
                event_count += 1
        
        return total_delay / event_count if event_count > 0 else 0

    def get_solution(self):
        delay_metrics = self.calculate_delay_metrics()
        throughput_metrics = self.calculate_segment_throughput()  # NEW: Add throughput metrics
        
        return {
            'trains': self.solution,
            'objective_value': self.objective_value,
            'scenario_id': self.scenario.get('_id') if self.scenario else None,
            'delay_metrics': delay_metrics,
            'throughput_metrics': throughput_metrics,  # NEW: Add throughput data
            'avg_delay': delay_metrics.get('overall_avg_delay', 0)
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
        
        delay_metrics = self.calculate_delay_metrics()
        
        # Print train-by-train results
        for tid, sol in self.solution.items():
            train_delays = delay_metrics['delays_by_train'][tid]
            print(f"Train {tid} ({sol['type']}) - Avg Delay: {train_delays['avg_delay']:.1f} min:")
            for st in sol['route']:
                arr = sol['actual_arrival'][st]
                dep = sol['actual_departure'][st]
                plat = sol['platform'].get(st)
                delay = self.solver.Value(self.variables[tid]['delay'][st])
                print(f"  {st}: arr={arr} min, dep={dep} min, platform={plat}, delay={delay} min")
        
        # Print delay summary
        print('\n' + '='*80)
        print('DELAY SUMMARY')
        print('='*80)
        print(f"Overall Average Delay: {delay_metrics['overall_avg_delay']:.2f} minutes")
        print(f"Maximum Delay: {delay_metrics['overall_max_delay']} minutes")
        print(f"Minimum Delay: {delay_metrics['overall_min_delay']} minutes")
        print(f"Total Events: {delay_metrics['total_events']}")
        print(f"Objective Value: {self.objective_value}")
        
        print('\nDelays by Train Type:')
        for train_type, type_metrics in delay_metrics['delays_by_type'].items():
            print(f"  {train_type}: avg={type_metrics['avg_delay']:.2f} min, "
                  f"max={type_metrics['max_delay']} min, min={type_metrics['min_delay']} min, events={type_metrics['count']}")
        
        # NEW: Print throughput summary
        throughput_metrics = self.calculate_segment_throughput()
        print('\n' + '='*80)
        print('SEGMENT THROUGHPUT ANALYSIS')
        print('='*80)
        for seg_id, seg_data in throughput_metrics.items():
            print(f"Segment {seg_id}:")
            print(f"  Total Trains: {seg_data['total_trains']}")
            print(f"  Train Types: {dict(seg_data['trains_by_type'])}")
            print(f"  Avg Traverse Time: {seg_data['avg_traverse_time']:.1f} minutes")
            print(f"  Segment Utilization: {seg_data['segment_utilization']:.1f}%")
            print(f"  Trains: {', '.join(seg_data['train_list'])}")
            print()
        print('='*80)
