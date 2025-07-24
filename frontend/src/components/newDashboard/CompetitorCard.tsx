import React from 'react';
import { TrendingUp, DollarSign, Target, AlertTriangle, Shield, Zap } from 'lucide-react';

interface Competitor {
  name: string;
  fundingRaised: string;
  differentiators: string[];
  description: string;
  threatLevel: 'High' | 'Medium' | 'Low';
  marketShare: string;
}

interface CompetitorCardProps {
  competitor: Competitor;
  index: number;
}

const CompetitorCard: React.FC<CompetitorCardProps> = ({ competitor, index }) => {
  const getThreatColor = (level: string) => {
    switch (level) {
      case 'High': return { bg: 'from-red-500 to-orange-500', glow: 'shadow-red-500/25', text: 'text-red-400' };
      case 'Medium': return { bg: 'from-yellow-500 to-orange-500', glow: 'shadow-yellow-500/25', text: 'text-yellow-400' };
      case 'Low': return { bg: 'from-green-500 to-emerald-500', glow: 'shadow-green-500/25', text: 'text-green-400' };
      default: return { bg: 'from-gray-500 to-gray-600', glow: 'shadow-gray-500/25', text: 'text-gray-400' };
    }
  };

  const getThreatIcon = (level: string) => {
    switch (level) {
      case 'High': return AlertTriangle;
      case 'Medium': return Shield;
      case 'Low': return Zap;
      default: return Shield;
    }
  };

  const threatStyle = getThreatColor(competitor.threatLevel);
  const ThreatIcon = getThreatIcon(competitor.threatLevel);

  return (
    <div 
      className="group relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl hover:shadow-blue-500/20 transition-all duration-700 hover:scale-105 animate-fade-in-up overflow-hidden"
      style={{ animationDelay: `${index * 150}ms` }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
      <div className="relative z-10">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div className="flex-1">
          <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-500 mb-2">
            {competitor.name}
          </h3>
          <div className="flex items-center gap-3 text-[#CCCCCC]">
            <DollarSign className="w-4 h-4" />
            <span className="text-sm font-medium">{competitor.fundingRaised}</span>
          </div>
        </div>
        
        {/* Threat Level Indicator */}
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r ${threatStyle.bg} ${threatStyle.glow} shadow-lg`}>
          <ThreatIcon className="w-3 h-3 text-white" />
          <span className="text-xs font-bold text-white">{competitor.threatLevel}</span>
        </div>
        <div className="text-xs text-[#CCCCCC]">
          Market: {competitor.marketShare}
        </div>
      </div>

      {/* Description */}
      <p className="text-[#CCCCCC] leading-relaxed mb-8 group-hover:text-white/90 transition-colors duration-500 text-lg font-light">
        {competitor.description}
      </p>

      {/* Differentiators */}
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/25">
            <Target className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-white text-lg">Key Differentiators</span>
        </div>
        
        <ul className="space-y-3">
          {competitor.differentiators.map((diff, idx) => (
            <li 
              key={idx}
              className="flex items-start gap-4 text-[#CCCCCC] group-hover:text-white/90 transition-colors duration-500"
            >
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mt-2 flex-shrink-0 shadow-lg shadow-blue-500/25 group-hover:shadow-purple-500/25 transition-all duration-500"></div>
              <span className="font-medium">{diff}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Performance Indicator */}
      <div className="mt-8 pt-6 border-t border-[#333333] group-hover:border-blue-400/30 transition-colors duration-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/25">
              <TrendingUp className="w-3 h-3 text-white" />
            </div>
            <span className="text-sm font-semibold text-white">Threat Assessment</span>
          </div>
          <div className={`px-3 py-1 rounded-full border ${threatStyle.text} border-current`}>
            <span className="text-xs font-bold">{competitor.threatLevel} Risk</span>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
};

export default CompetitorCard; 