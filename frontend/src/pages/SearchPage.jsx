import React, { useState } from 'react';

const SearchPage = () => {
  const [query, setQuery] = useState('');

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 space-y-12 bg-dark-bg text-text-main">
      {/* Header Section */}
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-extrabold tracking-tighter">
          AdaptEngine<span className="text-accent-blue">V1</span>
        </h1>
        <p className="text-text-muted text-xl font-light max-w-lg mx-auto">
          Knowledge Acquisition Interface for <span className="text-text-main font-medium">AI_Codex</span>
        </p>
      </div>

      {/* Search Component */}
      <div className="w-full max-w-3xl relative group">
        {/* Ambient Glow Effect */}
        <div className="absolute -inset-1 bg-gradient-to-r from-accent-blue to-blue-600 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-700"></div>
        
        <div className="relative flex gap-3 p-3 card-glass bg-dark-surface">
          <div className="flex-1 relative">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </div>
            <input 
              type="text" 
              className="w-full bg-transparent pl-10 pr-4 py-3 text-text-main focus:outline-none placeholder:text-text-muted transition-all" 
              placeholder="Search the global knowledge base..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button className="btn-primary shadow-[0_0_15px_rgba(0,209,255,0.3)]">
            Query
          </button>
        </div>
      </div>

      {/* Results Grid */}
      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card-glass p-6 group cursor-pointer relative overflow-hidden">
            {/* Accent line that expands on hover */}
            <div className="h-1 w-12 bg-accent-blue mb-6 group-hover:w-full transition-all duration-500 rounded-full"></div>
            
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold group-hover:text-accent-blue transition-colors">
                Knowledge Node {i}
              </h3>
              <span className="text-[10px] uppercase tracking-widest text-text-muted border border-dark-border px-2 py-1 rounded">
                Vectorized
              </span>
            </div>
            
            <p className="text-text-muted text-sm leading-relaxed mb-6">
              Semantic search results retrieved via the pgvector pipeline. Analysis of current state and contextual dependencies.
            </p>
            
            <div className="flex items-center text-accent-blue text-xs font-semibold group-hover:translate-x-1 transition-transform">
              View Details 
              <svg xmlns="http://www.w3.org/2000/svg" className="ml-1" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchPage;
