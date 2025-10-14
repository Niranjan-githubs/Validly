
import React from 'react';
import { TrendingUp, DollarSign, Target, AlertTriangle, Shield, Zap, Globe, Users, Calendar, Link as LinkIcon } from 'lucide-react';

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
  threatLevel?: string | null;
}

interface CompetitorCardProps {
  competitor: Competitor;
  index: number;
}

const CompetitorCard: React.FC<CompetitorCardProps> = ({ competitor, index }) => {
  // Status color for company status (e.g. Acquired, Active, etc.)
  const getStatusStyle = (status: string | null) => {
    if (!status) return { bg: 'from-gray-500 to-gray-600', glow: 'shadow-gray-500/25' };
    if (status.includes('Acquired') || status.includes('Merged')) {
      return { bg: 'from-purple-500 to-blue-500', glow: 'shadow-purple-500/25' };
    }
    return { bg: 'from-green-500 to-emerald-500', glow: 'shadow-green-500/25' };
  };

  // Compute threat level and style
  const threatLevel = competitor.threatLevel || 'Medium';
  const getThreatStyle = (level: string) => {
    switch (level) {
      case 'High':
        return { text: 'text-red-500 border-red-500' };
      case 'Low':
        return { text: 'text-green-400 border-green-400' };
      default:
        return { text: 'text-yellow-400 border-yellow-400' };
    }
  };
  const threatStyle = getThreatStyle(threatLevel);
  const statusStyle = getStatusStyle(competitor.status);

  return (
    <div 
      className="group relative bg-gradient-to-br from-black via-[#111] to-black border border-[#222] rounded-3xl p-8 shadow-xl hover:shadow-blue-500/20 transition-all duration-700 hover:scale-105 animate-fade-in-up overflow-hidden"
      style={{ animationDelay: `${index * 150}ms` }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-500 mb-2">
              {competitor.name}
            </h3>
            <div className="flex items-center gap-3 text-[#CCCCCC] flex-wrap mb-2">
              {competitor.funding && <><DollarSign className="w-4 h-4" /><span className="text-sm font-medium">{competitor.funding}</span></>}
              {competitor.year_founded && <><Calendar className="w-4 h-4 ml-4" /><span className="text-sm font-medium">Founded: {competitor.year_founded}</span></>}
              {competitor.headquarters && <><Globe className="w-4 h-4 ml-4" /><span className="text-sm font-medium">{competitor.headquarters}</span></>}
            </div>
            {competitor.ownership_status && (
              <div className="text-xs text-[#CCCCCC] mb-1">Ownership: {competitor.ownership_status}</div>
            )}
            {competitor.status && (
              <div className="text-xs text-[#CCCCCC] mb-1">Status: {competitor.status}</div>
            )}
          </div>
          {/* Status Indicator */}
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r ${statusStyle.bg} ${statusStyle.glow} shadow-lg`}>
            <span className="text-xs font-bold text-white">{competitor.status || 'Active'}</span>
          </div>
        </div>

        {/* Description */}
        {competitor.description && (
          <div className="mb-4">
            <div className="text-[#CCCCCC] leading-relaxed group-hover:text-white/90 transition-colors duration-500 text-base font-light">
              {competitor.description}
            </div>
          </div>
        )}

        {/* Industries & Verticals */}
        {(competitor.industries || competitor.verticals) && (
          <div className="mb-4 flex flex-wrap gap-2">
            {competitor.industries && competitor.industries.map((ind, idx) => (
              <span key={idx} className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-300 text-xs font-semibold">{ind}</span>
            ))}
            {competitor.verticals && competitor.verticals.map((vert, idx) => (
              <span key={idx} className="px-3 py-1 rounded-full bg-purple-500/10 text-purple-300 text-xs font-semibold">{vert}</span>
            ))}
          </div>
        )}

        {/* Employees & Revenue */}
        {(competitor.employees || competitor.revenue) && (
          <div className="flex gap-6 mb-4">
            {competitor.employees && (
              <div className="flex items-center gap-2 text-[#CCCCCC]">
                <Users className="w-4 h-4" />
                <span className="text-sm">Employees: {competitor.employees}</span>
              </div>
            )}
            {competitor.revenue && (
              <div className="flex items-center gap-2 text-[#CCCCCC]">
                <DollarSign className="w-4 h-4" />
                <span className="text-sm">Revenue: {competitor.revenue}</span>
              </div>
            )}
          </div>
        )}

        {/* Website & Profile Links */}
        {(competitor.website || competitor.url) && (
          <div className="mb-4 flex flex-col gap-1">
            {competitor.website && (
              <div className="flex items-center gap-2">
                <LinkIcon className="w-4 h-4 text-blue-400" />
                <a href={competitor.website} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-200 underline break-all">{competitor.website}</a>
              </div>
            )}
            {competitor.url && (
              <div className="flex items-center gap-2">
                <LinkIcon className="w-4 h-4 text-blue-400" />
                <a href={competitor.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-200 underline break-all">{competitor.url}</a>
              </div>
            )}
          </div>
        )}

        {/* Social Media */}
        {competitor.social_media && (
          <div className="flex gap-4 mb-4">
            {competitor.social_media.Twitter && (
              <a href={competitor.social_media.Twitter} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-200 underline">Twitter</a>
            )}
            {competitor.social_media.LinkedIn && (
              <a href={competitor.social_media.LinkedIn} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-200 underline">LinkedIn</a>
            )}
          </div>
        )}

        {/* Divider & Threat Assessment */}
        <div className="mt-8 pt-6 border-t border-[#333333] group-hover:border-blue-400/30 transition-colors duration-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/25">
                <TrendingUp className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-semibold text-white">Threat Assessment</span>
            </div>
            <div className={`px-3 py-1 rounded-full border ${threatStyle.text} border-current`}>
              <span className="text-xs font-bold">{threatLevel} Risk</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitorCard; 