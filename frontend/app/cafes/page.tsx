// หน้าเลือกจังหวัดเพื่อดูรายการคาเฟ่
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
        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSj6MxhAUpN8w8Zn3YmZNE4qHJvR6znG8Vfwg&s',
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
