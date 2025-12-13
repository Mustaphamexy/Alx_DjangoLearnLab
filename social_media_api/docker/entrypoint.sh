#!/bin/bash
# docker/entrypoint.sh

set -e

# Wait for database to be ready
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done
    
    echo "PostgreSQL started"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || true
fi

# Start server
echo "Starting server..."
exec gunicorn social_media_api.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info