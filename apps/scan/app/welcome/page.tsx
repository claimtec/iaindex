'use client';

import { motion } from 'framer-motion';
import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { CheckCircleIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

function WelcomeContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    if (sessionId) {
      verifySession();
    } else {
      setError('No session ID provided');
      setLoading(false);
    }
  }, [sessionId]);

  const verifySession = async () => {
    try {
      // In production, you would verify the session with your backend
      // For now, we'll just show the welcome message
      setLoading(false);
    } catch (err) {
      console.error('Session verification error:', err);
      setError('Failed to verify payment session');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verifying your payment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-md mx-auto px-4 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Something went wrong
          </h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <a
            href="/pricing"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Back to Pricing
          </a>
        </div>
      </div>
    );
  }

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.6 } },
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg"></div>
              <span className="text-xl font-bold">IAIndex</span>
            </div>
            <a
              href={process.env.NEXT_PUBLIC_APP_URL || 'https://app.iaindex.org'}
              className="text-sm text-gray-600 hover:text-gray-900 transition"
            >
              Go to Dashboard
            </a>
          </div>
        </div>
      </nav>

      {/* Success Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          className="text-center"
          initial="initial"
          animate="animate"
          variants={staggerChildren}
        >
          {/* Success Icon */}
          <motion.div variants={fadeIn}>
            <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircleIcon className="w-12 h-12 text-white" />
            </div>
          </motion.div>

          {/* Title */}
          <motion.h1
            className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4"
            variants={fadeIn}
          >
            Welcome to{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              IAIndex
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            className="text-xl text-gray-600 mb-8"
            variants={fadeIn}
          >
            Your subscription is now active!
          </motion.p>

          {/* Welcome Email Confirmation */}
          <motion.div
            className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8 inline-block"
            variants={fadeIn}
          >
            <p className="text-blue-800">
              We've sent a welcome email with your account details and next steps.
              Please check your inbox.
            </p>
          </motion.div>

          {/* Next Steps */}
          <motion.div
            className="bg-white rounded-2xl shadow-lg p-8 mb-8 text-left"
            variants={fadeIn}
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              Next Steps
            </h2>

            <div className="space-y-4">
              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mr-4 mt-1">
                  <span className="text-blue-600 font-semibold">1</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Add Your First Website
                  </h3>
                  <p className="text-gray-600">
                    Start monitoring your website's AI visibility by adding it to your
                    dashboard.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mr-4 mt-1">
                  <span className="text-blue-600 font-semibold">2</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Review Your Visibility Score
                  </h3>
                  <p className="text-gray-600">
                    See how visible your website is across ChatGPT, Perplexity, Claude,
                    and other AI search engines.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mr-4 mt-1">
                  <span className="text-blue-600 font-semibold">3</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Implement Recommendations
                  </h3>
                  <p className="text-gray-600">
                    Follow our AI-optimized schema recommendations to improve your
                    visibility score.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mr-4 mt-1">
                  <span className="text-blue-600 font-semibold">4</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Track Your Progress
                  </h3>
                  <p className="text-gray-600">
                    Monitor your visibility improvements over time with detailed
                    analytics and reports.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* CTA Button */}
          <motion.div variants={fadeIn}>
            <a
              href={process.env.NEXT_PUBLIC_APP_URL || 'https://app.iaindex.org'}
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105"
            >
              Go to Dashboard
              <ArrowRightIcon className="w-5 h-5 ml-2" />
            </a>
          </motion.div>

          {/* Support */}
          <motion.div className="mt-12 pt-8 border-t" variants={fadeIn}>
            <p className="text-gray-600 mb-2">Need help getting started?</p>
            <div className="flex justify-center space-x-6 text-sm">
              <a
                href="#"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                View Documentation
              </a>
              <span className="text-gray-400">|</span>
              <a
                href="#"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Contact Support
              </a>
              <span className="text-gray-400">|</span>
              <a
                href="#"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Watch Tutorial
              </a>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Highlight */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t">
        <h2 className="text-3xl font-bold text-center mb-12">
          What's Included in Your Plan
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Real-time Analytics</h3>
            <p className="text-gray-600">
              Track your AI visibility across all major platforms with detailed
              analytics and insights.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Optimization</h3>
            <p className="text-gray-600">
              Get personalized recommendations to improve your schema markup and AI
              visibility.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Email Reports</h3>
            <p className="text-gray-600">
              Receive regular email reports with your visibility scores and
              actionable insights.
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
}

export default function WelcomePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <WelcomeContent />
    </Suspense>
  );
}
