export function formatMoney(value: string | number | null | undefined, currency = 'RUB'): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  const amount = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(amount)) {
    return '—'
  }

  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}
