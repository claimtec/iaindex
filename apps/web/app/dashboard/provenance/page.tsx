'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { VerificationBadge } from '@/components/badges/verification-badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Shield,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Copy,
  Check,
  Clock,
  GitBranch,
  Link as LinkIcon,
  QrCode,
  FileText,
  Fingerprint,
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

// Mock data - in production, this would come from an API
const provenanceData = {
  c2pa: {
    enabled: true,
    manifestCount: 1247,
    lastUpdated: '2025-10-13T10:30:00Z',
    signingKey: '0x1234...5678',
    validSignatures: 1243,
    invalidSignatures: 4,
  },
  merkle: {
    enabled: true,
    dailyRoots: 7,
    totalLeaves: 45823,
    lastRoot: '0xabcd...ef01',
    lastRootTimestamp: '2025-10-13T00:00:00Z',
    treeDepth: 16,
  },
  timestamp: {
    enabled: true,
    authority: 'DigiCert Timestamp Authority',
    lastVerification: '2025-10-13T09:45:00Z',
    totalTimestamps: 1247,
    verificationUrl: 'https://timestamp.digicert.com/verify',
  },
  blockchain: {
    enabled: true,
    network: 'Ethereum Mainnet',
    contractAddress: '0x742d...35Ac',
    totalTransactions: 124,
    lastTransaction: '0x8f23...a4d2',
    explorerUrl: 'https://etherscan.io/tx/',
  },
  contentCredentials: [
    {
      id: 'cc-001',
      contentId: 'receipt-2025-001',
      issuer: 'IAIndex Authority',
      issuedAt: '2025-10-12T14:30:00Z',
      status: 'valid',
      claims: ['origin', 'integrity', 'timestamp'],
    },
    {
      id: 'cc-002',
      contentId: 'receipt-2025-002',
      issuer: 'IAIndex Authority',
      issuedAt: '2025-10-12T15:45:00Z',
      status: 'valid',
      claims: ['origin', 'integrity', 'timestamp'],
    },
    {
      id: 'cc-003',
      contentId: 'receipt-2025-003',
      issuer: 'IAIndex Authority',
      issuedAt: '2025-10-12T16:20:00Z',
      status: 'revoked',
      claims: ['origin', 'integrity'],
    },
  ],
}

