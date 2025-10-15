---
title: weuflow Plugin
---

# weuflow Plugin

Integrate IAIndex with your weuflow site for automatic content attribution.

## Installation

### Via Plugin Marketplace

1. Log into your weuflow dashboard
2. Navigate to Plugins/Extensions/Add-ons
3. Search for "IAIndex"
4. Click "Install" and then "Activate"

### Manual Installation

Download the plugin from [GitHub](https://github.com/claimtec/iaindex-webflow) and follow the installation instructions.

## Configuration

### Step 1: Domain Verification

1. Go to Settings → IAIndex
2. Click "Verify Domain"
3. Follow the DNS verification process
4. Wait for verification confirmation

### Step 2: Publisher Settings

Configure your publisher information:

- **Domain**: Auto-detected from your site
- **Publisher Name**: Your site/organization name
- **Contact Email**: Support/contact email
- **License Type**: Default license for content

### Step 3: Content Selection

Choose which content to include:

- All published posts/pages
- Specific categories/tags
- Custom post types
- Exclude specific content

### Step 4: Automatic Indexing

Enable automatic index generation:

- ✓ Auto-generate index on publish
- ✓ Update index on content edit
- ✓ Daily index regeneration

## Features

- **Automatic Index Generation**: Creates IAIndex entries for all content
- **Domain Verification**: Built-in domain verification workflow
- **Receipt Handling**: Webhook endpoint for receiving usage receipts
- **Analytics Dashboard**: View content usage statistics
- **Bulk Import**: Import existing content into IAIndex
- **Custom Licenses**: Set per-content license terms

## Usage

Once configured, the plugin automatically:

1. Creates IAIndex entries for new content
2. Updates entries when content is modified
3. Generates signed index file
4. Hosts index at `/.well-known/iaindex.json`
5. Receives and stores usage receipts

## Webhook Configuration

The plugin automatically creates a webhook endpoint at:

```
https://yoursite.com/wp-json/iaindex/v1/receipt
```

This endpoint receives usage receipts from AI clients.

## Analytics

View analytics in your weuflow dashboard:

- Total content entries indexed
- Usage receipts received
- Top accessed content
- AI clients accessing your content
- Usage trends over time

## Troubleshooting

### Index Not Generated

- Check domain verification status
- Verify publish permissions
- Check error logs in Settings → IAIndex → Logs

### Receipts Not Received

- Verify webhook endpoint is accessible
- Check firewall/security settings
- Test webhook with [Webhook Tester](https://webhook.site)

### Performance Issues

- Enable caching for index file
- Limit number of entries per index
- Use CDN for index hosting

## Support

- [Documentation](https://docs.iaindex.com/plugins/webflow)
- [GitHub Issues](https://github.com/claimtec/iaindex-webflow/issues)
- [Community Forum](https://community.iaindex.com)

