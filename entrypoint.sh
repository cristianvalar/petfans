#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --settings=petfans.settings.prod

echo "Populating breeds..."
python manage.py populate_breeds --settings=petfans.settings.prod

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput --settings=petfans.settings.prod || echo "Superuser already exists, skipping."
fi

echo "Starting server..."
exec gunicorn petfans.wsgi:application --bind 0.0.0.0:${PORT:-8000}
