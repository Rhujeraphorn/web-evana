// คืน URL backend จาก env (fallback localhost)
export function getBackendUrl() {
  return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
}
