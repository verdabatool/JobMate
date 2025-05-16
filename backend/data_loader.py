import pandas as pd
import s3fs
import boto3
import os
from dotenv import load_dotenv
load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

# Now pass them into boto3
session = boto3.Session(
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

s3_fs = s3fs.S3FileSystem(session=session)

S3_PATHS = [
    "s3://glassdoor-de-final-project/dynamic_updates/adzuna/adzuna.parquet",
    "s3://glassdoor-de-final-project/dynamic_updates/remoteok/remoteok.parquet",
    "s3://glassdoor-de-final-project/dynamic_updates/remotive/remotive.parquet"
]

COLUMNS = ["job_title", "company", "description", "tags", "url", "source"]

def load_all_jobs():
    dfs = [pd.read_parquet(path, engine="pyarrow") for path in S3_PATHS]

    for df in dfs:
        print("Original columns:", df.columns)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        print("After filling missing cols:", df[COLUMNS].head())

    df_merged = pd.concat([df[COLUMNS] for df in dfs], ignore_index=True)
    print("Merged shape:", df_merged.shape)
    return df_merged[:300]
