// แปลงข้อความเป็น slug ตัวพิมพ์เล็ก
// - normalize('NFD') เพื่อตัดสระ/วรรณยุกต์ แล้วแปลงเป็น a-z0-9-
export function toSlug(input: string) {
  return input
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '')
}
