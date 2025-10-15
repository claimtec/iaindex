# Wix & Squarespace Integration Summary

This document provides a comprehensive overview of the AI Index integrations for Wix and Squarespace platforms.

## Overview

Two complete platform integrations have been built to enable websites to publish their content to AI search engines like ChatGPT, Perplexity, and Claude.

---

## Wix Plugin

**Location:** `/packages/wix-plugin/`

### Architecture

The Wix plugin leverages Wix Velo (formerly Corvid) to provide server-side functionality with a native dashboard integration.

### Files Created

```
wix-plugin/
├── backend/
│   └── aiindex.jsw                 # Backend module with HTTP functions
├── public/
│   └── pages/
│       └── aiindex.js              # Public page code and frontend API
├── dashboard/
│   └── panel.html                  # Dashboard panel interface
├── package.json                    # NPM package configuration
├── wix.config.json                 # Wix plugin configuration
└── README.md                       # Complete documentation
```

### Key Features

#### 1. Backend Module (`backend/aiindex.jsw`)
- **Content Generation**: Automatically indexes pages, blog posts, and products
- **HTTP Function**: Serves `/ai-index.json` endpoint
- **API Integration**: Publishes to AI Index API
- **Data Hooks**: Triggers on content changes
- **Configuration Management**: Stores settings in Wix Data Collections
- **Analytics**: Fetches and displays AI search metrics
- **Webhook Support**: Notifies external services on updates

**Key Functions:**
- `generateAIIndex()` - Creates AI Index from site content
- `publishToAPI()` - Publishes to AI Index API
- `saveConfig()` - Saves configuration settings
- `getAnalytics()` - Retrieves analytics data
- `verifyApiKey()` - Validates API credentials
- `get_aiindex()` - HTTP Function handler
- `handleContentChange()` - Webhook handler for data changes

#### 2. Public Page Code (`public/pages/aiindex.js`)
- **Verification Badge**: Displays AI Index verification status
- **Status Display**: Shows current index status and stats
- **Manual Publishing**: Provides UI for manual publish actions
- **Public API**: Exports functions for use in other pages

**Exported Functions:**
- `getAIIndexUrl()` - Returns the AI Index endpoint URL
- `isAIIndexActive()` - Checks if AI Index is configured
- `getAIIndexData()` - Fetches current AI Index data

#### 3. Dashboard Panel (`dashboard/panel.html`)
- **Status Overview**: Real-time status cards with metrics
- **Configuration Form**: API key, webhook, content options
- **Actions Panel**: Generate, publish, preview, and analytics buttons
- **JSON Preview**: Live preview of generated AI Index
- **Responsive Design**: Modern gradient UI with smooth animations

**Features:**
- API key management with verification
- Webhook URL configuration
- Content type selection (pages, blog, products)
- Auto-publish toggle
- One-click publishing
- Analytics dashboard integration

#### 4. Configuration (`wix.config.json`)
- Plugin metadata and permissions
- Dashboard integration settings
- HTTP Functions routing
- Secret storage configuration

### Setup Instructions for Wix

#### Quick Setup
1. **Enable Velo**: Go to Settings > Custom Code > Enable Velo
2. **Copy Files**: Upload all files to your Wix site
3. **Install Dependencies**: Add required packages to package.json
4. **Create Collection**: Create `AIIndexConfig` collection
5. **Set API Key**: Add `aiIndexApiKey` to Secrets Manager
6. **Configure Dashboard**: Enable HTTP Functions

#### Data Collection Schema
Create a collection named `AIIndexConfig` with these fields:
- `webhookUrl` (Text)
- `autoPublish` (Boolean)
- `includePages` (Boolean)
- `includeBlog` (Boolean)
- `includeProducts` (Boolean)

#### Dependencies
```json
{
  "wix-fetch": "^1.0.0",
  "wix-data": "^1.0.0",
  "wix-secrets-backend": "^1.0.0"
}
```

#### API Endpoint
Once configured, your AI Index will be available at:
```
https://yoursite.com/_functions/ai-index.json
```

### Data Hooks for Auto-Publishing

Add these hooks to enable automatic publishing when content changes:

```javascript
import { handleContentChange } from 'backend/aiindex';

export function SitePages_afterUpdate(item, context) {
  return handleContentChange(item, context);
}

export function BlogPosts_afterUpdate(item, context) {
  return handleContentChange(item, context);
}

export function Products_afterUpdate(item, context) {
  return handleContentChange(item, context);
}
```

---

## Squarespace Extension

**Location:** `/packages/squarespace-snippet/`

### Architecture

The Squarespace extension is a client-side solution using Code Injection, as Squarespace doesn't support server-side custom code.

### Files Created

```
squarespace-snippet/
├── aiindex-squarespace.js          # Main JavaScript module
├── config.html                     # Configuration UI page
├── styles.css                      # Badge and UI styles
├── install-guide.md                # Detailed installation guide
└── README.md                       # Complete documentation
```

### Key Features

#### 1. Main Script (`aiindex-squarespace.js`)
- **Content Discovery**: Multiple methods to find site content
- **Auto-Generation**: Regenerates every 24 hours automatically
- **localStorage Storage**: Persists data and configuration
- **Public API**: `window.AIIndex` global object
- **Multiple Content Types**: Pages, blog posts, products

