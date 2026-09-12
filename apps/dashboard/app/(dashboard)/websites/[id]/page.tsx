'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { VisibilityGauge } from '@/components/charts/VisibilityGauge';
import { websitesAPI, visibilityAPI } from '@/lib/api';
import { formatDate, formatDateTime } from '@/lib/utils';
import {
  Globe,
  ExternalLink,
  FileCode,
  Activity,
  ArrowLeft,
  Loader2,
  Check,
  X
} from 'lucide-react';
import Link from 'next/link';

export default function WebsiteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const websiteId = params.id as string;

  const { data: website, isLoading } = useQuery({
    queryKey: ['website', websiteId],
    queryFn: async () => {
      const response = await websitesAPI.get(websiteId);
      return response.data.website;
    },
  });

  const { data: historyData } = useQuery({
    queryKey: ['visibility-history', websiteId],
    queryFn: async () => {
      const response = await visibilityAPI.getHistory(websiteId, { days: 7 });
      return response.data.history || [];
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!website) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Website not found</h2>
        <Link href="/websites">
          <Button className="mt-4">Back to Websites</Button>
        </Link>
      </div>
    );
  }

  const platforms = [
    { name: 'ChatGPT', score: 85, color: 'text-success' },
    { name: 'Perplexity', score: 72, color: 'text-primary' },
    { name: 'Claude', score: 68, color: 'text-secondary' },
    { name: 'Gemini', score: 75, color: 'text-warning' },
  ];

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft size={20} />
        <span>Back to Websites</span>
      </button>

      {/* Website header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{website.name}</h1>
          <div className="flex items-center gap-4 text-gray-600">
            <a
              href={`https://${website.domain}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 hover:text-primary"
            >
              <Globe size={16} />
              {website.domain}
              <ExternalLink size={14} />
            </a>
            {website.industry && (
              <span className="text-sm">
                Industry: {website.industry}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Link href={`/websites/${websiteId}/schema`}>
            <Button variant="outline">
              <FileCode size={18} className="mr-2" />
              Manage Schema
            </Button>
          </Link>
          <Link href={`/websites/${websiteId}/visibility`}>
            <Button>
              <Activity size={18} className="mr-2" />
              Check Visibility
            </Button>
          </Link>
        </div>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visibility score */}
        <Card>
          <CardHeader>
            <CardTitle>Visibility Score</CardTitle>
            <CardDescription>Current overall AI visibility</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <VisibilityGauge score={website.visibilityScore} size="lg" showLabel={false} />
            <div className="mt-6 w-full space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Last scan</span>
                <span className="font-medium">{formatDate(website.lastScanDate)}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Status</span>
                <span className={`font-medium capitalize ${
                  website.status === 'active' ? 'text-success' :
                  website.status === 'pending' ? 'text-warning' :
                  'text-danger'
                }`}>
                  {website.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Schema</span>
                <span className="flex items-center gap-1">
                  {website.hasSchema ? (
                    <>
                      <Check size={16} className="text-success" />
                      <span className="text-success font-medium">Installed</span>
                    </>
                  ) : (
                    <>
                      <X size={16} className="text-danger" />
                      <span className="text-danger font-medium">Not installed</span>
                    </>
                  )}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Platform breakdown */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Platform Breakdown</CardTitle>
            <CardDescription>Visibility across different AI platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {platforms.map((platform) => (
                <div key={platform.name}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{platform.name}</span>
                    <span className={`font-bold ${platform.color}`}>{platform.score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        platform.score >= 80 ? 'bg-success' :
                        platform.score >= 60 ? 'bg-warning' :
                        'bg-danger'
                      }`}
                      style={{ width: `${platform.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Add more descriptive content about your products and services</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Implement schema markup for better structured data</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Increase presence in authoritative industry sources</span>
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent scans */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Scans</CardTitle>
          <CardDescription>History of visibility checks for this website</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {historyData && Array.isArray(historyData) && historyData.length > 0 ? (
              historyData.slice(0, 5).map((item: any, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      Visibility Check - Score: {item.score}%
                    </p>
                    <p className="text-sm text-gray-600">{formatDateTime(item.date)}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${
                      item.score >= 80 ? 'text-success' :
                      item.score >= 60 ? 'text-warning' :
                      'text-danger'
                    }`}>
                      {item.score >= 80 ? 'Excellent' :
                       item.score >= 60 ? 'Good' :
                       'Needs Improvement'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Activity size={32} className="mx-auto mb-2 opacity-20" />
                <p className="text-sm">No scans yet</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href={`/websites/${websiteId}/schema`}>
          <div className="p-6 border border-gray-200 rounded-lg hover:border-primary hover:shadow-md transition-all cursor-pointer h-full">
            <FileCode className="text-primary mb-3" size={24} />
            <h3 className="font-semibold text-gray-900 mb-1">Generate Schema</h3>
            <p className="text-sm text-gray-600">
              Create optimized schema markup for this website
            </p>
          </div>
        </Link>

        <Link href={`/websites/${websiteId}/visibility`}>
          <div className="p-6 border border-gray-200 rounded-lg hover:border-primary hover:shadow-md transition-all cursor-pointer h-full">
            <Activity className="text-primary mb-3" size={24} />
            <h3 className="font-semibold text-gray-900 mb-1">Check Visibility</h3>
            <p className="text-sm text-gray-600">
              Run a new visibility check across all platforms
            </p>
          </div>
        </Link>

        <div className="p-6 border border-gray-200 rounded-lg hover:border-primary hover:shadow-md transition-all cursor-pointer">
          <ExternalLink className="text-primary mb-3" size={24} />
          <h3 className="font-semibold text-gray-900 mb-1">View Full Report</h3>
          <p className="text-sm text-gray-600">
            Download comprehensive AI visibility report
          </p>
        </div>
      </div>
    </div>
  );
}
