import { BackButton } from '@/components/BackButton'

export default function CafesIndex() {
  const provinces = [
    {
      slug: 'chiang-mai',
      label: 'เชียงใหม่',
      image: 'https://miwservices.com/wp-content/uploads/2023/01/cafes-in-chiang-mai-01.jpg',
    },
    {
      slug: 'lamphun',
      label: 'ลำพูน',
      image:
        'https://scontent.fbkk3-1.fna.fbcdn.net/v/t39.30808-6/480497289_1146006890299314_1189463385880274527_n.jpg?_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeHT2I-n6xkQZKL4enGA4mqJRCsFl2SlBhFEKwWXZKUGEUlBq_2LGOEFFle7mX-udqiYwfeF7q_lM54v2Z-ZKXgL&_nc_ohc=tnJtKmvM4oQQ7kNvwGZ42wM&_nc_oc=AdmEDXQQCu94xWWaGlcdun-snShw-0tBHizeRku8wT2WZ6OjJYkoW8jek0S75tskHIo&_nc_zt=23&_nc_ht=scontent.fbkk3-1.fna&_nc_gid=9eZqcG9SaJYFLbzVOkHI0g&oh=00_AfhhvWLPfLkkR75vnGiUyfv_YoaqNjTMBigYsFWDlWlZKg&oe=692CA552',
    },
    {
      slug: 'lampang',
      label: 'ลำปาง',
      image: 'https://www.ryoiireview.com/upload/article/202503/1742802007_a44aa62e128ab9fc4a63e0f86e50ce29.jpeg',
    },
    {
      slug: 'mae-hong-son',
      label: 'แม่ฮ่องสอน',
      image: 'https://www.saitiew.com/upload/2024/11/owd4y4ki1qcb.jpg',
    },
  ]
  return (
    <div>
      <div className="mb-2">
        <BackButton href="/" force />
      </div>
      <h1 className="text-2xl font-semibold mb-2">คาเฟ่</h1>
      <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4">
        {provinces.map((p) => (
          <a
            key={p.slug}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            href={`/cafes/${p.slug}`}
          >
            <div className="relative h-40 overflow-hidden">
              <img
                src={p.image}
                alt={`คาเฟ่ใน${p.label}`}
                className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-black/20 to-transparent" />
              <div className="absolute bottom-3 left-3">
                <div className="text-lg font-semibold text-white drop-shadow">{p.label}</div>
                <div className="text-sm text-slate-100">คลิกเพื่อดูคาเฟ่</div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
