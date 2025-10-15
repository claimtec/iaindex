# 🔄 AIIndex v1.1 - Git & DevOps Guide

**Last Updated**: 2025-10-14 21:50:00
**For**: Version control and CI/CD automation

---

## 📋 Overview

This guide covers:
- ✅ Git repository setup and workflow
- ✅ Branch strategy (Git Flow)
- ✅ Azure DevOps CI/CD pipeline
- ✅ Automated testing and deployment
- ✅ Release management

---

## 🌳 Git Repository Setup

### 1. Initialize Repository (Already Done) ✅

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex
git init
```

### 2. Initial Commit

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AIIndex v1.1 complete implementation

- Complete API with v1.1 features (policy enforcement, bot reputation, fraud detection)
- Dashboard with 13 routes including v1.1 pages (policy, compliance, provenance)
- Database schema with 11 tables
- 8 CMS plugins (WordPress, Shopify, Webflow, Bubble, Wix, Squarespace, Framer, Ghost)
- 2 AI connectors (LangChain, LlamaIndex)
- PM2 configuration for production deployment
- Azure DevOps pipeline configuration
- Comprehensive documentation (18+ docs)

Deployment ready for Azure with PM2 process management."
```

### 3. Connect to Remote Repository

```bash
# Create repository on Azure Repos or GitHub
# Then connect:

# For Azure DevOps
git remote add origin https://dev.azure.com/YOUR_ORG/aiindex/_git/aiindex
git branch -M main
git push -u origin main

# For GitHub
git remote add origin https://github.com/YOUR_USERNAME/aiindex.git
git branch -M main
git push -u origin main
```

---

## 🌿 Git Flow Branch Strategy

### Branch Structure

```
main            → Production-ready code
├── develop     → Integration branch for features
    ├── feature/policy-enforcement
    ├── feature/compliance-dashboard
    ├── feature/ai-connectors
    └── hotfix/critical-bug-fix
```

### Branch Types

1. **main** - Production branch
   - Always deployable
   - Protected (requires PR approval)
   - Deploys to production automatically

2. **develop** - Development branch
   - Integration branch for features
   - Deploys to staging automatically
   - Merge features here for testing

