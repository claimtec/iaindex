# IAIndex CLI - Usage Guide

## Installation

### From Source

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
npm install
npm run build
```

### Link Globally (for development)

```bash
npm link
```

Now you can use `iaindex` command from anywhere.

## Quick Start

### 1. Check CLI is Working

```bash
iaindex --help
```

### 2. Generate Cryptographic Keys

Generate an RSA key pair for signing your attestations:

```bash
iaindex generate-keys -o ~/iaindex-keys -n mysite
```

This creates:
- `mysite-private.pem` - Keep this secure!
- `mysite-public.pem` - Include in your attestations

### 3. Create an IAIndex File

#### Option A: Interactive Mode

```bash
iaindex create-index --interactive
```

You'll be prompted for all required information.

#### Option B: From Config File

Create a `config.json`:

```json
{
  "url": "https://mysite.com/blog/article",
  "title": "My Article Title",
  "description": "Article description",
  "contentType": "article",
  "aiGenerated": {
    "percentage": 60,
    "sections": ["introduction", "main-content"]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "Your Name"
  },
  "publisher": {
    "name": "Your Company",
    "domain": "mysite.com"
  }
}
```

Then generate:

```bash
iaindex create-index config.json -s ~/iaindex-keys/mysite-private.pem -o iaindex.json
```

### 4. Upload to Your Website

Upload the generated `iaindex.json` to:

```
https://yourdomain.com/.well-known/iaindex.json
```

## Authentication (for API features)

Some commands require authentication with the IAIndex API.

### Login

```bash
iaindex auth login
```

You'll be prompted for email and password. Credentials are stored in `~/.iaindex/config.json`.

### Check Status

```bash
iaindex auth status
```

### Logout

```bash
iaindex auth logout
```

## Domain Verification

To verify ownership of your domain:

### 1. Initiate Verification

```bash
iaindex verify init yourdomain.com
```

Output:
```
✓ Verification initiated for yourdomain.com

Add this TXT record to your DNS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:  _iaindex-verification.yourdomain.com
Type:  TXT
Value: iaindex-verification=abc123def456...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Verification Token: xyz789...

Then run: iaindex verify check xyz789...
```

### 2. Add DNS Record

Add the TXT record to your DNS configuration.

### 3. Check Verification

```bash
iaindex verify check xyz789...
```

Output:
```
✓ Domain yourdomain.com is verified!
```

Note: DNS records can take up to 48 hours to propagate.

## Command Reference

### Authentication Commands

```bash
# Login to IAIndex
iaindex auth login

# Optional: provide credentials via flags
iaindex auth login -e user@example.com -p password

# Check authentication status
iaindex auth status

# Logout
iaindex auth logout
```

### Domain Verification

```bash
# Initialize domain verification
iaindex verify init <domain>

# Check verification status
iaindex verify check <token>
```

### Key Generation

```bash
# Generate RSA key pair
iaindex generate-keys [options]

Options:
  -o, --output <dir>   Output directory (default: current directory)
  -n, --name <name>    Base name for key files (default: "iaindex")

Example:
iaindex generate-keys -o ./keys -n production
```

### Index Creation

```bash
# Interactive mode
iaindex create-index --interactive

# From config file
iaindex create-index <config.json> [options]

Options:
  -i, --interactive      Use interactive mode
  -o, --output <file>    Output file path (default: "./iaindex.json")
  -s, --sign <key>       Path to private key for signing

