# pyrefly: ignore [missing-import]
from google.cloud import bigquery
from scraper_trm import fetch_daily_trm
from datetime import datetime
import pytz
import io
import json

def run_pipeline():
    # 1. Extraction Phase
    print("Starting data extraction...")
    data = fetch_daily_trm()
    
    if not data:
        print("Extraction failed. Pipeline aborted.")
        return
        
    print(f"Data extracted successfully -> TRM: {data['trm_value']}, Date: {data['trm_date']}")
    
    # 2. Connection Phase
    try:
        print("\nConnecting to Google BigQuery...")
        key_path = "bigquery-keys.json"
        client = bigquery.Client.from_service_account_json(key_path)
        print(f"Successfully connected to GCP Project: {client.project}!")

        dataset_id = "raw_data"
        table_id = f"{client.project}.{dataset_id}.daily_trm"

        schema = [
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("trm_value", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("extraction_date", "TIMESTAMP", mode="REQUIRED")
        ]

        try:
            client.get_table(table_id)  
            print(f"Table {table_id} already exists.")
        except Exception:
            print(f"Table {table_id} not found. Creating it now...")
            table_obj = bigquery.Table(table_id, schema=schema)
            client.create_table(table_obj)
            print(f"Table {table_id} successfully created!")

        colombia_tz = pytz.timezone('America/Bogota')
        current_timestamp = datetime.now(colombia_tz).isoformat()
        
        row_to_insert = {
            "date": data["trm_date"],
            "trm_value": data["trm_value"],
            "extraction_date": current_timestamp
        }

        ndjson_data = json.dumps(row_to_insert) + "\n"

        file_like_object = io.StringIO(ndjson_data)

        print(f"Loading data via Batch into {table_id}...")

        job_config = bigquery.LoadJobConfig(
            source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema = schema
        )

        load_job = client.load_table_from_file(
            file_like_object,
            table_id,
            job_config=job_config
        )

        load_job.result()

        print("Success! New row successfully loaded into BigQuery via Batch (100% Free).")

    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        
if __name__ == "__main__":
    run_pipeline()