'use client'

import { useState } from 'react'
import { CheckCircle2, XCircle, Shield, QrCode, Copy, Check } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'

interface VerificationStatus {
  c2pa: boolean
  merkle: boolean
  domain: boolean
  timestamp: boolean
}

interface VerificationBadgeProps {
  status: VerificationStatus
  contentId?: string
  variant?: 'compact' | 'detailed' | 'qr'
  showEmbed?: boolean
}

export function VerificationBadge({
  status,
  contentId = 'example-id',
  variant = 'detailed',
  showEmbed = false,
}: VerificationBadgeProps) {
  const [copied, setCopied] = useState(false)

  const allVerified = Object.values(status).every((v) => v)
  const verificationCount = Object.values(status).filter((v) => v).length
  const totalChecks = Object.keys(status).length

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const embedCode = `<div class="iaindex-badge" data-content-id="${contentId}">
  <a href="https://iaindex.com/verify/${contentId}" target="_blank" rel="noopener">
    <img src="https://iaindex.com/api/badge/${contentId}" alt="Verified by IAIndex" />
  </a>
</div>
<script src="https://iaindex.com/badge.js" async></script>`

  if (variant === 'compact') {
    return (
      <div className="inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1.5">
        {allVerified ? (
          <CheckCircle2 className="h-4 w-4 text-green-600" />
        ) : (
          <Shield className="h-4 w-4 text-yellow-600" />
        )}
        <span className="text-sm font-medium">
          {allVerified ? 'Fully Verified' : `${verificationCount}/${totalChecks} Verified`}
        </span>
      </div>
    )
  }

  if (variant === 'qr') {
    return (
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <div className="mx-auto mb-2 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <QrCode className="h-8 w-8 text-primary" />
          </div>
          <CardTitle>Scan to Verify</CardTitle>
          <CardDescription>Verify content authenticity instantly</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="aspect-square w-full rounded-lg border-2 border-dashed bg-muted flex items-center justify-center">
            <div className="text-center p-4">
              <QrCode className="h-24 w-24 mx-auto mb-2 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">QR Code Placeholder</p>
              <p className="text-xs text-muted-foreground mt-1">
                iaindex.com/verify/{contentId}
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(status).map(([key, value]) => (
              <div key={key} className="flex items-center gap-1">
                {value ? (
                  <CheckCircle2 className="h-3 w-3 text-green-600" />
                ) : (
                  <XCircle className="h-3 w-3 text-red-600" />
                )}
                <span className="capitalize">{key}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Content Verification
            </CardTitle>
            <CardDescription>Multi-layer authenticity verification</CardDescription>
          </div>
          <Badge
            variant={allVerified ? 'default' : 'secondary'}
            className={cn(
              'font-bold',
              allVerified && 'bg-green-600 hover:bg-green-700'
            )}
          >
            {allVerified ? 'Fully Verified' : `${verificationCount}/${totalChecks} Checks`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-3">
          <VerificationItem
            icon={Shield}
            label="C2PA Content Credentials"
            status={status.c2pa}
            description="Cryptographic proof of content origin"
          />
          <VerificationItem
            icon={Shield}
            label="Merkle Tree Attestation"
            status={status.merkle}
            description="Immutable timestamp recorded"
          />
          <VerificationItem
            icon={Shield}
            label="Domain Verification"
            status={status.domain}
            description="Publisher identity confirmed"
          />
          <VerificationItem
            icon={Shield}
            label="External Timestamp"
            status={status.timestamp}
            description="Third-party timestamp authority"
          />
        </div>

        {showEmbed && (
          <Tabs defaultValue="preview" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="preview">Preview</TabsTrigger>
              <TabsTrigger value="embed">Embed Code</TabsTrigger>
            </TabsList>
            <TabsContent value="preview" className="space-y-2">
              <div className="rounded-lg border bg-muted p-4 flex items-center justify-center">
                <VerificationBadge status={status} variant="compact" />
              </div>
            </TabsContent>
            <TabsContent value="embed" className="space-y-2">
              <div className="relative">
                <Textarea
                  readOnly
                  value={embedCode}
                  className="font-mono text-xs min-h-[120px]"
                />
                <Button
                  size="sm"
                  variant="ghost"
                  className="absolute top-2 right-2"
                  onClick={() => copyToClipboard(embedCode)}
                >
                  {copied ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Copy this code to embed the verification badge on your website
              </p>
            </TabsContent>
          </Tabs>
        )}

        <div className="flex gap-2">
          <Button variant="outline" className="flex-1">
            <QrCode className="mr-2 h-4 w-4" />
            Generate QR
          </Button>
          <Button variant="outline" className="flex-1">
            <Copy className="mr-2 h-4 w-4" />
            Copy Link
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

interface VerificationItemProps {
  icon: any
  label: string
  status: boolean
  description: string
}

function VerificationItem({ icon: Icon, label, status, description }: VerificationItemProps) {
  return (
    <div className="flex items-start gap-3 rounded-lg border p-3">
      <div
        className={cn(
          'flex h-8 w-8 items-center justify-center rounded-full',
          status ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
        )}
      >
        {status ? (
          <CheckCircle2 className="h-4 w-4" />
        ) : (
          <XCircle className="h-4 w-4" />
        )}
      </div>
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium">{label}</p>
          <Badge variant={status ? 'default' : 'secondary'} className="text-xs">
            {status ? 'Active' : 'Inactive'}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}
