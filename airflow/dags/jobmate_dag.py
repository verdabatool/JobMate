from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

from backend.jobmate_full_pipeline_refactored import (
    download_from_kaggle,
    upload_raw_to_s3,
    clean_glassdoor_data_and_upload_to_s3,
    scrape_remoteok,
    scrape_remotive,
    scrape_adzuna,
    merge_all_sources_and_save,
    generate_and_cache_embeddings,
    build_faiss_index,
    check_if_new_data
)

default_args = {
    'owner': 'jobmate_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'jobmate_full_pipeline_refactored',
    default_args=default_args,
    description='End-to-End Jobmate Pipeline with FAISS & Smart Caching',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['jobmate', 'glassdoor', 'recommendation', 'faiss', 'cache-aware'],
) as dag:

    # Phase 1: Data Ingestion and Preprocessing
    task_download_kaggle = PythonOperator(
        task_id='download_from_kaggle',
        python_callable=download_from_kaggle,
    )

    task_upload_raw_to_s3 = PythonOperator(
        task_id='upload_raw_to_s3',
        python_callable=upload_raw_to_s3,
    )

    task_clean_glassdoor = PythonOperator(
        task_id='clean_glassdoor_data_and_upload_to_s3',
        python_callable=clean_glassdoor_data_and_upload_to_s3,
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

    # Phase 2: Merge all sources
    task_merge_sources = PythonOperator(
        task_id='merge_all_sources_and_save',
        python_callable=merge_all_sources_and_save,
    )

    # Phase 3: Smart change detection via BranchPythonOperator
    def _check_if_new_data():
        return 'generate_and_cache_embeddings' if check_if_new_data() else 'end_of_pipeline'

    task_check_if_new_data = BranchPythonOperator(
        task_id='check_if_new_data',
        python_callable=_check_if_new_data,
    )

    # Phase 4: Embeddings and FAISS Index build if new data
    task_generate_embeddings = PythonOperator(
        task_id='generate_and_cache_embeddings',
        python_callable=generate_and_cache_embeddings,
    )

    task_build_faiss_index = PythonOperator(
        task_id='build_faiss_index',
        python_callable=build_faiss_index,
    )

    # Phase 5: End pipeline if no changes detected
    task_end_of_pipeline = PythonOperator(
        task_id='end_of_pipeline',
        python_callable=lambda: print("✅ No new data detected. Pipeline finished gracefully."),
    )

    # DAG Dependencies flow
    (
        task_download_kaggle
        >> task_upload_raw_to_s3
        >> task_clean_glassdoor
        >> [task_scrape_remoteok, task_scrape_remotive, task_scrape_adzuna]
        >> task_merge_sources
        >> task_check_if_new_data
    )

    task_check_if_new_data >> task_generate_embeddings >> task_build_faiss_index
    task_check_if_new_data >> task_end_of_pipeline

