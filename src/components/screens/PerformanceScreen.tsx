import { BarChart3, TrendingUp, Clock, Target, Calendar } from 'lucide-react';

export const PerformanceScreen = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Performance Dashboard</h1>
            <p className="text-muted-foreground">System performance metrics and analytics</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <select className="px-3 py-2 bg-input border border-border rounded">
            <option>Today</option>
            <option>This Week</option>
            <option>This Month</option>
            <option>Custom Range</option>
          </select>
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="control-panel p-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm text-muted-foreground">On-Time Performance</p>
              <p className="text-3xl font-bold text-success">94.2%</p>
            </div>
            <div className="p-3 bg-success/20 rounded-full">
              <Target className="w-6 h-6 text-success" />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-success" />
            <span className="text-sm text-success">+2.1% from yesterday</span>
          </div>
        </div>

        <div className="control-panel p-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm text-muted-foreground">Average Delay</p>
              <p className="text-3xl font-bold">3.2min</p>
            </div>
            <div className="p-3 bg-primary/20 rounded-full">
              <Clock className="w-6 h-6 text-primary" />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-success" />
            <span className="text-sm text-success">-0.8min improvement</span>
          </div>
        </div>

        <div className="control-panel p-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm text-muted-foreground">Throughput</p>
              <p className="text-3xl font-bold">142</p>
            </div>
            <div className="p-3 bg-warning/20 rounded-full">
              <BarChart3 className="w-6 h-6 text-warning" />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">trains per hour</span>
          </div>
        </div>

        <div className="control-panel p-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm text-muted-foreground">Efficiency Score</p>
              <p className="text-3xl font-bold text-primary">89.7</p>
            </div>
            <div className="p-3 bg-secondary/50 rounded-full">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-success" />
            <span className="text-sm text-success">+1.2 points today</span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Punctuality Trend */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Punctuality Trend (7 Days)</h3>
          <div className="bg-secondary/50 rounded-lg p-8 h-64 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <div className="text-4xl mb-4">📈</div>
              <p className="font-semibold">Line Chart</p>
              <p className="text-sm">7-day punctuality performance trend</p>
              <div className="mt-4 flex justify-center space-x-4 text-xs">
                <span className="text-success">● 94.2% Today</span>
                <span className="text-warning">● 91.8% Yesterday</span>
                <span className="text-muted-foreground">● 93.5% Week Avg</span>
              </div>
            </div>
          </div>
        </div>

        {/* Delay Histogram */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Delay Distribution</h3>
          <div className="bg-secondary/50 rounded-lg p-8 h-64 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <div className="text-4xl mb-4">📊</div>
              <p className="font-semibold">Histogram</p>
              <p className="text-sm">Distribution of delays by time ranges</p>
              <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
                <div className="bg-success/20 p-2 rounded">0-2min: 68%</div>
                <div className="bg-warning/20 p-2 rounded">2-5min: 22%</div>
                <div className="bg-destructive/20 p-2 rounded">5+min: 10%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Platform Utilization */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">Platform Utilization</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Platform 1</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-secondary/50 rounded-full h-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '78%' }}></div>
                </div>
                <span className="text-sm font-medium">78%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Platform 2</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-secondary/50 rounded-full h-2">
                  <div className="bg-warning h-2 rounded-full" style={{ width: '92%' }}></div>
                </div>
                <span className="text-sm font-medium">92%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Platform 3</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-secondary/50 rounded-full h-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
                <span className="text-sm font-medium">65%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Platform 4</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-secondary/50 rounded-full h-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '83%' }}></div>
                </div>
                <span className="text-sm font-medium">83%</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="control-panel p-6">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="status-indicator status-operational"></div>
                <span className="font-medium">Signaling System</span>
              </div>
              <span className="text-sm text-success">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="status-indicator status-operational"></div>
                <span className="font-medium">Communication Network</span>
              </div>
              <span className="text-sm text-success">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-warning/10 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="status-indicator status-delayed"></div>
                <span className="font-medium">Track Sensors</span>
              </div>
              <span className="text-sm text-warning">Degraded</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="status-indicator status-operational"></div>
                <span className="font-medium">Power Systems</span>
              </div>
              <span className="text-sm text-success">Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="control-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Daily Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-primary">1,247</div>
            <div className="text-sm text-muted-foreground">Total Trains</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-success">1,175</div>
            <div className="text-sm text-muted-foreground">On Time</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-warning">58</div>
            <div className="text-sm text-muted-foreground">Minor Delays</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-destructive">14</div>
            <div className="text-sm text-muted-foreground">Major Delays</div>
          </div>
          <div>
            <div className="text-2xl font-bold">3.2min</div>
            <div className="text-sm text-muted-foreground">Avg Delay</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-success">15</div>
            <div className="text-sm text-muted-foreground">Records Broken</div>
          </div>
        </div>
      </div>
    </div>
  );
};