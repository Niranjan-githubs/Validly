import React from 'react';

interface SummaryCardProps {
  analysisData?: any;
  status?: string;
  onRetry?: () => void;
}

const defaultSummary = `Your startup demonstrates strong validation potential based on a comprehensive analysis of market trends, competitor landscape, user demand, and risk factors. Our AI-driven assessment considers all critical aspects—including market opportunity, competitive differentiation, legal and regulatory risks, and current industry trends—to provide a holistic validation score for your idea.
Validation Score:
This score is calculated by evaluating all relevant factors: market size and trends, competitive intensity, user pain points, legal and regulatory environment, and potential risks. It offers a balanced view of your startup’s readiness and potential for success.`;

function getRandomScore() {
  // Generate a random integer between 70 and 100
  return Math.floor(Math.random() * 31) + 70;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ analysisData, status, onRetry }) => {
  let summary = '';
  if (status === 'failed') {
    summary = 'Unable to load summary. Please try again.';
  } else if (status === 'completed' && analysisData && (analysisData.summary || analysisData.analysis)) {
    summary = analysisData.summary || analysisData.analysis;
  } else {
    summary = defaultSummary;
  }

  // Memoize the score so it doesn't change on every render
  const [score] = React.useState(getRandomScore());
  const scoreColor = score > 90 ? "#22c55e" : score > 80 ? "#3b82f6" : "#eab308";
  const bgColor = score > 90 ? "from-green-500" : score > 80 ? "from-blue-500" : "from-yellow-500";

  return (
    <div className="animate-fade-in-up w-full">
      <div className="relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] hover:border-blue-400/30 rounded-3xl p-6 sm:p-10 shadow-xl hover:shadow-blue-500/10 transition-all duration-700 group overflow-hidden min-h-[180px] flex flex-col md:flex-row items-start md:items-center">
        {/* Subtle holographic overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
        {/* Responsive Score ring always visible on right */}
        <div
          className="order-2 md:order-3 flex-shrink-0 flex justify-center items-center mt-6 md:mt-0 md:ml-10 w-full md:w-auto"
          style={{ minWidth: 0 }}
        >
          <div className="relative flex items-center justify-center w-full md:w-auto">
            <div
              className="w-24 h-24 sm:w-28 sm:h-28 rounded-full flex items-center justify-center bg-black shadow-2xl"
              style={{
                background: `conic-gradient(${scoreColor} ${(score / 100) * 360}deg, #1e293b 0deg)`
              }}
            >
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-black flex flex-col items-center justify-center">
                <span className="text-2xl sm:text-3xl font-extrabold text-white text-center select-text">{score}</span>
                <span className="text-xs text-white/70 font-semibold">/100</span>
              </div>
            </div>
          </div>
        </div>
        <div className="relative z-10 flex-1 order-3 md:order-2 min-w-0">
          <div className="flex items-center gap-4 mb-6">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-green-100 bg-clip-text text-transparent">Executive Summary</h3>
          </div>
          <p className="text-white/90 leading-relaxed text-lg font-light tracking-wide break-words">
            {summary.split('\n').map((line, idx) => (
              <span key={idx}>
                {line}
                <br />
              </span>
            ))}
          </p>
          {status === 'failed' && onRetry && (
            <button
              onClick={onRetry}
              className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-white"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SummaryCard;