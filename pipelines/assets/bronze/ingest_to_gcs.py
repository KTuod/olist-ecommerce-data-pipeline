"""@bruin
name: bronze.ingest_to_gcs
type: python
description: "Upload data files to Data Lake (GCS)"
@bruin"""

import os
from google.cloud import storage
from dotenv import load_dotenv

def upload_to_datalake():
    load_dotenv()
    
    # PROJECT ID
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    
    # Initiating GCP connection
    client = storage.Client(project=project_id)
    
    bucket_name = f"{project_id}-olist-datalake"

    try:
        bucket = client.get_bucket(bucket_name)
    except Exception as e:
        print(f"ERROR: Cannot find the bucket '{bucket_name}'")
        return

    # Data folder path
    data_path = "data/"
    if not os.path.exists(data_path):
        print(f"ERROR: Cannot find the folder '{data_path}'.")
        return

    csv_files = [f for f in os.listdir(data_path) if f.endswith(".csv")]
    
    if len(csv_files) == 0:
        print("WARNING: Folder 'data/' is empty.")
        return

    # Upload to cloud
    for filename in csv_files:
        local_path = os.path.join(data_path, filename)
        
        # Storing to folder raw_csv
        blob_name = f"raw_csv/{filename}" 
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        print(f"Uploaded: {filename}")

if __name__ == "__main__":
    upload_to_datalake()