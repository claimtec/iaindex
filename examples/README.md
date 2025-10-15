# AIIndex Examples and Seed Data

This directory contains comprehensive examples and seed data for the AIIndex protocol.

## Directory Structure

```
examples/
├── publishers/          # Example publisher implementations
│   ├── example-blog/           # WordPress blog example
│   ├── example-ecommerce/      # Shopify e-commerce example
│   └── example-docs/           # Docusaurus documentation example
├── seed/               # Seed data for development and testing
│   ├── seed-database.sql       # SQL seed data
│   ├── generate-test-receipts.py  # Receipt generator
│   ├── publishers.json         # Sample publishers
│   ├── clients.json           # Sample AI clients
│   └── receipts.json          # Sample receipts
└── integration/        # Integration examples
    ├── langchain-example.ts    # LangChain integration
    ├── llamaindex-example.py   # LlamaIndex integration
    ├── custom-crawler.js       # Custom crawler
    └── receipt-verifier.py     # Receipt verification
```

## Example Publishers

### 1. Example Blog (WordPress)

**Path:** `publishers/example-blog/`

A tech blog demonstrating AIIndex integration with WordPress.

**Contents:**
- `ai-index.json` - Complete AIIndex file with 10 articles
- `README.md` - Setup and configuration guide
- `verification-badge.html` - Badge implementation examples

**Features:**
- Blog articles with AI-friendly summaries
- FAQ section
- Author information
- WordPress plugin configuration
- Receipt webhook implementation

**Use Cases:**
- Content sites
- News publications
- Magazine websites
- Personal blogs

### 2. Example E-commerce (Shopify)

**Path:** `publishers/example-ecommerce/`

An online store selling tech accessories via Shopify.

**Contents:**
- `ai-index.json` - Product catalog with 5+ products
- `README.md` - Shopify app integration guide
- `shopify-integration.liquid` - Theme integration code

**Features:**
- Product entities with pricing
- Collection pages
- Product recommendations
- AI attribution tracking
- E-commerce specific metadata

**Use Cases:**
- Online stores
- Product catalogs
- Marketplace vendors
- Retail websites

### 3. Example Documentation (Docusaurus)

**Path:** `publishers/example-docs/`

Technical documentation for an open-source cloud platform.

**Contents:**
- `ai-index.json` - Documentation structure with 10 pages
- `README.md` - Docusaurus plugin guide
- `docusaurus.config.js` - Complete configuration

**Features:**
- API documentation
- Getting started guides
- Code examples
- Version management
- Search integration

**Use Cases:**
- Technical documentation
- API references
- Developer portals
- Knowledge bases

## Seed Data

### Database Seed (`seed-database.sql`)

Populates PostgreSQL/Supabase database with test data:

- **10 Publishers** - Diverse verified publishers
- **100 Receipts** - Distributed across 30 days
- **5 AI Clients** - Major LLM providers
- **Daily Aggregates** - Analytics data
- **Merkle Roots** - Daily attestations

**Usage:**
```bash
psql -U postgres -d aiindex < seed/seed-database.sql
```

**What it creates:**
- Publisher accounts with different tiers
- Historical receipt data
- Client registry
- Analytics aggregates
- Audit log entries

### Receipt Generator (`generate-test-receipts.py`)

Python script to generate realistic test receipts.

**Usage:**
```bash
# Generate 100 receipts
python seed/generate-test-receipts.py --count 100 --output-dir ./receipts

# Generate 50 receipts
python seed/generate-test-receipts.py --count 50
```

**Output:**
- Individual receipt JSON files
- Combined `all-receipts.json`
- Statistics summary

**Features:**
- Realistic timestamp distribution
- Various purpose types
- Multiple publishers and clients
- Valid/invalid signature mix (90/10)
- Commercial use flags

### JSON Seed Files

#### `publishers.json`
Sample publisher data for 10 verified sites:
- Tech blog
- E-commerce store
- Documentation site
- News site
- Educational platform
- API provider
- SaaS product
- Research organization
- Media company
- Open source project

#### `clients.json`
Sample AI client data:
- OpenAI GPT-4
- Anthropic Claude
- Google Gemini
- Meta Llama
- Perplexity AI
- Custom crawler

