# AI Index - Framer Plugin

Make your Framer site discoverable by AI assistants like ChatGPT, Claude, and others.

## Features

- **Zero Configuration**: Drop the component on any page to activate
- **Automatic Page Discovery**: Scans your Framer site structure automatically
- **JSON Injection**: Generates `/ai-index.json` metadata in page head
- **Webhook Support**: Send notifications to your backend when AI accesses content
- **Custom Metadata**: Add your own metadata fields
- **Real-time Updates**: Regenerates on page navigation

## Installation

### Method 1: Via Framer Package Manager

1. Open your Framer project
2. Click on the "+" icon in the Assets panel
3. Search for "AI Index"
4. Click "Install"

### Method 2: Manual Installation

1. **Download the plugin**:
   ```bash
   git clone https://github.com/yourusername/ai-index.git
   cd ai-index/packages/framer-plugin
   npm install
   npm run build
   ```

2. **Add to Framer**:
   - In Framer, go to your project
   - Click Assets > Code
   - Click "New from NPM"
   - Enter: `@iaindex/framer-plugin`

## Usage

### Basic Setup

1. **Add the component** to your site:
   - Open your Framer project
   - Add the "AI Index" component from the Assets panel
   - Place it on your main layout or master page (it's invisible)

2. **Configure the component**:
   - Select the AI Index component
   - In the Properties panel, configure:
     - **Enabled**: Toggle to activate/deactivate
     - **Publisher ID**: Your site's unique identifier (defaults to domain)
     - **Site Name**: Your site's name
     - **Description**: Brief description of your site
     - **Webhook URL**: Optional URL to receive AI access notifications

3. **That's it!** The AI Index is now active on your site.

### Advanced Configuration

#### Custom Metadata

Add custom metadata in JSON format:

```json
{
  "industry": "technology",
  "features": ["blog", "portfolio", "shop"],
  "contact": "hello@example.com"
}
```

#### Webhook Integration

To receive notifications when AI assistants access your content:

1. Set up a webhook endpoint (see example below)
2. Enter the webhook URL in the component properties
3. Enable "Auto Generate"

Example webhook endpoint:

```javascript
// Express.js example
app.post('/api/aiindex/access', async (req, res) => {
  const { llm_provider, content_accessed, timestamp } = req.body;

  // Log the access
  console.log('AI Access:', {
    provider: llm_provider,
    pages: content_accessed,
    time: timestamp
  });

  // Store in database, send analytics, etc.

  res.json({ success: true });
});
```

#### Component Placement

Best practices:
- Place on your **master page** or **main layout** to ensure it loads on all pages
- Only use **one instance** per site
- The component is invisible and won't affect your design

## How It Works

1. **Page Discovery**: The component scans your site's navigation and extracts all pages
2. **Index Generation**: Creates a structured JSON with page metadata
3. **Injection**: Adds the index to the page `<head>` as a `<script type="application/json">`
4. **AI Access**: AI assistants can read the metadata and understand your site structure

### Generated AI Index Structure

```json
{
  "version": "1.0",
  "publisher": {
    "id": "example.com",
    "name": "My Awesome Site",
    "description": "A portfolio and blog",
    "domain": "example.com",
    "type": "website",
    "platform": "framer"
  },
  "content": {
    "pages": [
      {
        "id": "home",
        "title": "Home",
        "description": "Welcome to my site",
        "url": "https://example.com/",
        "path": "/",
        "published_at": "2025-01-15T10:30:00Z"
      }
    ]
  },
  "metadata": {
    "generated_at": "2025-01-15T10:30:00Z",
    "total_pages": 5
  },
  "access": {
    "webhook_url": "https://api.example.com/aiindex/access",
    "verification_required": true
  }
}
```

## Development

### Building the Plugin

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Watch mode for development
npm run watch
```

### File Structure

```
framer-plugin/
├── src/
│   ├── AIIndex.tsx       # Main component
│   └── index.tsx         # Exports
├── framer.json           # Plugin manifest
├── package.json
├── tsconfig.json
└── README.md
```

## API Reference

### Component Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable AI Index generation |
| `publisherId` | string | `window.location.hostname` | Unique identifier for your site |
| `siteName` | string | `document.title` | Name of your site |
| `siteDescription` | string | `""` | Brief description |
| `webhookUrl` | string | `""` | URL to receive AI access notifications |
| `autoGenerate` | boolean | `true` | Auto-generate on page load |
| `customMetadata` | string | `{}` | Custom metadata as JSON string |

## Webhooks

### AI Access Webhook

When an AI assistant accesses your content, you'll receive:

```json
{
  "llm_provider": "openai-chatgpt",
  "content_accessed": ["/", "/blog", "/about"],
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {
    "user_query": "Tell me about this site",
    "response_included": true
  }
}
```

## Troubleshooting

### AI Index not appearing

- Check that the component is placed on a page that loads globally (master/layout)
- Ensure "Enabled" is set to `true`
- Check browser console for errors
- Verify the component is the latest version

### Pages not discovered

- Ensure pages are linked in navigation
- Check that links use relative paths (`/about` not `https://example.com/about`)
- Try adding pages manually via custom metadata

### Webhook not receiving data

- Verify the webhook URL is publicly accessible
- Check that "Auto Generate" is enabled
- Test the webhook endpoint with curl or Postman
- Review server logs for errors

## Examples

### E-commerce Site

```tsx
<AIIndex
  enabled={true}
  publisherId="myshop.com"
  siteName="My Shop"
  siteDescription="Premium handcrafted goods"
  customMetadata='{"type":"ecommerce","products":["furniture","decor"]}'
  webhookUrl="https://api.myshop.com/ai-access"
/>
```

### Portfolio Site

```tsx
<AIIndex
  enabled={true}
  publisherId="janedoe.com"
  siteName="Jane Doe - Designer"
  siteDescription="Product designer specializing in mobile apps"
  customMetadata='{"skills":["UI","UX","Prototyping"],"contact":"jane@example.com"}'
/>
```

### Blog

```tsx
<AIIndex
  enabled={true}
  publisherId="techblog.com"
  siteName="Tech Insights"
  siteDescription="Latest in web development and AI"
  customMetadata='{"category":"technology","topics":["AI","web","mobile"]}'
  webhookUrl="https://analytics.techblog.com/ai-webhook"
/>
```

## Support

- **Documentation**: [Full docs](https://docs.example.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-index/issues)
- **Discord**: [Join our community](https://discord.gg/example)
- **Email**: support@example.com

## License

MIT

## Credits

Built with love for the Framer community.
