import { describe, expect, it } from 'vitest'

import { formatMoney } from '../format'

describe('formatMoney', () => {
  it('returns a placeholder for empty values', () => {
    expect(formatMoney(null)).toBe('—')
    expect(formatMoney(undefined)).toBe('—')
    expect(formatMoney('')).toBe('—')
    expect(formatMoney('not-a-number')).toBe('—')
  })

  it('formats ruble amounts', () => {
    expect(formatMoney('4500.00')).toMatch(/4\s*500/)
    expect(formatMoney(800)).toMatch(/800/)
    expect(formatMoney('1234.50')).toMatch(/1\s*234/)
  })
})
