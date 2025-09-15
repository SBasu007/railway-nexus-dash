import { useState, useEffect } from 'react';
import { 
  Wifi, 
  WifiOff, 
  User, 
  Settings, 
  Bell, 
  RefreshCw,
  Activity
} from 'lucide-react';

export const TopBar = () => {
  const [isConnected, setIsConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    // Simulate connection status changes
    const interval = setInterval(() => {
      setLastUpdate(new Date());
      // Randomly simulate connection issues (5% chance)
      if (Math.random() > 0.95) {
        setIsConnected(false);
        setTimeout(() => setIsConnected(true), 2000);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-card border-b border-border px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Left: System Status */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <>
                <Wifi className="w-5 h-5 text-success" />
                <span className="text-sm text-success font-medium">System Online</span>
              </>
            ) : (
              <>
                <WifiOff className="w-5 h-5 text-destructive" />
                <span className="text-sm text-destructive font-medium">Connection Lost</span>
              </>
            )}
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Activity className="w-4 h-4" />
            <span>Last Update: {lastUpdate.toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Right: User Actions */}
        <div className="flex items-center space-x-4">
          <button className="p-2 hover:bg-secondary rounded-lg transition-colors relative">
            <Bell className="w-5 h-5" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full border-2 border-card"></div>
          </button>
          
          <button className="p-2 hover:bg-secondary rounded-lg transition-colors">
            <RefreshCw className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-3 pl-4 border-l border-border">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-primary-foreground" />
              </div>
              <div className="text-sm">
                <div className="font-medium">Controller Smith</div>
                <div className="text-muted-foreground">Central Section</div>
              </div>
            </div>
            
            <button className="p-2 hover:bg-secondary rounded-lg transition-colors">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};