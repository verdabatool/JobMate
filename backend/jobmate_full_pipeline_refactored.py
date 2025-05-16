import os
import pandas as pd
import numpy as np
import boto3
import hashlib
import faiss
import requests
import mlflow
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
from kaggle.api.kaggle_api_extended import KaggleApi


# ----------------- Config & Paths -----------------
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
LOCAL_MERGED_PARQUET = f"{LOCAL_DATA_FOLDER}/merged_jobs.parquet"
LOCAL_HASH_FILE = f"{LOCAL_DATA_FOLDER}/merged_jobs.hash"
LOCAL_EMBEDDINGS = f"{LOCAL_DATA_FOLDER}/embeddings.npy"
LOCAL_METADATA = f"{LOCAL_DATA_FOLDER}/metadata.csv"
LOCAL_FAISS_INDEX = f"{LOCAL_DATA_FOLDER}/faiss_index.bin"

RAW_KEY = "raw/glassdoor_reviews.csv"
CLEANED_KEY = "processed/glassdoor_cleaned.parquet"
SCRAPED_KEY_PREFIX = "dynamic_updates/remoteok/remoteok.parquet"  # Example, we'll use last_modified


def s3_client():
    return boto3.client('s3',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=AWS_REGION)


def check_glassdoor_data():
    s3 = s3_client()
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=RAW_KEY)
        s3.head_object(Bucket=S3_BUCKET, Key=CLEANED_KEY)
        print("✅ Both raw & cleaned Glassdoor data present.")
        return False  # Skip Kaggle tasks
    except:
        print("⚠️ Glassdoor raw or cleaned data missing. Will download & clean.")
        return True  # Proceed to download & clean

def check_if_scraping_needed():
    s3 = s3_client()
    try:
        obj = s3.head_object(Bucket=S3_BUCKET, Key=SCRAPED_KEY_PREFIX)
        last_modified = obj['LastModified']
        days_since = (datetime.utcnow() - last_modified.replace(tzinfo=None)).days
        print(f"✅ Last scraping was {days_since} days ago.")
        if days_since >= 15:
            print("⚠️ More than 15 days since last scraping. Will scrape & update data.")
            return True  # Scrape new
        else:
            print("✅ Scraping still fresh (<15 days). Will use existing data.")
            return False  # Skip scraping, use existing data
    except:
        print("⚠️ Scraping files not found. Will scrape & update data.")
        return True  # First run case

def upload_to_s3(local_file, s3_key, cleanup=False):
    s3 = s3_client()
    try:
        s3.upload_file(local_file, S3_BUCKET, s3_key)
        print(f"✅ Uploaded {local_file} to s3://{S3_BUCKET}/{s3_key}")
        if cleanup:
            os.remove(local_file)
            print(f"🗑 Local file {local_file} deleted after upload.")
    except Exception as e:
        raise Exception(f"❌ Error uploading {local_file} to S3: {e}")

def download_from_s3(s3_key, local_file):
    s3_client().download_file(S3_BUCKET, s3_key, local_file)
    print(f"✅ Downloaded {s3_key} to {local_file}")

def file_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# ----------------- Ingestion & Preprocessing -----------------
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
        df = df.head(100)  # For testing, remove this line in production

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
        df = df.head(100)  # For testing, remove this line in production
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


def scrape_and_upload(source_name, api_url, records_fn):
    response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    jobs = records_fn(response)
    df = pd.DataFrame(jobs)
    local_file = f"{LOCAL_DATA_FOLDER}/{source_name}.parquet"
    df.to_parquet(local_file, index=False)
    upload_to_s3(local_file, f"{DYNAMIC_SOURCES_PREFIX}{source_name}/{source_name}.parquet")

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
    path = f"{LOCAL_DATA_FOLDER}/remoteok.parquet"
    df.to_parquet(path, index=False)
    upload_to_s3(path, f"{DYNAMIC_SOURCES_PREFIX}remoteok/remoteok.parquet", cleanup=True)

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
    path = f"{LOCAL_DATA_FOLDER}/remotive.parquet"
    df.to_parquet(path, index=False)
    upload_to_s3(path, f"{DYNAMIC_SOURCES_PREFIX}remotive/remotive.parquet", cleanup=True)

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
    path = f"{LOCAL_DATA_FOLDER}/adzuna.parquet"
    df.to_parquet(path, index=False)

    upload_to_s3(path, f"{DYNAMIC_SOURCES_PREFIX}adzuna/adzuna.parquet", cleanup=True)

def ensure_file_or_download(file_path, s3_key):
    if not os.path.isfile(file_path):
        print(f"[Info] {file_path} not found locally. Attempting to download from S3...")
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION)
        try:
            s3.download_file(S3_BUCKET, s3_key, file_path)
            print(f"[Info] Downloaded {file_path} from S3.")
        except Exception as e:
            raise FileNotFoundError(f"Failed to download {file_path} from S3: {e}")

