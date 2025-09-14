import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './navigation/Sidebar';
import { TopBar } from './navigation/TopBar';
import { MainDashboard } from './screens/MainDashboard';
import { RecommendationsScreen } from './screens/RecommendationsScreen';
import { ScenarioAnalysisScreen } from './screens/ScenarioAnalysisScreen';
import { ScheduleEditorScreen } from './screens/ScheduleEditorScreen';
import { AuditTrailScreen } from './screens/AuditTrailScreen';
import { PerformanceScreen } from './screens/PerformanceScreen';

export const DashboardLayout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="h-screen flex bg-background text-foreground">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar />
        
        <main className="flex-1 p-6 overflow-auto">
          <Routes>
            <Route path="/" element={<MainDashboard />} />
            <Route path="/recommendations" element={<RecommendationsScreen />} />
            <Route path="/scenarios" element={<ScenarioAnalysisScreen />} />
            <Route path="/schedule-editor" element={<ScheduleEditorScreen />} />
            <Route path="/audit-trail" element={<AuditTrailScreen />} />
            <Route path="/performance" element={<PerformanceScreen />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};