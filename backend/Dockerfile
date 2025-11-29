# Backend Dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (psycopg binary needs none; add build tools if compiling)
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . ./

EXPOSE 8000

# Use DB URL and CSV base via env at runtime
ENV PORT=8000

CMD ["sh","-c","python scripts/bootstrap.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
