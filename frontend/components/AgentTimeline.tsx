// แสดงไทม์ไลน์การกระทำของ agent ทีละรายการ
// ใช้ <ol> พร้อมจุดสีน้ำเงินแสดงแต่ละ event
import type { AgentLog } from '@/lib/types'

export function AgentTimeline({ logs }: { logs: AgentLog[] }) {
  return (
    <ol className="relative border-s border-slate-200 ml-4">
      {logs.map((l, idx) => (
        <li key={idx} className="mb-4 ms-6">
          <span className="absolute -start-3 mt-1.5 flex h-3 w-3 rounded-full bg-brand-500" />
          <div className="flex items-start gap-3">
            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
              {l.ts_text || '—'}
            </span>
            <div className="font-medium leading-relaxed">
              {l.action}
              {l.poi_name ? ` → ${l.poi_name}` : ''}
            </div>
          </div>
        </li>
      ))}
    </ol>
  )
}
