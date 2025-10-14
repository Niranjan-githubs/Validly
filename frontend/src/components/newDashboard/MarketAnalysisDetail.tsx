import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { getAuth } from 'firebase/auth';

const MarketAnalysisDetail: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
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
          throw new Error('Failed to fetch market analysis');
        }
        const data = await response.json();
        setApiResponse(data);
        // eslint-disable-next-line no-console
      
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load market analysis');
      } finally {
        setLoading(false);
      }
    };
    if (sessionId) {
      fetchAnalysis();
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
          <p className="text-xl mb-4">Error loading market analysis</p>
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

  // Helper renderers
  const renderList = (items: any[], color = "text-white") => (
    <ul className={`list-disc pl-6 space-y-1 ${color}`}>
      {items && items.length > 0 ? items.map((item, i) => <li key={i}>{item}</li>) : <li className="italic opacity-60">None</li>}
    </ul>
  );

  const ma = apiResponse?.market_analysis || {};
  const risks = apiResponse?.market_risks || apiResponse?.risks || ma.market_risks || [];
  const recommendations = apiResponse?.recommendations || [];
  const investments = ma.recent_investments || [];
  const customerSegments = ma.customer_segments || [];

  // Modern progress bar for TAM/SAM/SOM (fake values for demo if not present)
  const parseValue = (val: string | undefined) => {
    if (!val) return 0;
    const num = parseFloat(val.replace(/[^\d.]/g, ''));
    if (val.includes('B')) return num * 1e9;
    if (val.includes('M')) return num * 1e6;
    return num;
  };
  const tam = parseValue(ma.TAM);
  const sam = parseValue(ma.SAM);
  const som = parseValue(ma.SOM);
  const maxMarket = Math.max(tam, sam, som, 1);

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
          <h1 className="text-3xl font-bold text-white mb-8">Market Analysis Report</h1>

          {/* TAM/SAM/SOM as big round ring cards with value-matching fill */}
          <div className="flex flex-col sm:flex-row gap-8 mb-12 items-center justify-center">
            {/* TAM */}
            <div className="flex flex-col items-center">
              <div className="relative flex items-center justify-center">
                <div
                  className="w-40 h-40 rounded-full flex items-center justify-center bg-black shadow-2xl"
                  style={{
                    background: `conic-gradient(#3b82f6 ${Math.round((tam / maxMarket) * 360)}deg, #1e293b 0deg)`
                  }}
                >
                  <div className="w-32 h-32 rounded-full bg-black flex items-center justify-center">
                    <span className="text-3xl font-extrabold text-white text-center select-text break-words">{ma.TAM || <span className='italic opacity-60'>N/A</span>}</span>
                  </div>
                </div>
                <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-blue-400 font-bold text-lg whitespace-nowrap">TAM</span>
              </div>
              <span className="mt-12 text-blue-300/70 text-sm font-medium">Total Addressable</span>
            </div>
            {/* SAM */}
            <div className="flex flex-col items-center">
              <div className="relative flex items-center justify-center">
                <div
                  className="w-40 h-40 rounded-full flex items-center justify-center bg-black shadow-2xl"
                  style={{
                    background: `conic-gradient(#22c55e ${Math.round((sam / maxMarket) * 360)}deg, #1e293b 0deg)`
                  }}
                >
                  <div className="w-32 h-32 rounded-full bg-black flex items-center justify-center">
                    <span className="text-3xl font-extrabold text-white text-center select-text break-words">{ma.SAM || <span className='italic opacity-60'>N/A</span>}</span>
                  </div>
                </div>
                <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-green-400 font-bold text-lg whitespace-nowrap">SAM</span>
              </div>
              <span className="mt-12 text-green-300/70 text-sm font-medium">Serviceable</span>
            </div>
            {/* SOM */}
            <div className="flex flex-col items-center">
              <div className="relative flex items-center justify-center">
                <div
                  className="w-40 h-40 rounded-full flex items-center justify-center bg-black shadow-2xl"
                  style={{
                    background: `conic-gradient(#a21caf ${Math.round((som / maxMarket) * 360)}deg, #1e293b 0deg)`
                  }}
                >
                  <div className="w-32 h-32 rounded-full bg-black flex items-center justify-center">
                    <span className="text-3xl font-extrabold text-white text-center select-text break-words">{ma.SOM || <span className='italic opacity-60'>N/A</span>}</span>
                  </div>
                </div>
                <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-purple-400 font-bold text-lg whitespace-nowrap">SOM</span>
              </div>
              <span className="mt-12 text-purple-300/70 text-sm font-medium">Obtainable</span>
            </div>
          </div>

          {/* Industry, Trend, Pricing as text */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Industry</h3>
            <p className="text-white/90 mb-4">{ma.industry || <span className="italic opacity-60">N/A</span>}</p>
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Market Trend</h3>
            <p className="text-white/90 mb-4">{ma.market_trend || <span className="italic opacity-60">N/A</span>}</p>
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Pricing Opportunity</h3>
            <p className="text-white/90 mb-4">{ma.pricing_opportunity || <span className="italic opacity-60">N/A</span>}</p>
          </div>

          {/* Customer Segments as text */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Customer Segments</h3>
            {renderList(customerSegments)}
          </div>

          {/* Market Risks as text */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-red-400 mb-2">Market Risks</h3>
            {renderList(risks, "text-red-300")}
          </div>

          {/* Recent Investments as text */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-green-400 mb-2">Recent Investments</h3>
            {renderList(investments, "text-green-300")}
          </div>

          {/* Recommendations as text */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Recommendations</h3>
            {renderList(recommendations, "text-blue-200")}
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

export default MarketAnalysisDetail;
