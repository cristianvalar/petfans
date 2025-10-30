web: gunicorn petfans.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate --settings=petfans.settings.prod
