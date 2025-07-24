import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const MarketAnalysisDetail: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/new-dashboard')}
          className="group flex items-center gap-2 text-white/70 hover:text-white mb-8 transition-colors duration-200 bg-transparent border border-blue-500/30 px-6 py-3 rounded-2xl backdrop-blur-lg hover:bg-blue-500/10"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform duration-300" />
          Back to Dashboard
        </button>
        <div className="bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl animate-fade-in">
          <h1 className="text-3xl font-bold text-white mb-6">Market Analysis Report</h1>
          <p className="text-white leading-relaxed text-lg">
            Comprehensive market analysis reveals a $32.8B total addressable market with 23% year-over-year growth trajectory. The target segment shows strong demand signals with low regulatory barriers and enterprise adoption rising. Competitive landscape analysis identifies 3 direct competitors with differentiation opportunities in UX and pricing strategies. Market timing appears optimal with emerging technologies creating new opportunities for disruption. Consumer behavior trends support the core value proposition with increasing willingness to adopt innovative solutions in this space.
          </p>
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysisDetail;
