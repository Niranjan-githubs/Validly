
import React from 'react';
import { TrendingUp, DollarSign, Users } from 'lucide-react';

interface Investor {
  name: string;
  amountInvested: string;
  inspiration: string;
  description: string;
  stage: string;
  marketFocus: string;
}

const sampleInvestors: Investor[] = [
  {
    name: 'Sequoia Capital',
    amountInvested: '$5M',
    inspiration: 'Early belief in disruptive founders',
    description: 'Leading VC firm with a track record of backing transformative startups.',
    stage: 'Series A',
    marketFocus: 'Tech, SaaS, AI'
  },
  {
    name: 'Accel Partners',
    amountInvested: '$3.2M',
    inspiration: 'Focus on scalable business models',
    description: 'Global venture firm investing in high-growth companies.',
    stage: 'Seed',
    marketFocus: 'Enterprise, SaaS'
  },
  {
    name: 'Lightspeed Venture',
    amountInvested: '$2.5M',
    inspiration: 'Backing bold ideas in emerging markets',
    description: 'VC firm supporting founders in tech and consumer sectors.',
    stage: 'Series B',
    marketFocus: 'Consumer, Fintech'
  }
];

const VCMatchingDetail: React.FC = () => {
  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">VC Matching Results</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {sampleInvestors.map((inv, idx) => (
            <div
              key={idx}
              className="group relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl hover:shadow-blue-500/20 transition-all duration-700 hover:scale-105 animate-fade-in-up overflow-hidden"
              style={{ animationDelay: `${idx * 150}ms` }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-500 mb-2">
                      {inv.name}
                    </h3>
                    <div className="flex items-center gap-3 text-[#CCCCCC]">
                      <DollarSign className="w-4 h-4" />
                      <span className="text-sm font-medium">{inv.amountInvested}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg">
                    <Users className="w-3 h-3 text-white" />
                    <span className="text-xs font-bold text-white">{inv.stage}</span>
                  </div>
                  <div className="text-xs text-[#CCCCCC]">
                    Market: {inv.marketFocus}
                  </div>
                </div>
                <p className="text-[#CCCCCC] leading-relaxed mb-4 group-hover:text-white/90 transition-colors duration-500 text-base font-light">
                  {inv.description}
                </p>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/25">
                    <TrendingUp className="w-4 h-4 text-white" />
                  </div>
                  <span className="font-bold text-white text-lg">Inspiration</span>
                </div>
                <p className="text-[#CCCCCC] group-hover:text-white/90 transition-colors duration-500 text-base font-medium mb-2">
                  {inv.inspiration}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VCMatchingDetail;
