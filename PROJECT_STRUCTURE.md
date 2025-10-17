# AIIndex v1.1 - Project Structure

Complete directory structure and organization of the AIIndex project.

```
iaindex/
│
├── README.md                      # Main project README
├── PROJECT_STRUCTURE.md           # This file
├── .gitignore                     # Git ignore rules
├── .dockerignore                  # Docker ignore rules
├── docker-compose.yml             # Local development setup
├── azure-pipelines.yml            # Azure CI/CD pipeline
├── ecosystem.config.js            # PM2 configuration
│
├── apps/                          # Main applications
│   ├── api/                       # FastAPI backend (Python 3.11)
│   │   ├── src/                   # Source code
│   │   │   ├── routes/           # API endpoints
│   │   │   ├── services/         # Business logic
│   │   │   ├── middleware/       # Authentication, CORS, etc.
│   │   │   ├── models/           # Data models
│   │   │   └── config.py         # Configuration
│   │   ├── Dockerfile            # Container image
│   │   ├── requirements.txt      # Python dependencies
│   │   └── tests/                # API tests
│   │
│   ├── web/                       # Next.js frontend (not actively used)
│   │   ├── src/                  # React components
│   │   ├── public/               # Static assets
│   │   ├── Dockerfile            # Container image
│   │   └── package.json          # Node.js dependencies
│   │
│   └── docs/                      # Docusaurus documentation site
│       ├── docs/                 # Documentation content
│       ├── src/                  # Custom components
│       ├── static/               # Static assets
│       └── docusaurus.config.js  # Site configuration
│
├── packages/                      # Client libraries and tools
│   ├── sdk-nodejs/               # Node.js SDK (@iaindex/sdk)
│   │   ├── src/                  # TypeScript source
│   │   │   ├── publisher.ts     # Publisher class
│   │   │   ├── client.ts        # Client class
│   │   │   ├── crypto.ts        # ECDSA utilities
│   │   │   └── api-client.ts    # API wrapper
│   │   ├── tests/                # Jest tests (27 tests)
│   │   ├── package.json          # Package manifest
│   │   └── iaindex-sdk-1.0.0.tgz # Built package
│   │
│   ├── sdk-python/               # Python SDK (iaindex-sdk)
│   │   ├── aiindex/              # Package source
│   │   │   ├── publisher.py     # Publisher class
│   │   │   ├── client.py        # Client class
│   │   │   └── crypto.py        # ECDSA utilities
│   │   ├── tests/                # Pytest tests
│   │   ├── setup.py              # Package setup
│   │   ├── pyproject.toml        # Modern Python config
│   │   └── dist/                 # Built packages (wheel + source)
│   │
│   ├── cli/                      # CLI tool (@iaindex/cli)
│   │   ├── src/                  # TypeScript source
│   │   │   ├── commands/        # CLI commands
│   │   │   │   ├── verify.ts   # Domain verification
│   │   │   │   ├── keys.ts     # Key generation
│   │   │   │   ├── index-gen.ts # Index creation
│   │   │   │   └── auth.ts     # Authentication
│   │   │   ├── utils/           # Utilities
│   │   │   └── index.ts         # Entry point
│   │   ├── package.json         # Package manifest
│   │   └── iaindex-cli-1.0.0.tgz # Built package
│   │
│   └── wordpress-plugin/         # WordPress plugin
│       ├── iaindex.php           # Main plugin file
│       ├── admin/                # Admin interface
│       │   ├── settings.php     # Settings page
│       │   └── dashboard.php    # Dashboard widget
│       ├── includes/             # Core functionality
│       │   ├── index-generator.php  # Index generation
│       │   ├── webhook.php      # Receipt handler
│       │   └── api-client.php   # API wrapper
│       ├── assets/               # CSS/JS/images
│       └── iaindex-wordpress-plugin-v1.0.0.zip  # Built plugin
│
├── examples/                      # Working examples and demos
│   ├── publisher-nodejs/         # Publisher example (Node.js)
│   │   ├── index.js              # Main example script
│   │   └── package.json          # Dependencies
│   │
│   ├── client-python/            # AI client example (Python)
│   │   ├── main.py               # Main example script
│   │   └── requirements.txt      # Dependencies
│   │
│   ├── langchain-integration/    # LangChain custom loader
│   │   ├── iaindex_loader.py    # Custom document loader
│   │   ├── example.py            # Usage example
│   │   └── requirements.txt      # Dependencies
│   │
│   ├── e2e-test/                 # End-to-end test suite
│   │   ├── test.py               # E2E tests (8 tests)
│   │   └── requirements.txt      # Dependencies
│   │
│   └── webflow-snippet/          # Embeddable JavaScript
│       ├── iaindex-snippet.js    # Main snippet
│       └── README.md             # Integration guide
│
├── docs/                          # Project documentation
│   ├── INDEX.md                  # Documentation index
│   ├── deployment/               # Deployment documentation (12 files)
│   │   ├── AZURE_DEPLOYMENT_COMPLETE.md
│   │   ├── AZURE_DEPLOYMENT_SUMMARY.md
│   │   ├── DEPLOYMENT_PLAN.md
│   │   └── ...
│   ├── guides/                   # Development guides (6 files)
│   │   ├── QUICKSTART.md
│   │   ├── START_HERE.md
│   │   ├── BUILD_COMPLETE.md
│   │   └── ...
│   ├── testing/                  # Test reports (3 files)
│   │   ├── END_TO_END_TEST_REPORT.md
│   │   ├── API_ENDPOINTS_FIXED.md
│   │   └── SCHEMA_FIXES_APPLIED.md
│   ├── migration/                # Migration guides (5 files)
│   │   ├── MIGRATION_COMPLETE.md
│   │   ├── MIGRATION_V1.0_TO_V1.1.md
│   │   └── ...
│   └── marketing/                # Marketing materials (7 files)
│       ├── AIINDEX_ONE_PAGER.md
│       ├── PRESS_RELEASE_V1.1.md
│       └── ...
│
├── releases/                      # Distribution packages
│   └── v1.0.0/                   # Version 1.0.0 release
│       ├── iaindex-sdk-1.0.0.tgz           # Node.js SDK (15 KB)
│       ├── iaindex_sdk-1.0.0-py3-none-any.whl  # Python wheel (29 KB)
│       ├── aiindex-sdk-1.0.0.tar.gz        # Python source (28 KB)
│       ├── iaindex-cli-1.0.0.tgz           # CLI tool (72 KB)
│       ├── iaindex-wordpress-plugin-v1.0.0.zip  # WordPress (49 KB)
│       ├── SHA256SUMS.txt         # Package checksums
│       ├── MANIFEST.md            # Package details (6.2 KB)
│       └── DEPLOYMENT_GUIDE.md    # Publishing guide (21 KB)
│
├── migrations/                    # Database migrations
│   ├── enable-public-access.sql  # RLS permissions
│   └── fix-rls-conflicts.sql     # RLS fixes
│
├── scripts/                       # Automation scripts
│   ├── deploy-azure.sh           # Azure deployment (11 KB)
│   └── deploy.sh                 # General deployment (6.6 KB)
│
├── logs/                          # Deployment logs
│   ├── azure-deployment.log      # Azure deployment log (49 KB)
│   └── deployment_staging_*.log  # Staging logs
│
├── archive/                       # Historical documentation
│   ├── PROJECT_COMPLETE.md       # Original completion report
│   ├── V1.1_IMPLEMENTATION_COMPLETE.md  # v1.1 summary
│   ├── OPTIONAL_PROVIDER_KEYS.md # API key docs
│   ├── README.old.md             # Previous README
│   ├── INFRASTRUCTURE_FILES.txt  # File listing
│   └── MIGRATION_FILES_INDEX.txt # Migration index
│
├── infra/                         # Infrastructure code
│   ├── supabase/                 # Supabase configuration
│   ├── terraform/                # Terraform IaC
│   └── merkle/                   # Merkle tree utilities
│
├── spec/                          # Protocol specification
│   └── aiindex-spec-v1.1.md     # IAIndex v1.1 specification
│
└── tests/                         # Test suites
    └── e2e/                      # End-to-end tests
        └── test_api.py           # API integration tests
```

