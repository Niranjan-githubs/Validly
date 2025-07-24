import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import AgentCard from './AgentCard';
import { ChevronRight, Zap, Brain, Activity, Users, Shield } from 'lucide-react';
import SummaryCard from './SummaryCard';

const Dashboard: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const agents = [
    { name: 'Competitors', id: 'competitor-intelligence', icon: Zap, status: 'active' as 'active' },
    { name: 'Market Analysis', id: 'market-analysis', icon: Activity, status: 'processing' as 'processing' },
    { name: 'VC Matching', id: 'vc-matching', icon: Users, status: 'idle' as 'idle' },
    { name: 'Risk Assessment', id: 'risk-assessment', icon: Shield, status: 'completed' as 'completed' },
    { name: 'User Pain Points', id: 'user-pain-points', icon: Brain, status: 'active' as 'active' }
  ];

  const navigate = useNavigate();
  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-black relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-cyan-500/5 to-blue-500/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-purple-500/3 to-pink-500/3 rounded-full blur-3xl animate-spin-slow"></div>
      </div>
      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          backgroundColor: '#000'
        }}></div>
      </div>

      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

      <main className={`flex-1 transition-all duration-500 relative z-10 ${sidebarCollapsed ? 'ml-4 sm:ml-20' : 'ml-16 sm:ml-64'}`}> {/* Responsive margin */}
        <div className="p-2 sm:p-4 md:p-8"> {/* Responsive padding */}
          {/* Header with New Research Button */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-16">
            <div>
              <div className="flex items-center gap-4 mb-7">
                
                <h1 className="text-2xl sm:text-5xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent leading-[1.15]">
                 Validly Dashboard
                </h1>
              </div>
              <p className="text-[#CCCCCC] text-base sm:text-xl font-light tracking-wide">Comprehensive startup analysis powered by advanced AI intelligence</p>
            </div>
            <div className="flex flex-row gap-2 w-full sm:w-auto">
              <button
                className="group relative bg-transparent text-white px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-semibold transition-all duration-300 flex items-center gap-3 border border-white/10 hover:border-blue-400/30 w-full sm:w-auto"
              >
                <svg className="w-5 h-5 relative z-10" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                Download Report
              </button>
              <button
                className="group relative bg-transparent text-white px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-semibold transition-all duration-300 flex items-center gap-3 border border-white/10 hover:border-blue-400/30 w-full sm:w-auto"
                onClick={() => navigate('/chat')}
              >
                <Zap className="w-5 h-5 relative z-10" />
                New Research
                <ChevronRight className="w-5 h-5 group-hover:translate-x-2 transition-transform duration-300 relative z-10" />
              </button>
            </div>
          </div>

          {/* AI Agent Cards Grid */}
          <div className="mb-16">
            <div className="flex items-center gap-4 mb-10">
             
              <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">AI Validation Agents</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-blue-500/50 to-transparent"></div>
            </div>
            {/* Single responsive grid for agent cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 w-full">
              {agents.map((agent) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          </div>

          {/* Summary Report Card */}
          <SummaryCard />
        </div>
      </main>
    </div>
  );
};

export default Dashboard; 