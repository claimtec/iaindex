# AIIndex — Open Protocol for AI-Readable Web Data

AIIndex is an open protocol and verification network that enables websites to publish AI-readable metadata and track AI agent access through cryptographically verifiable receipts.

## 🎯 Overview

- **Protocol**: Standard `/ai-index.json` format for structured, AI-readable content
- **Verification Network**: SaaS API that verifies and logs access receipts
- **Analytics Dashboard**: Publisher insights on AI agent traffic
- **SDKs**: Node.js and Python libraries for easy integration
- **Plugins**: Ready-made integrations for major website builders
- **Client Connectors**: LangChain and LlamaIndex readers

## 🏗️ Architecture

```
/aiindex/
├── apps/
│   ├── api/                # Verification & Analytics API
│   ├── web/                # Next.js Dashboard
│   └── docs/               # Documentation site
├── packages/
│   ├── sdk-node/           # Node.js SDK
│   ├── sdk-python/         # Python SDK
│   ├── lc-aiindex-reader/  # LangChain connector
│   ├── li-aiindex-reader/  # LlamaIndex connector
│   ├── wp-plugin/          # WordPress
│   ├── webflow-snippet/    # Webflow
│   ├── bubble-plugin/      # Bubble.io
│   ├── wix-plugin/         # Wix
│   ├── squarespace-snippet/# Squarespace
│   ├── shopify-app/        # Shopify
│   ├── framer-plugin/      # Framer
│   └── ghost-plugin/       # Ghost CMS
├── spec/
│   ├── aiindex.schema.json
│   └── receipts.schema.json
└── infra/
    ├── supabase/
    └── terraform/
```

## 🚀 Quick Start

### For Publishers

```bash
# Install SDK
npm install -g @aiindex/sdk

# Initialize your site
aiindex-gen init
aiindex-gen build
aiindex-gen serve

# Verify setup
aiindex-gen verify
```

### For AI Applications

```python
from aiindex import AIIndexReader

reader = AIIndexReader()
data = reader.fetch("https://example.com/ai-index.json")
reader.send_receipt(data)
```

## 🔧 Components

### Protocol Specification
Standard JSON format at `/ai-index.json` with fields for publisher identity, entities, pages, FAQs, and cryptographic signatures.

### Verification API
- Receipt ingestion and validation
- Domain verification via DNS
- Analytics aggregation
- Daily Merkle attestations

### Publisher Dashboard
- Domain verification
- Traffic analytics and charts
- Receipt explorer
- Verification badge generator
- API key management

### Website Builder Plugins
Pre-built integrations for:
- WordPress
- Webflow
- Bubble.io
- Wix
- Squarespace
- Shopify
- Framer
- Ghost CMS

## 📊 Features

- **Domain Verification**: DNS-based publisher authentication
- **Cryptographic Receipts**: ECDSA signatures for proof-of-access
- **Privacy-First**: No content hosting, minimal data collection
- **Open Standard**: Community-driven protocol specification
- **Merkle Attestations**: Daily append-only proof logs
- **Analytics**: Track AI agent access patterns

## 🛡️ Security

- ES256 (ECDSA P-256) signatures
- DNS TXT verification
- Rate limiting and CORS
- No raw IP storage
- Hash-based receipt verification

## 📚 Documentation

Full documentation at `docs.aiindex.org`:
- Protocol specification
- Integration guides
- API reference
- Builder plugin docs
- Compliance (GDPR/POPIA)

## 💰 Monetization (Optional)

- Free tier: Basic analytics, 90-day retention
- Verified tier: Badge, extended retention
- Enterprise: Custom webhooks, raw data access

## 🤝 Contributing

AIIndex is open source. Contributions welcome via GitHub.

## 📄 License

MIT License - see LICENSE file

## 🔗 Links

- Website: https://aiindex.org
- Docs: https://docs.aiindex.org
- GitHub: https://github.com/aiindex/aiindex
- Discord: https://discord.gg/aiindex
