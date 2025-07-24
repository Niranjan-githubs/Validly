import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const IdeaAgentDetail: React.FC = () => {
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
          <h1 className="text-3xl font-bold text-white mb-6">Idea Agent Analysis</h1>
          <p className="text-white leading-relaxed text-lg">
            Your startup idea demonstrates strong technical innovation with clear market validation potential. The concept addresses a significant pain point in the target market with a novel approach that differentiates from existing solutions. Key strengths include a compelling value proposition, scalable business model, and alignment with emerging market trends. The technical feasibility assessment indicates moderate complexity with available talent and resources. Recommended next steps include prototype development, user feedback collection, and market size validation through targeted research initiatives.
          </p>
        </div>
      </div>
    </div>
  );
};

export default IdeaAgentDetail;
