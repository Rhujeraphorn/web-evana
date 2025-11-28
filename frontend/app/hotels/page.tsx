import { BackButton } from '@/components/BackButton'

export default function HotelsIndex() {
  const provinces = [
    {
      slug: 'mae-hong-son',
      label: 'แม่ฮ่องสอน',
      image: 'https://cms.dmpcdn.com/travel/2022/11/16/73db2ea0-65ba-11ed-8ade-438f05570363_webp_original.jpg',
    },
    {
      slug: 'chiang-mai',
      label: 'เชียงใหม่',
      image: 'https://cms.dmpcdn.com/travel/2021/11/05/677a8530-3e19-11ec-9f41-f5429bd5d430_original.jpg',
    },
    {
      slug: 'lamphun',
      label: 'ลำพูน',
      image: 'https://ak-d.tripcdn.com/images/1mc5r12000fwvoiv2BDA9_W_480_360_R5_Q70.jpg',
    },
    {
      slug: 'lampang',
      label: 'ลำปาง',
      image: 'https://lampangcity.go.th/a/media/main/travel/sample/post-n/hotel.jpg.l.webp',
    },
  ]
  return (
    <div>
      <div className="mb-2">
        <BackButton href="/" force />
      </div>
      <h1 className="text-2xl font-semibold mb-2">โรงแรม</h1>
      <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4">
        {provinces.map((p) => (
          <a
            key={p.slug}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            href={`/hotels/${p.slug}`}
          >
            <div className="relative h-40 overflow-hidden">
              <img
                src={p.image}
                alt={`โรงแรมใน${p.label}`}
                className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-black/20 to-transparent" />
              <div className="absolute bottom-3 left-3">
                <div className="text-lg font-semibold text-white drop-shadow">{p.label}</div>
                <div className="text-sm text-slate-100">คลิกเพื่อดูโรงแรม</div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
