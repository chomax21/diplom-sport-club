import type { Membership, Payment, PaymentMethod } from '@/api/memberships'
import type { UserRole } from '@/api/types'
import { differenceInCalendarDays, isValid, parseISO } from 'date-fns'

export const PAYMENT_METHOD_LABELS: Record<PaymentMethod, string> = {
  card: 'Банковская карта',
  cash: 'Наличные',
  online: 'Онлайн-оплата',
}

const visitRules = new Intl.PluralRules('ru-RU')
const dayRules = new Intl.PluralRules('ru-RU')

function pluralize(
  count: number,
  rules: Intl.PluralRules,
  forms: { one: string; few: string; many: string },
): string {
  const category = rules.select(count)
  if (category === 'one') {
    return forms.one
  }
  if (category === 'few') {
    return forms.few
  }
  return forms.many
}

export function visitsLeftLabel(visitsLeft: number | null): string {
  if (visitsLeft === null) {
    return 'Безлимит'
  }
  if (visitsLeft <= 0) {
    return 'Посещения закончились'
  }

  return `${visitsLeft} ${pluralize(visitsLeft, visitRules, {
    one: 'посещение',
    few: 'посещения',
    many: 'посещений',
  })}`
}

export function durationDaysLabel(days: number): string {
  return `${days} ${pluralize(days, dayRules, { one: 'день', few: 'дня', many: 'дней' })}`
}

export function daysUntilDate(value: string, today = new Date()): number | null {
  const date = parseISO(value)
  if (!isValid(date)) {
    return null
  }

  return differenceInCalendarDays(date, today)
}

export function membershipExpiryLabel(membership: Membership, today = new Date()): string {
  if (membership.status !== 'active') {
    return ''
  }

  const days = daysUntilDate(membership.ends_at, today)
  if (days === null) {
    return ''
  }
  if (days < 0) {
    return 'Срок истёк'
  }
  if (days === 0) {
    return 'Заканчивается сегодня'
  }
  if (days <= 7) {
    return `Осталось ${days} ${pluralize(days, dayRules, {
      one: 'день',
      few: 'дня',
      many: 'дней',
    })}`
  }

  return ''
}

export function canCancelMembership(
  membership: Pick<Membership, 'status'>,
  role: UserRole | null,
): boolean {
  return role === 'admin' && (membership.status === 'active' || membership.status === 'pending')
}

export function canRefundPayment(payment: Pick<Payment, 'status'>, role: UserRole | null): boolean {
  return role === 'admin' && payment.status === 'succeeded'
}

export function paymentProviderLabel(provider: string): string {
  if (provider === 'mock') {
    return 'Демо-провайдер'
  }
  if (provider === 'manual') {
    return 'Оплата в клубе'
  }
  return provider
}
