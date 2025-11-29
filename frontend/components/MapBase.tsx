"use client"
import { MapContainer, TileLayer, Marker, Polyline, Popup, Tooltip } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { LatLng, RouteStop } from '@/lib/types'
import { useEffect } from 'react'

type MarkerItem = { id: string; name: string; lat: number; lon: number }

const pinSvg = `
<svg width="44" height="60" viewBox="0 0 44 60" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0EA5E9"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-10%" width="140%" height="130%" color-interpolation-filters="sRGB">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0EA5E9" flood-opacity="0.22"/>
    </filter>
  </defs>
  <path d="M22 58C22 58 42 38.6131 42 22C42 10.9543 33.0457 2 22 2C10.9543 2 2 10.9543 2 22C2 38.6131 22 58 22 58Z" fill="url(#g)" filter="url(#shadow)" stroke="#E5E7EB" stroke-width="1.5"/>
  <circle cx="22" cy="22" r="9.5" fill="white" stroke="#0EA5E9" stroke-width="2"/>
  <circle cx="22" cy="22" r="5" fill="#0EA5E9"/>
</svg>
`

const pinDataUrl = `data:image/svg+xml;utf8,${encodeURIComponent(pinSvg)}`

const defaultIcon = new L.Icon({
  iconUrl: pinDataUrl,
  iconRetinaUrl: pinDataUrl,
  iconSize: [32, 44],
  iconAnchor: [16, 42],
})

L.Marker.prototype.options.icon = defaultIcon

export default function MapBase({
  center,
  zoom = 12,
  markers = [],
  polyline = [],
  height = 360,
  stops = [],
  showPermanentLabels = false,
}: {
  center: LatLng
  zoom?: number
  markers?: MarkerItem[]
  polyline?: LatLng[]
  height?: number | string
  stops?: RouteStop[]
  showPermanentLabels?: boolean
}) {
  // Fix container height in parent
  useEffect(() => {}, [])
  return (
    <div style={{ height: typeof height === 'number' ? `${height}px` : height }}>
      <MapContainer center={[center.lat, center.lon]} zoom={zoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map((m) => (
          <Marker key={m.id} position={[m.lat, m.lon]}>
            <Popup>{m.name}</Popup>
            {showPermanentLabels && (
              <Tooltip
                direction="top"
                offset={[0, -10]}
                opacity={1}
                permanent
                className="!bg-white !px-3 !py-1 !rounded-xl !border !border-slate-200 !text-slate-800 !shadow-md"
              >
                {m.name}
              </Tooltip>
            )}
          </Marker>
        ))}
        {stops.map((s, idx) => (
          <Marker key={s.label || `stop-${idx}`} position={[s.lat, s.lon]}>
            <Popup>{s.label || `จุดแวะ ${idx + 1}`}</Popup>
            {showPermanentLabels && (
              <Tooltip
                direction="top"
                offset={[0, -10]}
                opacity={1}
                permanent
                className="!bg-white !px-3 !py-1 !rounded-xl !border !border-slate-200 !text-slate-800 !shadow-md"
              >
                {s.label || `จุดแวะ ${idx + 1}`}
              </Tooltip>
            )}
          </Marker>
        ))}
        {polyline.length > 1 && (
          <Polyline positions={polyline.map((p) => [p.lat, p.lon])} color="#0EA5E9" />
        )}
      </MapContainer>
    </div>
  )
}
