# AIIndex v1.1 - Quick Navigation Guide

Fast access to all key files and directories in the AIIndex project.

## 🚀 Start Here

| What | Where | Description |
|------|-------|-------------|
| **Main README** | [README.md](README.md) | Project overview and quick start |
| **Project Structure** | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Complete directory tree |
| **Documentation Index** | [docs/INDEX.md](docs/INDEX.md) | All documentation organized |
| **Quick Start Guide** | [docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md) | Get started in 5 minutes |

---

## 📦 Distribution Packages (Ready to Publish)

All packages are in **[releases/v1.0.0/](releases/v1.0.0/)**

| Package | File | Size |
|---------|------|------|
| Node.js SDK | `iaindex-sdk-1.0.0.tgz` | 15 KB |
| Python SDK (wheel) | `iaindex_sdk-1.0.0-py3-none-any.whl` | 29 KB |
| Python SDK (source) | `aiindex-sdk-1.0.0.tar.gz` | 28 KB |
| CLI Tool | `iaindex-cli-1.0.0.tgz` | 72 KB |
| WordPress Plugin | `iaindex-wordpress-plugin-v1.0.0.zip` | 49 KB |

**Publication Guide**: [releases/v1.0.0/DEPLOYMENT_GUIDE.md](releases/v1.0.0/DEPLOYMENT_GUIDE.md)

---

## 💻 Source Code

### Backend API
```
apps/api/
├── src/routes/          # API endpoints
├── src/services/        # Business logic
├── src/middleware/      # Auth, CORS, etc.
└── src/models/          # Data models
```

**Key Files**:
- [apps/api/src/routes/publishers.py](apps/api/src/routes/publishers.py) - Publisher verification
- [apps/api/src/routes/receipts.py](apps/api/src/routes/receipts.py) - Receipt submission
- [apps/api/src/routes/attestations.py](apps/api/src/routes/attestations.py) - Merkle trees
- [apps/api/src/routes/analytics.py](apps/api/src/routes/analytics.py) - Analytics dashboard
- [apps/api/src/config.py](apps/api/src/config.py) - Configuration

### Node.js SDK
```
packages/sdk-nodejs/
├── src/publisher.ts     # Publisher class
├── src/client.ts        # Client class
├── src/crypto.ts        # ECDSA utilities
└── tests/               # 27 Jest tests
```

### Python SDK
```
packages/sdk-python/
├── aiindex/publisher.py # Publisher class
├── aiindex/client.py    # Client class
├── aiindex/crypto.py    # ECDSA utilities
└── tests/               # Pytest tests
```

### CLI Tool
```
packages/cli/
├── src/commands/verify.ts      # Domain verification
├── src/commands/keys.ts        # Key generation
├── src/commands/index-gen.ts   # Index creation
└── src/commands/auth.ts        # Authentication
```

### WordPress Plugin
```
packages/wordpress-plugin/
├── iaindex.php                 # Main plugin file
├── admin/settings.php          # Settings page
├── admin/dashboard.php         # Dashboard widget
└── includes/index-generator.php # Index generation
```

---

## 📚 Documentation

### By Topic

**Getting Started**
- [Quick Start](docs/guides/QUICKSTART.md)
- [Start Here](docs/guides/START_HERE.md)
- [Database Setup](docs/guides/DATABASE_SETUP_INSTRUCTIONS.md)

**Deployment**
- [Azure Deployment Complete](docs/deployment/AZURE_DEPLOYMENT_COMPLETE.md)
- [Deployment Plan](docs/deployment/DEPLOYMENT_PLAN.md)
- [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)

**Development**
- [Build Complete](docs/guides/BUILD_COMPLETE.md)
- [Local Testing Guide](docs/guides/LOCAL_TESTING_GUIDE.md)
- [Git DevOps Guide](docs/guides/GIT_DEVOPS_GUIDE.md)

**Testing**
- [End-to-End Test Report](docs/testing/END_TO_END_TEST_REPORT.md)
- [API Endpoints Fixed](docs/testing/API_ENDPOINTS_FIXED.md)
- [Schema Fixes Applied](docs/testing/SCHEMA_FIXES_APPLIED.md)

