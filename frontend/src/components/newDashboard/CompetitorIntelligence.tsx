import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Zap, Target } from 'lucide-react';
import CompetitorCard from './CompetitorCard';

const CompetitorIntelligence: React.FC = () => {
  const navigate = useNavigate();

  const competitors = [
    {
      name: 'TechValidate Pro',
      fundingRaised: '$12.5M Series A',
      differentiators: [
        'Focus on B2B SaaS validation',
        'Manual analyst involvement',
        'Limited AI integration'
      ],
      description: 'Established player in startup validation with traditional consulting approach and human-heavy analysis processes.',
      threatLevel: 'High' as 'High',
      marketShare: '23%'
    },
    {
      name: 'StartupScanner',
      fundingRaised: '$8.2M Seed',
      differentiators: [
        'Market research emphasis',
        'Static reporting format',
        'Geographic limitations'
      ],
      description: 'Market research focused platform with comprehensive data collection but limited real-time AI analysis capabilities.',
      threatLevel: 'Medium' as 'Medium',
      marketShare: '18%'
    },
    {
      name: 'IdeaMetrics',
      fundingRaised: '$15.7M Series B',
      differentiators: [
        'Enterprise-only focus',
        'High pricing tier',
        'Complex onboarding'
      ],
      description: 'Enterprise-focused validation platform with sophisticated analytics but limited accessibility for early-stage startups.',
      threatLevel: 'Medium' as 'Medium',
      marketShare: '31%'
    },
    {
      name: 'VentureCheck',
      fundingRaised: '$6.3M Pre-Series A',
      differentiators: [
        'VC network integration',
        'Limited analysis depth',
        'Narrow industry focus'
      ],
      description: 'Investor-network focused platform with strong connections but limited comprehensive validation capabilities.',
      threatLevel: 'Low' as 'Low',
      marketShare: '12%'
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
              Competitor Intelligence
            </h1>
          </div>
          <p className="text-[#CCCCCC] text-xl font-light tracking-wide">
            Comprehensive analysis of key competitors in the startup validation space with strategic positioning insights.
          </p>
        </div>

        {/* Competitors Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {competitors.map((competitor, index) => (
            <CompetitorCard 
              key={competitor.name} 
              competitor={competitor} 
              index={index}
            />
          ))}
        </div>
      </div>
      </div>
    </div>
  );
};

export default CompetitorIntelligence; 