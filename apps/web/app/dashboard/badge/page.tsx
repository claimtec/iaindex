'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { BadgeCheck, Copy } from 'lucide-react'

export default function BadgePage() {
  const [receiptId, setReceiptId] = useState('')
  const [style, setStyle] = useState('default')
  const [size, setSize] = useState('medium')
  const [copied, setCopied] = useState(false)

  const generateBadgeUrl = () => {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : ''
    return `${baseUrl}/api/badge/${receiptId}?style=${style}&size=${size}`
  }

  const generateHtmlCode = () => {
    const badgeUrl = generateBadgeUrl()
    const verifyUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/verify/${receiptId}`
    return `<a href="${verifyUrl}" target="_blank" rel="noopener noreferrer">
  <img src="${badgeUrl}" alt="Verified Receipt" />
</a>`
  }

  const generateMarkdownCode = () => {
    const badgeUrl = generateBadgeUrl()
    const verifyUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/verify/${receiptId}`
    return `[![Verified Receipt](${badgeUrl})](${verifyUrl})`
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getBadgePreview = () => {
    const sizeClasses = {
      small: 'h-6',
      medium: 'h-8',
      large: 'h-10',
    }

    const styleVariants = {
      default: 'bg-primary text-primary-foreground',
      success: 'bg-green-500 text-white',
      minimal: 'bg-transparent border border-primary text-primary',
    }

    return (
      <div className="flex items-center justify-center rounded-lg border bg-muted/50 p-8">
        <div
          className={`inline-flex items-center space-x-2 rounded-md px-3 py-1.5 ${
            styleVariants[style as keyof typeof styleVariants]
          } ${sizeClasses[size as keyof typeof sizeClasses]}`}
        >
          <BadgeCheck className="h-4 w-4" />
          <span className="text-sm font-medium">Verified Receipt</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Badge Generator</h1>
        <p className="text-muted-foreground">
          Generate verification badges for your receipts
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Badge Configuration</CardTitle>
              <CardDescription>Customize your verification badge</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="receipt_id">Receipt ID</Label>
                <Input
                  id="receipt_id"
                  placeholder="Enter receipt ID"
                  value={receiptId}
                  onChange={(e) => setReceiptId(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="style">Badge Style</Label>
                <Select
                  id="style"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                >
                  <option value="default">Default</option>
                  <option value="success">Success</option>
                  <option value="minimal">Minimal</option>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="size">Badge Size</Label>
                <Select
                  id="size"
                  value={size}
                  onChange={(e) => setSize(e.target.value)}
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Implementation</CardTitle>
              <CardDescription>Copy and paste the code below</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>HTML</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(generateHtmlCode())}
                  >
                    <Copy className="mr-2 h-4 w-4" />
                    {copied ? 'Copied!' : 'Copy'}
                  </Button>
                </div>
                <pre className="rounded-lg bg-muted p-4 text-xs overflow-x-auto">
                  <code>{generateHtmlCode()}</code>
                </pre>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Markdown</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(generateMarkdownCode())}
                  >
                    <Copy className="mr-2 h-4 w-4" />
                    {copied ? 'Copied!' : 'Copy'}
                  </Button>
                </div>
                <pre className="rounded-lg bg-muted p-4 text-xs overflow-x-auto">
                  <code>{generateMarkdownCode()}</code>
                </pre>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Image URL</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(generateBadgeUrl())}
                  >
                    <Copy className="mr-2 h-4 w-4" />
                    {copied ? 'Copied!' : 'Copy'}
                  </Button>
                </div>
                <pre className="rounded-lg bg-muted p-4 text-xs overflow-x-auto">
                  <code>{generateBadgeUrl()}</code>
                </pre>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>See how your badge will look</CardDescription>
            </CardHeader>
            <CardContent>{getBadgePreview()}</CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Badge Features</CardTitle>
              <CardDescription>What makes our badges special</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start">
                  <BadgeCheck className="mr-2 h-5 w-5 flex-shrink-0 text-primary" />
                  <span>
                    <strong>Real-time Verification:</strong> Badges link to live
                    verification pages
                  </span>
                </li>
                <li className="flex items-start">
                  <BadgeCheck className="mr-2 h-5 w-5 flex-shrink-0 text-primary" />
                  <span>
                    <strong>Customizable:</strong> Choose from multiple styles and sizes
                  </span>
                </li>
                <li className="flex items-start">
                  <BadgeCheck className="mr-2 h-5 w-5 flex-shrink-0 text-primary" />
                  <span>
                    <strong>Secure:</strong> Cryptographically signed to prevent tampering
                  </span>
                </li>
                <li className="flex items-start">
                  <BadgeCheck className="mr-2 h-5 w-5 flex-shrink-0 text-primary" />
                  <span>
                    <strong>Responsive:</strong> Works on all devices and screen sizes
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Usage Guidelines</CardTitle>
              <CardDescription>Best practices for badge implementation</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="list-inside list-disc space-y-2 text-sm text-muted-foreground">
                <li>Place badges in prominent, easily visible locations</li>
                <li>Ensure badges are clickable and link to verification pages</li>
                <li>Don't modify or alter badge designs</li>
                <li>Use badges only for verified receipts</li>
                <li>Keep badge implementations up to date</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
