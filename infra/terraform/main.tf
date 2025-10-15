terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
  }

  backend "s3" {
    bucket         = "iaindex-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "iaindex-terraform-locks"
  }
}

# AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "IA Index"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Cloudflare Provider
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Vercel Provider
provider "vercel" {
  api_token = var.vercel_api_token
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 Bucket for Attestations
resource "aws_s3_bucket" "attestations" {
  bucket = "${var.project_name}-attestations-${var.environment}"

  tags = {
    Name        = "Attestations Storage"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "attestations" {
  bucket = aws_s3_bucket.attestations.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "attestations" {
  bucket = aws_s3_bucket.attestations.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "attestations_public_read" {
  bucket = aws_s3_bucket.attestations.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.attestations.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.attestations]
}

resource "aws_s3_bucket_cors_configuration" "attestations" {
  bucket = aws_s3_bucket.attestations.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3600
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "attestations" {
  bucket = aws_s3_bucket.attestations.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

# IAM User for Merkle Cron Job
resource "aws_iam_user" "merkle_publisher" {
  name = "${var.project_name}-merkle-publisher-${var.environment}"

  tags = {
    Description = "Service account for Merkle attestation publishing"
  }
}

resource "aws_iam_access_key" "merkle_publisher" {
  user = aws_iam_user.merkle_publisher.name
}

resource "aws_iam_user_policy" "merkle_publisher_s3" {
  name = "attestation-publisher-policy"
  user = aws_iam_user.merkle_publisher.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.attestations.arn,
          "${aws_s3_bucket.attestations.arn}/*"
        ]
      }
    ]
  })
}

# CloudFront Distribution for Attestations
resource "aws_cloudfront_distribution" "attestations" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "IA Index Attestations CDN"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  origin {
    domain_name = aws_s3_bucket.attestations.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.attestations.id}"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.attestations.id}"

    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"]

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "Attestations CDN"
    Environment = var.environment
  }
}

# Cloudflare DNS Records
data "cloudflare_zone" "main" {
  name = var.domain_name
}

resource "cloudflare_record" "api" {
  zone_id = data.cloudflare_zone.main.id
  name    = var.environment == "production" ? "api" : "api-${var.environment}"
  value   = var.fly_app_hostname
  type    = "CNAME"
  proxied = true
  ttl     = 1
}

resource "cloudflare_record" "attestations" {
  zone_id = data.cloudflare_zone.main.id
  name    = "attestations"
  value   = aws_cloudfront_distribution.attestations.domain_name
  type    = "CNAME"
  proxied = true
  ttl     = 1
}

# Cloudflare Page Rules
resource "cloudflare_page_rule" "api_cache" {
  zone_id  = data.cloudflare_zone.main.id
  target   = "${cloudflare_record.api.hostname}/*"
  priority = 1

  actions {
    cache_level = "bypass"
  }
}

resource "cloudflare_page_rule" "attestations_cache" {
  zone_id  = data.cloudflare_zone.main.id
  target   = "${cloudflare_record.attestations.hostname}/*"
  priority = 2

  actions {
    cache_level         = "cache_everything"
    edge_cache_ttl      = 86400
    browser_cache_ttl   = 86400
    cache_on_cookie     = "nocookie"
  }
}

# Cloudflare R2 Bucket (Alternative to S3)
resource "cloudflare_r2_bucket" "attestations_r2" {
  account_id = var.cloudflare_account_id
  name       = "${var.project_name}-attestations-${var.environment}"
  location   = "WNAM"
}

# Vercel Project for Web Dashboard
resource "vercel_project" "web" {
  name      = "${var.project_name}-web-${var.environment}"
  framework = "nextjs"

  git_repository = {
    type = "github"
    repo = var.github_repo
  }

  build_command    = "npm run build"
  output_directory = ".next"
  install_command  = "npm ci"

  environment = [
    {
      key    = "NEXT_PUBLIC_API_URL"
      value  = "https://${cloudflare_record.api.hostname}"
      target = ["production"]
    },
    {
      key    = "NODE_ENV"
      value  = "production"
      target = ["production"]
    }
  ]
}

# Vercel Project for Documentation
resource "vercel_project" "docs" {
  name      = "${var.project_name}-docs"
  framework = "docusaurus"

  git_repository = {
    type = "github"
    repo = var.github_repo
  }

  build_command    = "npm run build"
  output_directory = "build"
  install_command  = "npm ci"
}

# AWS Secrets Manager for Sensitive Configuration
resource "aws_secretsmanager_secret" "supabase_credentials" {
  name                    = "${var.project_name}/${var.environment}/supabase"
  description             = "Supabase credentials for ${var.environment}"
  recovery_window_in_days = 7

  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "supabase_credentials" {
  secret_id = aws_secretsmanager_secret.supabase_credentials.id

  secret_string = jsonencode({
    url = var.supabase_url
    key = var.supabase_key
  })
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name                    = "${var.project_name}/${var.environment}/jwt"
  description             = "JWT secret for ${var.environment}"
  recovery_window_in_days = 7

  tags = {
    Environment = var.environment
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "merkle_cron" {
  name              = "/iaindex/${var.environment}/merkle-cron"
  retention_in_days = 30

  tags = {
    Application = "Merkle Attestation"
    Environment = var.environment
  }
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-alerts"

  tags = {
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "attestation_failures" {
  alarm_name          = "${var.project_name}-${var.environment}-attestation-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "AttestationFailures"
  namespace           = "IAIndex"
  period              = 300
  statistic           = "Sum"
  threshold           = 3
  alarm_description   = "Alert when attestation publishing fails repeatedly"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  tags = {
    Environment = var.environment
  }
}
