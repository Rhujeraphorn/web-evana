// คืน URL backend จาก env (fallback localhost)
// ใช้ตัวแปร NEXT_PUBLIC_BACKEND_URL เพื่อให้ทั้ง client/server อ้างที่เดียวกัน
export function getBackendUrl() {
  return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
}
