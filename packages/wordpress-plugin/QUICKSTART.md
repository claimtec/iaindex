# IAIndex WordPress Plugin - Quick Start Guide

Get up and running with IAIndex in 5 minutes!

## Prerequisites

- WordPress 6.0+ installed and running
- PHP 7.4+ on your server
- IAIndex API key ([Get one here](https://aiindex.io))
- Admin access to your WordPress site

## Installation (3 Steps)

### Step 1: Install the Plugin

**Option A: Upload via WordPress Admin**
1. Zip the plugin folder: `wordpress-plugin` → `iaindex.zip`
2. Go to WordPress Admin → **Plugins** → **Add New** → **Upload Plugin**
3. Choose `iaindex.zip` and click **Install Now**
4. Click **Activate Plugin**

**Option B: Manual Installation**
```bash
# Copy plugin to WordPress
cp -r /Users/dineshanchetty/Documents/claimtec/iaindex/packages/wordpress-plugin \
      /path/to/wordpress/wp-content/plugins/iaindex

# Set permissions
chmod -R 755 /path/to/wordpress/wp-content/plugins/iaindex
```

Then activate via WordPress Admin → Plugins.

### Step 2: Configure Settings

1. Go to **Settings** → **IAIndex**
2. Fill in the form:
   - **Domain**: Your website URL (e.g., `https://yourdomain.com`)
   - **API Key**: Your IAIndex API key
   - **Auto-Generate**: ✓ Check to enable automatic index updates
3. Click **Save Settings**

### Step 3: Verify & Generate

1. Click **Verify Domain Now** button
   - Wait for the green success message
   - If it fails, see troubleshooting below

2. Click **Generate Index Now** button
   - You'll see how many entries were created
   - Index is now available at `/.well-known/iaindex.json`

**That's it!** Your WordPress site is now integrated with IAIndex.

## Verify It's Working

### Check 1: View Your Index

Visit: `https://yourdomain.com/.well-known/iaindex.json`

You should see JSON like this:
```json
{
  "domain": "yourdomain.com",
  "version": "1.1",
  "entries": [
    {
      "url": "https://yourdomain.com/hello-world",
      "title": "Hello World",
      "author": "Admin",
      "publishedDate": "2025-01-17T12:00:00Z",
      "license": {"type": "CC-BY-4.0"}
    }
  ],
  "generatedAt": "2025-01-17T12:00:00Z"
}
```

### Check 2: Dashboard Widget

Go to WordPress **Dashboard** → You should see the **IAIndex Status** widget showing:
- ✓ Verification status: **Verified**
- Number of index entries
- Number of receipts (starts at 0)

### Check 3: Webhook Endpoint

Test the webhook is accessible:
```bash
curl https://yourdomain.com/wp-json/iaindex/v1/receipt
```

Expected response: `401 Unauthorized` (this is correct - means auth is working)

## Common Setup Issues

### Issue: Index Returns 404

**Solution 1**: Flush permalinks
1. Go to **Settings** → **Permalinks**
2. Click **Save Changes** (don't change anything)
3. Try accessing the index again

**Solution 2**: Check file exists
```bash
ls /path/to/wordpress/wp-content/uploads/iaindex/iaindex.json
```

If missing, click "Generate Index Now" again.

### Issue: Domain Verification Fails

**Checklist**:
- [ ] Index file is accessible publicly (test in incognito mode)
- [ ] Domain URL includes `https://` (not just `example.com`)
- [ ] No trailing slash in domain URL
- [ ] API key is correct (no extra spaces)
- [ ] Your site is accessible from the internet (not localhost)

### Issue: No Posts in Index

**Checklist**:
- [ ] You have published posts (not drafts or pages)
- [ ] Posts are set to "Published" status
- [ ] You clicked "Generate Index Now" after creating posts

## Next Steps

### 1. Customize Auto-Generation

By default, the index regenerates when you publish a post. To change:
- Go to **Settings** → **IAIndex**
- Uncheck **Auto-Generate Index** for manual control
- Click **Save Settings**

### 2. View Receipts

When receipts are received:
1. Go to **Tools** → **IAIndex Receipts**
2. Or click **View Receipts** from the dashboard widget
3. See all timestamped content receipts

### 3. Monitor Dashboard

The **IAIndex Status** widget on your dashboard shows:
- Real-time verification status
- Index statistics
- Receipt count
- Last update time

## Usage Examples

### Publish a New Post

1. Create and publish a post normally
2. If auto-generate is enabled:
   - Index updates automatically
   - New post appears in `/.well-known/iaindex.json`
3. If auto-generate is disabled:
   - Go to **Settings** → **IAIndex**
   - Click **Generate Index Now**

### Bulk Update Index

If you've published many posts:
1. Go to **Settings** → **IAIndex**
2. Click **Generate Index Now**
3. All published posts are included in the index

### Receive a Receipt

Receipts arrive via webhook automatically when:
- Your content is indexed by AI systems
- The AI system sends a receipt to your webhook
- The plugin stores it and makes it viewable in admin

No action needed - it's automatic!

## API Endpoints Reference

### Public Endpoints

- **Index File**: `https://yourdomain.com/.well-known/iaindex.json`
  - Method: GET
  - Auth: None
  - Returns: JSON index

### REST API Endpoints

- **Receive Receipt**: `https://yourdomain.com/wp-json/iaindex/v1/receipt`
  - Method: POST
  - Auth: Bearer token (API key)
  - Body: Receipt JSON data

- **Get Receipts**: `https://yourdomain.com/wp-json/iaindex/v1/receipts`
  - Method: GET
  - Auth: WordPress admin session
  - Returns: List of stored receipts

## Settings Reference

| Setting | Description | Default |
|---------|-------------|---------|
| **Domain** | Your website's primary domain | Auto-detected from WordPress |
| **API Key** | IAIndex API authentication key | Empty (must be provided) |
| **Auto-Generate** | Regenerate index when posts publish | Enabled |

## File Locations

```
WordPress Installation
├── wp-content/
│   ├── plugins/
│   │   └── iaindex/              # Plugin files
│   │       ├── iaindex.php
│   │       ├── admin/
│   │       ├── includes/
│   │       └── assets/
│   └── uploads/
│       └── iaindex/              # Generated files
│           └── iaindex.json      # Your index file
```

## Quick Commands

### Reinstall Plugin
```bash
# Remove old version
rm -rf /path/to/wordpress/wp-content/plugins/iaindex

# Copy new version
cp -r /path/to/new/plugin /path/to/wordpress/wp-content/plugins/iaindex

# Set permissions
chmod -R 755 /path/to/wordpress/wp-content/plugins/iaindex

# Reactivate in WordPress admin
```

### Regenerate Index via WP-CLI (future feature)
```bash
# Coming soon
wp iaindex generate
```

### Check Plugin Status
```bash
# View plugin files
ls -la /path/to/wordpress/wp-content/plugins/iaindex

# View generated index
cat /path/to/wordpress/wp-content/uploads/iaindex/iaindex.json

# Check permissions
ls -la /path/to/wordpress/wp-content/uploads/iaindex
```

## Tips & Best Practices

### 1. Keep API Key Secure
- Never commit it to version control
- Don't share in screenshots
- Regenerate if compromised

### 2. Test Before Going Live
- Test on staging site first
- Verify all features work
- Check index is accessible

### 3. Monitor Receipts
- Check receipts regularly
- Set up email notifications (future feature)
- Archive old receipts periodically

### 4. Performance
- Auto-generate works well for most sites
- For high-traffic sites, consider manual generation
- Index file is cached by WordPress

### 5. Backup
- Include `wp-content/uploads/iaindex/` in backups
- Export receipts before major updates
- Keep settings documented

## Support & Resources

### Documentation
- Installation Guide: See `INSTALLATION.md`
- Technical Docs: See `TECHNICAL.md`
- IAIndex Docs: https://docs.aiindex.io

### Getting Help
- Check troubleshooting section above
- Review technical documentation
- GitHub Issues: https://github.com/claimtec/iaindex/issues
- IAIndex Support: support@aiindex.io

### Updates
To check for updates:
1. Visit the plugin repository
2. Download latest version
3. Follow reinstall steps above

## FAQ

**Q: Do I need to manually add posts to the index?**
A: No, all published posts are automatically included.

**Q: Can I exclude certain posts?**
A: Not in v1.0 - coming in future version.

**Q: Does this work with custom post types?**
A: Currently only standard posts - custom post types coming soon.

**Q: How do I get an API key?**
A: Register at https://aiindex.io

**Q: Is this plugin free?**
A: Yes, the plugin is free and open source.

**Q: What data is sent to IAIndex?**
A: Only your domain for verification. The index is hosted on your site.

**Q: How often should I regenerate the index?**
A: Auto-generate handles it. Manual regeneration is only needed for bulk updates.

**Q: Can I customize the license type?**
A: Not yet - currently defaults to CC-BY-4.0. Customization coming in v1.1.

## What's Next?

Now that you're set up:

1. **Publish Content**: Continue publishing posts normally
2. **Monitor Dashboard**: Check the IAIndex widget regularly
3. **Verify Receipts**: Watch for incoming receipts
4. **Stay Updated**: Check for plugin updates

Your content is now discoverable and verifiable via IAIndex!

---

**Need more help?** See the full [Installation Guide](INSTALLATION.md) or [Technical Documentation](TECHNICAL.md).
