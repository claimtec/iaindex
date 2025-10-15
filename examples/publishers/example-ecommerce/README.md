# Example E-commerce - Shopify Publisher

This is an example AIIndex implementation for a Shopify-powered e-commerce store.

## Overview

**Store**: TechGear Shop
**Domain**: techgear-shop.com
**Platform**: Shopify
**Products**: Technology accessories and gadgets (150+ products)

## Setup Instructions

### 1. Install AIIndex Shopify App

```bash
# From Shopify App Store
1. Go to Shopify Admin > Apps
2. Search for "AIIndex"
3. Click "Add app"
4. Authorize the app
```

Or install from URL:
```
https://apps.shopify.com/aiindex
```

### 2. Configure App Settings

Navigate to **Apps > AIIndex** in Shopify admin:

#### Basic Settings
- **Publisher ID**: techgear-shop.com
- **Store Domain**: techgear-shop.com
- **Store Name**: TechGear Shop
- **Description**: Premium technology accessories for developers

#### Access Control
- **Enable AI Access**: Yes
- **Attribution Required**: Yes
- **Commercial Use**: Allowed
- **Receipt Required**: Yes
- **Webhook URL**: https://techgear-shop.com/api/aiindex/receipts

#### Product Settings
- **Include Product Descriptions**: Yes
- **Include Prices**: Yes
- **Include Inventory Status**: Yes
- **Include Product Images**: Yes
- **Update Frequency**: Daily

### 3. Select Products for AI Index

By default, all published products are included. To exclude specific products:

```javascript
// In product metafields
{
  "aiindex": {
    "exclude": false,
    "priority": "high",
    "ai_description": "Custom AI-optimized description"
  }
}
```

### 4. Generate ai-index.json

The app automatically generates and updates `ai-index.json` at:
```
https://techgear-shop.com/.well-known/ai-index.json
```

Auto-updates occur:
- When products are added/updated
- Daily at 3am UTC
- When manually triggered in app settings

### 5. Verify Implementation

```bash
# Test the ai-index.json file
curl https://techgear-shop.com/.well-known/ai-index.json

# Verify with AIIndex validator
npx @aiindex/sdk-node validate https://techgear-shop.com

# Check product data
curl https://techgear-shop.com/.well-known/ai-index.json | jq '.entities[] | select(.type=="Product")'
```

## Product Catalog

### Featured Products

1. **Mechanical Keyboard Pro** - $149.99
   - Cherry MX Blue switches
   - Per-key RGB lighting
   - USB-C connection
   - URL: /products/mechanical-keyboard-pro

2. **Wireless Mouse Elite** - $79.99
   - 16000 DPI sensor
   - Ergonomic design
   - 70-hour battery life
   - URL: /products/wireless-mouse-elite

3. **USB-C Hub Pro** - $59.99
   - 7-in-1 multiport adapter
   - 4K HDMI output
   - 100W power delivery
   - URL: /products/usb-c-hub-pro

4. **Laptop Stand Aluminum** - $49.99
   - Adjustable height and angle
   - Heat-dissipating design
   - Supports 10-17" laptops
   - URL: /products/laptop-stand-aluminum

5. **Webcam 4K Pro** - $129.99
   - 4K Ultra HD resolution
   - Auto-focus
   - Dual noise-cancelling microphones
   - URL: /products/webcam-4k-pro

### Product Collections

- **Keyboards** - /collections/keyboards
- **Mice & Trackpads** - /collections/mice
- **Adapters & Hubs** - /collections/accessories
- **Monitor Stands** - /collections/stands
- **Webcams & Audio** - /collections/audio-video

## Access Policy

- **AI Access**: Allowed
- **Attribution**: Required (cite as "TechGear Shop")
- **Commercial Use**: Allowed
- **Receipts**: Required via webhook
- **Product Recommendations**: Allowed with proper attribution

## Receipt Handling

### Webhook Endpoint

```
POST https://techgear-shop.com/api/aiindex/receipts
Content-Type: application/json
```

### Example Receipt

```json
{
  "version": "1.0",
  "receipt_id": "123e4567-e89b-12d3-a456-426614174000",
  "publisher_id": "techgear-shop.com",
  "publisher_domain": "techgear-shop.com",
  "client_id": "anthropic-claude",
  "client_name": "Claude AI",
  "timestamp": "2025-10-13T10:30:00Z",
  "access": {
    "url": "https://techgear-shop.com/.well-known/ai-index.json",
    "status_code": 200,
    "pages_accessed": [
      "https://techgear-shop.com/products/mechanical-keyboard-pro"
    ]
  },
  "purpose": {
    "type": "inference",
    "description": "Product recommendation for user query",
    "commercial": true
  },
  "attribution": {
    "method": "citation",
    "citation_text": "Product information from TechGear Shop"
  }
}
```

