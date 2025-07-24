import React from 'react';
import Navbar from '../components/common/Navbar';
import Hero from '../components/landing/Hero';



const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar transparent={true} />
      <Hero />
      
    </div>
  );
};

export default LandingPage;