export default function ProvenancePage() {
  const [copied, setCopied] = useState('')

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(''), 2000)
  }

  const verificationStatus = {
    c2pa: provenanceData.c2pa.enabled,
    merkle: provenanceData.merkle.enabled,
    domain: true,
    timestamp: provenanceData.timestamp.enabled,
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Provenance & Verification</h1>
        <p className="text-muted-foreground">
          Multi-layer content authentication and cryptographic proof
        </p>
      </div>

      {/* Status Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">C2PA Status</CardTitle>
            {provenanceData.c2pa.enabled ? (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {provenanceData.c2pa.enabled ? 'Enabled' : 'Disabled'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {provenanceData.c2pa.manifestCount} manifests
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Merkle Trees</CardTitle>
            {provenanceData.merkle.enabled ? (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {provenanceData.merkle.dailyRoots}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Daily roots generated
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Timestamps</CardTitle>
            {provenanceData.timestamp.enabled ? (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {provenanceData.timestamp.totalTimestamps}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Verified timestamps
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blockchain</CardTitle>
            {provenanceData.blockchain.enabled ? (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {provenanceData.blockchain.totalTransactions}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              On-chain records
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="c2pa" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="c2pa">C2PA</TabsTrigger>
          <TabsTrigger value="merkle">Merkle Trees</TabsTrigger>
          <TabsTrigger value="timestamp">Timestamps</TabsTrigger>
          <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
          <TabsTrigger value="credentials">Credentials</TabsTrigger>
        </TabsList>

        {/* C2PA Tab */}
        <TabsContent value="c2pa" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                C2PA Content Credentials
              </CardTitle>
              <CardDescription>
                Coalition for Content Provenance and Authenticity
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Status</p>
                  <Badge
                    variant="default"
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Active
                  </Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Total Manifests</p>
                  <p className="text-2xl font-bold">
                    {provenanceData.c2pa.manifestCount}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Valid Signatures</p>
                  <p className="text-2xl font-bold text-green-600">
                    {provenanceData.c2pa.validSignatures}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Invalid Signatures</p>
                  <p className="text-2xl font-bold text-red-600">
                    {provenanceData.c2pa.invalidSignatures}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border bg-muted p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">Signing Key</p>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      copyToClipboard(provenanceData.c2pa.signingKey, 'signing-key')
                    }
                  >
                    {copied === 'signing-key' ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="font-mono text-xs">{provenanceData.c2pa.signingKey}</p>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Last Updated</span>
                <span className="font-medium">
                  {new Date(provenanceData.c2pa.lastUpdated).toLocaleString()}
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Merkle Tab */}
        <TabsContent value="merkle" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5" />
                Merkle Tree Attestation
              </CardTitle>
              <CardDescription>
                Cryptographic tree structure for batch verification
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Daily Roots</p>
                  <p className="text-2xl font-bold">
                    {provenanceData.merkle.dailyRoots}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Total Leaves</p>
                  <p className="text-2xl font-bold">
                    {provenanceData.merkle.totalLeaves.toLocaleString()}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Tree Depth</p>
                  <p className="text-2xl font-bold">
                    {provenanceData.merkle.treeDepth}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border bg-muted p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">Latest Root Hash</p>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      copyToClipboard(provenanceData.merkle.lastRoot, 'root-hash')
                    }
                  >
                    {copied === 'root-hash' ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="font-mono text-xs">{provenanceData.merkle.lastRoot}</p>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Root Generated</span>
                <span className="font-medium">
                  {new Date(provenanceData.merkle.lastRootTimestamp).toLocaleString()}
                </span>
              </div>

              <div className="rounded-lg border-2 border-dashed p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <GitBranch className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Next Root Generation</p>
                    <p className="text-xs text-muted-foreground">
                      Scheduled for midnight UTC
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Timestamp Tab */}
        <TabsContent value="timestamp" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                External Timestamp Verification
              </CardTitle>
              <CardDescription>
                Third-party timestamp authority integration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Timestamp Authority</p>
                  <p className="text-lg font-bold">
                    {provenanceData.timestamp.authority}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Total Timestamps</p>
                  <p className="text-2xl font-bold">
                    {provenanceData.timestamp.totalTimestamps}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Last Verification</span>
                <span className="font-medium">
                  {new Date(provenanceData.timestamp.lastVerification).toLocaleString()}
                </span>
              </div>

              <Button variant="outline" className="w-full" asChild>
                <a
                  href={provenanceData.timestamp.verificationUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Verify with Authority
                </a>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Blockchain Tab */}
        <TabsContent value="blockchain" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LinkIcon className="h-5 w-5" />
                Blockchain Integration
              </CardTitle>
              <CardDescription>
                On-chain provenance records
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Network</p>
                  <Badge variant="default">{provenanceData.blockchain.network}</Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Total Transactions</p>
                  <p className="text-2xl font-bold">
                    {provenanceData.blockchain.totalTransactions}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border bg-muted p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">Contract Address</p>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      copyToClipboard(
                        provenanceData.blockchain.contractAddress,
                        'contract'
                      )
                    }
                  >
                    {copied === 'contract' ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="font-mono text-xs">
                  {provenanceData.blockchain.contractAddress}
                </p>
              </div>

              <div className="rounded-lg border bg-muted p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">Latest Transaction</p>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      copyToClipboard(
                        provenanceData.blockchain.lastTransaction,
                        'tx'
                      )
                    }
                  >
                    {copied === 'tx' ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="font-mono text-xs">
                  {provenanceData.blockchain.lastTransaction}
                </p>
              </div>

              <Button variant="outline" className="w-full" asChild>
                <a
                  href={`${provenanceData.blockchain.explorerUrl}${provenanceData.blockchain.lastTransaction}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  View on Etherscan
                </a>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Credentials Tab */}
        <TabsContent value="credentials" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Content Credentials Viewer
              </CardTitle>
              <CardDescription>
                Recent content credentials and their status
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {provenanceData.contentCredentials.map((credential) => (
                <div
                  key={credential.id}
                  className="rounded-lg border p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Fingerprint className="h-4 w-4 text-muted-foreground" />
                      <span className="font-mono text-sm">{credential.id}</span>
                    </div>
                    <Badge
                      variant={
                        credential.status === 'valid'
                          ? 'default'
                          : 'destructive'
                      }
                    >
                      {credential.status}
                    </Badge>
                  </div>
                  <div className="grid gap-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Content ID</span>
                      <span className="font-medium">{credential.contentId}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Issuer</span>
                      <span className="font-medium">{credential.issuer}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Issued At</span>
                      <span className="font-medium">
                        {new Date(credential.issuedAt).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {credential.claims.map((claim) => (
                      <Badge key={claim} variant="outline" className="text-xs">
                        {claim}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Verification Badge Generator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5" />
            Verification Badge Generator
          </CardTitle>
          <CardDescription>
            Generate embeddable verification badges with QR codes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <VerificationBadge
            status={verificationStatus}
            contentId="example-content-123"
            variant="detailed"
            showEmbed={true}
          />
        </CardContent>
      </Card>
    </div>
  )
}
