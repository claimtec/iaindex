# IAIndex WordPress Plugin - Installation Guide

## Overview

This WordPress plugin integrates your WordPress site with IAIndex for AI content tracking and verification. It automatically generates an index of your published posts and provides receipt tracking capabilities.

## Requirements

- WordPress 6.0 or higher
- PHP 7.4 or higher
- Active IAIndex account with API key
- Write permissions to wp-content/uploads directory

## Installation Steps

### Method 1: Manual Installation

1. **Download the Plugin**
   - Copy the entire `wordpress-plugin` folder to your WordPress installation

2. **Upload to WordPress**
   ```bash
   # Navigate to your WordPress plugins directory
   cd /path/to/your/wordpress/wp-content/plugins/

   # Copy or move the plugin folder
   cp -r /Users/dineshanchetty/Documents/claimtec/iaindex/packages/wordpress-plugin ./iaindex
   ```

3. **Set Permissions**
   ```bash
   # Ensure proper permissions
   chmod -R 755 /path/to/wordpress/wp-content/plugins/iaindex
   ```

4. **Activate the Plugin**
   - Log in to your WordPress admin panel
   - Navigate to **Plugins** > **Installed Plugins**
   - Find "IAIndex Integration" and click **Activate**

### Method 2: ZIP Installation

1. **Create a ZIP file**
   ```bash
   cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/
   zip -r iaindex-plugin.zip wordpress-plugin/
   ```

2. **Upload via WordPress Admin**
   - Log in to WordPress admin
   - Go to **Plugins** > **Add New** > **Upload Plugin**
   - Choose the `iaindex-plugin.zip` file
   - Click **Install Now**
   - Click **Activate Plugin**

## Configuration

### 1. Access Settings

After activation, navigate to **Settings** > **IAIndex** in your WordPress admin panel.

### 2. Configure Domain

- **Domain**: Your website domain (usually auto-detected)
  - Example: `https://yourdomain.com`
  - This should match your site's primary domain

### 3. Add API Key

- **API Key**: Your IAIndex API key
  - Obtain from: https://aiindex.io
  - Click the eye icon to toggle visibility
  - Keep this secure and never share it

### 4. Auto-Generate Setting

- **Auto-Generate Index**: Check this box to automatically regenerate the index when posts are published
  - Recommended: Keep enabled for automatic updates
  - Uncheck if you prefer manual control

### 5. Save Settings

Click **Save Settings** to store your configuration.

## Verification

### Verify Your Domain

1. Ensure your index is generated (see below)
2. Click the **Verify Domain Now** button
3. Wait for the verification process to complete
4. You should see a success message if verification is successful

**Note**: Domain verification requires:
- A valid index file at `/.well-known/iaindex.json`
- The index file must be publicly accessible
- Your domain must be reachable from the internet

## Index Generation

### Automatic Generation

If **Auto-Generate Index** is enabled:
- The index regenerates automatically when you publish a post
- No manual intervention required

### Manual Generation

To manually generate the index:

1. Go to **Settings** > **IAIndex**
2. Scroll to **Index Management**
3. Click **Generate Index Now**
4. Wait for the generation process to complete
5. You'll see a success message with:
   - Number of entries
   - File location
   - Public URL

### Verify Index is Accessible

Check that your index is publicly accessible:

1. Visit: `https://yourdomain.com/.well-known/iaindex.json`
2. You should see a JSON file with your posts

**Troubleshooting**: If the index is not accessible, see the Troubleshooting section below.

## Dashboard Widget

After setup, you'll see an **IAIndex Status** widget on your WordPress dashboard showing:

- Verification status (Verified/Not Verified)
- Number of index entries
- Number of receipts received
- Last index generation time
- Quick action buttons

## Receipt Tracking

### Webhook Endpoint

The plugin creates a webhook endpoint for receiving receipts:

**Endpoint**: `https://yourdomain.com/wp-json/iaindex/v1/receipt`

**Authentication**: Bearer token (your API key)

### View Receipts

To view received receipts:

1. Go to **Tools** > **IAIndex Receipts** in WordPress admin
2. Or click **View Receipts** from the dashboard widget
3. Receipts are displayed with:
   - Receipt ID
   - Content URL
   - Provider
   - Timestamp
   - Received date

## File Structure

After installation, your plugin directory will contain:

