# AI Index - Shopify App

Make your Shopify store discoverable by AI assistants like ChatGPT, Claude, and others.

## Features

- **Automatic AI Index Generation**: Generates a structured `/ai-index.json` file from your store data
- **Theme Integration**: Auto-publishes the index into your theme's `assets/` directory
- **Merchant Verification**: Uses shop domain as publisher_id for verification
- **LLM Access Webhooks**: Receive notifications when AI assistants access your content
- **Analytics Dashboard**: Track AI traffic and engagement with your store
- **Auto-sync**: Automatically updates the index when products, pages, or articles change

## Installation

### Prerequisites

- Node.js 16 or higher
- A Shopify Partner account
- Shopify CLI installed (`npm install -g @shopify/cli`)

### Setup

1. **Clone and install dependencies**:
   ```bash
   cd packages/shopify-app
   npm install
   cd frontend && npm install
   ```

2. **Create a Shopify app**:
   ```bash
   shopify app create
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Update `.env` with your Shopify credentials:
   - `SHOPIFY_API_KEY`: Your app's API key
   - `SHOPIFY_API_SECRET`: Your app's API secret
   - `SHOPIFY_APP_URL`: Your app's public URL

4. **Update shopify.app.toml**:
   - Set `client_id` to your app's client ID
   - Set `application_url` to your app's URL

5. **Build the frontend**:
   ```bash
   npm run build:frontend
   ```

6. **Start the app**:
   ```bash
   npm start
   ```

7. **Deploy to production**:
   ```bash
   shopify app deploy
   ```

## Usage

### For Merchants

1. **Install the app** from the Shopify App Store or via partner link
2. **Authorize** the app to access your store data
3. **Generate AI Index**: Click "Generate AI Index" in the dashboard
4. **View Analytics**: Monitor AI assistant traffic in the dashboard

The app will automatically:
- Create `/ai-index.json` in your theme's assets
- Add a snippet to reference the index
- Update the index when you add/edit products, pages, or articles

### For Developers

#### API Endpoints

- `GET /api/shop` - Get current shop information
- `GET /api/ai-index` - Get generated AI Index JSON
- `POST /api/generate-index` - Manually trigger index generation
- `GET /api/analytics` - Get analytics data
- `POST /api/webhooks/access` - Webhook for LLM access receipts
- `POST /api/webhooks/content` - Webhook for content updates

#### AI Index Structure

The generated `/ai-index.json` includes:

```json
{
  "version": "1.0",
  "publisher": {
    "id": "store.myshopify.com",
    "name": "My Store",
    "domain": "mystore.com",
    "type": "ecommerce",
    "platform": "shopify"
  },
  "content": {
    "products": [...],
    "pages": [...],
    "articles": [...]
  },
  "metadata": {
    "generated_at": "2025-01-15T10:30:00Z",
    "total_products": 150,
    "total_pages": 10,
    "total_articles": 25
  },
  "access": {
    "webhook_url": "https://your-app.com/api/webhooks/access",
    "verification_required": true
  }
}
```

## Architecture

```
shopify-app/
├── server.js              # Express server & OAuth
├── routes/
│   ├── index.js          # Main API routes
│   ├── webhooks.js       # Webhook handlers
│   └── analytics.js      # Analytics endpoints
├── services/
│   └── shopify.js        # Shopify API integration
├── frontend/             # React + Polaris UI
│   └── src/
│       ├── App.js
│       └── components/
│           ├── Dashboard.js
│           └── AIIndexViewer.js
├── package.json
├── shopify.app.toml      # Shopify app configuration
└── README.md
```

## Webhooks

### Content Update Webhooks

Automatically registered for:
- `products/create`
- `products/update`
- `products/delete`
- `pages/create`
- `pages/update`
- `pages/delete`

### LLM Access Webhook

Endpoint: `POST /api/webhooks/access`

Receives notifications when AI assistants access your content:

```json
{
  "llm_provider": "openai-chatgpt",
  "content_accessed": ["product:123", "page:456"],
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {
    "user_query": "What products do you sell?",
    "response_included": true
  }
}
```

## Development

```bash
# Start development server
npm run dev

# Build frontend
npm run build:frontend

# Install frontend dependencies
npm run install:frontend
```

## Testing

1. Install the app on a development store
2. Add some products, pages, and blog posts
3. Click "Generate AI Index"
4. Visit `https://your-store.myshopify.com/assets/ai-index.json`
5. Verify the JSON structure

## Troubleshooting

### Theme Access Issues
- Ensure the app has `read_themes` and `write_themes` scopes
- Check that you have an active theme published

### Webhook Failures
- Verify your app URL is publicly accessible
- Check webhook signatures are being validated
- Review webhook logs in Shopify admin

### Missing Content
- Ensure products/pages are published and not drafts
- Check API rate limits haven't been exceeded
- Verify the app has necessary read scopes

## Support

For issues and questions:
- GitHub Issues: [repository-url]
- Documentation: [docs-url]
- Email: support@example.com

## License

MIT
