FROM python:3.13.3-slim

ENV PYTHONDONTWRITEBYTECODE 1  # Evita que Python escriba archivos pyc en el disco
ENV PYTHONUNBUFFERED 1  # Asegura que la salida de Python se envíe directamente al terminal sin ser almacenada en búfer

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/