# AI Index - Ghost CMS Plugin

Make your Ghost blog discoverable by AI assistants like ChatGPT, Claude, and others.

## Features

- **Automatic AI Index Generation**: Generates `/ai-index.json` from your Ghost content
- **Real-time Updates**: Auto-syncs when content is published/unpublished
- **LLM Access Webhooks**: Receive notifications when AI assistants access your content
- **Analytics Dashboard**: Track AI engagement in Ghost Admin
- **Zero Configuration**: Works out of the box after installation
- **Lightweight**: Minimal performance impact

## Installation

### Method 1: Via Ghost CLI (Recommended)

```bash
# Navigate to your Ghost installation
cd /var/www/ghost

# Install the plugin
ghost install @iaindex/ghost-plugin

# Restart Ghost
ghost restart
```

### Method 2: Manual Installation

1. **Download the plugin**:
   ```bash
   cd /var/www/ghost/content/plugins
   git clone https://github.com/yourusername/ai-index.git ghost-ai-index
   cd ghost-ai-index/packages/ghost-plugin
   npm install
   ```

2. **Activate the plugin**:
   Edit your Ghost config file (`config.production.json`):
   ```json
   {
     "plugins": {
       "ghost-ai-index": true
     }
   }
   ```

3. **Restart Ghost**:
   ```bash
   ghost restart
   ```

### Method 3: Docker

Add to your `docker-compose.yml`:

```yaml
services:
  ghost:
    image: ghost:latest
    volumes:
      - ./ghost-ai-index:/var/lib/ghost/content/plugins/ghost-ai-index
```

## Usage

### Access the AI Index

Once installed, your AI Index is automatically available at:

```
https://yourblog.com/ai-index.json
```

### View Analytics Dashboard

1. Log in to Ghost Admin
2. Navigate to "Settings" → "Integrations"
3. Find "AI Index" in the list
4. Click "Configure" to open the dashboard

### Configure Webhooks

To receive notifications when AI assistants access your content:

1. Set the `AIINDEX_WEBHOOK_URL` environment variable:
   ```bash
   export AIINDEX_WEBHOOK_URL=https://your-api.com/webhook
   ```

2. Or add to your Ghost config:
   ```json
   {
     "aiindex": {
       "webhook_url": "https://your-api.com/webhook"
     }
   }
   ```

## AI Index Structure

The generated `/ai-index.json` includes all your published content:

```json
{
  "version": "1.0",
  "publisher": {
    "id": "yourblog.com",
    "name": "Your Blog",
    "description": "Your blog description",
    "domain": "yourblog.com",
    "type": "blog",
    "platform": "ghost",
    "logo": "https://yourblog.com/logo.png",
    "icon": "https://yourblog.com/icon.png"
  },
  "content": {
    "posts": [
      {
        "id": "post-id",
        "uuid": "post-uuid",
        "title": "Post Title",
        "slug": "post-slug",
        "excerpt": "Post excerpt...",
        "content": "Post content preview...",
        "url": "https://yourblog.com/post-slug/",
        "featured": false,
        "feature_image": "https://yourblog.com/content/images/image.jpg",
        "published_at": "2025-01-15T10:30:00.000Z",
        "updated_at": "2025-01-15T10:30:00.000Z",
        "authors": [
          {
            "id": "author-id",
            "name": "Author Name",
            "slug": "author-slug",
            "profile_image": "https://yourblog.com/content/images/author.jpg"
          }
        ],
        "tags": [
          {
            "id": "tag-id",
            "name": "Tag Name",
            "slug": "tag-slug"
          }
        ],
        "primary_tag": {
          "id": "tag-id",
          "name": "Primary Tag",
          "slug": "primary-tag"
        }
      }
    ],
    "pages": [
      {
        "id": "page-id",
        "title": "Page Title",
        "slug": "page-slug",
        "excerpt": "Page excerpt...",
        "url": "https://yourblog.com/page-slug/",
        "published_at": "2025-01-15T10:30:00.000Z"
      }
    ]
  },
  "metadata": {
    "generated_at": "2025-01-15T10:30:00.000Z",
    "total_posts": 50,
    "total_pages": 5,
    "ghost_version": "5.0.0"
  },
  "access": {
    "webhook_url": "https://yourblog.com/api/aiindex/access",
    "verification_required": true,
    "rate_limit": {
      "requests_per_hour": 100,
      "burst": 10
    }
  }
}
```

