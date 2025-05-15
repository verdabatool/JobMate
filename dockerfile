FROM apache/airflow:2.7.2-python3.9

USER root

# Ensure CA certificates & secure SSL layer inside Docker
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Set working dir
ENV AIRFLOW_HOME=/opt/airflow
WORKDIR $AIRFLOW_HOME

COPY requirements.txt .

# Upgrade pip, reinstall numpy, enforce versions
RUN pip install --upgrade pip && \
    pip install --force-reinstall --no-cache-dir numpy==1.23.5 && \
    pip install --no-cache-dir -r requirements.txt
