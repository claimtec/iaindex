# IAIndex v2.0 API Quick Reference

Base URL: `https://api.iaindex.org`

## Authentication

All endpoints require authentication via:
- **API Key**: `X-API-Key: your_api_key` header
- **JWT Token**: `Authorization: Bearer your_jwt_token` header

## Schema Endpoints

### Generate Schema Markup
```http
POST /v1/schema/generate
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "url": "https://example.com",
  "business_name": "Example Business",
  "business_type": "LocalBusiness",
  "location": {
    "address": "123 Main St",
    "city": "Cape Town",
    "country": "South Africa"
  }
}
```

**Response (200):**
```json
{
  "schema_markup": {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Example Business",
    "address": {...},
    "contactPoint": {...}
  },
  "recommendations": [
    {
      "type": "schema",
      "priority": "high",
      "title": "Add FAQ schema markup",
      "description": "FAQ schema is highly visible in AI search results",
      "action_items": ["Create FAQPage schema", "Include common questions"],
      "impact_score": 80
    }
  ],
  "scraped_data": {
    "title": "Example Business - Home",
    "description": "Welcome to Example Business",
    "has_existing_schema": false
  },
  "generated_at": "2025-01-15T10:30:00Z"
}
```

### Validate Schema
```http
POST /v1/schema/validate
Content-Type: application/json

{
  "schema_markup": {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Example"
  }
}
```

**Response (200):**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Missing recommended 'description' field"],
  "score": 85
}
```

### Register Website
```http
POST /v1/schema/websites
Content-Type: application/json

