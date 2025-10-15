# AI Index Platform Integrations - Complete Summary

Three production-ready integrations have been built for Shopify, Framer, and Ghost CMS. This document provides installation instructions and architectural details for each.

---

## 1. Shopify App Integration

**Location**: `/Users/dineshanchetty/Documents/claimtec/iaindex/packages/shopify-app/`

### Architecture

```
shopify-app/
├── server.js                        # Express server with OAuth & Shopify App Bridge
├── routes/
│   ├── index.js                    # Main API routes (generate, view AI Index)
│   ├── webhooks.js                 # LLM access & content update webhooks
│   └── analytics.js                # Analytics endpoints
├── services/
│   └── shopify.js                  # Shopify API integration & AI Index generator
├── frontend/                       # React + Polaris UI
│   ├── package.json
│   └── src/
│       ├── App.js                  # Main app with tabs
│       └── components/
│           ├── Dashboard.js        # Analytics dashboard
│           └── AIIndexViewer.js    # AI Index preview
├── package.json
├── shopify.app.toml                # Shopify app configuration
├── .env.example                    # Environment variables template
└── README.md                       # Full documentation

Total Files: 13 core files
```

### Features Implemented

1. **Embedded App**: Full Shopify App Bridge integration with Polaris UI
2. **OAuth Flow**: Complete authentication with session management
3. **AI Index Generation**:
   - Fetches products, pages, articles, and blog posts
   - Transforms to standardized AI Index JSON
   - Publishes to theme assets as `/ai-index.json`
4. **Merchant Verification**: Uses shop domain as publisher_id
5. **Webhooks**:
   - Content update webhooks (products, pages)
   - LLM access receipt webhook
6. **Analytics Dashboard**:
   - Total AI accesses
   - By LLM provider
   - By content type
   - Recent access logs
7. **Auto-sync**: Registers webhooks for automatic updates

### Installation Steps

#### Prerequisites
```bash
# Required
- Node.js 16+
- Shopify Partner account
- Shopify CLI: npm install -g @shopify/cli
```

#### Setup Instructions

```bash
# 1. Navigate to the app directory
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/shopify-app

# 2. Install backend dependencies
npm install

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Create Shopify app (if not already created)
shopify app create

# 5. Configure environment variables
cp .env.example .env

# Edit .env with your credentials:
# SHOPIFY_API_KEY=your_api_key
# SHOPIFY_API_SECRET=your_api_secret
# SHOPIFY_APP_URL=https://your-app-url.com
# PORT=3000

# 6. Update shopify.app.toml
# Set client_id and application_url

# 7. Build the frontend
npm run build:frontend

# 8. Start the development server
npm run dev

# 9. Deploy to production
shopify app deploy
```

#### Testing

```bash
# 1. Install on a development store
shopify app install

# 2. Generate AI Index
# Click "Generate AI Index" in the dashboard

# 3. Verify the output
# Visit: https://your-store.myshopify.com/assets/ai-index.json
```

### API Endpoints

- `GET /api/shop` - Get shop information
- `GET /api/ai-index` - Get generated AI Index
- `POST /api/generate-index` - Generate and publish AI Index
- `GET /api/analytics` - Get analytics data
- `POST /api/webhooks/access` - LLM access receipt webhook
- `POST /api/webhooks/content` - Content update webhook

---

## 2. Framer Plugin Integration

**Location**: `/Users/dineshanchetty/Documents/claimtec/iaindex/packages/framer-plugin/`

### Architecture

```
framer-plugin/
├── src/
│   ├── AIIndex.tsx                 # Main React component with AI Index logic
│   └── index.tsx                   # Exports
├── framer.json                     # Framer plugin manifest
├── package.json
├── tsconfig.json
└── README.md                       # Full documentation

Total Files: 6 core files
```

### Features Implemented

1. **React Component**: Invisible component that runs on page load
2. **Page Discovery**: Automatically scans navigation links
3. **AI Index Generation**:
   - Extracts page titles, URLs, and metadata
   - Generates standardized AI Index JSON
4. **JSON Injection**: Adds metadata to page `<head>`
5. **Framer Property Controls**:
   - Enable/disable toggle
   - Publisher ID
   - Site name and description
   - Webhook URL
   - Custom metadata (JSON)
6. **Webhook Support**: Posts to external endpoint when configured
7. **Storage**: Saves to localStorage for access

### Installation Steps

#### Method 1: From NPM (Recommended)

```bash
# 1. Open your Framer project
# 2. Click Assets panel > "+" button
# 3. Search for "AI Index"
# 4. Click "Install"
```

#### Method 2: Manual Build & Import

```bash
# 1. Navigate to plugin directory
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/framer-plugin

# 2. Install dependencies
npm install

# 3. Build the plugin
npm run build

# 4. In Framer:
# - Go to Assets > Code
# - Click "New from NPM"
# - Enter: @iaindex/framer-plugin
```

#### Usage in Framer

