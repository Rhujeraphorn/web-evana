// ประเภทข้อมูลสำหรับ frontend เช่น พิกัด เส้นทาง และการ์ด agent
export type ProvinceEN = 'Chiang Mai'|'Lamphun'|'Lampang'|'Mae Hong Son'
// พิกัดละติจูด/ลองจิจูด
export type LatLng = { lat: number; lon: number }
// จุดแวะบนเส้นทาง แถม label ไว้แสดง tooltip
export type RouteStop = LatLng & { label?: string }
// รายละเอียดสถานีชาร์จ
export type Charger = { id:string; name:string; type:'AC'|'DC'; kw?:number; capacity?:number; province:string; lat:number; lon:number }
// โครงสร้างพื้นฐานของ POI ทั่วไป
export type POIBase = { id:string; name_th:string; name_en?:string; province:string; lat:number; lon:number }
export type Attraction = POIBase & { kind:'CTA'|'NTA'|'AVT' }
export type Hotel = POIBase & { stars?:number }
export type Food = POIBase & { price_range?:string }
export type Cafe = POIBase
// การ์ดสรุป agent และบันทึกเหตุการณ์ของ agent
export type AgentCard = { id:number; title:string; style:string; total_km:number; days:number; poi_tags:string[]; points:number; province_slug:string }
export type AgentLog = { ts_text:string; day:number; action:string; poi_name?:string; lat?:number; lon?:number }
