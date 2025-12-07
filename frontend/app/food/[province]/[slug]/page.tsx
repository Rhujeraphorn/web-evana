// หน้าแสดงรายละเอียดร้านอาหารรายจุด
// - ดึงข้อมูลร้านอาหารตาม province/slug พร้อมแสดงเวลาเปิดปิดถ้ามี
// - ปักหมุดบนแผนที่และให้ปุ่มเปิด Google Maps สำหรับนำทาง
import dynamic from 'next/dynamic'
import { OpenInMapsButton } from '@/components/OpenInMapsButton'
import { BackButton } from '@/components/BackButton'
import { getBackendUrl } from '@/lib/urls'
import { toThaiProvince } from '@/lib/provinces'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function FoodDetail({ params }: { params: { province: string; slug: string } }) {
  const res = await fetch(new URL(`/api/food/${params.province}/${params.slug}`, getBackendUrl()), { next: { revalidate: 0 } })
  const d = res.ok ? await res.json() : { name_th: decodeURIComponent(params.slug), lat: 18.79, lon: 98.99 }
  const lat = d.lat
  const lon = d.lon
  return (
    <div className="space-y-4">
      <div>
        <BackButton fallbackHref={`/food/${params.province}`} />
      </div>
      <h1 className="text-2xl font-semibold">{d.name_th}</h1>
      {d.open_hours && (d.open_hours.open || d.open_hours.close) ? (
        <p className="text-slate-700">เวลาเปิดปิด: {(d.open_hours.open || '').trim()}{d.open_hours.open && d.open_hours.close ? ' - ' : ''}{(d.open_hours.close || '').trim()}</p>
      ) : null}
      <p className="text-slate-500">จังหวัด: {toThaiProvince(params.province)}</p>
      <div className="rounded-2xl border border-slate-200 overflow-hidden">
        <MapBase center={{ lat, lon }} zoom={14} markers={[{ id: params.slug, name: d.name_th, lat, lon }]} />
      </div>
      <div className="flex items-center gap-2">
        <OpenInMapsButton points={[{ lat, lon }]} />
      </div>
    </div>
  )
}
