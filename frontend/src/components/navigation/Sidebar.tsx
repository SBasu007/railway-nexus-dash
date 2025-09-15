import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Brain, 
  GitCompare, 
  Calendar, 
  FileText, 
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Train
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const navigationItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { name: 'AI Recommendations', icon: Brain, path: '/recommendations' },
  { name: 'Scenario Analysis', icon: GitCompare, path: '/scenarios' },
  { name: 'Schedule Editor', icon: Calendar, path: '/schedule-editor' },
  { name: 'Audit Trail', icon: FileText, path: '/audit-trail' },
  { name: 'Performance', icon: BarChart3, path: '/performance' },
];

export const Sidebar = ({ collapsed, onToggle }: SidebarProps) => {
  return (
    <div className={cn(
      "bg-card border-r border-border flex flex-col transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        {!collapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center">
              <Train className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Railway TMS</h1>
              <p className="text-xs text-muted-foreground">Traffic Management</p>
            </div>
          </div>
        )}
        
        <button 
          onClick={onToggle}
          className="p-2 hover:bg-secondary rounded-lg transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2">
        <ul className="space-y-1">
          {navigationItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => cn(
                  "flex items-center px-3 py-2.5 rounded-lg transition-all duration-200 group",
                  isActive 
                    ? "bg-primary text-primary-foreground shadow-lg" 
                    : "hover:bg-secondary text-muted-foreground hover:text-foreground",
                  collapsed && "justify-center"
                )}
              >
                <item.icon className={cn("w-5 h-5", !collapsed && "mr-3")} />
                {!collapsed && (
                  <span className="font-medium">{item.name}</span>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};