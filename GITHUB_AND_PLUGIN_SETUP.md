# GitHub Repository & WordPress Plugin Deployment

Let's get your GitHub repository live and deploy the WordPress plugin!

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI (Fastest)

```bash
# Install GitHub CLI if not installed
brew install gh

# Login
gh auth login

# Create repository
cd /Users/dineshanchetty/Documents/claimtec/iaindex
gh repo create claimtec/iaindex --public --source=. --remote=origin --push

# This creates the repo, adds remote, and pushes in one command!
```

### Option B: Using GitHub Web Interface

1. **Go to GitHub**: https://github.com/new

2. **Repository settings**:
   - **Owner**: `claimtec` (or your username)
   - **Repository name**: `iaindex`
   - **Description**: "Transparent, cryptographically-verifiable content provenance for the AI era"
   - **Visibility**: **Public** ✅
   - **Initialize**: ❌ Don't check any boxes (we have code)

3. **Click "Create repository"**

4. **Add remote and push**:
   ```bash
   cd /Users/dineshanchetty/Documents/claimtec/iaindex

   # Add remote
   git remote add origin https://github.com/claimtec/iaindex.git

   # Stage all files
   git add .

   # Commit
   git commit -m "feat: IAIndex v1.0.0 complete implementation

   - Backend API deployed to Azure Container Apps (api.iaindex.org)
   - Node.js SDK published to npm (iaindex-sdk@1.0.0)
   - Python SDK published to PyPI (aiindex-sdk@1.0.0)
   - CLI tool published to npm (iaindex-cli@1.0.0)
   - WordPress plugin ready for distribution
   - Complete documentation and examples
   - All packages tested and production ready

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"

   # Push to GitHub
   git push -u origin main
   ```

---

## Step 2: Create GitHub Release with WordPress Plugin

Once the repository is live:

```bash
# Create a release tag
git tag -a v1.0.0 -m "IAIndex v1.0.0 - Initial Release

- Node.js SDK (iaindex-sdk@1.0.0)
- Python SDK (aiindex-sdk@1.0.0)
- CLI tool (iaindex-cli@1.0.0)
- WordPress plugin
- Production API at api.iaindex.org"

# Push tag
git push origin v1.0.0
```

### Create Release on GitHub Web

1. **Go to releases**: https://github.com/claimtec/iaindex/releases/new

2. **Tag**: `v1.0.0`

3. **Release title**: `IAIndex v1.0.0 - Initial Release`

4. **Description**:
   ```markdown
   # IAIndex v1.0.0 🎉

   First stable release of IAIndex - transparent AI content tracking protocol.

   ## 📦 Published Packages

   - **Node.js SDK**: [iaindex-sdk@1.0.0](https://www.npmjs.com/package/iaindex-sdk)
   - **Python SDK**: [aiindex-sdk@1.0.0](https://pypi.org/project/aiindex-sdk/)
   - **CLI Tool**: [iaindex-cli@1.0.0](https://www.npmjs.com/package/iaindex-cli)

   ## 🌐 Production API

   - **Base URL**: https://api.iaindex.org
   - **Documentation**: https://api.iaindex.org/docs
   - **Status**: Production Ready

   ## 🔌 WordPress Plugin

   Download the WordPress plugin ZIP file attached to this release.

   ## 📚 Getting Started

   ```bash
   # Node.js
   npm install iaindex-sdk

   # Python
   pip install aiindex-sdk

   # CLI
   npm install -g iaindex-cli
   ```

   ## 📖 Documentation

   - [Quick Start Guide](docs/guides/QUICKSTART.md)
   - [API Documentation](https://api.iaindex.org/docs)
   - [Examples](examples/)

   ## ✨ Features

   - Cryptographic content signing (ECDSA)
   - Domain verification
   - Receipt tracking for AI usage
   - Merkle tree attestations
   - OpenTimestamps integration
   ```

5. **Attach files**:
   - Drag and drop: `releases/v1.0.0/iaindex-wordpress-plugin-v1.0.0.zip`

6. **Click "Publish release"**

---

## Step 3: WordPress Plugin Distribution

You now have three options:

### Option 1: GitHub Releases (Recommended - Easiest)

✅ Already done in Step 2!

**Users can download from**:
```
https://github.com/claimtec/iaindex/releases/download/v1.0.0/iaindex-wordpress-plugin-v1.0.0.zip
```

**Installation instructions**:
1. Download ZIP from GitHub releases
2. WordPress Admin → Plugins → Add New → Upload Plugin
3. Upload ZIP file
4. Activate plugin

### Option 2: WordPress.org Plugin Directory (Most Visible)

**Pros**: Listed in official WordPress plugin directory
**Cons**: Takes 7-14 days for review

