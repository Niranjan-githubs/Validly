import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Zap, Brain, Activity } from 'lucide-react';

interface Agent {
  name: string;
  id: string;
  status: 'active' | 'processing' | 'completed' | 'idle';
  icon: React.ElementType;
}

interface AgentCardProps {
  agent: Agent;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
  const navigate = useNavigate();

  const handleSeeDetails = () => {
    if (agent.id === 'competitor-intelligence') {
      navigate('/new-dashboard/CompetitorIntelligence');
    } else if (agent.id === 'user-pain-points') {
      navigate('/new-dashboard/userpainpointDetails');
    } else if (agent.id === 'vc-matching') {
      navigate('/new-dashboard/VCInvestorCardDetails');
    } else if (agent.id === 'market-analysis') {
      navigate('/new-dashboard/MarketAnalysisDetail');
    } else if (agent.id === 'risk-assessment') {
      navigate('/new-dashboard/RiskAssessmentDetail');
    } else {
      navigate(`/new-dashboard/agent/${agent.id}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'from-green-500 to-emerald-500';
      case 'processing': return 'from-blue-500 to-cyan-500';
      case 'completed': return 'from-purple-500 to-pink-500';
      case 'idle': return 'from-gray-500 to-gray-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getStatusGlow = (status: string) => {
    switch (status) {
      case 'active': return 'shadow-green-500/25';
      case 'processing': return 'shadow-blue-500/25';
      case 'completed': return 'shadow-purple-500/25';
      case 'idle': return 'shadow-gray-500/25';
      default: return 'shadow-gray-500/25';
    }
  };

  return (
    <div className={`group relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] hover:border-blue-400/40 rounded-3xl shadow-xl hover:shadow-blue-500/20 transition-all duration-700 hover:scale-105 animate-fade-in-up overflow-hidden p-8`}> 
      {/* Subtle holographic effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
      
      <div className="relative z-10 flex flex-col items-center text-center">
        {/* Status indicator and icon */}
        <div className="relative mb-6">
          <div className={`w-16 h-16 bg-gradient-to-r ${getStatusColor(agent.status)} rounded-2xl flex items-center justify-center shadow-lg ${getStatusGlow(agent.status)} group-hover:shadow-xl transition-all duration-500`}>
          <div className="w-16 h-16 bg-gradient-to-r from-black to-gray-800 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-500">
            {agent.icon && <agent.icon className="w-8 h-8 text-white" />}
          </div>
          </div>
          {/* Status pulse animation */}
          {agent.status === 'processing' && (
            <div className="absolute inset-0 rounded-2xl bg-blue-500/30 animate-ping"></div>
          )}
          {agent.status === 'active' && (
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
          )}
        </div>
        
        <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent mb-8 group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-500">
          {agent.name === 'User Pain Points' ? 'User Pain Points' : agent.name}
        </h3>
        
        <button
          onClick={handleSeeDetails}
          className="group/btn relative bg-transparent border border-blue-500/30 text-white px-8 py-4 rounded-2xl font-semibold transition-all duration-500 hover:shadow-xl hover:shadow-blue-500/25 flex items-center gap-3 overflow-visible backdrop-blur-lg hover:bg-blue-500/10"
        >
          <span className="absolute inset-0 pointer-events-none"></span>
          See Details
          <ChevronRight className="w-5 h-5 group-hover/btn:translate-x-2 transition-transform duration-500 relative z-10" />
        </button>
      </div>
    </div>
  );
};

export default AgentCard; 