## 📊 Directory Statistics

### Source Code

| Directory | Purpose | Language | Lines of Code |
|-----------|---------|----------|---------------|
| `apps/api/` | Backend API | Python | ~3,500 |
| `apps/docs/` | Documentation site | MDX/JS | ~2,000 |
| `packages/sdk-nodejs/` | Node.js SDK | TypeScript | ~1,650 |
| `packages/sdk-python/` | Python SDK | Python | ~1,200 |
| `packages/cli/` | CLI tool | TypeScript | ~1,680 |
| `packages/wordpress-plugin/` | WordPress plugin | PHP/JS | ~1,680 |
| `examples/` | Examples & tests | Mixed | ~2,000 |

**Total**: ~14,000 lines of code

### Documentation

| Directory | Files | Total Size |
|-----------|-------|------------|
| `docs/deployment/` | 12 | ~100 KB |
| `docs/guides/` | 6 | ~77 KB |
| `docs/testing/` | 3 | ~42 KB |
| `docs/migration/` | 5 | ~55 KB |
| `docs/marketing/` | 7 | ~62 KB |
| `archive/` | 6 | ~52 KB |

**Total**: 39 documentation files, ~388 KB

### Distribution Packages

| Package | Size | Type |
|---------|------|------|
| Node.js SDK | 15 KB | npm tarball |
| Python SDK (wheel) | 29 KB | Python wheel |
| Python SDK (source) | 28 KB | Source tarball |
| CLI tool | 72 KB | npm tarball |
| WordPress plugin | 49 KB | ZIP file |

