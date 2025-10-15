# Infrastructure as Code - Terraform

This directory contains Terraform configuration for deploying the IA Index infrastructure.

## Overview

The infrastructure includes:

- **AWS S3**: Attestation storage with versioning and lifecycle policies
- **CloudFront**: CDN for fast global attestation delivery
- **Cloudflare**: DNS management and DDoS protection
- **Cloudflare R2**: Alternative object storage (optional)
- **Vercel**: Web dashboard and documentation hosting
- **AWS Secrets Manager**: Secure credential storage
- **CloudWatch**: Logging and monitoring
- **SNS**: Alert notifications

## Prerequisites

1. **Install Terraform**: Version 1.5.0 or higher
   ```bash
   brew install terraform  # macOS
   ```

2. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```

3. **Set up Required Accounts**:
   - AWS account with appropriate permissions
   - Cloudflare account with API token
   - Vercel account with API token
   - Fly.io account for API hosting
   - Supabase project

## Setup

1. **Initialize Terraform**:
   ```bash
   cd infra/terraform
   terraform init
   ```

2. **Create Configuration**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Review Plan**:
   ```bash
   terraform plan
   ```

4. **Apply Configuration**:
   ```bash
   terraform apply
   ```

## Configuration

### Required Variables

Edit `terraform.tfvars` with your values:

```hcl
# Cloudflare
cloudflare_api_token  = "your-token"
cloudflare_account_id = "your-account-id"

# Vercel
vercel_api_token = "your-vercel-token"

# Supabase
supabase_url = "https://your-project.supabase.co"
supabase_key = "your-key"

# Monitoring
alert_email = "alerts@example.com"

# Fly.io
fly_app_hostname = "your-app.fly.dev"
```

### Environments

Use Terraform workspaces for multiple environments:

```bash
# Create and switch to staging
terraform workspace new staging
terraform workspace select staging

# Apply staging configuration
terraform apply -var="environment=staging"

# Switch back to production
terraform workspace select production
```

## Architecture

### Storage Layer

- **S3 Bucket**: Primary attestation storage
  - Versioning enabled
  - Lifecycle policies (90 days → Glacier → Deep Archive)
  - Public read access for attestations
  - CORS enabled

- **CloudFront CDN**: Global content delivery
  - HTTPS enforcement
  - Caching optimization
  - Gzip compression

### DNS & Security

- **Cloudflare**:
  - DNS management
  - DDoS protection
  - SSL/TLS termination
  - Page rules for caching

### Application Hosting

- **Vercel**: Next.js web dashboard and Docusaurus docs
  - Automatic deployments from Git
  - Edge functions
  - Preview environments

### Secrets Management

- **AWS Secrets Manager**:
  - Supabase credentials
  - JWT secrets
  - API keys
  - 7-day recovery window

### Monitoring

- **CloudWatch**:
  - Log aggregation
  - Custom metrics
  - Alarms for failures

- **SNS**:
  - Email alerts
  - Webhook notifications

## Outputs

After applying, Terraform outputs important values:

```bash
terraform output
```

Key outputs:
- `api_url`: API endpoint
- `attestations_url`: CDN URL for attestations
- `merkle_publisher_access_key_id`: IAM credentials (sensitive)
- `deployment_summary`: Complete deployment info

Retrieve sensitive outputs:
```bash
terraform output -raw merkle_publisher_secret_access_key
```

## State Management

Terraform state is stored in S3 with DynamoDB locking:

```hcl
backend "s3" {
  bucket         = "iaindex-terraform-state"
  key            = "production/terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "iaindex-terraform-locks"
}
```

### State Setup

Create state backend resources (one-time):

```bash
# Create S3 bucket for state
aws s3 mb s3://iaindex-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket iaindex-terraform-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for locks
aws dynamodb create-table \
  --table-name iaindex-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## Common Operations

### Update Infrastructure

```bash
# Pull latest state
terraform refresh

# Plan changes
terraform plan

# Apply changes
terraform apply
```

### Destroy Resources

```bash
# Preview destruction
terraform plan -destroy

# Destroy (with confirmation)
terraform destroy

# Destroy specific resource
terraform destroy -target=aws_s3_bucket.attestations
```

### Import Existing Resources

```bash
# Import existing S3 bucket
terraform import aws_s3_bucket.attestations iaindex-attestations-production

# Import CloudFront distribution
terraform import aws_cloudfront_distribution.attestations E1234567890ABC
```

### View State

```bash
# List resources
terraform state list

# Show resource details
terraform state show aws_s3_bucket.attestations

# Pull state
terraform state pull > state.json
```

## Cost Estimation

Approximate monthly costs:

- **S3 Storage**: $0.023/GB (~$2.30 for 100GB)
- **CloudFront**: $0.085/GB for first 10TB (~$85 for 1TB)
- **Secrets Manager**: $0.40 per secret (~$1.60)
- **CloudWatch Logs**: $0.50/GB ingested (~$5)
- **R2 Storage** (optional): $0.015/GB (~$1.50 for 100GB)

**Estimated Total**: $10-100/month depending on usage

## Security Best Practices

1. **Never commit terraform.tfvars**:
   ```bash
   echo "terraform.tfvars" >> .gitignore
   ```

2. **Use separate AWS accounts** for production/staging

3. **Enable MFA** for Terraform operations:
   ```bash
   export AWS_PROFILE=terraform-mfa
   ```

4. **Rotate credentials regularly**:
   ```bash
   terraform apply -replace=aws_iam_access_key.merkle_publisher
   ```

5. **Review security groups** before applying

6. **Enable AWS CloudTrail** for audit logging

## Troubleshooting

### State Lock Issues

```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

### Provider Authentication

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test Cloudflare API
curl -X GET "https://api.cloudflare.com/client/v4/user" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### Plan Failures

```bash
# Increase log verbosity
TF_LOG=DEBUG terraform plan

# Validate configuration
terraform validate
```

## CI/CD Integration

GitHub Actions workflow for Terraform:

```yaml
# .github/workflows/terraform.yml
- name: Terraform Plan
  run: terraform plan -no-color
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

- name: Terraform Apply
  if: github.ref == 'refs/heads/main'
  run: terraform apply -auto-approve
```

## Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Cloudflare Provider](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs)
- [Terraform Vercel Provider](https://registry.terraform.io/providers/vercel/vercel/latest/docs)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected/)
- [Cloudflare Security](https://www.cloudflare.com/learning/security/)

## Support

For infrastructure issues:
1. Check CloudWatch logs
2. Review Terraform plan output
3. Consult AWS/Cloudflare status pages
4. Contact platform team
