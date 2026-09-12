'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { VisibilityChart } from '@/components/charts/VisibilityChart';
import { analyticsAPI, websitesAPI } from '@/lib/api';
import { formatDate, formatNumber, getScoreColor } from '@/lib/utils';
import {
  Globe,
  TrendingUp,
  Activity,
  AlertCircle,
  Plus,
  ExternalLink,
  Loader2
} from 'lucide-react';
import Link from 'next/link';
import type { DashboardStats, VisibilityHistory, Activity as ActivityType } from '@/types';

function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  loading
}: {
  title: string;
  value: string | number;
  icon: any;
  trend?: string;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            {loading ? (
              <div className="h-8 w-24 bg-gray-200 animate-pulse rounded" />
            ) : (
              <p className="text-3xl font-bold text-gray-900">{value}</p>
            )}
            {trend && (
              <p className="text-xs text-success flex items-center gap-1">
                <TrendingUp size={14} />
                {trend}
              </p>
            )}
          </div>
          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
            <Icon className="text-primary" size={24} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  // Fetch dashboard stats
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await analyticsAPI.getDashboardStats();
      return response.data.stats;
    },
  });

  // Fetch visibility trend
  const { data: trendData, isLoading: trendLoading } = useQuery({
    queryKey: ['visibility-trend'],
    queryFn: async () => {
      const response = await analyticsAPI.getVisibilityTrend(30);
      return response.data.trend || [];
    },
  });

  // Fetch recent activity
  const { data: activityData, isLoading: activityLoading } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: async () => {
      const response = await analyticsAPI.getRecentActivity({ limit: 5 });
      return response.data.activities || [];
    },
  });

  const stats = statsData as DashboardStats | undefined;

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here&apos;s your AI visibility overview.
          </p>
        </div>
        <Link href="/websites">
          <Button>
            <Plus size={18} className="mr-2" />
            Add Website
          </Button>
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Websites"
          value={stats?.totalWebsites || 0}
          icon={Globe}
          loading={statsLoading}
        />
        <StatCard
          title="Avg Visibility Score"
          value={stats?.averageVisibilityScore ? `${stats.averageVisibilityScore}%` : '0%'}
          icon={TrendingUp}
          trend="+12% from last month"
          loading={statsLoading}
        />
        <StatCard
          title="Active Scans"
          value={stats?.activeScansThisMonth || 0}
          icon={Activity}
          loading={statsLoading}
        />
        <StatCard
          title="Recommendations"
          value={stats?.recommendationsPending || 0}
          icon={AlertCircle}
          loading={statsLoading}
        />
      </div>

      {/* Charts and activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visibility trend chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Visibility Trend</CardTitle>
            <CardDescription>Your AI visibility over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            {trendLoading ? (
              <div className="h-80 flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : trendData && trendData.length > 0 ? (
              <div className="h-80">
                <VisibilityChart data={trendData as VisibilityHistory[]} />
              </div>
            ) : (
              <div className="h-80 flex flex-col items-center justify-center text-gray-500">
                <Activity size={48} className="mb-4 opacity-20" />
                <p>No visibility data yet</p>
                <p className="text-sm">Add a website to start tracking</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates from your websites</CardDescription>
          </CardHeader>
          <CardContent>
            {activityLoading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <div className="h-4 bg-gray-200 animate-pulse rounded w-3/4" />
                    <div className="h-3 bg-gray-200 animate-pulse rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : activityData && activityData.length > 0 ? (
              <div className="space-y-4">
                {(activityData as ActivityType[]).map((activity) => (
                  <div key={activity.id} className="pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                    <p className="text-sm text-gray-900 font-medium">
                      {activity.message}
                    </p>
                    {activity.websiteName && (
                      <p className="text-xs text-gray-600 mt-1">
                        {activity.websiteName}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(activity.timestamp)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <Activity size={32} className="mb-2 opacity-20" />
                <p className="text-sm">No recent activity</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to manage your AI visibility</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/websites" className="block">
              <div className="p-6 border border-gray-200 rounded-lg hover:border-primary hover:shadow-md transition-all cursor-pointer">
                <Plus className="text-primary mb-3" size={24} />
                <h3 className="font-semibold text-gray-900 mb-1">Add Website</h3>
                <p className="text-sm text-gray-600">
                  Register a new website to track its AI visibility
                </p>
              </div>
            </Link>

            <div className="p-6 border border-gray-200 rounded-lg hover:border-primary hover:shadow-md transition-all cursor-pointer">
              <Activity className="text-primary mb-3" size={24} />
              <h3 className="font-semibold text-gray-900 mb-1">Run Visibility Check</h3>
              <p className="text-sm text-gray-600">
                Check how your websites appear in AI responses
              </p>
            </div>

            <div className="p-6 border border-gray-200 rounded-lg hover:border-primary hover:shadow-md transition-all cursor-pointer">
              <ExternalLink className="text-primary mb-3" size={24} />
              <h3 className="font-semibold text-gray-900 mb-1">Generate Schema</h3>
              <p className="text-sm text-gray-600">
                Create optimized schema markup for better visibility
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
