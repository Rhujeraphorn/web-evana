# EVANA Project

ระบบวางแผนการเดินทางด้วยรถยนต์ไฟฟ้า สำหรับภาคเหนือตอนบนของประเทศไทย
พัฒนาด้วย Next.js และ FastAPI

## Overview

EVANA คือเว็บแอปสำหรับช่วยวางแผนการเดินทางด้วยรถยนต์ไฟฟ้าในพื้นที่ภาคเหนือ 4 จังหวัด
ได้แก่ เชียงใหม่ ลำพูน ลำปาง และแม่ฮ่องสอน ระบบออกแบบมาให้ใช้งานง่าย
สามารถแนะนำเส้นทาง แสดงจุดสนใจ (POIs) และตำแหน่งสถานีชาร์จรถยนต์ไฟฟ้า
ผ่านอินเทอร์เฟซที่ดูเข้าใจง่าย

## Features

- ค้นหาและแสดงทริปการเดินทาง พร้อมลำดับเหตุการณ์ (timeline) อย่างละเอียด
- แสดงข้อมูลสถานีชาร์จ แหล่งท่องเที่ยว ร้านอาหาร คาเฟ่ และที่พัก แยกตามจังหวัด
- แสดงผลเส้นทางบนแผนที่ และสามารถส่งต่อไปเปิดใน Google Maps ได้
- มีข้อมูลตัวอย่าง (demo data) ฝังอยู่ในระบบ ทำให้สามารถรันได้แม้ไม่เชื่อมต่อฐานข้อมูล

## Tech Stack

- Frontend: ใช้ Next.js (App Router), TypeScript, Tailwind CSS และ Leaflet สำหรับแผนที่
- Backend: ใช้ FastAPI และ SQLAlchemy สำหรับจัดการ API และข้อมูล
- Database: ใช้ PostgreSQL (ไม่จำเป็น หากต้องการรันแบบ demo)

## Project Structure

โครงสร้างหลักของโปรเจกต์แบ่งออกเป็นโฟลเดอร์สำคัญดังนี้

- `backend/` สำหรับฝั่งเซิร์ฟเวอร์ (FastAPI) รวม API, schema และข้อมูลตัวอย่าง
- `frontend/` สำหรับฝั่งเว็บแอป (Next.js – App Router)
- `data/` สำหรับเก็บข้อมูลเส้นทางและไฟล์ตัวอย่าง
- `nginx/` สำหรับไฟล์ตั้งค่า reverse proxy

โครงสร้างไฟล์ที่แสดงเป็นเวอร์ชันย่อ โดยตัดไฟล์ที่ใช้เฉพาะเครื่องพัฒนาออก เช่น
`.venv`, `node_modules`, `.next`, `__pycache__` และ `.vscode`

## Getting Started

### Prerequisites

ก่อนเริ่มใช้งาน ต้องติดตั้งเครื่องมือพื้นฐานดังนี้

- Node.js เวอร์ชัน 18 ขึ้นไป
- Python เวอร์ชัน 3.10 ขึ้นไป
- PostgreSQL เวอร์ชัน 14 ขึ้นไป (ไม่บังคับ หากใช้โหมด demo)

### Directory Tree (Condensed)
```
.
|-- backend/
|   |-- app/
|   |   |-- routers/
|   |   |   |-- agents.py
|   |   |   |-- chargers.py
|   |   |   |-- pois.py
|   |   |   |-- routes.py
|   |   |   `-- search.py
|   |   |-- config.py
|   |   |-- db.py
|   |   |-- demo_data.py
|   |   |-- main.py
|   |   |-- models.py
|   |   `-- schemas.py
|   |-- etl/
|   |   |-- import_activities.py
|   |   |-- import_agents.py
|   |   |-- import_cafes.py
|   |   |-- import_chargers.py
|   |   |-- import_foods.py
|   |   |-- import_hotels.py
|   |   |-- import_pois.py
|   |   `-- import_provinces.py
|   |-- scripts/
|   |   |-- bootstrap.py
|   |   `-- init_db.py
|   |-- sql/
|   |   |-- ddl.sql
|   |   |-- seed_demo.sql
|   |   `-- seed_prod_template.sql
|   |-- Dockerfile
|   `-- requirements.txt
|-- data/
|   `-- routes/
|       |-- Chiangmai_routes_all.geojson
|       |-- Chiangmai_routes_all.json
|       |-- Lampang_routes_all.geojson
|       |-- Lampang_routes_all.json
|       |-- Lamphun_routes.geojson
|       |-- Lamphun_routes.json
|       |-- Maehongson_all.geojson
|       `-- Maehongson_all.json
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- public/
|   |-- styles/
|   |-- Dockerfile
|   |-- next.config.mjs
|   |-- nginx.conf
|   |-- package.json
|   |-- postcss.config.js
|   |-- tailwind.config.ts
|   `-- tsconfig.json
|-- nginx/
|   `-- default.conf
|-- .env
|-- .gitignore
|-- docker-compose.yml
|-- LICENSE
`-- README.md
```

_Note: This tree omits local/dev artifacts such as `.venv`, `node_modules`, `.next`, `__pycache__`, and `.vscode`._

### Install Dependencies

ฝั่ง Backend จะสร้าง virtual environment และติดตั้งไลบรารีที่จำเป็น
ฝั่ง Frontend จะติดตั้งแพ็กเกจผ่าน npm ตามปกติ

### Run (Development)

สามารถรัน backend และ frontend แยกกันในโหมดพัฒนา
จากนั้นเปิดเว็บผ่านเบราว์เซอร์ที่ `http://localhost:3000`

### Demo Data

ระบบมีข้อมูลตัวอย่างของเส้นทางและ POIs ฝังอยู่ในไฟล์ `backend/app/demo_data.py`
ทำให้สามารถเรียกใช้งาน API ได้ แม้ยังไม่ได้เชื่อมต่อฐานข้อมูล PostgreSQL

หากต้องการใช้งานร่วมกับฐานข้อมูลจริง สามารถ seed ข้อมูลตัวอย่างลง PostgreSQL ได้ด้วยไฟล์
`backend/sql/seed_demo.sql`

