from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os

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
    recommend_jobs_task,
    check_if_new_data
)

# Helper to check FAISS existence
def check_faiss_exists():
    return os.path.exists("/opt/airflow/data/faiss_index.bin")

# Smart branching combining both conditions
def smart_branching():
    if check_if_new_data():
        return 'process_new_data'
    elif not check_faiss_exists():
        return 'rebuild_faiss_for_existing_data'
    else:
        return 'recommend_jobs_with_existing_data'

default_args = {
    'owner': 'jobmate_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'jobmate_full_pipeline_refactored',
    default_args=default_args,
    description='End-to-End Jobmate Pipeline with FAISS & Smart Caching + Fallback',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['jobmate', 'glassdoor', 'recommendation', 'faiss', 'cache-aware'],
) as dag:

    # Phase 1: Data ingestion & preprocessing
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

    # Phase 3: Smart branching
    task_smart_branching = BranchPythonOperator(
        task_id='smart_branching',
        python_callable=smart_branching,
    )

    # Path A: Data is new → rebuild everything
    task_prepare_new_data = EmptyOperator(task_id='process_new_data')

    task_generate_embeddings_new = PythonOperator(
        task_id='generate_and_cache_embeddings',
        python_callable=generate_and_cache_embeddings,
    )

    task_build_faiss_new = PythonOperator(
        task_id='build_faiss_index',
        python_callable=build_faiss_index,
    )

    task_recommend_after_new_data = PythonOperator(
        task_id='recommend_jobs_after_new_data',
        python_callable=recommend_jobs_task,
    )

    # Path B: Data is old but FAISS is missing → rebuild FAISS only
    task_build_faiss_for_existing = PythonOperator(
        task_id='rebuild_faiss_for_existing_data',
        python_callable=build_faiss_index,
    )

    task_recommend_after_faiss_rebuild = PythonOperator(
        task_id='recommend_jobs_after_faiss_rebuild',
        python_callable=recommend_jobs_task,
    )

    # Path C: Data old & FAISS exists → Recommend directly
    task_recommend_existing = PythonOperator(
        task_id='recommend_jobs_with_existing_data',
        python_callable=recommend_jobs_task,
    )

    # DAG dependencies flow
    (
        task_download_kaggle
        >> task_upload_raw_to_s3
        >> task_clean_glassdoor
        >> [task_scrape_remoteok, task_scrape_remotive, task_scrape_adzuna]
        >> task_merge_sources
        >> task_smart_branching
    )

    # Path A flow
    (
        task_smart_branching
        >> task_prepare_new_data
        >> task_generate_embeddings_new
        >> task_build_faiss_new
        >> task_recommend_after_new_data
    )

    # Path B flow
    (
        task_smart_branching
        >> task_build_faiss_for_existing
        >> task_recommend_after_faiss_rebuild
    )

    # Path C flow
    task_smart_branching >> task_recommend_existing
