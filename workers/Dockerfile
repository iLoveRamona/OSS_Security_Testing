FROM python:3.9-slim as worker-base

WORKDIR /app
RUN apt update && apt install -y curl

COPY common/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY common ./common
