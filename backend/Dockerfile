# Backend Dockerfile
# สร้างอิมเมจ FastAPI + ETL บน Python 3.11
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ติดตั้ง system deps ขั้นต่ำ (psycopg binary ไม่ต้องคอมไพล์)
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . ./

EXPOSE 8000

# ใช้ DATABASE_URL / CSV_BASE_DIR กำหนดตอน runtime
ENV PORT=8000

CMD ["sh","-c","python scripts/bootstrap.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
