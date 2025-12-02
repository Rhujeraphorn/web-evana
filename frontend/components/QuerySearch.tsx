"use client"
import { useEffect, useMemo, useState } from 'react'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import type { Route } from 'next'

// ช่องค้นหาที่ sync ค่า q ใน URL พร้อม debounce
export function QuerySearch({ placeholder = 'พิมพ์ชื่อสถานที่…', debounceMs = 300 }: { placeholder?: string; debounceMs?: number }) {
  const sp = useSearchParams()
  const pathname = usePathname()
  const router = useRouter()
  const initial = sp.get('q') || ''
  const [value, setValue] = useState(initial)

  useEffect(() => {
    setValue(initial)
  }, [initial])

  useEffect(() => {
    const t = setTimeout(() => {
      const params = new URLSearchParams(sp.toString())
      if (value) params.set('q', value)
      else params.delete('q')
      const qs = params.toString()
      const href = (qs ? `${pathname}?${qs}` : pathname) as Route
      router.replace(href)
    }, debounceMs)
    return () => clearTimeout(t)
  }, [value, debounceMs, pathname, router, sp])

  return (
    <input
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder={placeholder}
      className="w-full rounded-2xl border border-slate-300 px-4 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    />
  )
}
