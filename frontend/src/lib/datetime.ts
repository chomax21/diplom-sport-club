import { differenceInMinutes, format, isToday, isTomorrow, isValid, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'

export function parseDateValue(value: string | null | undefined): Date | null {
  if (!value) {
    return null
  }

  const date = parseISO(value)
  return isValid(date) ? date : null
}

export function formatTime(value: string): string {
  const date = parseDateValue(value)
  return date ? format(date, 'HH:mm') : '—'
}

export function formatTimeRange(startsAt: string, endsAt: string): string {
  return `${formatTime(startsAt)}–${formatTime(endsAt)}`
}

export function formatDateLong(value: string): string {
  const date = parseDateValue(value)
  return date ? format(date, 'd MMMM, EEEE', { locale: ru }) : '—'
}

export function formatDayHeading(value: string): string {
  const date = parseDateValue(value)
  if (!date) {
    return 'Дата не указана'
  }

  if (isToday(date)) {
    return `Сегодня, ${format(date, 'd MMMM', { locale: ru })}`
  }

  if (isTomorrow(date)) {
    return `Завтра, ${format(date, 'd MMMM', { locale: ru })}`
  }

  return format(date, 'd MMMM, EEEE', { locale: ru })
}

export function formatDateTime(value: string): string {
  const date = parseDateValue(value)
  return date ? format(date, 'd MMMM yyyy, HH:mm', { locale: ru }) : '—'
}

export function formatDateShort(value: string): string {
  const date = parseDateValue(value)
  return date ? format(date, 'dd.MM.yyyy') : '—'
}

export function formatDateRange(from: string, to: string): string {
  return `${formatDateShort(from)} — ${formatDateShort(to)}`
}

export function dayKey(value: string): string {
  const date = parseDateValue(value)
  return date ? format(date, 'yyyy-MM-dd') : value
}

export function dateInputValue(value: Date | string = new Date()): string {
  const date = typeof value === 'string' ? parseDateValue(value) : value
  return date ? format(date, 'yyyy-MM-dd') : ''
}

export function timeInputValue(value: Date | string = new Date()): string {
  const date = typeof value === 'string' ? parseDateValue(value) : value
  return date ? format(date, 'HH:mm') : ''
}

export function toDateInput(date: Date): string {
  return format(date, 'yyyy-MM-dd')
}

export function todayDateInput(): string {
  return toDateInput(new Date())
}

export function addDaysDateInput(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return toDateInput(date)
}

export function toIsoFromDateTime(date: string, time: string): string {
  return new Date(`${date}T${time}:00`).toISOString()
}

export function isPastDate(value: string): boolean {
  const date = parseDateValue(value)
  return date !== null && date.getTime() < Date.now()
}

export function durationMinutes(startsAt: string, endsAt: string): number {
  const start = parseDateValue(startsAt)
  const end = parseDateValue(endsAt)
  if (!start || !end) {
    return 0
  }

  return Math.max(0, differenceInMinutes(end, start))
}

export function formatDuration(startsAt: string, endsAt: string): string {
  const minutes = durationMinutes(startsAt, endsAt)
  if (minutes === 0) {
    return '—'
  }

  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60

  if (hours === 0) {
    return `${rest} мин`
  }
  if (rest === 0) {
    return `${hours} ч`
  }

  return `${hours} ч ${rest} мин`
}