#### `receipts.json`
Sample receipt data showing different scenarios:
- Successful access with attribution
- Product recommendations
- Documentation queries
- News search
- Research access

## Integration Examples

### 1. LangChain Integration (`langchain-example.ts`)

Complete LangChain integration demonstrating:

**Features:**
- Custom AIIndex document loader
- Automatic receipt sending
- Attribution in responses
- RAG system with multiple domains
- Source citation

**Usage:**
```typescript
import { AIIndexRAG } from './langchain-example';

const rag = new AIIndexRAG(process.env.OPENAI_API_KEY);
await rag.addDomains(['example-blog.com', 'cloudforge-docs.dev']);

const result = await rag.query('How do AI agents work?');
console.log(result.answer);
console.log(result.sources);
```

**Requirements:**
```bash
npm install langchain @langchain/openai @langchain/community
```

### 2. LlamaIndex Integration (`llamaindex-example.py`)

Complete LlamaIndex integration with:

**Features:**
- Custom AIIndex reader
- Receipt webhook integration
- Metadata filtering
- Attribution generation
- Custom retriever

**Usage:**
```python
from llamaindex_example import AIIndexRAG

rag = AIIndexRAG(os.environ['OPENAI_API_KEY'])
rag.add_domains(['example-blog.com', 'techgear-shop.com'])

result = rag.query('What keyboards do you recommend?')
print(result['answer'])
print(result['sources'])
```

**Requirements:**
```bash
pip install llama-index openai requests
```

### 3. Custom Crawler (`custom-crawler.js`)

Production-ready crawler demonstrating:

**Features:**
- AIIndex discovery
- Access policy compliance
- Rate limiting
- Receipt sending
- Data storage
- Search indexing

**Usage:**
```bash
node custom-crawler.js example-blog.com techgear-shop.com cloudforge-docs.dev
```

**Output:**
- Crawled data JSON files
- Summary statistics
- Searchable index

**Requirements:**
```bash
npm install axios cheerio bottleneck
```

### 4. Receipt Verifier (`receipt-verifier.py`)

Comprehensive receipt validation tool:

**Features:**
- Schema validation
- Field checking
- Timestamp validation
- Signature structure verification
- Policy compliance checking
- Batch verification

**Usage:**
```bash
# Verify single receipt
python receipt-verifier.py receipt.json

# Verify all receipts in directory
python receipt-verifier.py --batch receipts/

# Generate report
python receipt-verifier.py --batch receipts/ --output report.json
```

**Requirements:**
```bash
pip install jsonschema cryptography requests
```

## Quick Start

### 1. Set Up Database

```bash
# Start PostgreSQL (or use Supabase)
psql -U postgres -d aiindex < examples/seed/seed-database.sql
```

### 2. Generate Test Receipts

```bash
cd examples/seed
python generate-test-receipts.py --count 100
```

### 3. Try Integration Examples

**LangChain:**
```bash
cd examples/integration
export OPENAI_API_KEY=your-key
npm install
npx tsx langchain-example.ts
```

**LlamaIndex:**
```bash
cd examples/integration
export OPENAI_API_KEY=your-key
pip install -r requirements.txt
python llamaindex-example.py
```

**Custom Crawler:**
```bash
cd examples/integration
npm install
node custom-crawler.js example-blog.com techgear-shop.com
```

### 4. Verify Receipts

```bash
cd examples/integration
python receipt-verifier.py ../seed/receipts.json
```

## Testing Scenarios

### Scenario 1: Blog Content Access

1. Crawler discovers `example-blog.com`
2. Fetches `ai-index.json`
3. Checks access policy (attribution required)
4. Indexes article content
5. Sends receipt to webhook
6. Uses content with attribution

### Scenario 2: Product Recommendations

1. RAG system queries product data
2. Accesses `techgear-shop.com` via AIIndex
3. Retrieves product information
4. Generates recommendations
5. Includes product links
6. Sends receipt with pages accessed

### Scenario 3: Documentation Queries

1. User asks technical question
2. System searches `cloudforge-docs.dev`
3. Retrieves relevant documentation
4. Generates answer with citations
5. Links to original docs
6. Tracks attribution

