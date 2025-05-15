import os
import pandas as pd
import numpy as np
import boto3
import hashlib
import faiss
import requests
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi
from sklearn.metrics.pairwise import cosine_similarity
import mlflow

# Environment variables
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
KAGGLE_DATASET = "davidgauthier/glassdoor-job-reviews"
RAW_S3_PREFIX = "raw/"
PROCESSED_S3_PREFIX = "processed/"
FEATURES_S3_PREFIX = "features/"
DYNAMIC_SOURCES_PREFIX = "dynamic_updates/"

LOCAL_DATA_FOLDER = "/opt/airflow/data"
os.makedirs(LOCAL_DATA_FOLDER, exist_ok=True)

# File paths
LOCAL_RAW_FILE = f"{LOCAL_DATA_FOLDER}/glassdoor_reviews.csv"
LOCAL_CLEAN_FILE = f"{LOCAL_DATA_FOLDER}/glassdoor_cleaned.parquet"
LOCAL_MERGED_CSV = f"{LOCAL_DATA_FOLDER}/merged_jobs.csv"
LOCAL_HASH_FILE = f"{LOCAL_DATA_FOLDER}/merged_jobs.hash"
LOCAL_EMBEDDINGS = f"{LOCAL_DATA_FOLDER}/embeddings.npy"
LOCAL_METADATA = f"{LOCAL_DATA_FOLDER}/metadata.csv"
LOCAL_FAISS_INDEX = f"{LOCAL_DATA_FOLDER}/faiss_index.bin"

def s3_client():
    return boto3.client('s3',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=AWS_REGION)

def upload_to_s3(local_file, s3_key, cleanup=False):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)
    try:
        s3.upload_file(local_file, S3_BUCKET, s3_key)
        print(f"Uploaded {local_file} to s3://{S3_BUCKET}/{s3_key}")
        if cleanup:
            os.remove(local_file)
            print(f"Local file {local_file} deleted after upload.")
    except Exception as e:
        raise Exception(f"Error uploading {local_file} to S3: {e}")

def download_from_s3(s3_key, local_file):
    s3_client().download_file(S3_BUCKET, s3_key, local_file)
    print(f"Downloaded {s3_key} to {local_file}")

def file_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# ---------------- Ingestion & Preprocessing ----------------

def download_from_kaggle():
    api = KaggleApi()
    api.authenticate()

    # Download the entire dataset as a zip
    zip_path = os.path.join(LOCAL_DATA_FOLDER, "glassdoor_reviews.zip")
    api.dataset_download_files(KAGGLE_DATASET, path=LOCAL_DATA_FOLDER, force=True)
    
    print(f"Files after download: {os.listdir(LOCAL_DATA_FOLDER)}")

    if not os.path.exists(zip_path):
        # If Kaggle saved it with a different name, find it
        for file in os.listdir(LOCAL_DATA_FOLDER):
            if file.endswith(".zip"):
                zip_path = os.path.join(LOCAL_DATA_FOLDER, file)
                break
        else:
            raise FileNotFoundError("No zip file found after Kaggle download.")

    # ✅ Unzip safely
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(LOCAL_DATA_FOLDER)
        print(f"[Info] Extracted ZIP contents to {LOCAL_DATA_FOLDER}: {os.listdir(LOCAL_DATA_FOLDER)}")
    except zipfile.BadZipFile as e:
        raise Exception(f"[❌ Error] Bad ZIP file: {e}")
    except EOFError as e:
        raise Exception(f"[❌ Error] ZIP file corrupted or incomplete: {e}")

    # ✅ Now load the extracted CSV file
    csv_file = os.path.join(LOCAL_DATA_FOLDER, "glassdoor_reviews.csv")
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"{csv_file} not found after extraction.")

    try:
        df = pd.read_csv(csv_file, engine='python', on_bad_lines='skip', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_file, engine='python', on_bad_lines='skip', encoding='latin1')