{
  "domain": "example.com",
  "url": "https://example.com",
  "business_name": "Example Business",
  "business_type": "LocalBusiness",
  "keywords": ["example", "business", "service"]
}
```

**Response (201):**
```json
{
  "id": "uuid-here",
  "domain": "example.com",
  "url": "https://example.com",
  "business_name": "Example Business",
  "schema_markup": null,
  "visibility_score": 0,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### List Websites
```http
GET /v1/schema/websites?limit=10&offset=0
```

**Response (200):**
```json
{
  "websites": [...],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

### Get Website Schema
```http
GET /v1/schema/{website_id}
```

### Update Website
```http
PATCH /v1/schema/{website_id}
Content-Type: application/json

{
  "business_name": "New Name",
  "keywords": ["new", "keywords"]
}
```

## Visibility Endpoints

### Check AI Visibility
```http
POST /v1/visibility/check
Content-Type: application/json

{
  "website_id": "uuid-here",
  "queries": [
    "example business near me",
    "best example service"
  ],
  "platforms": ["chatgpt", "perplexity"]
}
```

**Response (200):**
```json
{
  "visibility_score": 65,
  "mentions": [
    {
      "platform": "chatgpt",
      "query": "example business near me",
      "mentioned": true,
      "position": 2,
      "context_snippet": "Example Business is a leading provider...",
      "visibility_score": 80
    },
    {
      "platform": "perplexity",
      "query": "best example service",
      "mentioned": false,
      "position": null,
      "context_snippet": null,
      "visibility_score": 0
    }
  ],
  "platform_scores": [
    {
      "platform": "chatgpt",
      "score": 80,
      "mentions_count": 1,
      "total_queries": 2
    },
    {
      "platform": "perplexity",
      "score": 50,
      "mentions_count": 0,
      "total_queries": 2
    }
  ],
  "checked_at": "2025-01-15T10:35:00Z"
}
```

**Rate Limit:** 10 checks per hour per user

### Get Latest Visibility
```http
GET /v1/visibility/{website_id}
```

**Response (200):**
```json
{
  "current": {
    "visibility_score": 65,
    "mentions": [...],
    "checked_at": "2025-01-15T10:35:00Z"
  },
  "history": {
    "checks": [
      {
        "visibility_score": 58,
        "checked_at": "2025-01-08T10:30:00Z"
      },
      {
        "visibility_score": 65,
        "checked_at": "2025-01-15T10:35:00Z"
      }
    ],
    "average_score": 61,
    "trend": "improving",
    "change_percentage": 12.1
  }
}
```

### Get Visibility History
```http
GET /v1/visibility/{website_id}/history?days=30
```

**Response (200):**
```json
{
  "checks": [...],
  "average_score": 61,
  "trend": "improving",
  "change_percentage": 12.1,
  "total_checks": 15
}
```

### Get Platform-Specific Data
```http
GET /v1/visibility/{website_id}/platforms/chatgpt
```

**Response (200):**
```json
{
  "platform": "chatgpt",
  "latest_score": 80,
  "average_score": 75,
  "total_mentions": 45,
  "total_checks": 60,
  "mention_rate": 0.75,
  "recent_checks": [...]
}
```

### List Supported Platforms
```http
GET /v1/visibility/platforms
```

**Response (200):**
```json
{
  "platforms": [
    {
      "id": "chatgpt",
      "name": "ChatGPT",
      "description": "OpenAI's ChatGPT with web browsing"
    },
    {
      "id": "perplexity",
      "name": "Perplexity AI",
      "description": "Perplexity AI search engine"
    },
    {
      "id": "claude",
      "name": "Claude",
      "description": "Anthropic's Claude AI assistant"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid URL format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Website not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Visibility checks limited to 10 per hour."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to generate schema: Claude API timeout"
}
```

## Visibility Score Explained

**Visibility Score (0-100):**
- **0-30**: Poor visibility, rarely mentioned in AI responses
- **31-60**: Moderate visibility, occasionally mentioned
- **61-80**: Good visibility, frequently mentioned
- **81-100**: Excellent visibility, consistently mentioned in top positions

**Score Calculation:**
```
Platform Score = (
  (mentions / total_queries) * 50 +
  (avg_position_score) * 30 +
  (context_quality) * 20
)

Overall Score = average(all platform scores)
```

## Common Use Cases

### 1. Onboard New Website
```bash
# Step 1: Register website
POST /v1/schema/websites
{
  "domain": "example.com",
  "url": "https://example.com",
  "business_name": "Example Business"
}
# Get website_id from response

# Step 2: Generate schema
POST /v1/schema/generate
{
  "url": "https://example.com",
  "business_name": "Example Business"
}

# Step 3: Check visibility
POST /v1/visibility/check
{
  "website_id": "uuid-from-step-1",
  "queries": ["example business"]
}
```

### 2. Monitor Visibility Over Time
```bash
# Weekly check (run via cron/scheduler)
POST /v1/visibility/check
{
  "website_id": "uuid",
  "queries": ["brand name", "service + location"]
}

# View trends
GET /v1/visibility/{website_id}/history?days=90
```

### 3. Improve Visibility Score
```bash
# Get current status
GET /v1/visibility/{website_id}

# Generate optimized schema
POST /v1/schema/generate

# Apply recommendations (client-side)

# Re-check after 7 days
POST /v1/visibility/check
```

## SDK Examples

### Node.js
```javascript
import { IAIndexClient } from 'iaindex-sdk';

const client = new IAIndexClient({
  apiBaseUrl: 'https://api.iaindex.org',
  apiKey: 'your_api_key'
});

// Generate schema
const result = await client.generateSchema({
  url: 'https://example.com',
  businessName: 'Example Business'
});

// Check visibility
const visibility = await client.checkVisibility({
  websiteId: 'uuid',
  queries: ['example business near me']
});

console.log(`Visibility Score: ${visibility.visibility_score}`);
```

### Python
```python
from aiindex import IAIndexClient

client = IAIndexClient(
    api_base_url="https://api.iaindex.org",
    api_key="your_api_key"
)

# Generate schema
result = client.generate_schema(
    url="https://example.com",
    business_name="Example Business"
)

# Check visibility
visibility = client.check_visibility(
    website_id="uuid",
    queries=["example business near me"]
)

print(f"Visibility Score: {visibility['visibility_score']}")
```

## Rate Limits

- Schema generation: 100/hour per user
- Schema validation: 1000/hour per user
- Visibility checks: **10/hour per user** (expensive AI API calls)
- Website CRUD: 1000/hour per user

## Webhooks (Coming Soon)

Subscribe to events:
- `visibility.score_improved` - Score increased by >10 points
- `visibility.score_dropped` - Score decreased by >10 points
- `schema.recommendation_available` - New optimization recommendations