### Receipt Analytics

View receipt analytics in the Shopify app:
- Total receipts received
- Unique AI clients
- Popular products (by AI access)
- Revenue attribution (estimated)
- Receipt timeline

## Shopify Theme Integration

### Add Verification Badge to Footer

```liquid
<!-- In theme.liquid footer section -->
{% if shop.metafields.aiindex.verified %}
  <div class="aiindex-badge">
    <a href="https://aiindex.org/publishers/{{ shop.domain }}"
       target="_blank"
       rel="noopener">
      <img src="https://aiindex.org/badge.svg"
           alt="AIIndex Verified Publisher"
           loading="lazy"
           width="120"
           height="40">
    </a>
  </div>
{% endif %}
```

### Add to Product Pages

```liquid
<!-- In product.liquid template -->
<div class="product-meta">
  {% if product.metafields.aiindex.ai_friendly %}
    <span class="badge badge-ai">
      AI-Ready Product Data
    </span>
  {% endif %}
</div>
```

## Shopify App Features

### 1. Auto-Update Products
- Monitors product changes via webhooks
- Updates ai-index.json automatically
- Handles inventory updates
- Syncs pricing changes

### 2. Analytics Dashboard
- Receipt tracking
- AI client breakdown
- Product access metrics
- Revenue attribution

### 3. Custom Product Data
Add AI-optimized descriptions:

```javascript
// Set via Shopify Admin API
PUT /admin/api/2024-01/products/{product_id}/metafields.json
{
  "metafield": {
    "namespace": "aiindex",
    "key": "ai_description",
    "value": "AI-optimized product description",
    "type": "single_line_text_field"
  }
}
```

## Testing

### Test Product Access

```bash
# Get all products
curl https://techgear-shop.com/.well-known/ai-index.json | \
  jq '.entities[] | select(.type=="Product")'

# Test specific product
curl https://techgear-shop.com/.well-known/ai-index.json | \
  jq '.entities[] | select(.name=="Mechanical Keyboard Pro")'
```

### Send Test Receipt

```bash
curl -X POST https://techgear-shop.com/api/aiindex/receipts \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "receipt_id": "test-123",
    "publisher_id": "techgear-shop.com",
    "client_id": "test-client",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'
```

### Validate Schema

```bash
# Validate ai-index.json
npx @aiindex/sdk-node validate https://techgear-shop.com

# Check for errors
npx @aiindex/sdk-node validate https://techgear-shop.com --verbose
```

## API Integration

### Shopify Webhooks

The app subscribes to these webhooks:
- `products/create`
- `products/update`
- `products/delete`
- `collections/update`
- `inventory_levels/update`

### Manual Trigger

```bash
# Regenerate ai-index.json via API
POST https://techgear-shop.com/admin/apps/aiindex/regenerate
Authorization: Bearer {admin_api_token}
```

## Advanced Configuration

### Custom Filters

```javascript
// In app settings > Advanced
{
  "filters": {
    "exclude_tags": ["draft", "internal"],
    "min_price": 10,
    "in_stock_only": true,
    "collections": ["keyboards", "mice", "accessories"]
  }
}
```

### Custom Metadata

```javascript
{
  "metadata": {
    "shipping_regions": ["US", "CA", "EU"],
    "currency": "USD",
    "bulk_pricing": true,
    "api_available": true
  }
}
```

## Troubleshooting

### ai-index.json not updating

1. Check app status in Shopify Admin
2. Verify webhook subscriptions
3. Manually trigger regeneration:
   - Go to Apps > AIIndex
   - Click "Regenerate Now"

### Products not appearing

1. Ensure products are published
2. Check product tags (excluded tags)
3. Verify inventory status settings
4. Review app filters

### Receipt webhook failing

1. Check webhook URL is publicly accessible
2. Verify SSL certificate
3. Test endpoint with curl
4. Review Shopify app logs

## Best Practices

### 1. Product Descriptions
Write AI-friendly descriptions:
- Clear, concise product information
- Include key specifications
- Mention use cases
- Add comparison points

### 2. Product Organization
- Use consistent tagging
- Maintain accurate inventory
- Keep pricing up-to-date
- Organize collections logically

### 3. Receipt Handling
- Monitor receipt volume
- Track AI-attributed sales
- Respond to access patterns
- Optimize popular products

## Resources

- [AIIndex Shopify App Documentation](https://docs.aiindex.org/shopify)
- [Shopify API Documentation](https://shopify.dev/api)
- [Product Schema Best Practices](https://docs.aiindex.org/schemas/products)
- [Publisher Dashboard](https://aiindex.org/dashboard)

## Support

- Shopify App Support: apps@aiindex.org
- General AIIndex Support: support@aiindex.org
- Documentation: https://docs.aiindex.org
- Community Forum: https://community.aiindex.org
