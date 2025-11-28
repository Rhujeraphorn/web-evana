import { BackButton } from '@/components/BackButton'

export default function FoodIndex() {
  const imageUrl =
    'https://d3h1lg3ksw6i6b.cloudfront.net/media/image/2024/03/25/4e3db9c26b00421a967bfd294c6f10c2_11-must-try-northern-thai-dishes-in-chiang-mai_%281%29.jpg'
  const provinces = [
    { slug: 'chiang-mai', label: 'เชียงใหม่' },
    { slug: 'lamphun', label: 'ลำพูน' },
    { slug: 'lampang', label: 'ลำปาง' },
    { slug: 'mae-hong-son', label: 'แม่ฮ่องสอน' },
  ]
  return (
    <div>
      <div className="mb-2">
        <BackButton href="/" force />
      </div>
      <h1 className="text-2xl font-semibold mb-2">ร้านอาหาร</h1>
      <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4">
        {provinces.map((p) => (
          <a
            key={p.slug}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            href={`/food/${p.slug}`}
          >
            <div className="relative h-40 overflow-hidden">
              <img
                src={imageUrl}
                alt={`อาหารแนะนำใน${p.label}`}
                className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-black/20 to-transparent" />
              <div className="absolute bottom-3 left-3">
                <div className="text-lg font-semibold text-white drop-shadow">{p.label}</div>
                <div className="text-sm text-slate-100">คลิกเพื่อดูร้านอาหาร</div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
