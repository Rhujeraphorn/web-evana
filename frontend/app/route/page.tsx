import { RouteSearch } from '@/components/RouteSearch'

export const dynamic = 'force-dynamic'

export default function RoutePlannerPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">ค้นหาเส้นทาง</h1>
      <p className="text-slate-600">พิมพ์ชื่อสถานที่ต้นทางและปลายทางเพื่อเริ่มค้นหา</p>
      <RouteSearch />
    </div>
  )
}
