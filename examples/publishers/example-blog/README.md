# Example Blog - WordPress Publisher

This is an example AIIndex implementation for a WordPress-powered tech blog.

## Overview

**Site**: Tech Insights Blog
**Domain**: example-blog.com
**Platform**: WordPress 6.4
**Content Type**: Technology articles and tutorials

## Setup Instructions

### 1. Install AIIndex WordPress Plugin

```bash
# Download the plugin
wget https://github.com/aiindex/wordpress-plugin/releases/latest/download/aiindex-wp.zip

# Upload to WordPress
wp plugin install aiindex-wp.zip --activate
```

### 2. Configure Plugin Settings

Navigate to **Settings > AIIndex** in WordPress admin:

- **Publisher ID**: example-blog.com
- **Domain**: example-blog.com
- **Enable Access Receipts**: Yes
- **Webhook URL**: https://example-blog.com/api/receipts
- **Attribution Required**: Yes
- **Commercial Use**: Allowed

### 3. Generate ai-index.json

The plugin automatically generates `ai-index.json` at:
```
https://example-blog.com/.well-known/ai-index.json
```

### 4. Verify Implementation

```bash
# Test the ai-index.json file
curl https://example-blog.com/.well-known/ai-index.json

# Verify with AIIndex validator
npx @aiindex/sdk-node validate https://example-blog.com
```

## Verification Badge Implementation

Add the verification badge to your site:

### In Theme (footer.php)

```html
<!-- AIIndex Verification Badge -->
<div class="aiindex-badge">
  <a href="https://aiindex.org/publishers/example-blog.com"
     target="_blank"
     rel="noopener">
    <img src="https://aiindex.org/badge.svg"
         alt="AIIndex Verified Publisher"
         width="120"
         height="40">
  </a>
</div>
```

### Using Shortcode

```
[aiindex_badge]
```

### Using Widget

Add the "AIIndex Badge" widget to your sidebar or footer widget area.

## Content Structure

### Published Articles (10)

1. **Introduction to AI Agents** (Oct 1, 2025)
   - Tags: AI, Agents, Automation, LLM
   - URL: /posts/introduction-to-ai-agents

2. **LangChain Best Practices** (Sep 28, 2025)
   - Tags: LangChain, Python, Best Practices, Production
   - URL: /posts/langchain-best-practices

3. **The Complete Guide to Prompt Engineering** (Sep 20, 2025)
   - Tags: Prompt Engineering, LLM, AI, GPT
   - URL: /posts/prompt-engineering-guide

4. **RAG Systems Explained** (Sep 15, 2025)
   - Tags: RAG, Vector Database, Embeddings, LLM
   - URL: /posts/rag-systems-explained

5. **Web Scraping Ethics and Best Practices** (Sep 10, 2025)
   - Tags: Web Scraping, Ethics, robots.txt
   - URL: /posts/web-scraping-ethics

6. **Vector Database Comparison** (Sep 5, 2025)
   - Tags: Vector Database, Pinecone, Weaviate, Qdrant
   - URL: /posts/vector-databases-comparison

7. **Building Production Chatbots with Claude AI** (Aug 30, 2025)
   - Tags: Claude, Chatbots, Anthropic
   - URL: /posts/building-chatbots-claude

8. **Mastering OpenAI Function Calling** (Aug 25, 2025)
   - Tags: OpenAI, Function Calling, GPT-4
   - URL: /posts/openai-function-calling

9. **About Tech Insights Blog**
   - URL: /about

10. **Contact Us**
    - URL: /contact

## Access Policy

- **AI Access**: Allowed
- **Attribution**: Required
- **Commercial Use**: Allowed
- **Receipts**: Required
- **Webhook**: https://example-blog.com/api/receipts

## Receipt Handling

The site accepts access receipts at the webhook endpoint. Example receipt:

```json
{
  "version": "1.0",
  "receipt_id": "550e8400-e29b-41d4-a716-446655440000",
  "publisher_id": "example-blog.com",
  "client_id": "openai-gpt4",
  "timestamp": "2025-10-13T10:00:00Z",
  "access": {
    "url": "https://example-blog.com/.well-known/ai-index.json",
    "status_code": 200
  },
  "purpose": {
    "type": "inference",
    "commercial": true
  }
}
```

## Testing

### Test AI Access

```bash
# Using AIIndex SDK
npx @aiindex/sdk-node crawl https://example-blog.com

# Send test receipt
curl -X POST https://example-blog.com/api/receipts \
  -H "Content-Type: application/json" \
  -d @test-receipt.json
```

### Validate ai-index.json

```bash
# Validate against schema
npx @aiindex/sdk-node validate https://example-blog.com

# Check signature
npx @aiindex/sdk-node verify https://example-blog.com
```

## WordPress Plugin Configuration

### Required Settings

```php
// wp-config.php additions
define('AIINDEX_PUBLISHER_ID', 'example-blog.com');
define('AIINDEX_WEBHOOK_URL', 'https://example-blog.com/api/receipts');
define('AIINDEX_AUTO_UPDATE', true);
```

### Filters and Hooks

```php
// Customize ai-index.json output
add_filter('aiindex_metadata', function($metadata) {
    $metadata['custom_field'] = 'custom_value';
    return $metadata;
});

// Handle receipt received
add_action('aiindex_receipt_received', function($receipt) {
    // Log receipt
    error_log('Receipt received: ' . $receipt['receipt_id']);
});
```

## Troubleshooting

### ai-index.json not updating

```bash
# Clear WordPress cache
wp cache flush

# Regenerate ai-index.json
wp aiindex regenerate
```

### Webhook not receiving receipts

1. Check webhook URL is publicly accessible
2. Verify SSL certificate is valid
3. Check server logs for errors
4. Test with curl:

```bash
curl -X POST https://example-blog.com/api/receipts \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## Resources

- [AIIndex WordPress Plugin Documentation](https://docs.aiindex.org/wordpress)
- [AIIndex Protocol Specification](https://aiindex.org/spec)
- [WordPress Codex](https://codex.wordpress.org/)
- [Publisher Dashboard](https://aiindex.org/dashboard)

## Support

For issues with this example:
- GitHub: https://github.com/aiindex/examples
- Docs: https://docs.aiindex.org
- Email: support@aiindex.org
