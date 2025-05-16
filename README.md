
# JobMate Project - Setup Guide

## 1. Clone the Repository

Clone the entire repository into your local system:

```bash
git clone git@github.com:verdabatool/JobMate.git
```

## 2. Create and Activate a Virtual Environment

Create a virtual environment:

```bash
python3 -m venv _venv
```

Activate it:

```bash
source _venv/bin/activate
```

## 3. S3 Bucket Structure

Your S3 bucket should have the following structure:

```
your-bucket-name/
├── dynamic_updates/
├── features/
├── mlflow/
├── models/
├── processed/
└── raw/
```

## 4. Create Environment Variables File

In the project root directory, create a `.env` file with the following content:

```ini
# ---- Kaggle API ----
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-kaggle-key

# ---- AWS S3 ----
AWS_ACCESS_KEY_ID=your-access-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=your-default-region

# ---- S3 Bucket Settings ----
S3_BUCKET_NAME=your-bucket-name
RAW_S3_PREFIX=raw/
PROCESSED_S3_PREFIX=processed/
DYNAMIC_S3_PREFIX=dynamic_updates/
FEATURES_S3_PREFIX=features/

# ---- Adzuna Credentials ----
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# ---- MLflow ----
MLFLOW_TRACKING_URI=http://localhost:5000
```

## 5. Build Docker Containers

Run the following commands to build the Docker containers:

```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

## 6. Access Airflow

You can access the Airflow web interface at:

```
http://localhost:8081/login/
```

Login credentials:
- Username: `airflow`
- Password: `airflow`

Trigger the required DAG from the Airflow UI.

## 7. Run Backend Server

Navigate to the backend folder:

```bash
cd backend
python3 app.py
```

The backend server will be available at:

```
http://127.0.0.1:5005/jobs
```

## 8. Run Frontend Server

In a separate terminal, navigate to the `role-preference-match` folder and run:

```bash
cd role-preference-match
npm run dev
```

The frontend will be accessible at:

```
http://localhost:8083/
```

Lastly, the demo of this project is available at: 

```
https://drive.google.com/file/d/1tjeXs5CKekekfj5SzLTy2phwZMTVdVtI/view?usp=sharing
``` 
