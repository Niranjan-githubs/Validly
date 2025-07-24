import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  // Dummy handler for card click (replace with backend fetch)
  const handleResearchClick = (title: string) => {
    // TODO: Fetch data from backend for the selected research title
    alert(`Fetch and show data for: ${title}`);
  };
  // Navigation logic removed per user request


  // Recent research titles (Grok-inspired)
  const recentResearch = [
    'AI in Healthcare',
    'E-commerce Logistics',
    'Fintech Security',
    'SaaS Market Trends',
    'Investor Sentiment',
  ];

  return (
    <>
      {/* Mobile floating access button - moved lower, smaller, with safe area padding */}
      <button
        className={`fixed left-4 bottom-6 z-[60] p-2 sm:p-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg text-white transition-all duration-300 lg:hidden ${!collapsed ? 'hidden' : ''}`}
        style={{
          // Add a little extra space for safe area on iOS/Android
          paddingBottom: 'env(safe-area-inset-bottom, 0px)'
        }}
        onClick={onToggle}
        aria-label="Open sidebar"
      >
        <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
      </button>
      {/* Sidebar overlay for mobile when open */}
      <div
        className={`fixed inset-0 bg-black/40 z-40 transition-opacity duration-300 lg:hidden ${collapsed ? 'pointer-events-none opacity-0' : 'pointer-events-auto opacity-100'}`}
        onClick={onToggle}
        aria-hidden="true"
      />
      <div
        className={`fixed left-0 top-0 h-full bg-black backdrop-blur-xl border-r border-[#333333] hover:border-blue-400/30 transition-all duration-500 z-50 flex flex-col
        ${collapsed ? 'w-0 sm:w-16 -translate-x-full lg:w-16 lg:translate-x-0' : 'w-64 translate-x-0'}
        shadow-2xl shadow-black/50
        ${collapsed ? 'lg:w-16' : 'lg:w-64'}
        ${collapsed ? 'lg:translate-x-0' : ''}
        `}
        style={{ maxWidth: '90vw', minWidth: collapsed ? 0 : undefined, overflow: 'hidden' }}
        aria-label="Sidebar navigation"
      >
        {/* Header always at the top */}
        <div className="relative z-20 flex items-center justify-between p-4 sm:p-6 border-b border-[#333333] hover:border-blue-400/30 transition-colors duration-500 bg-black/80 sticky top-0">
          {!collapsed && (
            <div className="flex items-center gap-4 animate-fade-in">
              <div className="relative">
               
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur-lg opacity-30 animate-pulse"></div>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">Validly</span>
            </div>
          )}
          {/* Collapse/expand button always visible on desktop, and on mobile when open */}
          <button
            onClick={onToggle}
            className={`p-2 sm:p-3 rounded-xl hover:bg-gradient-to-r hover:from-[#333333] hover:to-[#444444] transition-all duration-300 text-[#CCCCCC] hover:text-white border border-transparent hover:border-blue-400/30 hover:shadow-lg hover:shadow-blue-500/25 ${collapsed ? 'mx-auto' : ''} ${collapsed ? 'hidden lg:block' : ''}`}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" /> : <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />}
          </button>
        </div>

        {/* Navigation and status indicator (single block) */}
        <nav className={`relative z-10 flex-1 overflow-y-auto ${collapsed ? 'flex flex-col items-center justify-center py-8 gap-6' : 'p-2 sm:p-6'}`}>
          {/* Navigation buttons removed. Only research cards and status indicator remain. */}
          {/* Status indicator */}
         
          {/* Highly responsive Recent Research section */}
          {!collapsed && (
            <div className="mt-6">
              <h3 className="text-1xl font-extrabold text-white mb-4 px-2 tracking-wide">Recent Research</h3>
              <div className="flex flex-col gap-3">
                {recentResearch.map((title, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleResearchClick(title)}
                    className="w-full flex items-center justify-between px-6 py-4 rounded-2xl bg-black border border-[#23263a] shadow-lg hover:shadow-blue-500/20 transition-all duration-300 text-base text-white font-semibold hover:bg-blue-500/10 hover:border-blue-400/30 cursor-pointer backdrop-blur-md"
                    style={{ minHeight: 56, fontSize: '1rem', letterSpacing: '0.02em' }}
                  >
                    <span className="truncate text-lg font-medium">{title}</span>
                    <svg className="w-5 h-5 text-blue-400 ml-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
                  </button>
                ))}
              </div>
            </div>
          )}
        </nav>
        {/* Holographic overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-purple-500/5 opacity-50 pointer-events-none"></div>


      </div>
    </>
  );
};

export default Sidebar; 