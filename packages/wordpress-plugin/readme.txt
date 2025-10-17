=== IAIndex Integration ===
Contributors: claimtec
Tags: ai, content, blockchain, receipts, verification
Requires at least: 6.0
Tested up to: 6.4
Requires PHP: 7.4
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Integration with IAIndex for AI content tracking and verification with blockchain-backed receipts.

== Description ==

IAIndex Integration plugin helps you track and verify AI-generated content on your WordPress site with blockchain-backed receipts. This plugin automatically generates an index of your content and integrates with the IAIndex API for domain verification and receipt management.

**Key Features:**

* **Automatic Index Generation**: Automatically creates and updates an index of all your published posts
* **Domain Verification**: Verify your domain with IAIndex to establish trust
* **Receipt Tracking**: Receive and store blockchain-backed receipts for your content
* **Dashboard Widget**: Quick overview of your IAIndex status and statistics
* **API Integration**: Seamless integration with IAIndex API
* **REST API Webhook**: Endpoint for receiving receipts from IAIndex

**How It Works:**

1. Install and activate the plugin
2. Configure your domain and API key in Settings > IAIndex
3. Verify your domain with IAIndex
4. The plugin automatically generates an index from your published posts
5. The index is available at `/.well-known/iaindex.json`
6. Receive and track receipts via the webhook endpoint

**Requirements:**

* WordPress 6.0 or higher
* PHP 7.4 or higher
* Active IAIndex account with API key

== Installation ==

1. Upload the `iaindex` folder to the `/wp-content/plugins/` directory
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Navigate to Settings > IAIndex to configure the plugin
4. Enter your domain and API key
5. Click "Verify Domain" to complete setup
6. Click "Generate Index Now" to create your first index

== Frequently Asked Questions ==

= What is IAIndex? =

IAIndex is a platform for tracking and verifying AI-generated content using blockchain technology. It provides timestamped receipts that prove when and where content was created.

= Do I need an API key? =

Yes, you need an IAIndex API key to use this plugin. You can obtain one by registering at https://aiindex.io

= Where is the index file stored? =

The index file is stored in your WordPress uploads directory at `wp-content/uploads/iaindex/iaindex.json` and is accessible via `/.well-known/iaindex.json`

= Does the index update automatically? =

Yes, by default the index regenerates automatically whenever you publish a new post. You can disable this in the settings and generate manually instead.

= How do I receive receipts? =

Receipts are sent to your site via a webhook endpoint at `/wp-json/iaindex/v1/receipt`. They are automatically stored as custom post types and can be viewed in the admin panel.

= Is my content secure? =

The plugin only generates a public index of your already-published posts. No private content is exposed. The API key is stored securely in your WordPress database.

== Screenshots ==

1. Settings page with domain configuration and verification
2. Dashboard widget showing IAIndex status and statistics
3. Index management with generation controls
4. Receipts list in admin panel

== Changelog ==

= 1.0.0 =
* Initial release
* Domain verification functionality
* Automatic index generation
* Receipt webhook handler
* Dashboard widget
* Settings page
* REST API endpoints

== Upgrade Notice ==

= 1.0.0 =
Initial release of IAIndex Integration plugin.

== Configuration ==

After activation, configure the plugin:

1. Go to Settings > IAIndex
2. Enter your domain (usually auto-detected)
3. Enter your IAIndex API key
4. Click "Verify Domain"
5. Click "Generate Index Now"

The index will be available at: `https://yourdomain.com/.well-known/iaindex.json`

== API Endpoints ==

The plugin creates the following REST API endpoints:

* `POST /wp-json/iaindex/v1/receipt` - Receive receipt webhooks (requires API key authentication)
* `GET /wp-json/iaindex/v1/receipts` - Get stored receipts (admin only)

== Support ==

For support, please visit:
* Documentation: https://docs.aiindex.io
* GitHub: https://github.com/claimtec/iaindex

== Privacy Policy ==

This plugin:
* Stores API keys and settings in your WordPress database
* Generates a public index of published posts
* Receives and stores receipt data via webhooks
* Makes API calls to IAIndex servers (https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io)
* Does not collect any personal information from site visitors
* Does not use cookies or tracking

== Development ==

GitHub Repository: https://github.com/claimtec/iaindex
Report Issues: https://github.com/claimtec/iaindex/issues

== License ==

This plugin is licensed under the GPL v2 or later.

Copyright (C) 2025 ClaimTec

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
