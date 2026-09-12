'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { PLANS, PlanType } from '@/lib/stripe';
import { CheckIcon } from '@heroicons/react/24/outline';

export default function PricingPage() {
  const [isLoading, setIsLoading] = useState<string | null>(null);
  const [email, setEmail] = useState('');

  const handleCheckout = async (plan: PlanType) => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    setIsLoading(plan);

    try {
      const response = await fetch('/api/create-checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plan, email }),
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to create checkout session. Please try again.');
      setIsLoading(null);
    }
  };

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
            <a href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg"></div>
              <span className="text-xl font-bold">IAIndex</span>
            </a>
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
          className="text-center max-w-4xl mx-auto mb-16"
          initial="initial"
          animate="animate"
          variants={staggerChildren}
        >
          <motion.h1
            className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6"
            variants={fadeIn}
          >
            Choose Your{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI Visibility Plan
            </span>
          </motion.h1>

          <motion.p
            className="text-xl text-gray-600 mb-8"
            variants={fadeIn}
          >
            Get discovered by AI search engines and stay ahead of the competition
          </motion.p>

          {/* Email Input */}
          <motion.div
            className="max-w-md mx-auto"
            variants={fadeIn}
          >
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </motion.div>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto"
          initial="initial"
          animate="animate"
          variants={staggerChildren}
        >
          {(Object.keys(PLANS) as PlanType[]).map((planKey) => {
            const plan = PLANS[planKey];
            const isPopular = 'popular' in plan && plan.popular;

            return (
              <motion.div
                key={planKey}
                className={`relative bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow ${
                  isPopular ? 'ring-2 ring-blue-600 transform scale-105' : ''
                }`}
                variants={fadeIn}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Name */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {plan.name}
                  </h3>

                  {/* Price */}
                  <div className="mb-6">
                    <span className="text-5xl font-bold text-gray-900">
                      ${plan.price}
                    </span>
                    <span className="text-gray-600">/month</span>
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleCheckout(planKey)}
                    disabled={isLoading !== null}
                    className={`w-full py-3 px-6 rounded-lg font-semibold transition-all ${
                      isPopular
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {isLoading === planKey ? 'Loading...' : 'Get Started'}
                  </button>

                  {/* Features */}
                  <ul className="mt-8 space-y-4">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <CheckIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </section>

      {/* Feature Comparison Table */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Compare Plans
        </h2>
        <div className="overflow-x-auto bg-white rounded-2xl shadow-lg">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                  Feature
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">
                  Starter
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">
                  Professional
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">
                  Agency
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Websites</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">1</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">5</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">50</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Check Frequency</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Weekly</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Daily</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Real-time</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Email Reports</td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">API Access</td>
                <td className="px-6 py-4 text-center text-sm text-gray-400">-</td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">White-label Reports</td>
                <td className="px-6 py-4 text-center text-sm text-gray-400">-</td>
                <td className="px-6 py-4 text-center text-sm text-gray-400">-</td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Client Portals</td>
                <td className="px-6 py-4 text-center text-sm text-gray-400">-</td>
                <td className="px-6 py-4 text-center text-sm text-gray-400">-</td>
                <td className="px-6 py-4 text-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mx-auto" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Frequently Asked Questions
        </h2>
        <div className="space-y-6">
          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h3 className="text-lg font-semibold mb-2">
              Can I upgrade or downgrade my plan?
            </h3>
            <p className="text-gray-600">
              Yes, you can change your plan at any time. Upgrades take effect
              immediately, while downgrades will apply at the end of your current
              billing period.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            <h3 className="text-lg font-semibold mb-2">
              What payment methods do you accept?
            </h3>
            <p className="text-gray-600">
              We accept all major credit cards (Visa, Mastercard, American Express)
              through our secure payment processor, Stripe.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <h3 className="text-lg font-semibold mb-2">
              Is there a free trial?
            </h3>
            <p className="text-gray-600">
              We offer a free scan that gives you a visibility score and basic
              recommendations. Paid plans are required for ongoing monitoring and
              advanced features.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            <h3 className="text-lg font-semibold mb-2">
              Can I cancel anytime?
            </h3>
            <p className="text-gray-600">
              Yes, you can cancel your subscription at any time. You'll continue to
              have access until the end of your current billing period.
            </p>
          </motion.div>

          <motion.div
            className="bg-white rounded-xl p-6 shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
          >
            <h3 className="text-lg font-semibold mb-2">
              Do you offer refunds?
            </h3>
            <p className="text-gray-600">
              We offer a 14-day money-back guarantee. If you're not satisfied with
              our service, contact us within 14 days of your purchase for a full
              refund.
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
                <li>
                  <a href="/" className="hover:text-gray-900">
                    Features
                  </a>
                </li>
                <li>
                  <a href="/pricing" className="hover:text-gray-900">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-gray-900">
                    API
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <a href="#" className="hover:text-gray-900">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-gray-900">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-gray-900">
                    Support
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <a href="#" className="hover:text-gray-900">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-gray-900">
                    Privacy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-gray-900">
                    Terms
                  </a>
                </li>
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
