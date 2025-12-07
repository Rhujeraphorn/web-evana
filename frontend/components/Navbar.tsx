// แถบเมนูนำทางหลักของเว็บ
// - ตรึงด้านบน (sticky) พร้อม blur background และลิงก์ไปแต่ละหมวด
export function Navbar() {
  return (
    <nav className="sticky top-0 z-20 backdrop-blur-lg">
      <div className="max-w-6xl mx-auto px-4 pt-4">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-full border border-white/70 bg-white/90 px-4 py-3 shadow-lg shadow-slate-900/5 ring-1 ring-slate-200/80">
          <a href="/" className="flex items-center gap-3 text-lg font-semibold tracking-tight text-slate-900">
            <span className="grid h-10 w-10 place-items-center rounded-full bg-gradient-to-br from-sky-500 to-slate-900 text-white shadow-md shadow-slate-900/10">EV</span>
            <div>
              <div className="leading-tight">EVANA</div>
              <div className="text-xs font-medium uppercase text-slate-500">Northern routes</div>
            </div>
          </a>

          <div className="flex flex-1 flex-wrap justify-end gap-2 text-sm font-medium sm:text-base">
            <a href="/chargers" className="rounded-full border border-slate-200 bg-white px-4 py-2 text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">สถานีชาร์จ</a>
            <a href="/attractions" className="rounded-full border border-slate-200 bg-white px-4 py-2 text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">สถานที่ท่องเที่ยว</a>
            <a href="/food" className="rounded-full border border-slate-200 bg-white px-4 py-2 text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">ร้านอาหาร</a>
            <a href="/cafes" className="rounded-full border border-slate-200 bg-white px-4 py-2 text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">คาเฟ่</a>
            <a href="/hotels" className="rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 px-4 py-2 text-white shadow-md shadow-sky-500/30 transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-sky-500/40">ที่พัก</a>
          </div>
        </div>
      </div>
    </nav>
  )
}
