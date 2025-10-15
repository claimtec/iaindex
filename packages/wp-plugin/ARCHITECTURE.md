# AIIndex WordPress Plugin Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        WordPress Core                            │
└────────────────┬────────────────────────────────┬────────────────┘
                 │                                 │
                 │                                 │
     ┌───────────▼───────────┐         ┌──────────▼──────────┐
     │   Admin Interface     │         │   Public Interface   │
     │                       │         │                      │
     │  ┌─────────────────┐  │         │  ┌────────────────┐ │
     │  │ Settings Page   │  │         │  │ ai-index.json  │ │
     │  │ - 4 Tabs        │  │         │  │ (JSON API)     │ │
     │  │ - Form Handler  │  │         │  └────────────────┘ │
     │  └─────────────────┘  │         │                      │
     │                       │         │  ┌────────────────┐ │
     │  ┌─────────────────┐  │         │  │ Badge          │ │
     │  │ Receipts Page   │  │         │  │ Shortcode      │ │
     │  │ - List View     │  │         │  └────────────────┘ │
     │  │ - Pagination    │  │         │                      │
     │  └─────────────────┘  │         │  ┌────────────────┐ │
     │                       │         │  │ REST API       │ │
     │  ┌─────────────────┐  │         │  │ Endpoints      │ │
     │  │ Dashboard       │  │         │  └────────────────┘ │
     │  │ Widget          │  │         └──────────────────────┘
     │  └─────────────────┘  │
     │                       │
     │  ┌─────────────────┐  │
     │  │ Post Meta Box   │  │
     │  └─────────────────┘  │
     └───────────┬───────────┘
                 │
                 │
     ┌───────────▼────────────────────────────────────────┐
     │              Core Plugin Classes                   │
     │                                                     │
     │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
     │  │  Generator   │  │   Signer     │  │ Receipts │ │
     │  │              │  │              │  │          │ │
     │  │ - Build JSON │  │ - Gen Keys   │  │ - Save   │ │
     │  │ - Get Posts  │  │ - Sign Data  │  │ - Query  │ │
     │  │ - Format     │  │ - Verify     │  │ - Export │ │
     │  └──────────────┘  └──────────────┘  └──────────┘ │
     │                                                     │
     │  ┌──────────────┐  ┌──────────────┐               │
     │  │     API      │  │    Loader    │               │
     │  │              │  │              │               │
     │  │ - Routes     │  │ - Hooks      │               │
     │  │ - Handlers   │  │ - Filters    │               │
     │  │ - Validate   │  │ - Actions    │               │
     │  └──────────────┘  └──────────────┘               │
     └─────────────────────────┬──────────────────────────┘
                               │
                               │
     ┌─────────────────────────▼──────────────────────────┐
     │              WordPress Database                     │
     │                                                     │
     │  ┌──────────────────────────────────────────────┐  │
     │  │  wp_aiindex_receipts                         │  │
     │  │                                              │  │
     │  │  - id (PK)                                   │  │
     │  │  - receipt_id (UNIQUE)                       │  │
     │  │  - content_url                               │  │
     │  │  - content_hash (INDEXED)                    │  │
     │  │  - indexed_at (INDEXED)                      │  │
     │  │  - indexer_name                              │  │
     │  │  - indexer_url                               │  │
     │  │  - verification_status                       │  │
     │  │  - metadata (JSON)                           │  │
     │  │  - created_at                                │  │
     │  └──────────────────────────────────────────────┘  │
     │                                                     │
     │  ┌──────────────────────────────────────────────┐  │
     │  │  wp_options                                  │  │
     │  │                                              │  │
     │  │  - aiindex_enabled                           │  │
     │  │  - aiindex_public_key                        │  │
     │  │  - aiindex_private_key                       │  │
     │  │  - aiindex_webhook_url                       │  │
     │  │  - aiindex_verification_status               │  │
     │  │  - ... (more settings)                       │  │
     │  └──────────────────────────────────────────────┘  │
     └─────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Index Generation Flow

```
User Request (GET /ai-index.json)
    │
    ▼
WordPress Template Redirect Hook
    │
    ▼
AIIndex::serve_ai_index_json()
    │
    ▼
AIIndex_Generator::generate()
    │
    ├──► Get Posts (if enabled)
    │    └──► Filter excluded posts
    │         └──► Format post data
    │              └──► Extract categories/tags
    │
    ├──► Get Pages (if enabled)
    │    └──► Filter excluded pages
    │         └──► Format page data
    │
    ▼
Build Index Array
    │
    ▼
AIIndex_Signer::sign_content()
    │
    ├──► Load private key
    ├──► JSON encode content
    └──► Generate Ed25519 signature
    │
    ▼
Add Signature to Index
    │
    ▼
Output JSON with Headers
    │
    ├──► Content-Type: application/json
    └──► Access-Control-Allow-Origin: *
```

