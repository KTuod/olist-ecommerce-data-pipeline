variable "cloudflare_account_id" {
  description = "CloudFlare Account ID"
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "API Token"
  type        = string
  sensitive   = true
}

variable "bucket_name" {
  description = "Name of Storing Dataset"
  type        = string
  default     = "scm-car-dataset"
}

variable "alert_email" {
  description = "Email for notification if exceed free tier"
  type        = string
}