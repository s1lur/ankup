FROM python:3.7-slim

RUN apt-get update && apt-get -y install libpq-dev gcc

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

WORKDIR /app