### Receipt Processing Flow

```
AI Indexer (POST /wp-json/aiindex/v1/receipt)
    │
    │ {receiptId, contentUrl, contentHash, indexedAt, indexer}
    │
    ▼
WordPress REST API Router
    │
    ▼
AIIndex_API::receive_receipt()
    │
    ├──► Validate receipt data
    │    ├──► Check required fields
    │    ├──► Validate URL format
    │    └──► Validate date format
    │
    ▼
AIIndex_Receipts::save_receipt()
    │
    ├──► Sanitize input data
    ├──► Check for existing receipt
    │    │
    │    ├──► If exists: UPDATE
    │    └──► If new: INSERT
    │
    ▼
Database (wp_aiindex_receipts)
    │
    ▼
Return Success Response
```

### Scheduled Sync Flow

```
WordPress Cron (hourly/daily/twicedaily)
    │
    ▼
AIIndex::run_scheduled_sync()
    │
    ├──► Check webhook URL configured
    │
    ▼
AIIndex_Generator::generate()
    │
    ▼
Get Complete Index Data
    │
    ▼
wp_remote_post(webhook_url, index_data)
    │
    ▼
External Webhook Endpoint
```

### Key Generation Flow

```
Admin Clicks "Generate Keys"
    │
    ▼
AJAX Request (aiindex_generate_keys)
    │
    ├──► Verify nonce
    └──► Check capability (manage_options)
    │
    ▼
AIIndex_Admin::ajax_generate_keys()
    │
    ▼
AIIndex_Signer::generate_keys()
    │
    ├──► Check sodium extension
    ├──► Generate Ed25519 keypair
    │    └──► sodium_crypto_sign_keypair()
    │
    ├──► Extract public key
    │    └──► sodium_crypto_sign_publickey()
    │
    ├──► Extract secret key
    │    └──► sodium_crypto_sign_secretkey()
    │
    └──► Base64 encode both keys
    │
    ▼
Save to wp_options
    │
    ├──► aiindex_public_key
    └──► aiindex_private_key
    │
    ▼
Return Success Response
    │
    ▼
Display Keys in Admin (public only)
```

## Class Hierarchy

```
AIIndex (Main Plugin Class)
    │
    ├── Loads all dependencies
    ├── Registers hooks
    └── Initializes components
        │
        ├──► AIIndex_Loader (Hook Manager)
        │    └── Registers actions/filters
        │
        ├──► AIIndex_i18n (Internationalization)
        │    └── Loads text domain
        │
        ├──► AIIndex_Admin (Admin Interface)
        │    ├── Enqueues assets
        │    ├── Registers menus
        │    ├── Handles forms
        │    └── AJAX handlers
        │
        ├──► AIIndex_Generator (Index Generation)
        │    ├── get_content()
        │    ├── get_posts()
        │    ├── get_pages()
        │    └── format_post()
        │
        ├──► AIIndex_Signer (Cryptography)
        │    ├── generate_keys()
        │    ├── sign_content()
        │    └── verify_signature()
        │
        ├──► AIIndex_Receipts (Receipt Management)
        │    ├── save_receipt()
        │    ├── get_receipts()
        │    ├── get_analytics()
        │    └── export_to_csv()
        │
        └──► AIIndex_API (REST API)
             ├── register_routes()
             ├── receive_receipt()
             ├── get_receipts()
             └── get_index()
```

## Hook System

```
WordPress Lifecycle
    │
    ├──► plugins_loaded
    │    └── AIIndex_i18n::load_plugin_textdomain()
    │
    ├──► admin_menu
    │    └── AIIndex_Admin::add_plugin_admin_menu()
    │
    ├──► admin_init
    │    └── AIIndex_Admin::register_settings()
    │
    ├──► admin_enqueue_scripts
    │    ├── AIIndex_Admin::enqueue_styles()
    │    └── AIIndex_Admin::enqueue_scripts()
    │
    ├──► add_meta_boxes
    │    └── AIIndex_Admin::add_meta_box()
    │
    ├──► save_post
    │    └── AIIndex_Admin::save_meta_box()
    │
    ├──► wp_dashboard_setup
    │    └── AIIndex_Admin::add_dashboard_widget()
    │
    ├──► rest_api_init
    │    └── AIIndex_API::register_routes()
    │
    ├──► template_redirect
    │    └── AIIndex::serve_ai_index_json()
    │
    └──► aiindex_sync_cron (Custom)
         └── AIIndex::run_scheduled_sync()
```

