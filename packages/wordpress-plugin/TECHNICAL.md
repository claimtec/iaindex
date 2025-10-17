# IAIndex WordPress Plugin - Technical Documentation

## Architecture Overview

The IAIndex WordPress plugin is built using WordPress best practices and follows a modular architecture.

## File Structure

```
iaindex/
├── iaindex.php                 # Main plugin bootstrap file
├── readme.txt                  # WordPress.org plugin readme
├── INSTALLATION.md            # Installation guide
├── TECHNICAL.md               # This file
├── admin/                     # Admin interface files
│   ├── settings.php           # Settings page UI and handlers
│   └── dashboard.php          # Dashboard widget and receipts UI
├── includes/                  # Core functionality
│   ├── api-client.php         # IAIndex API client wrapper
│   ├── index-generator.php    # Index generation logic
│   └── webhook.php            # REST API webhook endpoints
└── assets/                    # Frontend assets
    ├── css/
    │   └── admin.css          # Admin panel styles
    └── js/
        └── admin.js           # Admin panel JavaScript
```

## Core Components

### 1. Main Plugin File (`iaindex.php`)

**Purpose**: Bootstrap the plugin, register hooks, and load dependencies.

**Key Functions**:
- `iaindex_activate()`: Activation hook - creates directories, sets defaults
- `iaindex_deactivate()`: Deactivation hook - cleanup
- `iaindex_register_receipt_post_type()`: Registers custom post type for receipts
- `iaindex_enqueue_admin_assets()`: Loads CSS/JS in admin
- `iaindex_auto_generate_on_publish()`: Auto-generates index on post publish
- `iaindex_wellknown_redirect()`: Handles /.well-known/iaindex.json requests
- `iaindex_rewrite_rules()`: Adds rewrite rule for .well-known
- `iaindex_template_redirect()`: Serves the index file

**Constants**:
```php
IAINDEX_VERSION          // Plugin version
IAINDEX_PLUGIN_DIR       // Absolute path to plugin directory
IAINDEX_PLUGIN_URL       // URL to plugin directory
IAINDEX_API_BASE_URL     // IAIndex API base URL
```

### 2. API Client (`includes/api-client.php`)

**Class**: `IAIndex_API_Client`

**Purpose**: Wrapper for all IAIndex API interactions.

**Methods**:
- `__construct()`: Initializes API client with base URL and API key
- `set_api_key($api_key)`: Updates API key
- `request($endpoint, $method, $body)`: Generic API request handler
- `verify_domain($domain)`: POST /v1/publishers/verify
- `submit_receipt($receipt_data)`: POST /v1/receipts/submit
- `get_publisher_status($domain)`: GET /v1/publishers/{domain}
- `get_receipts($domain, $limit)`: GET /v1/receipts
- `register_publisher($data)`: POST /v1/publishers/register
- `check_index($index_url)`: POST /v1/publishers/check-index

**HTTP Client**: Uses WordPress HTTP API (`wp_remote_request()`)

**Authentication**: Bearer token in Authorization header

**Error Handling**: Returns array with success/error status and data

### 3. Index Generator (`includes/index-generator.php`)

**Class**: `IAIndex_Generator`

**Purpose**: Generates IAIndex JSON from WordPress posts.

**Methods**:
- `generate_index()`: Main generation method
  - Queries all published posts
  - Builds IAIndex structure
  - Saves to file system
  - Updates settings with metadata
- `get_index_path()`: Returns file system path to index
- `get_index_url()`: Returns public URL to index
- `index_exists()`: Checks if index file exists
- `get_stats()`: Returns index statistics

**Index Structure**:
```json
{
  "domain": "example.com",
  "version": "1.1",
  "entries": [
    {
      "url": "https://example.com/post-slug",
      "title": "Post Title",
      "author": "Author Name",
      "publishedDate": "2025-01-15T10:00:00Z",
      "license": {"type": "CC-BY-4.0"},
      "description": "Optional excerpt",
      "tags": ["Category1", "Category2"]
    }
  ],
  "generatedAt": "2025-01-17T12:00:00Z"
}
```

