# AIIndex for WordPress

A comprehensive WordPress plugin that generates and manages AI index files for your website, enabling AI systems to discover, index, and verify your content.

## Features

### Core Functionality
- **Automatic Index Generation**: Auto-generates `/ai-index.json` from your WordPress content
- **Cryptographic Signing**: Signs index files with Ed25519 keys for verification
- **REST API**: Provides `/wp-json/aiindex/v1/receipt` endpoint to receive indexing receipts
- **Scheduled Sync**: Automatically syncs content using WordPress Cron
- **Content Control**: Choose which post types to include/exclude from the index

### Admin Features
- **Key Management**: Generate and manage cryptographic key pairs
- **Domain Verification**: Verify that your index is properly configured
- **Receipt Tracking**: Store and view all indexing receipts from AI systems
- **Analytics Dashboard**: View statistics on indexing activity
- **Export Receipts**: Export receipt data to CSV format
- **Dashboard Widget**: Quick overview of indexing statistics

### Public Features
- **Verification Badge**: Display an `[aiindex_badge]` shortcode to show verification status
- **Public Index**: Serve ai-index.json at your domain root
- **Per-Post Control**: Include/exclude individual posts/pages from the index

## Installation

1. Upload the `wp-plugin` folder to `/wp-content/plugins/`
2. Rename the folder to `aiindex`
3. Activate the plugin through the 'Plugins' menu in WordPress
4. Go to AIIndex settings to configure

## Requirements

- WordPress 5.0 or higher
- PHP 7.2 or higher (with Sodium extension for cryptographic signing)
- MySQL 5.6 or higher

## Configuration

### General Settings
1. Navigate to **AIIndex > Settings**
2. Enable AIIndex
3. Select content types (Posts/Pages)
4. Configure webhook URL (optional)
5. Set sync frequency

### Keys
1. Go to **AIIndex > Settings > Keys**
2. Click "Generate Keys"
3. Your public key will be displayed (share with AI indexers)
4. Private key is stored securely

### Verification
1. Go to **AIIndex > Settings > Verification**
2. Click "Verify Domain"
3. Ensures your ai-index.json is accessible

## Usage

### Index File
Your AI index is automatically available at:
```
https://yourdomain.com/ai-index.json
```

### REST API Endpoints

#### Receive Receipt
```bash
POST /wp-json/aiindex/v1/receipt
Content-Type: application/json

{
  "receiptId": "unique-id",
  "contentUrl": "https://yourdomain.com/post-url",
  "contentHash": "sha256-hash",
  "indexedAt": "2024-01-01T00:00:00Z",
  "indexer": {
    "name": "Indexer Name",
    "url": "https://indexer.com"
  }
}
```

#### Get Receipts (Admin Only)
```bash
GET /wp-json/aiindex/v1/receipts?limit=20&offset=0
Authorization: Bearer {admin-token}
```

#### Get Current Index
```bash
GET /wp-json/aiindex/v1/index
```

### Shortcode

Display a verification badge anywhere in your content:

```
[aiindex_badge]
```

Options:
- `style`: default, minimal, detailed
- `show_count`: true/false
- `show_status`: true/false

Example:
```
[aiindex_badge style="minimal" show_count="true"]
```

### Post Meta Box

When editing posts or pages, use the "AIIndex Settings" meta box to exclude specific content from the index.

## Database Tables

The plugin creates one table:

### wp_aiindex_receipts
Stores all indexing receipts received from AI systems.

Columns:
- `id`: Primary key
- `receipt_id`: Unique receipt identifier
- `content_url`: URL of indexed content
- `content_hash`: SHA-256 hash of content
- `indexed_at`: Timestamp of indexing
- `indexer_name`: Name of the indexer
- `indexer_url`: URL of the indexer
- `verification_status`: Status (verified/pending/failed)
- `metadata`: JSON metadata
- `created_at`: Receipt creation timestamp

## Hooks & Filters

### Actions
```php
// Before index generation
do_action('aiindex_before_generate');

// After index generation
do_action('aiindex_after_generate', $index_data);

// After receipt saved
do_action('aiindex_receipt_saved', $receipt_id, $receipt_data);
```

### Filters
```php
// Modify index content before signing
apply_filters('aiindex_content', $content);

// Modify complete index data
apply_filters('aiindex_index_data', $index_data);

// Customize badge HTML
apply_filters('aiindex_badge_html', $html, $atts);
```

## Security

- Uses WordPress nonces for all AJAX requests
- Prepared statements for all database queries
- Capability checks for admin functions
- Input sanitization and validation
- Cryptographic signing with Ed25519
- Secure key storage

## Development

### File Structure
```
wp-plugin/
├── aiindex.php                 # Main plugin file
├── includes/
│   ├── class-aiindex.php       # Core plugin class
│   ├── class-loader.php        # Hook loader
│   ├── class-i18n.php          # Internationalization
│   ├── class-activator.php     # Activation handler
│   ├── class-deactivator.php   # Deactivation handler
│   ├── class-generator.php     # Index generator
│   ├── class-signer.php        # Cryptographic signing
│   ├── class-receipts.php      # Receipt management
│   └── class-api.php           # REST API endpoints
├── admin/
│   ├── class-admin.php         # Admin functionality
│   ├── admin-settings.php      # Settings page template
│   ├── admin-receipts.php      # Receipts page template
│   └── assets/
│       ├── admin.css           # Admin styles
│       └── admin.js            # Admin scripts
├── public/
│   └── badge-shortcode.php     # Badge shortcode
├── languages/
│   └── aiindex.pot             # Translation template
└── README.md
```

## Changelog

### 1.0.0
- Initial release
- Core index generation
- Receipt tracking
- Admin interface
- REST API endpoints
- Verification badge shortcode
- Analytics dashboard

## Support

For support, please visit: https://aiindex.dev/support

## License

MIT License - See LICENSE file for details

## Credits

Developed by AIIndex
https://aiindex.dev
