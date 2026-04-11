terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Google Cloud Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# ------------------------------------------------------
# 1. DATA LAKE (Bronze Layer): Google Cloud Storage Bucket
# ------------------------------------------------------
resource "google_storage_bucket" "data_lake" {
  name          = "${var.project_id}-olist-datalake"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"
  uniform_bucket_level_access = true
}

# ------------------------------------------------------
# 2. DATA WAREHOUSE (Silver & Gold Layer): BigQuery Dataset
# ------------------------------------------------------
resource "google_bigquery_dataset" "data_warehouse" {
  dataset_id                  = var.dataset_name
  friendly_name               = "Olist E-Commerce DWH"
  description                 = "Data Warehouse for the Olist pipeline, supporting sales analytics"
  location                    = var.region
  delete_contents_on_destroy  = true
}