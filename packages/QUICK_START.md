# AI Index Integrations - Quick Start Guide

Get your site AI-discoverable in minutes! Choose your platform below.

---

## Shopify Store

### 5-Minute Setup

```bash
# 1. Clone and install
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/shopify-app
npm install
cd frontend && npm install && cd ..

# 2. Configure
cp .env.example .env
# Edit .env with your Shopify API credentials

# 3. Build and start
npm run build:frontend
npm start

# 4. Deploy
shopify app deploy
```

**Result**: Your products, pages, and blog posts are now discoverable at:
`https://your-store.myshopify.com/assets/ai-index.json`

**Dashboard**: Access analytics at your app URL

---

## Framer Site

### 2-Minute Setup

```bash
# 1. Build plugin
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/framer-plugin
npm install
npm run build
```

**In Framer:**
1. Import the built plugin
2. Drag "AI Index" component onto your master page
3. Configure properties (site name, description, webhook URL)
4. Publish your site

**Result**: AI Index automatically generates on every page load
- Stored in browser localStorage
- Injected into page `<head>`
- Available to AI assistants

---

## Ghost Blog

### 3-Minute Setup

```bash
# 1. Install on Ghost server
cd /var/www/ghost
ghost install @iaindex/ghost-plugin
ghost restart

# Or manually:
cd /var/www/ghost/content/plugins
cp -r /Users/dineshanchetty/Documents/claimtec/iaindex/packages/ghost-plugin ./ghost-ai-index
cd ghost-ai-index && npm install
cd /var/www/ghost && ghost restart
```

**Result**: Instant AI Index at `https://yourblog.com/ai-index.json`

**Dashboard**: Ghost Admin → Settings → Integrations → AI Index

---

## Wix Plugin - Quick Setup

### 1. Enable Velo
```
Wix Editor > Settings > Custom Code > Enable Velo Development Mode
```

### 2. Copy Files
Upload these files to your Wix site:
- `/packages/wix-plugin/backend/aiindex.jsw`
- `/packages/wix-plugin/public/pages/aiindex.js`
- `/packages/wix-plugin/dashboard/panel.html`
- `/packages/wix-plugin/package.json`
- `/packages/wix-plugin/wix.config.json`

### 3. Create Data Collection
Name: `AIIndexConfig`

Fields:
- `webhookUrl` (Text)
- `autoPublish` (Boolean)
- `includePages` (Boolean)
- `includeBlog` (Boolean)
- `includeProducts` (Boolean)

### 4. Add API Key
```
Settings > Secrets Manager > Add Secret
Name: aiIndexApiKey
Value: [Your API key from aiindex.com]
```

### 5. Enable HTTP Functions
```
Settings > Custom Code > HTTP Functions > Enable
```

### 6. Configure
Open the dashboard panel and configure your settings.

### 7. Your AI Index URL
```
https://yoursite.com/_functions/ai-index.json
```

**Full Documentation:** `/packages/wix-plugin/README.md`

---

## Squarespace Extension - Quick Setup

### 1. Add Main Script
```
Settings > Advanced > Code Injection > Header
```

Paste:
```html
<script>
  // Copy entire contents of aiindex-squarespace.js here
</script>
```

### 2. Add Styles
```
Design > Custom CSS
```

Paste entire contents of `styles.css`

### 3. Create Config Page (Optional)
```
Pages > + Add Page > Blank
```

Add Code Block with contents of `config.html`

### 4. Configure via Config Page
1. Visit your config page
2. Enter API key from aiindex.com
3. Set content options
4. Click "Save Configuration"
5. Click "Generate Index"
6. Click "Publish to API"

### 5. Or Configure via Console
```javascript
window.AIIndex.setConfig({
  apiKey: 'your-api-key-here',
  autoPublish: true,
  includePages: true,
  includeBlog: true,
  includeProducts: false
});

await window.AIIndex.generate();
await window.AIIndex.publish();
```

### 6. Verify Installation
Open browser console (F12), you should see:
```
AI Index for Squarespace loaded. Use window.AIIndex to interact.
```

### 7. Your AI Index
The index is served client-side via JavaScript at:
```
https://yoursite.com/ai-index.json
```

**Full Documentation:** `/packages/squarespace-snippet/README.md`

**Installation Guide:** `/packages/squarespace-snippet/install-guide.md`

---

## Get Your API Key

1. Visit [aiindex.com](https://aiindex.com)
2. Sign up or log in
3. Go to Dashboard > API Keys
4. Generate new API key
5. Copy and use in your integration

---

## Verification Badge

Add this HTML anywhere on your site to show the verification badge:

```html
<div class="ai-index-badge">
  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
  </svg>
  <span>AI Index Verified</span>
</div>
```

The CSS is included in the styles.css file.

---

## File Locations

### Wix Plugin
```
/Users/dineshanchetty/Documents/claimtec/iaindex/packages/wix-plugin/
├── backend/aiindex.jsw          (308 lines)
├── public/pages/aiindex.js      (186 lines)
├── dashboard/panel.html         (487 lines)
├── package.json
├── wix.config.json
└── README.md                    (279 lines)
```

### Squarespace Extension
```
/Users/dineshanchetty/Documents/claimtec/iaindex/packages/squarespace-snippet/
├── aiindex-squarespace.js       (441 lines)
├── config.html                  (568 lines)
├── styles.css                   (309 lines)
├── install-guide.md             (356 lines)
└── README.md                    (374 lines)
```

---

## What Gets Indexed?

Both integrations index:

### Pages
- All public static pages
- Navigation pages
- Pages from sitemap

### Blog Posts
- Published blog articles
- Post titles and excerpts
- Author information
- Tags/categories

### Products (Optional)
- Store products
- Product descriptions
- Prices and availability
- Product images

---

## Testing Your Integration

### Wix
```javascript
// In browser console or Velo editor
import { generateAIIndex } from 'backend/aiindex';

const aiIndex = await generateAIIndex();
console.log(`Indexed ${aiIndex.pages.length} pages`);
```

### Squarespace
```javascript
// In browser console
const data = await window.AIIndex.generate();
console.log(`Indexed ${data.pages.length} pages`);
```

---

## Common Issues

### Wix
**Problem**: HTTP function not working
**Solution**: Enable HTTP Functions in Settings > Custom Code

**Problem**: API key not found
**Solution**: Add to Secrets Manager as `aiIndexApiKey`

### Squarespace
**Problem**: Script not loading
**Solution**: Ensure it's in Header section, not Footer

**Problem**: Configuration not saving
**Solution**: Check localStorage is enabled, not in Incognito mode

---

## Support

- Email: support@aiindex.com
- Docs: [aiindex.com/docs](https://aiindex.com/docs)
- GitHub: [github.com/claimtec/iaindex](https://github.com/claimtec/iaindex)

---

## Next Steps

After setup:

1. **Verify** your AI Index is generating correctly
2. **Test** the JSON endpoint
3. **Submit** your site to AI search engines
4. **Monitor** analytics in your dashboard
5. **Update** content regularly

---

**Created:** October 13, 2025
**Version:** 1.0.0
