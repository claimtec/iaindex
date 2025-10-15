# AIIndex Webflow Integration

Seamlessly integrate AIIndex with your Webflow site to automatically generate and maintain your `/ai-index.json` file.

## Features

- **Automatic AI Index Generation**: Auto-generates `/ai-index.json` from your Webflow CMS collections
- **Real-time Synchronization**: Syncs content updates to AIIndex API automatically
- **Domain Verification**: Built-in domain verification workflow
- **Webhook Support**: Get notified when your AI Index is updated
- **Verification Badge**: Display an AIIndex verification badge on your site
- **Visual Configuration UI**: Easy-to-use HTML configuration panel
- **CMS Integration**: Seamlessly works with Webflow CMS collections

## Installation

### Method 1: Custom Code (Recommended)

1. **Copy the Configuration UI**
   - Open `config.html` in your browser
   - Or host it on your own server for team access

2. **Configure Your Settings**
   - Enter your AIIndex API key (get one at [aiindex.org/dashboard](https://aiindex.org))
   - Enter your Webflow domain
   - Verify your domain
   - Configure webhook URL (optional)
   - Customize badge settings

3. **Add to Webflow**
   - Go to Webflow Site Settings > Custom Code
   - Add the generated embed code to **Footer Code** section
   - Publish your site

### Method 2: Manual Installation

Add this code to your Webflow site's footer:

```html
<script src="https://cdn.aiindex.org/webflow/snippet.js"></script>
<script>
  window.aiIndexConfig = {
    apiKey: 'your-api-key-here',
    domain: 'yoursite.com',
    webhookUrl: 'https://yoursite.com/webhooks/aiindex', // Optional
    badgeEnabled: true,
    autoSync: true
  };
  AIIndexWebflow.init(window.aiIndexConfig);
</script>
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | *required* | Your AIIndex API key |
| `domain` | string | *auto-detected* | Your site domain |
| `apiEndpoint` | string | `https://api.aiindex.org/v1` | AIIndex API endpoint |
| `webhookUrl` | string | `null` | Webhook URL for notifications |
| `badgeEnabled` | boolean | `true` | Show verification badge |
| `autoSync` | boolean | `true` | Auto-sync on page load |

## Usage

### Automatic Sync

Once installed, the snippet will automatically:
1. Fetch all CMS collections from your Webflow site
2. Transform the data into AIIndex format
3. Sync to AIIndex API
4. Display verification badge (if enabled)

### Manual Sync

You can trigger a manual sync from anywhere in your site:

```javascript
// Trigger manual sync
AIIndexWebflow.manualSync();

// Or via custom event
window.dispatchEvent(new Event('aiindex:sync'));
```

### Check Sync Status

```javascript
AIIndexWebflow.getStatus().then(status => {
  console.log('Last sync:', status.lastSync);
  console.log('Total pages:', status.totalPages);
});
```

### Domain Verification

```javascript
AIIndexWebflow.verifyDomain().then(result => {
  console.log('Domain verified:', result);
});
```

## Webhook Integration

Configure a webhook to receive notifications when your AI Index is updated:

```json
{
  "event": "aiindex.sync.complete",
  "timestamp": "2025-10-13T10:30:00Z",
  "data": {
    "domain": "yoursite.com",
    "totalPages": 42,
    "lastSync": "2025-10-13T10:30:00Z"
  }
}
```

## Badge Customization

### Position

Add a `data-aiindex-badge` attribute to any element to use it as the badge container:

```html
<div data-aiindex-badge></div>
```

### Custom Styles

The badge uses the ID `#aiindex-badge`. Override styles in your Webflow custom CSS:

```css
#aiindex-badge {
  bottom: 10px !important;
  left: 10px !important;
  right: auto !important;
}
```

### Badge Variants

Apply classes to customize badge appearance:

```html
<div data-aiindex-badge class="compact light"></div>
```

Available classes:
- `compact` - Smaller badge
- `light` - Light theme
- `purple`, `blue`, `green` - Colored variants
- `top-left`, `top-right`, `bottom-left` - Position variants
- `pulse` - Animated pulse effect

## Data Transformation

The snippet automatically transforms Webflow CMS data to AIIndex format:

**Webflow CMS Item:**
```json
{
  "name": "My Blog Post",
  "slug": "/blog/my-post",
  "content": "Post content...",
  "published-on": "2025-10-13",
  "author": { "name": "John Doe" },
  "category": { "name": "Technology" }
}
```

**AIIndex Format:**
```json
{
  "url": "https://yoursite.com/blog/my-post",
  "title": "My Blog Post",
  "content": "Post content...",
  "metadata": {
    "published": "2025-10-13",
    "author": "John Doe",
    "category": "Technology"
  },
  "access": {
    "crawlable": true,
    "aiTrainable": true
  }
}
```

## Webflow CMS Collections

The integration works with any Webflow CMS collection:

- Blog posts
- Product catalogs
- Portfolio items
- Team members
- Case studies
- Custom collections

All collection fields are automatically mapped to AIIndex format.

## Troubleshooting

### Badge not appearing

1. Check that `badgeEnabled: true` in your config
2. Verify the snippet is loaded (check browser console)
3. Make sure your site is published

### Sync not working

1. Verify your API key is correct
2. Check browser console for errors
3. Ensure your domain is verified
4. Test API connection using the config UI

### CMS data not syncing

1. Make sure your CMS collections are published
2. Check collection visibility settings
3. Verify API permissions in your AIIndex dashboard

## Security

- API keys are stored in `localStorage` (client-side only)
- Use environment variables for production deployments
- Never commit API keys to version control
- Rotate API keys regularly

## Support

- Documentation: [docs.aiindex.org/webflow](https://docs.aiindex.org/webflow)
- Dashboard: [aiindex.org/dashboard](https://aiindex.org/dashboard)
- Issues: [github.com/aiindex/webflow-integration](https://github.com/aiindex/webflow-integration)
- Email: support@aiindex.org

## License

MIT License - See LICENSE file for details

## Version

Current version: 1.0.0

## Changelog

### 1.0.0 (2025-10-13)
- Initial release
- Automatic CMS sync
- Domain verification
- Webhook support
- Configuration UI
- Verification badge
