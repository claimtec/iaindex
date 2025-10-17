# 🚀 AIIndex Deployment Checklist

Complete pre-flight checklist before production deployment.

---

## 📋 Pre-Deployment Checklist

### 1. Environment Setup ✅

#### Supabase
- [ ] Create Supabase project
- [ ] Run database schema (`infra/supabase/schema.sql`)
- [ ] Enable Row Level Security (RLS)
- [ ] Configure auth providers
- [ ] Set up database backups
- [ ] Copy connection details

#### GitHub
- [ ] Repository created
- [ ] Branch protection rules (main/production)
- [ ] Required CI checks enabled
- [ ] Secrets configured (see below)

#### Secrets Configuration
```bash
# GitHub Secrets Required:
DOCKER_USERNAME=
DOCKER_PASSWORD=
FLY_API_TOKEN=
VERCEL_TOKEN=
VERCEL_ORG_ID=
VERCEL_PROJECT_ID=
NETLIFY_AUTH_TOKEN=
NETLIFY_SITE_ID=
NPM_TOKEN=
PYPI_API_TOKEN=
SUPABASE_URL=
SUPABASE_KEY=
SLACK_WEBHOOK= (optional)
```

---

### 2. API Deployment ✅

**Target**: Fly.io

- [ ] Create `.env` from `.env.example`
- [ ] Update `SECRET_KEY` (generate new)
- [ ] Set `DEBUG=False`
- [ ] Configure `CORS_ORIGINS`
- [ ] Set `SUPABASE_URL` and `SUPABASE_KEY`
- [ ] Test locally: `make dev`
- [ ] Build Docker image: `make docker-build`
- [ ] Deploy: `fly launch` then `fly deploy`
- [ ] Run health check: `curl https://api.aiindex.org/health`
- [ ] Test endpoints: `curl https://api.aiindex.org/v1/verified-domains`

**Commands**:
```bash
cd apps/api
cp .env.example .env
# Edit .env
make docker-build
fly launch --name aiindex-api
fly deploy
fly logs
```

**Verify**:
- [ ] Health endpoint responds
- [ ] API docs accessible at `/docs`
- [ ] Database connection works
- [ ] Rate limiting active
- [ ] CORS configured correctly

---

### 3. Web Dashboard Deployment ✅

**Target**: Vercel

- [ ] Create `.env.local` from `.env.example`
- [ ] Set `NEXT_PUBLIC_SUPABASE_URL`
- [ ] Set `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- [ ] Set `NEXT_PUBLIC_API_URL`
- [ ] Test build: `npm run build`
- [ ] Test locally: `npm run start`
- [ ] Deploy: `vercel deploy --prod`
- [ ] Test authentication flow
- [ ] Verify analytics charts load

**Commands**:
```bash
cd apps/web
cp .env.example .env.local
# Edit .env.local
npm run build
vercel deploy --prod
```

**Verify**:
- [ ] Login works
- [ ] Dashboard loads
- [ ] Charts display data
- [ ] Receipt explorer functional
- [ ] Settings page works
- [ ] Badge generator functional
- [ ] Dark mode works

---

### 4. Documentation Deployment ✅

**Target**: Netlify

- [ ] Test build: `npm run build`
- [ ] Check for broken links
- [ ] Verify all images load
- [ ] Test search functionality
- [ ] Deploy: `netlify deploy --prod`

**Commands**:
```bash
cd apps/docs
npm run build
netlify deploy --prod --dir=build
```

**Verify**:
- [ ] All pages load
- [ ] Navigation works
- [ ] Code examples render
- [ ] Search functional
- [ ] Dark mode works
- [ ] Mobile responsive

---

### 5. Infrastructure Deployment ✅

**Target**: AWS + Cloudflare + Vercel

- [ ] Configure `terraform.tfvars`
- [ ] Review plan: `terraform plan`
- [ ] Apply: `terraform apply`
- [ ] Verify S3 bucket created
- [ ] Verify CloudFront distribution
- [ ] Verify DNS records
- [ ] Test CDN: `curl https://cdn.aiindex.org/test`

