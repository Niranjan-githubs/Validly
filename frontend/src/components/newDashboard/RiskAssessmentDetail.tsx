import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const RiskAssessmentDetail: React.FC = () => {
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
          <h1 className="text-3xl font-bold text-white mb-6">Risk Assessment Overview</h1>
          <p className="text-white leading-relaxed text-lg">
            Risk analysis identifies moderate overall risk profile with primary concerns in regulatory compliance and market competition. Technical complexity presents manageable challenges with proper resource allocation. Market risks include potential economic downturns affecting customer spending and increased competition from established players. Mitigation strategies include diversified revenue streams, strong intellectual property protection, and strategic partnerships. Regulatory risk assessment shows compliance requirements above industry average with changing landscape requiring ongoing monitoring and adaptation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentDetail;
