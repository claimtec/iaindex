# AIIndex v1.1

**Transparent, cryptographically-verifiable content provenance for the AI era.**

AIIndex is a decentralized protocol that enables publishers to cryptographically sign and timestamp their content, allowing AI systems to verify content authenticity and track usage through immutable receipts.

## 🚀 Quick Links

- **Live API**: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
- **Documentation**: https://aiindex-docs.azurewebsites.net
- **API Docs**: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/docs

## 📦 Installation

### Node.js SDK
```bash
npm install @iaindex/sdk
```

### Python SDK
```bash
pip install iaindex-sdk
```

### CLI Tool
```bash
npm install -g @iaindex/cli
```

## 🔧 Quick Start

### For Publishers

```javascript
// Node.js
const { IAIndexPublisher } = require('@iaindex/sdk');

const publisher = new IAIndexPublisher({
  domain: 'example.com',
  privateKey: 'your-private-key',
  name: 'Example Publisher',
  contact: 'contact@example.com'
});

await publisher.initialize();
await publisher.addEntry({
  url: 'https://example.com/article',
  title: 'My Article',
  content: 'Article content...',
  author: 'John Doe'
});

const index = await publisher.generateIndex();
```

### For AI Systems

```python
# Python
from aiindex import IAIndexClient

client = IAIndexClient(api_url='https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io')

# Verify content authenticity
is_verified = client.verify_content(
    domain='example.com',
    content_hash='sha256_hash_here'
)

# Submit receipt after usage
receipt = client.submit_receipt(
    client_id='your-client-id',
    content_hashes=['hash1', 'hash2'],
    usage_metadata={'tokens': 1000}
)
```

## 📁 Project Structure

```
iaindex/
├── apps/
│   ├── api/                    # FastAPI backend (Azure Container Apps)
│   ├── web/                    # Next.js documentation site (Azure Static Web Apps)
│   └── docs/                   # Docusaurus documentation
├── packages/
│   ├── sdk-nodejs/             # Node.js SDK (@iaindex/sdk)
│   ├── sdk-python/             # Python SDK (iaindex-sdk)
│   ├── cli/                    # CLI tool (@iaindex/cli)
│   └── wordpress-plugin/       # WordPress plugin
├── examples/
│   ├── publisher-nodejs/       # Publisher example (Node.js)
│   ├── client-python/          # AI client example (Python)
│   ├── langchain-integration/  # LangChain custom loader
│   ├── e2e-test/              # End-to-end test suite
│   └── webflow-snippet/       # Embeddable JavaScript snippet
├── migrations/                 # Database migration scripts
├── releases/
│   └── v1.0.0/                # Distribution packages
├── docs/                       # Project documentation
│   ├── deployment/            # Deployment guides and logs
│   ├── migration/             # Migration documentation
│   ├── marketing/             # Marketing materials
│   ├── testing/               # Test reports and fixes
│   └── guides/                # Development guides
├── scripts/                    # Deployment and utility scripts
├── logs/                       # Deployment logs
└── archive/                    # Historical documentation
```

## 📚 Documentation Index

### Getting Started
- [Quick Start Guide](docs/guides/QUICKSTART.md)
- [Start Here](docs/guides/START_HERE.md)
- [Database Setup](docs/guides/DATABASE_SETUP_INSTRUCTIONS.md)

### Deployment
- [Azure Deployment Complete](docs/deployment/AZURE_DEPLOYMENT_COMPLETE.md)
- [Deployment Plan](docs/deployment/DEPLOYMENT_PLAN.md)
- [Docs Deployment](docs/deployment/DOCS_DEPLOYMENT.md)
- [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)

### Development Guides
- [Build Complete](docs/guides/BUILD_COMPLETE.md)
- [Local Testing Guide](docs/guides/LOCAL_TESTING_GUIDE.md)
- [Git DevOps Guide](docs/guides/GIT_DEVOPS_GUIDE.md)
- [Infrastructure Setup](docs/guides/INFRASTRUCTURE_SETUP.md)
- [PM2 Deployment Guide](docs/guides/PM2_DEPLOYMENT_GUIDE.md)

### Testing
- [End-to-End Test Report](docs/testing/END_TO_END_TEST_REPORT.md)
- [API Endpoints Fixed](docs/testing/API_ENDPOINTS_FIXED.md)
- [Schema Fixes Applied](docs/testing/SCHEMA_FIXES_APPLIED.md)

### Migration
- [Migration Complete](docs/migration/MIGRATION_COMPLETE.md)
- [Migration Summary](docs/migration/MIGRATION_SUMMARY.md)
- [Migration v1.0 to v1.1](docs/migration/MIGRATION_V1.0_TO_V1.1.md)
- [Migration Quickstart](docs/migration/MIGRATION_QUICKSTART.md)
- [Gap Analysis](docs/migration/GAP_ANALYSIS.md)

