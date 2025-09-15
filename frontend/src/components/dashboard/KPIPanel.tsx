import { useQuery } from '@tanstack/react-query';
import { Clock, Target, TrendingUp, TrendingDown, Activity, AlertTriangle } from 'lucide-react';
import apiClient from '../../api/apiClient';

// Static KPI data for fallback when API is not available
const staticKpiData = [
  {
    label: 'On-Time Performance',
    value: '94.2%',
    change: '+2.1%',
    trend: 'up',
    icon: Target,
    color: 'success'
  },
  {
    label: 'Average Delay',
    value: '3.2min',
    change: '-0.8min',
    trend: 'up',
    icon: Clock,
    color: 'primary'
  },
  {
    label: 'Trains per Hour',
    value: '142',
    change: '+8',
    trend: 'up',
    icon: Activity,
    color: 'warning'
  },
  {
    label: 'Active Alerts',
    value: '3',
    change: '-2',
    trend: 'up',
    icon: AlertTriangle,
    color: 'destructive'
  }
];

// Function to fetch KPI data from the API
const fetchKPIData = async () => {
  try {
    // In a production app, this would be a real API call
    const response = await apiClient.get('/api/analytics/kpis');
    return response;
  } catch (error) {
    console.error('Failed to fetch KPI data:', error);
    // Return static data as fallback
    return staticKpiData;
  }
};

const getColorClasses = (color: string) => {
  switch (color) {
    case 'success':
      return {
        icon: 'text-success bg-success/20',
        value: 'text-success'
      };
    case 'warning':
      return {
        icon: 'text-warning bg-warning/20',
        value: 'text-warning'
      };
    case 'destructive':
      return {
        icon: 'text-destructive bg-destructive/20',
        value: 'text-destructive'
      };
    default:
      return {
        icon: 'text-primary bg-primary/20',
        value: 'text-primary'
      };
  }
};

export const KPIPanel = () => {
  // Use React Query to fetch KPI data
  const { data: kpiData, isLoading, error } = useQuery({
    queryKey: ['kpis'],
    queryFn: fetchKPIData,
    // Keep data fresh for 30 seconds
    staleTime: 30000,
  });

  // Use static data as fallback if there's an error, data is loading, or data is undefined
  const displayData = error || isLoading || !kpiData ? staticKpiData : kpiData;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {displayData.map((kpi, index) => {
        const IconComponent = kpi.icon;
        const colors = getColorClasses(kpi.color);
        
        return (
          <div key={index} className="control-panel p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${colors.icon}`}>
                <IconComponent className="w-6 h-6" />
              </div>
              <div className="flex items-center space-x-1">
                {kpi.trend === 'up' ? (
                  <TrendingUp className="w-4 h-4 text-success" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-destructive" />
                )}
                <span className={`text-sm font-medium ${
                  kpi.change.startsWith('+') || kpi.change.startsWith('-') && kpi.change.includes('min') ? 'text-success' : 
                  kpi.change.startsWith('-') ? 'text-success' : 'text-destructive'
                }`}>
                  {kpi.change}
                </span>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm text-muted-foreground mb-1">{kpi.label}</h3>
              <p className={`text-3xl font-bold ${colors.value}`}>{kpi.value}</p>
            </div>
            
            {/* Mini trend visualization */}
            <div className="mt-4 flex items-end space-x-1 h-8">
              {Array.from({ length: 7 }, (_, i) => (
                <div 
                  key={i}
                  className={`flex-1 bg-gradient-to-t ${
                    kpi.trend === 'up' ? 'from-success/20 to-success' : 'from-destructive/20 to-destructive'
                  } rounded-sm`}
                  style={{ 
                    height: `${Math.random() * 60 + 20}%`,
                    opacity: i === 6 ? 1 : 0.3 + (i * 0.1)
                  }}
                ></div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};