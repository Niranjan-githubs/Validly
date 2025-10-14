
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Loader2 } from 'lucide-react';
import { getAuth } from 'firebase/auth';

interface PainPoint {
  title: string;
  comment: string;
  author: string;
  score: number;
  url: string;
  subreddit?: string;
  pain_indicators?: string[];
  relevance_score?: number;
}

const PainPointCard: React.FC<{ pain: PainPoint; index: number }> = ({ pain, index }) => {
  return (
    <div
      className="group relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl hover:shadow-blue-500/20 transition-all duration-700 hover:scale-105 animate-fade-in-up overflow-hidden"
      style={{ animationDelay: `${index * 120}ms` }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 via-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
      <div className="relative z-10">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg bg-gradient-to-r from-pink-500 to-blue-500">
            <AlertTriangle className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold bg-gradient-to-r from-white to-pink-100 bg-clip-text text-transparent group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-500">
            {pain.title}
          </h3>
        </div>
        <div className="mb-2 text-[#CCCCCC] text-base"><span className="font-semibold">Author:</span> {pain.author}</div>
        <div className="mb-2 text-[#CCCCCC] text-base"><span className="font-semibold">Score:</span> {pain.score}</div>
        {pain.pain_indicators && pain.pain_indicators.length > 0 && (
          <div className="mb-2 text-[#CCCCCC] text-base">
            <span className="font-semibold">Pain Indicators:</span> {pain.pain_indicators.join(', ')}
          </div>
        )}
        {pain.relevance_score !== undefined && (
          <div className="mb-2 text-[#CCCCCC] text-base">
            <span className="font-semibold">Relevance Score:</span> {pain.relevance_score}
          </div>
        )}
        <div className="mb-2 text-[#CCCCCC] text-base"><span className="font-semibold">Subreddit:</span> {pain.subreddit}</div>
        <div className="mb-2 text-[#CCCCCC] text-base"><span className="font-semibold">Comment:</span> {pain.comment}</div>
        <a
          href={pain.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-4 text-blue-400 hover:underline hover:text-blue-300 transition-colors duration-200"
        >
          View Source
        </a>
      </div>
    </div>
  );
};

const UserPainpointDetails: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [painPoints, setPainPoints] = useState<PainPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPainPoints = async () => {
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
          throw new Error('Failed to fetch user pain points');
        }
        const data = await response.json();
        setPainPoints(data.user_pain_points || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load user pain points');
      } finally {
        setLoading(false);
      }
    };
    if (sessionId) {
      fetchPainPoints();
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-pink-500 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-red-500 text-center">
          <p className="text-xl mb-4">Error loading user pain points</p>
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

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-gradient-to-r from-pink-500/5 to-blue-500/5 rounded-full blur-3xl animate-pulse-slow"></div>
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
              className="group flex items-center gap-3 text-[#CCCCCC] hover:text-white mb-8 transition-all duration-500 hover:bg-gradient-to-r hover:from-[#333333] hover:to-[#444444] px-4 py-2 rounded-xl border border-transparent hover:border-pink-400/30"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-2 transition-transform duration-500" />
              Back to Dashboard
            </button>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-pink-500/25">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-pink-100 to-blue-100 bg-clip-text text-transparent">
                User Pain Points
              </h1>
            </div>
            <p className="text-[#CCCCCC] text-xl font-light tracking-wide">
              Insights into real user pain points and frustrations, extracted from community discussions and feedback.
            </p>
          </div>
          {/* Pain Points */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            {painPoints.length === 0 ? (
              <div className="col-span-2 text-center text-[#888] text-lg">No user pain points found for this session.</div>
            ) : (
              painPoints.map((pain, index) => (
                <PainPointCard key={pain.url + index} pain={pain} index={index} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserPainpointDetails;