**Total**: 193 KB across 5 packages

## 🗂️ Key Files

### Root Configuration Files

- **docker-compose.yml** - Local development environment
- **azure-pipelines.yml** - CI/CD pipeline for Azure
- **ecosystem.config.js** - PM2 process management
- **.gitignore** - Git exclusions
- **.dockerignore** - Docker build exclusions

### Package Configuration Files

Each package has its own configuration:
- **package.json** - Node.js packages (SDK, CLI)
- **setup.py / pyproject.toml** - Python packages
- **tsconfig.json** - TypeScript configuration
- **jest.config.js** - Jest test configuration
- **pytest.ini** - Pytest configuration

### Environment Files (Not in Git)

These files are required but not committed:
- `.env` - Local environment variables
- `.env.production` - Production environment variables
- `.azure/` - Azure credentials and configuration

## 📦 Build Artifacts

### Generated at Build Time

```
apps/api/
├── __pycache__/           # Python bytecode cache
└── .pytest_cache/         # Pytest cache

apps/docs/
├── build/                 # Built documentation site
└── .docusaurus/           # Docusaurus cache

packages/sdk-nodejs/
├── dist/                  # Compiled JavaScript
├── node_modules/          # Dependencies
└── *.tgz                  # Built tarball

packages/sdk-python/
├── dist/                  # Built packages (wheel + source)
├── build/                 # Build artifacts
├── *.egg-info/           # Package metadata
└── __pycache__/          # Python bytecode cache

packages/cli/
├── dist/                  # Compiled JavaScript
├── node_modules/          # Dependencies
└── *.tgz                  # Built tarball

packages/wordpress-plugin/
└── *.zip                  # Built plugin archive
```

## 🚀 Deployment Locations

### Azure Container Apps (API)
- **URL**: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
- **Region**: East US
- **Container Registry**: ACR (Azure Container Registry)
- **Source**: `apps/api/`

### Azure Static Web Apps (Docs)
- **URL**: https://aiindex-docs.azurewebsites.net
- **Source**: `apps/docs/`
- **Build Command**: `npm run build`
- **Output Directory**: `build/`

### Package Registries (Pending)
- **npm**: `@iaindex/sdk`, `@iaindex/cli`
- **PyPI**: `iaindex-sdk`
- **WordPress**: Plugin directory or direct download

## 🔍 Finding Things

### I need to...

**Modify the API**
→ `apps/api/src/routes/` - API endpoints
→ `apps/api/src/services/` - Business logic

**Work on the Node.js SDK**
→ `packages/sdk-nodejs/src/` - Source code
→ `packages/sdk-nodejs/tests/` - Tests

**Work on the Python SDK**
→ `packages/sdk-python/aiindex/` - Source code
→ `packages/sdk-python/tests/` - Tests

**Add a CLI command**
→ `packages/cli/src/commands/` - CLI commands
→ `packages/cli/src/index.ts` - Register command

**Update documentation**
→ `apps/docs/docs/` - Documentation content
→ `docs/` - Project documentation

**Find examples**
→ `examples/` - Working examples
→ `packages/*/tests/` - Test code examples

**Deploy to Azure**
→ `scripts/deploy-azure.sh` - Deployment script
→ `docs/deployment/` - Deployment guides

**Publish packages**
→ `releases/v1.0.0/DEPLOYMENT_GUIDE.md` - Publishing instructions
→ `releases/v1.0.0/` - Distribution packages

## 📝 Notes

- All build artifacts are excluded from Git via `.gitignore`
- Environment variables are managed via Azure Key Vault in production
- Package distributions are in `releases/v1.0.0/` ready for publication
- Documentation is organized by category in `docs/` subdirectories
- All deployment logs are preserved in `logs/` for troubleshooting

---

**Last Updated**: 2025-10-17
**Version**: 1.1
**Status**: Production Ready
