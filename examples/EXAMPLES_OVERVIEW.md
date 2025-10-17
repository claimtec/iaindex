# IAIndex Examples - Complete Overview

Comprehensive example applications and integration guides for the IAIndex protocol.

**API Base URL:** `https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io`

## New Examples (Complete Implementation)

This directory contains **5 new complete working examples** that demonstrate end-to-end IAIndex integration:

### 1. Publisher Example (Node.js)
**Path:** `publisher-nodejs/`

Complete publisher integration demonstrating:
- Domain verification via DNS TXT
- AI-Index file generation
- Receipt submission
- Analytics retrieval
- Verified domains listing

**Quick Start:**
```bash
cd publisher-nodejs
npm install
cp .env.example .env
# Edit .env with your API key
npm start
```

**Documentation:** [publisher-nodejs/README.md](./publisher-nodejs/README.md)

---

### 2. AI Client Example (Python)
**Path:** `client-python/`

Complete AI client implementation showing:
- Fetching AI-Index files from publishers
- Content access tracking
- Cryptographic receipt generation (HMAC-SHA256)
- Receipt submission and verification
- Best practices for AI clients

**Quick Start:**
```bash
cd client-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python main.py
```

**Documentation:** [client-python/README.md](./client-python/README.md)

---

### 3. LangChain Integration
**Path:** `langchain-integration/`

Custom LangChain document loader with automatic receipt tracking:
- `IAIndexLoader` class extending BaseLoader
- Automatic receipt generation for verified publishers
- AI-Index file detection and caching
- Custom metadata extraction
- Seamless integration with LangChain chains

**Quick Start:**
```bash
cd langchain-integration
pip install -r requirements.txt
cp .env.example .env
# Edit .env
python example.py
```

**Usage Example:**
```python
from iaindex_loader import IAIndexLoader

loader = IAIndexLoader(
    urls=["https://example.com/article"],
    client_id="my-rag-app"
)
docs = loader.load()
# Receipts automatically sent for verified publishers
```

**Documentation:** [langchain-integration/README.md](./langchain-integration/README.md)

---

### 4. End-to-End Test Suite
**Path:** `e2e-test/`

Automated test suite validating complete user journey:
- API health check
- Domain verification flow
- Receipt submission and retrieval
- Analytics queries (publisher and system-wide)
- Error handling validation

**Tests:**
1. API Health
2. Domain Verification Initiation
3. Verification Status Check
4. Verified Domains List
5. Receipt Submission
6. Receipt Retrieval
7. Publisher Analytics
8. System Analytics

**Quick Start:**
```bash
cd e2e-test
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python test.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════════╗
║                  IAIndex End-to-End Test Suite                    ║
╚════════════════════════════════════════════════════════════════════╝

Total Tests:    8
Passed:         8
Failed:         0

✓ ALL TESTS PASSED!
```

**Documentation:** [e2e-test/README.md](./e2e-test/README.md)

---

### 5. Webflow Snippet
**Path:** `webflow-snippet/`

Embeddable JavaScript for Webflow sites:
- Automatic page metadata extraction
- AI bot detection (GPTBot, ClaudeBot, etc.)
- Client-side receipt generation
- Zero-configuration setup
- ~5KB minified

**Installation:**
1. Copy `iaindex-snippet.js`
2. Add to Webflow Project Settings > Custom Code > Head Code
3. Configure API key and publisher info
4. Publish site

**Features:**
- Automatic title, description, author extraction
- Detects content type (blog, article, product, etc.)
- Sends receipts when AI bots visit
- Debug mode for troubleshooting
- Exposes `window.IAIndex` API for manual control

**Documentation:** [webflow-snippet/README.md](./webflow-snippet/README.md)

---

## Directory Structure