### Marketing Materials
- [One Pager](docs/marketing/AIINDEX_ONE_PAGER.md)
- [Executive Brief](docs/marketing/AIINDEX_V1.1_EXECUTIVE_BRIEF.md)
- [Press Release](docs/marketing/PRESS_RELEASE_V1.1.md)
- [Pitch Deck Outline](docs/marketing/PITCH_DECK_OUTLINE.md)
- [Social Campaign](docs/marketing/SOCIAL_CAMPAIGN.md)
- [Launch Materials Summary](docs/marketing/LAUNCH_MATERIALS_SUMMARY.md)

## 🔑 Key Features

### For Publishers
- **Domain Verification**: Prove ownership of your domain
- **Content Signing**: Cryptographically sign content with ECDSA
- **Timestamping**: Immutable timestamps via blockchain
- **Receipt Tracking**: Track AI system usage of your content
- **Merkle Tree Attestations**: Efficient batch verification

### For AI Systems
- **Content Verification**: Verify content authenticity before use
- **Publisher Discovery**: Find verified publishers and their indexes
- **Receipt Submission**: Create transparent usage records
- **Semantic Search**: Query content by meaning (optional)
- **LangChain Integration**: Drop-in document loader

## 🏗️ Architecture

### Backend (API)
- **Platform**: Azure Container Apps
- **Framework**: FastAPI (Python 3.11)
- **Database**: Supabase PostgreSQL
- **Authentication**: JWT tokens
- **Timestamping**: OpenTimestamps

### Frontend (Docs)
- **Platform**: Azure Static Web Apps
- **Framework**: Docusaurus
- **Hosting**: GitHub Pages compatible

### Client SDKs
- **Node.js**: TypeScript, axios, elliptic (ECDSA)
- **Python**: Type hints, requests, ecdsa library
- **CLI**: Commander.js, chalk, ora, inquirer

## 📦 Available Packages

All packages are available in [releases/v1.0.0/](releases/v1.0.0/):

| Package | Size | Description |
|---------|------|-------------|
| `@iaindex/sdk` | 15 KB | Node.js SDK |
| `iaindex-sdk` (wheel) | 29 KB | Python SDK |
| `iaindex-sdk` (source) | 28 KB | Python SDK source |
| `@iaindex/cli` | 72 KB | CLI tool |
| WordPress Plugin | 49 KB | WordPress integration |

**Total**: 193 KB across 5 distribution files

See [releases/v1.0.0/MANIFEST.md](releases/v1.0.0/MANIFEST.md) for detailed package information.

## 🧪 Testing Status

- **Backend API**: ✅ 8/8 tests passing (100%)
- **Node.js SDK**: ✅ 27/28 tests passing (96.4%)
- **Python SDK**: ✅ All verification tests passing
- **CLI**: ✅ All commands functional
- **E2E Tests**: ✅ 2/6 public tests passing (4 auth-protected as expected)

## 🚢 Deployment Status

### Production
- ✅ API deployed to Azure Container Apps
- ✅ Docs deployed to Azure Static Web Apps
- ✅ Database configured on Supabase
- ✅ All secrets configured in Azure Key Vault
- ✅ Health checks passing

### Package Distribution
- ⏳ npm packages ready (awaiting publication)
- ⏳ PyPI packages ready (awaiting publication)
- ⏳ WordPress plugin ready (awaiting distribution decision)

See [releases/v1.0.0/DEPLOYMENT_GUIDE.md](releases/v1.0.0/DEPLOYMENT_GUIDE.md) for publishing instructions.

## 🔐 Environment Variables

### API (apps/api/)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
DEBUG=False

# Optional
OPENAI_API_KEY=sk-...        # For semantic search
COHERE_API_KEY=...           # Alternative embeddings
ANTHROPIC_API_KEY=...        # Alternative embeddings
```

### Web (apps/web/)
```bash
NEXT_PUBLIC_API_URL=https://your-api.azurecontainerapps.io
```

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Documentation**: https://aiindex-docs.azurewebsites.net
- **API Issues**: Check [docs/testing/](docs/testing/) for known issues
- **Deployment**: See [docs/deployment/](docs/deployment/) for guides

## 🗺️ Roadmap

### v1.1 (Current) ✅
- Core protocol implementation
- Publisher verification
- Receipt tracking
- Azure deployment
- Client SDKs (Node.js, Python)
- CLI tool
- WordPress plugin

### v1.2 (Planned)
- Additional AI platform integrations
- Browser extensions for publishers
- Analytics dashboard
- Advanced semantic search
- Multi-language SDK support

---

**Built with**: FastAPI • Next.js • Docusaurus • TypeScript • Python • PostgreSQL • Azure

**Status**: ✅ Production Ready (v1.1)
