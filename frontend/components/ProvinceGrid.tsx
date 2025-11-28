export function ProvinceGrid() {
  const provinces = [
    {
      slug: 'chiang-mai',
      label: 'เชียงใหม่',
      image: 'https://www.thailand-reiseprofis.com/wp-content/bilder/chiang-mai-sehenswuerdigkeiten.jpg',
    },
    {
      slug: 'lamphun',
      label: 'ลำพูน',
      image: 'https://www.maehongsonholidays.com/wp-content/uploads/2023/07/Tha-Chomphu-White-Bridge_02_07_2023.webp',
    },
    {
      slug: 'lampang',
      label: 'ลำปาง',
      image: 'https://www.takemetour.com/amazing-thailand-go-local/wp-content/uploads/2018/09/Wat-Phra-Bat-Pu-Pha-Daeng.jpg',
    },
    {
      slug: 'mae-hong-son',
      label: 'แม่ฮ่องสอน',
      image:
        'https://res.cloudinary.com/tischler-reisen-ag/image/upload/w_1920/w_1920,h_768,c_crop,y_94/f_auto,q_auto:good,ar_2.5,c_crop/w_1920/thailand-mae-hong-son-chong-kham-tempel-51781.webp',
    },
  ]
  return (
    <div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2">
      {provinces.map((p) => (
        <div
          key={p.slug}
          className="group relative overflow-hidden rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-900/10"
        >
          <div className="absolute inset-x-0 -bottom-10 h-24 bg-gradient-to-r from-sky-50 via-white to-sky-50 opacity-80 transition group-hover:opacity-100" />
          <div className="relative overflow-hidden rounded-2xl border border-slate-100">
            <div className="h-36 w-full overflow-hidden">
              <img
                src={p.image}
                alt={p.label}
                className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
                loading="lazy"
              />
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/35 via-black/10 to-transparent" />
            <div className="absolute bottom-3 left-3 text-white drop-shadow">
              <div className="text-lg font-semibold">{p.label}</div>
              <div className="text-xs text-slate-100">คลิกเพื่อดูจุดเช็คอิน</div>
            </div>
          </div>
          <div className="relative mt-4 space-y-2">
            <div className="text-sm font-semibold uppercase tracking-wide text-slate-500">สำรวจ</div>
            <div className="flex flex-wrap gap-2">
              <a
                className="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-sm font-medium text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow"
                href={`/chargers/${p.slug}`}
              >
                สถานีชาร์จ
              </a>
              <a
                className="rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 px-3.5 py-1.5 text-sm font-semibold text-white shadow-md shadow-sky-500/30 transition hover:-translate-y-0.5 hover:shadow-lg"
                href={`/attractions/${p.slug}`}
              >
                ท่องเที่ยว
              </a>
              <a
                className="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-sm font-medium text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow"
                href={`/food/${p.slug}`}
              >
                ร้านอาหาร
              </a>
              <a
                className="rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 px-3.5 py-1.5 text-sm font-semibold text-white shadow-md shadow-sky-500/30 transition hover:-translate-y-0.5 hover:shadow-lg"
                href={`/attractions/${p.slug}`}
              >
                คาเฟ่
              </a>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
