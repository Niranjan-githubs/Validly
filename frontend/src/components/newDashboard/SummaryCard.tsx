import React from 'react';


interface SummaryCardProps {
  summaryText?: string;
}

const defaultSummary = `Y   demonstrates strong market validation potential with compelling user demand and solid competitive positioning.\nThe AI analysis reveals significant opportunities in the target market with moderate risk factors. Key differentiators have been identified that position your venture favorably against existing competitors. Market timing appears optimal with emerging trends supporting your core value proposition. Recommended next steps include deeper market penetration analysis and strategic investor outreach through our VC matching algorithms.`;

const SummaryCard: React.FC<SummaryCardProps> = ({ summaryText }) => {
  return (
    <div className="animate-fade-in-up w-full">
      <div className="relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] hover:border-blue-400/30 rounded-3xl p-6 sm:p-10 shadow-xl hover:shadow-blue-500/10 transition-all duration-700 group overflow-hidden min-h-[180px]">
        {/* Subtle holographic overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
           
            <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-green-100 bg-clip-text text-transparent">Executive Summary</h3>
          </div>
          <p className="text-white/90 leading-relaxed text-lg font-light tracking-wide break-words">
            {(summaryText || defaultSummary).split('\n').map((line, idx) => (
              <span key={idx}>
                {line}
                <br />
              </span>
            ))}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SummaryCard;
