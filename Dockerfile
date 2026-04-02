FROM python:3.13.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /code/

# Collect static files at build time using a placeholder key
RUN SECRET_KEY=build-placeholder python manage.py collectstatic --noinput --settings=petfans.settings.prod

RUN chmod +x /code/entrypoint.sh

EXPOSE 8000

CMD ["/code/entrypoint.sh"]
