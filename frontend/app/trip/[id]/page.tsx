// หน้าแสดงทริป agent รายตัวพร้อมแผนที่ Polyline และไทม์ไลน์
import dynamic from 'next/dynamic'
import { AgentTimeline } from '@/components/AgentTimeline'
import { OpenInMapsButton } from '@/components/OpenInMapsButton'
import { BackButton } from '@/components/BackButton'
import { getBackendUrl } from '@/lib/urls'

const MapBase = dynamic(() => import('@/components/MapBase'), { ssr: false })

export default async function TripDetail({ params, searchParams }: { params: { id: string }, searchParams?: { day?: string } }) {
  const day = searchParams?.day
  const url = new URL(`/api/agents/${params.id}`, getBackendUrl())
  if (day) url.searchParams.set('day', String(day))
  const res = await fetch(url, { next: { revalidate: 0 } })
  const d = res.ok ? await res.json() : { id: params.id, title: `Agent #${params.id}`, style: 'mix', total_km: 0, days: 0, timeline: [], polyline: [] }
  const firstRoutePoint = Array.isArray(d.polyline) && d.polyline.length ? d.polyline[0] : null
  const firstPoint = firstRoutePoint || { lat: 18.79, lon: 98.99 }
  const normalize = (v?: string) => (v || '').trim().toLowerCase()
  const stopByLabel = new Map<string, { label?: string; lat: number; lon: number }>()
  ;(d.stops || []).forEach((s: { label?: string; lat: number; lon: number }) => {
    if (s.lat === undefined || s.lon === undefined) return
    stopByLabel.set(normalize(s.label), s)
  })

  const timelineStops =
    (d.timeline || []).map((t: any, idx: number) => {
      const label = t.poi_name || t.action || `จุดที่ ${idx + 1}`
      const norm = normalize(label)
      const matchedStop = stopByLabel.get(norm)
      if (matchedStop) return matchedStop
      if (t.lat !== undefined && t.lon !== undefined) {
        return { label, lat: Number(t.lat), lon: Number(t.lon) }
      }
      return null
    }).filter(Boolean) as { label?: string; lat: number; lon: number }[]

  const startHotelLabel = (() => {
    const hotelKeywords = ['โรงแรม', 'hotel', 'hostel', 'resort', 'inn', 'guesthouse', 'guest house']
    const extractHotelFromAction = (text?: string) => {
      if (!text) return ''
      const match = text.match(/เริ่มทริป.*(?:โรงแรม|hotel)[:\s]+([^(\n\r]+?)(?:\sแบต|$|\()/i)
      if (match?.[1]) return match[1].trim()
      return text.trim()
    }
    const candidate = (d.timeline || []).find((t: any) => {
      const text = normalize(t.poi_name) || normalize(t.action)
      if (!text) return false
      return hotelKeywords.some((kw) => text.includes(kw))
    })
    if (!candidate) return ''
    return (candidate.poi_name || '').trim() || extractHotelFromAction(candidate.action || '')
  })()
  const startStop = startHotelLabel && firstRoutePoint
    ? { label: startHotelLabel, lat: Number(firstRoutePoint.lat), lon: Number(firstRoutePoint.lon) }
    : null

  const mergedStopsMap = new Map<string, { label?: string; lat: number; lon: number }>()
  ;[...(d.stops || []), ...timelineStops].forEach((s: { label?: string; lat: number; lon: number }) => {
    if (s.lat === undefined || s.lon === undefined) return
    const key = `${normalize(s.label)}-${s.lat.toFixed(5)}-${s.lon.toFixed(5)}`
    if (!mergedStopsMap.has(key)) {
      mergedStopsMap.set(key, s)
    }
  })
  if (startStop) {
    const key = `${normalize(startStop.label)}-${startStop.lat.toFixed(5)}-${startStop.lon.toFixed(5)}`
    if (!mergedStopsMap.has(key)) {
      mergedStopsMap.set(key, startStop)
    }
  }
  const mapStops = Array.from(mergedStopsMap.values()).filter(
    (s) => Number.isFinite(s.lat) && Number.isFinite(s.lon)
  )
  // map label -> stop เพื่อนำไปจับคู่กับ visited_pois
  const stopByNormLabel = new Map<string, { label?: string; lat: number; lon: number }>()
  mapStops.forEach((s) => {
    const key = normalize(s.label)
    if (key && !stopByNormLabel.has(key)) {
      stopByNormLabel.set(key, s)
    }
  })
  const styleMap: Record<string, string> = { cta: 'Culture', nta: 'Nature', avt: 'Activity' }
  const styleCode = String(d.style || '').toLowerCase()
  const styleFull = styleMap[styleCode] || (d.style ? String(d.style) : '')
  const dayCount = d.days || (d.timeline ? Math.max(...d.timeline.map((t: any) => t.day || 0), 1) : 1)
  const totalKm = d.total_km ? Math.round(d.total_km) : 0
  const uniqueVisitedPoi: string[] = Array.from(
    new Set<string>(
      (d.timeline || [])
        .map((t: any) => normalize(t.poi_name || ''))
        .filter((v: string) => Boolean(v))
    )
  )
  const uniqueTimelinePoi: string[] = Array.from(
    new Set<string>(
      (d.timeline || [])
        .map((t: any) => normalize(t.poi_name || t.action || ''))
        .filter((v: string) => Boolean(v))
    )
  )
  // ใช้จำนวน POI ที่มีชื่อจริงใน timeline (visited_pois) เป็นหลัก
  const stopCount = uniqueVisitedPoi.length || mapStops.length || uniqueTimelinePoi.length || (d.timeline ? d.timeline.length : 0)
  // ปักหมุดตามรายชื่อ visited_pois เป็นหลัก ถ้ามีใน stops
  const visitedStops = uniqueVisitedPoi
    .map((name) => stopByNormLabel.get(name))
    .filter((v): v is { label?: string; lat: number; lon: number } => Boolean(v))
  const markersBase = visitedStops.length ? visitedStops : mapStops
  const markers = startStop && !markersBase.some((s) => normalize(s.label) === normalize(startStop.label))
    ? [startStop, ...markersBase]
    : markersBase

  return (
    <div className="space-y-8 px-3 md:px-6 lg:px-10 max-w-none">
      <section className="relative overflow-hidden rounded-[32px] border border-slate-200/80 bg-white/95 p-6 shadow-xl shadow-slate-900/10">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-sky-50 via-white to-slate-100 opacity-90" />
          <div className="absolute -right-24 -top-16 h-64 w-64 rounded-full bg-sky-200/30 blur-3xl" />
          <div className="absolute -left-16 bottom-0 h-48 w-48 rounded-full bg-slate-900/5 blur-3xl" />
        </div>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <BackButton fallbackHref={`/`} />
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">แนะนำทริป</p>
              <h1 className="text-3xl font-bold leading-tight text-slate-900 md:text-4xl">{d.title}</h1>
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  รูปแบบ: {styleFull || 'mix'}
                </span>
                <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">
                  {dayCount} วัน
                </span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 min-w-[260px]">
            <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-sky-500 to-slate-900 px-4 py-3 text-white shadow-lg shadow-sky-500/30">
              <div className="text-2xl font-semibold">{dayCount}</div>
              <div className="text-xs font-semibold uppercase tracking-wide text-white/70">วันเดินทาง</div>
              
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-left shadow-sm shadow-slate-900/5">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">จุดแวะ</div>
              <div className="text-2xl font-semibold text-slate-900">{stopCount}</div>
              <div className="text-xs text-slate-500">POIs ในเส้นทาง</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.5fr,1fr] lg:items-start">
        <div className="flex h-[78vh] flex-col overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-xl shadow-slate-900/10 ring-1 ring-slate-200/60 lg:h-[calc(100vh-200px)]">
          <div className="flex items-center justify-between px-5 py-3">
            <div>
              <p className="text-sm font-semibold text-slate-500">เส้นทางบนแผนที่</p>
            </div>
            <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">Zoom / Tap</span>
          </div>
          <div className="flex-1 border-t border-slate-100">
            <MapBase
              center={{ lat: firstPoint.lat, lon: firstPoint.lon }}
              zoom={12}
              polyline={d.polyline || []}
              stops={markers}
              height="100%"
              showPermanentLabels
            />
          </div>
        </div>

        <div className="space-y-4 lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto lg:pr-1">
          <div className="rounded-3xl border border-slate-200/80 bg-white/95 p-4 shadow-sm shadow-slate-900/5">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-600">ไทม์ไลน์</p>
            </div>
            <div className="rounded-2xl border border-slate-100 bg-white p-3 shadow-inner shadow-slate-100">
              <AgentTimeline logs={d.timeline || []} />
            </div>
          </div>
          <div className="rounded-3xl border border-slate-200/80 bg-white/90 p-4 shadow-sm shadow-slate-900/10">
            <p className="text-sm font-semibold text-slate-700 mb-3">นำทาง</p>
            <OpenInMapsButton points={d.polyline || []} stops={mapStops} />
          </div>
        </div>
      </section>
    </div>
  )
}
