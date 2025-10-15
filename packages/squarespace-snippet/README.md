# AI Index Extension for Squarespace

Make your Squarespace website discoverable by AI search engines like ChatGPT, Perplexity, and Claude. This extension automatically generates and publishes an AI-readable index of your site content.

## Features

- **Automatic Content Indexing**: Automatically indexes pages, blog posts, and products
- **Client-Side Generation**: No server required - works entirely in the browser
- **Real-time Updates**: Auto-generates every 24 hours
- **Configuration UI**: Beautiful HTML interface for easy setup
- **API Integration**: Publishes to AI Index API
- **Verification Badge**: Show visitors your site is AI-indexed
- **localStorage Persistence**: Settings and data persist across sessions
- **Multiple Content Types**: Supports pages, blog posts, and store products

## Quick Start

### 1. Installation

See detailed instructions in [install-guide.md](./install-guide.md)

**Quick steps:**

1. Add `aiindex-squarespace.js` to **Settings > Advanced > Code Injection > Header**
2. Add `styles.css` to **Design > Custom CSS**
3. Create a config page using `config.html` (optional)
4. Configure your API key and settings
5. Generate and publish your AI Index

### 2. Get API Key

Sign up at [aiindex.com](https://aiindex.com) to get your API key.

### 3. Configure

Use the configuration page or browser console:

```javascript
window.AIIndex.setConfig({
  apiKey: 'your-api-key-here',
  autoPublish: true,
  includePages: true,
  includeBlog: true,
  includeProducts: false
});
```

### 4. Generate and Publish

```javascript
await window.AIIndex.generate();
await window.AIIndex.publish();
```

## Files Included

- **aiindex-squarespace.js** - Main script that handles generation and publishing
- **config.html** - Configuration interface with dashboard
- **styles.css** - Styles for verification badge and UI components
- **install-guide.md** - Detailed installation instructions
- **README.md** - This file

## How It Works

### Content Discovery

The extension uses multiple methods to discover your content:

1. **Navigation Parsing**: Extracts links from your site's navigation
2. **Sitemap.xml**: Fetches and parses your sitemap
3. **Blog JSON API**: Uses `/blog?format=json` to get blog posts
4. **Commerce API**: Fetches products from `/api/commerce/products`

### Data Storage

All data is stored in browser localStorage:
- Configuration settings
- Generated AI Index JSON
- Last generation timestamp

### Automatic Updates

The script automatically regenerates the AI Index every 24 hours when someone visits your homepage. You can also trigger manual updates at any time.

### Publishing

The generated AI Index is published to the AI Index API, making it available to AI search engines like ChatGPT, Perplexity, and Claude.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | String | Required | Your AI Index API key |
| `webhookUrl` | String | Optional | URL to receive update notifications |
| `autoPublish` | Boolean | `true` | Auto-publish on regeneration |
| `includePages` | Boolean | `true` | Include static pages in index |
| `includeBlog` | Boolean | `true` | Include blog posts in index |
| `includeProducts` | Boolean | `false` | Include store products in index |

## API Reference

### window.AIIndex.generate()

Generates the AI Index from your site content.

```javascript
const aiIndex = await window.AIIndex.generate();
console.log(`Generated ${aiIndex.pages.length} pages`);
```

**Returns:** Promise<Object> - The generated AI Index data

### window.AIIndex.publish()

Publishes the AI Index to the API.

```javascript
const result = await window.AIIndex.publish();
console.log('Published successfully');
```

**Returns:** Promise<Object> - API response

### window.AIIndex.getData()

Retrieves the stored AI Index data.

```javascript
const data = window.AIIndex.getData();
if (data) {
  console.log(`${data.pages.length} pages indexed`);
}
```

**Returns:** Object | null - The stored AI Index data or null

### window.AIIndex.getConfig()

Gets the current configuration.

```javascript
const config = window.AIIndex.getConfig();
console.log(config.apiKey);
```

**Returns:** Object - Current configuration

### window.AIIndex.setConfig(config)

Updates configuration settings.

```javascript
window.AIIndex.setConfig({
  apiKey: 'new-key',
  autoPublish: false
});
```

**Parameters:**
- `config` (Object) - Configuration object with keys to update

### window.AIIndex.verifyApiKey(apiKey)

Verifies an API key.

```javascript
const result = await window.AIIndex.verifyApiKey('your-key');
console.log(result.valid); // true or false
```

**Parameters:**
- `apiKey` (String) - API key to verify

**Returns:** Promise<Object> - Verification result with `valid` and `status` properties

## Generated JSON Format

The extension generates JSON in this format:

```json
{
  "version": "1.0",
  "metadata": {
    "site_name": "Your Site Name",
    "base_url": "https://yoursite.com",
    "last_updated": "2025-10-13T12:00:00Z",
    "language": "en",
    "contact": {
      "email": "contact@yoursite.com"
    }
  },
  "pages": [
    {
      "url": "https://yoursite.com/page",
      "title": "Page Title",
      "description": "Page description",
      "last_modified": "2025-10-13T12:00:00Z",
      "content_type": "page",
      "keywords": []
    }
  ]
}
```

## Verification Badge

Add this HTML to display the verification badge:

```html
<div class="ai-index-badge">
  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
  </svg>
  <span>AI Index Verified</span>
</div>
```

### Badge Variations

Add these classes for different styles:

- `badge-light` - Light background
- `badge-dark` - Dark background
- `badge-success` - Green background
- `badge-minimal` - Minimal border style
- `badge-pill` - Rounded pill shape
- `badge-animated` - Pulsing animation

## Webhook Notifications

Configure a webhook URL to receive notifications:

```javascript
window.AIIndex.setConfig({
  webhookUrl: 'https://yoursite.com/webhook'
});
```

Webhook payload:

```json
{
  "event": "ai_index_updated",
  "timestamp": "2025-10-13T12:00:00Z",
  "page_count": 42
}
```

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires:
- localStorage support
- Fetch API
- Promises/async-await
- ES6 features

## Limitations

### Squarespace Limitations

1. **No Server-Side Code**: Squarespace doesn't support custom server-side endpoints
2. **Client-Side Only**: All processing happens in the browser
3. **localStorage Dependent**: Requires browser storage
4. **API Access**: Some features require Business plan or higher
5. **Rate Limiting**: Frequent API calls may be rate-limited

### Workarounds

For high-traffic sites:
- Host AI Index JSON externally
- Use CDN for caching
- Implement scheduled external generation

## Troubleshooting

### Common Issues

**Script not loading:**
- Verify script is in Header (not Footer)
- Check for JavaScript errors in console
- Clear browser cache

**API key invalid:**
- Verify key from aiindex.com
- Check for extra spaces
- Try regenerating key

**No pages indexed:**
- Ensure pages are published
- Check content options are enabled
- Verify sitemap.xml is accessible

**Blog posts missing:**
- Confirm blog exists
- Check posts are published
- Test `/blog?format=json` endpoint

See [install-guide.md](./install-guide.md) for detailed troubleshooting.

## Best Practices

1. **Security**: Keep your API key secure; password-protect the config page
2. **Performance**: Let auto-publish handle updates automatically
3. **Testing**: Generate a new index after major site changes
4. **Monitoring**: Use webhooks to track update events
5. **Backup**: Export your AI Index JSON periodically

## Requirements

- Squarespace website (any plan, Business+ recommended)
- AI Index API key from [aiindex.com](https://aiindex.com)
- Code Injection access (Business plan or higher)
- Modern browser with JavaScript enabled

## Support

- **Installation Guide**: [install-guide.md](./install-guide.md)
- **Documentation**: [aiindex.com/docs/squarespace](https://aiindex.com/docs/squarespace)
- **Support Email**: support@aiindex.com
- **GitHub**: [github.com/claimtec/iaindex](https://github.com/claimtec/iaindex)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on Squarespace
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Changelog

### Version 1.0.0
- Initial release
- Automatic content indexing
- Configuration UI
- API integration
- Verification badge
- localStorage persistence
- Multiple content type support
- Webhook notifications

## Roadmap

- [ ] Squarespace Extensions API integration
- [ ] Advanced analytics dashboard
- [ ] Automatic sitemap updates
- [ ] Multi-language support
- [ ] Custom content filters
- [ ] Scheduled generation options
- [ ] Export/import functionality

## Credits

Built by ClaimTec for the AI Index project.

Special thanks to:
- Squarespace for their platform and APIs
- The AI search engine community
- Open-source contributors

---

**Note**: This is an unofficial third-party extension and is not affiliated with Squarespace, Inc.
