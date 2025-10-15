# AIIndex Bubble.io Plugin

Official AIIndex plugin for Bubble.io - Generate AI Index JSON, verify domains, and manage AI content access receipts directly from your Bubble application.

## Features

### Workflow Actions
- **Generate AI Index JSON** - Automatically generate and sync AI Index from your Bubble database
- **Send Access Receipt** - Track when AI systems access your content
- **Verify Domain with AIIndex** - Complete domain verification workflow
- **Get AIIndex Status** - Check current sync status and verification
- **Update AIIndex Document** - Update individual documents

### Visual Elements
- **AIIndex Badge** - Display verification badge on your pages
- **Verification Status** - Show real-time verification status

### Data Types
- **AIIndex Document** - Store and manage indexed content
- **AIIndex Receipt** - Track AI access receipts

### API Integration
- Pre-configured API Connector for `https://api.aiindex.org/v1`
- All endpoints ready to use
- Bearer token authentication built-in

## Installation

### 1. Install the Plugin

1. Go to your Bubble editor
2. Navigate to **Plugins** tab
3. Click **Add plugins**
4. Search for "AIIndex"
5. Click **Install**

### 2. Configure API Key

1. Go to **Plugins** > **AIIndex**
2. Click **API Keys** section
3. Add your AIIndex API key (get one at [aiindex.org/dashboard](https://aiindex.org/dashboard))
4. Save changes

### 3. Add Data Types (Optional)

The plugin comes with pre-defined data types. To use them:

1. Go to **Data** tab
2. Find **AIIndex Document** and **AIIndex Receipt**
3. Optionally customize fields or create your own

## Quick Start Guide

### Generate AI Index from Your Database

1. **Add a Workflow Action**:
   - Create a button or schedule a recurring workflow
   - Add action: **Plugins > AIIndex - Generate AI Index JSON**

2. **Configure the Action**:
   ```
   Domain: your-site.com
   Data source: Your Bubble data type (e.g., "Blog Post")
   Auto-sync: Yes (checked)
   ```

3. **Result**:
   - Creates `/ai-index.json` with all your content
   - Syncs to AIIndex API
   - Returns document count and sync status

### Display Verification Badge

1. **Add the Element**:
   - Drag **AIIndex Badge** element to your page
   - Place it where you want the badge to appear

2. **Configure Properties**:
   ```
   Domain: your-site.com
   Theme: dark (or light, purple, blue, green)
   Size: medium (or small, large)
   Position: bottom-right (or other corners)
   ```

3. **Style**: Badge automatically styled, but you can customize via CSS

### Verify Your Domain

1. **Add a Workflow**:
   - Create a "Verify Domain" button
   - Add action: **Plugins > AIIndex - Verify Domain with AIIndex**

2. **Configure**:
   ```
   Domain: your-site.com
   Verification method: dns (or html, meta)
   ```

3. **Display Instructions**:
   - Show result field `instructions` in a text element
   - User follows the instructions
   - Click "Check Verification" to complete

### Track AI Access

1. **Add Workflow on Page Load**:
   - Create workflow: When page is loaded
   - Add condition: Detect AI bot (user agent check)
   - Add action: **Plugins > AIIndex - Send Access Receipt**

2. **Configure**:
   ```
   Document ID: Current page's document ID
   AI Provider: OpenAI (or other detected provider)
   Access type: crawl (or training, inference, analysis)
   ```

3. **Result**: Access tracked in AIIndex dashboard

## Workflow Examples

### Example 1: Auto-Sync on Schedule

Create a recurring workflow that syncs your content daily:

1. **Backend Workflow**: "Sync AIIndex Daily"
2. **Schedule**: Recurring event, every day at 2 AM
3. **Actions**:
   - Generate AI Index JSON
   - Send email notification (optional)

### Example 2: Verification Status Display

Show verification status on your settings page:

1. **Add Element**: AIIndex - Verification Status
2. **Configure**:
   ```
   Domain: Get from URL or user input
   Show icon: Yes
   Compact mode: No
   ```
3. **Conditional**: Show error message if not verified

### Example 3: Manual Sync Button

Create a button for admins to manually trigger sync:

1. **Button**: "Sync to AIIndex"
2. **Workflow**: When button is clicked
3. **Actions**:
   - Show loading spinner
   - Generate AI Index JSON
   - Show success message with document count
   - Hide loading spinner

### Example 4: Track Content Views

Track when AI systems view specific content:

1. **Page Load Workflow**
2. **Condition**: User agent contains "bot" or "crawler"
3. **Actions**:
   - Send Access Receipt
   - Log to database (optional)

## API Connector Setup (Advanced)

If you need direct API access:

1. Go to **Plugins** > **API Connector**
2. **Add Another API**
3. Use the preset: **AIIndex API v1**
4. Or import from `/api/api-connector-preset.json`

Available calls:
- Get Documents
- Get Document by ID
- Create Document
- Update Document
- Delete Document
- Verify Domain
- Check Verification
- Get Domain Status
- Create Receipt
- Get Receipts
- Bulk Sync
- Health Check

## Data Structure

### AIIndex Document

```javascript
{
  document_id: "doc_123abc",
  domain: "yoursite.com",
  url: "https://yoursite.com/page",
  title: "Page Title",
  description: "Page description",
  content: "Full page content...",
  published_date: "2025-10-13",
  updated_date: "2025-10-13",
  author: "John Doe",
  category: "Blog",
  tags: ["ai", "technology"],
  crawlable: true,
  ai_trainable: true,
  verification_status: "verified",
  last_synced: "2025-10-13T10:30:00Z"
}
```

### AIIndex Receipt

```javascript
{
  receipt_id: "rec_456def",
  document_id: "doc_123abc",
  ai_provider: "OpenAI",
  access_type: "crawl",
  timestamp: "2025-10-13T10:30:00Z",
  status: "sent"
}
```

## Customization

### Badge Styling

Override badge styles in your page HTML header:

```html
<style>
  #aiindex-badge {
    bottom: 10px !important;
    left: 10px !important;
  }
</style>
```

### Custom Badge Position

Use inline positioning by setting position to "inline" and placing the element where you want.

### Conditional Visibility

Show badge only when verified:

1. Add condition to badge element
2. Check: **Get AIIndex Status's is_verified is "yes"**

## Events

The plugin triggers custom events you can use in workflows:

- **AIIndex Sync Complete** - When sync finishes
- **Domain Verified** - When domain verification succeeds
- **Receipt Sent** - When access receipt is sent

To use events:

1. Create workflow: **Plugins > AIIndex - [Event Name]**
2. Add actions to respond to the event

## Troubleshooting

### Badge Not Appearing

- Verify API key is configured
- Check element visibility conditions
- Ensure domain is set correctly
- Check browser console for errors

### Sync Failing

- Verify API key is valid
- Check data source has accessible records
- Ensure domain is verified
- Check API status at [status.aiindex.org](https://status.aiindex.org)

### Verification Not Working

- Double-check DNS/HTML/meta tag is added correctly
- DNS changes can take up to 48 hours
- Try alternative verification method
- Contact support if issues persist

### No Receipts Showing

- Verify receipt sending workflow is triggered
- Check AI provider detection logic
- Ensure document_id is valid
- Check receipts in AIIndex dashboard

## Best Practices

1. **Schedule Regular Syncs**: Use recurring workflows to keep content fresh
2. **Verify Domain First**: Complete verification before generating indexes
3. **Monitor Receipts**: Track AI access patterns in your dashboard
4. **Use Conditions**: Only show badges on verified domains
5. **Test Thoroughly**: Use Bubble's debugger to test workflows
6. **Cache Status**: Store verification status to reduce API calls
7. **Handle Errors**: Add error handling to all API workflows

## Security

- API keys are stored securely by Bubble
- Never expose API keys in client-side code
- Use privacy rules to protect sensitive data
- Rotate API keys regularly
- Review access logs in AIIndex dashboard

## Performance

- Badge loads asynchronously (no page delay)
- API calls are cached when possible
- Bulk sync recommended for large datasets
- Use pagination for large result sets
- Consider background workflows for heavy operations

## Support

- **Documentation**: [docs.aiindex.org/bubble](https://docs.aiindex.org/bubble)
- **Dashboard**: [aiindex.org/dashboard](https://aiindex.org/dashboard)
- **Forum**: [forum.bubble.io/t/aiindex-plugin](https://forum.bubble.io/t/aiindex-plugin)
- **Email**: support@aiindex.org
- **Status**: [status.aiindex.org](https://status.aiindex.org)

## Pricing

The AIIndex plugin is free to install. API usage follows your AIIndex plan:

- **Free Tier**: 1,000 documents/month
- **Pro**: 10,000 documents/month
- **Enterprise**: Unlimited

See [aiindex.org/pricing](https://aiindex.org/pricing) for details.

## Changelog

### 1.0.0 (2025-10-13)
- Initial release
- Generate AI Index JSON action
- Send Access Receipt action
- Verify Domain action
- AIIndex Badge element
- Verification Status element
- API Connector preset
- Custom data types
- Event triggers

## License

MIT License - See LICENSE file for details

## Version

Current version: 1.0.0

## Links

- Plugin Page: [bubble.io/plugin/aiindex](https://bubble.io/plugin/aiindex)
- GitHub: [github.com/aiindex/bubble-plugin](https://github.com/aiindex/bubble-plugin)
- Website: [aiindex.org](https://aiindex.org)