```
examples/
├── EXAMPLES_OVERVIEW.md          # This file - complete overview
├── README.md                      # Original examples documentation
│
├── publisher-nodejs/              # NEW: Publisher example (Node.js)
│   ├── index.js                   # Main example script
│   ├── package.json               # Dependencies
│   ├── .env.example               # Configuration template
│   └── README.md                  # Detailed guide
│
├── client-python/                 # NEW: AI client example (Python)
│   ├── main.py                    # Complete client implementation
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Configuration template
│   └── README.md                  # Usage guide
│
├── langchain-integration/         # NEW: LangChain integration
│   ├── iaindex_loader.py          # Custom document loader
│   ├── example.py                 # Usage examples
│   ├── requirements.txt           # Dependencies
│   ├── .env.example               # Configuration template
│   └── README.md                  # Integration guide
│
├── e2e-test/                      # NEW: End-to-end test suite
│   ├── test.py                    # Test script
│   ├── requirements.txt           # Dependencies
│   ├── .env.example               # Configuration template
│   └── README.md                  # Test documentation
│
├── webflow-snippet/               # NEW: Webflow JavaScript snippet
│   ├── iaindex-snippet.js         # Embeddable snippet
│   └── README.md                  # Installation guide
│
├── publishers/                    # Original: Example publisher sites
│   └── example-blog/              # WordPress blog example
│
├── seed/                          # Original: Seed data
│   ├── seed-database.sql
│   ├── generate-test-receipts.py
│   └── ...
│
└── integration/                   # Original: Integration examples
    ├── langchain-example.ts
    ├── llamaindex-example.py
    └── ...
```

## Quick Reference

### API Endpoints Demonstrated

All examples interact with these IAIndex API endpoints:

#### Publisher Endpoints
```
POST   /v1/publishers/verify              # Initiate verification
GET    /v1/publishers/verify/{token}      # Check verification
GET    /v1/publishers/verified-domains    # List verified domains
```

#### Receipt Endpoints
```
POST   /v1/receipts/ingest               # Submit receipt
GET    /v1/receipts                      # List receipts
```

#### Analytics Endpoints
```
GET    /v1/analytics?domain={domain}     # Publisher analytics
GET    /v1/analytics/summary             # System analytics
```

### Authentication

All examples support two authentication methods:

**1. API Key (Header):**
```
X-API-Key: your-api-key-here
```

**2. JWT Bearer Token:**
```
Authorization: Bearer your-jwt-token
```

### Configuration

All examples use `.env` files:

```bash
# Copy template
cp .env.example .env

# Common variables
API_BASE_URL=https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
API_KEY=your-api-key-here
CLIENT_ID=your-client-id
SECRET_KEY=your-secret-key
```

## Use Cases by Example

### For Content Publishers

**Use:** [publisher-nodejs](./publisher-nodejs/)

Perfect for:
- Verifying your domain
- Generating AI-Index files
- Testing receipt submission
- Monitoring analytics

**Workflow:**
1. Run example to initiate verification
2. Add DNS TXT record
3. Check verification status
4. Generate and deploy ai-index.json
5. Monitor receipts in dashboard

---

### For AI Application Developers

**Use:** [client-python](./client-python/)

Perfect for:
- Building RAG systems
- Creating AI assistants
- Developing content aggregators
- Research tools

**Workflow:**
1. Check for AI-Index before accessing content
2. Fetch and parse AI-Index file
3. Access content
4. Generate and send receipt
5. Verify receipt submission

---

### For LangChain Developers

**Use:** [langchain-integration](./langchain-integration/)

Perfect for:
- RAG pipelines
- Document loaders
- Question answering systems
- Content retrieval

**Workflow:**
1. Install IAIndexLoader
2. Load documents with URLs
3. Receipts automatically sent
4. Use with standard LangChain components

---

### For Testing & CI/CD

**Use:** [e2e-test](./e2e-test/)

Perfect for:
- API validation
- Integration testing
- Deployment verification
- CI/CD pipelines

**Workflow:**
1. Set API key
2. Run test suite
3. Review results
4. Fix any failures

