// แมประหว่าง slug จังหวัด -> ชื่อภาษาไทย และฟังก์ชันแปลง
export const PROVINCE_THAI_MAP: Record<string, string> = {
  'chiang-mai': 'เชียงใหม่',
  'lamphun': 'ลำพูน',
  'lampang': 'ลำปาง',
  'mae-hong-son': 'แม่ฮ่องสอน',
}

export function toThaiProvince(slug: string | undefined | null): string {
  if (!slug) return ''
  return PROVINCE_THAI_MAP[slug] || slug
}
