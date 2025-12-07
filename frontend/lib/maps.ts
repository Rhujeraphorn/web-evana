// ฟังก์ชันสร้างลิงก์ Google Maps สำหรับพิกัด/จุดแวะ
// - ถ้ามี stops หลายจุดจะใช้รูปแบบ /maps/dir/?origin&destination&waypoints
// - จำกัดจำนวนพิกัดที่ส่งไปที่ Maps ไว้ 10 จุดเพื่อไม่ให้ URL ยาวเกิน
import type { LatLng, RouteStop } from './types'

export function buildMapsLink(points: LatLng[], stops?: RouteStop[]): string {
  if (stops && stops.length >= 2) {
    const keep = stops.slice(0, 10)
    const origin = keep[0]
    const destination = keep[keep.length - 1]
    const middle = keep.slice(1, -1)
    const originPart = encodeURIComponent(`${origin.lat},${origin.lon}`)
    const destinationPart = encodeURIComponent(`${destination.lat},${destination.lon}`)
    let url = `https://www.google.com/maps/dir/?api=1&travelmode=driving&origin=${originPart}&destination=${destinationPart}`
    if (middle.length) {
      const waypointCoord = middle.map((p) => `${p.lat},${p.lon}`).join('|')
      url += `&waypoints=${encodeURIComponent(waypointCoord)}`
    }
    return url
  }
  if (!points.length) return 'https://www.google.com/maps'
  if (points.length === 1) {
    const p = points[0]
    return `https://www.google.com/maps/?q=${p.lat},${p.lon}`
  }
  // Limit to 10 points to avoid URL overflows
  const keep = points.slice(0, 10)
  const path = keep.map((p) => `${p.lat},${p.lon}`).join('/')
  return `https://www.google.com/maps/dir/${path}`
}

export function getBackendUrl() {
  // ซ้ำกับ lib/urls.ts สำหรับการใช้งานร่วม map utils
  return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
}
