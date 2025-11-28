"use client"

import { useEffect, useMemo, useRef, useState } from 'react'
import { getBackendUrl } from '@/lib/urls'
import dynamic from 'next/dynamic'
import type { LatLng } from '@/lib/types'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

type Segment = {
  from: string
  to: string
  distance_km: number
  travel_time_min: number
  energy_kwh?: number
  ev_cost_thb?: number
  unit?: string
}
type AgentPlan = {
  agent_id?: string | number
  policy_main?: string | null
}
type SearchResult = {
  path: Segment[]
  totalDist: number
  totalTime: number
  totalEnergy: number
  totalCost: number
  agent?: AgentPlan
}

const ROUTE_SOURCES = [
  { key: 'mae-hong-son-agg', label: 'แม่ฮ่องสอน' },
  { key: 'chiang-mai-agg', label: 'เชียงใหม่' },
  { key: 'lamphun-agg', label: 'ลำพูน' },
  { key: 'lampang-agg', label: 'ลำปาง' },
] as const

async function fetchNodes(source: string): Promise<string[]> {
  const url = new URL('/api/routes/nodes', getBackendUrl())
  url.searchParams.set('source', source)
  const res = await fetch(url.toString(), { cache: 'no-store' })
  if (!res.ok) return []
  const data = await res.json()
  return Array.isArray(data) ? (data as string[]) : []
}

async function searchRouteAPI(from: string, to: string, source: string): Promise<SearchResult | null> {
  const url = new URL('/api/routes/search', getBackendUrl())
  url.searchParams.set('from_name', from)
  url.searchParams.set('to_name', to)
  url.searchParams.set('source', source)
  const res = await fetch(url.toString(), { cache: 'no-store' })
  if (!res.ok) return null
  return (await res.json()) as SearchResult
}

