# IA Index Infrastructure

Complete infrastructure setup for the IA Index project, including Merkle attestation system, CI/CD pipelines, containerization, and infrastructure as code.

## Directory Structure

```
infra/
├── merkle/              # Merkle attestation system
│   ├── build_tree.py    # Build daily Merkle trees
│   ├── generate_proof.py # Generate inclusion proofs
│   ├── verify_proof.py  # Verify proof validity
│   ├── publish.py       # Publish to cloud storage
│   ├── cron.py          # Scheduled task runner
│   ├── requirements.txt # Python dependencies
│   ├── Dockerfile       # Container configuration
│   └── README.md        # Detailed documentation
└── terraform/           # Infrastructure as code
    ├── main.tf          # Main configuration
    ├── variables.tf     # Variable definitions
    ├── outputs.tf       # Output definitions
    ├── terraform.tfvars.example
    └── README.md        # Terraform documentation
```

## Components

### 1. Merkle Attestation System

A cryptographic system that builds daily Merkle trees from verified receipts.

**Features:**
- Daily automated tree building
- Inclusion proof generation
- Cryptographic verification
- Cloud storage publishing (S3/R2)
- Scheduled execution

**Quick Start:**
```bash
cd infra/merkle
pip install -r requirements.txt

# Build tree for today
python build_tree.py --output-dir ../../attestations

# Generate proof
python generate_proof.py --receipt-id <id> --output-dir ./proofs

# Verify proof
python verify_proof.py --proof ./proofs/proof_<id>.json
```

[Full Documentation](./merkle/README.md)

### 2. CI/CD Pipeline

GitHub Actions workflows for automated testing, building, and deployment.

**Workflows:**

- **test.yml**: Run tests on all packages
  - API tests with PostgreSQL
  - JavaScript SDK tests
  - Python SDK tests (multiple versions)
  - Merkle system tests
  - Web dashboard tests
  - Documentation build tests

- **build.yml**: Build all components
  - API build
  - Web dashboard build
  - Documentation build
  - Docker images
  - SDK packages

- **deploy-api.yml**: Deploy API to Fly.io
  - Production deployment
  - Staging deployment
  - Database migrations
  - Health checks
  - Automatic rollback on failure

- **deploy-web.yml**: Deploy dashboard to Vercel
  - Production deployment
  - Preview deployments for PRs
  - Lighthouse CI
  - Health checks

- **deploy-docs.yml**: Deploy docs to Netlify
  - Production deployment
  - Preview deployments
  - Broken link checking

- **publish-npm.yml**: Publish to NPM
  - JavaScript SDK
  - API types
  - Version tagging
  - Release notes

- **publish-pypi.yml**: Publish to PyPI
  - Python SDK
  - Merkle package
  - Version tagging

**Setup Required:**

GitHub Secrets:
```
# Docker
DOCKER_USERNAME
DOCKER_PASSWORD

# Fly.io
FLY_API_TOKEN

# Vercel
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID

# Netlify
NETLIFY_AUTH_TOKEN
NETLIFY_SITE_ID

# NPM
NPM_TOKEN

# PyPI
PYPI_API_TOKEN

# Notifications
SLACK_WEBHOOK

# Optional: Twitter
TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
```

### 3. Docker Configuration

Complete containerization for local development and production deployment.

**Services:**

- **postgres**: PostgreSQL 15 database
- **redis**: Redis cache
- **api**: Node.js API service
- **web**: Next.js dashboard
- **docs**: Docusaurus documentation
- **merkle-cron**: Daily attestation builder
- **adminer**: Database management UI
- **minio**: S3-compatible storage (local dev)

**Quick Start:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**Service URLs:**
- API: http://localhost:3000
- Web: http://localhost:3001
- Docs: http://localhost:3002
- Adminer: http://localhost:8080
- MinIO: http://localhost:9001

**Individual Dockerfiles:**
- `/packages/api/Dockerfile` - API service
- `/apps/web/Dockerfile` - Web dashboard
- `/apps/docs/Dockerfile` - Documentation
- `/infra/merkle/Dockerfile` - Merkle cron

### 4. Infrastructure as Code (Terraform)

Complete cloud infrastructure setup using Terraform.

**Resources Provisioned:**

**AWS:**
- S3 bucket for attestations with versioning
- CloudFront CDN for global delivery
- IAM user for Merkle publisher
- Secrets Manager for credentials
- CloudWatch logs and alarms
- SNS topics for alerts

**Cloudflare:**
- DNS records (api, attestations)
- Page rules for caching
- R2 bucket (alternative storage)
- DDoS protection

**Vercel:**
- Web dashboard project
- Documentation project
- Environment variables
- Git integration

**Quick Start:**
```bash
cd infra/terraform

# Initialize
terraform init

# Configure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Plan
terraform plan

# Apply
terraform apply

# View outputs
terraform output
```

[Full Documentation](./terraform/README.md)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                               │
│  (Source Code Repository & CI/CD Workflows)                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> GitHub Actions (CI/CD)
             │    ├─> Test (all packages)
             │    ├─> Build (Docker, SDKs)
             │    ├─> Deploy API (Fly.io)
             │    ├─> Deploy Web (Vercel)
             │    ├─> Deploy Docs (Netlify)
             │    └─> Publish (NPM, PyPI)
             │
┌────────────┴────────────────────────────────────────────────┐
│                    Production Infrastructure                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Fly.io     │     │   Vercel     │     │   Netlify    │
│  (API)       │     │  (Web)       │     │  (Docs)      │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├──> Supabase (Database)
       └──> Redis (Cache)