def upload_raw_to_s3():
    if not os.path.isfile(LOCAL_RAW_FILE):
        raise FileNotFoundError(f"File {LOCAL_RAW_FILE} does not exist. files in {LOCAL_DATA_FOLDER}: {os.listdir(LOCAL_DATA_FOLDER)}")
    
    print(f"Uploading {LOCAL_RAW_FILE} to S3...")
    upload_to_s3(LOCAL_RAW_FILE, f"{RAW_S3_PREFIX}glassdoor_reviews.csv", cleanup=False)
    print("✅ Raw data uploaded to S3")

def clean_glassdoor_data_and_upload_to_s3():
    try:
        if not os.path.isfile(LOCAL_RAW_FILE):
            raise FileNotFoundError(f"File {LOCAL_RAW_FILE} does not exist. files in {LOCAL_DATA_FOLDER}: {os.listdir(LOCAL_DATA_FOLDER)}")

        df = pd.read_csv(LOCAL_RAW_FILE, engine='python', on_bad_lines='skip', encoding='latin1')
        df = df[['job_title', 'firm', 'pros', 'cons']].dropna()
        df['job_title'] = df['job_title'].astype(str).str.strip()
        df['pros'] = df['pros'].str.strip()
        df['cons'] = df['cons'].str.strip()
        df['firm'] = df['firm'].str.strip()
        df['content'] = "Pros: " + df['pros'] + ". Cons: " + df['cons'] + "."

        df_clean = df[['job_title', 'firm', 'content']]
        df_clean.to_parquet(LOCAL_CLEAN_FILE, index=False)
        print(df_clean.head())
        upload_to_s3(LOCAL_CLEAN_FILE, f"{PROCESSED_S3_PREFIX}glassdoor_cleaned.parquet", cleanup=False)
        print("✅ Glassdoor data cleaned and uploaded to S3")
    except Exception as e:
        print(f"❌ Error in cleaning Glassdoor data: {e}")
        raise

def scrape_remoteok():
    url = "https://remoteok.com/api"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    jobs = response.json()[1:]
    records = [{"job_title": job.get("position", ""),
                "company": job.get("company", ""),
                "description": BeautifulSoup(job.get("description", ""), 'html.parser').get_text(),
                "tags": ", ".join(job.get("tags", [])),
                "url": job.get("url", "")} for job in jobs]
    df = pd.DataFrame(records)
    df.to_parquet(f"{LOCAL_DATA_FOLDER}/remoteok.parquet", index=False)
    upload_to_s3(f"{LOCAL_DATA_FOLDER}/remoteok.parquet", "dynamic_updates/remoteok/remoteok.parquet", cleanup=False)

def scrape_remotive():
    url = "https://remotive.com/api/remote-jobs"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    jobs = response.json()['jobs']
    records = [{"job_title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "description": BeautifulSoup(job.get("description", ""), 'html.parser').get_text(),
                "tags": ", ".join(job.get("tags", [])),
                "url": job.get("url", "")} for job in jobs]
    df = pd.DataFrame(records)
    df.to_parquet(f"{LOCAL_DATA_FOLDER}/remotive.parquet", index=False)
    upload_to_s3(f"{LOCAL_DATA_FOLDER}/remotive.parquet", "dynamic_updates/remotive/remotive.parquet", cleanup=False)

def scrape_adzuna():
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {"app_id": os.getenv("ADZUNA_APP_ID"),
              "app_key": os.getenv("ADZUNA_APP_KEY"),
              "what": "remote developer",
              "results_per_page": 20}
    response = requests.get(url, params=params)
    data = response.json().get("results", [])
    records = [{"job_title": job.get("title", ""),
                "company": job.get("company", {}).get("display_name", ""),
                "description": job.get("description", ""),
                "location": job.get("location", {}).get("display_name", ""),
                "url": job.get("redirect_url", "")} for job in data]
    df = pd.DataFrame(records)
    df.to_parquet(f"{LOCAL_DATA_FOLDER}/adzuna.parquet", index=False)
    upload_to_s3(f"{LOCAL_DATA_FOLDER}/adzuna.parquet", "dynamic_updates/adzuna/adzuna.parquet", cleanup=False)

