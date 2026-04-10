import React, { useState, useRef } from "react";
import KanbanBoard from "../components/kanban/KanbanBoard";
import DashboardSidebarCard from "../components/dashboard/DashboardSidebarCard";
import { RefreshCw } from "lucide-react";

export default function WorkflowKanban() {
  const [stats, setStats] = useState({ total: 0 });
  const kanbanBoardRef = useRef(null);

  function handleNewCard() {
    // Open new card modal via ref
    if (kanbanBoardRef.current) {
      kanbanBoardRef.current.openNewCardModal();
    }
  }

  function handleViewAll() {
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function handleArchive() {
    // Archive will be handled by KanbanBoard's clearDone function
    // We'll trigger it via a state change or direct call
    if (kanbanBoardRef.current) {
      kanbanBoardRef.current.archiveDone();
    }
  }

  function handleRefresh() {
    // Reload cards
    if (kanbanBoardRef.current) {
      kanbanBoardRef.current.reload();
    }
  }

  return (
    <div className="min-h-screen transition-colors duration-300" style={{ 
      background: 'linear-gradient(to bottom right, var(--bg-primary), var(--bg-secondary), var(--bg-tertiary))',
      color: 'var(--text-primary)'
    }}>
      {/* Background pattern overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-teal-900/10 via-transparent to-transparent pointer-events-none"></div>
      
      <div className="relative mx-auto max-w-[1800px] px-3 sm:px-5 lg:px-6 py-3 sm:py-4 lg:py-5">
        {/* Header Section - Matching Dashboard style */}
        <div className="mb-3 sm:mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-1 h-6 bg-gradient-to-b from-teal-400 to-teal-600 rounded-full"></div>
            <h1 className="text-lg sm:text-xl lg:text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
              Workflow
            </h1>
          </div>
          <button
            onClick={handleRefresh}
            className="rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-white/90 hover:bg-white/10 hover:border-white/20 transition-all duration-200 flex items-center gap-2"
          >
            <RefreshCw size={16} />
            <span className="text-xs font-medium hidden sm:inline">Refresh</span>
          </button>
        </div>

        {/* Enhanced Board Container - Full Width */}
        <div className="mb-4 lg:mb-6">
          <div className="backdrop-blur-xl rounded-2xl p-3 sm:p-4 lg:p-5 shadow-2xl" style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-primary)',
            borderWidth: '1px'
          }}>
            <KanbanBoard 
              ref={kanbanBoardRef}
              onStats={setStats}
            />
          </div>
        </div>
        
        {/* Moved Sidebar Content Below - Compact Horizontal Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 lg:gap-4">
          {/* Board Overview */}
          <DashboardSidebarCard title="📊 Board Overview">
            <div className="grid grid-cols-2 gap-3">
              <StatCard label="Total Cards" value={stats.total || 0} gradient="from-purple-500/20 to-pink-500/20" />
              <StatCard label="In Script" value={stats.script || 0} gradient="from-blue-500/20 to-cyan-500/20" />
              <StatCard label="In Edit" value={stats.edit || 0} gradient="from-amber-500/20 to-orange-500/20" />
              <StatCard label="Published" value={(stats.publish || 0) + (stats.published || 0)} gradient="from-emerald-500/20 to-teal-500/20" />
            </div>
          </DashboardSidebarCard>

          {/* Pro Tip - Compact */}
          <div className="bg-gradient-to-br from-teal-500/10 to-blue-500/10 backdrop-blur-xl rounded-xl border border-teal-500/20 p-4 shadow-xl">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-full bg-teal-500/20 flex items-center justify-center text-base shrink-0">
                💡
              </div>
              <h3 className="text-sm font-semibold text-white">Pro Tip</h3>
            </div>
            <p className="text-white/80 text-xs leading-relaxed">
              Drag cards between stages to update their status. Set WIP limits to maintain focus and prevent bottlenecks.
            </p>
          </div>

          {/* Quick Actions - Compact */}
          <div className="bg-white/[0.02] backdrop-blur-xl rounded-xl border border-white/10 p-4 shadow-xl">
            <h3 className="text-sm font-semibold text-white mb-2">Quick Actions</h3>
            <div className="space-y-1.5">
              <QuickActionButton icon="➕" label="New Card" onClick={handleNewCard} />
              <QuickActionButton icon="📋" label="View All" onClick={handleViewAll} />
              <QuickActionButton icon="🗄️" label="Archive" onClick={handleArchive} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ label, value, gradient }) {
  return (
    <div className={`group relative overflow-hidden rounded-lg bg-gradient-to-br ${gradient} border border-white/10 p-3 transition-all duration-300 hover:scale-105 hover:border-white/20`}>
      <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div className="relative">
        <div className="text-[10px] font-medium text-white/60 mb-1">{label}</div>
        <div className="text-xl font-bold text-white">{value}</div>
      </div>
    </div>
  );
}

// Quick Action Button Component
function QuickActionButton({ icon, label, onClick }) {
  return (
    <button 
      onClick={onClick}
      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/90 hover:bg-white/10 hover:border-white/20 transition-all duration-200 group"
    >
      <span className="text-lg group-hover:scale-110 transition-transform">{icon}</span>
      <span className="text-xs font-medium">{label}</span>
    </button>
  );
}

