// ฟังก์ชันสร้างลิงก์ Google Maps สำหรับพิกัด/จุดแวะ
// - ถ้ามี stops หลายจุดจะใช้รูปแบบ /maps/dir/?origin&destination&waypoints
// - จำกัดจำนวนพิกัดที่ส่งไปที่ Maps ไว้ 10 จุดเพื่อไม่ให้ URL ยาวเกิน
import type { LatLng, RouteStop } from './types'

export function buildMapsLink(points: LatLng[], stops?: RouteStop[]): string {
  const isValidPoint = (p: LatLng) =>
    Number.isFinite(p.lat) &&
    Number.isFinite(p.lon) &&
    !(Math.abs(p.lat) < 1e-6 && Math.abs(p.lon) < 1e-6)

  const cleanStops = (stops || []).filter(isValidPoint)
  const cleanPoints = (points || []).filter(isValidPoint)
  const formatStop = (p: RouteStop) => {
    const label = (p.label || '').trim()
    return label || `${p.lat},${p.lon}`
  }

  if (cleanStops.length >= 2) {
    const keep = cleanStops.slice(0, 10)
    const origin = keep[0]
    const destination = keep[keep.length - 1]
    const middle = keep.slice(1, -1)
    const originPart = encodeURIComponent(formatStop(origin))
    const destinationPart = encodeURIComponent(formatStop(destination))
    let url = `https://www.google.com/maps/dir/?api=1&travelmode=driving&origin=${originPart}&destination=${destinationPart}`
    if (middle.length) {
      const waypointCoord = middle.map((p) => formatStop(p)).join('|')
      url += `&waypoints=${encodeURIComponent(waypointCoord)}`
    }
    return url
  }
  if (!cleanPoints.length) return 'https://www.google.com/maps'
  if (cleanPoints.length === 1) {
    const p = cleanPoints[0]
    return `https://www.google.com/maps/?q=${p.lat},${p.lon}`
  }
  // Limit to 10 points to avoid URL overflows
  const keep = cleanPoints.slice(0, 10)
  const path = keep.map((p) => `${p.lat},${p.lon}`).join('/')
  return `https://www.google.com/maps/dir/${path}`
}

export function getBackendUrl() {
  // ซ้ำกับ lib/urls.ts สำหรับการใช้งานร่วม map utils
  return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
}