**Content Discovery Methods:**
1. Navigation parsing
2. Sitemap.xml parsing
3. Blog JSON API (`/blog?format=json`)
4. Commerce API (`/api/commerce/products`)

**Public API:**
```javascript
window.AIIndex.generate()        // Generate AI Index
window.AIIndex.publish()         // Publish to API
window.AIIndex.getData()         // Get stored data
window.AIIndex.getConfig()       // Get configuration
window.AIIndex.setConfig({})     // Update configuration
window.AIIndex.verifyApiKey()    // Verify API key
```

#### 2. Configuration UI (`config.html`)
- **Beautiful Dashboard**: Gradient design with status cards
- **Real-time Configuration**: Instant updates to localStorage
- **API Key Management**: Secure storage and verification
- **Content Options**: Toggle pages, blog, products
- **Actions Panel**: Generate and publish buttons
- **Badge Code**: Copy-paste verification badge HTML

**Features:**
- Status overview with metrics
- API key verification
- Content type toggles
- Manual generation/publishing
- Verification badge snippet
- Inline documentation

#### 3. Styles (`styles.css`)
- **Verification Badge**: Multiple style variations
- **Status Indicators**: Active, inactive, pending states
- **Loading Animations**: Smooth spinner and transitions
- **Responsive Design**: Mobile-friendly components
- **Badge Variations**: Light, dark, minimal, pill, animated

**Badge Classes:**
- `.ai-index-badge` - Default gradient badge
- `.badge-light` - Light background variant
- `.badge-dark` - Dark background variant
- `.badge-success` - Green success variant
- `.badge-minimal` - Minimal border style
- `.badge-pill` - Rounded pill shape
- `.badge-animated` - Pulsing animation

#### 4. Installation Guide (`install-guide.md`)
Comprehensive step-by-step installation instructions including:
- Prerequisites
- Code injection setup
- Configuration methods
- Troubleshooting guide
- Advanced configuration
- API reference
- Best practices

### Setup Instructions for Squarespace

#### Quick Setup
1. **Add Script**: Settings > Advanced > Code Injection > Header
2. **Add Styles**: Design > Custom CSS
3. **Create Config Page**: Add new page with `config.html` (optional)
4. **Configure**: Enter API key and set options
5. **Generate**: Click "Generate Index"
6. **Publish**: Click "Publish to API"

#### Code Injection
Add to **Header** section:
```html
<script>
  // Paste contents of aiindex-squarespace.js here
</script>
```

#### Custom CSS
Add to **Design > Custom CSS**:
```css
/* Paste contents of styles.css here */
```

#### Browser Console Configuration
Alternative to config page:
```javascript
window.AIIndex.setConfig({
  apiKey: 'your-api-key',
  autoPublish: true,
  includePages: true,
  includeBlog: true,
  includeProducts: false
});

await window.AIIndex.generate();
await window.AIIndex.publish();
```

#### Verification Badge
Add this HTML to any page:
```html
<div class="ai-index-badge">
  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
  </svg>
  <span>AI Index Verified</span>
</div>
```

---

## Feature Comparison

| Feature | Wix Plugin | Squarespace Extension |
|---------|------------|----------------------|
| **Server-Side** | Yes (Velo) | No (Client-side) |
| **HTTP Endpoint** | `/_functions/ai-index.json` | Client-served via JS |
| **Dashboard Integration** | Native Wix Dashboard | HTML Config Page |
| **Auto-Publishing** | Data Hooks | 24-hour timer |
| **Configuration Storage** | Wix Data Collections | localStorage |
| **API Key Storage** | Secrets Manager | localStorage |
| **Content Types** | Pages, Blog, Products | Pages, Blog, Products |
| **Analytics** | Native integration | API-based |
| **Webhook Support** | Yes | Yes |
| **Real-time Updates** | Yes (via hooks) | No (24hr interval) |
| **Installation Complexity** | Medium | Low |

---

## Common Features

Both integrations provide:

1. **Automatic Content Indexing**
   - Static pages
   - Blog posts
   - Store products

2. **AI Index API Integration**
   - Publishing to API
   - Analytics retrieval
   - API key verification

3. **Configuration Management**
   - API key setup
   - Webhook URLs
   - Content type selection
   - Auto-publish toggle

4. **Verification Badge**
   - HTML snippet
   - Multiple style variations
   - Responsive design

5. **Documentation**
   - Comprehensive README
   - Installation guides
   - Troubleshooting
   - API reference

---

## JSON Format

Both integrations generate AI Index JSON in the same format:

```json
{
  "version": "1.0",
  "metadata": {
    "site_name": "Site Name",
    "base_url": "https://example.com",
    "last_updated": "2025-10-13T12:00:00Z",
    "language": "en",
    "contact": {
      "email": "contact@example.com"
    }
  },
  "pages": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "description": "Page description",
      "last_modified": "2025-10-13T12:00:00Z",
      "content_type": "page",
      "keywords": [],
      "author": "Author Name",
      "published_date": "2025-10-01T12:00:00Z"
    }
  ]
}
```