# ---------------- Merging, Embeddings, FAISS ----------------

def merge_all_sources_and_save():
    # Load all cleaned and dynamic data
    df_glassdoor = pd.read_parquet(LOCAL_CLEAN_FILE)
    df_glassdoor['description'] = df_glassdoor['content']
    df_glassdoor['tags'] = ""
    df_glassdoor['url'] = ""
    df_glassdoor['source'] = "glassdoor"
    df_glassdoor = df_glassdoor.rename(columns={"firm": "company"})
    df_glassdoor = df_glassdoor[["job_title", "company", "description", "tags", "url", "source"]]

    df_remoteok = pd.read_parquet(f"{LOCAL_DATA_FOLDER}/remoteok.parquet")
    df_remotive = pd.read_parquet(f"{LOCAL_DATA_FOLDER}/remotive.parquet")
    df_adzuna = pd.read_parquet(f"{LOCAL_DATA_FOLDER}/adzuna.parquet")

    for df in [df_remoteok, df_remotive, df_adzuna]:
        df["source"] = df.get("source", df.__class__.__name__.lower())
        if "tags" not in df.columns:
            df["tags"] = ""
        if "url" not in df.columns:
            df["url"] = ""

    df_merged = pd.concat([df_glassdoor, df_remoteok, df_remotive, df_adzuna], ignore_index=True)

    # Save as parquet instead of CSV
    LOCAL_MERGED_PARQUET = f"{LOCAL_DATA_FOLDER}/merged_jobs.parquet"
    df_merged.to_parquet(LOCAL_MERGED_PARQUET, index=False)

    upload_to_s3(LOCAL_MERGED_PARQUET, "features/merged_jobs.parquet")

    # Calculate hash based on parquet file
    with open(LOCAL_MERGED_PARQUET, "rb") as f:
        hash_val = file_md5(LOCAL_MERGED_PARQUET)
    with open(LOCAL_HASH_FILE, "w") as f:
        f.write(hash_val)
    upload_to_s3(LOCAL_HASH_FILE, "features/merged_jobs.hash")

    print("Merged dataset and hash uploaded to S3 in Parquet format.")


def check_if_new_data():
    try:
        download_from_s3("features/merged_jobs.hash", LOCAL_HASH_FILE)
        existing_hash = open(LOCAL_HASH_FILE).read()
        new_hash = file_md5(LOCAL_MERGED_CSV)
        if existing_hash == new_hash:
            print("Data unchanged.")
            return False
        else:
            print("Data changed.")
            return True
    except:
        print("No existing hash found. Assuming first run.")
        return True

def generate_and_cache_embeddings():
    df = pd.read_csv(LOCAL_MERGED_CSV)
    df["content"] = df["description"].astype(str) + " Tags: " + df["tags"].astype(str)
    df = df[df["content"].str.strip() != ""]
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df["content"].tolist(), batch_size=128, show_progress_bar=True)
    np.save(LOCAL_EMBEDDINGS, embeddings)
    df[["job_title", "company", "url"]].to_csv(LOCAL_METADATA, index=False)
    upload_to_s3(LOCAL_EMBEDDINGS, "features/embeddings.npy")
    upload_to_s3(LOCAL_METADATA, "features/metadata.csv")
    print("Embeddings and metadata uploaded to features/")

def build_faiss_index():
    embeddings = np.load(LOCAL_EMBEDDINGS)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, LOCAL_FAISS_INDEX)
    upload_to_s3(LOCAL_FAISS_INDEX, "models/faiss_index.bin")
    print("FAISS index uploaded to models/")
