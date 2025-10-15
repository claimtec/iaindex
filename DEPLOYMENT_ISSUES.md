# AIIndex v1.1 - Deployment Issues & Fixes

**Generated**: 2025-10-14
**Status**: 🔧 Issues Identified, Fixes in Progress

---

## Summary

The initial deployment test run identified several blockers that need to be resolved before successful deployment:

### 🔴 Critical Issues (Block Deployment)

1. **Next.js Build Failure** - Dashboard build failing
2. **Python Dependency Conflicts** - API requirements incompatible

### 🟡 Warnings (Non-Blocking)

3. **PostgreSQL CLI Missing** - psql not installed
4. **Git Repository Not Initialized** - Not a git repo
5. **pytest Not on PATH** - Testing tools need PATH update

---

## Issue Details & Fixes

### 1. Next.js Build Failure (Critical)

**Error**:
```
./lib/supabase/server.ts
Error: You're importing a component that needs next/headers.
That only works in a Server Component which is not supported in the pages/ directory.
```

**Root Cause**:
- Using `next/headers` (App Router) in a project configured for Pages Router
- The `apps/web` dashboard is using Next.js 14 with App Router structure but may have Pages Router config

**Impact**: Dashboard cannot build, blocking deployment

**Fix Options**:

**Option A: Update Next.js Config (Recommended)**
```javascript
// apps/web/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true, // Enable App Router
  },
}
module.exports = nextConfig
```

**Option B: Create Client-Side Wrapper**
```typescript
// apps/web/lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

Then update `apps/web/lib/api.ts` to use client-side calls with proper server action wrappers.

**Status**: ✅ Fix prepared (see below)

---

### 2. Python Dependency Conflicts (Critical)

**Error**:
```
ERROR: Cannot install -r requirements.txt (line 3) and httpx==0.26.0
because these package versions have conflicting dependencies.

Conflicts:
- supabase 2.18.1 requires httpx<0.29,>=0.26, but you have httpx 0.25.2
- pyjwt<3.0.0,>=2.10.1 required, but you have pyjwt 2.8.0
- numpy<2.3.0,>=2 required, but you have numpy 1.26.2
```

**Root Cause**:
- System-wide Python packages conflict with project requirements
- Old httpx version (0.25.2) incompatible with Supabase Python SDK
- Old pyjwt version (2.8.0) incompatible with supabase-auth

**Impact**: API dependencies cannot install, blocking deployment

**Fix**: Update `apps/api/requirements.txt` with compatible versions

```txt
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
python-dotenv>=1.0.0
httpx>=0.27.0  # Changed from 0.26.0
pydantic>=2.7.0
pydantic-settings>=2.0.0
supabase>=2.18.1
pyjwt>=2.10.1  # Added explicit version
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
redis>=5.0.0
cryptography>=42.0.0
ecdsa>=0.18.0
numpy>=2.0.0,<2.3.0  # Added explicit constraint
```

**Alternative**: Use virtual environment to isolate dependencies
```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Status**: ✅ Fix prepared (see below)

---

### 3. PostgreSQL CLI Missing (Warning)

**Warning**:
```
psql is not installed (required for database migration)
```

**Root Cause**: PostgreSQL client tools not installed on system

**Impact**: Cannot run database migration from command line

**Fix**:
```bash
# macOS
brew install postgresql

# Or use Supabase CLI
brew install supabase/tap/supabase
supabase db push
```

**Workaround**: Run migration directly in Supabase dashboard SQL editor

**Status**: ⚠️ Non-blocking (can use Supabase dashboard)

---

### 4. Git Repository Not Initialized (Warning)

**Warning**:
```
fatal: not a git repository (or any of the parent directories): .git
```

**Root Cause**: Project directory is not a git repository

**Impact**: Cannot track changes or use git-based deployment

**Fix**:
```bash
git init
git add .
git commit -m "Initial commit: AIIndex v1.1"
git remote add origin https://github.com/yourusername/iaindex.git
git push -u origin main
```

**Status**: ⚠️ Non-blocking (but recommended for version control)

---

### 5. pytest Not on PATH (Warning)

**Warning**:
```
WARNING: The scripts py.test and pytest are installed in
'/Users/dineshanchetty/Library/Python/3.9/bin' which is not on PATH.
```

**Root Cause**: Python user bin directory not in system PATH

**Impact**: Cannot run tests from command line easily

**Fix**:
```bash
# Add to ~/.zshrc or ~/.bash_profile
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Then reload
source ~/.zshrc
```

**Alternative**: Use python -m pytest
```bash
python3 -m pytest tests/e2e/
```

**Status**: ⚠️ Non-blocking (tests can still run with python -m)

---

## Recommended Action Plan

### Immediate (Before Next Deployment Attempt)

1. ✅ **Fix Next.js Config** - Update `next.config.js` to enable App Router
2. ✅ **Fix Python Dependencies** - Update `requirements.txt` with compatible versions
3. ✅ **Create Virtual Environment** - Isolate Python dependencies

### Short-Term (This Week)

4. ⚠️ **Install PostgreSQL CLI** - For local migration testing
5. ⚠️ **Initialize Git Repository** - For version control
6. ⚠️ **Fix PATH** - Add Python user bin to PATH

### Long-Term (Post-Deployment)

7. 📋 **Set Up CI/CD** - Automate testing and deployment
8. 📋 **Dependency Pinning** - Lock all dependency versions
9. 📋 **Docker Containers** - Eliminate environment issues

---

## Deployment Status

### Current State
- ❌ **Cannot deploy** - Critical issues blocking
- 🔧 **Fixes prepared** - Ready to apply
- ⏱️ **ETA to fix**: 15-30 minutes

### Next Steps
1. Apply fixes (see below)
2. Re-run deployment script
3. Verify builds succeed
4. Continue with staging deployment

---

## Fixes to Apply

See [DEPLOYMENT_FIXES.md](./DEPLOYMENT_FIXES.md) for detailed fix implementation.

---

**Last Updated**: 2025-10-14 15:35:00
