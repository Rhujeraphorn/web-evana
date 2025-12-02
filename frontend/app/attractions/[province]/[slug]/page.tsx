// หน้าแสดงรายละเอียดสถานที่ท่องเที่ยวรายจุด + ปุ่มเปิดแผนที่
import dynamic from 'next/dynamic'
import { OpenInMapsButton } from '@/components/OpenInMapsButton'
import { BackButton } from '@/components/BackButton'
import { getBackendUrl } from '@/lib/urls'
import { toThaiProvince } from '@/lib/provinces'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function AttractionDetail({ params }: { params: { province: string; slug: string } }) {
  const res = await fetch(new URL(`/api/attractions/${params.province}/${params.slug}`, getBackendUrl()), { next: { revalidate: 0 } })
  const d = res.ok ? await res.json() : { name_th: decodeURIComponent(params.slug), lat: 18.804, lon: 98.943 }
  const safe = <T,>(val: T, fallback: string = '-') => {
    if (val === null || val === undefined) return fallback
    if (typeof val === 'string' && val.trim().toLowerCase() === 'nan') return fallback
    if (typeof val === 'string' && val.trim() === '') return fallback
    return val
  }
  const lat = d.lat
  const lon = d.lon
  return (
    <div className="space-y-6">
      <div>
        <BackButton fallbackHref={`/attractions/${params.province}`} />
      </div>
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">{safe(d.name_th)}</h1>
        {d.address_th || d.province_th || d.district_th || d.subdistrict_th ? (
          <p className="text-slate-500">
            {safe(d.address_th) !== '-' ? (
              <>ที่อยู่: {safe(d.address_th)}</>
            ) : (
              <>
                {safe(d.province_th) !== '-' ? `จังหวัด${d.province_th}` : `จังหวัด${toThaiProvince(params.province)}`}
                {safe(d.district_th) !== '-' ? ` · อำเภอ${d.district_th}` : ''}
                {safe(d.subdistrict_th) !== '-' ? ` · ตำบล${d.subdistrict_th}` : ''}
              </>
            )}
          </p>
        ) : null}
      </div>
      <div className="rounded-2xl border border-slate-200 overflow-hidden">
        <MapBase center={{ lat, lon }} zoom={13} markers={[{ id: params.slug, name: d.name_th, lat, lon }]} />
      </div>
      <div className="flex gap-2">
        <OpenInMapsButton points={[{ lat, lon }]} />
        {d.website ? (
          <a href={d.website} target="_blank" className="inline-flex items-center rounded-xl border px-3 py-1.5 text-sm hover:bg-slate-50">เว็บไซต์</a>
        ) : null}
        {d.facebook ? (
          <a href={d.facebook} target="_blank" className="inline-flex items-center rounded-xl border px-3 py-1.5 text-sm hover:bg-slate-50">Facebook</a>
        ) : null}
        {d.instagram ? (
          <a href={d.instagram} target="_blank" className="inline-flex items-center rounded-xl border px-3 py-1.5 text-sm hover:bg-slate-50">Instagram</a>
        ) : null}
        {d.tiktok ? (
          <a href={d.tiktok} target="_blank" className="inline-flex items-center rounded-xl border px-3 py-1.5 text-sm hover:bg-slate-50">TikTok</a>
        ) : null}
      </div>
      {(d.tel || d.email || d.address_road || d.postcode || d.address_th) ? (
        <div className="rounded-2xl border p-4 space-y-2">
          <h2 className="font-semibold">ข้อมูลติดต่อ</h2>
          {d.address_th || d.address_road ? (
            <p>
              ที่อยู่: {safe(d.address_road, '')}{d.address_road && d.address_th ? ', ' : ''}{safe(d.address_th, '')}{d.postcode ? ` ${safe(d.postcode)}` : ''}
            </p>
          ) : null}
          {d.tel ? <p>โทร: {safe(d.tel)}</p> : null}
          {d.email ? <p>อีเมล: {safe(d.email)}</p> : null}
          {d.start_end ? <p>เวลาเปิดทำการ: {safe(d.start_end)}</p> : null}
        </div>
      ) : null}
      {(d.hilight || d.reward || d.suitable_duration || d.market_limitation || d.market_chance || d.traveler_pre) ? (
        <div className="rounded-2xl border p-4 grid md:grid-cols-2 gap-4">
          {d.hilight ? <div><div className="font-semibold mb-1">ไฮไลต์</div><p className="text-slate-700 whitespace-pre-wrap">{safe(d.hilight)}</p></div> : null}
          {d.reward ? <div><div className="font-semibold mb-1">รางวัล/มาตรฐาน</div><p className="text-slate-700 whitespace-pre-wrap">{safe(d.reward)}</p></div> : null}
          {d.suitable_duration ? <div><div className="font-semibold mb-1">ช่วงเวลาที่เหมาะสม</div><p className="text-slate-700 whitespace-pre-wrap">{safe(d.suitable_duration)}</p></div> : null}
          {d.market_limitation ? <div><div className="font-semibold mb-1">ข้อจำกัด</div><p className="text-slate-700 whitespace-pre-wrap">{safe(d.market_limitation)}</p></div> : null}
          {d.market_chance ? <div><div className="font-semibold mb-1">โอกาสตลาด</div><p className="text-slate-700 whitespace-pre-wrap">{safe(d.market_chance)}</p></div> : null}
          {d.traveler_pre ? <div><div className="font-semibold mb-1">นักท่องเที่ยวเป้าหมาย</div><p className="text-slate-700 whitespace-pre-wrap">{safe(d.traveler_pre)}</p></div> : null}
        </div>
      ) : null}
      {d.detail_th ? (
        <div className="prose max-w-none">
          <div className="font-semibold mb-2">รายละเอียด</div>
          <div dangerouslySetInnerHTML={{ __html: d.detail_th }} />
        </div>
      ) : null}
    </div>
  )
}
