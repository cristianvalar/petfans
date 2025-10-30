web: gunicorn petfans.wsgi:application --bind 0.0.0.0:${PORT:-8000}
release: python manage.py migrate --settings=petfans.settings.prod
