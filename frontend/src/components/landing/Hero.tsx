import React, { useState } from 'react';
import Spline from '@splinetool/react-spline';
import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import GradientText from '../common/GradientText';
import Button from '../common/Button';
import SplineFooterCover from './SplineFooterCover.tsx';

const Hero: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen flex flex-col items-center overflow-hidden bg-black">
      {/* Blur Overlay */}
      <div
        className={`absolute inset-0 z-20 transition-all duration-700 ${loading ? 'backdrop-blur-md bg-black/40 opacity-100' : 'opacity-0 pointer-events-none'}`}
      />
      <Spline
        scene="https://prod.spline.design/yVw9UTkEVbZX96hX/scene.splinecode"
        className="absolute inset-0 z-0"
        style={{ pointerEvents: 'all' }}
        onLoad={() => setLoading(false)}
      />
      {/* Hero Text and Button at Adjusted Position */}
      <div
        className="relative z-10 container mx-auto px-4 pt-32 flex flex-col items-center text-center" /* Increased pt-32 for downward shift */
        style={{ pointerEvents: 'none' }}
      >
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
           <GradientText>Validate Your Startup Idea With AI-Powered Intelligence </GradientText>
        </h1>
        <p className="text-gray-300 text-xl mb-8 max-w-3xl mx-auto"> 
          Get comprehensive market analysis, competitor insights, and risk assessment for your startup idea in minutes, not months.
        </p>
        {/* Button Row: pointer-events enabled */}
        <div
          className="flex flex-col sm:flex-row items-center justify-center lg:justify-start space-y-4 sm:space-y-0 sm:space-x-4"
          style={{ pointerEvents: 'auto' }}
        >
          <Button
            variant="primary"
            size="lg"
            onClick={() => navigate('/login')}
            className="group"
          >
            Start Validating My Idea
            <ChevronRight className="ml-2 h-5 w-5 group-hover:translate-x-1" />
          </Button>
        </div>
      </div>
      {/* Curved black box to hide Spline watermark/footer */}
      <SplineFooterCover />
    </div>
  );
};

export default Hero;