import React, { ReactNode } from 'react';

interface GlassmorphicCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

const GlassmorphicCard: React.FC<GlassmorphicCardProps> = ({ 
  children, 
  className = '', 
  glowColor = 'rgba(139, 92, 246, 0.3)', // Default purple glow
  onClick,
  hoverable = false
}) => {
  return (
    <div 
      className={`relative bg-gray-900/40 backdrop-blur-lg border border-gray-800 rounded-xl shadow-xl overflow-hidden ${
        hoverable ? 'transition-transform hover:scale-[1.02]' : ''
      } ${onClick ? 'cursor-pointer' : ''} ${className}`}
      onClick={onClick}
      style={{
        boxShadow: `0 8px 32px -8px rgba(0, 0, 0, 0.6), 0 0 16px ${glowColor}`
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-gray-800/20 to-gray-900/20 pointer-events-none"></div>
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

export default GlassmorphicCard;