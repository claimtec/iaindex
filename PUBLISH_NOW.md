# Publish IAIndex v1.0.0 - Step-by-Step Instructions

**Everything is ready!** Follow these steps to publish all packages.

---

## Step 1: Publish to npm (Node.js SDK & CLI)

### 1a. Login to npm

```bash
npm login
```

This will open your browser. Log in with your npm account credentials.

**If you don't have an npm account**:
1. Go to https://www.npmjs.com/signup
2. Create a free account
3. Then run `npm login`

### 1b. Verify Login

```bash
npm whoami
```

Should show your username.

### 1c. Publish Node.js SDK

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/releases/v1.0.0
npm publish iaindex-sdk-1.0.0.tgz --access public
```

**Expected output**:
```
+ @iaindex/sdk@1.0.0
```

### 1d. Publish CLI Tool

```bash
npm publish iaindex-cli-1.0.0.tgz --access public
```

**Expected output**:
```
+ @iaindex/cli@1.0.0
```

### 1e. Verify npm Publication

```bash
npm view @iaindex/sdk
npm view @iaindex/cli
```

---

## Step 2: Publish to PyPI (Python SDK)

### 2a. Configure PyPI Credentials

**Option A: Using API Token (Recommended)**

1. Go to https://pypi.org/account/register/ (if no account)
2. Log in to https://pypi.org
3. Go to Account Settings → API tokens
4. Create new token with scope: "Entire account"
5. Copy the token (starts with `pypi-`)

**Option B: Using Username/Password**

Have your PyPI username and password ready.

### 2b. Publish to PyPI

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

# Option A: With API token
python3 -m twine upload dist/* --username __token__ --password pypi-YOUR_TOKEN_HERE

# Option B: With username/password (will prompt)
python3 -m twine upload dist/*
```

**Expected output**:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading aiindex_sdk-1.0.0-py3-none-any.whl
Uploading aiindex-sdk-1.0.0.tar.gz
View at: https://pypi.org/project/aiindex-sdk/1.0.0/
```

### 2c. Verify PyPI Publication

```bash
pip3 install aiindex-sdk
python3 -c "from aiindex import IAIndexClient; print('Success!')"
```

---

## Step 3: Test Installed Packages

### Test Node.js SDK

```bash
mkdir /tmp/test-iaindex && cd /tmp/test-iaindex
npm init -y
npm install @iaindex/sdk

node -e "const { IAIndexClient } = require('@iaindex/sdk'); console.log('SDK loaded successfully!');"
```

### Test CLI

```bash
npm install -g @iaindex/cli
iaindex --version
iaindex --help
```

### Test Python SDK

```bash
pip3 install aiindex-sdk
python3 -c "from aiindex import IAIndexClient, IAIndexPublisher; print('Python SDK working!')"
```

---

## Step 4: Verify Everything Works

### Check Package Pages

**npm**:
- Node.js SDK: https://www.npmjs.com/package/@iaindex/sdk
- CLI: https://www.npmjs.com/package/@iaindex/cli

**PyPI**:
- Python SDK: https://pypi.org/project/aiindex-sdk/

### Test with Live API

```bash
# Test Node.js SDK
node << 'EOF'
const { IAIndexClient } = require('@iaindex/sdk');
const client = new IAIndexClient({
  clientId: 'test-client',
  privateKey: 'test-key',
  apiUrl: 'https://api.iaindex.org'
});
console.log('✅ Node.js SDK configured with custom domain');
EOF
```

```bash
# Test Python SDK
python3 << 'EOF'
from aiindex import IAIndexClient
client = IAIndexClient(
    client_id='test-client',
    private_key='test-key',
    api_base_url='https://api.iaindex.org'
)
print('✅ Python SDK configured with custom domain')
EOF
```

```bash
# Test CLI
iaindex --version
```

---

## Quick Command Summary

```bash
# Step 1: npm
npm login
cd /Users/dineshanchetty/Documents/claimtec/iaindex/releases/v1.0.0
npm publish iaindex-sdk-1.0.0.tgz --access public
npm publish iaindex-cli-1.0.0.tgz --access public

# Step 2: PyPI
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python
python3 -m twine upload dist/* --username __token__ --password YOUR_PYPI_TOKEN

# Step 3: Verify
npm view @iaindex/sdk
npm view @iaindex/cli
pip3 install aiindex-sdk --force-reinstall
```

---

## Troubleshooting

### npm: "You do not have permission to publish"

**Solution**: The `@iaindex` scope might already exist. Either:

1. **Request access** to @iaindex organization on npm
2. **Use your own scope**:
   ```bash
   npm publish iaindex-sdk-1.0.0.tgz --access public --scope @yourname
   ```

### PyPI: "Project name already taken"

**Solution**: Add a prefix:
```bash
# Edit setup.py first
name="yourname-aiindex-sdk"
```

### "Package already published"

**Solution**: This version is already live! Use:
```bash
npm view @iaindex/sdk
pip3 show aiindex-sdk
```

---

## After Publication

### 1. Update Documentation

Add installation badges to README.md:

```markdown
[![npm](https://img.shields.io/npm/v/@iaindex/sdk)](https://www.npmjs.com/package/@iaindex/sdk)
[![PyPI](https://img.shields.io/pypi/v/aiindex-sdk)](https://pypi.org/project/aiindex-sdk/)
```

### 2. Announce Launch

Share on:
- Twitter/X
- LinkedIn
- Reddit (r/programming, r/MachineLearning)
- Hacker News
- Your blog

### 3. Monitor

```bash
# Check download stats
npm info @iaindex/sdk
# Visit: https://pypistats.org/packages/aiindex-sdk
```

---

## WordPress Plugin Distribution

**Option 1: WordPress.org** (Recommended but takes time)
- Submit to https://wordpress.org/plugins/developers/add/
- Review takes 7-14 days
- Will be listed in WordPress plugin directory

**Option 2: GitHub Release**
- Create release on GitHub
- Attach `iaindex-wordpress-plugin-v1.0.0.zip`
- Users download from GitHub

**Option 3: Direct Download**
- Host ZIP on your website
- Add download link to documentation

---

## Success! 🎉

Once published, users can install with:

```bash
# Node.js
npm install @iaindex/sdk

# Python
pip install aiindex-sdk

# CLI
npm install -g @iaindex/cli
```

And use your professional API at: **https://api.iaindex.org**

---

**Files Ready**:
- ✅ All packages in `/releases/v1.0.0/`
- ✅ Custom domain configured
- ✅ API production ready
- ✅ Documentation complete

**Now**: Run the commands above to publish! 🚀
