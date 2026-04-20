""" @bruin
name: bronze/ingest.ingest_scm_kaggle
type: python
description: "Retrieve dataset from Kaggle and store it in a specified local directory (Bronze Layer)."
@bruin """

import os
import shutil
from dotenv import load_dotenv
import kagglehub


def load_env():
    """
    Load environment variables from .env file and validate required keys.
    """
    load_dotenv()

    required_vars = ["KAGGLE_USERNAME", "KAGGLE_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Missing environment variable: {var}")


def download_olist_dataset(target_dir: str) -> str:
    """
    Download Olist dataset from Kaggle and move it to a target directory.
    """

    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Idempotent check: skip if data already exists
    if os.listdir(target_dir):
        print(f"Dataset already exists at: {target_dir}")
        return target_dir

    print("Downloading dataset from Kaggle...")

    # Download dataset to kagglehub cache
    cache_path = kagglehub.dataset_download("prashantk93/supply-chain-management-for-car")
    print(f"Downloaded to cache: {cache_path}")

    # Move files from cache to target directory
    for file_name in os.listdir(cache_path):
        src = os.path.join(cache_path, file_name)
        dst = os.path.join(target_dir, file_name)

        if os.path.isfile(src):
            shutil.move(src, dst)

    print(f"Dataset moved to: {target_dir}")
    return target_dir


def list_files(data_path: str):
    """
    List all files in the dataset directory.

    Args:
        data_path (str): Path to dataset folder
    """
    print("\nFiles in dataset:")

    for root, _, files in os.walk(data_path):
        for file in files:
            print(f"- {os.path.join(root, file)}")


def run():
    """
    Main pipeline execution function.
    """
    print("Starting ingest pipeline...")

    # Load environment variables
    load_env()

    # Set target directory
    target_dir = os.getenv(
        "RAW_DATA_PATH",
        "/workspaces/scm-data-pipeline/data"
    )

    # Download and store dataset
    data_path = download_olist_dataset(target_dir)

    # List files for verification
    list_files(data_path)


if __name__ == "__main__":
    run()