**File Location**: `wp-content/uploads/iaindex/iaindex.json`

**WordPress Integration**:
- Uses `get_posts()` to query posts
- Uses `wp_upload_dir()` for file storage
- Uses `wp_mkdir_p()` for directory creation

### 4. Webhook Handler (`includes/webhook.php`)

**Purpose**: Handles incoming receipt webhooks via REST API.

**REST Endpoints**:

1. **Receive Receipt**
   - Route: `/wp-json/iaindex/v1/receipt`
   - Method: `POST`
   - Auth: Bearer token (API key)
   - Callback: `iaindex_handle_receipt_webhook()`
   - Permission: `iaindex_verify_webhook_request()`

2. **Get Receipts**
   - Route: `/wp-json/iaindex/v1/receipts`
   - Method: `GET`
   - Auth: WordPress admin
   - Callback: `iaindex_get_receipts()`
   - Permission: `manage_options` capability

**Functions**:
- `iaindex_register_rest_routes()`: Registers REST endpoints
- `iaindex_verify_webhook_request()`: Validates API key for webhooks
- `iaindex_handle_receipt_webhook()`: Processes incoming receipts
- `iaindex_store_receipt()`: Saves receipt as custom post type
- `iaindex_get_receipts()`: Returns stored receipts
- `iaindex_get_receipts_count()`: Counts total receipts

**Receipt Storage**:
- Custom post type: `iaindex_receipt`
- Post content: Full JSON data
- Post meta:
  - `_iaindex_receipt_id`: Receipt ID
  - `_iaindex_content_url`: Content URL
  - `_iaindex_timestamp`: Timestamp
  - `_iaindex_provider`: Provider name

### 5. Settings Page (`admin/settings.php`)

**Purpose**: Admin interface for plugin configuration.

**Functions**:
- `iaindex_add_settings_page()`: Registers settings page
- `iaindex_render_settings_page()`: Renders settings UI
- `iaindex_ajax_verify_domain()`: AJAX handler for domain verification
- `iaindex_ajax_generate_index()`: AJAX handler for index generation

**Settings Sections**:
1. Configuration - domain, API key, auto-generate toggle
2. Domain Verification - status and verify button
3. Index Management - status, stats, generate button

**AJAX Actions**:
- `wp_ajax_iaindex_verify_domain`: Verify domain
- `wp_ajax_iaindex_generate_index`: Generate index

**Security**:
- Nonce verification for form submissions
- Capability check: `manage_options`
- Input sanitization with `sanitize_text_field()`
- Output escaping with `esc_attr()`, `esc_html()`, `esc_url()`

### 6. Dashboard Widget (`admin/dashboard.php`)

**Purpose**: Display IAIndex status on WordPress dashboard.

**Functions**:
- `iaindex_add_dashboard_widget()`: Registers dashboard widget
- `iaindex_render_dashboard_widget()`: Renders widget content
- `iaindex_add_receipts_menu()`: Adds receipts to Tools menu
- `iaindex_receipts_columns()`: Customizes receipts list columns
- `iaindex_receipts_column_content()`: Populates custom columns

**Widget Displays**:
- Verification status (verified/not verified)
- Index entries count
- Receipts count
- Last generation time
- Quick action buttons

**Custom Post Type Columns**:
- Receipt ID
- Content URL
- Provider
- Timestamp
- Received date

### 7. Assets

**CSS (`assets/css/admin.css`)**:
- Grid layouts for settings page
- Status indicators (success/error/warning)
- Dashboard widget styles
- Responsive design
- WordPress admin color scheme integration

**JavaScript (`assets/js/admin.js`)**:
- AJAX handlers for verification and generation
- Loading states and spinners
- Password toggle for API key
- Success/error message display
- Copy-to-clipboard for code blocks
- Auto-hide success messages