**Commands**:
```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

**Verify**:
- [ ] S3 bucket accessible
- [ ] CloudFront serving content
- [ ] DNS resolves correctly
- [ ] SSL certificates valid
- [ ] Secrets in AWS Secrets Manager
- [ ] CloudWatch logs working

---

### 6. Merkle Attestation System ✅

**Target**: Docker on Fly.io or AWS ECS

- [ ] Build Docker image
- [ ] Configure environment variables
- [ ] Set up cron schedule (daily at 00:00 UTC)
- [ ] Test locally: `python cron.py --mode once`
- [ ] Deploy container
- [ ] Verify first attestation generated

**Commands**:
```bash
cd infra/merkle
docker build -t aiindex-merkle .
docker run -e SUPABASE_URL=... aiindex-merkle python cron.py --mode once
# Deploy to Fly.io or ECS
```

**Verify**:
- [ ] Cron job runs daily
- [ ] Merkle trees generated
- [ ] Attestations published to S3
- [ ] Logs in CloudWatch
- [ ] No errors in output

---

### 7. SDK Publishing ✅

#### Node.js SDK

- [ ] Update version in `package.json`
- [ ] Run tests: `npm test`
- [ ] Build: `npm run build`
- [ ] Test package: `npm pack`
- [ ] Login to NPM: `npm login`
- [ ] Publish: `npm publish --access public`
- [ ] Verify on npmjs.com

**Commands**:
```bash
cd packages/sdk-node
npm version patch # or minor/major
npm test
npm run build
npm publish --access public
```

#### Python SDK

- [ ] Update version in `setup.py` and `pyproject.toml`
- [ ] Run tests: `pytest`
- [ ] Build: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Upload: `twine upload dist/*`
- [ ] Verify on pypi.org

**Commands**:
```bash
cd packages/sdk-python
# Update version
pytest
python -m build
twine check dist/*
twine upload dist/*
```

---

### 8. Plugin Deployment ✅

#### WordPress
- [ ] Zip plugin: `cd packages/wp-plugin && zip -r aiindex.zip .`
- [ ] Test on local WordPress
- [ ] Submit to WordPress.org Plugin Directory
- [ ] Or host on GitHub releases

#### Webflow
- [ ] Host `snippet.js` on CDN (e.g., jsDelivr)
- [ ] Update documentation with CDN URL
- [ ] Test on live Webflow site

#### Bubble.io
- [ ] Package plugin files
- [ ] Submit to Bubble Plugin Store
- [ ] Or provide import instructions

#### Shopify
- [ ] Submit to Shopify App Store
- [ ] Or provide OAuth installation link

#### Others (Wix, Squarespace, Framer, Ghost)
- [ ] Host on GitHub releases
- [ ] Provide installation documentation
- [ ] Create demo videos

---

### 9. Database Seeding (Optional) ✅

**For Testing/Demo**:

- [ ] Run seed script: `psql < examples/seed/seed-database.sql`
- [ ] Generate test receipts: `python examples/seed/generate-test-receipts.py`
- [ ] Verify data in dashboard
- [ ] Test analytics display

**Commands**:
```bash
psql $DATABASE_URL < examples/seed/seed-database.sql
python examples/seed/generate-test-receipts.py --count 100
```

---

### 10. Monitoring & Alerts ✅

- [ ] CloudWatch logs configured
- [ ] SNS alerts set up
- [ ] Slack webhook configured (optional)
- [ ] Set up uptime monitoring (e.g., UptimeRobot)
- [ ] Configure error tracking (e.g., Sentry)

**Services to monitor**:
- [ ] API health (`/health`)
- [ ] Web dashboard
- [ ] Documentation site
- [ ] Merkle cron job
- [ ] Database connections

---

### 11. Security Hardening ✅

- [ ] Change all default credentials
- [ ] Rotate `SECRET_KEY`
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up DDoS protection (Cloudflare)
- [ ] Review RLS policies
- [ ] Enable database encryption
- [ ] Set up WAF rules
- [ ] Configure security headers

---

### 12. Performance Optimization ✅

- [ ] Enable CDN caching
- [ ] Configure Redis caching
- [ ] Optimize database indexes
- [ ] Enable gzip compression
- [ ] Minify static assets
- [ ] Enable HTTP/2
- [ ] Set up connection pooling
- [ ] Configure auto-scaling

---

### 13. Documentation Updates ✅

- [ ] Update all URLs in docs
- [ ] Replace `localhost` with production URLs
- [ ] Update API base URLs
- [ ] Add production examples
- [ ] Update README files
- [ ] Create getting started guide
- [ ] Record demo videos
- [ ] Create troubleshooting guide

---

### 14. Testing ✅

#### End-to-End Testing

**Publisher Flow**:
- [ ] Sign up on dashboard
- [ ] Verify domain via DNS
- [ ] Generate API key
- [ ] Install plugin (WordPress/Shopify)
- [ ] Generate ai-index.json
- [ ] Submit test receipt
- [ ] View receipt in dashboard
- [ ] Check analytics

**Developer Flow**:
- [ ] Install SDK (Node.js or Python)
- [ ] Fetch ai-index.json
- [ ] Generate receipt
- [ ] Send receipt to API
- [ ] Verify receipt stored

**API Testing**:
```bash
# Test all endpoints
curl https://api.aiindex.org/health
curl https://api.aiindex.org/v1/verified-domains
curl -X POST https://api.aiindex.org/v1/auth/login
curl -X POST https://api.aiindex.org/v1/receipts/ingest
curl https://api.aiindex.org/v1/analytics?domain=example.com
curl https://api.aiindex.org/v1/attestations/2025-10-13
```

---

### 15. Launch Preparation ✅

- [ ] Create marketing website
- [ ] Prepare launch blog post
- [ ] Set up social media accounts
- [ ] Create demo video
- [ ] Prepare press kit
- [ ] List on Product Hunt
- [ ] Post on Hacker News
- [ ] Announce on Twitter/LinkedIn
- [ ] Create launch email

---

## 🎯 Post-Deployment Checklist

### Day 1
- [ ] Monitor error logs
- [ ] Check API response times
- [ ] Verify all services running
- [ ] Monitor database performance
- [ ] Check CDN cache hit rate
- [ ] Review security logs

### Week 1
- [ ] Analyze usage patterns
- [ ] Review cost usage
- [ ] Optimize slow queries
- [ ] Address user feedback
- [ ] Fix critical bugs
- [ ] Update documentation

### Month 1
- [ ] Review analytics
- [ ] Optimize infrastructure
- [ ] Scale services if needed
- [ ] Plan feature updates
- [ ] Security audit
- [ ] Performance review

---

## 🚨 Rollback Plan

If deployment fails:

1. **API**: `fly rollback`
2. **Web**: Vercel → Deployments → Promote previous
3. **Docs**: Netlify → Deploys → Restore
4. **Infrastructure**: `terraform apply` with previous state
5. **Database**: Restore from Supabase backup

---

## 📊 Success Metrics

Track these KPIs:

- [ ] API uptime > 99.9%
- [ ] Response time < 200ms (p95)
- [ ] Error rate < 0.1%
- [ ] Publisher sign-ups
- [ ] Receipts processed
- [ ] SDK downloads
- [ ] Documentation page views
- [ ] Support tickets < 5/day

---

## 🔧 Maintenance Schedule

**Daily**:
- Check error logs
- Monitor uptime
- Review alerts

**Weekly**:
- Database optimization
- Security updates
- Performance review

**Monthly**:
- Cost analysis
- Feature planning
- Security audit
- Backup testing

---

## 📞 Emergency Contacts

- **API Issues**: api-team@aiindex.org
- **Database Issues**: db-team@aiindex.org
- **Security Issues**: security@aiindex.org
- **General Support**: support@aiindex.org

---

## ✅ Final Sign-Off

Before going live, confirm:

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Team notified
- [ ] Monitoring active
- [ ] Rollback plan ready
- [ ] Support team ready

**Deployment Approved By**: _________________

**Date**: _________________

---

**Ready to launch! 🚀**

Review this checklist one more time, then execute the deployment. Good luck!