```typescript
// 1. Drag the "AI Index" component onto your master page/layout
// 2. Configure in Properties panel:

<AIIndex
  enabled={true}
  publisherId="mysite.com"
  siteName="My Awesome Site"
  siteDescription="A portfolio and blog"
  webhookUrl="https://api.mysite.com/webhook"
  autoGenerate={true}
  customMetadata='{"industry":"design","contact":"hello@mysite.com"}'
/>

// 3. Publish your site
// 4. The AI Index is now active!
```

#### Testing

```bash
# 1. Preview your Framer site
# 2. Open browser console
# 3. Check for AI Index in localStorage:
localStorage.getItem('ai-index')

# 4. View injected metadata:
document.querySelector('#ai-index-data')
```

### Component Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable the plugin |
| `publisherId` | string | domain | Unique identifier |
| `siteName` | string | title | Site name |
| `siteDescription` | string | `""` | Brief description |
| `webhookUrl` | string | `""` | Webhook endpoint |
| `autoGenerate` | boolean | `true` | Auto-generate on load |
| `customMetadata` | string | `{}` | Custom JSON metadata |

---

## 3. Ghost CMS Plugin Integration

**Location**: `/Users/dineshanchetty/Documents/claimtec/iaindex/packages/ghost-plugin/`

### Architecture

```
ghost-plugin/
├── index.js                        # Main plugin entry & Ghost event handlers
├── lib/
│   ├── generator.js               # AI Index generator from Ghost content
│   ├── receipts.js                # Access receipt storage & analytics
│   └── webhooks.js                # Content update handlers
├── admin/
│   └── index.html                 # Admin dashboard UI
├── package.json
├── ghost.json                     # Ghost plugin metadata
└── README.md                      # Full documentation

Total Files: 8 core files
```

### Features Implemented

1. **Automatic Endpoint**: Creates `/ai-index.json` route
2. **Content Integration**:
   - Fetches published posts, pages, authors, tags
   - Transforms to AI Index format
   - Includes excerpts, featured images, metadata
3. **Event-Driven Updates**: Auto-regenerates on:
   - `post.published`
   - `post.unpublished`
   - `page.published`
   - `page.unpublished`
4. **Webhook Endpoint**: `/api/aiindex/access` for LLM receipts
5. **Analytics**:
   - Total accesses
   - By LLM provider
   - By date
   - Recent access logs
6. **Admin Dashboard**: Beautiful UI in Ghost Admin panel

### Installation Steps

#### Method 1: Via Ghost CLI (Recommended)

```bash
# 1. Navigate to Ghost installation
cd /var/www/ghost

# 2. Install the plugin
ghost install @iaindex/ghost-plugin

# 3. Restart Ghost
ghost restart

# 4. Verify installation
ghost ls

# 5. Check logs
ghost log
```

#### Method 2: Manual Installation

```bash
# 1. Navigate to Ghost plugins directory
cd /var/www/ghost/content/plugins

# 2. Clone or copy the plugin
cp -r /Users/dineshanchetty/Documents/claimtec/iaindex/packages/ghost-plugin ./ghost-ai-index

# 3. Install dependencies
cd ghost-ai-index
npm install

# 4. Activate in Ghost config
# Edit: /var/www/ghost/config.production.json
{
  "plugins": {
    "ghost-ai-index": true
  }
}

# 5. Restart Ghost
cd /var/www/ghost
ghost restart
```

#### Method 3: Docker

```yaml
# Add to docker-compose.yml
services:
  ghost:
    image: ghost:latest
    volumes:
      - /Users/dineshanchetty/Documents/claimtec/iaindex/packages/ghost-plugin:/var/lib/ghost/content/plugins/ghost-ai-index
    environment:
      - AIINDEX_WEBHOOK_URL=https://your-api.com/webhook
```

#### Configuration (Optional)

```bash
# Set webhook URL for content updates
export AIINDEX_WEBHOOK_URL=https://your-api.com/webhook

# Or add to Ghost config:
{
  "aiindex": {
    "webhook_url": "https://your-api.com/webhook",
    "cache_ttl": 300,
    "rate_limit": {
      "requests_per_hour": 100
    }
  }
}
```

#### Testing

```bash
# 1. Verify AI Index endpoint
curl https://yourblog.com/ai-index.json | jq

# 2. Test webhook endpoint
curl -X POST https://yourblog.com/api/aiindex/access \
  -H "Content-Type: application/json" \
  -d '{
    "llm_provider": "openai-chatgpt",
    "content_accessed": ["post-123"],
    "timestamp": "2025-01-15T10:30:00Z"
  }'

# 3. Check Ghost logs
tail -f /var/www/ghost/content/logs/ghost.log

# 4. Access admin dashboard
# Login to Ghost Admin → Settings → Integrations → AI Index
```

---

## Comparison Matrix

