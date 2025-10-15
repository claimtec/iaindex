# Example Documentation - Docusaurus Publisher

This is an example AIIndex implementation for a Docusaurus-powered documentation site.

## Overview

**Site**: CloudForge Documentation
**Domain**: cloudforge-docs.dev
**Platform**: Docusaurus 3.0
**Content Type**: Technical documentation for cloud infrastructure platform

## Setup Instructions

### 1. Install AIIndex Docusaurus Plugin

```bash
cd your-docusaurus-site
npm install @aiindex/docusaurus-plugin
```

### 2. Configure Plugin

Add to `docusaurus.config.js`:

```javascript
module.exports = {
  // ... other config
  plugins: [
    [
      '@aiindex/docusaurus-plugin',
      {
        publisherId: 'cloudforge-docs.dev',
        domain: 'cloudforge-docs.dev',
        publisherInfo: {
          name: 'CloudForge Documentation',
          description: 'Comprehensive documentation for CloudForge',
          url: 'https://cloudforge-docs.dev',
          contact: {
            email: 'docs@cloudforge.dev',
            url: 'https://cloudforge-docs.dev/contact'
          },
          logo: 'https://cloudforge-docs.dev/img/logo.svg'
        },
        accessPolicy: {
          allowed: true,
          attributionRequired: true,
          commercialUse: true,
          receiptRequired: true,
          webhookUrl: 'https://cloudforge-docs.dev/api/aiindex/receipts'
        },
        // Include/exclude patterns
        includePaths: ['/docs/**'],
        excludePaths: ['/blog/**', '/internal/**'],
        // Auto-generate summaries
        generateSummaries: true,
        summaryLength: 2000,
        // Update on build
        generateOnBuild: true,
        outputPath: 'static/.well-known/ai-index.json'
      }
    ]
  ]
};
```

### 3. Add Frontmatter to Docs

Enhance doc pages with AI-friendly metadata:

```markdown
---
id: getting-started
title: Getting Started with CloudForge
description: Quick start guide to deploy your first application
tags: [getting-started, tutorial, basics]
ai_summary: >
  Step-by-step guide covering installation, cluster setup,
  and first deployment. Takes approximately 15 minutes.
ai_priority: high
---

# Getting Started

Your documentation content...
```

### 4. Generate ai-index.json

```bash
# Generate during build
npm run build

# Or manually generate
npx aiindex-docusaurus generate

# Output will be at: build/.well-known/ai-index.json
```

### 5. Verify Implementation

```bash
# Test the generated file
curl https://cloudforge-docs.dev/.well-known/ai-index.json

# Validate schema
npx @aiindex/sdk-node validate https://cloudforge-docs.dev

# Preview locally
npm start
# Visit: http://localhost:3000/.well-known/ai-index.json
```

## Documentation Structure

### Core Documentation (10 pages)

1. **Getting Started** - `/docs/getting-started`
   - Installation and first deployment
   - 15-minute tutorial
   - Prerequisites and system requirements

2. **Installation Guide** - `/docs/installation`
   - Detailed installation for all platforms
   - Docker and Kubernetes deployment
   - Building from source

3. **Core Concepts** - `/docs/core-concepts`
   - Architecture overview
   - Fundamental concepts
   - Design philosophy

4. **Deploying Applications** - `/docs/deploying-applications`
   - CLI and YAML deployment
   - Container management
   - Health checks and rollbacks

5. **Scaling and Load Balancing** - `/docs/scaling`
   - Auto-scaling configuration
   - Load balancer setup
   - Performance optimization

6. **Networking** - `/docs/networking`
   - Service discovery
   - DNS configuration
   - Network policies

7. **Storage** - `/docs/storage`
   - Persistent volumes
   - Snapshots and backups
   - Database integration

8. **Monitoring** - `/docs/monitoring`
   - Metrics and logging
   - Alerting
   - Observability stack

9. **API Reference** - `/docs/api-reference`
   - REST API documentation
   - Authentication
   - Examples

10. **CLI Reference** - `/docs/cli-reference`
    - Command reference
    - Configuration
    - Shell completion

## Verification Badge Implementation

### Add to Docusaurus Config

```javascript
// docusaurus.config.js
module.exports = {
  themeConfig: {
    navbar: {
      items: [
        // ... other items
        {
          type: 'html',
          position: 'right',
          value: '<a href="https://aiindex.org/publishers/cloudforge-docs.dev" target="_blank" class="navbar__aiindex">AIIndex Verified</a>'
        }
      ]
    },
    footer: {
      links: [
        // ... other links
        {
          title: 'AI Access',
          items: [
            {
              label: 'AIIndex Verified',
              href: 'https://aiindex.org/publishers/cloudforge-docs.dev'
            },
            {
              label: 'AI-Index JSON',
              href: '/.well-known/ai-index.json'
            }
          ]
        }
      ]
    }
  }
};
```

### Custom CSS for Badge

Add to `src/css/custom.css`:

```css
/* AIIndex Badge Styles */
.navbar__aiindex {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
  color: white !important;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.navbar__aiindex:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.navbar__aiindex::before {
  content: '✓';
  margin-right: 6px;
  font-weight: bold;
}

/* Footer badge */
.footer__aiindex-badge {
  margin-top: 20px;
}

.footer__aiindex-badge img {
  transition: opacity 0.2s;
}

.footer__aiindex-badge img:hover {
  opacity: 0.8;
}
```

## Receipt Handling

### Setup Receipt Endpoint

Create `src/pages/api/aiindex/receipts.js`:

