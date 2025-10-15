'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Globe, Shield, Zap, X, Plus, Upload } from 'lucide-react'

interface PolicyConfig {
  blockTraining: boolean
  allowRetrievalOnly: boolean
  requireSignedReceipts: boolean
  enableRenderFallback: boolean
  enableEmbeddings: boolean
  rateLimit: {
    perMinute: number
    perDay: number
  }
  allowlist: string[]
  blocklist: string[]
  userAgentPatterns: string[]
}

export default function PolicyPage() {
  const [config, setConfig] = useState<PolicyConfig>({
    blockTraining: true,
    allowRetrievalOnly: false,
    requireSignedReceipts: true,
    enableRenderFallback: true,
    enableEmbeddings: false,
    rateLimit: {
      perMinute: 100,
      perDay: 10000,
    },
    allowlist: ['googlebot', 'bingbot'],
    blocklist: ['scraperbot', 'malicious-agent'],
    userAgentPatterns: ['*bot*', '*crawler*', '*spider*'],
  })

  const [newClient, setNewClient] = useState('')
  const [newPattern, setNewPattern] = useState('')

  const addToList = (list: 'allowlist' | 'blocklist', value: string) => {
    if (value.trim()) {
      setConfig({
        ...config,
        [list]: [...config[list], value.trim()],
      })
      setNewClient('')
    }
  }

  const removeFromList = (list: 'allowlist' | 'blocklist', index: number) => {
    setConfig({
      ...config,
      [list]: config[list].filter((_, i) => i !== index),
    })
  }

  const addPattern = (value: string) => {
    if (value.trim()) {
      setConfig({
        ...config,
        userAgentPatterns: [...config.userAgentPatterns, value.trim()],
      })
      setNewPattern('')
    }
  }

  const removePattern = (index: number) => {
    setConfig({
      ...config,
      userAgentPatterns: config.userAgentPatterns.filter((_, i) => i !== index),
    })
  }

  const policyJSON = {
    'iaindex-policy': {
      version: '1.1',
      rules: [
        {
          allow: config.allowRetrievalOnly ? ['retrieval'] : ['retrieval', 'training'],
          block: config.blockTraining ? ['training'] : [],
          require: config.requireSignedReceipts ? ['signed-receipts'] : [],
        },
      ],
      features: {
        'render-fallback': config.enableRenderFallback,
        embeddings: config.enableEmbeddings,
      },
      'rate-limits': {
        'requests-per-minute': config.rateLimit.perMinute,
        'requests-per-day': config.rateLimit.perDay,
      },
      clients: {
        allow: config.allowlist,
        block: config.blocklist,
        patterns: config.userAgentPatterns,
      },
    },
  }

  const handlePublish = async () => {
    // In a real implementation, this would publish to /.well-known/iaindex-policy.json
    console.log('Publishing policy:', policyJSON)
    alert('Policy published to /.well-known/iaindex-policy.json')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Policy Configuration</h1>
        <p className="text-muted-foreground">
          Configure AI access policies and publish to your domain
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Policy Controls */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Access Controls
              </CardTitle>
              <CardDescription>Configure AI model access permissions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="block-training">Block Model Training</Label>
                  <p className="text-sm text-muted-foreground">
                    Prevent AI models from training on content
                  </p>
                </div>
                <Switch
                  id="block-training"
                  checked={config.blockTraining}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, blockTraining: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="retrieval-only">Allow Retrieval Only</Label>
                  <p className="text-sm text-muted-foreground">
                    Permit retrieval but not training
                  </p>
                </div>
                <Switch
                  id="retrieval-only"
                  checked={config.allowRetrievalOnly}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, allowRetrievalOnly: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="signed-receipts">Require Signed Receipts</Label>
                  <p className="text-sm text-muted-foreground">
                    Mandate cryptographic receipts for access
                  </p>
                </div>
                <Switch
                  id="signed-receipts"
                  checked={config.requireSignedReceipts}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, requireSignedReceipts: checked })
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Features
              </CardTitle>
              <CardDescription>Enable optional capabilities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="render-fallback">Enable Render Fallback</Label>
                  <p className="text-sm text-muted-foreground">
                    Provide alternative rendering for blocked content
                  </p>
                </div>
                <Switch
                  id="render-fallback"
                  checked={config.enableRenderFallback}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, enableRenderFallback: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="embeddings">Enable Embeddings</Label>
                  <p className="text-sm text-muted-foreground">
                    Allow semantic embedding generation
                  </p>
                </div>
                <Switch
                  id="embeddings"
                  checked={config.enableEmbeddings}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, enableEmbeddings: checked })
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Rate Limits</CardTitle>
              <CardDescription>Control request frequency</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Requests per Minute</Label>
                  <span className="text-sm font-bold">{config.rateLimit.perMinute}</span>
                </div>
                <Slider
                  value={[config.rateLimit.perMinute]}
                  onValueChange={([value]) =>
                    setConfig({
                      ...config,
                      rateLimit: { ...config.rateLimit, perMinute: value },
                    })
                  }
                  min={10}
                  max={1000}
                  step={10}
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Requests per Day</Label>
                  <span className="text-sm font-bold">{config.rateLimit.perDay}</span>
                </div>
                <Slider
                  value={[config.rateLimit.perDay]}
                  onValueChange={([value]) =>
                    setConfig({
                      ...config,
                      rateLimit: { ...config.rateLimit, perDay: value },
                    })
                  }
                  min={100}
                  max={100000}
                  step={1000}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Client Management</CardTitle>
              <CardDescription>Manage allowed and blocked clients</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Allowlist</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add client to allowlist..."
                    value={newClient}
                    onChange={(e) => setNewClient(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') addToList('allowlist', newClient)
                    }}
                  />
                  <Button
                    size="icon"
                    variant="outline"
                    onClick={() => addToList('allowlist', newClient)}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {config.allowlist.map((client, index) => (
                    <Badge key={index} variant="default" className="gap-1">
                      {client}
                      <button
                        onClick={() => removeFromList('allowlist', index)}
                        className="ml-1 hover:text-destructive"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>Blocklist</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add client to blocklist..."
                    value={newClient}
                    onChange={(e) => setNewClient(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') addToList('blocklist', newClient)
                    }}
                  />
                  <Button
                    size="icon"
                    variant="outline"
                    onClick={() => addToList('blocklist', newClient)}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {config.blocklist.map((client, index) => (
                    <Badge key={index} variant="destructive" className="gap-1">
                      {client}
                      <button
                        onClick={() => removeFromList('blocklist', index)}
                        className="ml-1 hover:text-destructive-foreground"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>User-Agent Patterns</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add pattern (e.g., *bot*)..."
                    value={newPattern}
                    onChange={(e) => setNewPattern(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') addPattern(newPattern)
                    }}
                  />
                  <Button
                    size="icon"
                    variant="outline"
                    onClick={() => addPattern(newPattern)}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {config.userAgentPatterns.map((pattern, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {pattern}
                      <button
                        onClick={() => removePattern(index)}
                        className="ml-1 hover:text-destructive"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Policy Preview */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Policy Preview
              </CardTitle>
              <CardDescription>
                Real-time JSON policy configuration
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                readOnly
                value={JSON.stringify(policyJSON, null, 2)}
                className="font-mono text-xs min-h-[600px]"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Publish Policy</CardTitle>
              <CardDescription>
                Deploy your policy to /.well-known/iaindex-policy.json
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border-2 border-dashed bg-muted p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Globe className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Publishing Location</p>
                    <p className="text-xs text-muted-foreground">
                      https://yourdomain.com/.well-known/iaindex-policy.json
                    </p>
                  </div>
                </div>
              </div>

              <Button onClick={handlePublish} className="w-full" size="lg">
                <Upload className="mr-2 h-4 w-4" />
                Publish to /.well-known/
              </Button>

              <p className="text-xs text-muted-foreground text-center">
                This will update your public policy and may take a few minutes to propagate
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
