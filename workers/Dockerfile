FROM python:3.9-slim as worker-base

WORKDIR /app
RUN apt update && apt install -y curl

COPY main.py .
COPY common ./common

RUN pip install --no-cache-dir -r common/requirements.txt
