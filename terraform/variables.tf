variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Server Location"
  type        = string
  default     = "asia-southeast1" # Singapore Region
}

variable "dataset_name" {
  description = "Big Query Dataset Name"
  type        = string
  default     = "olist_dwh"
}