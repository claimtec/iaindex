'use client';

import React from 'react';
import { cn, getScoreColor } from '@/lib/utils';

interface VisibilityGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function VisibilityGauge({
  score,
  size = 'md',
  showLabel = true,
  className
}: VisibilityGaugeProps) {
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-48 h-48'
  };

  const textSizes = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-5xl'
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={cn('flex flex-col items-center gap-2', className)}>
      <div className={cn('relative', sizeClasses[size])}>
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={cn(
              'transition-all duration-1000 ease-out',
              score >= 80 ? 'text-success' :
              score >= 60 ? 'text-warning' :
              'text-danger'
            )}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn('font-bold', textSizes[size], getScoreColor(score))}>
            {Math.round(score)}
          </span>
        </div>
      </div>
      {showLabel && (
        <p className="text-sm text-gray-600 font-medium">Visibility Score</p>
      )}
    </div>
  );
}
