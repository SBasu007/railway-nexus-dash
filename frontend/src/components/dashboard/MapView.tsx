import { Map, Navigation, Zap, AlertCircle, CheckCircle } from 'lucide-react';

const mockTrackSections = [
  { id: 'A1', name: 'Platform 1 Approach', status: 'operational', trains: 1 },
  { id: 'A2', name: 'Platform 2 Approach', status: 'operational', trains: 2 },
  { id: 'A3', name: 'Platform 3 Approach', status: 'maintenance', trains: 0 },
  { id: 'B1', name: 'Main Junction East', status: 'operational', trains: 3 },
  { id: 'B2', name: 'Main Junction West', status: 'delayed', trains: 1 },
  { id: 'C1', name: 'Express Route', status: 'operational', trains: 2 },
];

const mockTrainPositions = [
  { id: 'IC-204', x: 15, y: 25, status: 'moving', direction: 'east' },
  { id: 'RX-156', x: 45, y: 45, status: 'stopped', direction: 'west' },
  { id: 'EC-891', x: 70, y: 25, status: 'moving', direction: 'east' },
  { id: 'DX-445', x: 25, y: 65, status: 'moving', direction: 'north' },
];

const getTrackStatusColor = (status: string) => {
  switch (status) {
    case 'operational': return 'stroke-success';
    case 'delayed': return 'stroke-warning';
    case 'maintenance': return 'stroke-destructive';
    default: return 'stroke-muted-foreground';
  }
};

export const MapView = () => {
  return (
    <div className="control-panel p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center space-x-2">
          <Map className="w-5 h-5 text-primary" />
          <span>Railway Section Overview</span>
        </h3>
        <div className="flex items-center space-x-2">
          <Navigation className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Central Section</span>
        </div>
      </div>

      <div className="relative bg-secondary/30 rounded-lg p-4 h-64 overflow-hidden">
        {/* SVG Railway Map */}
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {/* Track Lines */}
          <g className="tracks">
            {/* Main horizontal tracks */}
            <line x1="5" y1="20" x2="95" y2="20" className="stroke-success stroke-2" strokeDasharray="none" />
            <line x1="5" y1="30" x2="95" y2="30" className="stroke-success stroke-2" strokeDasharray="none" />
            <line x1="5" y1="40" x2="95" y2="40" className="stroke-warning stroke-2" strokeDasharray="none" />
            <line x1="5" y1="50" x2="95" y2="50" className="stroke-destructive stroke-2" strokeDasharray="5,5" />
            
            {/* Junction connections */}
            <line x1="30" y1="20" x2="30" y2="70" className="stroke-success stroke-2" />
            <line x1="70" y1="20" x2="70" y2="70" className="stroke-success stroke-2" />
            
            {/* Platform areas */}
            <rect x="10" y="75" width="15" height="8" className="fill-primary/30 stroke-primary stroke-1" rx="2" />
            <rect x="30" y="75" width="15" height="8" className="fill-primary/30 stroke-primary stroke-1" rx="2" />
            <rect x="50" y="75" width="15" height="8" className="fill-warning/30 stroke-warning stroke-1" rx="2" />
            <rect x="70" y="75" width="15" height="8" className="fill-primary/30 stroke-primary stroke-1" rx="2" />
          </g>
          
          {/* Train Positions */}
          {mockTrainPositions.map((train) => (
            <g key={train.id}>
              {/* Train Icon */}
              <circle 
                cx={train.x} 
                cy={train.y} 
                r="3" 
                className={`${train.status === 'moving' ? 'fill-primary' : 'fill-warning'} animate-pulse`}
              />
              {/* Train Label */}
              <text 
                x={train.x} 
                y={train.y - 5} 
                className="fill-foreground text-xs font-medium" 
                textAnchor="middle"
                fontSize="3"
              >
                {train.id}
              </text>
              {/* Direction Indicator */}
              {train.status === 'moving' && (
                <polygon 
                  points={`${train.x + 4},${train.y} ${train.x + 6},${train.y - 2} ${train.x + 6},${train.y + 2}`}
                  className="fill-primary"
                />
              )}
            </g>
          ))}
          
          {/* Platform Labels */}
          <text x="17.5" y="88" className="fill-foreground text-xs" textAnchor="middle" fontSize="3">P1</text>
          <text x="37.5" y="88" className="fill-foreground text-xs" textAnchor="middle" fontSize="3">P2</text>
          <text x="57.5" y="88" className="fill-foreground text-xs" textAnchor="middle" fontSize="3">P3</text>
          <text x="77.5" y="88" className="fill-foreground text-xs" textAnchor="middle" fontSize="3">P4</text>
        </svg>

        {/* Status Overlays */}
        <div className="absolute top-4 right-4 space-y-2">
          <div className="flex items-center space-x-2 bg-card/80 backdrop-blur-sm px-2 py-1 rounded text-xs">
            <Zap className="w-3 h-3 text-success" />
            <span>Power: Normal</span>
          </div>
          <div className="flex items-center space-x-2 bg-card/80 backdrop-blur-sm px-2 py-1 rounded text-xs">
            <AlertCircle className="w-3 h-3 text-warning" />
            <span>P3: Maintenance</span>
          </div>
        </div>
      </div>

      {/* Track Status Legend */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3">
        {mockTrackSections.map((section) => (
          <div key={section.id} className="flex items-center justify-between p-2 bg-secondary/50 rounded">
            <div className="flex items-center space-x-2">
              {section.status === 'operational' ? (
                <CheckCircle className="w-4 h-4 text-success" />
              ) : section.status === 'delayed' ? (
                <AlertCircle className="w-4 h-4 text-warning" />
              ) : (
                <AlertCircle className="w-4 h-4 text-destructive" />
              )}
              <div>
                <div className="text-sm font-medium">{section.name}</div>
                <div className="text-xs text-muted-foreground">{section.trains} train(s)</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};