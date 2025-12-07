// หน้าเลือกจังหวัดเพื่อดูสถานีชาร์จ EV
// - แสดงบัตรสี่จังหวัดภาคเหนือที่ระบบมีข้อมูล
// - ลิงก์ไปยัง /chargers/[province] เพื่อดูแผนที่รวมในจังหวัดนั้น
import { BackButton } from '@/components/BackButton'

export default function ChargersIndex() {
  const provinces = [
    { slug: 'chiang-mai', name: 'เชียงใหม่' },
    { slug: 'lampang', name: 'ลำปาง' },
    { slug: 'lamphun', name: 'ลำพูน' },
    { slug: 'mae-hong-son', name: 'แม่ฮ่องสอน' },
  ]

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-r from-slate-50 via-white to-emerald-50 p-6">
        <div className="absolute inset-y-0 right-0 w-1/3 bg-[radial-gradient(circle_at_center,_rgba(16,185,129,0.2),_transparent_60%)]" />
        <BackButton href="/" force />
        <div className="mt-4 space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">สถานีชาร์จ</h1>
          <p className="text-slate-500">เลือกจังหวัดที่ต้องการเพื่อดูสถานีและแผนที่รวม</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {provinces.map((p) => (
          <a
            key={p.slug}
            href={`/chargers/${p.slug}`}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
          >
            <div className="relative">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-emerald-500 text-white shadow-md shadow-sky-500/30">
                <span className="text-lg font-semibold">EV</span>
              </div>
              <div className="absolute right-0 top-0 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                คลิกดูสถานี
              </div>
            </div>
            <div className="mt-6 space-y-1">
              <div className="text-lg font-semibold text-slate-900">{p.name}</div>
              <div className="text-sm text-slate-600">ดูแผนที่รวมสถานีชาร์จในจังหวัดนี้</div>
            </div>
            <div className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-sky-700">
              เปิดดูแผนที่ <span aria-hidden>→</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
