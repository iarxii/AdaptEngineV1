import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-obsidian-900">
      {/* Top Navigation - AI_Codex Style */}
      <nav className="h-16 glass-panel flex items-center justify-between px-6 sticky top-0 z-50 silver-trim">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-silver-100 to-silver-400 rounded-lg shadow-lg shadow-silver-400/20" />
          <span className="text-xl font-bold tracking-tight text-silver-100">
            Adapt<span className="text-silver-400">Engine</span> <span className="text-xs font-light opacity-50">v1.0</span>
          </span>
        </div>
        <div className="flex items-center gap-6 text-sm font-medium text-silver-400">
          <a href="#" className="hover:text-silver-100 transition-colors">Knowledge Base</a>
          <a href="#" className="hover:text-silver-100 transition-colors">Crawl Monitor</a>
          <div className="h-4 w-px bg-silver-400/30" />
          <button className="px-3 py-1 rounded-full border border-silver-400/40 text-silver-100 hover:bg-silver-400 hover:text-obsidian-900 transition-all">
            AICodex Sync
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {children}
      </main>

      {/* Subtle Footer */}
      <footer className="p-4 text-center text-xs text-silver-400/40 border-t border-silver-400/10">
        &copy; 2026 AdaptEngine | Integrated with AI_Codex Framework
      </footer>
    </div>
  );
};

export default Layout;
