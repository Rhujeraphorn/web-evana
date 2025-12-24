# Inference server for EVANA chatbot (GPU)
# ใช้ base image ที่มี CUDA runtime ติดตั้งมาแล้ว
FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY evana_infer_server_local.py .

# ค่า default; สามารถ override ผ่าน docker-compose หรือ ENV
ENV BASE_MODEL_DIR=/models/mistral-nemo-instruct-2407 \
    ADAPTER_DIR=/models/evana-mistral-sft-general-20251113-0626 \
    PORT=8001

EXPOSE 8001

CMD ["python", "evana_infer_server_local.py"]