### Content Types

- `page` - Static pages
- `blog_post` - Blog articles
- `product` - Store products

---

## Platform Requirements

### Wix Requirements
- Wix website (any plan)
- Velo Development Mode enabled (free)
- Code injection access
- Secrets Manager access
- Wix Data Collections

### Squarespace Requirements
- Squarespace website (any plan)
- Business plan or higher (for full Code Injection)
- Modern browser with localStorage
- JavaScript enabled

---

## API Key Setup

Both integrations require an API key from AI Index:

1. Sign up at [aiindex.com](https://aiindex.com)
2. Generate API key in dashboard
3. Configure in plugin/extension:
   - **Wix**: Add to Secrets Manager as `aiIndexApiKey`
   - **Squarespace**: Enter in config UI or console

---

## Webhook Notifications

Both support webhook notifications with this payload:

```json
{
  "event": "content_updated" | "ai_index_updated",
  "timestamp": "2025-10-13T12:00:00Z",
  "page_count": 42,
  "item_id": "optional-item-id",
  "collection": "optional-collection-name"
}
```

Configure webhook URLs in the respective settings.

---

## Troubleshooting

### Common Issues

#### API Key Invalid
- Verify key from aiindex.com
- Check for extra spaces
- Ensure key hasn't expired
- Try regenerating key

#### No Content Indexed
- Check that content is published
- Verify content type toggles are enabled
- Check browser console for errors
- Ensure proper permissions

#### Script Not Loading (Squarespace)
- Verify script is in Header section
- Clear browser cache
- Check for JavaScript errors
- Ensure proper script tags

#### HTTP Function Not Working (Wix)
- Verify HTTP Functions are enabled
- Check function name matches config
- Test endpoint in browser
- Review Wix Console logs

### Platform-Specific Issues

**Wix:**
- Enable Velo if not already
- Check Secrets Manager for API key
- Verify Data Collection exists
- Review data hook configurations

**Squarespace:**
- Ensure Business plan for full access
- Check localStorage is enabled
- Verify not in Incognito mode
- Test individual API endpoints

---

## Best Practices

### Security
1. Never share API keys publicly
2. Password-protect config pages
3. Use HTTPS for webhooks
4. Regularly rotate API keys

### Performance
1. Enable auto-publish for fresh content
2. Monitor generation times
3. Use webhooks for notifications
4. Cache when possible

### Maintenance
1. Update integrations regularly
2. Test after platform updates
3. Monitor analytics
4. Backup configurations

### Testing
1. Generate after major changes
2. Verify JSON format
3. Test webhook endpoints
4. Check analytics data

---

## Support & Resources

### Documentation
- **Wix**: `/packages/wix-plugin/README.md`
- **Squarespace**: `/packages/squarespace-snippet/README.md`
- **Installation**: Check respective README files

### Online Resources
- AI Index Docs: [aiindex.com/docs](https://aiindex.com/docs)
- Wix Guide: [aiindex.com/docs/wix](https://aiindex.com/docs/wix)
- Squarespace Guide: [aiindex.com/docs/squarespace](https://aiindex.com/docs/squarespace)

### Support Channels
- Email: support@aiindex.com
- GitHub: [github.com/claimtec/iaindex](https://github.com/claimtec/iaindex)
- Issues: [github.com/claimtec/iaindex/issues](https://github.com/claimtec/iaindex/issues)

---

## License

Both integrations are released under the MIT License.

---

## Credits

Built by **ClaimTec** for the AI Index project.

### Technologies Used
- **Wix Velo** - Backend framework
- **Squarespace APIs** - Content discovery
- **JavaScript ES6+** - Core functionality
- **HTML5/CSS3** - User interfaces
- **localStorage API** - Client-side storage
- **Fetch API** - HTTP communications

---

## Version History

### Version 1.0.0 (2025-10-13)
- Initial release of both integrations
- Full feature parity where applicable
- Comprehensive documentation
- Installation guides
- Troubleshooting resources

---

## Future Enhancements

### Planned Features
- [ ] Advanced analytics dashboards
- [ ] Multi-language support
- [ ] Custom content filters
- [ ] Scheduled generation
- [ ] Export/import functionality
- [ ] Enhanced error reporting
- [ ] Rate limiting handling
- [ ] CDN integration options

### Platform-Specific Roadmap

**Wix:**
- [ ] Wix Blocks integration
- [ ] Enhanced dashboard widgets
- [ ] Multi-site management
- [ ] Advanced data hooks

**Squarespace:**
- [ ] Squarespace Extensions API
- [ ] Server-side workarounds
- [ ] Enhanced product support
- [ ] Automatic update detection

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on both platforms
5. Submit a pull request

Please ensure:
- Code follows existing style
- Documentation is updated
- Tests pass (if applicable)
- Changes work on both platforms where relevant

---

## Acknowledgments

Special thanks to:
- Wix and Squarespace for their platforms
- The AI search engine community
- Open-source contributors
- Beta testers and early adopters

---

**Last Updated**: October 13, 2025
**Version**: 1.0.0
**Maintained by**: ClaimTec
