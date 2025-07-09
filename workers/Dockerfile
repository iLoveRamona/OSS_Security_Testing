FROM python:3.9-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY common ./common

RUN pip install --no-cache-dir -r common/requirements.txt
