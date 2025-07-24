import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

// This page is intended for dynamic agent details fetched from backend
const AgentDynamicDetail: React.FC = () => {
  const { agentName } = useParams<{ agentName: string }>();
  const navigate = useNavigate();

  // Placeholder for backend data fetch
  // Replace with actual API call and state management
  const agentData = {
    title: agentName ? `${agentName} Details` : 'Agent Details',
    content: 'Analysis results and detailed insights for this validation agent are being processed. Please check back shortly for comprehensive findings and recommendations.'
  };

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

export default AgentDynamicDetail;
