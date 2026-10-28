import { describe, expect, it } from 'vitest'

import { hasRoleAccess } from '../permissions'
import { roleLabel, userInitials } from '../roles'

describe('hasRoleAccess', () => {
  it('allows sections without role restrictions', () => {
    expect(hasRoleAccess(undefined, 'client')).toBe(true)
    expect(hasRoleAccess([], null)).toBe(true)
  })

  it('matches only the listed roles', () => {
    expect(hasRoleAccess(['admin'], 'admin')).toBe(true)
    expect(hasRoleAccess(['admin'], 'trainer')).toBe(false)
    expect(hasRoleAccess(['admin', 'trainer'], 'trainer')).toBe(true)
    expect(hasRoleAccess(['admin', 'trainer'], 'client')).toBe(false)
  })

  it('denies restricted sections to a guest', () => {
    expect(hasRoleAccess(['admin'], null)).toBe(false)
  })
})

describe('role helpers', () => {
  it('returns Russian role labels', () => {
    expect(roleLabel('admin')).toBe('Администратор')
    expect(roleLabel('trainer')).toBe('Тренер')
    expect(roleLabel('client')).toBe('Клиент')
    expect(roleLabel(null)).toBe('Гость')
  })

  it('builds initials from the first two words', () => {
    expect(userInitials('Иван Петров')).toBe('ИП')
    expect(userInitials('Анна')).toBe('А')
    expect(userInitials('  ')).toBe('?')
    expect(userInitials(null)).toBe('?')
  })
})
