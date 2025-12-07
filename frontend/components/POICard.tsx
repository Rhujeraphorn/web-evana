type POICardProps = {
  title: string
  subtitle?: string
  href?: string
  tags?: string[]
}

// การ์ดแสดงข้อมูล POI สั้น ๆ พร้อมลิงก์/แท็ก
// - ถ้ามี href จะคลิกไปยังหน้ารายละเอียดได้ทั้งการ์ด
// - รองรับแท็กหลายตัวสำหรับ metadata สั้น ๆ
export function POICard({ title, subtitle, href, tags = [] }: POICardProps) {
  const inner = (
    <div className="rounded-2xl border border-slate-200 p-4 shadow-md hover:shadow-lg transition bg-white">
      <div className="font-medium">{title}</div>
      {subtitle && <div className="text-slate-500 text-sm">{subtitle}</div>}
      {tags.length > 0 && (
        <div className="flex gap-2 mt-2 flex-wrap">
          {tags.map((t) => (
            <span key={t} className="text-xs bg-slate-100 px-2 py-1 rounded-full">{t}</span>
          ))}
        </div>
      )}
    </div>
  )
  return href ? <a href={href}>{inner}</a> : inner
}