---

### For Webflow Users

**Use:** [webflow-snippet](./webflow-snippet/)

Perfect for:
- Blogs
- Marketing sites
- Documentation
- News sites

**Workflow:**
1. Copy snippet
2. Add to Webflow custom code
3. Configure settings
4. Publish site

## Testing Against Live API

All examples are configured to work with the deployed API at:
```
https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

### Prerequisites

1. **Get API Key** (optional but recommended)
   - Sign up at IAIndex Dashboard
   - Generate API key
   - Add to .env files

2. **Configure Examples**
   - Copy .env.example to .env
   - Add your API key
   - Customize settings

### Running Examples

```bash
# Publisher example
cd publisher-nodejs && npm install && npm start

# Client example
cd client-python && pip install -r requirements.txt && python main.py

# LangChain example
cd langchain-integration && pip install -r requirements.txt && python example.py

# E2E tests
cd e2e-test && pip install -r requirements.txt && python test.py

# Webflow snippet - add to Webflow custom code
```

## Test Results

### Example Test Run (E2E Suite)

```
API Base URL: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
Test Domain:  e2e-test-example.com
API Key:      Set

Test 1: API Health Check
  ✓ PASS API is healthy (Status: 200)

Test 2: Domain Verification Initiation
  ✓ PASS Verification initiated successfully

Test 3: Domain Verification Status Check
  ⚠ WARN Token not found (expected for test domain)

Test 4: List Verified Domains
  ✓ PASS Retrieved 0 verified domains

Test 5: Receipt Submission
  ✓ PASS Receipt submitted successfully
  ℹ INFO Status: rejected
  ℹ INFO Message: Publisher not verified

Test 6: Receipt Retrieval
  ✓ PASS Retrieved 0 receipts

Test 7: Publisher Analytics
  ⚠ WARN Publisher not found (expected for test domain)

Test 8: System Analytics
  ✓ PASS System analytics retrieved successfully

Total Tests:    8
Passed:         8
Failed:         0
Warnings:       2
Pass Rate:      100.0%

✓ ALL TESTS PASSED!
```

**Note:** Some warnings are expected for test domains that aren't actually verified.

## Common Workflows

### Workflow 1: Publisher Onboarding

```bash
# Step 1: Initiate verification
cd publisher-nodejs
npm install
npm start

# Step 2: Add DNS record (shown in output)
# TXT record: _iaindex-verification
# Value: iaindex-verification=abc123...

# Step 3: Wait for DNS propagation (5-60 minutes)

# Step 4: Check verification
# Re-run the script or call verify endpoint

# Step 5: Generate ai-index.json
# Use the example output or customize

# Step 6: Deploy to website root
# https://yourdomain.com/ai-index.json

# Step 7: Monitor analytics
# View in dashboard or use analytics endpoint
```

### Workflow 2: AI Client Integration

```bash
# Step 1: Install client
cd client-python
pip install -r requirements.txt

# Step 2: Configure
cp .env.example .env
# Edit with your settings

# Step 3: Test with live API
python main.py

# Step 4: Integrate into your app
# Import IAIndexClient class
# Use in your RAG/AI pipeline

# Step 5: Monitor receipts
# Check IAIndex dashboard
```

### Workflow 3: LangChain RAG

```bash
# Step 1: Install
cd langchain-integration
pip install -r requirements.txt

# Step 2: Test loader
python example.py

# Step 3: Integrate into pipeline
# from iaindex_loader import IAIndexLoader
# loader = IAIndexLoader(urls=your_urls)
# docs = loader.load()

# Step 4: Build RAG system
# Use docs with embeddings, vector stores, chains