# ----------------- Merging & Hash Checking -----------------
def merge_all_sources_and_save():


    mlflow.set_tracking_uri("http://mlflow-server:5000")  
    mlflow.set_experiment("glassdoor_jobmate_recommender")

    # ✅ Ensure files locally or download from S3
    ensure_file_or_download(LOCAL_CLEAN_FILE, f"{PROCESSED_S3_PREFIX}glassdoor_cleaned.parquet")
    ensure_file_or_download(f"{LOCAL_DATA_FOLDER}/remoteok.parquet", f"{DYNAMIC_SOURCES_PREFIX}remoteok/remoteok.parquet")
    ensure_file_or_download(f"{LOCAL_DATA_FOLDER}/remotive.parquet", f"{DYNAMIC_SOURCES_PREFIX}remotive/remotive.parquet")
    ensure_file_or_download(f"{LOCAL_DATA_FOLDER}/adzuna.parquet", f"{DYNAMIC_SOURCES_PREFIX}adzuna/adzuna.parquet")

    df_glassdoor = pd.read_parquet(LOCAL_CLEAN_FILE)
    df_glassdoor = df_glassdoor.rename(columns={"firm": "company"})
    df_glassdoor['description'] = df_glassdoor['content']
    df_glassdoor['tags'] = ""
    df_glassdoor['url'] = ""
    df_glassdoor['source'] = "glassdoor"
    df_glassdoor = df_glassdoor[["job_title", "company", "description", "tags", "url", "source"]]

    df_remoteok = pd.read_parquet(f"{LOCAL_DATA_FOLDER}/remoteok.parquet")
    df_remotive = pd.read_parquet(f"{LOCAL_DATA_FOLDER}/remotive.parquet")
    df_adzuna = pd.read_parquet(f"{LOCAL_DATA_FOLDER}/adzuna.parquet")

    df_merged = pd.concat([df_glassdoor, df_remoteok, df_remotive, df_adzuna], ignore_index=True)
    df_merged.to_parquet(LOCAL_MERGED_PARQUET, index=False)
    upload_to_s3(LOCAL_MERGED_PARQUET, "features/merged_jobs.parquet")

    hash_val = file_md5(LOCAL_MERGED_PARQUET)
    with open(LOCAL_HASH_FILE, "w") as f:
        f.write(hash_val)
    upload_to_s3(LOCAL_HASH_FILE, "features/merged_jobs.hash")

def check_if_new_data():
    s3 = s3_client()
    try:
        # Check if hash exists and compare
        download_from_s3("features/merged_jobs.hash", LOCAL_HASH_FILE)
        existing_hash = open(LOCAL_HASH_FILE).read()
        new_hash = file_md5(LOCAL_MERGED_PARQUET)
        if existing_hash != new_hash:
            print("✅ Data has changed, will process new data.")
            return True  # Data changed
        else:
            # Extra check: Does FAISS index exist?
            s3.head_object(Bucket=S3_BUCKET, Key="models/faiss_index.bin")
            print("✅ Data unchanged and FAISS index exists, will recommend using existing.")
            return False  # Data unchanged and index exists
    except s3.exceptions.ClientError as e:
        # Missing either hash or FAISS index triggers full rebuild
        print("⚠️ Hash or FAISS index missing in S3. Will process new data.")
        return True

# ----------------- Embeddings & FAISS -----------------
def generate_and_cache_embeddings():
    df = pd.read_parquet(LOCAL_MERGED_PARQUET)
    df["content"] = df["description"].astype(str) + " Tags: " + df["tags"].astype(str)
    df = df[df["content"].str.strip() != ""]
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df["content"].tolist(), batch_size=64, show_progress_bar=True)
    np.save(LOCAL_EMBEDDINGS, embeddings)
    df[["job_title", "company", "url"]].to_csv(LOCAL_METADATA, index=False)
    upload_to_s3(LOCAL_EMBEDDINGS, "features/embeddings.npy")
    upload_to_s3(LOCAL_METADATA, "features/metadata.csv")

def build_faiss_index():
    embeddings = np.load(LOCAL_EMBEDDINGS)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, LOCAL_FAISS_INDEX)
    upload_to_s3(LOCAL_FAISS_INDEX, "models/faiss_index.bin")

# ----------------- Recommendation -----------------
def load_faiss_and_metadata():
    index = faiss.read_index(LOCAL_FAISS_INDEX)
    metadata = pd.read_csv(LOCAL_METADATA)
    return index, metadata

def recommend_jobs_faiss(user_query, top_n=5):
    index, metadata = load_faiss_and_metadata()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    user_embedding = model.encode([user_query])
    faiss.normalize_L2(user_embedding)
    D, I = index.search(user_embedding, top_n)
    recommendations = metadata.iloc[I[0]].copy()
    recommendations['score'] = D[0]
    return recommendations

def recommend_jobs_task():
    user_query = "Software Engineer remote flexible work"
    recommendations = recommend_jobs_faiss(user_query)
    print("✅ Recommended Jobs:\n", recommendations[["job_title", "company", "url", "score"]])

