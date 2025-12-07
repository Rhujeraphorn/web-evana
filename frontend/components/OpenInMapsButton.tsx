// ปุ่มเปิดเส้นทาง/จุดแวะใน Google Maps
// ใช้ buildMapsLink รวมพิกัด points หรือ stops แล้วเปิดแท็บใหม่
import { buildMapsLink } from '@/lib/maps'
import type { LatLng, RouteStop } from '@/lib/types'

export function OpenInMapsButton({ points = [], stops = [] }: { points?: LatLng[]; stops?: RouteStop[] }) {
  const href = buildMapsLink(points, stops)
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-2 rounded-2xl bg-brand-500 text-white px-4 py-2 hover:bg-brand-600 shadow-md"
    >
      เปิดบน Google Maps
    </a>
  )
}