Examples:
iaindex create-index config.json
iaindex create-index config.json -s ./keys/private.pem
iaindex create-index config.json -o ./output/index.json -s ./keys/private.pem
```

## Configuration File Format

Full configuration example:

```json
{
  "url": "https://example.com/content/123",
  "title": "Content Title",
  "description": "Optional description",
  "contentType": "article",
  "aiGenerated": {
    "percentage": 75,
    "sections": [
      "introduction",
      "main-content",
      "conclusion"
    ]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "Editor Name"
  },
  "sources": [
    {
      "type": "training-data",
      "description": "GPT-4"
    },
    {
      "type": "human-input",
      "description": "Original research"
    }
  ],
  "publisher": {
    "name": "Publisher Name",
    "domain": "example.com",
    "publicKey": "-----BEGIN PUBLIC KEY-----\n..."
  }
}
```

### Content Types

- `article` - Blog post or article
- `blog-post` - Blog post
- `documentation` - Technical documentation
- `code` - Code or scripts
- `image` - Generated images
- `video` - Video content
- `other` - Other content types

### Human Oversight Levels

- `full` - Complete human review and editing
- `partial` - Significant human input
- `minimal` - Light human review
- `none` - Fully automated

## File Locations

- Configuration: `~/.iaindex/config.json`
- Contains API endpoint and authentication token
- Can be edited manually if needed

## Examples

### Example 1: Blog Post with Full Human Oversight

```bash
# 1. Create config
cat > blog-post.json << 'EOF'
{
  "url": "https://myblog.com/posts/ai-future",
  "title": "The Future of AI",
  "contentType": "blog-post",
  "aiGenerated": {
    "percentage": 50,
    "sections": ["research", "examples"]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "Jane Smith"
  },
  "publisher": {
    "name": "My Blog",
    "domain": "myblog.com"
  }
}
EOF

# 2. Generate keys
iaindex generate-keys -o ./keys -n myblog

# 3. Create signed index
iaindex create-index blog-post.json -s ./keys/myblog-private.pem -o iaindex.json

# 4. Upload iaindex.json to https://myblog.com/.well-known/iaindex.json
```

### Example 2: Fully AI-Generated Documentation

```bash
# Interactive mode for quick setup
iaindex create-index --interactive

# Follow prompts:
# Content URL: https://docs.example.com/api
# Content Title: API Documentation
# Content Type: documentation
# AI-generated percentage: 80
# Oversight level: minimal
# Verified by: Auto-review system
```

### Example 3: Batch Processing Multiple Files

```bash
#!/bin/bash

# Generate keys once
iaindex generate-keys -o ./keys -n batch

# Process multiple content files
for config in configs/*.json; do
  basename=$(basename "$config" .json)
  iaindex create-index "$config" \
    -s ./keys/batch-private.pem \
    -o "output/${basename}-iaindex.json"
done
```

## Troubleshooting

### Authentication Issues

```bash
# Check if logged in
iaindex auth status

# Re-login if needed
iaindex auth logout
iaindex auth login
```

### Key Generation Issues

```bash
# Ensure output directory exists
mkdir -p ~/iaindex-keys

# Generate keys
iaindex generate-keys -o ~/iaindex-keys
```

### API Connection Issues

Check that the API is accessible:

```bash
curl https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/health
```

If you need to change the API endpoint, edit `~/.iaindex/config.json`:

```json
{
  "apiBaseUrl": "https://your-api-endpoint.com"
}
```

## Security Best Practices

1. **Private Keys**
   - Never commit private keys to version control
   - Store in secure locations with restricted permissions
   - Use different keys for production and testing

2. **Configuration**
   - Don't share `~/.iaindex/config.json` (contains auth token)
   - Rotate tokens periodically
   - Use environment-specific configurations

3. **Signing**
   - Always sign production attestations
   - Verify signatures before trusting attestations
   - Keep backup of your keys

## API Integration

The CLI uses the IAIndex API at:

```
https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

### Endpoints Used

- `POST /v1/auth/login` - Authentication
- `POST /v1/publishers/verify` - Initiate domain verification
- `GET /v1/publishers/verify/{token}` - Check verification status

## Development

### Build from Source

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
npm install
npm run build
```

### Run Tests

```bash
npm test
```

### Watch Mode

```bash
npm run dev
```

This watches for file changes and rebuilds automatically.

## Support

For issues or questions:
- Documentation: https://docs.iaindex.org
- GitHub Issues: https://github.com/iaindex/cli/issues
- API Status: Check Azure Container Apps status

## License

MIT
