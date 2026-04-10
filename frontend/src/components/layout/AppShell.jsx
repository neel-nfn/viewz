import { Outlet, useLocation, Link } from 'react-router-dom';
import Topbar from './Topbar';
import EnvIndicator from '../common/EnvIndicator';
import { Home, BarChart3, Zap, Settings, FileText, Search, List, Menu, X, Users, Sparkles, FolderOpen, FileCheck2 } from 'lucide-react';
import { useState } from 'react';

export default function AppShell(){
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  return (
    <div className="flex h-screen bg-background text-textPrimary overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar - Mobile: Drawer, Desktop: Always visible */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-20 lg:w-20 xl:w-64
        bg-surface border-r border-border 
        flex flex-col items-center lg:items-center xl:items-start
        py-4 shrink-0
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Mobile Close Button */}
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden absolute top-4 right-4 text-textSecondary hover:text-primary"
        >
          <X size={24} />
        </button>
        
        <div className="text-2xl font-bold mb-8 text-primary px-4 hidden xl:block">Viewz</div>
        <div className="text-2xl font-bold mb-8 text-primary px-4 xl:hidden">VZ</div>
        
        <nav className="flex flex-col gap-6 text-textSecondary flex-1 w-full px-2 xl:px-4">
          <Link 
            to="/app" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname === '/app' || location.pathname === '/app/' ? 'text-primary bg-primary/10' : ''}`}
            title="Dashboard"
            onClick={() => setSidebarOpen(false)}
          >
            <Home size={20} />
            <span className="hidden xl:inline">Dashboard</span>
          </Link>
          <Link 
            to="/app/analytics" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/analytics') ? 'text-primary bg-primary/10' : ''}`}
            title="Analytics"
            onClick={() => setSidebarOpen(false)}
          >
            <BarChart3 size={20} />
            <span className="hidden xl:inline">Analytics</span>
          </Link>
          <Link 
            to="/app/research" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/research') ? 'text-primary bg-primary/10' : ''}`}
            title="Research"
            onClick={() => setSidebarOpen(false)}
          >
            <Search size={20} />
            <span className="hidden xl:inline">Research</span>
          </Link>
          <Link 
            to="/app/competitors" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/competitors') || location.pathname.startsWith('/app/topic-insights') ? 'text-primary bg-primary/10' : ''}`}
            title="Competitors"
            onClick={() => setSidebarOpen(false)}
          >
            <Users size={20} />
            <span className="hidden xl:inline">Competitors</span>
          </Link>
          <Link 
            to="/app/workflow" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/workflow') ? 'text-primary bg-primary/10' : ''}`}
            title="Workflow"
            onClick={() => setSidebarOpen(false)}
          >
            <FileText size={20} />
            <span className="hidden xl:inline">Workflow</span>
          </Link>
          <Link 
            to="/app/editor" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/editor') ? 'text-primary bg-primary/10' : ''}`}
            title="Editor"
            onClick={() => setSidebarOpen(false)}
          >
            <Sparkles size={20} />
            <span className="hidden xl:inline">Editor</span>
          </Link>
          <Link 
            to="/app/operator" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/operator') ? 'text-primary bg-primary/10' : ''}`}
            title="Operator"
            onClick={() => setSidebarOpen(false)}
          >
            <FileCheck2 size={20} />
            <span className="hidden xl:inline">Operator</span>
          </Link>
          <Link 
            to="/app/worker" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/worker') ? 'text-primary bg-primary/10' : ''}`}
            title="Worker"
            onClick={() => setSidebarOpen(false)}
          >
            <Sparkles size={20} />
            <span className="hidden xl:inline">Worker</span>
          </Link>
          <Link 
            to="/app/storage" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/storage') ? 'text-primary bg-primary/10' : ''}`}
            title="Storage"
            onClick={() => setSidebarOpen(false)}
          >
            <FolderOpen size={20} />
            <span className="hidden xl:inline">Storage</span>
          </Link>
          <Link 
            to="/app/filename-rules" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/filename-rules') ? 'text-primary bg-primary/10' : ''}`}
            title="Filename Rules"
            onClick={() => setSidebarOpen(false)}
          >
            <FileText size={20} />
            <span className="hidden xl:inline">Filename Rules</span>
          </Link>
          <Link 
            to="/app/tasks" 
            className={`flex items-center gap-3 hover:text-primary transition p-2 rounded-lg ${location.pathname.startsWith('/app/tasks') ? 'text-primary bg-primary/10' : ''}`}
            title="Tasks"
            onClick={() => setSidebarOpen(false)}
          >
            <List size={20} />
            <span className="hidden xl:inline">Tasks</span>
          </Link>
          <button 
            onClick={() => {
              window.dispatchEvent(new Event('viewz:toggle-ai'));
              setSidebarOpen(false);
            }}
            className="flex items-center gap-3 hover:text-primary transition p-2 rounded-lg"
            title="AI Assist"
          >
            <Zap size={20} />
            <span className="hidden xl:inline">AI Assist</span>
          </button>
          <Link 
            to="/app/settings" 
            className={`flex items-center gap-3 hover:text-primary transition mt-auto p-2 rounded-lg ${location.pathname.startsWith('/app/settings') ? 'text-primary bg-primary/10' : ''}`}
            title="Settings"
            onClick={() => setSidebarOpen(false)}
          >
            <Settings size={20} />
            <span className="hidden xl:inline">Settings</span>
          </Link>
        </nav>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Mobile Menu Button */}
        <div className="lg:hidden flex items-center gap-2 px-4 py-2 border-b border-border">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-textSecondary hover:text-primary"
          >
            <Menu size={24} />
          </button>
          <div className="flex-1">
            <Topbar />
          </div>
        </div>
        <div className="hidden lg:block">
          <Topbar />
        </div>
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-background">
          <Outlet />
        </main>
        <footer className="border-t border-border px-4 sm:px-6 py-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs opacity-60">
          <EnvIndicator />
          <span>Viewz v0.0.1</span>
        </footer>
      </div>
    </div>
  );
}
