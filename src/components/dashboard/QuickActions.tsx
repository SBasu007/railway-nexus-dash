import { 
  RefreshCw, 
  Undo2, 
  History, 
  AlertCircle, 
  Play, 
  Pause, 
  Settings,
  Download,
  Upload,
  Zap
} from 'lucide-react';

const quickActions = [
  {
    label: 'Refresh Data',
    icon: RefreshCw,
    color: 'primary',
    description: 'Update all live data'
  },
  {
    label: 'Undo Last Action',
    icon: Undo2,
    color: 'secondary',
    description: 'Revert previous change'
  },
  {
    label: 'View Changes',
    icon: History,
    color: 'secondary',
    description: 'Show recent modifications'
  },
  {
    label: 'Emergency Stop',
    icon: AlertCircle,
    color: 'destructive',
    description: 'Halt all operations'
  },
  {
    label: 'Auto Mode',
    icon: Play,
    color: 'success',
    description: 'Enable automatic control'
  },
  {
    label: 'Manual Override',
    icon: Pause,
    color: 'warning',
    description: 'Switch to manual control'
  }
];

const systemActions = [
  {
    label: 'Export Schedule',
    icon: Download,
    color: 'secondary'
  },
  {
    label: 'Import Config',
    icon: Upload,
    color: 'secondary'
  },
  {
    label: 'System Settings',
    icon: Settings,
    color: 'secondary'
  },
  {
    label: 'Power Status',
    icon: Zap,
    color: 'primary'
  }
];

const getButtonClasses = (color: string) => {
  switch (color) {
    case 'primary':
      return 'railway-btn-primary';
    case 'success':
      return 'railway-btn-success';
    case 'warning':
      return 'railway-btn-warning';
    case 'destructive':
      return 'railway-btn-danger';
    default:
      return 'railway-btn-secondary';
  }
};

export const QuickActions = () => {
  return (
    <div className="space-y-6">
      {/* Primary Actions */}
      <div className="control-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {quickActions.map((action, index) => {
            const IconComponent = action.icon;
            return (
              <button
                key={index}
                className={`${getButtonClasses(action.color)} flex flex-col items-center space-y-2 p-4 h-20 justify-center group relative`}
                title={action.description}
              >
                <IconComponent className="w-5 h-5" />
                <span className="text-xs font-medium text-center leading-tight">
                  {action.label}
                </span>
                
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-card border border-border rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  {action.description}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* System Status & Secondary Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Control Mode</span>
              <div className="flex items-center space-x-2">
                <div className="status-indicator status-operational"></div>
                <span className="text-sm font-medium text-success">Automatic</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Data Connection</span>
              <div className="flex items-center space-x-2">
                <div className="status-indicator status-operational"></div>
                <span className="text-sm font-medium text-success">Online</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Last Backup</span>
              <span className="text-sm text-muted-foreground">2 minutes ago</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Active Controllers</span>
              <span className="text-sm font-medium">3</span>
            </div>
          </div>
        </div>

        {/* Secondary Actions */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">System Tools</h3>
          <div className="grid grid-cols-2 gap-3">
            {systemActions.map((action, index) => {
              const IconComponent = action.icon;
              return (
                <button
                  key={index}
                  className={`${getButtonClasses(action.color)} flex items-center space-x-2 p-3 justify-start`}
                >
                  <IconComponent className="w-4 h-4" />
                  <span className="text-sm">{action.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};