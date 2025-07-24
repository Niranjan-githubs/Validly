import React from 'react';
import clsx from 'clsx';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className = '',
  children,
  ...props
}) => {
  const base =
    'inline-flex items-center justify-center font-semibold rounded-lg focus:outline-none transition-all duration-200';
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };
  const variants = {
    primary:
      'bg-transparent border border-white text-white shadow-md hover:bg-white/10 hover:text-white',
    outline:
      'border border-[#D3D8D6] text-[#D3D8D6] bg-transparent hover:bg-[#1C2526] hover:text-white',
  };
  return (
    <button
      className={clsx(
        base,
        sizes[size],
        variants[variant],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;