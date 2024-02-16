FROM python:3.11-alpine
RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir celery

RUN apk add --no-cache bash

COPY . .
