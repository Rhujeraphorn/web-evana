// หน้าแสดงรายละเอียดสถานีชาร์จ
// - ดึงข้อมูลสถานีจาก backend ตาม province และ id
// - ใช้แผนที่ Leaflet แบบ dynamic import เพื่อไม่บล็อก SSR
// - ดึง POI หมวดต่าง ๆ ในจังหวัดเดียวกัน แล้วคำนวณระยะทางจากสถานีด้วยสูตร Haversine
// - แนะนำ POI ใกล้สุด 5 แห่งต่อหมวด และวาง marker รวมบนแผนที่เดียว
import dynamic from 'next/dynamic'
import { OpenInMapsButton } from '@/components/OpenInMapsButton'
import { BackButton } from '@/components/BackButton'
import { getBackendUrl } from '@/lib/urls'
import { toThaiProvince } from '@/lib/provinces'
import { POICard } from '@/components/POICard'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function ChargerDetail({ params }: { params: { province: string; id: string } }) {
  const res = await fetch(new URL(`/api/chargers/${params.province}/${params.id}`, getBackendUrl()), { next: { revalidate: 0 } })
  const d = res.ok ? await res.json() : { name: params.id, type: 'DC', kw: 60, lat: 18.79, lon: 98.99 }
  const lat = d.lat
  const lon = d.lon
  const base = getBackendUrl()
  // Fetch POIs in the same province
  const [atRes, foodRes, cafeRes] = await Promise.all([
    fetch(new URL(`/api/attractions?province=${params.province}&limit=200`, base).toString(), { next: { revalidate: 0 } }),
    fetch(new URL(`/api/food?province=${params.province}&limit=200`, base).toString(), { next: { revalidate: 0 } }),
    fetch(new URL(`/api/cafes?province=${params.province}&limit=200`, base).toString(), { next: { revalidate: 0 } }),
  ])
  const attractions: any[] = atRes.ok ? await atRes.json() : []
  const foods: any[] = foodRes.ok ? await foodRes.json() : []
  const cafes: any[] = cafeRes.ok ? await cafeRes.json() : []

  const here = { lat, lon }
  // ฟังก์ชันคำนวณระยะทางแบบ Haversine (เหมือนจุดอื่น แต่ยกมาภายในไฟล์เพื่อหลีกเลี่ยงการ import เพิ่ม)
  const toKm = (a: { lat:number; lon:number }, b: { lat:number; lon:number }) => {
    const toRad = (x:number) => (x*Math.PI)/180
    const R = 6371
    const dLat = toRad(b.lat - a.lat)
    const dLon = toRad(b.lon - a.lon)
    const lat1 = toRad(a.lat)
    const lat2 = toRad(b.lat)
    const s1 = Math.sin(dLat/2)
    const s2 = Math.sin(dLon/2)
    const c = s1*s1 + Math.cos(lat1)*Math.cos(lat2)*s2*s2
    return 2*R*Math.asin(Math.min(1, Math.sqrt(c)))
  }

  const topAttractions = attractions
    .map((r) => ({ id: String(r.id), name_th: r.name_th || r.name_en || r.id, lat: Number(r.lat), lon: Number(r.lon), dist: toKm(here, { lat: Number(r.lat), lon: Number(r.lon) }) }))
    .filter((r) => Number.isFinite(r.lat) && Number.isFinite(r.lon))
    .sort((a, b) => a.dist - b.dist)
    .slice(0, 5)

  const topFoods = foods
    .map((r) => ({ id: String(r.id), name_th: r.name_th || r.name_en || r.id, lat: Number(r.lat), lon: Number(r.lon), dist: toKm(here, { lat: Number(r.lat), lon: Number(r.lon) }) }))
    .filter((r) => Number.isFinite(r.lat) && Number.isFinite(r.lon))
    .sort((a, b) => a.dist - b.dist)
    .slice(0, 5)

  const topCafes = cafes
    .map((r) => ({ id: String(r.id), name_th: r.name_th || r.name_en || r.id, lat: Number(r.lat), lon: Number(r.lon), dist: toKm(here, { lat: Number(r.lat), lon: Number(r.lon) }) }))
    .filter((r) => Number.isFinite(r.lat) && Number.isFinite(r.lon))
    .sort((a, b) => a.dist - b.dist)
    .slice(0, 5)

  const nearbyMarkers = [
    { id: params.id, name: d.name, lat, lon },
    ...topAttractions.map((p) => ({ id: `att-${p.id}`, name: `แหล่งท่องเที่ยว: ${p.name_th} (${p.dist.toFixed(1)} กม.)`, lat: p.lat, lon: p.lon })),
    ...topFoods.map((p) => ({ id: `food-${p.id}`, name: `ร้านอาหาร: ${p.name_th} (${p.dist.toFixed(1)} กม.)`, lat: p.lat, lon: p.lon })),
    ...topCafes.map((p) => ({ id: `cafe-${p.id}`, name: `คาเฟ่: ${p.name_th} (${p.dist.toFixed(1)} กม.)`, lat: p.lat, lon: p.lon })),
  ]
  return (
    <div className="space-y-4">
      <div>
        <BackButton fallbackHref={`/chargers/${params.province}`} />
      </div>
      <h1 className="text-2xl font-semibold">สถานี: {d.name}</h1>
      <p className="text-slate-500">ประเภท: {d.type} • {d.kw ?? ''} kW • จังหวัด: {toThaiProvince(params.province)}</p>
      <div className="rounded-2xl border border-slate-200 overflow-hidden">
        <MapBase center={{ lat, lon }} zoom={14} markers={nearbyMarkers} />
      </div>
      <OpenInMapsButton points={[{ lat, lon }]} />
      {topAttractions.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">แนะนำสถานที่ท่องเที่ยวใกล้สถานี (5 แห่ง)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topAttractions.map((p) => (
              <POICard key={`att-card-${p.id}`} title={p.name_th} subtitle={`แหล่งท่องเที่ยว • ${p.dist.toFixed(1)} กม.`} href={`/attractions/${params.province}/${p.id}`} />
            ))}
          </div>
        </section>
      )}
      {topFoods.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">แนะนำร้านอาหารใกล้สถานี (5 แห่ง)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topFoods.map((p) => (
              <POICard key={`food-card-${p.id}`} title={p.name_th} subtitle={`ร้านอาหาร • ${p.dist.toFixed(1)} กม.`} href={`/food/${params.province}/${p.id}`} />
            ))}
          </div>
        </section>
      )}
      {topCafes.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">แนะนำคาเฟ่ใกล้สถานี (5 แห่ง)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topCafes.map((p) => (
              <POICard key={`cafe-card-${p.id}`} title={p.name_th} subtitle={`คาเฟ่ • ${p.dist.toFixed(1)} กม.`} href={`/cafes/${params.province}/${p.id}`} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
