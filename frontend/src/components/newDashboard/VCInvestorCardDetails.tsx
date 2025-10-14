
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Target, Loader2 } from 'lucide-react';
import { getAuth } from 'firebase/auth';

interface Investor {
  name: string;
  focus: string;
  typical_check: string;
}

const InvestorCard: React.FC<{ investor: Investor; index: number; type: 'vc' | 'angel' }> = ({ investor, index, type }) => {
  return (
    <div
      className={`group relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl hover:shadow-blue-500/20 transition-all duration-700 hover:scale-105 animate-fade-in-up overflow-hidden`}
      style={{ animationDelay: `${index * 150}ms` }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
      <div className="relative z-10">
        <div className="flex items-center gap-4 mb-4">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${type === 'vc' ? 'bg-gradient-to-r from-blue-500 to-green-500' : 'bg-gradient-to-r from-pink-500 to-yellow-500'}`}>
            <Target className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-500">
            {investor.name}
          </h3>
        </div>
        <div className="mb-2 text-[#CCCCCC] text-base"><span className="font-semibold">Focus:</span> {investor.focus}</div>
        <div className="mb-2 text-[#CCCCCC] text-base"><span className="font-semibold">Typical Check:</span> {investor.typical_check}</div>
      </div>
    </div>
  );
};

const VCInvestorCardDetails: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [vcList, setVcList] = useState<Investor[]>([]);
  const [angelList, setAngelList] = useState<Investor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInvestors = async () => {
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
          throw new Error('Failed to fetch investors data');
        }
        const data = await response.json();
        setVcList(data.venture_capitalists || []);
        setAngelList(data.angel_investors || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load investors');
      } finally {
        setLoading(false);
      }
    };
    if (sessionId) {
      fetchInvestors();
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
          <p className="text-xl mb-4">Error loading investors</p>
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
                VC Matching Details
              </h1>
            </div>
            <p className="text-[#CCCCCC] text-xl font-light tracking-wide">
              Comprehensive analysis of key investors in the startup validation space with strategic positioning insights.
            </p>
          </div>
          {/* Venture Capitalists */}
          <h2 className="text-2xl font-bold text-blue-300 mb-6">Venture Capitalists</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-16">
            {vcList.map((investor, index) => (
              <InvestorCard key={investor.name} investor={investor} index={index} type="vc" />
            ))}
          </div>
          {/* Angel Investors */}
          <h2 className="text-2xl font-bold text-pink-300 mb-6">Angel Investors</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            {angelList.map((investor, index) => (
              <InvestorCard key={investor.name} investor={investor} index={index} type="angel" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VCInvestorCardDetails;