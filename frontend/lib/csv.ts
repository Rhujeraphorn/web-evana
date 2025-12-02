// ฟังก์ชันอ่าน CSV แบบง่าย (ฝั่ง client สำหรับเดโมเท่านั้น)
export async function readCsv(url: string): Promise<Record<string, string>[]> {
  const res = await fetch(url)
  const text = await res.text()
  const [header, ...rows] = text.split(/\r?\n/).filter(Boolean)
  const cols = header.split(',')
  return rows.map((r) => {
    const vals = r.split(',')
    return Object.fromEntries(cols.map((c, i) => [c, vals[i] ?? '']))
  })
}
