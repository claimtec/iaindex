# Quick PyPI Publication - Step by Step

## Fastest Method: API Token

### Step 1: Get Your PyPI API Token

1. **Log in to PyPI**: https://pypi.org/account/login/

2. **Go to Account Settings**: https://pypi.org/manage/account/

3. **Scroll to "API tokens"** section

4. **Click "Add API token"**
   - Token name: `aiindex-sdk-publish`
   - Scope: **"Entire account"** (for first time)
   - Click **"Add token"**

5. **Copy the token immediately** - it starts with `pypi-` and is shown only once!

### Step 2: Publish to PyPI

Open your terminal and run:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/sdk-python

# Paste your token after --password
python3 -m twine upload dist/* --username __token__ --password pypi-PASTE_YOUR_TOKEN_HERE
```

**Example**:
```bash
python3 -m twine upload dist/* --username __token__ --password pypi-AgEIcHlwaS5vcmcCJGZjMGY4NTc...
```

### Step 3: Verify Publication

```bash
# Check it's live
pip3 search aiindex-sdk  # (if search is enabled)

# Install and test
pip3 install aiindex-sdk
python3 -c "from aiindex import IAIndexClient; print('✅ Published successfully!')"
```

---

## Expected Output

When successful, you'll see:

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading aiindex_sdk-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 31.2/31.2 kB • 00:00
Uploading aiindex-sdk-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 30.5/30.5 kB • 00:00

View at:
https://pypi.org/project/aiindex-sdk/1.0.0/
```

---

## Troubleshooting

### "Package already exists"
Good news! It's already published. Visit: https://pypi.org/project/aiindex-sdk/

### "Invalid authentication"
- Make sure you copied the entire token (starts with `pypi-`)
- Token includes letters, numbers, and hyphens
- Use `__token__` (with underscores) as username

### "Permission denied"
- Use "Entire account" scope when creating the token
- Or create the project first, then use project-specific token

---

## Alternative: Save Token to .pypirc

To avoid typing the token each time:

```bash
# Create/edit ~/.pypirc
nano ~/.pypirc
```

Add this content:
```ini
[pypi]
username = __token__
password = pypi-YOUR_FULL_TOKEN_HERE
```

Save and close (Ctrl+X, Y, Enter)

Then simply run:
```bash
python3 -m twine upload dist/*
```

---

## After Publishing

**Package will be live at**: https://pypi.org/project/aiindex-sdk/

**Installation command**:
```bash
pip install aiindex-sdk
```

**Check download stats** (after a few hours):
https://pypistats.org/packages/aiindex-sdk

---

## All Three Packages Now Available!

Once PyPI is done:

| Platform | Package | Installation |
|----------|---------|--------------|
| **npm** | iaindex-sdk | `npm install iaindex-sdk` |
| **npm** | iaindex-cli | `npm install -g iaindex-cli` |
| **PyPI** | aiindex-sdk | `pip install aiindex-sdk` |

All using the same API: **https://api.iaindex.org** ✅

---

**Ready?** Just need your PyPI token to complete! 🚀