## WordPress Hooks

### Actions

```php
// Activation/Deactivation
register_activation_hook(__FILE__, 'iaindex_activate')
register_deactivation_hook(__FILE__, 'iaindex_deactivate')

// Initialization
add_action('init', 'iaindex_register_receipt_post_type')
add_action('init', 'iaindex_wellknown_redirect', 1)
add_action('init', 'iaindex_rewrite_rules')

// Admin
add_action('admin_menu', 'iaindex_add_settings_page')
add_action('admin_enqueue_scripts', 'iaindex_enqueue_admin_assets')
add_action('wp_dashboard_setup', 'iaindex_add_dashboard_widget')

// Content
add_action('publish_post', 'iaindex_auto_generate_on_publish', 10, 2)

// Template
add_action('template_redirect', 'iaindex_template_redirect')

// REST API
add_action('rest_api_init', 'iaindex_register_rest_routes')

// AJAX
add_action('wp_ajax_iaindex_verify_domain', 'iaindex_ajax_verify_domain')
add_action('wp_ajax_iaindex_generate_index', 'iaindex_ajax_generate_index')
```

### Filters

```php
// Plugin links
add_filter('plugin_action_links_...', 'iaindex_add_settings_link')

// Query vars
add_filter('query_vars', 'iaindex_query_vars')

// Post type columns
add_filter('manage_iaindex_receipt_posts_columns', 'iaindex_receipts_columns')
add_action('manage_iaindex_receipt_posts_custom_column', 'iaindex_receipts_column_content', 10, 2)
```

## Database Schema

### Options Table

```sql
-- Plugin settings stored as serialized array
wp_options.option_name = 'iaindex_settings'
wp_options.option_value = {
  'domain': 'https://example.com',
  'api_key': 'your-api-key',
  'auto_generate': true,
  'verified': false,
  'verified_at': 1234567890,
  'last_generated': 1234567890,
  'entries_count': 42
}
```

### Posts Table

```sql
-- Receipts stored as custom post type
wp_posts.post_type = 'iaindex_receipt'
wp_posts.post_title = 'Receipt: receipt-id-123'
wp_posts.post_content = '{"receiptId":"...","contentUrl":"...","timestamp":"..."}'
wp_posts.post_status = 'publish'
```

### Post Meta

```sql
wp_postmeta.meta_key = '_iaindex_receipt_id'
wp_postmeta.meta_value = 'receipt-id-123'

wp_postmeta.meta_key = '_iaindex_content_url'
wp_postmeta.meta_value = 'https://example.com/post'

wp_postmeta.meta_key = '_iaindex_timestamp'
wp_postmeta.meta_value = '2025-01-17T12:00:00Z'

wp_postmeta.meta_key = '_iaindex_provider'
wp_postmeta.meta_value = 'OpenAI'
```

## Security Features

### 1. Authentication & Authorization

- **API Key Storage**: Stored in WordPress options table (not in code)
- **Capability Checks**: All admin functions require `manage_options`
- **Nonce Verification**: All AJAX requests use WordPress nonces
- **Webhook Authentication**: Bearer token verification for webhooks

### 2. Input Validation

```php
// Sanitization functions used:
sanitize_text_field()      // Text inputs
esc_url_raw()              // URLs
intval()                   // Integers
```

### 3. Output Escaping

```php
// Escaping functions used:
esc_html()                 // HTML content
esc_attr()                 // HTML attributes
esc_url()                  // URLs
```

### 4. File System Security

- Files written to WordPress uploads directory
- Directory permissions: 755
- File permissions: 644
- Directory creation uses `wp_mkdir_p()`

### 5. API Security

- HTTPS enforced for API communication
- Authorization headers for authentication
- Error responses don't expose sensitive data

## Performance Considerations

### 1. Index Generation

- Uses `posts_per_page: -1` to get all posts
- Consider pagination for sites with >1000 posts
- Cached in file system, not regenerated on every request

### 2. AJAX Requests

