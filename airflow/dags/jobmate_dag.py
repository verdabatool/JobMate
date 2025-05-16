from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
import boto3
import os

# Import your business logic
from backend.jobmate_full_pipeline_refactored import (
    check_glassdoor_data,
    check_if_scraping_needed,
    download_from_kaggle,
    upload_raw_to_s3,
    clean_glassdoor_data_and_upload_to_s3,
    scrape_remoteok,
    scrape_remotive,
    scrape_adzuna,
    merge_all_sources_and_save,
    generate_and_cache_embeddings,
    build_faiss_index,
    recommend_jobs_task
)
# ---- DAG Definition ----
default_args = {
    'owner': 'jobmate_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'jobmate_daily_pipeline',
    default_args=default_args,
    description='Robust Jobmate Daily Pipeline with Smart Caching & Scheduled Scraping',
    schedule_interval='0 10 * * *',  # Every day at 10 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['jobmate', 'glassdoor', 'faiss', 'recommendations'],
) as dag:

    # Check Glassdoor Data
    task_check_glassdoor = ShortCircuitOperator(
        task_id='check_glassdoor_data_and_cleaned',
        python_callable=check_glassdoor_data,
    )

    task_download_kaggle = PythonOperator(
        task_id='download_from_kaggle',
        python_callable=download_from_kaggle,
    )

    task_upload_raw = PythonOperator(
        task_id='upload_raw_to_s3',
        python_callable=upload_raw_to_s3,
    )

    task_clean_glassdoor = PythonOperator(
        task_id='clean_glassdoor_data_and_upload_to_s3',
        python_callable=clean_glassdoor_data_and_upload_to_s3,
    )

    # Scraping Condition Check
    task_check_scraping = ShortCircuitOperator(
        task_id='check_if_scraping_needed',
        python_callable=check_if_scraping_needed,
    )

    task_scrape_remoteok = PythonOperator(
        task_id='scrape_remoteok',
        python_callable=scrape_remoteok,
    )

    task_scrape_remotive = PythonOperator(
        task_id='scrape_remotive',
        python_callable=scrape_remotive,
    )

    task_scrape_adzuna = PythonOperator(
        task_id='scrape_adzuna',
        python_callable=scrape_adzuna,
    )

    task_merge_sources = PythonOperator(
        task_id='merge_all_sources_and_save',
        python_callable=merge_all_sources_and_save,
    )

    task_generate_embeddings = PythonOperator(
        task_id='generate_and_cache_embeddings',
        python_callable=generate_and_cache_embeddings,
        execution_timeout=timedelta(hours=6)
    )

    task_build_faiss = PythonOperator(
        task_id='build_faiss_index',
        python_callable=build_faiss_index,
    )

    # Always run recommendations
    task_recommend_jobs = PythonOperator(
        task_id='recommend_jobs_task',
        python_callable=recommend_jobs_task,
    )

    # ---- Dependencies ----

    # Glassdoor data path
    task_check_glassdoor >> task_download_kaggle >> task_upload_raw >> task_clean_glassdoor

    # Scraping & Rebuild path
    task_check_scraping >> [task_scrape_remoteok, task_scrape_remotive, task_scrape_adzuna] >> task_merge_sources >> task_generate_embeddings >> task_build_faiss >> task_recommend_jobs

    # Normal recommendation path
    task_check_scraping >> task_recommend_jobs