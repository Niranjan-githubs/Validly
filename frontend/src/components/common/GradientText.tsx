import React from 'react';

const GradientText: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <span
    className={`bg-gradient-to-r from-[#A7A9AC] to-[#E0E4E6] bg-clip-text text-transparent ${className}`}
    style={{ WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
  >
    {children}
  </span>
);

export default GradientText;