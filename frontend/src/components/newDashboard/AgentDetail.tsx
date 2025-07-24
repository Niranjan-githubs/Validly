import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const AgentDetail: React.FC = () => {
  const { agentName } = useParams<{ agentName: string }>();
  const navigate = useNavigate();

  const getAgentContent = (agentName: string) => {
    const agentData: { [key: string]: { title: string; content: string } } = {
      'idea-agent': {
        title: 'Idea Agent Analysis',
        content: 'Your startup idea demonstrates strong technical innovation with clear market validation potential. The concept addresses a significant pain point in the target market with a novel approach that differentiates from existing solutions. Key strengths include a compelling value proposition, scalable business model, and alignment with emerging market trends. The technical feasibility assessment indicates moderate complexity with available talent and resources. Recommended next steps include prototype development, user feedback collection, and market size validation through targeted research initiatives.'
      },
      'market-analysis': {
        title: 'Market Analysis Report',
        content: 'Comprehensive market analysis reveals a $32.8B total addressable market with 23% year-over-year growth trajectory. The target segment shows strong demand signals with low regulatory barriers and enterprise adoption rising. Competitive landscape analysis identifies 3 direct competitors with differentiation opportunities in UX and pricing strategies. Market timing appears optimal with emerging technologies creating new opportunities for disruption. Consumer behavior trends support the core value proposition with increasing willingness to adopt innovative solutions in this space.'
      },
      'risk-assessment': {
        title: 'Risk Assessment Overview',
        content: 'Risk analysis identifies moderate overall risk profile with primary concerns in regulatory compliance and market competition. Technical complexity presents manageable challenges with proper resource allocation. Market risks include potential economic downturns affecting customer spending and increased competition from established players. Mitigation strategies include diversified revenue streams, strong intellectual property protection, and strategic partnerships. Regulatory risk assessment shows compliance requirements above industry average with changing landscape requiring ongoing monitoring and adaptation.'
      },
      'vc-matching': {
        title: 'VC Matching Results',
        content: 'AI-driven investor matching analysis identifies 47 potential venture capital firms aligned with your startup profile and industry focus. Portfolio alignment score indicates 89% compatibility with target investors specializing in early-stage technology ventures. Recommended approach includes warm introductions through mutual connections and participation in relevant industry events. Timing analysis suggests optimal fundraising window within the next 6-9 months based on market conditions and startup maturity. Preparation checklist includes financial projections, product demos, and competitive positioning materials.'
      }
    };

    return agentData[agentName || ''] || {
      title: 'Agent Details',
      content: 'Analysis results and detailed insights for this validation agent are being processed. Please check back shortly for comprehensive findings and recommendations.'
    };
  };

  const agentData = getAgentContent(agentName || '');

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/new-dashboard')}
          className="group flex items-center gap-2 text-white/70 hover:text-white mb-8 transition-colors duration-200 bg-transparent border border-blue-500/30 px-6 py-3 rounded-2xl backdrop-blur-lg hover:bg-blue-500/10"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform duration-300" />
          Back to Dashboard
        </button>

        {/* Detail Card */}
        <div className="bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl animate-fade-in">
          <h1 className="text-3xl font-bold text-white mb-6">{agentData.title}</h1>
          <p className="text-white leading-relaxed text-lg">
            {agentData.content}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AgentDetail; 