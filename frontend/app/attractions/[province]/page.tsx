// หน้า list แหล่งท่องเที่ยวรายจังหวัด
// - ใช้ dynamic import โหลด MapBase และ QuerySearch เพื่อเลี่ยง SSR-dependent libs
// - ดึงข้อมูลและตัวนับแยกหมวด (ธรรมชาติ/วัฒนธรรม/กิจกรรม) ตาม province และ query ค้นหา
// - สร้าง marker สำหรับแผนที่ และรายการ accordion ที่ลิงก์ไปยังหน้ารายละเอียด
import dynamic from 'next/dynamic'
import { ListAccordion } from '@/components/ListAccordion'
const QuerySearch = dynamic(() => import('@/components/QuerySearch').then(m => m.QuerySearch), { ssr: false })
import { BackButton } from '@/components/BackButton'
import { getBackendUrl } from '@/lib/urls'
import { toThaiProvince } from '@/lib/provinces'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function AttractionsProvince({ params, searchParams }: { params: { province: string }; searchParams?: { q?: string } }) {
  const q = searchParams?.q?.trim()
  const url = new URL('/api/attractions', getBackendUrl())
  url.searchParams.set('province', params.province)
  if (q) url.searchParams.set('q', q)
  const res = await fetch(url, { next: { revalidate: 0 } })
  const items: { id: string; name_th: string; lat: number; lon: number; kind?: string; province_th?: string; address_th?: string }[] = res.ok ? await res.json() : []

  const countUrl = new URL('/api/attractions/count', getBackendUrl())
  countUrl.searchParams.set('province', params.province)
  if (q) countUrl.searchParams.set('q', q)
  const countRes = await fetch(countUrl, { next: { revalidate: 0 } })
  const counts = countRes.ok ? await countRes.json() : { total: items.length, cta: 0, avt: 0, nta: 0 }

  const center = items[0] || { lat: 18.804, lon: 98.943 }
  const total = counts.total ?? items.length
  const cultureCount = counts.cta ?? items.filter((i) => i.kind === 'CTA').length
  const natureCount = counts.nta ?? items.filter((i) => i.kind === 'NTA').length
  const activityCount = counts.avt ?? items.filter((i) => i.kind === 'AVT').length
  const provinceName = items[0]?.province_th ? `จังหวัด${items[0]?.province_th}` : `จังหวัด${toThaiProvince(params.province)}`

  return (
    <div className="space-y-8 px-3 md:px-6 lg:px-10">
      <section className="relative overflow-hidden rounded-[32px] border border-slate-200/80 bg-white/95 p-6 shadow-xl shadow-slate-900/10">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-sky-50 via-white to-slate-100 opacity-90" />
          <div className="absolute -right-24 -top-16 h-64 w-64 rounded-full bg-sky-200/30 blur-3xl" />
          <div className="absolute -left-16 bottom-0 h-48 w-48 rounded-full bg-slate-900/5 blur-3xl" />
        </div>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <BackButton fallbackHref={`/attractions`} />
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">สถานที่ท่องเที่ยว</p>
              <h1 className="text-3xl font-bold leading-tight text-slate-900 md:text-4xl">{provinceName}</h1>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 min-w-[320px] sm:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-left shadow-sm shadow-slate-900/5">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">ทั้งหมด</div>
              <div className="text-2xl font-semibold text-slate-900">{total || '—'}</div>
              <div className="text-xs text-slate-500">จุดเช็คอิน</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-emerald-500 to-slate-900 px-4 py-3 text-white shadow-lg shadow-emerald-500/30">
              <div className="text-xs font-semibold uppercase tracking-wide text-white/70">ธรรมชาติ</div>
              <div className="text-2xl font-semibold">{natureCount}</div>
              <div className="text-xs text-white/80">น้ำตก ภูเขา</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-left shadow-sm shadow-slate-900/5">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">วัฒนธรรม</div>
              <div className="text-2xl font-semibold text-slate-900">{cultureCount}</div>
              <div className="text-xs text-slate-500">วัด/ประเพณี</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-sky-500 to-cyan-700 px-4 py-3 text-left text-white shadow-lg shadow-sky-500/30">
              <div className="text-xs font-semibold uppercase tracking-wide text-white/80">กิจกรรม</div>
              <div className="text-2xl font-semibold">{activityCount}</div>
              <div className="text-xs text-white/80">แอดเวนเจอร์/สนุกสนาน</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.45fr,1fr] lg:items-start">
        <div className="flex h-[78vh] flex-col overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-xl shadow-slate-900/10 ring-1 ring-slate-200/60 lg:h-[calc(100vh-200px)]">
          <div className="flex items-center justify-between px-5 py-3">
            <div>
              <p className="text-sm font-semibold text-slate-500">แผนที่สถานที่ท่องเที่ยว</p>
              <p className="text-xs text-slate-500">กดปักหมุดเพื่อดูชื่อและนำทาง</p>
            </div>
            <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">Zoom / Tap</span>
          </div>
          <div className="flex-1 border-t border-slate-100">
            <MapBase
              center={{ lat: center.lat, lon: center.lon }}
              zoom={11}
              markers={items.map(i => ({ id: i.id, name: i.name_th, lat: i.lat, lon: i.lon }))}
              height="100%"
            />
          </div>
        </div>

        <div className="space-y-4 lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto lg:pr-1">
          <div className="rounded-3xl border border-slate-200/80 bg-white/95 p-4 shadow-sm shadow-slate-900/5">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-600">ค้นหาและกรอง</p>
            </div>
            <QuerySearch placeholder="พิมพ์ชื่อสถานที่…" />
          </div>
          <div className="rounded-3xl border border-slate-200/80 bg-white/90 p-4 shadow-sm shadow-slate-900/10">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-700">รายการ ({total})</p>
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">Tap เพื่อดูรายละเอียด</span>
            </div>
            <ListAccordion
              items={items.map((m) => ({
                id: m.id,
                title: m.name_th,
                subtitle: `${m.kind === 'CTA' ? 'วัฒนธรรม' : m.kind === 'AVT' ? 'กิจกรรม' : 'ธรรมชาติ'}${m.address_th ? ` · ${m.address_th}` : ''}`,
                href: `/attractions/${params.province}/${m.id}`,
              }))}
            />
          </div>
        </div>
      </section>
    </div>
  )
}
