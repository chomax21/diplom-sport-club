export type CsvValue = string | number | null | undefined

function escapeCell(value: CsvValue): string {
  const text = value === null || value === undefined ? '' : String(value)
  return `"${text.replace(/"/g, '""')}"`
}

export function downloadCsv(filename: string, rows: CsvValue[][]): void {
  const content = `\uFEFF${rows.map((row) => row.map(escapeCell).join(';')).join('\r\n')}`
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
