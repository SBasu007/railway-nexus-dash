import { GanttChart } from '../dashboard/GanttChart';
import { MapView } from '../dashboard/MapView';
import { KPIPanel } from '../dashboard/KPIPanel';
import { AlertFeed } from '../dashboard/AlertFeed';
import { QuickActions } from '../dashboard/QuickActions';

export const MainDashboard = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Railway Traffic Control</h1>
          <p className="text-muted-foreground">Central Section - Real-time Operations Dashboard</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="status-indicator status-operational"></div>
          <span className="text-sm font-medium text-success">All Systems Operational</span>
        </div>
      </div>

      {/* KPI Row */}
      <KPIPanel />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-96">
        {/* Gantt Chart - Takes 2/3 of space */}
        <div className="lg:col-span-2">
          <GanttChart />
        </div>
        
        {/* Alert Feed - Takes 1/3 of space */}
        <div className="lg:col-span-1">
          <AlertFeed />
        </div>
      </div>

      {/* Map View */}
      <div className="h-80">
        <MapView />
      </div>

      {/* Quick Actions */}
      <QuickActions />
    </div>
  );
};