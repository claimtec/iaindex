# AI Index Plugin for Wix

Make your Wix website discoverable by AI search engines like ChatGPT, Perplexity, and Claude. This plugin automatically generates and publishes an AI-readable index of your site content.

## Features

- **Automatic Content Indexing**: Automatically indexes pages, blog posts, and products
- **Real-time Updates**: Auto-publish when content changes
- **Dashboard Integration**: Beautiful dashboard panel for easy management
- **Analytics**: Track AI search engine impressions and performance
- **HTTP Functions**: Serves `/ai-index.json` endpoint for AI crawlers
- **Verification Badge**: Show visitors your site is AI-indexed

## Installation

### 1. Add to Your Wix Site

1. Open your Wix site in the Editor
2. Go to **Settings** > **Custom Code**
3. Enable **Velo Development Mode**
4. Copy the plugin files to your site:
   - `backend/aiindex.jsw` - Backend module
   - `public/pages/aiindex.js` - Public page code
   - `dashboard/panel.html` - Dashboard panel

### 2. Install Dependencies

In your site's package.json, add:

```json
{
  "dependencies": {
    "wix-fetch": "^1.0.0",
    "wix-data": "^1.0.0",
    "wix-secrets-backend": "^1.0.0"
  }
}
```

### 3. Configure Data Collection

Create a new collection called `AIIndexConfig` with the following fields:

- `webhookUrl` (Text)
- `autoPublish` (Boolean)
- `includePages` (Boolean)
- `includeBlog` (Boolean)
- `includeProducts` (Boolean)

### 4. Set Up API Key

1. Get your API key from [aiindex.com](https://aiindex.com)
2. Go to **Settings** > **Secrets Manager**
3. Add a new secret named `aiIndexApiKey` with your API key

### 5. Enable HTTP Functions

1. Go to **Settings** > **Custom Code**
2. Enable **HTTP Functions**
3. The plugin will automatically serve at `https://yoursite.com/_functions/ai-index.json`

## Usage

### Dashboard Panel

Access the AI Index dashboard from your Wix Dashboard:

1. Go to your Wix Dashboard
2. Look for **AI Index** in the sidebar
3. Configure your settings:
   - Enter API key
   - Set webhook URL (optional)
   - Choose content to include
   - Enable/disable auto-publish

### Publishing Content

**Automatic Publishing** (Recommended):
- Enable "Auto-publish on content changes" in the dashboard
- Your content will automatically update when you make changes

**Manual Publishing**:
- Click "Publish Now" in the dashboard
- Use the backend function in your code:

```javascript
import { generateAIIndex, publishToAPI } from 'backend/aiindex';

// Generate and publish
const aiIndex = await generateAIIndex();
await publishToAPI(aiIndex);
```

### Adding Verification Badge

Add to any page where you want to show the verification badge:

1. Add an HTML element with ID `aiIndexBadge`
2. Add the public page code:

```javascript
import 'public/pages/aiindex.js';
```

3. The badge will automatically appear

### HTTP Function Endpoint

Your AI Index is automatically available at:
```
https://yoursite.com/_functions/ai-index.json
```

This endpoint:
- Returns JSON formatted for AI search engines
- Updates automatically with your content
- Includes proper CORS headers
- Caches for 1 hour

## Data Hooks (Auto-Publishing)

To enable automatic publishing on content changes, add data hooks:

1. Go to **Velo Sidebar** > **Data Hooks**
2. Add hooks for the collections you want to monitor:

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

## API Reference

### Backend Functions

#### `generateAIIndex()`
Generates the AI Index JSON from your site content.

```javascript
const aiIndex = await generateAIIndex();
```

#### `publishToAPI(aiIndexData)`
Publishes the AI Index to the API.

```javascript
await publishToAPI(aiIndex);
```

#### `saveConfig(configData)`
Saves configuration settings.

```javascript
await saveConfig({
  webhookUrl: 'https://example.com/webhook',
  autoPublish: true,
  includePages: true,
  includeBlog: true,
  includeProducts: false
});
```

#### `getAnalytics()`
Retrieves analytics data from the API.

```javascript
const analytics = await getAnalytics();
console.log(analytics.impressions);
```

#### `verifyApiKey(apiKey)`
Verifies an API key.

```javascript
const result = await verifyApiKey('your-api-key');
console.log(result.valid);
```

### Public Functions

#### `getAIIndexUrl()`
Returns the URL of your AI Index endpoint.

```javascript
import { getAIIndexUrl } from 'public/pages/aiindex';
const url = getAIIndexUrl();
```

#### `isAIIndexActive()`
Checks if AI Index is active and configured.

```javascript
import { isAIIndexActive } from 'public/pages/aiindex';
const active = await isAIIndexActive();
```

#### `getAIIndexData()`
Fetches the current AI Index data.

```javascript
import { getAIIndexData } from 'public/pages/aiindex';
const data = await getAIIndexData();
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | String | Required | Your AI Index API key |
| `webhookUrl` | String | Optional | URL to receive update notifications |
| `autoPublish` | Boolean | `true` | Auto-publish on content changes |
| `includePages` | Boolean | `true` | Include static pages in index |
| `includeBlog` | Boolean | `true` | Include blog posts in index |
| `includeProducts` | Boolean | `false` | Include store products in index |

## Troubleshooting

### AI Index Not Generating

1. Check that Velo is enabled
2. Verify API key is set in Secrets Manager
3. Check browser console for errors
4. Ensure collections have proper permissions

### HTTP Function Not Working

1. Verify HTTP Functions are enabled in Settings
2. Check the function name matches in `wix.config.json`
3. Test the endpoint in your browser
4. Check for errors in the Wix Console

### Auto-Publishing Not Working

1. Verify data hooks are set up correctly
2. Check that `autoPublish` is enabled in config
3. Verify API key is valid
4. Check the Wix Console for errors

### Dashboard Not Loading

1. Clear browser cache
2. Check that `dashboard/panel.html` is properly uploaded
3. Verify module imports are correct
4. Check browser console for errors

## Support

- Documentation: [aiindex.com/docs/wix](https://aiindex.com/docs/wix)
- Support: support@aiindex.com
- GitHub: [github.com/claimtec/iaindex](https://github.com/claimtec/iaindex)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## Changelog

### Version 1.0.0
- Initial release
- Automatic content indexing
- Dashboard integration
- HTTP Functions support
- Analytics tracking
- Verification badge
