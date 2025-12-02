// หน้าเลือกจังหวัดเพื่อดูสถานที่ท่องเที่ยว
import { getBackendUrl } from '@/lib/urls'
import { BackButton } from '@/components/BackButton'

export default async function AttractionsIndex() {
  const res = await fetch(new URL('/api/provinces', getBackendUrl()), { next: { revalidate: 0 } })
  const provinces: { slug: string; name_th: string }[] = res.ok
    ? await res.json()
    : [
        { slug: 'chiang-mai', name_th: 'เชียงใหม่' },
        { slug: 'lamphun', name_th: 'ลำพูน' },
        { slug: 'lampang', name_th: 'ลำปาง' },
        { slug: 'mae-hong-son', name_th: 'แม่ฮ่องสอน' },
      ]
  const imageMap: Record<string, string> = {
    'chiang-mai': 'https://www.thailand-reiseprofis.com/wp-content/bilder/chiang-mai-sehenswuerdigkeiten.jpg',
    lamphun: 'https://www.maehongsonholidays.com/wp-content/uploads/2023/07/Tha-Chomphu-White-Bridge_02_07_2023.webp',
    lampang: 'https://www.takemetour.com/amazing-thailand-go-local/wp-content/uploads/2018/09/Wat-Phra-Bat-Pu-Pha-Daeng.jpg',
    'mae-hong-son':
      'https://res.cloudinary.com/tischler-reisen-ag/image/upload/w_1920/w_1920,h_768,c_crop,y_94/f_auto,q_auto:good,ar_2.5,c_crop/w_1920/thailand-mae-hong-son-chong-kham-tempel-51781.webp',
  }
  const provincesWithImages = provinces.map((p) => ({ ...p, image: imageMap[p.slug] }))
  return (
    <div>
      <div className="mb-2">
        <BackButton href="/" force />
      </div>
      <h1 className="text-2xl font-semibold mb-2">สถานที่ท่องเที่ยว</h1>
      <p className="text-slate-500">เลือกจังหวัด</p>
      <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4">
        {provincesWithImages.map((p) => (
          <a
            key={p.slug}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            href={`/attractions/${p.slug}`}
          >
            <div className="relative h-40 overflow-hidden">
              {p.image ? (
                <img
                  src={p.image}
                  alt={p.name_th}
                  className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                  loading="lazy"
                />
              ) : (
                <div className="flex h-full items-center justify-center bg-slate-100 text-slate-500">No image</div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-black/20 to-transparent" />
              <div className="absolute bottom-3 left-3">
                <div className="text-lg font-semibold text-white drop-shadow">{p.name_th}</div>
                <div className="text-sm text-slate-100">คลิกเพื่อดูจุดท่องเที่ยว</div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
