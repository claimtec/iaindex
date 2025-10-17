# Publish to PyPI - Instructions

The Node.js packages are live on npm! Now we just need to publish the Python SDK to PyPI.

## ✅ Already Published to npm

- **iaindex-sdk**: https://www.npmjs.com/package/iaindex-sdk
- **iaindex-cli**: https://www.npmjs.com/package/iaindex-cli

## 📦 Publish Python SDK to PyPI

### Option 1: Using PyPI API Token (Recommended)

1. **Get your PyPI API token**:
   - Go to https://pypi.org/account/login/
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Scope: "Entire account" (or specific to aiindex-sdk project later)
   - Copy the token (starts with `pypi-`)

2. **Publish with token**:
   ```bash
   cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

   python3 -m twine upload dist/* \
     --username __token__ \
     --password pypi-PASTE_YOUR_TOKEN_HERE
   ```

### Option 2: Using Username/Password

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

# This will prompt for username and password
python3 -m twine upload dist/*
```

When prompted:
- **Username**: Your PyPI username
- **Password**: Your PyPI password

### Option 3: Configure ~/.pypirc (For future ease)

Create/edit `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

Then simply run:
```bash
python3 -m twine upload dist/*
```

---

## Verification

After publishing, verify it's live:

```bash
# Check on PyPI
open https://pypi.org/project/aiindex-sdk/

# Test installation
pip3 install aiindex-sdk
python3 -c "from aiindex import IAIndexClient; print('Success!')"
```

---

## Package Names

| Platform | Package Name | Status | URL |
|----------|--------------|--------|-----|
| **npm** | `iaindex-sdk` | ✅ Published | https://www.npmjs.com/package/iaindex-sdk |
| **npm** | `iaindex-cli` | ✅ Published | https://www.npmjs.com/package/iaindex-cli |
| **PyPI** | `aiindex-sdk` | ⏳ Pending | Will be at https://pypi.org/project/aiindex-sdk/ |

---

## Test Commands (After PyPI publish)

```bash
# Node.js SDK
npm install iaindex-sdk
node -e "const {IAIndexClient} = require('iaindex-sdk'); console.log('✅ Works!');"

# CLI
npm install -g iaindex-cli
iaindex --version

# Python SDK
pip3 install aiindex-sdk
python3 -c "from aiindex import IAIndexClient; print('✅ Works!');"
```

---

## Next: After Publishing to PyPI

1. Update README.md with installation badges
2. Announce on social media
3. Monitor download stats
4. Respond to issues/questions

Congratulations on the npm publications! 🎉
