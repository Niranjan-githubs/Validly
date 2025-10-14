import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Target, Loader2 } from 'lucide-react';
import { getAuth } from 'firebase/auth';
import CompetitorCard from './CompetitorCard';

interface SocialMedia {
  Twitter?: string;
  LinkedIn?: string;
  [key: string]: string | undefined;
}

interface Competitor {
  name: string;
  description: string | null;
  employees: string | null;
  funding: string | null;
  headquarters: string | null;
  industries: string[] | null;
  ownership_status: string | null;
  revenue: string | null;
  social_media: SocialMedia | null;
  status: string | null;
  url: string;
  verticals: string[] | null;
  website: string | null;
  year_founded: string | null;
}

const CompetitorIntelligence: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompetitors = async () => {
      try {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        // Get Firebase ID token
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
          throw new Error('Failed to fetch competitors data');
        }
        const data = await response.json();
        const competitorsData = data.competitors || [];
        const validCompetitors = competitorsData.filter((comp: any) => comp.name && comp.url);
        setCompetitors(validCompetitors);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load competitors');
      } finally {
        setLoading(false);
      }
    };
    if (sessionId) {
      fetchCompetitors();
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
          <p className="text-xl mb-4">Error loading competitors</p>
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