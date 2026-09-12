'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface VisibilityGaugeProps {
  score: number;
  size?: number;
}

export default function VisibilityGauge({ score, size = 280 }: VisibilityGaugeProps) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    // Animate score from 0 to actual score
    const duration = 2000; // 2 seconds
    const steps = 60;
    const increment = score / steps;
    let currentStep = 0;

    const interval = setInterval(() => {
      currentStep++;
      if (currentStep >= steps) {
        setDisplayScore(score);
        clearInterval(interval);
      } else {
        setDisplayScore(Math.round(increment * currentStep));
      }
    }, duration / steps);

    return () => clearInterval(interval);
  }, [score]);

  // Calculate stroke properties
  const strokeWidth = 12;
  const radius = (size / 2) - (strokeWidth / 2);
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayScore / 100) * circumference;

  // Determine colors based on score
  const getColor = () => {
    if (score <= 30) return { stroke: '#DC2626', bg: '#FEE2E2', text: '#DC2626' }; // Red
    if (score <= 60) return { stroke: '#F59E0B', bg: '#FEF3C7', text: '#F59E0B' }; // Yellow
    if (score <= 80) return { stroke: '#10B981', bg: '#D1FAE5', text: '#10B981' }; // Green
    return { stroke: '#3B82F6', bg: '#DBEAFE', text: '#3B82F6' }; // Blue
  };

  const getLabel = () => {
    if (score <= 30) return 'Needs Work';
    if (score <= 60) return 'Fair';
    if (score <= 80) return 'Good';
    return 'Excellent';
  };

  const colors = getColor();

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Background circle */}
        <svg className="transform -rotate-90" width={size} height={size}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={colors.bg}
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Animated progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 2, ease: 'easeOut' }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            className="text-6xl font-bold"
            style={{ color: colors.text }}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {displayScore}
          </motion.div>
          <motion.div
            className="text-2xl font-semibold text-gray-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.5 }}
          >
            / 100
          </motion.div>
        </div>
      </div>

      {/* Label */}
      <motion.div
        className="mt-4 px-6 py-2 rounded-full font-semibold text-lg"
        style={{ backgroundColor: colors.bg, color: colors.text }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.5 }}
      >
        {getLabel()}
      </motion.div>
    </div>
  );
}
