# IAIndex Publisher Example (Node.js)

Complete working example demonstrating IAIndex publisher integration.

## Features

- Domain verification via DNS TXT record
- AI-Index file generation
- Receipt submission
- Analytics retrieval
- Verified domains listing

## Prerequisites

- Node.js 18+
- npm or yarn
- A domain you control (for verification)
- IAIndex API key

## Installation

```bash
# Install dependencies
npm install
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
API_BASE_URL=https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
API_KEY=your-api-key-here
PUBLISHER_DOMAIN=example.com
PUBLISHER_NAME=Your Publisher Name
PUBLISHER_EMAIL=contact@example.com
```

## Usage

### Step 1: Run the complete example

```bash
npm start
```

This will:
1. Initiate domain verification
2. Generate a sample AI-Index file
3. List verified domains

### Step 2: Verify your domain

After running the example, you'll receive DNS verification instructions. Add the TXT record to your DNS:

```
Type: TXT
Host: _iaindex-verification or @
Value: iaindex-verification=<your-token>
```

Wait for DNS propagation (typically 5-60 minutes), then check verification:

```bash
# Edit verify-domain.js to use your token
node verify-domain.js
```

### Step 3: Deploy AI-Index file

The example generates a sample `ai-index.json` file. Deploy this to your website root:

```
https://yourdomain.com/ai-index.json
```

Example structure:
```json
{
  "publisher": {
    "domain": "example.com",
    "name": "Example Publisher",
    "contact": "contact@example.com",
    "verified": true
  },
  "pages": [
    {
      "url": "https://example.com/article-1",
      "title": "Article Title",
      "description": "Article description",
      "published_date": "2025-01-15",
      "content_type": "article"
    }
  ],
  "version": "1.0"
}
```

### Step 4: Test receipt submission

Once your domain is verified, test receipt submission:

```bash
node test-receipt.js
```

### Step 5: View analytics

Check your analytics:

```bash
# The main script includes analytics retrieval
npm start
```

## API Endpoints Used

This example demonstrates these IAIndex API endpoints:

### Domain Verification
```
POST /v1/publishers/verify
GET  /v1/publishers/verify/{token}
GET  /v1/publishers/verified-domains
```

### Receipt Management
```
POST /v1/receipts/ingest
GET  /v1/receipts
```

### Analytics
```
GET /v1/analytics?domain={domain}
GET /v1/analytics/summary
```

## Code Structure

- `index.js` - Main example demonstrating complete integration
- `verify-domain.js` - Standalone domain verification checker
- `generate-index.js` - AI-Index file generator
- `test-receipt.js` - Receipt submission tester

## Authentication

The API supports two authentication methods:

1. **API Key** (recommended for publishers):
```javascript
headers: {
  'X-API-Key': 'your-api-key'
}
```

2. **JWT Bearer Token**:
```javascript
headers: {
  'Authorization': 'Bearer your-jwt-token'
}
```

## Error Handling

The example includes comprehensive error handling:

```javascript
try {
  const response = await api.post('/v1/publishers/verify', data);
  // Handle success
} catch (error) {
  console.error('Error:', error.response?.data || error.message);
}
```

## Common Issues

### 1. DNS Verification Not Working

- **Issue**: Verification check returns "Token not found"
- **Solution**:
  - Wait for DNS propagation (use `dig` or `nslookup` to check)
  - Ensure TXT record is added correctly
  - Try checking from different locations

### 2. Receipt Submission Fails

- **Issue**: Receipt rejected or signature verification fails
- **Solution**:
  - Ensure domain is verified first
  - Check signature generation matches API requirements
  - Verify timestamp format is ISO 8601

### 3. API Key Invalid

- **Issue**: 401 Unauthorized errors
- **Solution**:
  - Verify API key is set correctly in .env
  - Check API key hasn't expired
  - Contact support for new key

## Next Steps

1. **Production Deployment**:
   - Use environment variables for secrets
   - Implement proper signature generation
   - Add error monitoring

2. **Integration**:
   - Add to your CMS or static site generator
   - Automate AI-Index file updates
   - Set up receipt tracking

3. **Monitoring**:
   - Track receipt volumes
   - Monitor verification rates
   - Set up alerts for anomalies

## Resources

- [IAIndex Documentation](https://docs.aiindex.org)
- [API Reference](https://docs.aiindex.org/api)
- [Protocol Specification](https://docs.aiindex.org/spec)
- [Dashboard](https://aiindex.com/dashboard)

## Support

- GitHub Issues: [github.com/iaindex/iaindex](https://github.com/iaindex/iaindex)
- Discord: [discord.gg/iaindex](https://discord.gg/iaindex)
- Email: support@iaindex.com

## License

MIT
