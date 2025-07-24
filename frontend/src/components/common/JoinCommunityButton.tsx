import React from 'react';

const JoinCommunityButton: React.FC = () => {
  return (
    <>
      {/* Black box overlay to hide Spline badge */}
      <div className="fixed bottom-6 right-6 z-50 w-44 h-12 rounded-full bg-black" style={{ pointerEvents: 'none' }} />
      {/* Community Button (optional, can be commented out if not needed) */}
      {/*
      <div className="fixed bottom-6 right-6 z-50 flex items-center justify-center">
        <button
          className="inline-flex items-center px-6 py-3 border border-white text-white rounded-full font-semibold bg-transparent hover:bg-white/10 transition-all duration-200 shadow-md w-44 h-12 justify-center"
          style={{ fontSize: '1rem' }}
          onClick={() => window.open('https://your-community-link.com', '_blank')}
        >
          Join Community
        </button>
      </div>
      */}
    </>
  );
};

export default JoinCommunityButton; 