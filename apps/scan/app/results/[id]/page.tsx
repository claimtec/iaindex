'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import VisibilityGauge from '@/components/VisibilityGauge';
import PlatformScore from '@/components/PlatformScore';
import { getScanResults, submitEmail } from '@/lib/api';

interface ScanResult {
  scan_id: string;
  url: string;
  visibility_score: number;
  platform_scores: {
    chatgpt: number;
    perplexity: number;
    claude: number;
  };
  recommendations: Array<{
    title: string;
    description: string;
    impact_score: number;
    priority: 'critical' | 'high' | 'medium';
  }>;
  scanned_at: string;
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const scanId = params.id as string;

  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [emailSubmitted, setEmailSubmitted] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getScanResults(scanId);
        setResults(data);
      } catch (error) {
        console.error('Failed to fetch results:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [scanId]);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !results) return;

    setEmailLoading(true);
    try {
      await submitEmail(scanId, email);
      setEmailSubmitted(true);
    } catch (error) {
      console.error('Failed to submit email:', error);
    } finally {
      setEmailLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score <= 30) return 'text-red-600';
    if (score <= 60) return 'text-yellow-600';
    if (score <= 80) return 'text-green-600';
    return 'text-blue-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score <= 30) return 'bg-red-50';
    if (score <= 60) return 'bg-yellow-50';
    if (score <= 80) return 'bg-green-50';
    return 'bg-blue-50';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const shareOnTwitter = () => {
    const text = `I just checked my website's AI visibility score: ${results?.visibility_score}/100! Check yours for free at`;
    const url = 'https://scan.iaindex.org';
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
  };

  const shareOnLinkedIn = () => {
    const url = 'https://scan.iaindex.org';
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Results not found</h2>
          <p className="text-gray-600 mb-6">The scan you're looking for doesn't exist.</p>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition"
          >
            Start New Scan
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Your AI Visibility Report
          </h1>
          <p className="text-gray-600 break-all">{results.url}</p>
        </motion.div>

        {/* Main Score */}
        <motion.div
          className={`${getScoreBgColor(results.visibility_score)} rounded-3xl p-8 md:p-12 mb-8`}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Overall Visibility Score
            </h2>
            <VisibilityGauge score={results.visibility_score} />
          </div>
        </motion.div>

        {/* Platform Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Breakdown</h2>
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <PlatformScore
              platform="ChatGPT"
              score={results.platform_scores.chatgpt}
              logo="🤖"
            />
            <PlatformScore
              platform="Perplexity"
              score={results.platform_scores.perplexity}
              logo="🔍"
            />
            <PlatformScore
              platform="Claude"
              score={results.platform_scores.claude}
              logo="🧠"
            />
          </div>
        </motion.div>

        {/* Recommendations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Top Recommendations
          </h2>
          <div className="space-y-4 mb-12">
            {results.recommendations.slice(0, 3).map((rec, index) => (
              <motion.div
                key={index}
                className="bg-white rounded-2xl p-6 shadow-lg"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">
                    {rec.title}
                  </h3>
                  <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getPriorityColor(rec.priority)}`}>
                    {rec.priority.toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-600 mb-4">{rec.description}</p>
                <div className="flex items-center">
                  <span className="text-sm text-gray-500 mr-2">Impact Score:</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                      style={{ width: `${rec.impact_score}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-700 ml-2">
                    {rec.impact_score}/100
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Email Capture */}
        {!emailSubmitted ? (
          <motion.div
            className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-8 md:p-12 text-white mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h2 className="text-3xl font-bold mb-4">Want the Full Report?</h2>
            <p className="text-blue-100 mb-6 text-lg">
              Get your detailed 10-page report + weekly monitoring sent to your inbox
            </p>
            <form onSubmit={handleEmailSubmit} className="flex flex-col sm:flex-row gap-4">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-4 focus:ring-blue-300"
                required
              />
              <button
                type="submit"
                disabled={emailLoading}
                className="bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold hover:bg-gray-100 transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {emailLoading ? 'Sending...' : 'Get Report'}
              </button>
            </form>
          </motion.div>
        ) : (
          <motion.div
            className="bg-green-50 rounded-3xl p-8 md:p-12 text-center mb-8"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email!</h3>
            <p className="text-gray-600">
              We've sent your detailed report to <span className="font-semibold">{email}</span>
            </p>
          </motion.div>
        )}

        {/* CTA Section */}
        <motion.div
          className="bg-white rounded-3xl p-8 md:p-12 shadow-xl text-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Improve Your Score?
          </h2>
          <p className="text-gray-600 mb-8 text-lg">
            Join IAIndex and get automated AI visibility optimization for your website
          </p>
          <a
            href="https://app.iaindex.org/signup"
            className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all transform hover:scale-105"
          >
            Fix My Visibility Score
          </a>
        </motion.div>

        {/* Share & Actions */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <button
            onClick={shareOnTwitter}
            className="flex items-center space-x-2 bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-600 transition"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
            </svg>
            <span>Share on Twitter</span>
          </button>
          <button
            onClick={shareOnLinkedIn}
            className="flex items-center space-x-2 bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-800 transition"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
            </svg>
            <span>Share on LinkedIn</span>
          </button>
          <button
            onClick={() => router.push('/')}
            className="flex items-center space-x-2 bg-gray-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-700 transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Scan Another Website</span>
          </button>
        </motion.div>
      </div>
    </div>
  );
}
