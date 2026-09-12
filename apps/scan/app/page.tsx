'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ScanForm from '@/components/ScanForm';

export default function HomePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleScan = async (url: string) => {
    setIsSubmitting(true);
    // Encode URL for use in path
    const encodedUrl = encodeURIComponent(url);
    router.push(`/scan/${encodedUrl}`);
  };

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
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
              href="https://app.iaindex.org"
              className="text-sm text-gray-600 hover:text-gray-900 transition"
            >
              Sign In
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <motion.div
          className="text-center max-w-4xl mx-auto"
          initial="initial"
          animate="animate"
          variants={staggerChildren}
        >
          <motion.h1
            className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6"
            variants={fadeIn}
          >
            Is Your Website Visible in{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              ChatGPT?
            </span>
          </motion.h1>

          <motion.p
            className="text-xl sm:text-2xl text-gray-600 mb-8"
            variants={fadeIn}
          >
            63% of websites are invisible to AI search engines.
            <br />
            Check your visibility score for free in 60 seconds.
          </motion.p>

          <motion.div variants={fadeIn}>
            <ScanForm onSubmit={handleScan} isLoading={isSubmitting} />
          </motion.div>

          <motion.div
            className="mt-6 flex items-center justify-center space-x-6 text-sm text-gray-500"
            variants={fadeIn}
          >
            <span className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              No credit card
            </span>
            <span className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              100% free
            </span>
            <span className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              10,000+ websites scanned
            </span>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          className="grid md:grid-cols-3 gap-8"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={staggerChildren}
        >
          <motion.div
            className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
            variants={fadeIn}
          >
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Multi-Platform Visibility</h3>
            <p className="text-gray-600">
              Check ChatGPT, Perplexity, Claude visibility across all major AI search engines
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
            variants={fadeIn}
          >
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">AI-Optimized Recommendations</h3>
            <p className="text-gray-600">
              Get AI-optimized schema recommendations to improve your visibility score
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
            variants={fadeIn}
          >
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Competitive Benchmarking</h3>
            <p className="text-gray-600">
              See where you rank vs. competitors in AI search visibility
            </p>
          </motion.div>
        </motion.div>
      </section>

      {/* Social Proof */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p className="text-2xl font-semibold text-gray-900 mb-4">
            Join 10,000+ businesses optimizing for AI search
          </p>
          <div className="flex justify-center items-center space-x-2">
            <div className="flex -space-x-2">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 border-2 border-white"
                />
              ))}
            </div>
            <span className="text-gray-600 ml-4">and counting...</span>
          </div>
        </motion.div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
        <div className="space-y-6">
          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h3 className="text-lg font-semibold mb-2">What is AI visibility?</h3>
            <p className="text-gray-600">
              AI visibility measures how likely your website is to be referenced by AI search engines like ChatGPT, Perplexity, and Claude when answering relevant queries.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            <h3 className="text-lg font-semibold mb-2">Why is this important?</h3>
            <p className="text-gray-600">
              Over 50% of online searches are now happening through AI search engines. If your website is not optimized for AI, you're missing out on a huge source of traffic.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <h3 className="text-lg font-semibold mb-2">How does the scan work?</h3>
            <p className="text-gray-600">
              Our AI crawler analyzes your website's structure, schema markup, and content to determine how visible you are to AI search engines. We then provide specific recommendations to improve your score.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            <h3 className="text-lg font-semibold mb-2">Is it really free?</h3>
            <p className="text-gray-600">
              Yes! The basic scan is completely free with no credit card required. You'll get your visibility score and top recommendations instantly.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg"></div>
                <span className="text-lg font-bold">IAIndex</span>
              </div>
              <p className="text-sm text-gray-600">
                Making the web visible to AI search engines
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">Features</a></li>
                <li><a href="#" className="hover:text-gray-900">Pricing</a></li>
                <li><a href="#" className="hover:text-gray-900">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">Documentation</a></li>
                <li><a href="#" className="hover:text-gray-900">Blog</a></li>
                <li><a href="#" className="hover:text-gray-900">Support</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">About</a></li>
                <li><a href="#" className="hover:text-gray-900">Privacy</a></li>
                <li><a href="#" className="hover:text-gray-900">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-sm text-gray-600">
            &copy; 2024 IAIndex. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
