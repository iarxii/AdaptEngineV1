import React, { useState } from 'react';

const App = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([
    { title: 'Introduction to AICodex', url: 'https://aicodex.io/docs', desc: 'The next generation of autonomous knowledge management.' },
    { title: 'Adaptive Crawling Engines', url: 'https://research.io/adaptive', desc: 'Understanding the transition from recursive to pipeline crawling.' },
    { title: 'Vector Databases & pgvector', url: 'https://postgres.org/vector', desc: 'Scaling semantic search using high-dimensional embeddings.' },
  ]);

  return (
    <div className="min-h-screen w-full bg-obsidian-900 text-silver-100 flex flex-col font-sans">
      {/* TOP NAVIGATION BAR */}
      <nav className="w-full h-16 border-b border-silver-400/20 bg-obsidian-800/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-silver-300 rounded-lg flex items-center justify-center">
            <span className="text-obsidian-900 font-bold text-xl">A</span>
          </div>
          <span className="text-xl font-semibold tracking-tight text-silver-100">
            AdaptEngine <span className="text-silver-400 font-light">V1</span>
          </span>
        </div>
        <div className="flex items-center gap-6 text-sm font-medium text-silver-400">
          <a href="#" className="hover:text-silver-100 transition-colors">Docs</a>
          <a href="#" className="hover:text-silver-100 transition-colors">API</a>
          <div className="h-4 w-px bg-silver-400/30"></div>
          <span className="text-silver-300 opacity-80">AI_Codex Integrated</span>
        </div>
      </nav>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col items-center px-4 py-12">
        
        {/* HERO SECTION */}
        <div className="w-full max-w-3xl text-center mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h1 className="text-5xl font-bold text-silver-100 mb-4 tracking-tight">
            Knowledge <span className="bg-clip-text bg-silver-gradient">Acquisition</span>
          </h1>
          <p className="text-silver-400 text-lg max-w-xl mx-auto">
            Search, index, and retrieve global information through the AI_Codex neural pipeline.
          </p>
        </div>

        {/* SEARCH BOX - GLASSMORPHISM */}
        <div className="w-full max-w-2xl relative group mb-16">
          <div className="absolute -inset-1 bg-silver-300/20 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-1000"></div>
          <div className="relative flex items-center bg-obsidian-800 border border-silver-400/30 rounded-2xl p-2 shadow-2xl focus-within:border-silver-300 transition-all">
            <div className="pl-4 pr-2 text-silver-400">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search the global knowledge base..." 
              className="w-full bg-transparent py-4 px-2 outline-none text-silver-100 placeholder-silver-400/50 text-lg"
            />
            <button className="bg-silver-300 text-obsidian-900 px-6 py-3 rounded-xl font-bold hover:bg-silver-100 transition-all active:scale-95 shadow-lg">
              Search
            </button>
          </div>
        </div>

        {/* RESULTS GRID */}
        <div className="w-full max-w-4xl grid grid-cols-1 gap-4">
          {results.map((res, idx) => (
            <div 
              key={idx} 
              className="group relative p-6 bg-obsidian-800/40 border border-silver-400/10 rounded-xl hover:border-silver-400/40 transition-all duration-300 hover:bg-obsidian-800/60 cursor-pointer"
            >
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-transparent group-hover:bg-silver-300 transition-all duration-300 rounded-l-xl"></div>
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <a href={res.url} className="text-xl font-semibold text-silver-300 group-hover:text-silver-100 transition-colors">
                    {res.title}
                  </a>
                  <span className="text-xs font-mono text-silver-400/50 uppercase tracking-widest">Indexed</span>
                </div>
                <p className="text-silver-400 leading-relaxed">
                  {res.desc}
                </p>
                <div className="mt-4 flex items-center gap-3">
                  <span className="text-xs text-silver-400 truncate max-w-xs">{res.url}</span>
                  <div className="h-px flex-1 bg-silver-400/10"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* FOOTER */}
      <footer className="w-full py-8 border-t border-silver-400/10 bg-obsidian-900 text-center">
        <p className="text-silver-400 text-sm">
          &copy; {new Date().getFullYear()} AdaptEngine V1 &bull; Built for <span className="text-silver-300">AI_Codex</span>
        </p>
      </footer>
    </div>
  );
};

export default App;
