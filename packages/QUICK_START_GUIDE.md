# AIIndex Integrations - Quick Start Guide

## Webflow Integration

### Installation (2 minutes)

1. **Get API Key**: Visit [aiindex.org/dashboard](https://aiindex.org/dashboard)

2. **Add to Webflow**:
   ```html
   <!-- Site Settings > Custom Code > Footer Code -->
   <script src="https://cdn.aiindex.org/webflow/snippet.js"></script>
   <script>
     window.aiIndexConfig = {
       apiKey: 'YOUR_API_KEY',
       domain: 'yoursite.com',
       badgeEnabled: true,
       autoSync: true
     };
     AIIndexWebflow.init(window.aiIndexConfig);
   </script>
   ```

3. **Publish**: Publish your Webflow site

### Features Enabled
- Auto-generated `/ai-index.json` from CMS
- Verification badge on all pages
- Real-time sync to AIIndex API

---

## Bubble.io Plugin

### Installation (3 minutes)

1. **Install Plugin**: Plugins tab → Add plugins → Search "AIIndex" → Install
2. **Configure API Key**: Plugins → AIIndex → API Keys → Add your key
3. **Add Workflow**: Create workflow → AIIndex - Generate AI Index JSON

---

## File Locations

**Webflow**: `/packages/webflow-snippet/`
**Bubble.io**: `/packages/bubble-plugin/`

See INTEGRATIONS_SUMMARY.md for complete documentation.