- Timeout: 30 seconds for API calls
- Loading states prevent duplicate requests
- Results cached in WordPress transients (future enhancement)

### 3. Database Queries

- Post queries use proper indexing
- Receipt counts use `wp_count_posts()`
- Minimal custom queries

### 4. Asset Loading

- CSS/JS only loaded on settings page
- Minification recommended for production
- No external dependencies (uses WordPress core)

## Customization Hooks

### For Developers

**Filter: Index Entries**
```php
add_filter('iaindex_entry', function($entry, $post) {
    // Customize individual entries
    $entry['custom_field'] = get_post_meta($post->ID, 'custom', true);
    return $entry;
}, 10, 2);
```

**Filter: Index Data**
```php
add_filter('iaindex_data', function($iaindex) {
    // Customize full index
    $iaindex['custom_metadata'] = 'value';
    return $iaindex;
});
```

**Action: After Index Generation**
```php
add_action('iaindex_after_generate', function($result) {
    // Do something after index is generated
    error_log('Index generated: ' . $result['entries_count'] . ' entries');
});
```

**Action: After Receipt Stored**
```php
add_action('iaindex_receipt_stored', function($receipt_id, $receipt_data) {
    // Do something when receipt is received
    wp_mail(get_option('admin_email'), 'Receipt Received', 'Receipt ID: ' . $receipt_id);
}, 10, 2);
```

## Testing

### Manual Testing Checklist

1. **Installation**
   - [ ] Plugin activates without errors
   - [ ] Settings page accessible
   - [ ] Dashboard widget appears
   - [ ] Directories created

2. **Configuration**
   - [ ] Settings save correctly
   - [ ] API key validates
   - [ ] Domain verification works
   - [ ] Error messages display

3. **Index Generation**
   - [ ] Manual generation works
   - [ ] Auto-generation on publish works
   - [ ] Index file created
   - [ ] Index accessible via URL

4. **Receipts**
   - [ ] Webhook endpoint responds
   - [ ] Authentication works
   - [ ] Receipts stored correctly
   - [ ] Receipts display in admin

5. **Security**
   - [ ] Non-admin cannot access settings
   - [ ] Nonce validation works
   - [ ] SQL injection protected
   - [ ] XSS protected

### API Testing

**Test Domain Verification:**
```bash
curl -X POST https://yourdomain.com/wp-json/iaindex/v1/verify \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Test Receipt Webhook:**
```bash
curl -X POST https://yourdomain.com/wp-json/iaindex/v1/receipt \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "receiptId": "test-123",
    "contentUrl": "https://example.com/test",
    "timestamp": "2025-01-17T12:00:00Z",
    "provider": "Test"
  }'
```

**Test Get Receipts:**
```bash
curl https://yourdomain.com/wp-json/iaindex/v1/receipts?limit=10 \
  -H "Cookie: wordpress_logged_in_..."
```

## Troubleshooting

### Debug Mode

Enable WordPress debug mode to see errors:

```php
// wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

Check logs at: `wp-content/debug.log`

### Common Issues

1. **Index 404**: Flush rewrite rules (save permalinks)
2. **Permission Denied**: Check file permissions
3. **API Errors**: Verify API key and network connectivity
4. **Empty Index**: Check that posts are published, not draft

## Future Enhancements

- [ ] Support for custom post types
- [ ] Batch index generation for large sites
- [ ] Index caching with transients
- [ ] Custom license type selection
- [ ] Multisite support
- [ ] WP-CLI commands
- [ ] Export/import settings
- [ ] Receipt notifications
- [ ] Advanced filtering for receipts
- [ ] Integration with popular page builders

## Resources

- WordPress Plugin Handbook: https://developer.wordpress.org/plugins/
- REST API Handbook: https://developer.wordpress.org/rest-api/
- WordPress Coding Standards: https://developer.wordpress.org/coding-standards/
- IAIndex API Documentation: https://api.aiindex.io/docs
