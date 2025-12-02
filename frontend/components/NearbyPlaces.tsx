// คำนวณและแสดง POI ที่อยู่ใกล้พิกัดที่ให้มา (5 อันดับ)
import { POICard } from '@/components/POICard'
import { getBackendUrl } from '@/lib/urls'

type NearbyItem = {
  id: string
  name_th: string
  lat: number
  lon: number
  href: string
  label: 'แหล่งท่องเที่ยว' | 'ร้านอาหาร' | 'คาเฟ่'
  distanceKm: number
}

function haversineKm(a: { lat: number; lon: number }, b: { lat: number; lon: number }): number {
  const toRad = (x: number) => (x * Math.PI) / 180
  const R = 6371
  const dLat = toRad(b.lat - a.lat)
  const dLon = toRad(b.lon - a.lon)
  const lat1 = toRad(a.lat)
  const lat2 = toRad(b.lat)
  const s1 = Math.sin(dLat / 2)
  const s2 = Math.sin(dLon / 2)
  const c = s1 * s1 + Math.cos(lat1) * Math.cos(lat2) * s2 * s2
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(c)))
}

export async function NearbyPlaces({ lat, lon, province }: { lat: number; lon: number; province: string }) {
  const base = getBackendUrl()

  const [atRes, foodRes, cafeRes] = await Promise.all([
    fetch(new URL(`/api/attractions?province=${province}&limit=200`, base).toString(), { next: { revalidate: 0 } }),
    fetch(new URL(`/api/food?province=${province}&limit=200`, base).toString(), { next: { revalidate: 0 } }),
    fetch(new URL(`/api/cafes?province=${province}&limit=200`, base).toString(), { next: { revalidate: 0 } }),
  ])

  const attractions: any[] = atRes.ok ? await atRes.json() : []
  const foods: any[] = foodRes.ok ? await foodRes.json() : []
  const cafes: any[] = cafeRes.ok ? await cafeRes.json() : []

  const here = { lat, lon }

  const items: NearbyItem[] = [
    ...attractions.map((r) => ({
      id: r.id as string,
      name_th: (r.name_th || r.name_en || r.id) as string,
      lat: Number(r.lat),
      lon: Number(r.lon),
      href: `/attractions/${province}/${r.id}`,
      label: 'แหล่งท่องเที่ยว' as const,
      distanceKm: haversineKm(here, { lat: Number(r.lat), lon: Number(r.lon) }),
    })),
    ...foods.map((r) => ({
      id: r.id as string,
      name_th: (r.name_th || r.name_en || r.id) as string,
      lat: Number(r.lat),
      lon: Number(r.lon),
      href: `/food/${province}/${r.id}`,
      label: 'ร้านอาหาร' as const,
      distanceKm: haversineKm(here, { lat: Number(r.lat), lon: Number(r.lon) }),
    })),
    ...cafes.map((r) => ({
      id: r.id as string,
      name_th: (r.name_th || r.name_en || r.id) as string,
      lat: Number(r.lat),
      lon: Number(r.lon),
      href: `/cafes/${province}/${r.id}`,
      label: 'คาเฟ่' as const,
      distanceKm: haversineKm(here, { lat: Number(r.lat), lon: Number(r.lon) }),
    })),
  ]

  const top5 = items
    .filter((it) => Number.isFinite(it.lat) && Number.isFinite(it.lon))
    .sort((a, b) => a.distanceKm - b.distanceKm)
    .slice(0, 5)

  if (top5.length === 0) return null

  return (
    <section className="space-y-2">
      <h2 className="text-xl font-semibold">สถานที่ใกล้สถานี (5 แห่ง)</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {top5.map((p) => (
          <POICard
            key={`${p.label}-${p.id}`}
            title={p.name_th}
            subtitle={`${p.label} • ${p.distanceKm.toFixed(1)} กม.`}
            href={p.href}
          />
        ))}
      </div>
    </section>
  )
}
