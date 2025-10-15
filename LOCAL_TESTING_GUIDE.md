# AIIndex v1.1 - Local Testing Guide

**Status**: Database is ready ✅
**Next**: Test locally before cloud deployment

---

## 🎯 Why Test Locally First?

The deployment script prepared everything, but deploying to Fly.io/Vercel/Netlify requires:
1. Account setup on each platform
2. CLI authentication
3. Domain configuration

**Easier approach**: Test everything locally first, then deploy to cloud platforms.

---

## ✅ What's Already Working

- ✅ Database schema created (11 tables)
- ✅ Supabase credentials configured
- ✅ Dashboard builds successfully
- ✅ API dependencies ready
- ✅ All code complete

---

## 🚀 Local Testing (15 minutes)

### Step 1: Start API Locally (5 minutes)

```bash
# Terminal 1
cd apps/api

# Activate virtual environment (if you created one)
source venv/bin/activate

# Or install dependencies globally
pip3 install -r requirements.txt

# Copy staging env to local
cp .env.staging .env

# Start API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test it** (in another terminal):
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

curl http://localhost:8000/
# Should return API info
```

---

### Step 2: Start Dashboard Locally (5 minutes)

```bash
# Terminal 2
cd apps/web

# Update .env.local to point to local API
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local

# Start dashboard
npm run dev
```

**Expected output**:
```
▲ Next.js 14.2.33
- Local:        http://localhost:3000
✓ Ready in 2s
```

**Test it**:
- Open: http://localhost:3000
- Should see AIIndex dashboard
- Try logging in (uses Supabase auth)
- Check dashboard pages

---

### Step 3: Test Key Features (5 minutes)

#### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Version info
curl http://localhost:8000/ | jq

# OpenAPI docs
open http://localhost:8000/docs
```

#### Test Dashboard Pages
Open in browser:
- http://localhost:3000 - Home
- http://localhost:3000/login - Login
- http://localhost:3000/dashboard - Dashboard (requires auth)
- http://localhost:3000/dashboard/policy - Policy config (NEW v1.1)
- http://localhost:3000/dashboard/compliance - Compliance (NEW v1.1)
- http://localhost:3000/dashboard/provenance - Provenance (NEW v1.1)

---

## ✅ Local Smoke Tests

Once both API and Dashboard are running, create a simple test:

```bash
#!/bin/bash
# local-smoke-test.sh

echo "Testing AIIndex Locally..."

# Test API
echo -n "API Health: "
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✓ PASS" || echo "✗ FAIL"

echo -n "API Root: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200" && echo "✓ PASS" || echo "✗ FAIL"

echo -n "API Docs: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200" && echo "✓ PASS" || echo "✗ FAIL"

# Test Dashboard
echo -n "Dashboard Home: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200" && echo "✓ PASS" || echo "✗ FAIL"

echo -n "Dashboard Login: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/login | grep -q "200" && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "Local testing complete!"
```

Make executable and run:
```bash
chmod +x local-smoke-test.sh
./local-smoke-test.sh
```

---

## 🎯 Expected Results

### API Should:
- ✅ Start without errors
- ✅ Respond to health check
- ✅ Show OpenAPI docs at /docs
- ✅ Connect to Supabase database
- ✅ Return version info

### Dashboard Should:
- ✅ Build and start without errors
- ✅ Load home page
- ✅ Show login page
- ✅ Connect to Supabase auth
- ✅ Load all 13 routes
- ✅ Display v1.1 pages (policy, compliance, provenance)

---

## 🐛 Troubleshooting

### API Issues

**"ModuleNotFoundError: No module named..."**
```bash
cd apps/api
pip3 install -r requirements.txt
```

**"Connection to database failed"**
- Check DATABASE_URL in .env has correct password
- Test connection: `psql "$DATABASE_URL" -c "SELECT 1;"`

**"Port 8000 already in use"**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Dashboard Issues

**"Module not found"**
```bash
cd apps/web
npm install
```

**"NEXT_PUBLIC_SUPABASE_URL not defined"**
- Check .env.local has Supabase credentials
- Make sure file is in apps/web/.env.local

**"Port 3000 already in use"**
```bash
# Use different port
npm run dev -- -p 3001
```

---

## 📊 Testing Checklist

- [ ] API starts without errors
- [ ] API health endpoint returns healthy
- [ ] API docs page loads (http://localhost:8000/docs)
- [ ] Dashboard starts without errors
- [ ] Dashboard home page loads
- [ ] Dashboard login page loads
- [ ] Can navigate to /dashboard/policy
- [ ] Can navigate to /dashboard/compliance
- [ ] Can navigate to /dashboard/provenance
- [ ] Supabase authentication works

---

## 🚀 After Local Testing Passes

Once everything works locally, you can deploy to cloud platforms:

### Option 1: Deploy to Fly.io (API)
```bash
# Install Fly CLI
brew install flyctl

# Login
flyctl auth login

# Deploy
cd apps/api
fly launch --name aiindex-api-staging
fly deploy
```

### Option 2: Deploy to Vercel (Dashboard)
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd apps/web
vercel --env-file .env.staging
```

### Option 3: Deploy to Netlify (Docs)
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Login
netlify login

# Deploy
cd apps/docs
netlify deploy --prod
```

---

## 💡 Alternative: Use Docker

If you prefer Docker:

```bash
# Build and run API
cd apps/api
docker build -t aiindex-api .
docker run -p 8000:8000 --env-file .env aiindex-api

# Build and run Dashboard
cd apps/web
docker build -t aiindex-web .
docker run -p 3000:3000 aiindex-web
```

---

## 📚 Next Steps

1. **Now**: Test locally with instructions above
2. **If local works**: Deploy to cloud platforms
3. **If local fails**: Debug and fix issues
4. **After cloud deploy**: Run smoke tests against production URLs

---

**Quick Start**:
```bash
# Terminal 1 - API
cd apps/api && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Dashboard
cd apps/web && npm run dev

# Terminal 3 - Test
curl http://localhost:8000/health
open http://localhost:3000
```

---

**Last Updated**: 2025-10-14 21:35:00
