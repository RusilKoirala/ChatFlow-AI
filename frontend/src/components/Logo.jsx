import React from 'react';

const Logo = ({ size = 'md', className = '', showText = false, theme = 'light' }) => {
  const sizes = {
    xs: 'w-6 h-6',
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20',
    '2xl': 'w-24 h-24'
  };

  const textSizes = {
    xs: 'text-xs',
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl',
    xl: 'text-2xl',
    '2xl': 'text-3xl'
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className={`${sizes[size]} relative flex-shrink-0`}>
        {/* Main logo circle with gradient */}
        <div className="w-full h-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-2xl shadow-lg flex items-center justify-center relative overflow-hidden">
          {/* Inner glow effect */}
          <div className="absolute inset-1 bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400 rounded-xl opacity-50"></div>
          
          {/* Logo symbol - stylized "A" for AI */}
          <div className="relative z-10 text-white font-bold flex items-center justify-center">
            <svg 
              viewBox="0 0 24 24" 
              className={`${size === 'xs' ? 'w-3 h-3' : size === 'sm' ? 'w-4 h-4' : size === 'md' ? 'w-5 h-5' : size === 'lg' ? 'w-8 h-8' : 'w-10 h-10'} fill-current`}
            >
              {/* Stylized "A" with neural network pattern */}
              <path d="M12 2L3 22h3.5l1.5-4h8l1.5 4H21L12 2zm-2.5 12L12 8l2.5 6h-5z" />
              {/* Neural network dots */}
              <circle cx="8" cy="16" r="1" opacity="0.7" />
              <circle cx="16" cy="16" r="1" opacity="0.7" />
              <circle cx="12" cy="12" r="0.8" opacity="0.5" />
            </svg>
          </div>
        </div>
        
        {/* Online indicator */}
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white shadow-sm"></div>
      </div>
      
      {showText && (
        <div className="flex flex-col">
          <h1 className={`font-bold ${textSizes[size]} ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            ChatFlow AI
          </h1>
          <p className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'} -mt-1`}>
            Intelligent Assistant
          </p>
        </div>
      )}
    </div>
  );
};

export default Logo;