| Feature | Shopify | Framer | Ghost |
|---------|---------|--------|-------|
| **Platform Type** | E-commerce | Website Builder | CMS/Blog |
| **Installation Complexity** | Medium | Easy | Medium |
| **UI Dashboard** | ✅ Full Polaris UI | ❌ | ✅ HTML Dashboard |
| **Analytics** | ✅ Advanced | ❌ | ✅ Basic |
| **Auto-Sync** | ✅ Webhooks | ✅ On-load | ✅ Events |
| **Configuration** | ✅ Admin + .env | ✅ Component props | ✅ Config file |
| **Content Types** | Products, Pages, Articles | Pages | Posts, Pages, Authors |
| **Webhook Support** | ✅ Bidirectional | ✅ Outgoing | ✅ Bidirectional |
| **Backend Required** | ✅ Node/Express | ❌ Client-side | ✅ Ghost plugin |
| **OAuth** | ✅ Shopify OAuth | ❌ | ❌ |
| **Theme Integration** | ✅ Asset injection | ✅ HTML injection | ✅ Route middleware |

---

## Common AI Index Structure

All three integrations generate this standardized format:

```json
{
  "version": "1.0",
  "publisher": {
    "id": "unique-publisher-id",
    "name": "Publisher Name",
    "description": "Brief description",
    "domain": "example.com",
    "type": "ecommerce|blog|website",
    "platform": "shopify|framer|ghost"
  },
  "content": {
    "products": [...],     // Shopify only
    "posts": [...],        // Ghost only
    "pages": [...],        // All platforms
    "articles": [...]      // Shopify (blogs)
  },
  "metadata": {
    "generated_at": "2025-01-15T10:30:00.000Z",
    "total_products": 100,  // If applicable
    "total_posts": 50,      // If applicable
    "total_pages": 10
  },
  "access": {
    "webhook_url": "https://example.com/api/aiindex/access",
    "verification_required": true,
    "rate_limit": {
      "requests_per_hour": 100,
      "burst": 10
    }
  }
}
```

---

## Webhook Specification

All integrations support LLM access webhooks:

### Request Format

```json
POST /api/aiindex/access
Content-Type: application/json

{
  "llm_provider": "openai-chatgpt",
  "content_accessed": ["post-123", "product-456"],
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {
    "user_query": "What products do you have?",
    "response_included": true,
    "model": "gpt-4"
  }
}
```

### Response Format

```json
{
  "success": true,
  "receipt_id": "receipt_1234567890",
  "message": "Access recorded successfully"
}
```

---

## Development Workflow

### Local Development

**Shopify:**
```bash
cd packages/shopify-app
npm run dev
# Uses Shopify CLI dev server
```

**Framer:**
```bash
cd packages/framer-plugin
npm run watch
# Import into Framer preview
```

**Ghost:**
```bash
cd packages/ghost-plugin
npm link
cd /var/www/ghost/content/plugins
npm link @iaindex/ghost-plugin
ghost restart
```

### Testing

Each integration includes comprehensive testing instructions in its README:
- `/packages/shopify-app/README.md`
- `/packages/framer-plugin/README.md`
- `/packages/ghost-plugin/README.md`

---

## Production Deployment

### Shopify App

```bash
# Build frontend
npm run build:frontend

# Deploy using Shopify CLI
shopify app deploy

# Or deploy to hosting provider (Heroku, Vercel, etc.)
git push heroku main
```

### Framer Plugin

```bash
# Build and publish to NPM
npm run build
npm publish

# Users can then install from Framer UI
```

### Ghost Plugin

```bash
# Package for distribution
npm pack

# Install on Ghost server
ghost install ghost-ai-index-1.0.0.tgz

# Or publish to NPM
npm publish
```

---

## Support & Documentation

Each integration includes:
- ✅ Complete README with examples
- ✅ Installation instructions
- ✅ Configuration guide
- ✅ API documentation
- ✅ Troubleshooting section
- ✅ Code examples

### File Locations

- **Shopify**: `/packages/shopify-app/README.md`
- **Framer**: `/packages/framer-plugin/README.md`
- **Ghost**: `/packages/ghost-plugin/README.md`
- **Overview**: `/packages/README.md`

---

## Next Steps

### For Shopify Merchants
1. Create Shopify Partner account
2. Install Shopify CLI
3. Follow installation steps in `/packages/shopify-app/README.md`
4. Deploy to Heroku or Vercel
5. Install on your store

### For Framer Users
1. Build the plugin locally
2. Import into Framer project
3. Add component to master page
4. Configure properties
5. Publish site

### For Ghost Bloggers
1. Access your Ghost server
2. Install plugin via CLI
3. Restart Ghost
4. Verify `/ai-index.json` endpoint
5. Configure webhooks (optional)

---

## License

All integrations are MIT licensed.

## Contributing

Contributions welcome! Each integration is independently maintainable.

---

**Summary**: Three production-ready integrations are now available for Shopify, Framer, and Ghost CMS. Each includes complete documentation, testing instructions, and deployment guides.
