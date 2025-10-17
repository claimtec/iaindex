# GitHub Repository Setup for IAIndex

The npm packages reference `https://github.com/claimtec/iaindex.git` but this repository doesn't exist yet.

## Quick Setup Steps

### Option 1: Create Repository on GitHub

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `iaindex`
3. **Owner**: `claimtec` (or your organization/username)
4. **Description**: "Transparent, cryptographically-verifiable content provenance for the AI era"
5. **Public or Private**: Public (recommended for open source)
6. **Don't initialize** with README (we already have code)
7. Click **Create repository**

### Option 2: Use Different GitHub Account

If you want to use your personal account instead of `claimtec`:

**Repository URL format**: `https://github.com/YOUR_USERNAME/iaindex.git`

---

## After Creating GitHub Repository

### 1. Add Remote to Local Git

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Add the remote (replace with your actual URL)
git remote add origin https://github.com/claimtec/iaindex.git

# Or if using personal account:
# git remote add origin https://github.com/YOUR_USERNAME/iaindex.git
```

### 2. Commit All Changes

```bash
# Stage all changes
git add .

# Commit
git commit -m "feat: IAIndex v1.0.0 complete implementation

- Backend API deployed to Azure Container Apps
- Custom domain: api.iaindex.org
- Node.js SDK published to npm (iaindex-sdk@1.0.0)
- CLI tool published to npm (iaindex-cli@1.0.0)
- Python SDK ready for PyPI
- WordPress plugin ready for distribution
- Complete documentation and examples
- All packages tested and validated

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 3. Push to GitHub

```bash
# Push to main branch
git push -u origin main
```

### 4. Verify on GitHub

Visit your repository URL:
- `https://github.com/claimtec/iaindex`
- Or `https://github.com/YOUR_USERNAME/iaindex`

---

## Update Package Repository URLs (If Needed)

If you used a different GitHub account/organization, you'll need to update the npm packages:

### Update package.json Files

**Node.js SDK** (`packages/sdk-nodejs/package.json`):
```json
"repository": {
  "type": "git",
  "url": "https://github.com/YOUR_ACTUAL_USERNAME/iaindex.git",
  "directory": "packages/sdk-nodejs"
}
```

**CLI** (`packages/cli/package.json`):
```json
"repository": {
  "type": "git",
  "url": "https://github.com/YOUR_ACTUAL_USERNAME/iaindex.git",
  "directory": "packages/cli"
}
```

### Republish with Updated URLs

```bash
# Bump version to 1.0.1
cd packages/sdk-nodejs
npm version patch
npm publish

cd ../cli
npm version patch
npm publish
```

---

## Current Package Status

**Published on npm** with repository: `https://github.com/claimtec/iaindex.git`

- **iaindex-sdk@1.0.0**: https://www.npmjs.com/package/iaindex-sdk
- **iaindex-cli@1.0.0**: https://www.npmjs.com/package/iaindex-cli

The packages work fine even if the GitHub repo doesn't exist yet. The repository URL is just metadata for users to find the source code.

---

## Benefits of GitHub Repository

Once the repository is live:

### 1. Issue Tracking
Users can report bugs and request features via GitHub Issues

### 2. Contributions
Others can submit Pull Requests to improve the code

### 3. Releases
Create GitHub Releases for each version with changelogs

### 4. Documentation
GitHub Pages can host additional documentation

### 5. CI/CD
Set up GitHub Actions for automated testing and deployment

### 6. Visibility
- Star count shows popularity
- Appears in GitHub search
- Can add topics/tags for discoverability

---

## Recommended .gitignore Updates

Make sure these are in your `.gitignore`:

```
# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
.env

# Build outputs
dist/
build/
*.egg-info/
*.tgz
*.whl

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Secrets
.env.local
.env.production
*.pem
*.key
```

---

## Quick Commands Summary

```bash
# 1. Create repo on GitHub: https://github.com/new

# 2. Add remote
cd /Users/dineshanchetty/Documents/claimtec/iaindex
git remote add origin https://github.com/claimtec/iaindex.git

# 3. Commit and push
git add .
git commit -m "feat: IAIndex v1.0.0 complete"
git push -u origin main

# 4. Verify
open https://github.com/claimtec/iaindex
```

---

## What to Do Right Now

1. **Create the GitHub repository**: https://github.com/new
   - Name: `iaindex`
   - Owner: `claimtec` (or your account)
   - Public
   - Don't initialize

2. **Add remote and push** (commands above)

3. **Packages will automatically link** - npm will show the repo link

That's it! The packages are already published and working. GitHub is just for:
- Source code visibility
- Issue tracking
- Community contributions

---

**Current Status**:
- ✅ Packages published to npm
- ✅ API live at api.iaindex.org
- ⏳ GitHub repository needs to be created
- ⏳ PyPI publication pending

**Priority**: The GitHub repo is nice-to-have but not critical. Focus on PyPI publication first if needed!
