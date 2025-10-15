# Outputs for IA Index Infrastructure

# S3 Outputs
output "attestations_bucket_name" {
  description = "Name of the attestations S3 bucket"
  value       = aws_s3_bucket.attestations.id
}

output "attestations_bucket_arn" {
  description = "ARN of the attestations S3 bucket"
  value       = aws_s3_bucket.attestations.arn
}

output "attestations_bucket_domain" {
  description = "Domain name of the attestations S3 bucket"
  value       = aws_s3_bucket.attestations.bucket_regional_domain_name
}

# CloudFront Outputs
output "cdn_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.attestations.domain_name
}

output "cdn_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.attestations.id
}

# IAM Outputs
output "merkle_publisher_access_key_id" {
  description = "Access key ID for Merkle publisher"
  value       = aws_iam_access_key.merkle_publisher.id
  sensitive   = true
}

output "merkle_publisher_secret_access_key" {
  description = "Secret access key for Merkle publisher"
  value       = aws_iam_access_key.merkle_publisher.secret
  sensitive   = true
}

# Cloudflare Outputs
output "api_hostname" {
  description = "API hostname"
  value       = cloudflare_record.api.hostname
}

output "api_url" {
  description = "Full API URL"
  value       = "https://${cloudflare_record.api.hostname}"
}

output "attestations_hostname" {
  description = "Attestations CDN hostname"
  value       = cloudflare_record.attestations.hostname
}

output "attestations_url" {
  description = "Full attestations URL"
  value       = "https://${cloudflare_record.attestations.hostname}"
}

# R2 Outputs
output "r2_bucket_name" {
  description = "Name of the Cloudflare R2 bucket"
  value       = cloudflare_r2_bucket.attestations_r2.name
}

# Vercel Outputs
output "web_project_id" {
  description = "Vercel web project ID"
  value       = vercel_project.web.id
}

output "docs_project_id" {
  description = "Vercel docs project ID"
  value       = vercel_project.docs.id
}

# Secrets Manager Outputs
output "supabase_secret_arn" {
  description = "ARN of Supabase credentials secret"
  value       = aws_secretsmanager_secret.supabase_credentials.arn
}

output "jwt_secret_arn" {
  description = "ARN of JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

# Monitoring Outputs
output "alerts_topic_arn" {
  description = "ARN of SNS alerts topic"
  value       = aws_sns_topic.alerts.arn
}

output "merkle_log_group_name" {
  description = "Name of Merkle cron CloudWatch log group"
  value       = aws_cloudwatch_log_group.merkle_cron.name
}

# Summary Output
output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment           = var.environment
    region                = var.aws_region
    api_url               = "https://${cloudflare_record.api.hostname}"
    attestations_url      = "https://${cloudflare_record.attestations.hostname}"
    attestations_bucket   = aws_s3_bucket.attestations.id
    cdn_distribution      = aws_cloudfront_distribution.attestations.id
    web_project           = vercel_project.web.id
    docs_project          = vercel_project.docs.id
  }
}

# Environment Configuration Output
output "environment_config" {
  description = "Environment variables for application configuration"
  value = {
    S3_BUCKET               = aws_s3_bucket.attestations.id
    AWS_REGION              = var.aws_region
    CDN_URL                 = "https://${cloudflare_record.attestations.hostname}"
    API_URL                 = "https://${cloudflare_record.api.hostname}"
    SUPABASE_SECRET_ARN     = aws_secretsmanager_secret.supabase_credentials.arn
    JWT_SECRET_ARN          = aws_secretsmanager_secret.jwt_secret.arn
    LOG_GROUP               = aws_cloudwatch_log_group.merkle_cron.name
    ALERTS_TOPIC_ARN        = aws_sns_topic.alerts.arn
  }
  sensitive = false
}

# Terraform State Info
output "terraform_info" {
  description = "Terraform state information"
  value = {
    workspace      = terraform.workspace
    caller_account = data.aws_caller_identity.current.account_id
    caller_arn     = data.aws_caller_identity.current.arn
    region         = data.aws_region.current.name
  }
}
