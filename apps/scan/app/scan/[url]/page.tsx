'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { scanWebsite } from '@/lib/api';

interface ScanStep {
  id: number;
  label: string;
  status: 'pending' | 'active' | 'completed';
}

export default function ScanPage() {
  const router = useRouter();
  const params = useParams();
  const url = decodeURIComponent(params.url as string);

  const [steps, setSteps] = useState<ScanStep[]>([
    { id: 1, label: 'Analyzing website structure...', status: 'active' },
    { id: 2, label: 'Checking ChatGPT visibility...', status: 'pending' },
    { id: 3, label: 'Checking Perplexity visibility...', status: 'pending' },
    { id: 4, label: 'Generating recommendations...', status: 'pending' },
  ]);

  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const performScan = async () => {
      try {
        // Simulate step progression
        const stepDuration = 1500; // 1.5 seconds per step

        for (let i = 0; i < steps.length; i++) {
          await new Promise(resolve => setTimeout(resolve, stepDuration));

          setSteps(prev => prev.map((step, idx) => {
            if (idx < i) return { ...step, status: 'completed' };
            if (idx === i) return { ...step, status: 'completed' };
            if (idx === i + 1) return { ...step, status: 'active' };
            return step;
          }));

          setCurrentStep(i + 1);
        }

        // Call the API to perform the scan
        const result = await scanWebsite(url);

        // Redirect to results page
        router.push(`/results/${result.scan_id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to scan website');
      }
    };

    performScan();
  }, [url, router]);

  const progress = ((currentStep + 1) / steps.length) * 100;

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Scan Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="w-full bg-blue-600 text-white rounded-xl py-3 font-semibold hover:bg-blue-700 transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <motion.div
          className="bg-white rounded-2xl shadow-xl p-8 md:p-12"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4"
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </motion.div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
              Scanning Your Website
            </h1>
            <p className="text-gray-600 break-all">{url}</p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </div>

          {/* Steps */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                className="flex items-center space-x-4"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex-shrink-0">
                  {step.status === 'completed' ? (
                    <motion.div
                      className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    >
                      <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </motion.div>
                  ) : step.status === 'active' ? (
                    <motion.div
                      className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                  ) : (
                    <div className="w-8 h-8 border-4 border-gray-200 rounded-full" />
                  )}
                </div>
                <div className="flex-1">
                  <p className={`font-medium ${
                    step.status === 'active' ? 'text-blue-600' :
                    step.status === 'completed' ? 'text-green-600' :
                    'text-gray-400'
                  }`}>
                    {step.label}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Footer Message */}
          <motion.div
            className="mt-8 p-4 bg-blue-50 rounded-xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <p className="text-sm text-blue-900 text-center">
              Hang tight! We're analyzing your website's AI visibility across multiple platforms...
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