**Steps**:
1. Create account: https://wordpress.org/plugins/developers/add/
2. Submit plugin ZIP
3. Wait for review
4. Once approved, available at: `https://wordpress.org/plugins/iaindex/`

**Submission form**:
- Plugin name: IAIndex
- Description: Content verification and AI usage tracking
- Plugin ZIP: Upload from releases folder

### Option 3: Your Own Website

Host the ZIP file on your documentation site:

```bash
# Copy to documentation site
cp releases/v1.0.0/iaindex-wordpress-plugin-v1.0.0.zip /path/to/docs/downloads/

# Add download link to documentation
```

---

## Step 4: Update README with GitHub Info

After repository is live, update the main README.md:

```markdown
## 🏠 Repository

- **GitHub**: https://github.com/claimtec/iaindex
- **Issues**: https://github.com/claimtec/iaindex/issues
- **Releases**: https://github.com/claimtec/iaindex/releases

## 📥 WordPress Plugin

Download from [GitHub Releases](https://github.com/claimtec/iaindex/releases/latest)
```

---

## Step 5: Add README Badges

Make your README look professional:

```markdown
# IAIndex

[![npm SDK](https://img.shields.io/npm/v/iaindex-sdk)](https://www.npmjs.com/package/iaindex-sdk)
[![npm CLI](https://img.shields.io/npm/v/iaindex-cli)](https://www.npmjs.com/package/iaindex-cli)
[![PyPI](https://img.shields.io/pypi/v/aiindex-sdk)](https://pypi.org/project/aiindex-sdk/)
[![GitHub release](https://img.shields.io/github/v/release/claimtec/iaindex)](https://github.com/claimtec/iaindex/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![API Status](https://img.shields.io/website?url=https%3A%2F%2Fapi.iaindex.org%2Fhealth)](https://api.iaindex.org)

Transparent, cryptographically-verifiable content provenance for the AI era.
```

---

## Step 6: Set Up GitHub Pages (Optional)

For additional documentation hosting:

```bash
# Create gh-pages branch
git checkout -b gh-pages
git push origin gh-pages

# Go to Settings → Pages
# Source: gh-pages branch
# Your site will be at: https://claimtec.github.io/iaindex/
```

---

## WordPress Plugin Installation Guide

Create a file for users: `packages/wordpress-plugin/INSTALL.md`

```markdown
# IAIndex WordPress Plugin - Installation Guide

## Method 1: Download from GitHub

1. Go to [Releases](https://github.com/claimtec/iaindex/releases/latest)
2. Download `iaindex-wordpress-plugin-v1.0.0.zip`
3. WordPress Admin → Plugins → Add New → Upload Plugin
4. Choose downloaded ZIP file
5. Click "Install Now"
6. Click "Activate Plugin"

## Method 2: Manual Installation

1. Download plugin ZIP
2. Extract to `/wp-content/plugins/iaindex/`
3. Go to WordPress Admin → Plugins
4. Find "IAIndex" and click "Activate"

## Configuration

1. Go to Settings → IAIndex
2. Enter your domain name
3. Generate or paste your private key
4. Configure verification method
5. Save settings

## Usage

The plugin automatically:
- Generates IAIndex files from your posts
- Tracks content verification
- Displays receipt dashboard
- Handles webhook notifications

For more information, visit: https://api.iaindex.org/docs
```

---

## Quick Command Summary

```bash
# 1. Create GitHub repository (web interface)
# Visit: https://github.com/new

# 2. Push code
cd /Users/dineshanchetty/Documents/claimtec/iaindex
git remote add origin https://github.com/claimtec/iaindex.git
git add .
git commit -m "feat: IAIndex v1.0.0 complete implementation"
git push -u origin main

# 3. Create tag and push
git tag -a v1.0.0 -m "IAIndex v1.0.0 - Initial Release"
git push origin v1.0.0

# 4. Create release on GitHub web
# Visit: https://github.com/claimtec/iaindex/releases/new
# Attach: releases/v1.0.0/iaindex-wordpress-plugin-v1.0.0.zip

# 5. Update README with badges and links

# Done!
```

---

## Verification Checklist

After GitHub is live:

- [ ] Repository created and public
- [ ] Code pushed successfully
- [ ] README displays correctly
- [ ] v1.0.0 release created
- [ ] WordPress plugin ZIP attached to release
- [ ] npm packages show correct GitHub link
- [ ] Installation instructions updated
- [ ] Badges added to README

---

## Next: Announce Your Launch!

With GitHub live and plugin available:

### Social Media
- Twitter/X: Link to GitHub repo
- LinkedIn: Professional announcement with repo link
- Reddit: Share on r/wordpress, r/programming
- Hacker News: Submit GitHub URL

### WordPress Community
- WordPress.org forums
- WordPress Facebook groups
- WP Tavern (news site)

---

**Ready to go live?** Just need to create the GitHub repository and follow the steps above!
