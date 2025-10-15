# AI Index Platform Integrations

This directory contains platform-specific integrations for AI Index, enabling websites and e-commerce stores to be discoverable by AI assistants.

## Available Integrations

### 1. Shopify App (`/shopify-app/`)

Full-featured Shopify app with embedded UI, merchant verification, and analytics dashboard.

**Key Features:**
- Embedded app using Shopify App Bridge + Polaris UI
- Auto-publishes `/ai-index.json` into theme assets
- Merchant verification using shop domain as publisher_id
- Webhook endpoint for LLM access receipts
- Real-time analytics dashboard
- Auto-sync on product/page/article changes

**Tech Stack:**
- Backend: Node.js/Express
- Frontend: React + Shopify Polaris
- API: Shopify REST Admin API

### 2. Framer Plugin (`/framer-plugin/`)

React component for Framer sites that automatically generates AI Index metadata.

**Key Features:**
- Drop-in React component
- Automatic page discovery from site navigation
- JSON injection into page head
- Configuration panel in Framer UI
- Webhook support for AI access notifications
- Custom metadata support

**Tech Stack:**
- TypeScript/React
- Framer Component API
- Framer property controls

### 3. Ghost CMS Plugin (`/ghost-plugin/`)

Node-based Ghost integration with admin panel and real-time sync.

**Key Features:**
- Automatic `/ai-index.json` endpoint
- Real-time content sync (posts, pages, authors, tags)
- Admin dashboard in Ghost Admin
- Webhook endpoint for LLM access tracking
- Analytics and access logs
- Event-driven updates

**Tech Stack:**
- Node.js
- Ghost Admin API
- Ghost Events System

## Quick Start

### Shopify App

```bash
cd shopify-app
npm install
cp .env.example .env
# Configure your Shopify credentials
npm run build:frontend
npm start
```

[Full documentation](./shopify-app/README.md)

### Framer Plugin

```bash
cd framer-plugin
npm install
npm run build
# Import into Framer project
```

[Full documentation](./framer-plugin/README.md)

### Ghost Plugin

```bash
cd ghost-plugin
npm install
# Copy to Ghost plugins directory
# Restart Ghost
```

[Full documentation](./ghost-plugin/README.md)

## AI Index Structure

All integrations generate a standardized AI Index JSON structure:

```json
{
  "version": "1.0",
  "publisher": {
    "id": "unique-publisher-id",
    "name": "Publisher Name",
    "domain": "example.com",
    "type": "ecommerce|blog|website",
    "platform": "shopify|framer|ghost"
  },
  "content": {
    "products": [...],    // For e-commerce
    "posts": [...],       // For blogs
    "pages": [...],       // For all
    "articles": [...]     // For blogs
  },
  "metadata": {
    "generated_at": "2025-01-15T10:30:00Z",
    "total_products": 100,
    "total_posts": 50,
    "total_pages": 10
  },
  "access": {
    "webhook_url": "https://example.com/api/aiindex/access",
    "verification_required": true
  }
}
```

## Webhook Format

All integrations support a standardized webhook for LLM access tracking:

### Request

```json
{
  "llm_provider": "openai-chatgpt",
  "content_accessed": ["post-123", "product-456"],
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {
    "user_query": "What products do you have?",
    "response_included": true
  }
}
```

### Response

```json
{
  "success": true,
  "receipt_id": "receipt_1234567890"
}
```

## Integration Comparison

| Feature | Shopify | Framer | Ghost |
|---------|---------|--------|-------|
| Auto-publish | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ❌ | ✅ |
| Analytics | ✅ | ❌ | ✅ |
| Webhooks | ✅ | ✅ | ✅ |
| Auto-sync | ✅ | ✅ | ✅ |
| Configuration UI | ✅ | ✅ | ✅ |
| Real-time updates | ✅ | ✅ | ✅ |

## Development

Each integration has its own development setup. See individual READMEs for details.

### Testing Locally

1. **Shopify**: Use Shopify CLI's dev server
   ```bash
   cd shopify-app
   npm run dev
   ```

2. **Framer**: Use Framer's preview mode
   ```bash
   cd framer-plugin
   npm run watch
   ```

3. **Ghost**: Link to local Ghost installation
   ```bash
   cd ghost-plugin
   npm link
   cd /var/www/ghost/content/plugins
   npm link @iaindex/ghost-plugin
   ```

## Deployment

### Shopify App

Deploy to Heroku, Vercel, or any Node.js hosting:

```bash
cd shopify-app
npm run build:frontend
# Deploy to your hosting provider
shopify app deploy
```

### Framer Plugin

Publish to Framer package registry:

```bash
cd framer-plugin
npm run build
npm publish
```

### Ghost Plugin

Install via Ghost CLI or manually:

```bash
cd /var/www/ghost
ghost install @iaindex/ghost-plugin
ghost restart
```

## Architecture

### Common Patterns

All integrations follow these patterns:

1. **Content Discovery**: Platform-specific APIs to fetch content
2. **Index Generation**: Transform to standardized AI Index format
3. **Publishing**: Expose at `/ai-index.json` or inject into HTML
4. **Webhook Handling**: Receive and log LLM access notifications
5. **Analytics**: Aggregate and display access data

### Data Flow

```
Platform Content → Generator → AI Index JSON → AI Assistant
                                      ↓
                              Webhook Endpoint
                                      ↓
                              Analytics Dashboard
```

## Support

- **Documentation**: See individual integration READMEs
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-index/issues)
- **Email**: support@example.com

## Contributing

Contributions welcome! To add a new platform integration:

1. Create a new directory under `/packages/`
2. Implement the standard AI Index structure
3. Add webhook endpoint support
4. Write comprehensive README
5. Submit a pull request

## License

MIT
