import React from 'react';

/**
 * A curved black box to cover the Spline.io "Built with Spline" watermark/footer.
 * Place this component absolutely at the bottom of the Spline canvas.
 */
const SplineFooterCover: React.FC = () => (
  <div
    className="pointer-events-none select-none"
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 30,
      width: '101vw',
      height: '48px',
      background: 'transparent',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'flex-end',
      pointerEvents: 'none',
    }}
  >
    <div
      className="w-full h-14 bg-black opacity-95 shadow-lg pointer-events-none md:w-[170px] md:h-[54px] md:rounded-full md:ml-auto md:mr-6 md:mb-4"
      style={{
        boxShadow: '0 2px 16px 0 rgba(0,0,0,0.25)',
      }}
    />
  </div>
);

export default SplineFooterCover;
