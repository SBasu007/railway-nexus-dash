import { GitCompare, Play, Save, Upload } from 'lucide-react';

export const ScenarioAnalysisScreen = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <GitCompare className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Scenario Analysis</h1>
            <p className="text-muted-foreground">Compare different operational scenarios</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="railway-btn-secondary flex items-center space-x-2">
            <Upload className="w-4 h-4" />
            <span>Load Scenario</span>
          </button>
          <button className="railway-btn-primary flex items-center space-x-2">
            <Play className="w-4 h-4" />
            <span>Run Analysis</span>
          </button>
        </div>
      </div>

      {/* Scenario Creator */}
      <div className="control-panel p-6">
        <h2 className="text-xl font-semibold mb-4">Create New Scenario</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Scenario Name</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 bg-input border border-border rounded-lg"
              placeholder="Emergency Reroute Scenario"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Time Period</label>
            <select className="w-full px-3 py-2 bg-input border border-border rounded-lg">
              <option>Next 2 hours</option>
              <option>Next 4 hours</option>
              <option>Next 8 hours</option>
              <option>Full day</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Scenario Type</label>
            <select className="w-full px-3 py-2 bg-input border border-border rounded-lg">
              <option>Track Maintenance</option>
              <option>Emergency Delay</option>
              <option>Peak Hour Optimization</option>
              <option>Weather Impact</option>
            </select>
          </div>
        </div>
      </div>

      {/* Comparison View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Schedule */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Current Schedule</h3>
          <div className="space-y-4">
            <div className="bg-secondary/50 rounded-lg p-4">
              <div className="text-center text-muted-foreground">
                <div className="text-4xl mb-2">📊</div>
                <p>Current schedule visualization</p>
                <p className="text-sm">Gantt chart would be displayed here</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-success">94%</div>
                <div className="text-sm text-muted-foreground">On Time</div>
              </div>
              <div>
                <div className="text-2xl font-bold">3.2min</div>
                <div className="text-sm text-muted-foreground">Avg Delay</div>
              </div>
              <div>
                <div className="text-2xl font-bold">142</div>
                <div className="text-sm text-muted-foreground">Trains/Hour</div>
              </div>
            </div>
          </div>
        </div>

        {/* Scenario Comparison */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Scenario: Emergency Reroute</h3>
          <div className="space-y-4">
            <div className="bg-secondary/50 rounded-lg p-4">
              <div className="text-center text-muted-foreground">
                <div className="text-4xl mb-2">📈</div>
                <p>Scenario visualization</p>
                <p className="text-sm">Modified schedule would be displayed here</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-warning">87%</div>
                <div className="text-sm text-muted-foreground">On Time</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-warning">5.8min</div>
                <div className="text-sm text-muted-foreground">Avg Delay</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-destructive">128</div>
                <div className="text-sm text-muted-foreground">Trains/Hour</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Comparison */}
      <div className="control-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Impact Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-secondary/50 rounded-lg">
            <div className="text-2xl font-bold text-destructive">-7%</div>
            <div className="text-sm text-muted-foreground">Punctuality Change</div>
          </div>
          <div className="text-center p-4 bg-secondary/50 rounded-lg">
            <div className="text-2xl font-bold text-destructive">+2.6min</div>
            <div className="text-sm text-muted-foreground">Delay Increase</div>
          </div>
          <div className="text-center p-4 bg-secondary/50 rounded-lg">
            <div className="text-2xl font-bold text-destructive">-14</div>
            <div className="text-sm text-muted-foreground">Throughput Loss</div>
          </div>
          <div className="text-center p-4 bg-secondary/50 rounded-lg">
            <div className="text-2xl font-bold text-success">2</div>
            <div className="text-sm text-muted-foreground">Conflicts Resolved</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-3">
        <button className="railway-btn-success flex items-center space-x-2">
          <Save className="w-4 h-4" />
          <span>Save Scenario</span>
        </button>
        <button className="railway-btn-primary">Apply to Schedule</button>
        <button className="railway-btn-secondary">Export Report</button>
      </div>
    </div>
  );
};