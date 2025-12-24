from fastapi import APIRouter
import os
import requests
import time
import json
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api", tags=["chatbot"])

LANTA_URL = os.getenv("LANTA_CHAT_URL", "http://127.0.0.1:8001/chat")

# โฟลเดอร์/ไฟล์สำหรับเก็บประวัติ
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "evana_chat_history.jsonl"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_conversation(user_message: str, bot_reply: str, latency: float) -> None:
    """บันทึกประวัติการสนทนาแบบ JSONL ทีละบรรทัด"""
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_message": user_message,
        "bot_reply": bot_reply,
        "latency_sec": round(latency, 3),
    }
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        # กันพลาด: ไม่ให้การเขียน log ทำให้ API ล้ม
        print(f"[EVANA Backend][LOG ERROR] เขียน log ไม่สำเร็จ: {e}")


@router.post("/chat")
def chat(payload: dict):
    msg = payload.get("message", "")
    try:
        start = time.time()

        res = requests.post(LANTA_URL, json={"message": msg}, timeout=3600)
        res.raise_for_status()
        data = res.json()

        latency = time.time() - start
        reply_text = data.get("reply", "")

        # log เวลา + ข้อความ ลง console
        print(f"[EVANA Backend] Response time = {latency:.3f} sec | prompt = {msg[:60]}...")

        # log เป็นไฟล์ประวัติ
        log_conversation(msg, reply_text, latency)

        return data
    except Exception as e:
        err_msg = f"[EVANA ERROR] ตอนนี้เซิร์ฟเวอร์แชตบอตไม่ตอบสนอง: {e}"
        # กรณี error ก็ log ได้เหมือนกัน (ระบุว่าเป็น error)
        log_conversation(msg, err_msg, latency=0.0)
        return {"reply": err_msg}

# from fastapi import APIRouter
# import os
# import requests
# import time

# router = APIRouter()

# LANTA_URL = os.getenv("LANTA_CHAT_URL", "http://127.0.0.1:8001/chat")

# @router.post("/chat")
# def chat(payload: dict):
#     msg = payload.get("message", "")
#     try:
#         start = time.time()  # เริ่มจับเวลา

#         res = requests.post(LANTA_URL, json={"message": msg}, timeout=3600)
#         res.raise_for_status()

#         latency = time.time() - start  # จับเวลาเสร็จ

#         # 🟦 log ลง console ฝั่ง backend
#         print(f"[EVANA Backend] Response time = {latency:.3f} sec | prompt = {msg[:60]}...")

#         return res.json()
#     except Exception as e:
#         return {"reply": f"[EVANA ERROR] ตอนนี้เซิร์ฟเวอร์แชตบอตไม่ตอบสนอง: {e}"}


# from fastapi import APIRouter
# import os
# import requests

# router = APIRouter()

# LANTA_URL = os.getenv("LANTA_CHAT_URL", "http://127.0.0.1:8001/chat")

# @router.post("/chat")
# def chat(payload: dict):
#     msg = payload.get("message", "")
#     try:
#         res = requests.post(LANTA_URL, json={"message": msg}, timeout=3600)
#         res.raise_for_status()
#         return res.json()
#     except Exception as e:
#         return {"reply": f"[EVANA ERROR] ตอนนี้เซิร์ฟเวอร์แชตบอตไม่ตอบสนอง: {e}"}


# from fastapi import APIRouter
# import requests
# import os

# router = APIRouter()

# LANTA_URL = os.getenv("LANTA_CHAT_URL")  # เช่น http://127.0.0.1:8001/chat

# @router.post("/chat")
# def chat(payload: dict):
#     msg = payload.get("message", "")
#     res = requests.post(LANTA_URL, json={"message": msg})
#     return res.json()

# # from fastapi import APIRouter

# router = APIRouter()

# @router.post("/chat")
# def chat(payload: dict):
#     msg = payload.get("message", "")
#     # ทดสอบเฉย ๆ: ให้ backend ตอบกลับตรง ๆ
#     return {
#         "reply": f"[BACKEND OK] หนูได้รับข้อความจากนายท่านแล้วนะ: {msg}"
#     }
