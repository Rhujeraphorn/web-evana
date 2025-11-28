// Lightweight CSV reader for demo (client-unsafe; prefer server or backend API in production)
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

