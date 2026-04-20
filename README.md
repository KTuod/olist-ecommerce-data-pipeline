# 🚗 Car Supply Chain Data Pipeline

## ❗ Problem Statement

Modern supply chain systems generate large volumes of data from multiple sources such as orders, inventory, logistics, and suppliers. However, this data is often:

* Fragmented across multiple systems
* Stored in inconsistent formats
* Not structured for analytical use
* Difficult to process efficiently at scale

As a result, organizations face several key challenges:

* Slow and inefficient reporting workflows
* Limited visibility into supply chain performance
* Difficulty in building reliable dashboards
* High manual effort in data cleaning and preparation

Without a well-designed data pipeline, transforming raw data into actionable insights becomes time-consuming, error-prone, and not scalable.

---

## 💡 Solution

This project addresses these challenges by building an automated and scalable **end-to-end data pipeline** that:

* ✅ Ingests raw data from external sources (Kaggle)
* ✅ Cleans, validates, and standardizes datasets
* ✅ Structures data using **Medallion Architecture (Bronze → Silver → Gold)**
* ✅ Stores data in a cost-efficient **cloud data lake (Cloudflare R2)**
* ✅ Enables fast analytical queries via **MotherDuck (DuckDB)**
* ✅ Supports downstream analytics and dashboard applications

---

## ✨ Key Highlights

* 🏗️ End-to-end Data Pipeline (Ingestion → Transformation → Warehouse)
* 🧱 Medallion Architecture (Bronze / Silver / Gold)
* ⚙️ Fully automated workflow orchestration
* ☁️ Cloud-native storage (Data Lake + Data Warehouse)
* 🐳 Reproducible environment with Docker DevContainers
* 🔁 Infrastructure managed via Terraform (IaC)

---

## 🧠 Architecture Overview

```text
        ┌────────────┐
        │  Kaggle    │
        └─────┬──────┘
              │
              ▼
     🥉 Bronze Layer (Raw Data)
              │
              ▼
     🥈 Silver Layer (Cleaned Data)
              │
              ▼
     🥇 Gold Layer (Business Data)
              │
              ▼
     📊 Analytics / Dashboard
```

---

## 🏗️ Data Architecture: Medallion Model

| Layer     | Description                                                  |
| --------- | ------------------------------------------------------------ |
| 🥉 Bronze | Raw data ingested from source (immutable, no transformation) |
| 🥈 Silver | Cleaned, normalized, and structured data                     |
| 🥇 Gold   | Aggregated, business-ready datasets optimized for analytics  |

---

## ⚙️ Tech Stack

| Category       | Tools                          |
| -------------- | ------------------------------ |
| Language       | Python                         |
| Orchestration  | Bruin                          |
| Data Warehouse | MotherDuck (DuckDB)            |
| Data Lake      | Cloudflare R2                  |
| Infrastructure | Terraform                      |
| Environment    | Docker + VS Code DevContainers |

---

## 📂 Project Structure

```text
.
├── .devcontainer/          # Docker-based development environment
├── data/                   # Raw input data
├── pipelines/
│   ├── assets/
│   │   ├── bronze/         # Data ingestion
│   │   ├── silver/         # Data cleaning & transformation
│   │   ├── gold/           # Data aggregation & loading
│   │   └── storage/        # R2 upload logic
│   └── pipeline.yml        # Pipeline definition (Bruin)
├── terraform/              # Infrastructure as Code (R2 buckets)
├── .bruin.yml              # Bruin configuration
├── .env                    # Environment variables
├── app.py                  # Analytics / dashboard app
└── requirements.txt        # Dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites

* 🐳 Docker Desktop (running)
* 💻 Visual Studio Code + Dev Containers extension
* 🔑 Accounts:

  * Kaggle
  * Cloudflare
  * MotherDuck

---

### 2. Setup Development Environment

```bash
Ctrl + Shift + P → Dev Containers: Reopen in Container
```

---

### 3. Configure Variables

#### Environment Variables

Create file .env with the content:

```env
R2_ACCOUNT_ID=...
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
R2_BUCKET_NAME=scm-car-dataset

KAGGLE_USERNAME=...
KAGGLE_KEY=...

RAW_DATA_PATH=/workspaces/scm-data-pipeline/data

MOTHERDUCK_TOKEN=...
```

#### Terraform Variables

Before deploying infrastructure, create a `terraform.tfvars` file inside the `terraform/` directory to store your sensitive credentials and configuration values.

```bash
cd terraform
touch terraform.tfvars
```

Then add the following content:

```hcl
cloudflare_account_id =...
cloudflare_api_token  =...

bucket_name           = "scm-car-dataset"
alert_email           = ...
```

---

### 4. Provision Infrastructure (Terraform)

```bash
cd terraform

terraform init
terraform plan
terraform apply

cd ..
```

---

### 5. Run Data Pipeline

```bash
bruin run pipelines/pipeline.yml
```

---

### 6. Launch Streamlit

```bash
streamlit run app.py
```
![Streamlit Dashboard](documents/Streamlit%20Dashboard.png)
---
