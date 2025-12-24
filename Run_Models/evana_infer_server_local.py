# evana_infer_server_local.py
# เซิร์ฟเวอร์ inference โหมดตัวอย่าง: ใช้ชุดข้อมูลถาม-ตอบที่เตรียมไว้ แทนการยิงเข้าโมเดลจริง
# โค้ดโหลดโมเดลเดิมเก็บไว้ด้านล่างในตัวแปร LEGACY_MODEL_IMPLEMENTATION (คอมเมนต์/ซ่อน ไม่ได้รัน)

import json
from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

DATA_FILE = Path(__file__).parent / "sample_qa_dataset.json"

app = FastAPI(title="EVANA Local Chat Inference (Sample Dataset)")


class ChatRequest(BaseModel):
    message: str


def normalize_text(text: str) -> str:
    """ตัดช่องว่างซ้ำ ๆ และปรับเป็น lower-case เพื่อจับคู่คำถามที่เตรียมไว้"""
    return " ".join(text.strip().split()).casefold()


def load_qa_lookup(path: Path) -> Dict[str, str]:
    """โหลดชุดถาม-ตอบตัวอย่างเป็น dict เพื่อให้ตอบกลับเร็ว ๆ"""
    if not path.exists():
        print(f"[EVANA DEMO] ไม่พบไฟล์ชุดคำถามตัวอย่าง: {path}")
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as exc:
        print(f"[EVANA DEMO] โหลดไฟล์ตัวอย่างไม่สำเร็จ: {exc}")
        return {}

    lookup: Dict[str, str] = {}
    for item in items:
        question = normalize_text(str(item.get("question", "")))
        answer = item.get("answer", "").strip()
        if question and answer:
            lookup[question] = answer

    print(f"[EVANA DEMO] โหลดชุดคำถามตัวอย่างแล้ว {len(lookup)} รายการจาก {path.name}")
    return lookup


QA_LOOKUP = load_qa_lookup(DATA_FILE)
DEMO_HINT = (
    'ลองถามว่า "เล่าเส้นทางจากตัวเมืองลำปางไปยังวัดพระธาตุลำปางหลวงให้หน่อย" '
    "เพื่อดูตัวอย่างคำตอบที่เตรียมไว้"
)


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    normalized = normalize_text(req.message)
    answer = QA_LOOKUP.get(normalized)

    if answer:
        return {"reply": answer}

    fallback = (
        "นี่คือ EVANA Chatbot Demo กรุณาถามคำถามตามตัวอย่างที่มีอยู่ในไฟล์ sample_qa_dataset.json "
        "ตอนนี้ยังไม่มีคำตอบสำหรับคำถามนี้\n"
        f"{DEMO_HINT}"
    )
    return {"reply": fallback}


