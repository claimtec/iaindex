# AI Index Installation Guide for Squarespace

This guide will walk you through installing and configuring the AI Index integration on your Squarespace website.

## Prerequisites

- A Squarespace website (Business plan or higher recommended for full Code Injection access)
- An AI Index API key from [aiindex.com](https://aiindex.com)
- Basic familiarity with Squarespace's admin panel

## Installation Steps

### Step 1: Add the Main Script

1. Log in to your Squarespace admin panel
2. Go to **Settings > Advanced > Code Injection**
3. In the **Header** section, paste the contents of `aiindex-squarespace.js`
4. Wrap it in script tags:

```html
<script>
  // Paste the contents of aiindex-squarespace.js here
</script>
```

5. Click **Save**

### Step 2: Add the Styles

1. Go to **Design > Custom CSS**
2. Paste the contents of `styles.css`
3. Click **Save**

### Step 3: Create Configuration Page (Optional but Recommended)

1. Go to **Pages**
2. Click the **+** button to add a new page
3. Select **Blank** page
4. Name it "AI Index Config" (you can make it password-protected or Not Linked)
5. Add a **Code Block**
6. Paste the contents of `config.html`
7. Click **Apply**
8. Save and publish the page

### Step 4: Configure Your Settings

**Option A: Using the Configuration Page**

1. Visit your newly created AI Index Config page
2. Enter your API key from aiindex.com
3. Configure content options:
   - Auto-publish on changes
   - Include pages
   - Include blog posts
   - Include products (if you have a store)
4. Click **Save Configuration**
5. Click **Verify API Key** to ensure it's working
6. Click **Generate Index** to create your first AI Index
7. Click **Publish to API** to send it to AI search engines

**Option B: Using Browser Console**

If you prefer not to create a config page, you can configure via the browser console:

```javascript
// Set API key
window.AIIndex.setConfig({
  apiKey: 'your-api-key-here',
  webhookUrl: 'https://yoursite.com/webhook', // optional
  autoPublish: true,
  includePages: true,
  includeBlog: true,
  includeProducts: false
});

// Generate and publish
await window.AIIndex.generate();
await window.AIIndex.publish();
```

### Step 5: Verify Installation

1. Open your browser's developer console (F12)
2. You should see: "AI Index for Squarespace loaded. Use window.AIIndex to interact."
3. Test the API:

```javascript
// Check if configured
window.AIIndex.getConfig();

// Get current data
window.AIIndex.getData();
```

### Step 6: Add Verification Badge (Optional)

Add this HTML snippet to any page, blog post, or footer to display the verification badge:

```html
<div class="ai-index-badge">
  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
  </svg>
  <span>AI Index Verified</span>
</div>
```

## How It Works

### Automatic Updates

The AI Index automatically regenerates every 24 hours when someone visits your homepage. This ensures your content stays up-to-date with AI search engines.

### Manual Updates

You can manually trigger updates at any time:

```javascript
// Generate new index
await window.AIIndex.generate();

// Publish to API
await window.AIIndex.publish();
```

### Content Sources

The integration automatically indexes:

1. **Pages**: All public pages via your navigation and sitemap
2. **Blog Posts**: Using Squarespace's JSON API (`/blog?format=json`)
3. **Products**: Using Squarespace's Commerce API (if enabled)

### Storage

Your AI Index data is stored in the browser's `localStorage`:
- `aiindex_data`: The generated JSON data
- `aiindex_last_generated`: Timestamp of last generation
- `aiindex_api_key`: Your API key (stored locally)
- `aiindex_*`: Various configuration settings

## Advanced Configuration

### Webhook Notifications

Set up a webhook to receive notifications when your AI Index is updated:

```javascript
window.AIIndex.setConfig({
  webhookUrl: 'https://yoursite.com/webhook'
});
```

The webhook will receive POST requests with this payload:

```json
{
  "event": "ai_index_updated",
  "timestamp": "2025-10-13T12:00:00Z",
  "page_count": 42
}
```

### Customizing Content Selection

Control which content types are included:

```javascript
window.AIIndex.setConfig({
  includePages: true,      // Static pages
  includeBlog: true,       // Blog posts
  includeProducts: false   // Store products
});
```

### Manual Generation Schedule

If you want to control when the index is generated, disable auto-publish:

```javascript
window.AIIndex.setConfig({
  autoPublish: false
});

// Then manually generate/publish when needed
await window.AIIndex.generate();
await window.AIIndex.publish();
```

## Troubleshooting

### Script Not Loading

**Problem**: Console message not appearing

**Solutions**:
1. Check that the script is in the Header section (not Footer)
2. Clear your browser cache
3. Verify there are no JavaScript errors in the console
4. Ensure the script tags are properly closed

### API Key Invalid

**Problem**: "API key is invalid" message

**Solutions**:
1. Verify you copied the key correctly from aiindex.com
2. Check that your API key hasn't expired
3. Ensure there are no extra spaces before/after the key
4. Try generating a new API key

### No Pages Indexed

**Problem**: AI Index generates but shows 0 pages

**Solutions**:
1. Check that your pages are published and public
2. Verify content options are enabled (includePages, includeBlog, etc.)
3. Check browser console for errors during generation
4. Try manually visiting `/sitemap.xml` to ensure it's accessible

### Blog Posts Not Appearing

**Problem**: Blog posts aren't included in the index

**Solutions**:
1. Ensure you have a blog on your site
2. Check that blog posts are published (not drafts)
3. Verify `includeBlog` is set to true
4. Test the blog JSON endpoint: `/blog?format=json`

### Products Not Appearing

**Problem**: Store products aren't indexed

**Solutions**:
1. Ensure you have Squarespace Commerce enabled
2. Check that products are visible and published
3. Verify `includeProducts` is set to true
4. Note: Commerce API may require Business plan or higher

### Configuration Not Saving

**Problem**: Settings reset after page reload

**Solutions**:
1. Check that localStorage is enabled in your browser
2. Try a different browser to rule out extensions
3. Ensure you're not in Private/Incognito mode
4. Check browser console for storage errors

## Limitations

### Squarespace-Specific Limitations

1. **No Server-Side Endpoint**: Unlike Wix, Squarespace doesn't support custom server-side code, so the AI Index is served via JavaScript and localStorage

2. **Client-Side Generation**: The index is generated in the browser, which means:
   - First-time visitors may experience a slight delay
   - The index needs to regenerate every 24 hours
   - Some AI crawlers may need special handling

3. **API Access**: Some features (like products) may require higher-tier Squarespace plans

4. **Rate Limiting**: Frequent regeneration may be rate-limited by Squarespace's APIs

### Workarounds

For production sites with high traffic, consider:

1. **External Hosting**: Generate the AI Index on a separate server and host it there
2. **CDN**: Use a CDN to cache the generated JSON
3. **Scheduled Generation**: Use a cron job to regenerate periodically

## Best Practices

1. **Keep API Key Secure**: Don't share your config page publicly
2. **Regular Updates**: Let auto-publish stay enabled for fresh content
3. **Monitor Performance**: Check browser console for generation times
4. **Test After Changes**: Generate a new index after major site updates
5. **Use Webhooks**: Set up webhooks to track when updates occur

## API Reference

### Configuration Methods

```javascript
// Get current config
const config = window.AIIndex.getConfig();

// Set config values
window.AIIndex.setConfig({
  apiKey: 'your-key',
  webhookUrl: 'https://example.com/webhook',
  autoPublish: true,
  includePages: true,
  includeBlog: true,
  includeProducts: false
});

// Verify API key
const result = await window.AIIndex.verifyApiKey('your-key');
console.log(result.valid); // true or false
```

### Generation and Publishing

```javascript
// Generate AI Index from site content
const aiIndex = await window.AIIndex.generate();
console.log(`Generated ${aiIndex.pages.length} pages`);

// Publish to AI Index API
const publishResult = await window.AIIndex.publish();
console.log('Published successfully');

// Get stored data
const data = window.AIIndex.getData();
console.log(data);
```

## Support

- **Documentation**: [aiindex.com/docs/squarespace](https://aiindex.com/docs/squarespace)
- **Support Email**: support@aiindex.com
- **GitHub Issues**: [github.com/claimtec/iaindex/issues](https://github.com/claimtec/iaindex/issues)

## Upgrading

To upgrade to a new version:

1. Replace the script in Code Injection with the new version
2. Update the CSS in Custom CSS
3. Clear your browser cache
4. Regenerate your AI Index

## Uninstallation

To remove AI Index from your site:

1. Go to **Settings > Advanced > Code Injection**
2. Remove the script from the Header section
3. Go to **Design > Custom CSS**
4. Remove the AI Index styles
5. Delete the configuration page (if created)
6. Clear localStorage in browser console:

```javascript
Object.keys(localStorage)
  .filter(key => key.startsWith('aiindex_'))
  .forEach(key => localStorage.removeItem(key));
```

## License

MIT License - See LICENSE file for details
