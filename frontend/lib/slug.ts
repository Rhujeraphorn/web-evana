// แปลงข้อความเป็น slug ตัวพิมพ์เล็ก พร้อมตัดเครื่องหมายกำกับเสียง
export function toSlug(input: string) {
  return input
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '')
}
