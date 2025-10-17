# AIIndex v1.0.0 Deployment Guide

**Version**: 1.0.0
**Last Updated**: October 17, 2025
**Status**: Production Ready

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [NPM Package Publishing](#npm-package-publishing)
3. [PyPI Package Publishing](#pypi-package-publishing)
4. [WordPress Plugin Distribution](#wordpress-plugin-distribution)
5. [Verification Steps](#verification-steps)
6. [Rollback Procedures](#rollback-procedures)
7. [Post-Deployment Tasks](#post-deployment-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before publishing any packages, ensure all items are completed:

### General Requirements
- [ ] All tests passing (unit, integration, E2E)
- [ ] Documentation reviewed and updated
- [ ] Changelog updated with v1.0.0 release notes
- [ ] Version numbers consistent across all packages
- [ ] License files included in all packages
- [ ] Security audit completed
- [ ] Dependencies reviewed and updated
- [ ] API endpoints tested and functional
- [ ] SSL certificates valid

### Account Requirements
- [ ] NPM account with publish permissions
- [ ] PyPI account with maintainer access
- [ ] Two-factor authentication enabled on both accounts
- [ ] API tokens generated and securely stored
- [ ] Organization access verified (if publishing under org)

### Package-Specific
- [ ] Node.js SDK built and tested (`iaindex-sdk-1.0.0.tgz`)
- [ ] Python SDK distributions created (`.whl` and `.tar.gz`)
- [ ] CLI tool built and tested (`iaindex-cli-1.0.0.tgz`)
- [ ] WordPress plugin ZIP created and tested
- [ ] All checksums generated and verified
- [ ] MANIFEST.md reviewed and accurate

---

## NPM Package Publishing

### 1. Node.js SDK (`@iaindex/sdk`)

#### Prerequisites
```bash
# Ensure you're logged in to npm
npm whoami

# If not logged in:
npm login
```

#### Publishing Steps

**Step 1: Verify Package Contents**
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-nodejs

# Extract and inspect the tarball
tar -tzf iaindex-sdk-1.0.0.tgz

# Verify package.json
npm pkg get name version
# Expected: @iaindex/sdk, 1.0.0
```

**Step 2: Dry Run (Recommended)**
```bash
# Perform a dry run to see what would be published
npm publish iaindex-sdk-1.0.0.tgz --dry-run

# Review the output carefully:
# - Check file list
# - Verify package name and version
# - Ensure no sensitive files included
```

**Step 3: Publish Package**
```bash
# Publish to npm registry
npm publish iaindex-sdk-1.0.0.tgz --access public

# Expected output:
# + @iaindex/sdk@1.0.0
```

**Step 4: Verify Publication**
```bash
# Check package is live
npm view @iaindex/sdk

# Test installation
mkdir /tmp/test-sdk && cd /tmp/test-sdk
npm install @iaindex/sdk
node -e "const sdk = require('@iaindex/sdk'); console.log(sdk);"
```

**Step 5: Tag as Latest**
```bash
npm dist-tag add @iaindex/sdk@1.0.0 latest
```

---

### 2. CLI Tool (`@iaindex/cli`)

#### Publishing Steps

**Step 1: Verify Package**
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli

# Extract and inspect
tar -tzf iaindex-cli-1.0.0.tgz

# Verify package.json
npm pkg get name version bin
# Expected: @iaindex/cli, 1.0.0, {"iaindex": "bin/iaindex.js"}
```

**Step 2: Dry Run**
```bash
npm publish iaindex-cli-1.0.0.tgz --dry-run
```

**Step 3: Publish**
```bash
npm publish iaindex-cli-1.0.0.tgz --access public

# Expected output:
# + @iaindex/cli@1.0.0
```

**Step 4: Verify Global Installation**
```bash
# Test global installation
npm install -g @iaindex/cli

# Verify command works
iaindex --version
# Expected: 1.0.0

iaindex --help
# Should display help text

# Clean up test
npm uninstall -g @iaindex/cli
```

**Step 5: Tag as Latest**
```bash
npm dist-tag add @iaindex/cli@1.0.0 latest
```

---

### NPM Publishing - Best Practices

#### Security Considerations
- **Use npm tokens**: Generate access tokens at npmjs.com/settings/tokens
- **Enable 2FA**: Required for publishing packages
- **Review package contents**: Always run `npm publish --dry-run` first
- **Check for secrets**: Ensure no API keys, passwords, or sensitive data

#### Package Access
```bash
# For organization packages
npm publish --access public

# For scoped packages (default is restricted)
npm access public @iaindex/sdk
npm access public @iaindex/cli
```

#### Setting Package Metadata
```bash
# Add keywords for discoverability
npm pkg set keywords[]="aiindex"
npm pkg set keywords[]="ai"
npm pkg set keywords[]="attestation"
npm pkg set keywords[]="verification"

# Set homepage and repository
npm pkg set homepage="https://iaindex.com"
npm pkg set repository.type="git"
npm pkg set repository.url="https://github.com/iaindex/iaindex"
```

---

## PyPI Package Publishing

### Python SDK (`aiindex-sdk`)

#### Prerequisites
```bash
# Install publishing tools
pip install twine

# Verify installation
twine --version
```

#### Publishing Steps

**Step 1: Verify Package Contents**
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

# Inspect wheel
unzip -l dist/aiindex_sdk-1.0.0-py3-none-any.whl

# Inspect source distribution
tar -tzf dist/aiindex-sdk-1.0.0.tar.gz

# Verify package metadata
python3 setup.py --name --version
# Expected: aiindex-sdk, 1.0.0
```

**Step 2: Check Package**
```bash
# Run twine check to validate distributions
twine check dist/*

# Expected output:
# Checking dist/aiindex-sdk-1.0.0.tar.gz: PASSED
# Checking dist/aiindex_sdk-1.0.0-py3-none-any.whl: PASSED
```

**Step 3: Upload to TestPyPI (Recommended)**
```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Enter credentials when prompted
# Username: __token__
# Password: <your-testpypi-token>

# Or use .pypirc file (see below)
```

**Step 4: Test Installation from TestPyPI**
```bash
# Create test environment
python3 -m venv /tmp/test-pypi-env
source /tmp/test-pypi-env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ aiindex-sdk

# Test import
python3 -c "import aiindex; print(aiindex.__version__)"
# Expected: 1.0.0

# Test CLI
aiindex --version

# Clean up
deactivate
rm -rf /tmp/test-pypi-env
```

**Step 5: Upload to Production PyPI**
```bash
# Upload to production PyPI
twine upload dist/*

# Enter credentials when prompted
# Username: __token__
# Password: <your-pypi-token>

# Expected output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading aiindex_sdk-1.0.0-py3-none-any.whl
# Uploading aiindex-sdk-1.0.0.tar.gz
```

**Step 6: Verify Production Installation**
```bash
# Create test environment
python3 -m venv /tmp/test-prod-env
source /tmp/test-prod-env/bin/activate

# Install from PyPI
pip install aiindex-sdk

# Verify installation
python3 -c "import aiindex; print(aiindex.__version__)"
aiindex --version

# Run basic tests
python3 -c "from aiindex import IAIndexClient; print('Import successful')"

# Clean up
deactivate
rm -rf /tmp/test-prod-env
```

---

### PyPI Publishing - Configuration

#### Creating .pypirc File
```bash
# Create ~/.pypirc for automated authentication
cat > ~/.pypirc <<EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-production-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-test-token>
EOF

# Secure the file
chmod 600 ~/.pypirc
```

#### Generating API Tokens
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Set token name: "aiindex-sdk-deployment"
4. Scope: "Entire account" or specific project
5. Copy token (starts with `pypi-`)
6. Store securely (1Password, etc.)

#### Security Best Practices
- **Use API tokens**: Never use passwords for automated uploads
- **Scope tokens**: Limit to specific projects when possible
- **Rotate regularly**: Generate new tokens periodically
- **Enable 2FA**: Required for PyPI accounts
- **Check distributions**: Always run `twine check` before uploading

---

## WordPress Plugin Distribution

### Distribution Methods

#### 1. WordPress.org Plugin Repository (Recommended)

**Step 1: Create WordPress.org Account**
1. Register at https://wordpress.org/support/register.php
2. Verify email address
3. Complete profile

**Step 2: Submit Plugin**
1. Go to https://wordpress.org/plugins/developers/add/
2. Upload `iaindex-wordpress-plugin-v1.0.0.zip`
3. Fill out plugin information:
   - Plugin Name: AIIndex for WordPress
   - Short Description: Automatic AI content attestation and verification
   - Tags: ai, attestation, verification, content-authentication
4. Submit for review

**Step 3: Wait for Approval**
- Review typically takes 3-7 days
- Monitor email for approval/feedback
- Address any requested changes

**Step 4: Set Up SVN Repository**
```bash
# Check out SVN repository (after approval)
svn co https://plugins.svn.wordpress.org/iaindex-wordpress /tmp/iaindex-wp-svn
cd /tmp/iaindex-wp-svn

# Extract plugin files
unzip /Users/dineshanchetty/Documents/claimtec/iaindex/releases/v1.0.0/iaindex-wordpress-plugin-v1.0.0.zip

# Copy to trunk
cp -r wordpress-plugin/* trunk/

# Add assets (screenshots, banners, icons)
# Place in assets/ directory

# Commit to trunk
svn add trunk/*
svn ci -m "Initial release v1.0.0"

# Tag release
svn cp trunk tags/1.0.0
svn ci -m "Tagging version 1.0.0"
```

---

#### 2. Direct Download Distribution

**Step 1: Prepare Distribution Package**
```bash
# Verify ZIP integrity
unzip -t /Users/dineshanchetty/Documents/claimtec/iaindex/releases/v1.0.0/iaindex-wordpress-plugin-v1.0.0.zip

# Generate checksum
shasum -a 256 iaindex-wordpress-plugin-v1.0.0.zip
```

**Step 2: Upload to Distribution Server**
```bash
# Example: Upload to S3 or CDN
aws s3 cp iaindex-wordpress-plugin-v1.0.0.zip \
  s3://downloads.iaindex.com/wordpress/v1.0.0/ \
  --acl public-read

# Or upload to GitHub Releases
gh release create v1.0.0 \
  iaindex-wordpress-plugin-v1.0.0.zip \
  --title "AIIndex WordPress Plugin v1.0.0" \
  --notes "Initial release of AIIndex WordPress plugin"
```

**Step 3: Create Download Page**
- Add download link to website
- Include installation instructions
- Provide checksum for verification
- Link to documentation

---

#### 3. Premium Distribution (Optional)

For paid/premium versions:

**Using Easy Digital Downloads**:
1. Install EDD on WordPress site
2. Create product for AIIndex plugin
3. Upload ZIP as downloadable file
4. Set pricing and licensing
5. Configure automatic updates

**Using WooCommerce**:
1. Install WooCommerce
2. Create product
3. Add plugin ZIP as downloadable
4. Configure licensing system

---

### WordPress Plugin - Installation Instructions

Provide these instructions to users:

#### Method 1: WordPress Admin Upload
```
1. Log in to WordPress admin
2. Navigate to Plugins > Add New
3. Click "Upload Plugin"
4. Choose iaindex-wordpress-plugin-v1.0.0.zip
5. Click "Install Now"
6. Click "Activate Plugin"
7. Go to Settings > AIIndex to configure
```

#### Method 2: Manual FTP Upload
```bash
# Extract plugin
unzip iaindex-wordpress-plugin-v1.0.0.zip

# Upload via FTP to:
# /wp-content/plugins/wordpress-plugin/

# Set permissions
chmod -R 755 /wp-content/plugins/wordpress-plugin/

# Activate in WordPress admin
```

#### Method 3: WP-CLI
```bash
# Install via WP-CLI
wp plugin install iaindex-wordpress-plugin-v1.0.0.zip --activate

# Configure settings
wp option update iaindex_api_key "your-api-key"
wp option update iaindex_api_endpoint "https://api.iaindex.com"
```

---

## Verification Steps

### Post-Publication Verification

#### 1. NPM Packages

**Verify @iaindex/sdk**:
```bash
# Check package page
open https://www.npmjs.com/package/@iaindex/sdk

# Verify installation
npm view @iaindex/sdk

# Test installation
npm install @iaindex/sdk --dry-run

# Check unpacked size
npm view @iaindex/sdk dist.unpackedSize

# View tarball
npm view @iaindex/sdk dist.tarball
```

**Verify @iaindex/cli**:
```bash
# Check package page
open https://www.npmjs.com/package/@iaindex/cli

# Test global installation
npm install -g @iaindex/cli
iaindex --version
iaindex --help
npm uninstall -g @iaindex/cli
```

---

#### 2. PyPI Package

**Verify aiindex-sdk**:
```bash
# Check package page
open https://pypi.org/project/aiindex-sdk/

# View package details
pip show aiindex-sdk

# Test installation
pip install aiindex-sdk --dry-run

# Verify CLI
which aiindex
aiindex --version
```

---

#### 3. WordPress Plugin

**Verify Plugin**:
```bash
# Extract and inspect
unzip -l iaindex-wordpress-plugin-v1.0.0.zip

# Check main plugin file
unzip -p iaindex-wordpress-plugin-v1.0.0.zip wordpress-plugin/iaindex.php | head -30

# Verify plugin headers:
# - Plugin Name
# - Version: 1.0.0
# - Author
# - License
```

**Test Installation**:
1. Install on test WordPress site
2. Activate plugin
3. Check for errors in PHP error log
4. Verify settings page loads
5. Test AIIndex generation
6. Check webhook functionality
7. Verify dashboard displays correctly

---

### Integration Testing

#### End-to-End Test Scenarios

**Scenario 1: Node.js SDK Integration**
```javascript
// test-npm-package.js
const { IAIndexClient } = require('@iaindex/sdk');

async function test() {
  const client = new IAIndexClient({
    apiKey: 'test-key',
    apiEndpoint: 'https://api.iaindex.com'
  });

  const index = await client.generateIndex({
    content: 'Test content',
    metadata: { type: 'test' }
  });

  console.log('NPM package test: SUCCESS');
}

test().catch(console.error);
```

**Scenario 2: Python SDK Integration**
```python
# test-pypi-package.py
from aiindex import IAIndexClient

client = IAIndexClient(
    api_key='test-key',
    api_endpoint='https://api.iaindex.com'
)

index = client.generate_index(
    content='Test content',
    metadata={'type': 'test'}
)

print('PyPI package test: SUCCESS')
```

**Scenario 3: CLI Tool Test**
```bash
# test-cli.sh
#!/bin/bash

# Test CLI installation
iaindex --version

# Test authentication
iaindex auth configure --api-key test-key

# Test key generation
iaindex keys generate --type ed25519

# Test index generation
echo "Test content" | iaindex generate --output test.json

echo "CLI test: SUCCESS"
```

---

## Rollback Procedures

### NPM Package Rollback

#### Deprecate Package Version
```bash
# Deprecate specific version
npm deprecate @iaindex/sdk@1.0.0 "This version has been deprecated"

# Deprecate and redirect to newer version
npm deprecate @iaindex/sdk@1.0.0 "Please upgrade to @iaindex/sdk@1.0.1"
```

#### Unpublish Package (within 72 hours)
```bash
# DANGER: Only use within 72 hours of publication
npm unpublish @iaindex/sdk@1.0.0

# Note: After 72 hours, you can only deprecate, not unpublish
```

#### Update dist-tag
```bash
# Point 'latest' tag to previous version
npm dist-tag add @iaindex/sdk@0.9.0 latest

# Remove problematic version from 'latest'
npm dist-tag rm @iaindex/sdk@1.0.0 latest
```

---

### PyPI Package Rollback

#### Yank Release
```bash
# PyPI doesn't allow deleting releases
# Instead, yank the release (removes from default pip installs)

# Using web interface:
# 1. Go to https://pypi.org/project/aiindex-sdk/1.0.0/
# 2. Click "Options" > "Yank release"
# 3. Provide reason for yanking

# Note: Users can still install yanked versions explicitly:
# pip install aiindex-sdk==1.0.0
```

#### Upload Fixed Version
```bash
# Increment version and upload fix
# Edit setup.py: version='1.0.1'

cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

# Build new version
python3 setup.py sdist bdist_wheel

# Upload fixed version
twine upload dist/aiindex-sdk-1.0.1*
```

---

### WordPress Plugin Rollback

#### WordPress.org Repository
```bash
# Restore previous version from SVN
svn co https://plugins.svn.wordpress.org/iaindex-wordpress /tmp/iaindex-rollback
cd /tmp/iaindex-rollback

# Copy previous version to trunk
svn cp tags/0.9.0 trunk
svn ci -m "Rollback to version 0.9.0 due to critical bug"

# Users will automatically get the previous version via WordPress updates
```

#### Direct Distribution
```bash
# Replace download link with previous version
# Update website to point to older ZIP

# Notify users via email/announcement
# Provide manual downgrade instructions
```

---

## Post-Deployment Tasks

### 1. Update Documentation

**Update Package READMEs**:
- [ ] Update installation instructions with npm/pip install commands
- [ ] Add package badges (version, downloads, license)
- [ ] Update example code with latest API
- [ ] Add link to package registry pages

**Update Website**:
- [ ] Add v1.0.0 to downloads page
- [ ] Update getting started guide
- [ ] Refresh documentation with package links
- [ ] Add release announcement

---

### 2. Monitoring and Analytics

**Set Up Package Monitoring**:
```bash
# Monitor npm download stats
npm-stat @iaindex/sdk @iaindex/cli

# Check PyPI stats
# Visit: https://pypistats.org/packages/aiindex-sdk

# Set up alerts for:
# - Download spikes (potential security issue)
# - Error rate increases
# - Version adoption rates
```

---

### 3. Communication

**Announce Release**:
- [ ] Post to company blog
- [ ] Tweet from official account
- [ ] Post to relevant forums/communities
- [ ] Email existing users
- [ ] Update Product Hunt (if applicable)
- [ ] Submit to relevant newsletters

**Example Announcement**:
```
We're excited to announce AIIndex v1.0.0!

This release includes:
- Production-ready Node.js and Python SDKs
- Full-featured CLI tool
- WordPress plugin with admin dashboard
- Complete documentation and examples

Get started:
npm install @iaindex/sdk
pip install aiindex-sdk

Learn more: https://docs.iaindex.com
```

---

### 4. Support Preparation

**Prepare Support Team**:
- [ ] Document common issues and solutions
- [ ] Create FAQ for v1.0.0
- [ ] Set up issue tracking templates
- [ ] Prepare response templates
- [ ] Schedule on-call rotation

**Monitor Feedback Channels**:
- [ ] GitHub Issues
- [ ] npm package page comments
- [ ] PyPI project page
- [ ] WordPress.org support forum
- [ ] Social media mentions
- [ ] Email support queue

---

## Troubleshooting

### NPM Publishing Issues

#### Error: "You cannot publish over the previously published versions"
```bash
# Solution: Increment version number
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-nodejs
npm version patch  # or minor, or major
npm run build
npm pack
npm publish iaindex-sdk-1.0.1.tgz --access public
```

#### Error: "You must verify your email"
```bash
# Solution: Verify email with npm
npm adduser
# Follow email verification link
```

#### Error: "Package name too similar to existing package"
```bash
# Solution: Choose different package name
# Update package.json: "name": "@iaindex/sdk-v2"
```

---

### PyPI Publishing Issues

#### Error: "File already exists"
```bash
# Solution: PyPI doesn't allow re-uploading same version
# Increment version number
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

# Edit setup.py or pyproject.toml
# version='1.0.1'

# Rebuild and upload
python3 setup.py sdist bdist_wheel
twine upload dist/aiindex-sdk-1.0.1*
```

#### Error: "Invalid distribution"
```bash
# Solution: Fix package metadata
# Run twine check first
twine check dist/*

# Common issues:
# - Missing long_description
# - Invalid RST/Markdown formatting
# - Missing required metadata fields
```

---

### WordPress Plugin Issues

#### Issue: "Plugin failed to activate"
```bash
# Check PHP errors
tail -f /var/log/apache2/error.log
# or
tail -f /var/log/nginx/error.log

# Common causes:
# - PHP version incompatibility
# - Missing PHP extensions
# - Syntax errors
# - Conflicting plugins
```

#### Issue: "Plugin causes white screen"
```bash
# Enable WordPress debugging
# Add to wp-config.php:
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);

# Check debug.log
tail -f wp-content/debug.log

# Deactivate plugin via database if needed
mysql -u root -p wordpress_db
UPDATE wp_options SET option_value = '' WHERE option_name = 'active_plugins';
```

---

## Emergency Contacts

### Package Registry Support
- **NPM Support**: support@npmjs.com
- **PyPI Support**: admin@pypi.org
- **WordPress.org**: https://wordpress.org/support/forum/

### Internal Team
- **Release Manager**: [Name, Email]
- **DevOps Lead**: [Name, Email]
- **Security Team**: [Name, Email]
- **Support Lead**: [Name, Email]

---

## Deployment Timeline (Recommended)

### Day 1: Preparation
- 9:00 AM: Final testing of all packages
- 10:00 AM: Pre-deployment checklist review
- 11:00 AM: Team standup and go/no-go decision

### Day 1: Deployment
- 12:00 PM: Publish to TestPyPI (if not done)
- 12:30 PM: Publish to NPM (Node.js SDK)
- 1:00 PM: Publish to NPM (CLI)
- 1:30 PM: Publish to PyPI (production)
- 2:00 PM: Upload WordPress plugin
- 2:30 PM: Verification testing

### Day 1: Post-Deployment
- 3:00 PM: Update documentation
- 3:30 PM: Publish announcements
- 4:00 PM: Monitor for issues
- 5:00 PM: Team retrospective

### Day 2-7: Monitoring
- Daily: Check download stats
- Daily: Monitor error reports
- Daily: Review support tickets
- Daily: Check social media feedback

---

## Success Criteria

Deployment is considered successful when:

- [ ] All packages published and accessible
- [ ] Installation tested on clean systems
- [ ] No critical bugs reported within 24 hours
- [ ] Download counts increasing
- [ ] Documentation accessible and accurate
- [ ] Support team ready and trained
- [ ] Monitoring systems active
- [ ] Announcement published
- [ ] Positive community feedback

---

**Document Version**: 1.0.0
**Last Updated**: October 17, 2025
**Next Review**: January 17, 2026
