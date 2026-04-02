web: gunicorn petfans.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --settings=petfans.settings.prod && python manage.py populate_breeds --settings=petfans.settings.prod