**Migration**
- [Migration Complete](docs/migration/MIGRATION_COMPLETE.md)
- [Migration v1.0 to v1.1](docs/migration/MIGRATION_V1.0_TO_V1.1.md)
- [Migration Quickstart](docs/migration/MIGRATION_QUICKSTART.md)

**Marketing**
- [One Pager](docs/marketing/AIINDEX_ONE_PAGER.md)
- [Executive Brief](docs/marketing/AIINDEX_V1.1_EXECUTIVE_BRIEF.md)
- [Press Release](docs/marketing/PRESS_RELEASE_V1.1.md)

**Complete Index**: [docs/INDEX.md](docs/INDEX.md) (39 documents)

---

## 🧪 Examples & Tests

### Working Examples

| Example | Location | Purpose |
|---------|----------|---------|
| Publisher (Node.js) | [examples/publisher-nodejs/](examples/publisher-nodejs/) | How to publish content |
| AI Client (Python) | [examples/client-python/](examples/client-python/) | How to verify & track usage |
| LangChain Integration | [examples/langchain-integration/](examples/langchain-integration/) | Custom document loader |
| E2E Test Suite | [examples/e2e-test/](examples/e2e-test/) | Complete API testing |
| Webflow Snippet | [examples/webflow-snippet/](examples/webflow-snippet/) | Embeddable JavaScript |

---

## 🔧 Configuration & Scripts

### Configuration Files (Root)
- [docker-compose.yml](docker-compose.yml) - Local development
- [azure-pipelines.yml](azure-pipelines.yml) - CI/CD pipeline
- [ecosystem.config.js](ecosystem.config.js) - PM2 config
- [.gitignore](.gitignore) - Git exclusions
- [.dockerignore](.dockerignore) - Docker exclusions

### Deployment Scripts
- [scripts/deploy-azure.sh](scripts/deploy-azure.sh) - Azure deployment
- [scripts/deploy.sh](scripts/deploy.sh) - General deployment

### Database Migrations
- [migrations/enable-public-access.sql](migrations/enable-public-access.sql) - RLS permissions
- [migrations/fix-rls-conflicts.sql](migrations/fix-rls-conflicts.sql) - RLS fixes

---

## 🌐 Live Endpoints

| Service | URL | Status |
|---------|-----|--------|
| **API** | https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io | ✅ Live |
| **API Docs** | https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/docs | ✅ Live |
| **Documentation** | https://aiindex-docs.azurewebsites.net | ✅ Live |
| **Health Check** | https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/health | ✅ Live |

---

## 🗂️ Directory Quick Reference

```
iaindex/
├── 📄 README.md                   Main README
├── 📄 PROJECT_STRUCTURE.md        Complete structure
├── 📄 NAVIGATION.md               This file
│
├── 📁 apps/                       Main applications
│   ├── 🐍 api/                    FastAPI backend
│   ├── ⚛️  web/                    Next.js frontend
│   └── 📘 docs/                   Docusaurus docs
│
├── 📁 packages/                   Client SDKs & tools
│   ├── 📦 sdk-nodejs/             Node.js SDK
│   ├── 🐍 sdk-python/             Python SDK
│   ├── 💻 cli/                    CLI tool
│   └── 🔌 wordpress-plugin/       WordPress plugin
│
├── 📁 examples/                   Working examples
│   ├── publisher-nodejs/          Publisher demo
│   ├── client-python/             Client demo
│   ├── langchain-integration/     LangChain loader
│   ├── e2e-test/                  E2E tests
│   └── webflow-snippet/           JS snippet
│
├── 📁 releases/                   Distribution packages
│   └── v1.0.0/                    Version 1.0.0
│       ├── *.tgz, *.whl           Built packages
│       ├── MANIFEST.md            Package manifest
│       └── DEPLOYMENT_GUIDE.md    Publishing guide
│
├── 📁 docs/                       Project documentation
│   ├── INDEX.md                   Documentation index
│   ├── deployment/                Deployment guides (12)
│   ├── guides/                    Development guides (6)
│   ├── testing/                   Test reports (3)
│   ├── migration/                 Migration docs (5)
│   └── marketing/                 Marketing materials (7)
│
├── 📁 migrations/                 Database migrations
├── 📁 scripts/                    Deployment scripts
├── 📁 logs/                       Deployment logs
└── 📁 archive/                    Historical docs
```

