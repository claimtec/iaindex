# IAIndex WordPress Plugin

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![WordPress](https://img.shields.io/badge/WordPress-6.0%2B-blue)
![PHP](https://img.shields.io/badge/PHP-7.4%2B-purple)
![License](https://img.shields.io/badge/license-GPL%20v2-green)

Official WordPress plugin for integrating with IAIndex - AI content tracking and verification platform.

## Overview

The IAIndex WordPress plugin automatically generates an index of your published content and provides receipt tracking capabilities for AI-generated content. It integrates seamlessly with the IAIndex API to verify your domain and receive blockchain-backed receipts.

## Features

- **Automatic Index Generation**: Creates and maintains an index of all published posts
- **Domain Verification**: One-click domain verification with IAIndex
- **Receipt Tracking**: Receives and stores blockchain-backed content receipts
- **Dashboard Widget**: Quick overview of status and statistics
- **REST API Integration**: Webhook endpoint for receiving receipts
- **Auto-Update**: Index regenerates automatically when posts are published
- **.well-known Support**: Serves index at standard `/.well-known/iaindex.json` location

## Requirements

- WordPress 6.0 or higher
- PHP 7.4 or higher
- IAIndex API key ([Get one here](https://aiindex.io))
- HTTPS-enabled website (recommended)
- Write permissions to `wp-content/uploads` directory

## Quick Start

```bash
# 1. Install plugin
cp -r wordpress-plugin /path/to/wordpress/wp-content/plugins/iaindex

# 2. Activate in WordPress admin
# Go to Plugins → Activate "IAIndex Integration"

# 3. Configure
# Go to Settings → IAIndex
# Enter your domain and API key
# Click "Verify Domain" then "Generate Index"
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## Installation

### Method 1: WordPress Admin Upload

1. Zip the plugin folder
2. Go to WordPress Admin → Plugins → Add New → Upload Plugin
3. Choose the zip file and click Install Now
4. Click Activate Plugin

### Method 2: Manual Installation

```bash
# Copy plugin to WordPress
cp -r wordpress-plugin /path/to/wordpress/wp-content/plugins/iaindex

# Set permissions
chmod -R 755 /path/to/wordpress/wp-content/plugins/iaindex

# Activate via WordPress Admin → Plugins
```

See [INSTALLATION.md](INSTALLATION.md) for complete installation guide.

## Configuration

After activation:

1. Navigate to **Settings → IAIndex**
2. Configure your settings:
   - **Domain**: Your website URL (auto-detected)
   - **API Key**: Your IAIndex API key
   - **Auto-Generate**: Enable automatic index updates
3. Click **Save Settings**
4. Click **Verify Domain** to verify with IAIndex
5. Click **Generate Index** to create your first index

## Usage

### Automatic Mode (Recommended)

With auto-generation enabled:
- Publish posts normally
- Index updates automatically
- No manual intervention needed

### Manual Mode

With auto-generation disabled:
- Publish posts normally
- Go to Settings → IAIndex
- Click "Generate Index Now" when ready

### Viewing Your Index

Your index is accessible at:
```
https://yourdomain.com/.well-known/iaindex.json
```

### Checking Receipts

View received receipts:
1. Go to **Tools → IAIndex Receipts**
2. Or click **View Receipts** from dashboard widget

## File Structure

```
wordpress-plugin/
├── iaindex.php                 # Main plugin file
├── README.md                   # This file
├── QUICKSTART.md              # Quick start guide
├── INSTALLATION.md            # Detailed installation guide
├── TECHNICAL.md               # Technical documentation
├── readme.txt                 # WordPress.org readme
├── admin/
│   ├── settings.php           # Settings page
│   └── dashboard.php          # Dashboard widget
├── includes/
│   ├── api-client.php         # API client wrapper
│   ├── index-generator.php    # Index generation logic
│   └── webhook.php            # REST API endpoints
└── assets/
    ├── css/
    │   └── admin.css          # Admin styles
    └── js/
        └── admin.js           # Admin JavaScript
```

## API Endpoints

### Public Endpoint

**Index File**
```
GET /.well-known/iaindex.json
```
Returns the generated index of your content.

### REST API Endpoints

**Receive Receipt**
```bash
POST /wp-json/iaindex/v1/receipt
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "receiptId": "receipt-123",
  "contentUrl": "https://example.com/post",
  "timestamp": "2025-01-17T12:00:00Z",
  "provider": "OpenAI"
}
```

**Get Receipts**
```bash
GET /wp-json/iaindex/v1/receipts?limit=10
Authorization: WordPress Admin Session
```

## Index Format

The generated index follows the IAIndex v1.1 specification:

```json
{
  "domain": "example.com",
  "version": "1.1",
  "entries": [
    {
      "url": "https://example.com/post-slug",
      "title": "Post Title",
      "author": "Author Name",
      "publishedDate": "2025-01-17T12:00:00Z",
      "license": {
        "type": "CC-BY-4.0"
      },
      "description": "Post excerpt (optional)",
      "tags": ["Category1", "Category2"]
    }
  ],
  "generatedAt": "2025-01-17T12:00:00Z"
}
```

## Screenshots

### Settings Page
Configure your domain, API key, and verify your site with IAIndex.

![Settings Page - Configuration Section]

### Dashboard Widget
Quick overview of your IAIndex status, entries count, and receipts.

![Dashboard Widget]

### Index Management
Generate and manage your content index with one click.

![Index Management Section]

### Receipts List
View all blockchain-backed receipts received for your content.

![Receipts Admin Page]

## Security

The plugin implements WordPress security best practices:

- **Nonce Verification**: All AJAX requests use WordPress nonces
- **Capability Checks**: Admin functions require `manage_options` capability
- **Input Sanitization**: All user inputs are sanitized
- **Output Escaping**: All outputs are escaped
- **API Key Protection**: Keys stored securely in database
- **Webhook Authentication**: Bearer token verification for webhooks

See [TECHNICAL.md](TECHNICAL.md) for detailed security documentation.

## Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/claimtec/iaindex.git

# Navigate to plugin
cd iaindex/packages/wordpress-plugin

# Link to WordPress
ln -s $(pwd) /path/to/wordpress/wp-content/plugins/iaindex
```

### WordPress Coding Standards

This plugin follows WordPress Coding Standards:
- PHP: [WordPress PHP Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/)
- JavaScript: [WordPress JS Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/javascript/)
- CSS: [WordPress CSS Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/css/)

### Hooks & Filters

For developers extending the plugin:

```php
// Customize individual index entries
add_filter('iaindex_entry', function($entry, $post) {
    $entry['custom_field'] = get_post_meta($post->ID, 'custom', true);
    return $entry;
}, 10, 2);

// Customize full index data
add_filter('iaindex_data', function($iaindex) {
    $iaindex['custom_metadata'] = 'value';
    return $iaindex;
});

// Hook after index generation
add_action('iaindex_after_generate', function($result) {
    // Your code here
});

// Hook after receipt stored
add_action('iaindex_receipt_stored', function($receipt_id, $receipt_data) {
    // Your code here
}, 10, 2);
```

## Troubleshooting

### Index Returns 404

1. Go to Settings → Permalinks → Save Changes
2. Check file exists at `wp-content/uploads/iaindex/iaindex.json`
3. Verify file permissions (644)

### Domain Verification Fails

1. Ensure index is publicly accessible
2. Check API key is correct
3. Verify domain format includes protocol (`https://`)
4. Test in incognito mode

### Receipts Not Received

1. Check webhook endpoint: `/wp-json/iaindex/v1/receipt`
2. Verify API key authentication
3. Check WordPress debug logs

See [INSTALLATION.md](INSTALLATION.md) for complete troubleshooting guide.

## FAQ

**Q: Does this work with custom post types?**
A: Currently only standard WordPress posts. Custom post type support coming in v1.1.

**Q: Can I customize the license type?**
A: Default is CC-BY-4.0. Customization coming in future version.

**Q: How often is the index updated?**
A: Automatically on post publish (if enabled) or manually on demand.

**Q: Is my API key secure?**
A: Yes, stored securely in WordPress database with proper access controls.

**Q: Does this work with multisite?**
A: Not yet - multisite support planned for future release.

**Q: Can I exclude certain posts?**
A: Not in v1.0 - post exclusion coming in future version.

## Roadmap

- [ ] v1.1: Custom post type support
- [ ] v1.1: Custom license type selection
- [ ] v1.2: Post exclusion filters
- [ ] v1.2: WP-CLI commands
- [ ] v1.3: Multisite support
- [ ] v1.3: Receipt notifications via email
- [ ] v1.4: Bulk operations interface
- [ ] v1.4: Export/import settings

## Support

### Documentation
- [Quick Start Guide](QUICKSTART.md)
- [Installation Guide](INSTALLATION.md)
- [Technical Documentation](TECHNICAL.md)
- [IAIndex Documentation](https://docs.aiindex.io)

### Getting Help
- GitHub Issues: https://github.com/claimtec/iaindex/issues
- IAIndex Support: support@aiindex.io
- WordPress Forums: [Coming Soon]

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow WordPress coding standards
4. Test thoroughly
5. Submit a pull request

## Changelog

### Version 1.0.0 (2025-01-17)

**Initial Release**
- Domain verification functionality
- Automatic index generation
- Receipt webhook handler
- Dashboard widget with statistics
- Settings page with AJAX controls
- REST API endpoints
- .well-known/iaindex.json support
- WordPress 6.0+ compatibility
- PHP 7.4+ compatibility

See [readme.txt](readme.txt) for complete changelog.

## License

This plugin is licensed under GPL v2 or later.

```
Copyright (C) 2025 ClaimTec

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
```

See [LICENSE](https://www.gnu.org/licenses/gpl-2.0.html) for full license text.

## Credits

Developed by [ClaimTec](https://claimtec.com) for the IAIndex platform.

### Built With
- WordPress Plugin API
- WordPress REST API
- WordPress HTTP API
- jQuery (for admin interface)

### Special Thanks
- WordPress community for excellent documentation
- IAIndex team for API support

## Links

- **IAIndex**: https://aiindex.io
- **API Documentation**: https://api.aiindex.io/docs
- **GitHub Repository**: https://github.com/claimtec/iaindex
- **WordPress Plugin Directory**: [Coming Soon]

---

**Made with ❤️ for the WordPress and AI communities**