export function RouteSearch() {
  const [source, setSource] = useState<typeof ROUTE_SOURCES[number]['key']>(ROUTE_SOURCES[0].key)
  const nodesCache = useRef<Record<string, string[]>>({})
  const [nodes, setNodes] = useState<string[]>([])
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [focusField, setFocusField] = useState<'from' | 'to' | null>(null)
  const [result, setResult] = useState<SearchResult | null>(null)
  const [polyline, setPolyline] = useState<LatLng[]>([])

  useEffect(() => {
    let cancelled = false
    const loadNodes = async () => {
      setResult(null)
      setPolyline([])
      const cached = nodesCache.current[source]
      if (cached) {
        setNodes(cached)
        return
      }
      const list = await fetchNodes(source)
      if (!cancelled) {
        setNodes(list)
        nodesCache.current[source] = list
      }
    }
    loadNodes()
    return () => { cancelled = true }
  }, [source])
  const allPlaces = useMemo(() => nodes.slice().sort(), [nodes])

  const onSearch = () => {
    if (!from || !to) return
    searchRouteAPI(from, to, source).then((r) => {
      if (r) setResult(r)
      else {
        setResult(null)
        alert('ไม่พบจุดเริ่มต้นหรือปลายทางในข้อมูล หรือไม่พบเส้นทาง')
      }
    })
  }

  const swap = () => {
    setFrom(to)
    setTo(from)
  }

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      if (!result || !result.path || result.path.length === 0) { setPolyline([]); return }
      const base = getBackendUrl()
      const coords: LatLng[] = []
      for (const seg of result.path) {
        try {
          const url = new URL('/api/routes/geojson', base)
          url.searchParams.set('from_name', seg.from)
          url.searchParams.set('to_name', seg.to)
          url.searchParams.set('source', source)
          const res = await fetch(url.toString(), { cache: 'no-store' })
          if (!res.ok) continue
          const gj = await res.json()
          // Support Feature or FeatureCollection
          const features = gj.type === 'FeatureCollection' ? gj.features : [gj]
          for (const ft of features) {
            const geom = ft.geometry || {}
            if (geom.type === 'LineString' && Array.isArray(geom.coordinates)) {
              for (const c of geom.coordinates) {
                if (Array.isArray(c) && c.length >= 2) coords.push({ lat: Number(c[1]), lon: Number(c[0]) })
              }
            }
          }
        } catch {}
      }
      if (!cancelled) setPolyline(coords)
    }
    run()
    return () => { cancelled = true }
  }, [result, source])

  // Substring suggestions for inputs
  const fromMatches = useMemo(() => {
    const q = from.trim().toLowerCase()
    if (!q) return [] as string[]
    const starts = allPlaces.filter(p => p.toLowerCase().startsWith(q))
    const contains = allPlaces.filter(p => p.toLowerCase().includes(q) && !starts.includes(p))
    return [...starts, ...contains].slice(0, 8)
  }, [from, allPlaces])

  const toMatches = useMemo(() => {
    const q = to.trim().toLowerCase()
    if (!q) return [] as string[]
    const starts = allPlaces.filter(p => p.toLowerCase().startsWith(q))
    const contains = allPlaces.filter(p => p.toLowerCase().includes(q) && !starts.includes(p))
    return [...starts, ...contains].slice(0, 8)
  }, [to, allPlaces])

  const fromRef = useRef<HTMLInputElement>(null)
  const toRef = useRef<HTMLInputElement>(null)

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      onSearch()
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border shadow-sm p-4 bg-white">
        <div className="flex flex-col gap-3 mb-4 md:flex-row md:items-center">
          <label className="text-sm text-slate-600">
            เลือกจังหวัด/ชุดข้อมูล
            <select
              value={source}
              onChange={(e) => {
                setSource(e.target.value as typeof source)
                setFrom('')
                setTo('')
              }}
              className="mt-1 w-full md:w-auto md:ml-3 rounded-xl border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
            >
              {ROUTE_SOURCES.map((opt) => (
                <option key={opt.key} value={opt.key}>{opt.label}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr_auto] items-end">
          <div className="relative">
            <label className="block text-sm text-slate-600 mb-1">จาก</label>
            <input ref={fromRef} onFocus={() => setFocusField('from')} onBlur={() => setTimeout(() => setFocusField(null), 150)} onKeyDown={onKeyDown} value={from} onChange={(e) => setFrom(e.target.value)} placeholder="เช่น พิพิธภัณฑ์ไม้ไผ่" className="w-full rounded-xl border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500" />
            {focusField === 'from' && fromMatches.length > 0 ? (
              <div className="absolute z-10 mt-1 w-full rounded-xl border bg-white shadow-lg max-h-64 overflow-auto">
                {fromMatches.map((p) => (
                  <button key={p} type="button" onMouseDown={() => { setFrom(p); setFocusField(null); toRef.current?.focus() }} className="w-full text-left px-3 py-2 hover:bg-slate-50">
                    {p}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <div className="flex md:justify-center">
            <button onClick={swap} className="mt-6 inline-flex items-center rounded-xl border px-3 py-2 text-sm hover:bg-slate-50">สลับ</button>
          </div>
          <div className="relative">
            <label className="block text-sm text-slate-600 mb-1">ไป</label>
            <input ref={toRef} onFocus={() => setFocusField('to')} onBlur={() => setTimeout(() => setFocusField(null), 150)} onKeyDown={onKeyDown} value={to} onChange={(e) => setTo(e.target.value)} placeholder="เช่น กาดหลวง" className="w-full rounded-xl border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500" />
            {focusField === 'to' && toMatches.length > 0 ? (
              <div className="absolute z-10 mt-1 w-full rounded-xl border bg-white shadow-lg max-h-64 overflow-auto">
                {toMatches.map((p) => (
                  <button key={p} type="button" onMouseDown={() => { setTo(p); setFocusField(null) }} className="w-full text-left px-3 py-2 hover:bg-slate-50">
                    {p}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <div className="flex md:justify-end">
            <button onClick={onSearch} className="mt-6 inline-flex items-center rounded-xl bg-brand-500 text-white px-4 py-2 hover:bg-brand-600 shadow">
              ค้นหาเส้นทาง
            </button>
          </div>
        </div>
      </div>

      {result ? (
        <div className="rounded-2xl border p-4 space-y-3 bg-white shadow-sm">
          {polyline.length > 1 ? (
            <div className="rounded-xl overflow-hidden border">
              <MapBase center={polyline[0]} zoom={10} markers={[]} polyline={polyline} />
            </div>
          ) : null}
          <div className="font-semibold text-lg">สรุปเส้นทาง</div>
          <div className="text-slate-700">
            ระยะทางรวม: {result.totalDist.toFixed(2)} กม. • เวลาเดินทางรวม: {result.totalTime.toFixed(0)} นาที • พลังงาน: {result.totalEnergy.toFixed(2)} kWh • ค่าชาร์จ: {result.totalCost.toFixed(2)} บาท
          </div>
          <div className="text-sm text-slate-500">แผนจากตัวแทน: {result.agent?.agent_id} {result.agent?.policy_main ? `• ${result.agent?.policy_main}` : ''}</div>
          <div className="divide-y">
            {result.path.map((s, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between gap-4">
                <div>
                  <div className="font-medium">{s.from} → {s.to}</div>
                  <div className="text-slate-600">{s.distance_km} กม. • {s.travel_time_min} นาที{s.energy_kwh ? ` • ${s.energy_kwh} kWh` : ''}{s.ev_cost_thb ? ` • ${s.ev_cost_thb} บาท` : ''}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}
