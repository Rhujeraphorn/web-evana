// หน้าแสดงรายละเอียดคาเฟ่รายจุด + แผนที่นำทาง
import dynamic from 'next/dynamic'
import { OpenInMapsButton } from '@/components/OpenInMapsButton'
import { BackButton } from '@/components/BackButton'
import { getBackendUrl } from '@/lib/urls'
import { toThaiProvince } from '@/lib/provinces'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function CafeDetail({ params }: { params: { province: string; slug: string } }) {
  const res = await fetch(new URL(`/api/cafes/${params.province}/${params.slug}`, getBackendUrl()), { next: { revalidate: 0 } })
  const d = res.ok ? await res.json() : { name_th: decodeURIComponent(params.slug), lat: 18.81, lon: 98.98 }
  const lat = d.lat
  const lon = d.lon
  return (
    <div className="space-y-4">
      <div>
        <BackButton fallbackHref={`/cafes/${params.province}`} />
      </div>
      <h1 className="text-2xl font-semibold">{d.name_th}</h1>
      <p className="text-slate-500">จังหวัด: {toThaiProvince(params.province)}</p>
      <div className="rounded-2xl border border-slate-200 overflow-hidden">
        <MapBase center={{ lat, lon }} zoom={14} markers={[{ id: params.slug, name: d.name_th, lat, lon }]} />
      </div>
      <OpenInMapsButton points={[{ lat, lon }]} />
    </div>
  )
}
