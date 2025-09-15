import { Calendar, Save, Undo2, Redo2, AlertTriangle } from 'lucide-react';

export const ScheduleEditorScreen = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Calendar className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Schedule Editor</h1>
            <p className="text-muted-foreground">Interactive schedule management and editing</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="railway-btn-secondary flex items-center space-x-2">
            <Undo2 className="w-4 h-4" />
            <span>Undo</span>
          </button>
          <button className="railway-btn-secondary flex items-center space-x-2">
            <Redo2 className="w-4 h-4" />
            <span>Redo</span>
          </button>
          <button className="railway-btn-primary flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </button>
        </div>
      </div>

      {/* Validation Warnings */}
      <div className="control-panel p-4 border border-warning/30 bg-warning/10">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-warning" />
          <div>
            <h3 className="font-semibold text-warning">Schedule Conflicts Detected</h3>
            <p className="text-sm text-muted-foreground">2 platform conflicts and 1 timing overlap require attention</p>
          </div>
        </div>
      </div>

      {/* Editor Toolbar */}
      <div className="control-panel p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium mb-1">View Mode</label>
              <select className="px-3 py-1 bg-input border border-border rounded">
                <option>Timeline View</option>
                <option>Table View</option>
                <option>Track Diagram</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Time Range</label>
              <select className="px-3 py-1 bg-input border border-border rounded">
                <option>Next 4 Hours</option>
                <option>Next 8 Hours</option>
                <option>Full Day</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Filter</label>
              <select className="px-3 py-1 bg-input border border-border rounded">
                <option>All Trains</option>
                <option>Delayed Only</option>
                <option>Platform 1-3</option>
                <option>Express Trains</option>
              </select>
            </div>
          </div>
          <div className="text-sm text-muted-foreground">
            Last saved: 5 minutes ago
          </div>
        </div>
      </div>

      {/* Interactive Schedule Display */}
      <div className="control-panel p-6 h-96">
        <h3 className="text-lg font-semibold mb-4">Interactive Timeline Editor</h3>
        <div className="bg-secondary/50 rounded-lg p-8 h-full flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <div className="text-6xl mb-4">🚂</div>
            <h4 className="text-xl font-semibold mb-2">Interactive Gantt Chart Editor</h4>
            <p className="mb-4">Drag and drop train schedules, modify timings, and assign platforms</p>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="p-3 bg-card rounded">
                <div className="font-semibold">Train IC-204</div>
                <div className="text-muted-foreground">Platform 2, 14:30-14:35</div>
              </div>
              <div className="p-3 bg-card rounded border-2 border-warning">
                <div className="font-semibold">Train RX-156</div>
                <div className="text-warning text-xs">⚠️ Conflict</div>
                <div className="text-muted-foreground">Platform 2, 14:33-14:38</div>
              </div>
              <div className="p-3 bg-card rounded">
                <div className="font-semibold">Train EC-891</div>
                <div className="text-muted-foreground">Platform 3, 14:40-14:42</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Train Details Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Selected Train: RX-156</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Arrival Time</label>
                <input 
                  type="time" 
                  className="w-full px-3 py-2 bg-input border border-border rounded"
                  defaultValue="14:33"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Departure Time</label>
                <input 
                  type="time" 
                  className="w-full px-3 py-2 bg-input border border-border rounded"
                  defaultValue="14:38"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Platform Assignment</label>
              <select className="w-full px-3 py-2 bg-input border border-border rounded">
                <option>Platform 1</option>
                <option selected>Platform 2 ⚠️</option>
                <option>Platform 3</option>
                <option>Platform 4</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Route</label>
              <select className="w-full px-3 py-2 bg-input border border-border rounded">
                <option>Main Line</option>
                <option selected>Express Route</option>
                <option>Local Route</option>
              </select>
            </div>
          </div>
        </div>

        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Conflict Resolution</h3>
          <div className="space-y-4">
            <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-warning" />
                <span className="font-semibold text-warning">Platform Conflict</span>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Platform 2 is occupied by Train IC-204 from 14:30-14:35, conflicting with RX-156 arrival at 14:33
              </p>
              <div className="space-y-2">
                <button className="w-full railway-btn-success text-sm">
                  Move RX-156 to Platform 3
                </button>
                <button className="w-full railway-btn-secondary text-sm">
                  Delay RX-156 by 3 minutes
                </button>
                <button className="w-full railway-btn-secondary text-sm">
                  Advance IC-204 departure
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};