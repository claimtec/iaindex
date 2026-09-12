'use client';

import { motion } from 'framer-motion';

interface PlatformScoreProps {
  platform: string;
  score: number;
  logo: string;
}

export default function PlatformScore({ platform, score, logo }: PlatformScoreProps) {
  // Determine status and colors based on score
  const getStatus = () => {
    if (score <= 30) return { label: 'Poor', color: 'text-red-600', bg: 'bg-red-50', bar: 'bg-red-500' };
    if (score <= 60) return { label: 'Fair', color: 'text-yellow-600', bg: 'bg-yellow-50', bar: 'bg-yellow-500' };
    if (score <= 80) return { label: 'Good', color: 'text-green-600', bg: 'bg-green-50', bar: 'bg-green-500' };
    return { label: 'Excellent', color: 'text-blue-600', bg: 'bg-blue-50', bar: 'bg-blue-500' };
  };

  const status = getStatus();

  return (
    <motion.div
      className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.3 }}
    >
      {/* Platform Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-4xl">{logo}</div>
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{platform}</h3>
            <p className={`text-sm font-medium ${status.color}`}>{status.label}</p>
          </div>
        </div>
      </div>

      {/* Score Display */}
      <div className="mb-4">
        <div className="flex items-end justify-between mb-2">
          <span className="text-4xl font-bold text-gray-900">{score}</span>
          <span className="text-lg text-gray-500 mb-1">/100</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          className={`absolute top-0 left-0 h-full ${status.bar} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
        />
      </div>

      {/* Mini stats */}
      <div className={`mt-4 p-3 ${status.bg} rounded-lg`}>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Visibility Index</span>
          <span className={`font-semibold ${status.color}`}>{score}%</span>
        </div>
      </div>
    </motion.div>
  );
}