```
wp-content/plugins/iaindex/
├── iaindex.php                 # Main plugin file
├── readme.txt                  # WordPress plugin readme
├── INSTALLATION.md            # This file
├── admin/
│   ├── settings.php           # Settings page
│   └── dashboard.php          # Dashboard widget
├── includes/
│   ├── api-client.php         # IAIndex API client
│   ├── index-generator.php    # Index generation logic
│   └── webhook.php            # Webhook handler
└── assets/
    ├── css/
    │   └── admin.css          # Admin styles
    └── js/
        └── admin.js           # Admin JavaScript
```

## Generated Files

The plugin will create:

```
wp-content/uploads/iaindex/
└── iaindex.json               # Generated index file
```

## Troubleshooting

### Index Not Accessible

If `/.well-known/iaindex.json` returns 404:

1. **Check Permalinks**
   - Go to **Settings** > **Permalinks**
   - Click **Save Changes** to flush rewrite rules
   - Try accessing the index again

2. **Check File Permissions**
   ```bash
   # Ensure uploads directory is writable
   chmod 755 /path/to/wordpress/wp-content/uploads/iaindex
   chmod 644 /path/to/wordpress/wp-content/uploads/iaindex/iaindex.json
   ```

3. **Verify File Exists**
   - Check that the file exists at: `wp-content/uploads/iaindex/iaindex.json`
   - If not, click "Generate Index Now"

4. **Server Configuration**
   - Some servers may block `.well-known` directories
   - Contact your hosting provider if the issue persists

### Domain Verification Fails

If domain verification fails:

1. **Check Index Accessibility**
   - Ensure `/.well-known/iaindex.json` is publicly accessible
   - Test in an incognito/private browser window

2. **Check API Key**
   - Verify your API key is correct
   - No extra spaces or characters

3. **Check Domain Format**
   - Include the protocol: `https://yourdomain.com`
   - No trailing slash

4. **Check Firewall/Security**
   - Ensure IAIndex servers can access your site
   - Check security plugins aren't blocking requests

### Webhook Not Receiving Receipts

If receipts aren't being received:

1. **Check Endpoint**
   - Verify endpoint is accessible: `/wp-json/iaindex/v1/receipt`
   - Should return 401 without authentication

2. **Check API Key**
   - Webhook uses API key for authentication
   - Ensure it matches your IAIndex account

3. **Check Logs**
   - Enable WordPress debug logging
   - Check for errors in wp-content/debug.log

### No Posts in Index

If index is empty:

1. **Check Post Status**
   - Only published posts are included
   - Drafts and private posts are excluded

2. **Check Post Type**
   - Only standard posts are included by default
   - Pages and custom post types are not included

3. **Regenerate Index**
   - Click "Generate Index Now"
   - Check the entries count in the success message

## Security Notes

1. **API Key Protection**
   - API keys are stored in the WordPress database
   - Only administrators can view/edit settings
   - Use HTTPS to protect data in transit

2. **Nonce Verification**
   - All AJAX requests use WordPress nonces
   - Prevents CSRF attacks

3. **Capability Checks**
   - All admin functions check for `manage_options` capability
   - Regular users cannot access settings

4. **Input Sanitization**
   - All user inputs are sanitized
   - Outputs are escaped

## Uninstallation

To remove the plugin:

1. **Deactivate**
   - Go to **Plugins** > **Installed Plugins**
   - Click **Deactivate** under IAIndex Integration

2. **Delete**
   - Click **Delete** to remove plugin files
   - Note: This keeps your settings and receipts in the database

3. **Clean Up (Optional)**
   ```bash
   # Remove generated index file
   rm -rf /path/to/wordpress/wp-content/uploads/iaindex/
   ```

4. **Remove Database Entries (Optional)**
   - Settings are stored in `wp_options` table as `iaindex_settings`
   - Receipts are stored as custom post type `iaindex_receipt`
   - Use a database plugin or phpMyAdmin to remove if desired

## Support

For help and support:

- **Documentation**: https://docs.aiindex.io
- **API Documentation**: https://api.aiindex.io/docs
- **GitHub Issues**: https://github.com/claimtec/iaindex/issues

## Updates

To update the plugin:

1. Download the latest version
2. Deactivate the current version
3. Replace plugin files
4. Reactivate the plugin
5. Check settings and verify everything works

## Additional Resources

- IAIndex Website: https://aiindex.io
- WordPress Codex: https://codex.wordpress.org
- REST API Handbook: https://developer.wordpress.org/rest-api/

## Version

Current Version: 1.0.0
Release Date: 2025-01-17
