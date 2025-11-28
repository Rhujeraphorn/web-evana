"use client"
import { useEffect, useMemo, useRef, useState } from 'react'
import { getBackendUrl } from '@/lib/urls'

export function SearchBar() {
  const [q, setQ] = useState('')
  const [suggest, setSuggest] = useState<string[]>([])
  const [open, setOpen] = useState(false)
  const boxRef = useRef<HTMLDivElement>(null)

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const url = new URL(window.location.href)
    url.searchParams.set('q', q)
    window.location.href = url.toString()
  }

  useEffect(() => {
    let active = true
    const run = async () => {
      const qq = q.trim()
      if (!qq) { setSuggest([]); return }
      try {
        const url = new URL('/api/agents/suggest', getBackendUrl())
        url.searchParams.set('q', qq)
        url.searchParams.set('limit', '8')
        const res = await fetch(url.toString(), { cache: 'no-store' })
        if (!res.ok) return
        const items = await res.json()
        if (active) setSuggest(items || [])
      } catch {}
    }
    const t = setTimeout(run, 200)
    return () => { active = false; clearTimeout(t) }
  }, [q])

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('click', onClick)
    return () => document.removeEventListener('click', onClick)
  }, [])

  return (
    <form onSubmit={onSubmit} className="group relative flex flex-col gap-2 sm:flex-row sm:items-center" ref={boxRef}>
      <div className="relative w-full sm:flex-1">
        <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-3.6-3.6M10.8 19.2a8.4 8.4 0 1 1 0-16.8 8.4 8.4 0 0 1 0 16.8Z" />
          </svg>
        </span>
        <input
          className="w-full rounded-3xl border border-slate-200/80 bg-white/90 px-12 py-3 text-base shadow-inner shadow-slate-200/60 transition focus:border-sky-400 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-sky-100"
          placeholder="ค้นหาเส้นทาง"
          value={q}
          onFocus={() => setOpen(true)}
          onChange={(e) => { setQ(e.target.value); setOpen(true) }}
        />
        {open && suggest.length > 0 && (
          <div className="absolute z-10 mt-2 w-full max-h-64 overflow-auto rounded-2xl border border-slate-100 bg-white/95 shadow-xl shadow-slate-900/5 ring-1 ring-slate-200">
            {suggest.map((s: string) => (
              <button type="button" key={s} className="w-full px-4 py-2 text-left text-slate-700 transition hover:bg-slate-50" onMouseDown={() => { setQ(s); setOpen(false) }}>
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
      <button
        type="submit"
        className="rounded-3xl bg-gradient-to-r from-slate-900 via-sky-900 to-sky-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:-translate-y-0.5 hover:shadow-sky-500/25"
      >
        ค้นหา
      </button>
    </form>
  )
}