---

## 🔍 Common Tasks

### I Want To...

**Deploy the API to Azure**
1. Review [docs/deployment/DEPLOYMENT_PLAN.md](docs/deployment/DEPLOYMENT_PLAN.md)
2. Run [scripts/deploy-azure.sh](scripts/deploy-azure.sh)
3. Check [docs/deployment/AZURE_DEPLOYMENT_COMPLETE.md](docs/deployment/AZURE_DEPLOYMENT_COMPLETE.md)

**Publish npm Packages**
1. Read [releases/v1.0.0/DEPLOYMENT_GUIDE.md](releases/v1.0.0/DEPLOYMENT_GUIDE.md)
2. Navigate to `releases/v1.0.0/`
3. Run `npm publish iaindex-sdk-1.0.0.tgz --access public`
4. Run `npm publish iaindex-cli-1.0.0.tgz --access public`

**Publish Python Package**
1. Read [releases/v1.0.0/DEPLOYMENT_GUIDE.md](releases/v1.0.0/DEPLOYMENT_GUIDE.md)
2. Navigate to `releases/v1.0.0/`
3. Run `twine upload aiindex_sdk-1.0.0-py3-none-any.whl aiindex-sdk-1.0.0.tar.gz`

**Run Tests Locally**
1. Follow [docs/guides/LOCAL_TESTING_GUIDE.md](docs/guides/LOCAL_TESTING_GUIDE.md)
2. API: `cd apps/api && pytest`
3. Node.js SDK: `cd packages/sdk-nodejs && npm test`
4. Python SDK: `cd packages/sdk-python && pytest`

**Modify the API**
1. Edit files in `apps/api/src/routes/`
2. Update tests in `apps/api/tests/`
3. Run `pytest` to verify
4. Follow [docs/guides/BUILD_COMPLETE.md](docs/guides/BUILD_COMPLETE.md)

**Add Documentation**
1. Add markdown files to `apps/docs/docs/`
2. Update `apps/docs/sidebars.js`
3. Run `npm run build` in `apps/docs/`
4. Follow [docs/deployment/DOCS_DEPLOYMENT.md](docs/deployment/DOCS_DEPLOYMENT.md)

**Understand the Protocol**
1. Read [README.md](README.md) for overview
2. Review [docs/marketing/AIINDEX_V1.1_EXECUTIVE_BRIEF.md](docs/marketing/AIINDEX_V1.1_EXECUTIVE_BRIEF.md)
3. Check [spec/aiindex-spec-v1.1.md](spec/aiindex-spec-v1.1.md) for details

---

## 📊 Project Status

### ✅ Completed

- Backend API deployed to Azure Container Apps
- Documentation deployed to Azure Static Web Apps
- Database configured on Supabase
- Node.js SDK built and tested (96.4% pass rate)
- Python SDK built and tested (100% pass rate)
- CLI tool built and tested (100% functional)
- WordPress plugin built and ready
- All examples working
- E2E tests passing
- Distribution packages created (193 KB total)
- Comprehensive documentation (39 files, 388 KB)

### ⏳ Pending (Optional)

- npm package publication (requires user approval + credentials)
- PyPI package publication (requires user approval + credentials)
- WordPress plugin distribution decision

---

## 📞 Quick Links

| Resource | Link |
|----------|------|
| Live API | https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io |
| API Documentation | https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/docs |
| Public Docs | https://aiindex-docs.azurewebsites.net |
| Main README | [README.md](README.md) |
| Documentation Index | [docs/INDEX.md](docs/INDEX.md) |
| Project Structure | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| Release Packages | [releases/v1.0.0/](releases/v1.0.0/) |
| Deployment Guide | [releases/v1.0.0/DEPLOYMENT_GUIDE.md](releases/v1.0.0/DEPLOYMENT_GUIDE.md) |

---

**Last Updated**: 2025-10-17
**Version**: 1.1
**Status**: ✅ Production Ready

**Total**: ~14,000 lines of code • 39 documentation files • 5 distribution packages • 193 KB
