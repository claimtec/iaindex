# ⚡ AIIndex Quick Start Guide

Get AIIndex up and running in under 10 minutes.

---

## 🎯 Choose Your Path

### For Publishers (Website Owners)
→ Go to [Publisher Setup](#publisher-setup)

### For Developers (Building AI Apps)
→ Go to [Developer Setup](#developer-setup)

### For Infrastructure Teams
→ Go to [Infrastructure Setup](#infrastructure-setup)

---

## 📱 Publisher Setup

### Option 1: Use a Plugin (2 minutes)

#### WordPress
```bash
# Install plugin
cd wp-content/plugins
git clone [wp-plugin-url] aiindex
# Activate in WordPress admin
# Configure at Settings > AIIndex
```

#### Shopify
```bash
# Install from Shopify App Store
# Or deploy manually:
cd packages/shopify-app
npm install
npm start
# Follow OAuth flow
```

#### Other Platforms
- **Webflow**: Copy snippet from `/packages/webflow-snippet/snippet.js`
- **Bubble.io**: Import plugin from `/packages/bubble-plugin/`
- **Wix**: Upload `/packages/wix-plugin/` to site
- **Squarespace**: Add code from `/packages/squarespace-snippet/`
- **Framer**: Import component from `/packages/framer-plugin/`
- **Ghost**: `npm install` from `/packages/ghost-plugin/`

### Option 2: Use SDK (5 minutes)

#### Node.js
```bash
npm install -g @aiindex/sdk

# Initialize
aiindex-gen init --domain yourdomain.com

# Generate index
aiindex-gen build --url https://yourdomain.com

# Sign (generates keys automatically)
aiindex-gen sign --generate-keys

# Verify
aiindex-gen verify ai-index.json

# Deploy (serve at /ai-index.json)
aiindex-gen serve
```

#### Python
```bash
pip install aiindex-sdk

# Initialize
aiindex-gen init --domain yourdomain.com

# Generate index
aiindex-gen build https://yourdomain.com

# Sign
aiindex-gen sign ai-index.json --generate-key

# Verify
aiindex-gen verify ai-index.json

# Serve
aiindex-gen serve --port 8080
```

### Option 3: Manual Integration (10 minutes)

1. **Create `ai-index.json`**:
```json
{
  "version": "1.0",
  "publisher_id": "yourdomain.com",
  "domain": "yourdomain.com",
  "last_updated": "2025-10-13T10:00:00Z",
  "publisher": {
    "name": "Your Company",
    "description": "What you do",
    "url": "https://yourdomain.com"
  },
  "pages": [
    {
      "url": "https://yourdomain.com/about",
      "title": "About Us",
      "description": "Company info",
      "content_type": "page"
    }
  ],
  "access_policy": {
    "allowed": true,
    "attribution_required": true,
    "receipt_required": false
  }
}
```

2. **Host at Root**: Place file at `https://yourdomain.com/ai-index.json`

3. **Verify Domain** (optional):
   - Go to https://aiindex.org/dashboard
   - Add DNS TXT record: `aiindex-verify=YOUR_TOKEN`
   - Get verification badge

---

## 👨‍💻 Developer Setup

### Option 1: Use LangChain (5 minutes)

```bash
npm install @aiindex/lc-aiindex-reader langchain
```

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';
import { OpenAI } from '@langchain/openai';
import { RetrievalQAChain } from 'langchain/chains';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import { OpenAIEmbeddings } from '@langchain/openai';

// Load documents
const loader = new AIIndexLoader('example.com', {
  autoSendReceipt: true,
  clientId: 'my-app',
  maxPages: 20,
});
const docs = await loader.load();

// Create RAG system
const vectorStore = await MemoryVectorStore.fromDocuments(
  docs,
  new OpenAIEmbeddings()
);

const chain = RetrievalQAChain.fromLLM(
  new OpenAI({ modelName: 'gpt-4' }),
  vectorStore.asRetriever()
);

const response = await chain.call({
  query: "What does this company do?",
});
```

### Option 2: Use LlamaIndex (5 minutes)

```bash
pip install aiindex-llama llama-index
```

```python
from aiindex_llama import AIIndexLoader
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI

# Load documents
loader = AIIndexLoader(
    url="example.com",
    auto_send_receipt=True,
    client_id="my-app",
    max_pages=20,
)
documents = loader.load_data()

# Create RAG system
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(llm=OpenAI(model="gpt-4"))

response = query_engine.query("What does this company do?")
print(response)
```

### Option 3: Custom Integration (10 minutes)

See `/examples/integration/custom-crawler.js` for a complete example.

---

## 🏗️ Infrastructure Setup

### Local Development (5 minutes)

```bash
# Clone repo
git clone [repo-url] iaindex
cd iaindex

# Start all services
docker-compose up -d

# Access services
# API: http://localhost:3000
# Web: http://localhost:3001
# Docs: http://localhost:3002

# Seed database
psql -h localhost -U postgres -d aiindex < examples/seed/seed-database.sql

# View logs
docker-compose logs -f
```

### Production Deployment (20 minutes)

#### 1. Setup Supabase
```bash
# Create project at supabase.com
# Copy connection details
export SUPABASE_URL="your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Run schema
psql $DATABASE_URL < infra/supabase/schema.sql
```

#### 2. Deploy API (Fly.io)
```bash
cd apps/api
cp .env.example .env
# Edit .env with your credentials

fly launch
fly deploy
```

#### 3. Deploy Web (Vercel)
```bash
cd apps/web
cp .env.example .env.local
# Edit .env.local

vercel deploy --prod
```

#### 4. Deploy Docs (Netlify)
```bash
cd apps/docs
netlify deploy --prod
```

#### 5. Setup Infrastructure (Terraform)
```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars

terraform init
terraform plan
terraform apply
```

---

## 🧪 Testing

### Test API
```bash
# Health check
curl http://localhost:3000/health

# Create receipt
curl -X POST http://localhost:3000/v1/receipts/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "receipt_id": "rec_123",
    "publisher_domain": "example.com",
    "article_url": "https://example.com/article",
    "timestamp": "2025-10-13T10:00:00Z"
  }'
```

### Test Dashboard
```bash
# Open browser
open http://localhost:3001

# Sign up
# View dashboard
# Check receipts
```

### Test SDK
```bash
# Node.js
cd packages/sdk-node
npm install
npm run build
npm test

# Python
cd packages/sdk-python
pip install -e .
pytest
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `/spec/aiindex.schema.json` | Protocol specification |
| `/infra/supabase/schema.sql` | Database schema |
| `/apps/api/` | Verification API |
| `/apps/web/` | Publisher dashboard |
| `/packages/sdk-node/` | Node.js SDK |
| `/packages/sdk-python/` | Python SDK |
| `/examples/` | Examples and seed data |
| `/apps/docs/` | Documentation site |

---

## 🆘 Troubleshooting

### API won't start
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Check environment variables
cat .env | grep -v "^#"

# View logs
docker-compose logs api
```

### Dashboard shows errors
```bash
# Check Supabase connection
curl https://your-project.supabase.co/rest/v1/

# Check .env.local
cat apps/web/.env.local

# Clear Next.js cache
rm -rf apps/web/.next
cd apps/web && npm run build
```

### SDK CLI not found
```bash
# Node.js
npm link
# or
export PATH="$PATH:./node_modules/.bin"

# Python
pip install -e .
# or
export PATH="$PATH:~/.local/bin"
```

### Port already in use
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
PORT=3001 npm start
```

---

## 📞 Support

- **Documentation**: [docs.aiindex.org](https://docs.aiindex.org)
- **GitHub Issues**: [github.com/aiindex/aiindex/issues](https://github.com/aiindex/aiindex/issues)
- **Email**: support@aiindex.org
- **Discord**: [discord.gg/aiindex](https://discord.gg/aiindex)

---

## 🎓 Learn More

### For Publishers
- [Complete Publisher Guide](apps/docs/docs/publishers/)
- [Plugin Documentation](apps/docs/docs/plugins/)
- [Domain Verification](apps/docs/docs/publishers/domain-verification.md)

### For Developers
- [Node.js SDK Guide](apps/docs/docs/sdks/nodejs.md)
- [Python SDK Guide](apps/docs/docs/sdks/python.md)
- [LangChain Integration](apps/docs/docs/clients/langchain.md)
- [LlamaIndex Integration](apps/docs/docs/clients/llamaindex.md)
- [API Reference](apps/docs/docs/api/)

### For Infrastructure Teams
- [Infrastructure Guide](infra/README.md)
- [Terraform Setup](infra/terraform/README.md)
- [Merkle System](infra/merkle/README.md)
- [CI/CD Pipelines](.github/workflows/)

---

## ✅ Next Steps

After setup, consider:

1. **Verify your domain** → Get verification badge
2. **Set up webhooks** → Receive receipts in real-time
3. **Enable analytics** → Track AI agent access
4. **Add attribution** → Show "Powered by AIIndex" badge
5. **Monitor usage** → Check dashboard regularly
6. **Optimize content** → Update ai-index.json for better discoverability

---

**Ready to go! 🚀**

Choose your setup path above and follow the steps. Need help? Check the [troubleshooting section](#troubleshooting) or reach out via [support](#support).
