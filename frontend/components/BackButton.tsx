"use client"

// ปุ่มย้อนกลับ (ใช้ history.back ถ้ามี, มี fallback ไป href)
export function BackButton({ href, fallbackHref, label = 'ย้อนกลับ', force = false }: { href?: string; fallbackHref?: string; label?: string; force?: boolean }) {
  const onClick = () => {
    const target = href || fallbackHref
    if (target && force) {
      window.location.href = target
      return
    }
    if (typeof window !== 'undefined' && window.history.length > 1) {
      window.history.back()
      return
    }
    if (target) {
      window.location.href = target
      return
    }
  }
  return (
    <button onClick={onClick} className="inline-flex items-center rounded-xl border px-3 py-1.5 text-sm hover:bg-slate-50">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 mr-1.5">
        <path fillRule="evenodd" d="M9.53 4.47a.75.75 0 010 1.06L5.31 9.75H21a.75.75 0 010 1.5H5.31l4.22 4.22a.75.75 0 11-1.06 1.06l-5.5-5.5a.75.75 0 010-1.06l5.5-5.5a.75.75 0 011.06 0z" clipRule="evenodd" />
      </svg>
      {label}
    </button>
  )
}
