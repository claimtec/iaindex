'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getSettings, updateSettings } from '@/lib/api'
import type { Settings } from '@/lib/api'
import { CheckCircle, XCircle, Copy, RefreshCw } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    const data = await getSettings()
    setSettings(data)
    setLoading(false)
  }

  const handleSave = async () => {
    if (!settings) return

    setSaving(true)
    setMessage(null)

    const success = await updateSettings(settings)

    if (success) {
      setMessage({ type: 'success', text: 'Settings saved successfully!' })
    } else {
      setMessage({ type: 'error', text: 'Failed to save settings' })
    }

    setSaving(false)
  }

  const handleVerifyDomain = async () => {
    // Domain verification logic would go here
    setMessage({ type: 'success', text: 'Domain verification initiated' })
  }

  const handleGenerateApiKey = () => {
    const newApiKey = `sk_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
    setSettings(prev => prev ? { ...prev, api_key: newApiKey } : null)
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setMessage({ type: 'success', text: 'Copied to clipboard!' })
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">Loading settings...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your domain, API keys, and webhook configuration
        </p>
      </div>

      {message && (
        <div
          className={`rounded-md p-4 ${
            message.type === 'success'
              ? 'bg-green-500/10 text-green-500'
              : 'bg-destructive/10 text-destructive'
          }`}
        >
          {message.text}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Domain Verification</CardTitle>
          <CardDescription>
            Verify your domain to enable receipt verification
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="domain">Domain</Label>
            <div className="flex gap-2">
              <Input
                id="domain"
                placeholder="example.com"
                value={settings?.domain || ''}
                onChange={(e) =>
                  setSettings(prev => prev ? { ...prev, domain: e.target.value } : null)
                }
              />
              <Button onClick={handleVerifyDomain} variant="outline">
                Verify
              </Button>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Label>Status:</Label>
            {settings?.domain_verified ? (
              <Badge className="bg-green-500">
                <CheckCircle className="mr-1 h-3 w-3" />
                Verified
              </Badge>
            ) : (
              <Badge variant="secondary">
                <XCircle className="mr-1 h-3 w-3" />
                Not Verified
              </Badge>
            )}
          </div>
          <div className="rounded-md bg-muted p-4 text-sm">
            <p className="font-medium">Verification Instructions:</p>
            <ol className="mt-2 list-inside list-decimal space-y-1 text-muted-foreground">
              <li>Add a TXT record to your domain's DNS settings</li>
              <li>Use the name: _iaindex-verification</li>
              <li>Use the value: {settings?.api_key?.substring(0, 32)}</li>
              <li>Wait for DNS propagation (up to 24 hours)</li>
              <li>Click the Verify button above</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>API Keys</CardTitle>
          <CardDescription>
            Manage your API keys for programmatic access
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api_key">API Key</Label>
            <div className="flex gap-2">
              <Input
                id="api_key"
                type="password"
                value={settings?.api_key || ''}
                readOnly
              />
              <Button
                onClick={() => handleCopy(settings?.api_key || '')}
                variant="outline"
                size="icon"
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button onClick={handleGenerateApiKey} variant="outline" size="icon">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Keep your API key secret. It provides full access to your account.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Webhook Configuration</CardTitle>
          <CardDescription>
            Receive real-time notifications for receipt events
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="webhook_url">Webhook URL</Label>
            <Input
              id="webhook_url"
              type="url"
              placeholder="https://your-domain.com/webhooks/receipts"
              value={settings?.webhook_url || ''}
              onChange={(e) =>
                setSettings(prev => prev ? { ...prev, webhook_url: e.target.value } : null)
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="webhook_secret">Webhook Secret</Label>
            <div className="flex gap-2">
              <Input
                id="webhook_secret"
                type="password"
                value={settings?.webhook_secret || ''}
                readOnly
              />
              <Button
                onClick={() => handleCopy(settings?.webhook_secret || '')}
                variant="outline"
                size="icon"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Use this secret to verify webhook signatures
            </p>
          </div>
          <div className="rounded-md bg-muted p-4 text-sm">
            <p className="font-medium">Webhook Events:</p>
            <ul className="mt-2 list-inside list-disc space-y-1 text-muted-foreground">
              <li>receipt.verified - Receipt verification completed</li>
              <li>receipt.failed - Receipt verification failed</li>
              <li>receipt.created - New receipt created</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  )
}
