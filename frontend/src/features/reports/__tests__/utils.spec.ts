import { describe, expect, it } from 'vitest'

import type { AttendanceReport, RevenueReport } from '@/api/reports'
import {
  formatAverageCheck,
  formatChartDay,
  formatCount,
  formatPercent,
  hasAttendanceData,
  hasRevenueData,
  periodLabel,
} from '../utils'

function makeAttendance(overrides: Partial<AttendanceReport> = {}): AttendanceReport {
  return {
    date_from: '2026-10-01',
    date_to: '2026-10-30',
    sessions_count: 4,
    enrollments_count: 12,
    attended_count: 9,
    no_show_count: 1,
    attendance_rate: 90,
    by_day: [],
    ...overrides,
  }
}

function makeRevenue(overrides: Partial<RevenueReport> = {}): RevenueReport {
  return {
    date_from: '2026-10-01',
    date_to: '2026-10-30',
    payments_count: 2,
    total_amount: '9000.00',
    refunded_amount: '0',
    by_membership_type: [],
    by_day: [],
    ...overrides,
  }
}

describe('report formatting', () => {
  it('formats counts and percentages for the Russian locale', () => {
    expect(formatCount(1234)).toMatch(/1\s*234/)
    expect(formatPercent(91.25)).toBe('91,3%')
    expect(formatPercent(100, 0)).toBe('100%')
  })

  it('calculates an average check', () => {
    expect(formatAverageCheck('9000.00', 2)).toBe('4500')
    expect(formatAverageCheck('9000.00', 0)).toBe('—')
  })

  it('formats the report period', () => {
    expect(periodLabel('2026-10-01', '2026-10-30')).toBe('01.10.2026 — 30.10.2026')
    expect(formatChartDay('2026-10-01')).toBe('01.10')
    expect(formatChartDay('invalid')).toBe('invalid')
  })
})

describe('report emptiness', () => {
  it('detects attendance data', () => {
    expect(hasAttendanceData(makeAttendance())).toBe(true)
    expect(hasAttendanceData(makeAttendance({ sessions_count: 0, enrollments_count: 0 }))).toBe(
      false,
    )
    expect(hasAttendanceData(null)).toBe(false)
  })

  it('detects revenue data', () => {
    expect(hasRevenueData(makeRevenue())).toBe(true)
    expect(
      hasRevenueData(
        makeRevenue({
          payments_count: 0,
          total_amount: '0',
          refunded_amount: '0',
          by_membership_type: [],
        }),
      ),
    ).toBe(false)

    expect(
      hasRevenueData(
        makeRevenue({
          payments_count: 0,
          total_amount: '0',
          refunded_amount: '500.00',
          by_membership_type: [],
        }),
      ),
    ).toBe(true)
  })
})
