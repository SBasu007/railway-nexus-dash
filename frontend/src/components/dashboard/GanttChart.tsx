import { useQuery } from '@tanstack/react-query';
import { Clock, Train, MapPin } from 'lucide-react';
import { timetableService } from '../../api';

// Mock data for fallback
const mockTrains = [
  { id: 'IC-204', platform: 2, arrival: '14:30', departure: '14:35', status: 'on-time', route: 'Main Line' },
  { id: 'RX-156', platform: 3, arrival: '14:33', departure: '14:38', status: 'delayed', route: 'Express' },
  { id: 'EC-891', platform: 1, arrival: '14:40', departure: '14:42', status: 'on-time', route: 'Local' },
  { id: 'DX-445', platform: 4, arrival: '14:45', departure: '14:50', status: 'early', route: 'Main Line' },
  { id: 'LX-789', platform: 2, arrival: '14:55', departure: '15:00', status: 'on-time', route: 'Express' },
];

// Function to fetch timetable data from the API
const fetchTimetableData = async () => {
  try {
    // Get current date in YYYY-MM-DD format
    const today = new Date().toISOString().split('T')[0];
    const response = await timetableService.getTimetable({ date: today });
    
    // Transform API response to match our component's data structure
    return response.entries.map(entry => ({
      id: entry.train_id,
      platform: entry.platform_id ? parseInt(entry.platform_id.replace('P', '')) : 1,
      arrival: new Date(entry.arrival_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      departure: new Date(entry.departure_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      status: entry.status.toLowerCase(),
      route: 'Main Line', // This would come from a join with train data in a real app
    }));
  } catch (error) {
    console.error('Failed to fetch timetable data:', error);
    return mockTrains;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'on-time': return 'bg-success';
    case 'delayed': return 'bg-warning';
    case 'early': return 'bg-primary';
    default: return 'bg-secondary';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'on-time': return 'On Time';
    case 'delayed': return 'Delayed';
    case 'early': return 'Early';
    default: return 'Unknown';
  }
};

export const GanttChart = () => {
  // Use React Query to fetch timetable data
  const { data: trains, isLoading, error } = useQuery({
    queryKey: ['timetable'],
    queryFn: fetchTimetableData,
    // Keep data fresh for 15 seconds
    staleTime: 15000,
    // Refresh data every minute
    refetchInterval: 60000,
  });

  // Use mock data as fallback if there's an error, data is loading, or data is undefined
  const displayTrains = error || isLoading || !trains ? mockTrains : trains;

  // Get the current time for display
  const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

  return (
    <div className="control-panel p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center space-x-2">
          <Clock className="w-5 h-5 text-primary" />
          <span>Live Schedule Timeline</span>
        </h3>
        <div className="text-xs text-muted-foreground">
          Current Time: {currentTime}
        </div>
      </div>

      <div className="space-y-3">
        {/* Timeline Header */}
        <div className="flex items-center text-xs text-muted-foreground border-b border-border pb-2">
          <div className="w-20">Train</div>
          <div className="w-16">Platform</div>
          <div className="flex-1 ml-4">Timeline (14:30 - 15:00)</div>
          <div className="w-20">Status</div>
        </div>

        {/* Train Schedules */}
        {displayTrains.map((train) => (
          <div key={train.id} className="flex items-center py-2 hover:bg-secondary/30 rounded-lg transition-colors">
            <div className="w-20">
              <div className="flex items-center space-x-1">
                <Train className="w-3 h-3 text-primary" />
                <span className="text-sm font-medium">{train.id}</span>
              </div>
            </div>
            
            <div className="w-16">
              <div className="flex items-center space-x-1">
                <MapPin className="w-3 h-3 text-muted-foreground" />
                <span className="text-sm">{train.platform}</span>
              </div>
            </div>
            
            <div className="flex-1 ml-4 relative">
              {/* Timeline Background */}
              <div className="bg-secondary/50 h-6 rounded-full relative overflow-hidden">
                {/* Train Schedule Block */}
                <div 
                  className={`absolute h-full rounded-full ${getStatusColor(train.status)} opacity-80 flex items-center px-2`}
                  style={{
                    left: `${((parseInt(train.arrival.split(':')[1]) - 30) / 30) * 100}%`,
                    width: `${((parseInt(train.departure.split(':')[1]) - parseInt(train.arrival.split(':')[1])) / 30) * 100}%`
                  }}
                >
                  <span className="text-xs font-medium text-white">
                    {train.arrival} - {train.departure}
                  </span>
                </div>
                
                {/* Current Time Indicator */}
                <div 
                  className="absolute top-0 w-0.5 h-full bg-destructive"
                  style={{ left: '20%' }}
                ></div>
              </div>
            </div>
            
            <div className="w-20">
              <span className={`text-xs px-2 py-1 rounded-full ${
                train.status === 'on-time' ? 'bg-success/20 text-success' :
                train.status === 'delayed' ? 'bg-warning/20 text-warning' :
                train.status === 'early' ? 'bg-primary/20 text-primary' :
                'bg-secondary/50 text-muted-foreground'
              }`}>
                {getStatusText(train.status)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-border">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-success rounded"></div>
              <span>On Time</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-warning rounded"></div>
              <span>Delayed</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-primary rounded"></div>
              <span>Early</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-0.5 h-4 bg-destructive"></div>
              <span>Current Time</span>
            </div>
          </div>
          <button className="railway-btn-secondary text-xs">View Full Timeline</button>
        </div>
      </div>
    </div>
  );
};