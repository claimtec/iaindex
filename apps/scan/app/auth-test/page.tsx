'use client';

import { useState } from 'react';

export default function AuthTestPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('https://api.iaindex.org/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          company,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Registration failed');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="bg-white shadow-md rounded-lg p-8">
          <h1 className="text-2xl font-bold text-center mb-6">
            Auth Test - Register User
          </h1>

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                minLength={6}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company
              </label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Registering...' : 'Register'}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm font-medium">Error:</p>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800 text-sm font-medium mb-2">
                ✅ Registration Successful!
              </p>
              <div className="text-xs text-gray-700 mt-2">
                <p><strong>User ID:</strong> {result.user?.id}</p>
                <p><strong>Email:</strong> {result.user?.email}</p>
                <p><strong>Name:</strong> {result.user?.full_name}</p>
                <p><strong>Plan:</strong> {result.user?.plan}</p>
                <p className="mt-2 text-green-600">
                  <strong>Access Token:</strong> {result.access_token?.substring(0, 50)}...
                </p>
              </div>
            </div>
          )}

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h2 className="text-sm font-medium text-gray-700 mb-2">
              Test Configuration:
            </h2>
            <div className="text-xs text-gray-600 space-y-1">
              <p>
                <strong>Backend API:</strong> https://api.iaindex.org
              </p>
              <p>
                <strong>Supabase URL:</strong>{' '}
                {process.env.NEXT_PUBLIC_SUPABASE_URL || 'Not set'}
              </p>
              <p>
                <strong>Supabase Anon Key:</strong>{' '}
                {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
                  ? `${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY.substring(0, 20)}...`
                  : 'Not set'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