```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const receipt = req.body;

    // Validate receipt structure
    if (!receipt.version || !receipt.receipt_id || !receipt.publisher_id) {
      return res.status(400).json({ error: 'Invalid receipt format' });
    }

    // Store receipt (database, file, or forward to analytics)
    await storeReceipt(receipt);

    // Log receipt
    console.log('Receipt received:', {
      id: receipt.receipt_id,
      client: receipt.client_name,
      pages: receipt.access?.pages_accessed
    });

    return res.status(200).json({
      success: true,
      receipt_id: receipt.receipt_id,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Receipt handling error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

async function storeReceipt(receipt) {
  // Implement your storage logic
  // Options: Database, file system, analytics service, etc.
}
```

## Advanced Features

### 1. Auto-Summary Generation

The plugin can auto-generate AI-friendly summaries:

```javascript
// docusaurus.config.js
{
  generateSummaries: true,
  summaryOptions: {
    maxLength: 2000,
    includeCodeExamples: false,
    focusOnCommands: true // For CLI docs
  }
}
```

### 2. Versioned Docs Support

Handle multiple documentation versions:

```javascript
{
  versions: {
    current: {
      label: 'v2.5.x',
      path: 'docs'
    },
    '2.4': {
      label: 'v2.4.x',
      path: 'docs-2.4'
    }
  },
  includeAllVersions: true // Include all versions in ai-index.json
}
```

### 3. API Integration

Link to OpenAPI/Swagger specs:

```javascript
{
  apiDocs: {
    enabled: true,
    openApiUrl: 'https://api.cloudforge-docs.dev/openapi.json',
    includeInIndex: true
  }
}
```

### 4. Search Integration

Enhance with Algolia search data:

```javascript
{
  search: {
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_API_KEY',
      indexName: 'cloudforge-docs'
    },
    exportToAIIndex: true // Export search index to ai-index.json
  }
}
```

## Custom React Component

Create `src/components/AIIndexBadge.js`:

```jsx
import React from 'react';
import styles from './AIIndexBadge.module.css';

export default function AIIndexBadge({ size = 'medium' }) {
  const badgeUrl = `https://aiindex.org/badge-${size}.svg`;
  const publisherUrl = 'https://aiindex.org/publishers/cloudforge-docs.dev';

  return (
    <div className={styles.aiindexBadge}>
      <a href={publisherUrl} target="_blank" rel="noopener noreferrer">
        <img
          src={badgeUrl}
          alt="AIIndex Verified Publisher"
          loading="lazy"
        />
      </a>
      <p className={styles.description}>
        This documentation is AI-accessible via the AIIndex protocol.
        <a href="/.well-known/ai-index.json">View AI-Index</a>
      </p>
    </div>
  );
}
```

Use in MDX files:

```mdx
import AIIndexBadge from '@site/src/components/AIIndexBadge';

# Documentation

<AIIndexBadge size="large" />

Your content here...
```

## Testing

### Local Testing

```bash
# Start dev server
npm start

# In another terminal, test ai-index.json
curl http://localhost:3000/.well-known/ai-index.json | jq

# Validate
npx @aiindex/sdk-node validate http://localhost:3000
```

### Build Testing

```bash
# Build site
npm run build

# Serve build
npm run serve

# Test production ai-index.json
curl http://localhost:3000/.well-known/ai-index.json
```

### Receipt Testing

```bash
# Send test receipt to webhook
curl -X POST http://localhost:3000/api/aiindex/receipts \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "receipt_id": "test-123",
    "publisher_id": "cloudforge-docs.dev",
    "client_id": "test-client",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'
```

## Deployment

### Netlify

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "build"

[[redirects]]
  from = "/.well-known/ai-index.json"
  to = "/.well-known/ai-index.json"
  status = 200
  force = true

[[headers]]
  for = "/.well-known/ai-index.json"
  [headers.values]
    Content-Type = "application/json"
    Access-Control-Allow-Origin = "*"
```

### Vercel

```json
// vercel.json
{
  "routes": [
    {
      "src": "/.well-known/ai-index.json",
      "dest": "/.well-known/ai-index.json",
      "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    }
  ]
}
```

### GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

## Troubleshooting

### ai-index.json not found

1. Check `outputPath` in config
2. Verify build completed successfully
3. Ensure static files are copied

```bash
# Check if file exists in build
ls -la build/.well-known/ai-index.json
```

### Pages missing from index

1. Check `includePaths` and `excludePaths`
2. Verify frontmatter
3. Rebuild site

```bash
# Clear cache and rebuild
npm run clear
npm run build
```

### Summary generation issues

1. Check `generateSummaries` is enabled
2. Verify docs have content
3. Adjust `summaryLength` if truncated

## Best Practices

### 1. Write AI-Friendly Docs
- Clear, concise headings
- Structured content
- Code examples with explanations
- Consistent terminology

### 2. Use Frontmatter Effectively
```markdown
---
title: Clear, descriptive title
description: Brief summary (< 160 chars)
tags: [relevant, searchable, tags]
ai_summary: Detailed summary for AI (< 2000 chars)
ai_priority: high | medium | low
---
```

### 3. Maintain Up-to-Date Index
- Auto-generate on each build
- Review summaries periodically
- Update contact information
- Keep versions current

### 4. Monitor AI Usage
- Track receipt volume
- Identify popular docs
- Optimize frequently accessed content
- Monitor attribution compliance

## Resources

- [AIIndex Docusaurus Plugin Docs](https://docs.aiindex.org/docusaurus)
- [Docusaurus Documentation](https://docusaurus.io)
- [CloudForge GitHub](https://github.com/cloudforge/cloudforge)
- [AIIndex Protocol Spec](https://aiindex.org/spec)

## Support

- Plugin Issues: https://github.com/aiindex/docusaurus-plugin/issues
- AIIndex Support: support@aiindex.org
- CloudForge Docs: docs@cloudforge.dev
