import { FileText, Search, Download, Filter, Calendar } from 'lucide-react';

const mockAuditData = [
  {
    id: 1,
    timestamp: '2024-01-15 14:23:12',
    user: 'Controller Smith',
    action: 'Schedule Modified',
    details: 'Changed Train RX-156 platform from 2 to 3',
    severity: 'info'
  },
  {
    id: 2,
    timestamp: '2024-01-15 14:21:45',
    user: 'AI System',
    action: 'Recommendation Generated',
    details: 'Route optimization for Train IC-204 to prevent delays',
    severity: 'info'
  },
  {
    id: 3,
    timestamp: '2024-01-15 14:19:33',
    user: 'Controller Johnson',
    action: 'Emergency Override',
    details: 'Manual delay applied to Train EC-891 due to track maintenance',
    severity: 'warning'
  },
  {
    id: 4,
    timestamp: '2024-01-15 14:15:22',
    user: 'System',
    action: 'Alert Triggered',
    details: 'Platform 2 overcapacity warning activated',
    severity: 'error'
  },
  {
    id: 5,
    timestamp: '2024-01-15 14:12:10',
    user: 'Controller Smith',
    action: 'Recommendation Accepted',
    details: 'Applied AI recommendation for Train DX-445 rerouting',
    severity: 'success'
  }
];

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'error': return 'text-destructive';
    case 'warning': return 'text-warning';
    case 'success': return 'text-success';
    default: return 'text-muted-foreground';
  }
};

const getSeverityBg = (severity: string) => {
  switch (severity) {
    case 'error': return 'bg-destructive/10';
    case 'warning': return 'bg-warning/10';
    case 'success': return 'bg-success/10';
    default: return 'bg-secondary/50';
  }
};

export const AuditTrailScreen = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <FileText className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Audit Trail</h1>
            <p className="text-muted-foreground">Complete system activity and change log</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="railway-btn-secondary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
          <button className="railway-btn-secondary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="control-panel p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search audit logs..."
              className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-lg"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <select className="px-3 py-2 bg-input border border-border rounded">
              <option>All Users</option>
              <option>Controller Smith</option>
              <option>Controller Johnson</option>
              <option>AI System</option>
            </select>
            <select className="px-3 py-2 bg-input border border-border rounded">
              <option>All Actions</option>
              <option>Schedule Changes</option>
              <option>Recommendations</option>
              <option>Alerts</option>
              <option>Overrides</option>
            </select>
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <input
                type="date"
                className="px-3 py-2 bg-input border border-border rounded"
                defaultValue="2024-01-15"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="control-panel p-4 text-center">
          <div className="text-2xl font-bold">248</div>
          <div className="text-sm text-muted-foreground">Total Events Today</div>
        </div>
        <div className="control-panel p-4 text-center">
          <div className="text-2xl font-bold text-success">182</div>
          <div className="text-sm text-muted-foreground">Normal Operations</div>
        </div>
        <div className="control-panel p-4 text-center">
          <div className="text-2xl font-bold text-warning">52</div>
          <div className="text-sm text-muted-foreground">Warnings</div>
        </div>
        <div className="control-panel p-4 text-center">
          <div className="text-2xl font-bold text-destructive">14</div>
          <div className="text-sm text-muted-foreground">Critical Events</div>
        </div>
        <div className="control-panel p-4 text-center">
          <div className="text-2xl font-bold text-primary">23</div>
          <div className="text-sm text-muted-foreground">Manual Overrides</div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="control-panel overflow-hidden">
        <div className="p-4 border-b border-border">
          <h3 className="text-lg font-semibold">Recent Activity</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-secondary/50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-muted-foreground">Timestamp</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-muted-foreground">User</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-muted-foreground">Action</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-muted-foreground">Details</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-muted-foreground">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockAuditData.map((log) => (
                <tr key={log.id} className="hover:bg-secondary/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-mono">{log.timestamp}</td>
                  <td className="px-6 py-4 text-sm font-medium">{log.user}</td>
                  <td className="px-6 py-4 text-sm">{log.action}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{log.details}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityBg(log.severity)} ${getSeverityColor(log.severity)}`}>
                      {log.severity.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="p-4 border-t border-border flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Showing 5 of 248 entries</span>
          <div className="flex items-center space-x-2">
            <button className="railway-btn-secondary text-sm">Previous</button>
            <span className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm">1</span>
            <span className="px-3 py-1 text-sm">2</span>
            <span className="px-3 py-1 text-sm">3</span>
            <button className="railway-btn-secondary text-sm">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};