┌─────────────────────────────────────────────────────────────┐
│                    Storage & CDN Layer                       │
├─────────────────────────────────────────────────────────────┤
│  AWS S3 (Attestations) → CloudFront (CDN) → Cloudflare      │
│  Cloudflare R2 (Alternative)                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Merkle Attestation System                   │
├─────────────────────────────────────────────────────────────┤
│  Daily Cron Job                                              │
│  1. Fetch verified receipts from database                    │
│  2. Build Merkle tree                                        │
│  3. Generate root hash                                       │
│  4. Publish attestation to S3/R2                             │
│  5. Make available via CDN                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Monitoring & Alerts                        │
├─────────────────────────────────────────────────────────────┤
│  CloudWatch (Logs & Metrics)                                 │
│  SNS (Email Alerts)                                          │
│  Slack (Notifications)                                       │
└─────────────────────────────────────────────────────────────┘
```

## Development Workflow

### Local Development

1. **Start infrastructure:**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Run API locally:**
   ```bash
   cd packages/api
   npm install
   npm run dev
   ```

3. **Run web dashboard:**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. **Test Merkle system:**
   ```bash
   cd infra/merkle
   pip install -r requirements.txt
   python build_tree.py
   ```

### Testing

```bash
# Run all tests
npm test

# Test specific package
cd packages/api && npm test
cd packages/sdk-js && npm test
cd packages/sdk-python && pytest

# Test Merkle system
cd infra/merkle && python -m pytest
```

### Deployment

**Automatic (via CI/CD):**
- Push to `main` branch → Deploy to production
- Push to `develop` branch → Deploy to staging
- Create release → Publish to NPM/PyPI

**Manual:**
```bash
# Deploy API
cd packages/api
flyctl deploy

# Deploy web
cd apps/web
vercel --prod

# Run Merkle attestation
cd infra/merkle
python cron.py --mode once --storage s3
```

## Environment Variables

### API (.env)
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
JWT_SECRET=...
PORT=3000
NODE_ENV=production
```

### Web Dashboard (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://api.iaindex.dev
```

### Merkle System (.env)
```bash
SUPABASE_URL=https://...
SUPABASE_KEY=...
S3_BUCKET=iaindex-attestations-production
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

## Monitoring & Maintenance

### Daily Operations

1. **Check attestation status:**
   ```bash
   # View latest attestation
   aws s3 ls s3://iaindex-attestations-production/ --recursive | tail -1

   # Check Merkle cron logs
   docker-compose logs merkle-cron
   ```

2. **Monitor deployments:**
   - GitHub Actions: https://github.com/org/repo/actions
   - Fly.io Dashboard: https://fly.io/dashboard
   - Vercel Dashboard: https://vercel.com/dashboard
   - CloudWatch: AWS Console

3. **Review alerts:**
   - Check email for SNS notifications
   - Check Slack for deployment status
   - Review CloudWatch alarms

### Maintenance Tasks

**Weekly:**
- Review CloudWatch logs
- Check storage usage
- Verify backup integrity
- Update dependencies

**Monthly:**
- Rotate access keys
- Review cost reports
- Update documentation
- Security audit

**Quarterly:**
- Review infrastructure costs
- Optimize resource allocation
- Update Terraform modules
- Disaster recovery testing

## Troubleshooting

### Common Issues

**Merkle attestation failed:**
```bash
# Check logs
docker-compose logs merkle-cron

# Run manually
python infra/merkle/cron.py --mode once --storage local

# Verify database connection
echo $SUPABASE_URL
```

**API deployment failed:**
```bash
# Check Fly.io logs
flyctl logs

# SSH into container
flyctl ssh console

# Check health
curl https://api.iaindex.dev/health
```

**CI/CD pipeline failed:**
- Check GitHub Actions logs
- Verify secrets are set correctly
- Check service status (GitHub, Fly.io, Vercel)

**Terraform apply failed:**
```bash
# Validate configuration
terraform validate

# Check state
terraform state list

# Force unlock if locked
terraform force-unlock <LOCK_ID>
```

## Security

### Best Practices

1. **Secrets Management:**
   - Never commit secrets to Git
   - Use AWS Secrets Manager
   - Rotate credentials regularly
   - Use least-privilege IAM policies

2. **Network Security:**
   - Enable HTTPS everywhere
   - Use Cloudflare DDoS protection
   - Configure security groups
   - Enable VPC for sensitive resources

3. **Access Control:**
   - Use IAM roles when possible
   - Enable MFA for admin accounts
   - Audit access logs
   - Principle of least privilege

4. **Monitoring:**
   - Enable CloudTrail
   - Set up alerts for anomalies
   - Regular security audits
   - Automated vulnerability scanning

## Cost Optimization

### Current Costs (Estimated)

- **Fly.io**: $5-20/month (API hosting)
- **Vercel**: $0-20/month (Web/Docs)
- **AWS S3**: $2-5/month (Storage)
- **CloudFront**: $5-50/month (CDN)
- **Supabase**: $25/month (Database)
- **Total**: ~$40-120/month

### Optimization Tips

1. **Use CloudFront caching** to reduce S3 requests
2. **Enable S3 lifecycle policies** for old attestations
3. **Use Vercel free tier** for preview deployments
4. **Optimize Docker images** for faster builds
5. **Use AWS Reserved Instances** for predictable workloads

## Support & Resources

### Documentation
- [Merkle System](./merkle/README.md)
- [Terraform](./terraform/README.md)
- [Main Project README](../README.md)

### External Resources
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Fly.io Docs](https://fly.io/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Terraform Docs](https://terraform.io/docs)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected/)

### Getting Help
- Open an issue on GitHub
- Check existing issues and discussions
- Review CloudWatch logs
- Contact the platform team

## License

Part of the IA Index project.