3. **feature/** - Feature branches
   - Created from: develop
   - Merged into: develop
   - Naming: `feature/short-description`
   - Example: `feature/add-c2pa-support`

4. **hotfix/** - Hotfix branches
   - Created from: main
   - Merged into: main and develop
   - Naming: `hotfix/bug-description`
   - Example: `hotfix/fix-auth-vulnerability`

5. **release/** - Release branches
   - Created from: develop
   - Merged into: main and develop
   - Naming: `release/v1.2.0`
   - For final testing before production

---

## 🚀 Git Workflow Examples

### Starting a New Feature

```bash
# 1. Create develop branch (first time)
git checkout -b develop main
git push -u origin develop

# 2. Create feature branch
git checkout -b feature/add-embeddings develop

# 3. Make changes and commit
git add .
git commit -m "feat: add vector embeddings support for semantic search"

# 4. Push feature branch
git push -u origin feature/add-embeddings

# 5. Create Pull Request (PR) in Azure DevOps or GitHub
# - Target: develop
# - Reviewers: team members
# - Run automated tests

# 6. Merge PR after approval
# - Squash commits
# - Delete feature branch

# 7. Update local develop
git checkout develop
git pull origin develop

# 8. Delete local feature branch
git branch -d feature/add-embeddings
```

### Creating a Release

```bash
# 1. Create release branch from develop
git checkout -b release/v1.2.0 develop

# 2. Update version numbers
# - package.json
# - apps/api/src/config.py (APP_VERSION)
# - CHANGELOG.md

# 3. Commit version changes
git commit -am "chore: bump version to 1.2.0"

# 4. Push release branch
git push -u origin release/v1.2.0

# 5. Test thoroughly

# 6. Merge to main
git checkout main
git merge --no-ff release/v1.2.0 -m "Release v1.2.0"
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

# 7. Merge back to develop
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# 8. Delete release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

### Hotfix Workflow

```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/fix-sql-injection main

# 2. Fix the issue
git add .
git commit -m "fix: prevent SQL injection in receipts endpoint"

# 3. Push hotfix
git push -u origin hotfix/fix-sql-injection

# 4. Merge to main
git checkout main
git merge --no-ff hotfix/fix-sql-injection -m "Hotfix: SQL injection vulnerability"
git tag -a v1.1.1 -m "Hotfix v1.1.1"
git push origin main --tags

# 5. Merge to develop
git checkout develop
git merge --no-ff hotfix/fix-sql-injection
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/fix-sql-injection
git push origin --delete hotfix/fix-sql-injection
```

---

## 🔧 Azure DevOps Setup

### 1. Create Azure DevOps Organization

1. Go to https://dev.azure.com
2. Click "Start free"
3. Create organization (e.g., "aiindex-org")
4. Create project "aiindex"

### 2. Connect Repository

```bash
# Initialize Azure Repos
git remote add origin https://dev.azure.com/aiindex-org/aiindex/_git/aiindex
git push -u origin main develop
```

### 3. Configure Pipeline

**File**: [azure-pipelines.yml](./azure-pipelines.yml) (already created)

#### Pipeline Features:
- ✅ Triggers on push to main/develop/feature branches
- ✅ Builds API, Dashboard, and Docs
- ✅ Runs automated tests
- ✅ Deploys to staging (on develop)
- ✅ Deploys to production (on main)
- ✅ Uses PM2 for zero-downtime deployment

#### Enable Pipeline:

1. Go to Azure DevOps → Pipelines
2. Click "New Pipeline"
3. Select "Azure Repos Git"
4. Select "aiindex" repository
5. Choose "Existing Azure Pipelines YAML file"
6. Select `/azure-pipelines.yml`
7. Click "Run"

### 4. Configure Environments

Create environments in Azure DevOps:

1. Go to Pipelines → Environments
2. Create "staging" environment
   - Add approval gates (optional)
   - Link to staging server
3. Create "production" environment
   - **Required**: Add approval gates
   - Link to production server

### 5. Configure Service Connections

#### SSH Connection (for PM2 deployment):

1. Go to Project Settings → Service connections
2. Click "New service connection"
3. Select "SSH"
4. Configure:
   - **Name**: `staging-server` or `production-server`
   - **Host name**: Your server IP/domain
   - **Port**: 22
   - **Username**: Your SSH user
   - **Private Key**: Your SSH private key
5. Click "Verify and save"

---

## 🔐 Branch Protection Rules

### Main Branch Protection

1. Go to Project Settings → Repositories
2. Select "main" branch
3. Enable:
   - ✅ **Require a minimum number of reviewers**: 2
   - ✅ **Check for linked work items**: Yes
   - ✅ **Require build validation**: azure-pipelines
   - ✅ **Block force pushes**: Yes
   - ✅ **Block branch deletion**: Yes

### Develop Branch Protection

1. Select "develop" branch
2. Enable:
   - ✅ **Require a minimum number of reviewers**: 1
   - ✅ **Require build validation**: azure-pipelines
   - ✅ **Block force pushes**: Yes

---

## 📝 Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

### Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **ci**: CI/CD changes

### Examples:

```bash
# Feature
git commit -m "feat(api): add policy enforcement middleware

Implements v1.1 policy enforcement with:
- Training vs retrieval differentiation
- HTTP 403 denial with signed receipts
- 5-minute policy caching per domain

Closes #123"

# Bug fix
git commit -m "fix(dashboard): resolve policy page rendering issue

Fixed React hydration error on policy configuration page
when toggling render fallback setting.

Fixes #456"

# Documentation
git commit -m "docs: update deployment guide with PM2 instructions"

# Refactor
git commit -m "refactor(api): extract rate limiting to middleware"

# Breaking change
git commit -m "feat(api)!: change receipt signature algorithm to ES256

BREAKING CHANGE: All clients must update to ES256 signatures.
RS256 signatures will be rejected after 2025-11-01."
```

---

## 🧪 Automated Testing

### Test Types

1. **Unit Tests** - Individual functions/components
2. **Integration Tests** - API endpoints, database interactions
3. **E2E Tests** - Full user workflows
4. **Smoke Tests** - Basic health checks

### Running Tests Locally

```bash
# API tests
cd apps/api
pytest tests/ -v

# Dashboard tests (if configured)
cd apps/web
npm test

# E2E tests
cd tests
pytest e2e/ -v

# Smoke tests
./scripts/smoke-tests.sh staging
```

### CI Test Execution

Tests run automatically on:
- ✅ Every commit to feature branches
- ✅ Pull requests to develop/main
- ✅ Scheduled nightly (E2E tests)

---

## 📦 Release Process

### Semantic Versioning

Format: `MAJOR.MINOR.PATCH` (e.g., `1.1.0`)

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

**Before Release**:
- [ ] All tests passing
- [ ] Changelog updated
- [ ] Version bumped in:
  - [ ] package.json (apps/web, apps/docs)
  - [ ] apps/api/src/config.py (APP_VERSION)
  - [ ] spec/aiindex.v1.1.schema.json (version field)
- [ ] Documentation updated
- [ ] Migration scripts tested
- [ ] Release notes drafted

**Release**:
- [ ] Create release branch
- [ ] Final testing on staging
- [ ] Merge to main
- [ ] Create Git tag
- [ ] Deploy to production
- [ ] Verify deployment

**After Release**:
- [ ] Monitor logs for errors
- [ ] Publish release notes
- [ ] Update status page
- [ ] Notify stakeholders
- [ ] Merge back to develop

### Creating a Release

```bash
# 1. Update CHANGELOG.md
cat >> CHANGELOG.md <<EOF

## [1.2.0] - 2025-10-15

### Added
- Vector embeddings support with Pinecone integration
- Semantic search endpoint for verified publishers
- Enhanced compliance dashboard with fraud analytics

### Fixed
- Policy configuration page hydration error
- Rate limit header parsing in middleware

### Changed
- Improved bot reputation algorithm
- Updated LangChain connector to v0.3
EOF

# 2. Create release branch
git checkout -b release/v1.2.0 develop

# 3. Bump versions
# Edit files: package.json, config.py, etc.

# 4. Commit and push
git commit -am "chore: release v1.2.0"
git push -u origin release/v1.2.0

# 5. Test on staging

# 6. Merge to main
git checkout main
git merge --no-ff release/v1.2.0 -m "Release v1.2.0"
git tag -a v1.2.0 -m "Release v1.2.0

## Highlights
- Vector embeddings support
- Semantic search
- Enhanced compliance dashboard

See CHANGELOG.md for full details."

git push origin main --tags

# 7. Merge to develop
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# 8. Create GitHub/Azure DevOps Release
# Go to Releases → New Release
# Tag: v1.2.0
# Attach: release notes, binaries (if any)
```

---

## 🔄 CI/CD Pipeline Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                     COMMIT TO BRANCH                         │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    Feature/Hotfix         Develop/Main
          │                     │
          ▼                     ▼
   ┌──────────────┐      ┌──────────────┐
   │  Build Only  │      │ Build + Test │
   └──────────────┘      └──────┬───────┘
                                 │
                        ┌────────┴────────┐
                        │                 │
                    Develop            Main
                        │                 │
                        ▼                 ▼
              ┌──────────────┐  ┌──────────────┐
              │Deploy Staging│  │Deploy Prod   │
              │(Auto)        │  │(Manual Approval)
              └──────┬───────┘  └──────┬───────┘
                     │                 │
                     ▼                 ▼
              ┌──────────────┐  ┌──────────────┐
              │Smoke Tests   │  │Smoke Tests   │
              └──────────────┘  └──────────────┘
```

---

## 📊 Monitoring Deployments

### Azure DevOps Monitoring

1. Go to Pipelines → Runs
2. View:
   - Build duration
   - Test results
   - Deployment status
   - Logs

### PM2 Monitoring (on server)

```bash
# SSH to server
ssh user@your-server.com

# Check PM2 status
pm2 status

# View logs
pm2 logs

# Monitor in real-time
pm2 monit
```

### Application Insights (Optional)

```bash
# Install Azure Monitor
pip install opencensus-ext-azure

# Add to API
from opencensus.ext.azure import metrics_exporter

exporter = metrics_exporter.new_metrics_exporter(
    connection_string='YOUR_CONNECTION_STRING'
)
```

---

## 🚨 Rollback Procedure

### If Deployment Fails:

```bash
# 1. SSH to server
ssh user@your-server.com

# 2. Rollback to previous version
cd /var/www/aiindex
git reset --hard HEAD~1

# 3. Reload PM2
pm2 reload ecosystem.config.js --env production

# 4. Verify
pm2 logs
curl http://localhost:8000/health
```

### If Database Migration Fails:

```bash
# 1. Restore database backup
psql $DATABASE_URL < backups/pre-deploy-backup.sql

# 2. Rollback code (as above)
```

---

## ✅ DevOps Checklist

### Initial Setup
- [x] Git repository initialized
- [x] .gitignore configured
- [x] Azure DevOps project created
- [ ] Repository connected to Azure Repos
- [ ] Branch protection rules enabled
- [ ] Azure Pipeline configured
- [ ] Service connections set up (SSH)
- [ ] Environments created (staging, production)
- [ ] PM2 installed on servers

### Ongoing
- [ ] Run automated tests on every PR
- [ ] Require code review for main/develop
- [ ] Deploy to staging automatically
- [ ] Require manual approval for production
- [ ] Monitor deployment success/failure
- [ ] Keep CHANGELOG.md updated
- [ ] Tag releases with semantic versions

---

## 📚 Quick Reference

```bash
# Create feature branch
git checkout -b feature/my-feature develop

# Commit with convention
git commit -m "feat(scope): description"

# Push and create PR
git push -u origin feature/my-feature

# Merge feature to develop (via PR)
# Azure Pipeline runs: Build → Test → Deploy Staging

# Create release
git checkout -b release/v1.2.0 develop
# Bump versions, test, then:
git checkout main
git merge --no-ff release/v1.2.0
git tag v1.2.0
git push origin main --tags

# Azure Pipeline runs: Build → Test → Deploy Production (with approval)

# Hotfix
git checkout -b hotfix/critical-fix main
# Fix, commit, then:
git checkout main
git merge --no-ff hotfix/critical-fix
git tag v1.1.1
git push origin main --tags
git checkout develop
git merge --no-ff hotfix/critical-fix
git push origin develop
```

---

## 🎓 Resources

- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Azure Pipelines**: https://docs.microsoft.com/en-us/azure/devops/pipelines/
- **PM2 Docs**: https://pm2.keymetrics.io/docs/

---

**Last Updated**: 2025-10-14 21:50:00
**Status**: Git & DevOps configured ✅
