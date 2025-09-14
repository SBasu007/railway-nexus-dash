import { AlertTriangle, Clock, CheckCircle, Info, X } from 'lucide-react';

const mockAlerts = [
  {
    id: 1,
    type: 'warning',
    title: 'Platform 2 Overcapacity',
    message: 'Platform 2 approaching maximum passenger capacity. Consider rerouting next arrival.',
    time: '2 minutes ago',
    severity: 'medium'
  },
  {
    id: 2,
    type: 'error',
    title: 'Signal System Fault',
    message: 'Signal S-204 showing intermittent failures. Maintenance team dispatched.',
    time: '5 minutes ago',
    severity: 'high'
  },
  {
    id: 3,
    type: 'info',
    title: 'Schedule Update',
    message: 'Train IC-204 departure advanced by 2 minutes to optimize flow.',
    time: '8 minutes ago',
    severity: 'low'
  },
  {
    id: 4,
    type: 'success',
    title: 'Delay Resolved',
    message: 'Train RX-156 delay cleared. Now running 1 minute ahead of schedule.',
    time: '12 minutes ago',
    severity: 'low'
  },
  {
    id: 5,
    type: 'warning',
    title: 'Weather Advisory',
    message: 'Light rain expected in 30 minutes. Reduced visibility protocols activated.',
    time: '15 minutes ago',
    severity: 'medium'
  }
];

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'error':
      return <AlertTriangle className="w-4 h-4 text-destructive" />;
    case 'warning':
      return <AlertTriangle className="w-4 h-4 text-warning" />;
    case 'success':
      return <CheckCircle className="w-4 h-4 text-success" />;
    default:
      return <Info className="w-4 h-4 text-primary" />;
  }
};

const getAlertColors = (type: string, severity: string) => {
  switch (type) {
    case 'error':
      return 'border-destructive/30 bg-destructive/10';
    case 'warning':
      return 'border-warning/30 bg-warning/10';
    case 'success':
      return 'border-success/30 bg-success/10';
    default:
      return 'border-primary/30 bg-primary/10';
  }
};

const getSeverityIndicator = (severity: string) => {
  switch (severity) {
    case 'high':
      return 'bg-destructive';
    case 'medium':
      return 'bg-warning';
    default:
      return 'bg-success';
  }
};

export const AlertFeed = () => {
  return (
    <div className="control-panel p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-warning" />
          <span>Active Alerts</span>
        </h3>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-destructive rounded-full animate-pulse"></div>
            <span className="text-xs text-muted-foreground">Live</span>
          </div>
        </div>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-center text-xs">
        <div className="p-2 bg-destructive/20 rounded">
          <div className="font-bold text-destructive">1</div>
          <div className="text-muted-foreground">Critical</div>
        </div>
        <div className="p-2 bg-warning/20 rounded">
          <div className="font-bold text-warning">2</div>
          <div className="text-muted-foreground">Warning</div>
        </div>
        <div className="p-2 bg-success/20 rounded">
          <div className="font-bold text-success">2</div>
          <div className="text-muted-foreground">Info</div>
        </div>
      </div>

      {/* Alert List */}
      <div className="flex-1 space-y-3 overflow-y-auto">
        {mockAlerts.map((alert) => (
          <div 
            key={alert.id} 
            className={`p-3 rounded-lg border ${getAlertColors(alert.type, alert.severity)} transition-all hover:shadow-md`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div className="flex-shrink-0 mt-0.5">
                  {getAlertIcon(alert.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-semibold truncate">{alert.title}</h4>
                    <div className={`w-1 h-1 rounded-full ${getSeverityIndicator(alert.severity)}`}></div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    {alert.message}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      <span>{alert.time}</span>
                    </div>
                  </div>
                </div>
              </div>
              <button className="ml-2 p-1 hover:bg-secondary/50 rounded text-muted-foreground hover:text-foreground transition-colors">
                <X className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="mt-4 pt-4 border-t border-border">
        <div className="flex items-center justify-between">
          <button className="text-xs text-muted-foreground hover:text-foreground">
            View All Alerts
          </button>
          <button className="text-xs railway-btn-secondary">
            Mark All Read
          </button>
        </div>
      </div>
    </div>
  );
};