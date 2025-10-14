
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Loader2, ShieldAlert } from 'lucide-react';
import { getAuth } from 'firebase/auth';

const RiskAssessmentDetail: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRisks = async () => {
      try {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const auth = getAuth();
        const user = auth.currentUser;
        if (!user) {
          throw new Error('User not authenticated');
        }
        const token = await user.getIdToken();
        const response = await fetch(`${apiBaseUrl}/api/analysis/results/${sessionId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch risk assessment');
        }
        const data = await response.json();
        setApiResponse(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load risk assessment');
      } finally {
        setLoading(false);
      }
    };
    if (sessionId) {
      fetchRisks();
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-red-500 text-center">
          <p className="text-xl mb-4">Error loading risk assessment</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-white"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const risks = apiResponse?.risks || [];

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
          <h1 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-red-400" />
            Risk Assessment Overview
          </h1>
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-red-400 mb-4">Identified Risks</h3>
            {risks.length === 0 ? (
              <div className="text-[#888] italic">No risks found for this session.</div>
            ) : (
              <ul className="list-disc pl-6 space-y-2 text-red-200">
                {risks.map((risk: string, i: number) => (
                  <li key={i} className="text-lg">{risk}</li>
                ))}
              </ul>
            )}
          </div>
          {/* Optionally: Show full API response for devs */}
          {/*
          {apiResponse && (
            <pre className="bg-black/60 text-green-300 text-xs rounded-lg p-4 mb-6 overflow-x-auto max-h-64">
              {JSON.stringify(apiResponse, null, 2)}
            </pre>
          )}
          */}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentDetail;
