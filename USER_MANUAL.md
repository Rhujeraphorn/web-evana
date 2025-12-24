# EVANA Project - User Manual (การติดตั้งแบบละเอียด)
เอกสารนี้อธิบายการติดตั้งและการรันแบบ Development บน Windows ด้วย PowerShell

## 1) สิ่งที่ต้องมีในเครื่องเบื้องต้น
- Node.js 18+ (มาพร้อม npm)
- Python 3.10+
- PostgreSQL 14+ (ไม่บังคับ หากต้องการใช้ฐานข้อมูลจริง)
- Git (ไม่บังคับ หากต้องการดึงซอร์สด้วย git)

ตรวจสอบเวอร์ชันที่ติดตั้ง:
```powershell
node -v
npm -v
python --version
```

## 2) เปิดโปรเจกต์
```powershell
cd D:\403wdc02\EVANA-Project
```

## 3) ติดตั้ง Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

ถ้า Activate.ps1 รันไม่ได้ :
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4) ติดตั้ง Frontend
เปิด PowerShell อีกหน้าต่างหนึ่ง หรือกลับไปที่โฟลเดอร์หลักก่อน:
```powershell
cd D:\403wdc02\EVANA-Project\frontend
npm install
```

## 5) รัน Backend (Development)
ให้รันในหน้าต่างที่ใช้ Backend:
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## 6) รัน Frontend (Development)
ให้รันในอีกหน้าต่างหนึ่งสำหรับ Frontend:
```powershell
cd frontend
npm run dev
```

## 7) เข้าใช้งานระบบ
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 8) หยุดการทำงาน
กด `Ctrl+C` ในแต่ละหน้าต่างเพื่อหยุดเซิร์ฟเวอร์

## 9) ข้อมูลตัวอย่าง (Demo Data)
ระบบมี demo data ใน `backend/app/demo_data.py` ใช้งานได้แม้ไม่มี PostgreSQL

หากต้องการใช้ฐานข้อมูลจริง สามารถ seed ได้ด้วย:
```powershell
psql -U postgres -d evjourney -f backend/sql/seed_demo.sql
```

## 10) ปัญหาที่พบบ่อย
- `pip` หรือ `npm` หาไม่เจอ: ตรวจสอบ PATH หรือใช้ `python -m pip install -r requirements.txt`
