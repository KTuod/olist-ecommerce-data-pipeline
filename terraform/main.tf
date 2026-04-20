terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

# 1. Configure Cloudflare provider
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# 2. Create Data Lake storage (Bronze, Silver, Gold)
resource "cloudflare_r2_bucket" "data_lake" {
  account_id = var.cloudflare_account_id
  name       = var.bucket_name
  location   = "APAC"
}

# 3. Set up cost alert notification via email
resource "cloudflare_notification_policy" "r2_budget_alert" {
  account_id  = var.cloudflare_account_id
  name        = "Critical Alert - Cloudflare R2 Cost"
  description = "Automatically send an email when account billing increases significantly"
  enabled     = true
  alert_type  = "billing_usage_alert"

  filters {
    product = ["r2_storage"]
    limit   = ["10"]
  }

  email_integration {
    id = var.alert_email
  }
}

# 4. Output information for PySpark configuration
output "s3a_endpoint" {
  value       = "https://${var.cloudflare_account_id}.r2.cloudflarestorage.com"
  description = "Endpoint URL for Spark configuration: spark.hadoop.fs.s3a.endpoint"
  sensitive = true
}

output "bucket_created" {
  value = cloudflare_r2_bucket.data_lake.name
}