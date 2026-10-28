import { describe, expect, it } from 'vitest'

import { cn } from '../cn'

describe('cn', () => {
  it('joins strings and skips empty values', () => {
    expect(cn('flex', null, undefined, false, 'gap-2')).toBe('flex gap-2')
  })

  it('flattens arrays and object conditions', () => {
    expect(cn(['rounded-lg', ['p-3']], { 'bg-white': true, 'opacity-50': false })).toBe(
      'rounded-lg p-3 bg-white',
    )
  })
})
