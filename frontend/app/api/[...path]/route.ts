// Proxy endpoint ใน Next.js ส่งต่อไป backend FastAPI
// - รองรับทุก path ใต้ /api/* ด้วย catch-all [...path]
// - คง query string เดิมไว้ และส่ง method/headers/body ต่อให้ backend
// - ใช้เป็นทางแก้ CORS และให้ frontend พึ่ง env NEXT_PUBLIC_BACKEND_URL เพียงที่เดียว
import type { NextRequest } from 'next/server'

export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  const url = new URL(req.nextUrl)
  const target = `${backend}/api/${(params.path || []).join('/')}${url.search}`
  const res = await fetch(target)
  const body = await res.text()
  return new Response(body, { status: res.status, headers: { 'content-type': res.headers.get('content-type') || 'application/json' } })
}

export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  const url = new URL(req.nextUrl)
  const target = `${backend}/api/${(params.path || []).join('/')}${url.search}`
  const res = await fetch(target, { method: 'POST', body: await req.text(), headers: { 'content-type': req.headers.get('content-type') || 'application/json' } })
  const body = await res.text()
  return new Response(body, { status: res.status, headers: { 'content-type': res.headers.get('content-type') || 'application/json' } })
}
