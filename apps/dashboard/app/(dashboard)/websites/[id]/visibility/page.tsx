'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { VisibilityChart } from '@/components/charts/VisibilityChart';
import { websitesAPI, visibilityAPI } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import {
  ArrowLeft,
  Download,
  Play,
  Loader2,
  Check,
  X,
  Calendar
} from 'lucide-react';
import type { VisibilityHistory, VisibilityCheck } from '@/types';

export default function VisibilityTrackingPage() {
  const params = useParams();
  const router = useRouter();
  const websiteId = params.id as string;
  const [queries, setQueries] = useState('');
  const [checking, setChecking] = useState(false);

  const { data: website } = useQuery({
    queryKey: ['website', websiteId],
    queryFn: async () => {
      const response = await websitesAPI.get(websiteId);
      return response.data.website;
    },
  });

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['visibility-history', websiteId],
    queryFn: async () => {
      const response = await visibilityAPI.getHistory(websiteId, { days: 30 });
      return response.data.history || [];
    },
  });

  const { data: checksData, refetch: refetchChecks } = useQuery({
    queryKey: ['visibility-checks', websiteId],
    queryFn: async () => {
      const response = await visibilityAPI.getChecks(websiteId, { page: 1, page_size: 20 });
      return response.data.checks || [];
    },
  });

  const handleRunCheck = async () => {
    if (!queries.trim()) return;

    setChecking(true);
    try {
      const queryList = queries.split('\n').filter(q => q.trim());
      await visibilityAPI.check(websiteId, queryList);
      refetchChecks();
      setQueries('');
    } catch (err) {
      console.error('Failed to run visibility check:', err);
    } finally {
      setChecking(false);
    }
  };

  const handleDownloadReport = () => {
    // Generate PDF report logic here
    alert('Report download functionality will be implemented with a PDF generation service');
  };

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft size={20} />
        <span>Back to Website</span>
      </button>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Visibility Tracking</h1>
          <p className="text-gray-600">
            Monitor AI visibility trends for {website?.name}
          </p>
        </div>
        <Button onClick={handleDownloadReport} variant="outline">
          <Download size={18} className="mr-2" />
          Download Report
        </Button>
      </div>

      {/* Run visibility check */}
      <Card>
        <CardHeader>
          <CardTitle>Run Visibility Check</CardTitle>
          <CardDescription>
            Enter queries to check how your website appears in AI responses
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <textarea
                placeholder="Enter queries (one per line)&#10;Example:&#10;best project management tools&#10;top CRM software for small business"
                value={queries}
                onChange={(e) => setQueries(e.target.value)}
                rows={5}
                className="w-full p-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              />
            </div>
            <Button onClick={handleRunCheck} disabled={checking || !queries.trim()}>
              {checking ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Checking...
                </>
              ) : (
                <>
                  <Play size={18} className="mr-2" />
                  Run Check
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Visibility trend chart */}
      <Card>
        <CardHeader>
          <CardTitle>Visibility Score Over Time</CardTitle>
          <CardDescription>Last 30 days of visibility tracking</CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="h-80 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : historyData && (historyData as VisibilityHistory[]).length > 0 ? (
            <div className="h-80">
              <VisibilityChart data={historyData as VisibilityHistory[]} />
            </div>
          ) : (
            <div className="h-80 flex flex-col items-center justify-center text-gray-500">
              <Calendar size={48} className="mb-4 opacity-20" />
              <p>No visibility data yet</p>
              <p className="text-sm">Run a check to start tracking</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Platform-specific chart */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Breakdown</CardTitle>
          <CardDescription>Visibility across different AI platforms</CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="h-80 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : historyData && (historyData as VisibilityHistory[]).length > 0 ? (
            <div className="h-80">
              <VisibilityChart data={historyData as VisibilityHistory[]} showPlatforms />
            </div>
          ) : (
            <div className="h-80 flex flex-col items-center justify-center text-gray-500">
              <Calendar size={48} className="mb-4 opacity-20" />
              <p>No platform data yet</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Mention history table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Checks</CardTitle>
          <CardDescription>History of visibility checks and mentions</CardDescription>
        </CardHeader>
        <CardContent>
          {checksData && (checksData as VisibilityCheck[]).length > 0 ? (
            <div className="space-y-3">
              {(checksData as VisibilityCheck[]).map((check) => (
                <div
                  key={check.id}
                  className="flex items-start justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {check.mentioned ? (
                        <Check size={16} className="text-success" />
                      ) : (
                        <X size={16} className="text-danger" />
                      )}
                      <span className={`text-sm font-medium ${
                        check.mentioned ? 'text-success' : 'text-danger'
                      }`}>
                        {check.mentioned ? 'Mentioned' : 'Not mentioned'}
                      </span>
                      <span className="text-xs text-gray-500">
                        on {check.platform}
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 font-medium mb-1">
                      &quot;{check.query}&quot;
                    </p>
                    {check.context && (
                      <p className="text-xs text-gray-600 line-clamp-2">
                        {check.context}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-2">
                      {formatDateTime(check.checkedAt)}
                      {check.position && ` • Position: #${check.position}`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Calendar size={32} className="mx-auto mb-2 opacity-20" />
              <p className="text-sm">No checks yet</p>
              <p className="text-xs mt-1">Run a visibility check to see results here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
