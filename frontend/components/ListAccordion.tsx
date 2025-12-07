"use client"
import { useState } from 'react'

// รายการแบบแอคคอร์เดียน
// - เก็บ state id ที่เปิดอยู่ (open) และ toggle เมื่อกดหัวข้อ
// - แสดงลิงก์ CTA เมื่อมี href
export function ListAccordion({
  items,
}: {
  items: { id: string; title: string; subtitle?: string; href?: string }[]
}) {
  const [open, setOpen] = useState<string | null>(null)
  return (
    <div className="divide-y rounded-2xl border border-slate-200 overflow-hidden">
      {items.map((it) => (
        <div key={it.id} className="bg-white">
          <button
            className="w-full text-left px-4 py-3 hover:bg-slate-50 flex justify-between items-center"
            onClick={() => setOpen((o) => (o === it.id ? null : it.id))}
          >
            <div>
              <div className="font-medium">{it.title}</div>
              {it.subtitle && <div className="text-slate-500 text-sm">{it.subtitle}</div>}
            </div>
            <span className="text-slate-400">{open === it.id ? '−' : '+'}</span>
          </button>
          {open === it.id && (
            <div className="px-4 pb-3">
              {it.href && (
                <a className="text-brand-600 hover:underline" href={it.href}>
                  ดูรายละเอียด
                </a>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