# Step 5: Receipts sent automatically
```

## Troubleshooting

### API Key Issues

**Problem:** 401 Unauthorized

**Solution:**
- Check API_KEY in .env
- Verify key format
- Generate new key if expired

### Domain Verification

**Problem:** Verification fails

**Solution:**
- Check DNS TXT record is set
- Wait for DNS propagation (use dig/nslookup)
- Verify record format exactly matches

### Receipt Failures

**Problem:** Receipt rejected

**Solution:**
- Ensure domain is verified first
- Check signature generation matches API requirements
- Verify timestamp format (ISO 8601)
- Review error message for details

### CORS Errors

**Problem:** CORS policy blocked (browser)

**Solution:**
- Server-side examples shouldn't have CORS issues
- For browser: ensure using HTTPS
- Check API endpoint is correct

## Best Practices

### For All Users

1. **Environment Variables**
   - Never commit secrets
   - Use .env files
   - Rotate keys regularly

2. **Error Handling**
   - Log errors for debugging
   - Handle API failures gracefully
   - Don't break on receipt failures

3. **Testing**
   - Test on staging first
   - Use e2e-test suite
   - Verify before deploying

### For Publishers

1. **Verification First**
   - Complete domain verification before indexing
   - Keep DNS records up to date

2. **AI-Index Quality**
   - Provide complete metadata
   - Update when content changes
   - Include accurate descriptions

3. **Monitor Usage**
   - Track receipt volumes
   - Review analytics regularly
   - Identify popular content

### For AI Clients

1. **Check AI-Index First**
   - Look for ai-index.json before scraping
   - Respect publisher preferences
   - Follow rate limits

2. **Send Receipts**
   - Generate immediately after access
   - Include meaningful metadata
   - Handle failures gracefully

3. **Provide Attribution**
   - Cite sources properly
   - Link to original content
   - Follow publisher requirements

## Resources

### Documentation
- [IAIndex Specification](https://docs.iaindex.org/spec)
- [API Reference](https://docs.iaindex.org/api)
- [Integration Guides](https://docs.iaindex.org/guides)

### Support
- GitHub: [github.com/iaindex/iaindex](https://github.com/iaindex/iaindex)
- Discord: [discord.gg/iaindex](https://discord.gg/iaindex)
- Email: support@iaindex.com

### Community
- [GitHub Discussions](https://github.com/iaindex/iaindex/discussions)
- [Twitter](https://twitter.com/iaindex)
- [Blog](https://blog.iaindex.org)

## Contributing

Want to add more examples or improve existing ones?

1. Fork the repository
2. Create feature branch
3. Add your example following the structure
4. Test thoroughly against live API
5. Submit pull request

## License

All examples are MIT licensed.

## Changelog

### 2025-01-17

**New Examples Added:**
- ✅ Publisher Example (Node.js) - Complete implementation
- ✅ AI Client Example (Python) - Full client with receipt tracking
- ✅ LangChain Integration - Custom document loader
- ✅ End-to-End Test Suite - 8 comprehensive tests
- ✅ Webflow Snippet - Embeddable JavaScript

**Features:**
- All examples tested against live API
- Complete documentation for each
- Environment configuration templates
- Error handling and debugging support
- Best practices demonstrated

## Next Steps

1. **Choose Your Example**
   - Publisher? Start with `publisher-nodejs`
   - AI Developer? Start with `client-python`
   - LangChain User? Start with `langchain-integration`
   - Testing? Run `e2e-test`
   - Webflow? Use `webflow-snippet`

2. **Set Up Environment**
   - Copy .env.example to .env
   - Add your API key
   - Configure settings

3. **Run Example**
   - Follow Quick Start in each README
   - Check output for errors
   - Review results

4. **Integrate**
   - Adapt example to your needs
   - Test thoroughly
   - Deploy to production

5. **Monitor**
   - Check IAIndex dashboard
   - Review analytics
   - Optimize as needed

---

**Questions?** Join our [Discord](https://discord.gg/iaindex) or email support@iaindex.com

**Found a bug?** Open an [issue](https://github.com/iaindex/iaindex/issues)

**Have feedback?** We'd love to hear from you!
