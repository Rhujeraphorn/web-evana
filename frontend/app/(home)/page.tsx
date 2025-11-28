import { SearchBar } from '@/components/SearchBar'
import { ProvinceGrid } from '@/components/ProvinceGrid'
import type { AgentCard } from '@/lib/types'
import { getBackendUrl } from '@/lib/urls'
import { toThaiProvince } from '@/lib/provinces'

export default async function Home({ searchParams }: { searchParams?: { q?: string; province?: string } }) {
  const q = searchParams?.q?.trim()
  const province = searchParams?.province?.trim()
  let results: AgentCard[] = []
  if (q) {
    const url = new URL('/api/agents/search', getBackendUrl())
    url.searchParams.set('q', q)
    if (province) url.searchParams.set('province', province)
    const res = await fetch(url.toString(), { next: { revalidate: 0 } })
    if (res.ok) results = await res.json()
  }

  return (
    <div className="space-y-12">
      <section className="grid items-center gap-10 lg:grid-cols-[1.05fr,0.95fr]">
        <div className="space-y-6">
          
          <div className="space-y-4">
            <h1 className="text-4xl font-semibold leading-[1.1] text-slate-900 sm:text-5xl">
              แนะนำทริปท่องเที่ยว ในภาคเหนือ   <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 via-cyan-600 to-slate-900"></span>
            </h1>
            <p className="max-w-2xl text-lg leading-relaxed text-slate-600">
              รวมสถานีชาร์จ ร้านอาหาร คาเฟ่ โรงแรม และจุดเช็คอิน ในจังหวัดแม่ฮ่องสอน เชียงใหม่ ลำพูน ลำปาง
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <a
              href="/chargers"
              className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
            >
              ดูสถานีชาร์จใกล้ฉัน
            </a>
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 -left-6 rounded-[30px] bg-gradient-to-br from-sky-50 via-white to-slate-100 blur-0 shadow-2xl shadow-slate-900/5" />
          <div className="relative space-y-4 overflow-visible rounded-[30px] border border-slate-200/80 bg-white/90 p-6 shadow-xl shadow-slate-900/10 backdrop-blur">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-700">ค้นหาทริปที่แนะนำ</p>
              </div>
            </div>
            <SearchBar />
          </div>
        </div>
      </section>

      {q && (
        <section className="space-y-4 rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-lg shadow-slate-900/10">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-500">ผลการค้นหา</p>
              <h2 className="text-xl font-semibold text-slate-900">"{q}" {province ? `• ${province}` : ''}</h2>
            </div>
            <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">พบ {results.length} รายการ</div>
          </div>
          {results.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-3 text-slate-600">
              ยังไม่เจอผลลัพธ์ ลองค้นหาคำอื่น หรือเลือกจังหวัดที่ใกล้ที่สุด ✨
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {results.map((a) => (
                <a
                  key={a.id}
                  href={`/trip/${a.id}?day=1`}
                  className="group relative flex h-full flex-col justify-between overflow-hidden rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-900/10"
                >
                  <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-sky-500 to-cyan-500 opacity-70" />
                  <div className="flex items-center justify-between gap-3">
                    <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-800">
                      {toThaiProvince(a.province_slug)}
                    </div>
                    <div className="text-xs font-semibold text-slate-500">{a.style} • 1 วัน</div>
                  </div>
                  <div className="mt-3 text-lg font-semibold text-slate-900">{a.title}</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {a.poi_tags.slice(0, 5).map((t) => (
                      <span key={t} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                        {t}
                      </span>
                    ))}
                  </div>
                  <div className="mt-4 flex items-center gap-2 text-sm font-semibold text-sky-700">
                    ดูรายละเอียดเต็ม
                    <span aria-hidden>→</span>
                  </div>
                </a>
              ))}
            </div>
          )}
        </section>
      )}

      <section className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">เลือกจังหวัดที่อยากไป</h2>
          </div>
        </div>
        <ProvinceGrid />
      </section>

      <section className="grid gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { href: '/cafes', title: 'คาเฟ่', desc: 'คัดร้านวิวดี ให้แวะระหว่างทาง' },
          { href: '/hotels', title: 'ที่พัก', desc: 'โรงแรมที่มีมาตรฐาน' },
          { href: '/attractions', title: 'โลเคชั่นห้ามพลาด', desc: 'จุดชมวิว ถนนสวย ชนะทุกกล้อง ช่วยเติมความทรงจำ' },
        ].map((item) => (
          <a
            key={item.href}
            href={item.href}
            className="group relative overflow-hidden rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-900/10"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-sky-50/70 via-transparent to-white opacity-0 transition group-hover:opacity-100" />
            <div className="relative space-y-2">
              <div className="text-lg font-semibold text-slate-900">{item.title}</div>
              <p className="text-sm leading-relaxed text-slate-600">{item.desc}</p>
              <div className="pt-2 text-sm font-semibold text-sky-700">เปิดดูทันที →</div>
            </div>
          </a>
        ))}
      </section>
    </div>
  )
}