## Security Architecture

```
Request → Nonce Verification → Capability Check → Sanitization → Processing → Escaping → Response

Admin Actions:
    ├──► wp_verify_nonce() checks nonce
    ├──► current_user_can('manage_options') checks permission
    ├──► sanitize_text_field() / esc_url_raw() cleans input
    └──► esc_html() / esc_attr() / esc_url() escapes output

Database Operations:
    ├──► $wpdb->prepare() for queries (SQL injection prevention)
    └──► Indexed columns for performance

Cryptography:
    ├──► Ed25519 for signing (modern, secure algorithm)
    ├──► Private key never displayed
    └──► Public key safe to share
```

## Performance Considerations

```
Index Generation:
    ├──► Runs on-demand (not cached)
    ├──► Filtered by exclusion meta
    └──► Optimized WordPress queries

Receipt Storage:
    ├──► Indexed database table
    ├──► Efficient queries with prepared statements
    └──► Optional cleanup of old receipts

Admin Interface:
    ├──► Assets loaded only on plugin pages
    ├──► AJAX for non-blocking operations
    └──► Pagination for large datasets

Cron Jobs:
    ├──► Scheduled in background
    ├──► No user-facing impact
    └──► Configurable frequency
```

## Extension Points

```
Custom Filters:
    ├──► 'aiindex_content' - Modify content before signing
    ├──► 'aiindex_index_data' - Modify complete index
    └──► 'aiindex_badge_html' - Customize badge output

Custom Actions:
    ├──► 'aiindex_before_generate' - Pre-generation hook
    ├──► 'aiindex_after_generate' - Post-generation hook
    └──► 'aiindex_receipt_saved' - After receipt processing

Custom Post Types:
    └──► Extend AIIndex_Generator to include custom types

Custom Receipt Processors:
    └──► Extend AIIndex_Receipts for custom handling
```

## File Loading Order

```
1. aiindex.php (Main plugin file)
   ├── Defines constants
   ├── Includes class-activator.php
   ├── Includes class-deactivator.php
   └── Includes class-aiindex.php

2. class-aiindex.php (Core class)
   ├── Includes class-loader.php
   ├── Includes class-i18n.php
   ├── Includes class-generator.php
   ├── Includes class-signer.php
   ├── Includes class-receipts.php
   ├── Includes class-api.php
   ├── Includes admin/class-admin.php
   └── Includes public/badge-shortcode.php

3. class-loader.php registers all hooks

4. Hook callbacks execute on WordPress lifecycle events
```

## Database Schema Details

```sql
CREATE TABLE wp_aiindex_receipts (
    id bigint(20) NOT NULL AUTO_INCREMENT,
    receipt_id varchar(255) NOT NULL,
    content_url text NOT NULL,
    content_hash varchar(64) NOT NULL,
    indexed_at datetime NOT NULL,
    indexer_name varchar(255) DEFAULT NULL,
    indexer_url text DEFAULT NULL,
    verification_status varchar(50) DEFAULT 'pending',
    metadata longtext DEFAULT NULL,
    created_at datetime DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY receipt_id (receipt_id),
    KEY content_hash (content_hash),
    KEY indexed_at (indexed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## API Request/Response Examples

### POST /wp-json/aiindex/v1/receipt

Request:
```json
{
  "receiptId": "unique-receipt-id-123",
  "contentUrl": "https://example.com/post-slug",
  "contentHash": "sha256-abc123def456",
  "indexedAt": "2024-01-01T12:00:00Z",
  "indexer": {
    "name": "ExampleIndexer",
    "url": "https://indexer.example.com"
  }
}
```

Response (Success):
```json
{
  "success": true,
  "message": "Receipt saved successfully",
  "id": 42
}
```

Response (Error):
```json
{
  "code": "invalid_receipt",
  "message": "Invalid receipt data",
  "status": 400
}
```

### GET /ai-index.json

Response:
```json
{
  "version": "1.0",
  "domain": "example.com",
  "siteName": "Example Site",
  "lastUpdated": "2024-01-01T12:00:00+00:00",
  "content": [
    {
      "url": "https://example.com/sample-post/",
      "title": "Sample Post",
      "content": "Post content here...",
      "lastModified": "2024-01-01T10:00:00+00:00",
      "contentType": "post",
      "author": "John Doe",
      "categories": ["Technology", "AI"],
      "tags": ["wordpress", "plugin"]
    }
  ],
  "publicKey": "base64-encoded-public-key",
  "signature": "base64-encoded-signature"
}
```