## API Examples

### Fetch AIIndex

```javascript
const response = await fetch('https://example-blog.com/.well-known/ai-index.json');
const aiIndex = await response.json();

console.log(`Publisher: ${aiIndex.publisher.name}`);
console.log(`Pages: ${aiIndex.pages.length}`);
console.log(`Receipt required: ${aiIndex.access_policy.receipt_required}`);
```

### Send Receipt

```javascript
const receipt = {
  version: '1.0',
  receipt_id: crypto.randomUUID(),
  publisher_id: 'example-blog.com',
  client_id: 'my-app',
  timestamp: new Date().toISOString(),
  // ... other fields
};

await fetch('https://example-blog.com/api/receipts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(receipt)
});
```

### Query with Attribution

```python
from llamaindex_example import AIIndexRAG

rag = AIIndexRAG(api_key)
rag.add_domains(['example-blog.com'])

result = rag.query('What are AI agents?')

# Response includes attribution
print(result['answer'])  # "According to Tech Insights Blog, AI agents are..."
print(result['sources'])  # [{'publisher': 'Tech Insights Blog', ...}]
```

## Development Workflow

### 1. Local Testing

```bash
# Start with example publishers
cd examples/publishers/example-blog
cat ai-index.json

# Generate test data
cd ../../seed
python generate-test-receipts.py --count 10

# Test integration
cd ../integration
node custom-crawler.js localhost:3000
```

### 2. Seed Development Database

```bash
# Reset and seed database
psql -U postgres -d aiindex_dev < seed/seed-database.sql

# Verify data
psql -U postgres -d aiindex_dev -c "SELECT COUNT(*) FROM receipts;"
```

### 3. Test Receipt Flow

```bash
# Generate receipt
python seed/generate-test-receipts.py --count 1 --output-dir /tmp

# Verify receipt
python integration/receipt-verifier.py /tmp/receipt-001-*.json

# Send to webhook (if running locally)
curl -X POST http://localhost:3000/api/receipts \
  -H "Content-Type: application/json" \
  -d @/tmp/receipt-001-*.json
```

## Best Practices

### For Publishers

1. **Complete Metadata** - Fill all fields in ai-index.json
2. **Clear Summaries** - Write AI-friendly page summaries
3. **Proper Attribution** - Specify attribution requirements
4. **Receipt Handling** - Implement webhook endpoint
5. **Regular Updates** - Keep ai-index.json current

### For AI Clients

1. **Check Access Policy** - Respect publisher preferences
2. **Send Receipts** - If required by policy
3. **Provide Attribution** - Cite sources properly
4. **Rate Limiting** - Don't overwhelm publishers
5. **Error Handling** - Handle missing/invalid AIIndex gracefully

### For Integrators

1. **Use SDK** - Leverage existing SDKs when possible
2. **Cache Data** - Don't fetch ai-index.json repeatedly
3. **Validate Receipts** - Verify receipt structure
4. **Monitor Usage** - Track receipt statistics
5. **Test Thoroughly** - Use seed data for testing

## Troubleshooting

### AIIndex Not Found

```bash
# Check if file exists
curl -I https://example-blog.com/.well-known/ai-index.json

# Verify CORS headers
curl -H "Origin: https://my-app.com" \
  https://example-blog.com/.well-known/ai-index.json
```

### Receipt Not Accepted

```bash
# Validate receipt schema
python integration/receipt-verifier.py my-receipt.json

# Check webhook endpoint
curl -X POST https://example-blog.com/api/receipts \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Integration Issues

```bash
# Test with example data
node integration/custom-crawler.js example-blog.com

# Check dependencies
npm list
pip list

# Enable debug logging
DEBUG=aiindex:* node integration/custom-crawler.js example-blog.com
```

## Contributing

To add new examples:

1. Follow existing structure
2. Include complete README
3. Provide sample data
4. Add to this index
5. Test thoroughly

## Resources

- [AIIndex Specification](https://aiindex.org/spec)
- [SDK Documentation](https://docs.aiindex.org)
- [API Reference](https://docs.aiindex.org/api)
- [Community Forum](https://community.aiindex.org)

## License

Examples are provided under MIT License for educational purposes.
