'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { websitesAPI } from '@/lib/api';
import { formatDate, getScoreColor, getStatusColor } from '@/lib/utils';
import {
  Plus,
  Search,
  Globe,
  ExternalLink,
  TrendingUp,
  Loader2,
  Check,
  X
} from 'lucide-react';
import Link from 'next/link';
import type { Website } from '@/types';

function AddWebsiteModal({ open, onClose, onSuccess }: any) {
  const [domain, setDomain] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [industry, setIndustry] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await websitesAPI.create({
        domain,
        name,
        description,
        industry
      });

      if (response.data) {
        onSuccess();
        onClose();
        setDomain('');
        setName('');
        setDescription('');
        setIndustry('');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to add website');
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Add New Website</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-danger bg-danger/10 border border-danger/20 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="domain">Domain *</Label>
              <Input
                id="domain"
                placeholder="example.com"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Website Name *</Label>
              <Input
                id="name"
                placeholder="My Awesome Website"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Brief description of your website"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">Industry</Label>
              <Input
                id="industry"
                placeholder="e.g., Technology, Healthcare"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" disabled={loading} className="flex-1">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  'Add Website'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function WebsitesPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['websites'],
    queryFn: async () => {
      const response = await websitesAPI.list();
      return response.data?.data || [];
    },
  });

  const websites = (data as Website[]) || [];
  const filteredWebsites = websites.filter(
    (w) =>
      w.domain.toLowerCase().includes(search.toLowerCase()) ||
      w.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Websites</h1>
          <p className="text-gray-600 mt-1">
            Manage and monitor your websites&apos; AI visibility
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus size={18} className="mr-2" />
          Add Website
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg max-w-md">
        <Search size={18} className="text-gray-400" />
        <input
          type="text"
          placeholder="Search websites..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-transparent border-none outline-none text-sm w-full"
        />
      </div>

      {/* Websites grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="space-y-3 animate-pulse">
                  <div className="h-6 bg-gray-200 rounded w-3/4" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                  <div className="h-16 bg-gray-200 rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredWebsites.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Globe size={48} className="mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {search ? 'No websites found' : 'No websites yet'}
            </h3>
            <p className="text-gray-600 mb-6">
              {search
                ? 'Try adjusting your search terms'
                : 'Add your first website to start tracking AI visibility'}
            </p>
            {!search && (
              <Button onClick={() => setShowAddModal(true)}>
                <Plus size={18} className="mr-2" />
                Add Your First Website
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWebsites.map((website) => (
            <Card
              key={website.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => router.push(`/websites/${website.id}`)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
                      {website.name}
                      {website.hasSchema && (
                        <Check size={16} className="text-success" />
                      )}
                    </h3>
                    <p className="text-sm text-gray-600 flex items-center gap-1">
                      <Globe size={14} />
                      {website.domain}
                    </p>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(website.status)}`}>
                    {website.status}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Visibility Score</span>
                    <span className={`text-2xl font-bold ${getScoreColor(website.visibilityScore)}`}>
                      {website.visibilityScore}%
                    </span>
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        website.visibilityScore >= 80
                          ? 'bg-success'
                          : website.visibilityScore >= 60
                          ? 'bg-warning'
                          : 'bg-danger'
                      }`}
                      style={{ width: `${website.visibilityScore}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Last scan: {formatDate(website.lastScanDate)}</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100 flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/websites/${website.id}/schema`);
                    }}
                  >
                    Schema
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/websites/${website.id}/visibility`);
                    }}
                  >
                    Visibility
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add website modal */}
      <AddWebsiteModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={refetch}
      />
    </div>
  );
}
