# IAIndex Webflow Snippet

Standalone JavaScript snippet that automatically indexes Webflow pages and tracks AI access with cryptographic receipts.

## Features

- **Automatic Page Indexing** - Extracts metadata from Webflow pages
- **AI Access Tracking** - Detects AI bot visits and generates receipts
- **Zero Configuration** - Works out of the box with sensible defaults
- **Lightweight** - ~5KB minified, non-blocking execution
- **Customizable** - Configure selectors for your Webflow structure
- **Debug Mode** - Built-in logging for troubleshooting

## Quick Start

### 1. Get Your API Key

Sign up at [IAIndex Dashboard](https://aiindex.com/dashboard) and obtain your API key.

### 2. Add to Webflow

1. Open your Webflow project
2. Go to **Project Settings** > **Custom Code**
3. Paste the snippet in **Head Code**
4. Configure the settings (see below)
5. Publish your site

### 3. Configure Settings

Edit these lines in the snippet:

```javascript
const IAINDEX_CONFIG = {
  // Your IAIndex API key
  apiKey: 'YOUR_API_KEY_HERE',  // ← Add your key here

  // Your domain (auto-detected if not set)
  domain: window.location.hostname,

  // Publisher information
  publisher: {
    name: 'Your Site Name',      // ← Your site name
    contact: 'contact@yourdomain.com'  // ← Your contact email
  },

  // ... rest of config
};
```

### 4. Verify Installation

Open your published site and check the browser console:

```
[IAIndex] IAIndex Webflow Snippet initialized
[IAIndex] Metadata injected successfully
```

Also inspect the page source - you should see:

```html
<script type="application/ld+json" data-iaindex="true">
{
  "publisher": {
    "domain": "yoursite.com",
    ...
  }
}
</script>
```

## What It Does

### Automatic Metadata Extraction

The snippet automatically extracts:

- **Page Title** - From H1 or title tag
- **Description** - From meta description or first paragraph
- **Author** - From author elements or meta tags
- **Publish Date** - From time elements or meta tags
- **Tags/Categories** - From tag/category elements
- **Content Type** - Auto-detected (blog, article, page, etc.)
- **Word Count** - Estimated from main content
- **Language** - From HTML lang attribute

### AI Access Tracking

Detects access from AI bots:
- GPTBot (OpenAI)
- ClaudeBot (Anthropic)
- BingBot
- Perplexity
- Other AI crawlers

When detected:
1. Generates unique receipt ID
2. Creates cryptographic signature
3. Sends receipt to IAIndex API
4. Logs success/failure (in debug mode)

### Structured Data Injection

Adds JSON-LD structured data to page:

```html
<script type="application/ld+json" data-iaindex="true">
{
  "publisher": {...},
  "pages": [{
    "url": "https://yoursite.com/article",
    "title": "Article Title",
    "description": "Article description",
    ...
  }],
  "version": "1.0"
}
</script>
```

## Configuration Options

### Basic Configuration

```javascript
const IAINDEX_CONFIG = {
  apiKey: 'YOUR_API_KEY_HERE',
  domain: window.location.hostname,
  publisher: {
    name: 'Your Site Name',
    contact: 'contact@yourdomain.com'
  }
};
```

### Feature Flags

```javascript
features: {
  autoIndex: true,        // Automatically index pages
  trackAccess: true,      // Track AI bot access
  generateReceipts: true, // Generate receipts
  debug: false            // Enable console logging
}
```

### Custom Selectors

Customize for your Webflow structure:

```javascript
selectors: {
  title: 'h1, .page-title, .post-title',
  description: '.page-description, .post-excerpt',
  author: '.author-name, .post-author',
  publishDate: '.publish-date, .post-date, time[datetime]',
  content: 'article, .main-content, .post-content',
  tags: '.tag, .category, .post-tag'
}
```

## Advanced Usage

### Manual Control

The snippet exposes a global API:

```javascript
// Access current configuration
console.log(window.IAIndex.config);

// Extract current page metadata
const metadata = window.IAIndex.extractMetadata();

// Generate AI-Index for current page
const index = window.IAIndex.generateIndex();

// Manually send receipt
window.IAIndex.sendReceipt();

// Check version
console.log(window.IAIndex.version);
```

### Conditional Indexing

Only index certain pages:

```javascript
// Add after config
if (!window.location.pathname.startsWith('/blog/')) {
  IAINDEX_CONFIG.features.autoIndex = false;
}
```

### Custom Metadata

Add custom data to receipts:

```javascript
// Modify generateReceipt() function
metadata: {
  user_agent: navigator.userAgent,
  referrer: document.referrer,
  page_title: document.title,
  generator: 'webflow-snippet',
  // Add custom fields
  page_category: document.querySelector('.category')?.textContent,
  custom_field: 'custom_value'
}
```

### Event Tracking

Track when receipts are sent:

```javascript
// Add after sendReceipt()
window.dispatchEvent(new CustomEvent('iaindex:receipt-sent', {
  detail: { receiptId, status: 'success' }
}));

// Listen for events
window.addEventListener('iaindex:receipt-sent', (event) => {
  console.log('Receipt sent:', event.detail);
  // Send to your analytics
});
```

## Content Type Detection

The snippet automatically detects content types based on URL patterns:

| Pattern | Content Type |
|---------|--------------|
| `/blog/`, `/post/` | blog-post |
| `/article/` | article |
| `/news/` | news |
| `/product/` | product |
| `/` (root) | homepage |
| Has `<article>` tag | article |
| Other | page |

Customize in `detectContentType()` function.

## AI Bot Detection

Currently detects these user agents:

- `gptbot` - OpenAI GPT
- `chatgpt` - ChatGPT
- `claudebot` - Claude
- `anthropic` - Anthropic bots
- `bingbot` - Bing AI
- `googlebot-ai` - Google AI
- `perplexitybot` - Perplexity

Add more in `detectAIAccess()` function:

```javascript
const aiBots = [
  'gptbot',
  'claudebot',
  'your-custom-bot'  // Add here
];
```

## Debugging

### Enable Debug Mode

```javascript
features: {
  debug: true  // Enable detailed logging
}
```

### Debug Output

```
[IAIndex] IAIndex Webflow Snippet initialized
[IAIndex] Configuration: {...}
[IAIndex] Extracting page metadata...
[IAIndex] Extracted metadata: {...}
[IAIndex] Generating AI-Index data...
[IAIndex] Injecting IAIndex metadata...
[IAIndex] Metadata injected successfully
[IAIndex] AI access detected, generating receipt...
[IAIndex] Sending receipt to IAIndex...
[IAIndex] Receipt sent successfully: {...}
```

### Common Issues

#### API Key Not Set

**Error:** `API key not configured`

**Solution:** Replace `YOUR_API_KEY_HERE` with your actual API key

#### No Metadata Detected

**Issue:** Empty title, description, etc.

**Solution:**
- Check your Webflow structure matches selectors
- Customize selectors in config
- Use debug mode to see what's detected

#### Receipts Not Sending

**Issue:** No receipts in IAIndex dashboard

**Solution:**
- Enable debug mode to see errors
- Check browser console for network errors
- Verify domain is verified in IAIndex
- Check API key is valid

#### CORS Errors

**Issue:** `CORS policy blocked`

**Solution:** This shouldn't happen with IAIndex API, but if it does:
- Verify you're using the correct API endpoint
- Check API key is set correctly

## Performance

### Load Impact

- **Size:** ~5KB minified (~15KB unminified)
- **Load Time:** <10ms
- **Execution:** Non-blocking, runs after DOM ready
- **Network:** 1 request per AI bot visit (receipts only)

### Optimization Tips

1. **Disable on non-content pages:**
   ```javascript
   if (window.location.pathname.includes('/admin/')) {
     return; // Skip admin pages
   }
   ```

2. **Lazy load for better performance:**
   ```javascript
   // Load snippet after page is interactive
   if (document.readyState === 'complete') {
     init();
   } else {
     window.addEventListener('load', init);
   }
   ```

3. **Cache metadata:**
   ```javascript
   // Store in sessionStorage to avoid re-extraction
   const cached = sessionStorage.getItem('iaindex-metadata');
   if (cached) return JSON.parse(cached);
   ```

## Security Considerations

### Client-Side Signatures

The snippet uses client-side SHA-256 hashing for signatures. For production:

1. **Server-Side Signing (Recommended):**
   - Implement signing endpoint on your backend
   - Call it from the snippet
   - Use proper HMAC with secret key

2. **API Key Protection:**
   - API keys in client code are visible
   - Use read-only or limited-scope keys
   - Consider server-side integration for sensitive sites

### Best Practice

```javascript
// Instead of client-side signing:
async function generateSignature(receiptId, timestamp) {
  const response = await fetch('https://yoursite.com/api/sign-receipt', {
    method: 'POST',
    body: JSON.stringify({ receiptId, timestamp, url: window.location.href })
  });
  const { signature } = await response.json();
  return signature;
}
```

## Webflow Collection Pages

For Webflow CMS collection pages, the snippet automatically extracts:

- Collection item title
- Rich text content
- Author (if set in CMS)
- Publish date (if set in CMS)
- Categories/tags

Ensure your collection uses standard Webflow classes.

## Integration with Other Services

### Google Analytics

```javascript
// Track receipt sends
window.addEventListener('iaindex:receipt-sent', (event) => {
  gtag('event', 'iaindex_receipt', {
    receipt_id: event.detail.receiptId
  });
});
```

### Segment

```javascript
window.addEventListener('iaindex:receipt-sent', (event) => {
  analytics.track('IAIndex Receipt Sent', {
    receiptId: event.detail.receiptId,
    url: window.location.href
  });
});
```

## Migration

If you're using the old snippet version:

1. Replace entire snippet with new version
2. Update configuration keys (if changed)
3. Test on staging site first
4. Publish to production

## Support

### Documentation
- [IAIndex Docs](https://docs.iaindex.org)
- [Webflow Integration Guide](https://docs.iaindex.org/integrations/webflow)

### Help
- GitHub Issues: [github.com/iaindex/iaindex](https://github.com/iaindex/iaindex)
- Discord: [discord.gg/iaindex](https://discord.gg/iaindex)
- Email: support@iaindex.com

## Changelog

### v1.0.0 (2025-01-15)
- Initial release
- Automatic metadata extraction
- AI bot detection
- Receipt generation
- Debug mode

## License

MIT

## Credits

Built by the IAIndex team. Contributions welcome!
