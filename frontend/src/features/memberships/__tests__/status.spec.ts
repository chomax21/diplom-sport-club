import { describe, expect, it } from 'vitest'

import type { Membership } from '@/api/memberships'
import {
  canCancelMembership,
  canRefundPayment,
  daysUntilDate,
  durationDaysLabel,
  membershipExpiryLabel,
  paymentProviderLabel,
  visitsLeftLabel,
} from '../status'

function makeMembership(overrides: Partial<Membership> = {}): Membership {
  return {
    id: 'membership-1',
    client_id: 'client-1',
    client_name: 'Анна Клиентова',
    membership_type_id: 'type-1',
    membership_type_name: 'Месяц (12 посещений)',
    starts_at: '2026-10-01',
    ends_at: '2026-10-31',
    visits_left: 8,
    status: 'active',
    created_at: '2026-10-01T09:00:00Z',
    ...overrides,
  }
}

describe('membership labels', () => {
  it('pluralizes visits in Russian', () => {
    expect(visitsLeftLabel(null)).toBe('Безлимит')
    expect(visitsLeftLabel(0)).toBe('Посещения закончились')
    expect(visitsLeftLabel(1)).toBe('1 посещение')
    expect(visitsLeftLabel(3)).toBe('3 посещения')
    expect(visitsLeftLabel(11)).toBe('11 посещений')
  })

  it('pluralizes duration in days', () => {
    expect(durationDaysLabel(1)).toBe('1 день')
    expect(durationDaysLabel(2)).toBe('2 дня')
    expect(durationDaysLabel(30)).toBe('30 дней')
  })

  it('calculates calendar days until a date', () => {
    expect(daysUntilDate('2026-11-03', new Date('2026-10-29T12:00:00'))).toBe(5)
    expect(daysUntilDate('2026-10-29', new Date('2026-10-29T12:00:00'))).toBe(0)
    expect(daysUntilDate('not-a-date')).toBeNull()
  })

  it('shows expiry only for an active membership', () => {
    const today = new Date('2026-10-29T12:00:00')

    expect(membershipExpiryLabel(makeMembership({ ends_at: '2026-11-02' }), today)).toBe(
      'Осталось 4 дня',
    )
    expect(membershipExpiryLabel(makeMembership({ ends_at: '2026-10-28' }), today)).toBe(
      'Срок истёк',
    )
    expect(
      membershipExpiryLabel(makeMembership({ ends_at: '2026-11-02', status: 'cancelled' }), today),
    ).toBe('')
    expect(membershipExpiryLabel(makeMembership({ ends_at: '2026-12-31' }), today)).toBe('')
  })
})

describe('membership permissions', () => {
  it('allows cancellation only to an admin for pending or active memberships', () => {
    expect(canCancelMembership(makeMembership(), 'admin')).toBe(true)
    expect(canCancelMembership(makeMembership({ status: 'pending' }), 'admin')).toBe(true)
    expect(canCancelMembership(makeMembership({ status: 'expired' }), 'admin')).toBe(false)
    expect(canCancelMembership(makeMembership(), 'client')).toBe(false)
  })

  it('allows refunds only to an admin for successful payments', () => {
    expect(canRefundPayment({ status: 'succeeded' }, 'admin')).toBe(true)
    expect(canRefundPayment({ status: 'refunded' }, 'admin')).toBe(false)
    expect(canRefundPayment({ status: 'pending' }, 'admin')).toBe(false)
    expect(canRefundPayment({ status: 'succeeded' }, 'client')).toBe(false)
  })

  it('labels payment providers for the interface', () => {
    expect(paymentProviderLabel('mock')).toBe('Демо-провайдер')
    expect(paymentProviderLabel('manual')).toBe('Оплата в клубе')
    expect(paymentProviderLabel('custom')).toBe('custom')
  })
})
