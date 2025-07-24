
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, DollarSign, TrendingUp, Target, AlertTriangle, Shield, Zap } from 'lucide-react';

interface Investor {
  name: string;
  funding: string;
  differentiators: string[];
  description: string;
  threatLevel: 'High' | 'Medium' | 'Low';
  marketShare: string;
}

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

const VCInvestorCard: React.FC<{ investor: Investor; index: number }> = ({ investor, index }) => {
  const threatStyle = getThreatColor(investor.threatLevel);
  const ThreatIcon = getThreatIcon(investor.threatLevel);

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
              {investor.name}
            </h3>
            <div className="flex items-center gap-3 text-[#CCCCCC]">
              <DollarSign className="w-4 h-4" />
              <span className="text-sm font-medium">{investor.funding}</span>
            </div>
          </div>
          {/* Threat Level Indicator */}
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r ${threatStyle.bg} ${threatStyle.glow} shadow-lg`}>
            <ThreatIcon className="w-3 h-3 text-white" />
            <span className="text-xs font-bold text-white">{investor.threatLevel}</span>
          </div>
          <div className="text-xs text-[#CCCCCC]">
            Market: {investor.marketShare}
          </div>
        </div>
        {/* Description */}
        <p className="text-[#CCCCCC] leading-relaxed mb-8 group-hover:text-white/90 transition-colors duration-500 text-lg font-light">
          {investor.description}
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
            {investor.differentiators.map((diff, idx) => (
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
              <span className="text-xs font-bold">{investor.threatLevel} Risk</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const VCInvestorCardDetails: React.FC = () => {
  const navigate = useNavigate();
  const investors: Investor[] = [
    {
      name: 'Alpha Ventures',
      funding: '$20M Series B',
      differentiators: [
        'Global reach',
        'AI-driven investment strategy',
        'Strong founder support'
      ],
      description: 'Leading VC firm with a focus on technology startups and AI-powered market analysis.',
      threatLevel: 'High',
      marketShare: '28%'
    },
    {
      name: 'Beta Capital',
      funding: '$10M Series A',
      differentiators: [
        'Early-stage focus',
        'Diverse portfolio',
        'Fast decision cycles'
      ],
      description: 'Active investor in early-stage startups with a diverse portfolio and quick investment decisions.',
      threatLevel: 'Medium',
      marketShare: '19%'
    },
    {
      name: 'Gamma Partners',
      funding: '$15M Seed',
      differentiators: [
        'Industry expertise',
        'Mentorship programs',
        'Flexible funding options'
      ],
      description: 'VC firm known for industry expertise and strong mentorship programs for founders.',
      threatLevel: 'Low',
      marketShare: '15%'
    },
    {
      name: 'Delta Investors',
      funding: '$8M Pre-Series A',
      differentiators: [
        'Niche market focus',
        'Personalized guidance',
        'Long-term partnerships'
      ],
      description: 'Investor group specializing in niche markets and long-term founder partnerships.',
      threatLevel: 'Medium',
      marketShare: '11%'
    }
  ];

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-gradient-to-r from-red-500/5 to-orange-500/5 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/3 right-1/3 w-80 h-80 bg-gradient-to-r from-purple-500/5 to-pink-500/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '3s' }}></div>
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
      <div className="relative z-10 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-16">
            <button
              onClick={() => navigate('/new-dashboard')}
              className="group flex items-center gap-3 text-[#CCCCCC] hover:text-white mb-8 transition-all duration-500 hover:bg-gradient-to-r hover:from-[#333333] hover:to-[#444444] px-4 py-2 rounded-xl border border-transparent hover:border-blue-400/30"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-2 transition-transform duration-500" />
              Back to Dashboard
            </button>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg shadow-red-500/25">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-red-100 to-orange-100 bg-clip-text text-transparent">
                VC Matching Details
              </h1>
            </div>
            <p className="text-[#CCCCCC] text-xl font-light tracking-wide">
              Comprehensive analysis of key investors in the startup validation space with strategic positioning insights.
            </p>
          </div>
          {/* Investors Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            {investors.map((investor, index) => (
              <VCInvestorCard 
                key={investor.name} 
                investor={investor} 
                index={index}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VCInvestorCardDetails;