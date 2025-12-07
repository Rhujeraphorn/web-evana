// แสดงไทม์ไลน์การกระทำของ agent ทีละรายการ
// ใช้ <ol> พร้อมจุดสีน้ำเงินแสดงแต่ละ event
import type { AgentLog } from '@/lib/types'

export function AgentTimeline({ logs }: { logs: AgentLog[] }) {
  return (
    <ol className="relative border-s border-slate-200 ml-4">
      {logs.map((l, idx) => (
        <li key={idx} className="mb-4 ms-6">
          <span className="absolute -start-3 mt-1.5 flex h-3 w-3 rounded-full bg-brand-500" />
          <div className="font-medium">{l.action}{l.poi_name ? ` → ${l.poi_name}` : ''}</div>
        </li>
      ))}
    </ol>
  )
}
