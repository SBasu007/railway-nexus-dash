import { Brain, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';

const mockRecommendations = [
  {
    id: 1,
    priority: 'high',
    title: 'Delay Prevention - Route Optimization',
    description: 'Reroute Train IC-204 through Platform 3 to prevent 8-minute delay cascade',
    impact: 'Prevents delays for 3 subsequent trains',
    confidence: 94,
    estimatedSaving: '12 minutes',
    conflictsWith: []
  },
  {
    id: 2,
    priority: 'medium',
    title: 'Platform Assignment Change',
    description: 'Move Train RX-156 from Platform 2 to Platform 4 for better passenger flow',
    impact: 'Reduces platform congestion by 40%',
    confidence: 87,
    estimatedSaving: '5 minutes',
    conflictsWith: ['recommendation-5']
  },
  {
    id: 3,
    priority: 'low',
    title: 'Schedule Adjustment',
    description: 'Advance departure of Train EC-891 by 3 minutes to optimize track usage',
    impact: 'Improves overall section throughput',
    confidence: 78,
    estimatedSaving: '3 minutes',
    conflictsWith: []
  }
];

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return 'text-destructive';
    case 'medium': return 'text-warning';
    case 'low': return 'text-success';
    default: return 'text-muted-foreground';
  }
};

export const RecommendationsScreen = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">AI Recommendations</h1>
            <p className="text-muted-foreground">Intelligent traffic optimization suggestions</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-muted-foreground">Last Analysis:</span>
          <span className="text-sm font-medium">2 minutes ago</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="control-panel p-4">
          <div className="text-2xl font-bold text-primary">3</div>
          <div className="text-sm text-muted-foreground">Active Recommendations</div>
        </div>
        <div className="control-panel p-4">
          <div className="text-2xl font-bold text-success">20min</div>
          <div className="text-sm text-muted-foreground">Potential Savings</div>
        </div>
        <div className="control-panel p-4">
          <div className="text-2xl font-bold text-warning">1</div>
          <div className="text-sm text-muted-foreground">Conflicts Detected</div>
        </div>
        <div className="control-panel p-4">
          <div className="text-2xl font-bold">86%</div>
          <div className="text-sm text-muted-foreground">Avg Confidence</div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {mockRecommendations.map((rec) => (
          <div key={rec.id} className="control-panel p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${getPriorityColor(rec.priority).replace('text-', 'bg-')}`}></div>
                <div>
                  <h3 className="text-lg font-semibold">{rec.title}</h3>
                  <p className="text-sm text-muted-foreground capitalize">{rec.priority} Priority</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">{rec.confidence}% confidence</span>
                {rec.conflictsWith.length > 0 && (
                  <AlertTriangle className="w-4 h-4 text-warning" />
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="font-medium">{rec.description}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Impact</p>
                <p className="font-medium">{rec.impact}</p>
              </div>
            </div>

            {rec.conflictsWith.length > 0 && (
              <div className="mb-4 p-3 bg-warning/10 border border-warning/20 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-warning" />
                  <span className="text-sm font-medium text-warning">Conflicts with other recommendations</span>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-sm">Estimated Saving: <span className="font-bold text-success">{rec.estimatedSaving}</span></span>
              </div>
              <div className="flex items-center space-x-2">
                <button className="railway-btn-success flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Accept</span>
                </button>
                <button className="railway-btn-secondary">Modify</button>
                <button className="railway-btn-danger flex items-center space-x-2">
                  <XCircle className="w-4 h-4" />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};