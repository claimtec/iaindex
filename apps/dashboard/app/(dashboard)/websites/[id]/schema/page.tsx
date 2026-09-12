'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { websitesAPI, schemaAPI } from '@/lib/api';
import {
  ArrowLeft,
  Copy,
  Download,
  Check,
  Loader2,
  Sparkles,
  CheckCircle,
  XCircle
} from 'lucide-react';

export default function SchemaManagementPage() {
  const params = useParams();
  const router = useRouter();
  const websiteId = params.id as string;
  const [copied, setCopied] = useState(false);
  const [generating, setGenerating] = useState(false);

  const { data: website } = useQuery({
    queryKey: ['website', websiteId],
    queryFn: async () => {
      const response = await websitesAPI.get(websiteId);
      return response.data.website;
    },
  });

  const { data: schema, refetch: refetchSchema } = useQuery({
    queryKey: ['schema', websiteId],
    queryFn: async () => {
      const response = await schemaAPI.get(websiteId);
      return response.data.website;
    },
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      if (!website) return;
      setGenerating(true);
      const response = await schemaAPI.generate(websiteId, {
        domain: website.domain,
        name: website.name,
        description: website.description,
        industry: website.industry
      });
      return response.data.website;
    },
    onSuccess: () => {
      refetchSchema();
      setGenerating(false);
    },
    onError: () => {
      setGenerating(false);
    }
  });

  const schemaMarkup = (schema as any)?.schema_markup || (schema as any)?.schemaMarkup;

  const handleCopy = () => {
    if (schemaMarkup) {
      navigator.clipboard.writeText(JSON.stringify(schemaMarkup, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (schemaMarkup) {
      const blob = new Blob([JSON.stringify(schemaMarkup, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${website?.domain}-schema.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Schema Management</h1>
        <p className="text-gray-600">
          Generate and manage structured data markup for {website?.name}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Schema status */}
        <Card>
          <CardHeader>
            <CardTitle>Schema Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              {(schema as any)?.is_valid ? (
                <>
                  <CheckCircle className="text-success" size={24} />
                  <div>
                    <p className="font-medium text-gray-900">Valid Schema</p>
                    <p className="text-sm text-gray-600">Schema is properly formatted</p>
                  </div>
                </>
              ) : schema ? (
                <>
                  <XCircle className="text-danger" size={24} />
                  <div>
                    <p className="font-medium text-gray-900">Invalid Schema</p>
                    <p className="text-sm text-gray-600">Schema has validation errors</p>
                  </div>
                </>
              ) : (
                <>
                  <XCircle className="text-gray-400" size={24} />
                  <div>
                    <p className="font-medium text-gray-900">No Schema</p>
                    <p className="text-sm text-gray-600">Generate schema to get started</p>
                  </div>
                </>
              )}
            </div>

            {(schema as any)?.validation_errors && (schema as any)?.validation_errors.length > 0 && (
              <div className="p-3 bg-danger/10 border border-danger/20 rounded-lg">
                <p className="text-sm font-medium text-danger mb-2">Validation Errors:</p>
                <ul className="text-xs text-danger space-y-1">
                  {(schema as any)?.validation_errors.map((error: string, i: number) => (
                    <li key={i}>• {error}</li>
                  ))}
                </ul>
              </div>
            )}

            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generating}
              className="w-full"
            >
              {generating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  {schema ? 'Regenerate Schema' : 'Generate Schema'}
                </>
              )}
            </Button>

            {schema && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={handleCopy}
                  className="flex-1"
                  disabled={!schemaMarkup}
                >
                  {copied ? (
                    <>
                      <Check size={16} className="mr-2" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy size={16} className="mr-2" />
                      Copy
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleDownload}
                  className="flex-1"
                  disabled={!schemaMarkup}
                >
                  <Download size={16} className="mr-2" />
                  Download
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Schema editor */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Schema Markup</CardTitle>
            <CardDescription>
              Copy this JSON-LD schema and add it to your website&apos;s HTML
            </CardDescription>
          </CardHeader>
          <CardContent>
            {schemaMarkup ? (
              <div className="relative">
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs font-mono max-h-96">
                  {JSON.stringify(schemaMarkup, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <Sparkles size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-gray-600 mb-2">No schema generated yet</p>
                <p className="text-sm text-gray-500">
                  Click &quot;Generate Schema&quot; to create optimized markup
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Implementation instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Implementation Instructions</CardTitle>
          <CardDescription>
            How to add schema markup to your website
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">
                  Copy the Schema Markup
                </h4>
                <p className="text-sm text-gray-600">
                  Click the &quot;Copy&quot; button above to copy the JSON-LD schema to your clipboard.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">
                  Add to Your Website&apos;s HTML
                </h4>
                <p className="text-sm text-gray-600 mb-2">
                  Paste the schema inside a &lt;script&gt; tag in your HTML&apos;s &lt;head&gt; section:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded text-xs font-mono overflow-x-auto">
{`<script type="application/ld+json">
  {JSON-LD schema here}
</script>`}
                </pre>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">
                  Validate Implementation
                </h4>
                <p className="text-sm text-gray-600">
                  Use Google&apos;s Rich Results Test or Schema Markup Validator to verify your implementation.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                4
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">
                  Monitor Impact
                </h4>
                <p className="text-sm text-gray-600">
                  Return to this dashboard to track how schema markup improves your AI visibility.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
