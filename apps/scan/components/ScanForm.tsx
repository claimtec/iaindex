'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

interface ScanFormProps {
  onSubmit: (url: string) => void;
  isLoading?: boolean;
}

export default function ScanForm({ onSubmit, isLoading = false }: ScanFormProps) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const validateUrl = (input: string): boolean => {
    // Add protocol if missing
    let urlToValidate = input.trim();
    if (!urlToValidate.startsWith('http://') && !urlToValidate.startsWith('https://')) {
      urlToValidate = 'https://' + urlToValidate;
    }

    try {
      new URL(urlToValidate);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!url.trim()) {
      setError('Please enter a website URL');
      return;
    }

    // Add protocol if missing
    let formattedUrl = url.trim();
    if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
      formattedUrl = 'https://' + formattedUrl;
    }

    if (!validateUrl(formattedUrl)) {
      setError('Please enter a valid URL (e.g., example.com or https://example.com)');
      return;
    }

    onSubmit(formattedUrl);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              setError('');
            }}
            placeholder="Enter your website URL (e.g., example.com)"
            className={`w-full px-6 py-4 text-lg rounded-xl border-2 transition-all focus:outline-none focus:ring-4 ${
              error
                ? 'border-red-500 focus:ring-red-200'
                : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200'
            }`}
            disabled={isLoading}
          />
          {error && (
            <motion.p
              className="mt-2 text-sm text-red-600 flex items-center"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </motion.p>
          )}
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none whitespace-nowrap"
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Scanning...
            </span>
          ) : (
            'Scan Now'
          )}
        </button>
      </div>
    </form>
  );
}
