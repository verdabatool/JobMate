# Stop and remove old containers & volumes
docker-compose down -v

# Remove dangling images to avoid cache conflicts
docker image prune -a

# Build fresh
docker-compose build

# Initialize DB
docker-compose run --rm jobmate-cacheaware-airflow-webserver airflow db init

# Create user
docker-compose run --rm jobmate-cacheaware-airflow-webserver airflow users create \
    --username airflow --password airflow \
    --firstname Air --lastname Flow --role Admin \
    --email airflow@example.com

# Up everything
docker-compose up
