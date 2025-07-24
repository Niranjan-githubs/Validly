import React, { useState, useEffect } from 'react';
import { Brain } from 'lucide-react';

interface FloatingOrbProps {
  size?: 'sm' | 'md' | 'lg';
  isThinking?: boolean;
  color?: string;
  className?: string;
}

const FloatingOrb: React.FC<FloatingOrbProps> = ({
  size = 'md',
  isThinking = false,
  color = 'purple',
  className = '',
}) => {
  const [offset, setOffset] = useState(0);
  
  useEffect(() => {
    let animationFrame: number;
    let startTime = Date.now();
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const newOffset = Math.sin(elapsed / 1000) * 5;
      setOffset(newOffset);
      animationFrame = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      cancelAnimationFrame(animationFrame);
    };
  }, []);
  
  const sizeMap = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };
  
  const colorMap = {
    blue: 'from-blue-500 to-blue-600 shadow-blue-500/50',
    green: 'from-green-500 to-green-600 shadow-green-500/50',
    red: 'from-red-500 to-red-600 shadow-red-500/50',
    yellow: 'from-yellow-500 to-yellow-600 shadow-yellow-500/50',
    purple: 'from-purple-500 to-purple-600 shadow-purple-500/50',
  };
  
  return (
    <div 
      className={`relative ${sizeMap[size]} ${className}`}
      style={{ transform: `translateY(${offset}px)` }}
    >
      <div className={`absolute inset-0 rounded-full bg-gradient-to-br ${colorMap[color as keyof typeof colorMap]} opacity-50 blur-lg animate-pulse`}></div>
      <div 
        className={`absolute inset-0 flex items-center justify-center rounded-full bg-gradient-to-br ${colorMap[color as keyof typeof colorMap]} shadow-lg`}
      >
        <Brain className="w-1/2 h-1/2 text-white" />
      </div>
      
      {isThinking && (
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
          <div className="flex space-x-1">
            {[...Array(3)].map((_, i) => (
              <div 
                key={i} 
                className={`w-1.5 h-1.5 rounded-full bg-${color}-400`}
                style={{ 
                  animation: `bounce 1s infinite ${i * 0.2}s`,
                }}
              ></div>
            ))}
          </div>
        </div>
      )}
      
      <style>{`
        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-4px);
          }
        }
      `}</style>
    </div>
  );
};

export default FloatingOrb;