## API Endpoints

### GET /ai-index.json

Returns the complete AI Index JSON for your site.

**Response**: `200 OK`
```json
{
  "version": "1.0",
  "publisher": {...},
  "content": {...},
  "metadata": {...},
  "access": {...}
}
```

### POST /api/aiindex/access

Webhook endpoint to receive LLM access notifications.

**Request Body**:
```json
{
  "llm_provider": "openai-chatgpt",
  "content_accessed": ["post-id-1", "post-id-2"],
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {
    "user_query": "What are your latest posts about AI?",
    "response_included": true
  }
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "receipt_id": "receipt_1234567890"
}
```

## Events

The plugin listens to Ghost events and auto-updates the index:

- `post.published` - When a post is published
- `post.unpublished` - When a post is unpublished
- `page.published` - When a page is published
- `page.unpublished` - When a page is unpublished

## Architecture

```
ghost-plugin/
├── index.js              # Main plugin entry point
├── lib/
│   ├── generator.js      # AI Index generation logic
│   ├── receipts.js       # Access receipt management
│   └── webhooks.js       # Content update handlers
├── admin/
│   └── index.html        # Admin dashboard UI
├── package.json
├── ghost.json            # Ghost plugin metadata
└── README.md
```

## Configuration

### Environment Variables

- `AIINDEX_WEBHOOK_URL` - External webhook URL for content updates

### Ghost Config

Add to `config.production.json`:

```json
{
  "aiindex": {
    "enabled": true,
    "webhook_url": "https://your-api.com/webhook",
    "cache_ttl": 300,
    "rate_limit": {
      "requests_per_hour": 100,
      "burst": 10
    }
  }
}
```

## Analytics

The plugin tracks AI assistant access to your content:

- **Total Accesses**: Count of all AI accesses
- **By Provider**: Breakdown by LLM provider (ChatGPT, Claude, etc.)
- **By Date**: Daily access trends
- **Recent Accesses**: Last 50 access logs

Access analytics in the Ghost Admin dashboard under Integrations.

## Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-index.git
cd ai-index/packages/ghost-plugin

# Install dependencies
npm install

# Link to your Ghost installation
ln -s $(pwd) /var/www/ghost/content/plugins/ghost-ai-index

# Restart Ghost
cd /var/www/ghost
ghost restart

# Watch logs
ghost log
```

### Testing

```bash
# Test AI Index generation
curl https://localhost:2368/ai-index.json

# Test webhook endpoint
curl -X POST https://localhost:2368/api/aiindex/access \
  -H "Content-Type: application/json" \
  -d '{
    "llm_provider": "openai-chatgpt",
    "content_accessed": ["test-post-id"],
    "timestamp": "2025-01-15T10:30:00Z"
  }'
```

## Troubleshooting

### AI Index not accessible

1. Check that the plugin is activated:
   ```bash
   ghost ls
   ```

2. Verify Ghost logs:
   ```bash
   ghost log
   ```

3. Check file permissions:
   ```bash
   ls -la /var/www/ghost/content/plugins/
   ```

### Content not updating

1. Check Ghost events are firing:
   - Publish a post and check logs
   - Look for "Content update: post" messages

2. Clear Ghost cache:
   ```bash
   ghost restart
   ```

### Webhook not receiving data

1. Verify webhook URL is set:
   ```bash
   echo $AIINDEX_WEBHOOK_URL
   ```

2. Test webhook endpoint manually:
   ```bash
   curl -X POST $AIINDEX_WEBHOOK_URL \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

3. Check Ghost can reach external URLs (firewall/network)

## Performance

The plugin is designed to be lightweight:

- **Index Generation**: ~50ms for 100 posts
- **Memory Usage**: <5MB
- **Database Queries**: Optimized with Ghost's built-in caching
- **No Frontend Impact**: All processing happens server-side

## Security

- Webhook endpoints use Ghost's built-in authentication
- Rate limiting prevents abuse
- Access logs stored securely in Ghost database
- No external API calls (except configured webhooks)

## Compatibility

- **Ghost Version**: 5.0.0 or higher
- **Node.js**: 16.0.0 or higher
- **Database**: MySQL or SQLite (as supported by Ghost)

## Support

- **Documentation**: [Full docs](https://docs.example.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-index/issues)
- **Forum**: [Ghost Forum](https://forum.ghost.org)
- **Email**: support@example.com

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT

## Credits

Built with love for the Ghost community.
