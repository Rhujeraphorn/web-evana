// หน้า list โรงแรมรายจังหวัด + แผนที่
import dynamic from 'next/dynamic'
import { ListAccordion } from '@/components/ListAccordion'
import { getBackendUrl } from '@/lib/urls'
const QuerySearch = dynamic(() => import('@/components/QuerySearch').then(m => m.QuerySearch), { ssr: false })
import { BackButton } from '@/components/BackButton'
import { toThaiProvince } from '@/lib/provinces'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function HotelsProvince({ params, searchParams }: { params: { province: string }; searchParams?: { q?: string } }) {
  const q = searchParams?.q?.trim()
  const url = new URL('/api/hotels', getBackendUrl())
  url.searchParams.set('province', params.province)
  if (q) url.searchParams.set('q', q)
  const res = await fetch(url, { next: { revalidate: 0 } })
  const items: { id: string; name_th: string; lat: number; lon: number }[] = res.ok ? await res.json() : []
  const center = items[0] || { lat: 18.82, lon: 98.96 }
  const countUrl = new URL('/api/hotels/count', getBackendUrl())
  countUrl.searchParams.set('province', params.province)
  if (q) countUrl.searchParams.set('q', q)
  const countRes = await fetch(countUrl, { next: { revalidate: 0 } })
  const total = countRes.ok ? (await countRes.json()).total ?? items.length : items.length
  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[32px] border border-slate-200/80 bg-white/90 p-6 shadow-xl shadow-slate-900/10">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-sky-50 via-white to-slate-100 opacity-90" />
          <div className="absolute -right-24 -top-20 h-64 w-64 rounded-full bg-sky-200/30 blur-3xl" />
          <div className="absolute -left-10 bottom-0 h-48 w-48 rounded-full bg-slate-900/5 blur-3xl" />
        </div>
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6">
          <div className="flex items-center gap-4">
            <BackButton fallbackHref={`/hotels`} />
            <div className="flex items-baseline gap-3">
              <p className="text-3xl font-bold leading-tight text-slate-900 md:text-4xl">จังหวัด</p>
              <h1 className="text-3xl font-bold leading-tight text-black md:text-4xl">
                {toThaiProvince(params.province)}
              </h1>
            </div>
          </div>
        </div>
        <div className="grid gap-4 lg:grid-cols-[1.3fr,0.7fr] lg:items-end">
          <p className="mx-auto max-w-3xl text-center text-lg leading-relaxed text-slate-600">
            โรงแรมและที่พักในจังหวัด {toThaiProvince(params.province)} เลือกจากแผนที่หรือรายการด้านข้าง แล้วกดดูรายละเอียดและนำทางได้ทันที
          </p>
          <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 shadow-sm shadow-slate-900/5">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">ทั้งหมด</div>
              <div className="text-2xl font-semibold text-slate-900">{total || '—'}</div>
              <div className="text-xs text-slate-500">ที่พักในแผนที่</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.25fr,0.95fr] lg:items-start">
        <div className="flex h-[70vh] flex-col overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-xl shadow-slate-900/10 ring-1 ring-slate-200/60 lg:h-[calc(100vh-220px)]">
          <div className="flex items-center justify-between px-5 py-3">
            <div>
              <p className="text-sm font-semibold text-slate-500">แผนที่ที่พัก</p>
              <p className="text-xs text-slate-500">กดปักหมุดเพื่อดูชื่อโรงแรม</p>
            </div>
            <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">Zoom / Tap</span>
          </div>
          <div className="flex-1 border-t border-slate-100">
            <MapBase
              center={{ lat: center.lat, lon: center.lon }}
              zoom={12}
              markers={items.map(i => ({ id: i.id, name: i.name_th, lat: i.lat, lon: i.lon }))}
              height="100%"
            />
          </div>
        </div>

        <div className="space-y-4 lg:max-h-[calc(100vh-220px)] lg:overflow-y-auto lg:pr-1">
          <div className="rounded-3xl border border-slate-200/80 bg-white/95 p-4 shadow-sm shadow-slate-900/5">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-600">ค้นหา</p>
            </div>
            <QuerySearch placeholder="พิมพ์ชื่อโรงแรม..." />
          </div>
          <div className="rounded-3xl border border-slate-200/80 bg-white/90 p-4 shadow-sm shadow-slate-900/10">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-700">รายการที่พัก ({total})</p>
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">Tap เพื่อดูรายละเอียด</span>
            </div>
            <ListAccordion
              items={items.map((m) => ({
                id: m.id,
                title: m.name_th,
                href: `/hotels/${params.province}/${m.id}`,
              }))}
            />
          </div>
        </div>
      </section>
    </div>
  )
}
