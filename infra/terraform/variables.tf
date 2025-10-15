# Variables for IA Index Infrastructure

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "iaindex"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be one of: production, staging, development"
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Root domain name"
  type        = string
  default     = "iaindex.dev"
}

# Cloudflare Configuration
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
}

# Vercel Configuration
variable "vercel_api_token" {
  description = "Vercel API token"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository (org/repo format)"
  type        = string
  default     = "iaindex/iaindex"
}

# Fly.io Configuration
variable "fly_app_hostname" {
  description = "Fly.io app hostname"
  type        = string
}

# Supabase Configuration
variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
  sensitive   = true
}

variable "supabase_key" {
  description = "Supabase anon/service key"
  type        = string
  sensitive   = true
}

# Monitoring
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

# Feature Flags
variable "enable_r2" {
  description = "Enable Cloudflare R2 for attestation storage"
  type        = bool
  default     = false
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN for attestations"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Storage Configuration
variable "attestation_retention_days" {
  description = "Number of days to retain attestations in hot storage"
  type        = number
  default     = 90
}

variable "enable_versioning" {
  description = "Enable versioning for attestation bucket"
  type        = bool
  default     = true
}

# Database Configuration
variable "database_max_connections" {
  description = "Maximum number of database connections"
  type        = number
  default     = 100
}

# API Configuration
variable "api_rate_limit" {
  description = "API rate limit (requests per minute)"
  type        = number
  default     = 1000
}

# CDN Configuration
variable "cdn_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.cdn_price_class)
    error_message = "Price class must be one of: PriceClass_100, PriceClass_200, PriceClass_All"
  }
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# Backup Configuration
variable "enable_automated_backups" {
  description = "Enable automated database backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}