# -----------------------------------------------------------------------------
# Legacy model-based server preserved for reference (disabled in demo mode)
LEGACY_MODEL_IMPLEMENTATION = r"""
# evana_infer_server_local.py
# เซิร์ฟเวอร์ inference ที่รันบนเครื่อง
# โหลด base Mistral-Nemo-Instruct-2407 แบบ 4-bit + LoRA general 4 จังหวัด แล้วเปิด API /chat

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch
import sys
import time
import os

# ====== PATH โมเดลบนเครื่อง ======
DEFAULT_BASE_MODEL_DIR = r"C:\Users\Nervously\evana\models\mistral-nemo-instruct-2407"
DEFAULT_ADAPTER_DIR    = r"C:\Users\Nervously\evana\models\evana-mistral-sft-general-20251113-0626"

BASE_MODEL_DIR = os.getenv("BASE_MODEL_DIR", DEFAULT_BASE_MODEL_DIR)
ADAPTER_DIR    = os.getenv("ADAPTER_DIR", DEFAULT_ADAPTER_DIR)

if not os.path.exists(BASE_MODEL_DIR):
    print(f"❌ ไม่พบ BASE_MODEL_DIR: {BASE_MODEL_DIR}")
    sys.exit(1)

if not os.path.exists(ADAPTER_DIR):
    print(f"❌ ไม่พบ ADAPTER_DIR: {ADAPTER_DIR}")
    sys.exit(1)

app = FastAPI(title="EVANA Local Chat Inference")

class ChatRequest(BaseModel):
    message: str

# ====== เช็ก GPU ก่อนเลย กัน OOM ======
if not torch.cuda.is_available():
    print("❌ ไม่พบ GPU หรือ PyTorch ไม่รองรับ CUDA")
    print("โมเดล Mistral-Nemo-Instruct-2407 (8B) ใหญ่เกินกว่าจะรันบน CPU 32GB ได้อย่างปลอดภัย")
    print("โปรดเช็กว่าติดตั้ง torch เวอร์ชัน CUDA แล้ว และลองใหม่อีกครั้ง")
    sys.exit(1)

device = torch.device("cuda")
print(f"✅ ใช้ GPU: {torch.cuda.get_device_name(0)}")

print("🔹 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL_DIR,
    local_files_only=True,
    trust_remote_code=True,
    fix_mistral_regex=True,   # แก้ issue regex ตาม warning
)

if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

# ====== ตั้งค่า 4-bit quantization ด้วย bitsandbytes ======
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

print("🔹 Loading base model (Mistral-Nemo-Instruct-2407) แบบ 4-bit ทั้งก้อนบน GPU ...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_DIR,
    quantization_config=bnb_config,
    device_map={"": 0},       # ทั้งโมเดลลง GPU 0 ตัวเดียว
    local_files_only=True,
)

print("🔹 Loading LoRA adapter (general 4 provinces)...")
# ตรงนี้ไม่ส่ง device_map / offload_dir อะไรเลย ปล่อยให้ตาม base_model
model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_DIR,
    local_files_only=True,
)
model.eval()

if model.config.pad_token_id is None:
    model.config.pad_token_id = tokenizer.pad_token_id

print("✅ Model ready.")


def generate_answer(message: str) -> str:
    \"\"\"ฟังก์ชันยิงเข้าโมเดลแล้วดึงเฉพาะคำตอบของ EVANA ออกมา\"\"\"

    system_prompt = (
        "คุณคือ EVANA Chatbot ผู้ช่วยแนะนำการท่องเที่ยวภาคเหนือของไทยด้วยรถยนต์ไฟฟ้า "
        "ตอบแบบกระชับ อ่านง่าย เป็นกันเอง และอิงข้อมูลสถานที่จริงให้มากที่สุด "
        "ถ้าข้อมูลไม่แน่ใจให้เตือนผู้ใช้ให้เช็กข้อมูลล่าสุดอีกครั้ง"
    )

    prompt = f"{system_prompt}\n\nผู้ใช้: {message}\nEVANA:"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    ).to(device)

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=220,
            do_sample=True,
            temperature=0.25,
            top_p=0.9,
            repetition_penalty=1.15,
            no_repeat_ngram_size=4,
            pad_token_id=tokenizer.pad_token_id,
        )

    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    if "EVANA:" in full_text:
        reply = full_text.split("EVANA:")[-1].strip()
    else:
        reply = full_text[len(prompt):].strip() or full_text.strip()

    return reply


# @app.post("/chat")
# def chat_endpoint(req: ChatRequest):
#     \"\"\"จุดรับข้อความจาก backend (รับ message เดียวแบบที่ backend ส่งมา)\"\"\"
#     answer = generate_answer(req.message)
#     return {"reply": answer}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    \"\"\"จุดรับข้อความจาก backend (รับ message เดียวแบบที่ backend ส่งมา)\"\"\"
    start = time.time()   # เริ่มจับเวลา
    answer = generate_answer(req.message)
    latency = time.time() - start
    # 🟦 พิมพ์เวลาใน console แบบสวย ๆ
    print(f"[EVANA][Inference] ใช้เวลา {latency:.3f} วินาที  |  prompt = {req.message[:50]}...")
    return {"reply": answer}

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting EVANA inference server on 0.0.0.0:8001 ...")
    uvicorn.run("evana_infer_server_local:app", host="0.0.0.0", port=8001, reload=False)
"""


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting EVANA sample inference server on 0.0.0.0:8001 ...")
    uvicorn.run("evana_infer_server_local:app", host="0.0.0.0", port=8001, reload=False)
