# Installation Guide

## Quick Install

### Option 1: Manual Installation
1. Copy the entire `wp-plugin` folder to your WordPress plugins directory:
   ```bash
   cp -r wp-plugin /path/to/wordpress/wp-content/plugins/aiindex
   ```

2. Log in to your WordPress admin panel

3. Navigate to **Plugins > Installed Plugins**

4. Find "AIIndex for WordPress" and click **Activate**

### Option 2: ZIP Installation
1. Create a ZIP file of the plugin:
   ```bash
   cd packages
   zip -r aiindex.zip wp-plugin/
   ```

2. In WordPress admin, go to **Plugins > Add New**

3. Click **Upload Plugin**

4. Choose the `aiindex.zip` file

5. Click **Install Now** and then **Activate**

## Post-Installation Setup

### Step 1: Configure General Settings
1. Go to **AIIndex > Settings**
2. Check "Enable AIIndex"
3. Select content types (Posts and/or Pages)
4. Optionally add a webhook URL for automatic syncing
5. Choose sync frequency
6. Click **Save Settings**

### Step 2: Generate Keys
1. Go to **AIIndex > Settings > Keys** tab
2. Click **Generate Keys**
3. Your public key will be displayed
4. Copy the public key to share with AI indexers
5. The private key is stored securely (never displayed)

### Step 3: Verify Domain
1. Go to **AIIndex > Settings > Verification** tab
2. Click **Verify Domain**
3. Wait for verification to complete
4. You should see a "Verified" status

### Step 4: Test Your Index
1. Visit: `https://yourdomain.com/ai-index.json`
2. You should see a JSON response with your content
3. The response should include:
   - version
   - domain
   - siteName
   - lastUpdated
   - content (array of posts/pages)
   - publicKey
   - signature

## Using the Badge

Add the verification badge to any post, page, or widget:

```
[aiindex_badge]
```

Customization options:
```
[aiindex_badge style="minimal" show_count="true" show_status="true"]
```

## Excluding Content

To exclude specific posts or pages from the index:

1. Edit the post/page
2. Look for the "AIIndex Settings" meta box (usually in the sidebar)
3. Check "Exclude from AI Index"
4. Update/Publish the post

## Testing the Receipt API

Test receiving a receipt with curl:

```bash
curl -X POST https://yourdomain.com/wp-json/aiindex/v1/receipt \
  -H "Content-Type: application/json" \
  -d '{
    "receiptId": "test-receipt-123",
    "contentUrl": "https://yourdomain.com/sample-post/",
    "contentHash": "abc123def456",
    "indexedAt": "2024-01-01T12:00:00Z",
    "indexer": {
      "name": "Test Indexer",
      "url": "https://testindexer.com"
    }
  }'
```

View receipts at: **AIIndex > Receipts**

## Troubleshooting

### Index file not accessible
- Check that WordPress permalinks are enabled
- Ensure `.htaccess` allows the rewrite rule
- Try regenerating permalinks: Settings > Permalinks > Save Changes

### Keys not generating
- Ensure PHP 7.2+ with Sodium extension is installed
- Check: `php -m | grep sodium`
- Contact your hosting provider if Sodium is not available

### Receipts not saving
- Check PHP error logs
- Verify the receipt JSON format is correct
- Ensure database permissions are correct

### Dashboard widget not showing
- Clear WordPress cache
- Check that you have admin capabilities
- Refresh the browser

## System Requirements

- WordPress 5.0+
- PHP 7.2+ (with Sodium extension)
- MySQL 5.6+
- Pretty permalinks enabled (recommended)

## Uninstallation

To completely remove the plugin:

1. Deactivate the plugin
2. Delete the plugin files
3. (Optional) Remove the database table:
   ```sql
   DROP TABLE wp_aiindex_receipts;
   ```
4. (Optional) Remove options:
   ```sql
   DELETE FROM wp_options WHERE option_name LIKE 'aiindex_%';
   ```

## Support

For issues or questions:
- Documentation: https://aiindex.dev/docs
- Support: https://aiindex.dev/support
- GitHub: https://github.com/aiindex/wordpress-plugin
