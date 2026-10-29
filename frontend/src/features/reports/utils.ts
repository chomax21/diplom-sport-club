import type { AttendanceReport, RevenueReport } from '@/api/reports'

const numberFormatter = new Intl.NumberFormat('ru-RU')

export function formatCount(value: number): string {
  return numberFormatter.format(value)
}

export function formatPercent(value: number, digits = 1): string {
  return `${value.toLocaleString('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  })}%`
}

export function formatAverageCheck(total: string, payments: number): string {
  if (payments <= 0) {
    return '—'
  }
  return String(Number(total) / payments)
}

export function hasAttendanceData(report: AttendanceReport | null | undefined): boolean {
  return Boolean(report && (report.sessions_count > 0 || report.enrollments_count > 0))
}

export function hasRevenueData(report: RevenueReport | null | undefined): boolean {
  return Boolean(
    report &&
    (report.payments_count > 0 ||
      Number(report.refunded_amount) > 0 ||
      report.by_membership_type.length > 0),
  )
}

export function periodLabel(dateFrom: string, dateTo: string): string {
  const format = (value: string) => {
    const [year, month, day] = value.split('-')
    return day && month && year ? `${day}.${month}.${year}` : value
  }
  return `${format(dateFrom)} — ${format(dateTo)}`
}

export function formatChartDay(value: string): string {
  const [, month, day] = value.split('-')
  return day && month ? `${day}.${month}` : value
}
