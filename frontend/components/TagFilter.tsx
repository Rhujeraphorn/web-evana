"use client"
type Props = { tags: { id: string; label: string }[]; value?: string; onChange?: (v: string) => void }

// ปุ่มตัวกรองแบบแท็ก เลือกได้ทีละตัว
// - แสดงสถานะ active ด้วยพื้นหลังสีแบรนด์เมื่อค่า value ตรงกับ id
// - ส่งค่าที่เลือกกลับผ่าน onChange
export function TagFilter({ tags, value = '', onChange }: Props) {
  return (
    <div className="flex gap-2 flex-wrap">
      {tags.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange?.(t.id)}
          className={`px-3 py-1 rounded-full border ${value === t.id ? 'bg-brand-500 text-white' : 'bg-white text-slate-700'}`}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}
