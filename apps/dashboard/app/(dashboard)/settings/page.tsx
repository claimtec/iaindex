'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authAPI, apiKeysAPI } from '@/lib/api';
import { useStore } from '@/lib/store';
import { formatDateTime } from '@/lib/utils';
import {
  User,
  Mail,
  Bell,
  Key,
  Trash2,
  Copy,
  Plus,
  Check,
  Loader2
} from 'lucide-react';

export default function SettingsPage() {
  const user = useStore((state) => state.user);
  const setUser = useStore((state) => state.setUser);

  // Profile settings
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [profileSaving, setProfileSaving] = useState(false);

  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [weeklyReports, setWeeklyReports] = useState(true);
  const [visibilityAlerts, setVisibilityAlerts] = useState(true);

  // API Keys
  const [newKeyName, setNewKeyName] = useState('');
  const [showNewKeyModal, setShowNewKeyModal] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const { data: apiKeys, refetch: refetchKeys } = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      const response = await apiKeysAPI.list();
      return response.data || [];
    },
  });

  const createKeyMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await apiKeysAPI.create(name);
      return response.data;
    },
    onSuccess: () => {
      refetchKeys();
      setShowNewKeyModal(false);
      setNewKeyName('');
    },
  });

  const revokeKeyMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiKeysAPI.revoke(id);
    },
    onSuccess: () => {
      refetchKeys();
    },
  });

  const handleProfileUpdate = async () => {
    setProfileSaving(true);
    try {
      const response = await authAPI.updateProfile({ name, email });
      if (response.data) {
        setUser(response.data);
      }
    } catch (err) {
      console.error('Failed to update profile:', err);
    } finally {
      setProfileSaving(false);
    }
  };

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Profile settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User size={20} />
            Profile Information
          </CardTitle>
          <CardDescription>
            Update your personal information and email address
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
          </div>
          <Button onClick={handleProfileUpdate} disabled={profileSaving}>
            {profileSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Notification settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell size={20} />
            Notification Preferences
          </CardTitle>
          <CardDescription>
            Choose how you want to receive updates
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Email Notifications</p>
              <p className="text-sm text-gray-600">
                Receive email updates about your websites
              </p>
            </div>
            <input
              type="checkbox"
              checked={emailNotifications}
              onChange={(e) => setEmailNotifications(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Weekly Reports</p>
              <p className="text-sm text-gray-600">
                Get weekly summaries of your visibility metrics
              </p>
            </div>
            <input
              type="checkbox"
              checked={weeklyReports}
              onChange={(e) => setWeeklyReports(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Visibility Alerts</p>
              <p className="text-sm text-gray-600">
                Alert me when visibility scores change significantly
              </p>
            </div>
            <input
              type="checkbox"
              checked={visibilityAlerts}
              onChange={(e) => setVisibilityAlerts(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
            />
          </div>

          <Button>Save Preferences</Button>
        </CardContent>
      </Card>

      {/* API Keys */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Key size={20} />
                API Keys
              </CardTitle>
              <CardDescription>
                Manage API keys for programmatic access
              </CardDescription>
            </div>
            <Button onClick={() => setShowNewKeyModal(true)} size="sm">
              <Plus size={16} className="mr-2" />
              Create Key
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {apiKeys && Array.isArray(apiKeys) && apiKeys.length > 0 ? (
            <div className="space-y-3">
              {apiKeys.map((key: any) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{key.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <code className="text-xs bg-gray-200 px-2 py-1 rounded">
                        {key.key.substring(0, 20)}...
                      </code>
                      <button
                        onClick={() => handleCopyKey(key.key)}
                        className="text-gray-600 hover:text-primary"
                      >
                        {copiedKey === key.key ? (
                          <Check size={14} className="text-success" />
                        ) : (
                          <Copy size={14} />
                        )}
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Created: {formatDateTime(key.createdAt)}
                      {key.lastUsed && ` • Last used: ${formatDateTime(key.lastUsed)}`}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => revokeKeyMutation.mutate(key.id)}
                    className="text-danger hover:text-danger"
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Key size={32} className="mx-auto mb-2 opacity-20" />
              <p className="text-sm">No API keys yet</p>
              <p className="text-xs mt-1">Create one to access the IAIndex API</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Danger zone */}
      <Card className="border-danger/20">
        <CardHeader>
          <CardTitle className="text-danger">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible actions for your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 border border-danger/20 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Delete Account</p>
              <p className="text-sm text-gray-600">
                Permanently delete your account and all associated data
              </p>
            </div>
            <Button variant="destructive">
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Create API Key Modal */}
      {showNewKeyModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Create API Key</CardTitle>
              <CardDescription>
                Give your API key a descriptive name
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="keyName">Key Name</Label>
                <Input
                  id="keyName"
                  placeholder="e.g., Production API Key"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                />
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowNewKeyModal(false);
                    setNewKeyName('');
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => createKeyMutation.mutate(newKeyName)}
                  disabled={!newKeyName.trim() || createKeyMutation.isPending}
                  className="flex-1"
                >
                  {createKeyMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Key'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
