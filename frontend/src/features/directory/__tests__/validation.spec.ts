import { describe, expect, it } from 'vitest'

import {
  clientEditSchema,
  createUserFormSchema,
  roomFormSchema,
  trainerEditSchema,
} from '../validation'
import {
  USER_ROLE_OPTIONS,
  profileLabelForRole,
  roomCapacityLabel,
  userStatusLabel,
} from '../utils'

const validUser = {
  email: 'new.user@example.com',
  password: 'Password123',
  password_confirm: 'Password123',
  full_name: 'Иван Петров',
  phone: '+7 900 000-00-00',
  role: 'client',
}

describe('directory validation', () => {
  it('accepts a valid client card', () => {
    const result = clientEditSchema.safeParse({
      full_name: 'Анна Клиентова',
      phone: '+7 900 111-22-33',
      birth_date: '1995-04-12',
      emergency_contact: 'Мария, +7 900 222-33-44',
      notes: 'Предпочитает утренние тренировки.',
    })

    expect(result.success).toBe(true)
  })

  it('rejects a too short client name', () => {
    const result = clientEditSchema.safeParse({
      full_name: 'А',
      phone: '',
      birth_date: null,
      emergency_contact: '',
      notes: '',
    })

    expect(result.success).toBe(false)
  })

  it('validates trainer profile fields', () => {
    const result = trainerEditSchema.safeParse({
      full_name: 'Иван Тренеров',
      phone: '',
      specialization: 'Функциональный тренинг',
      bio: 'Опыт более 7 лет.',
    })

    expect(result.success).toBe(true)
  })

  it('validates room capacity boundaries', () => {
    expect(
      roomFormSchema.safeParse({
        name: 'Зал 2',
        capacity: '12',
        description: '',
        is_active: true,
      }).success,
    ).toBe(true)

    expect(
      roomFormSchema.safeParse({
        name: 'Зал 2',
        capacity: '0',
        description: '',
        is_active: true,
      }).success,
    ).toBe(false)
  })

  it('requires matching passwords when creating a user', () => {
    const schema = createUserFormSchema({ editing: false })
    expect(schema.safeParse(validUser).success).toBe(true)

    const mismatch = schema.safeParse({
      ...validUser,
      password_confirm: 'AnotherPassword123',
    })
    expect(mismatch.success).toBe(false)
    const mismatchPaths = mismatch.success
      ? []
      : mismatch.error.issues.map((issue) => issue.path.join('.'))
    expect(mismatchPaths).toContain('password_confirm')

    const shortPassword = schema.safeParse({ ...validUser, password: 'short' })
    expect(shortPassword.success).toBe(false)
  })

  it('skips email and password checks when editing a user', () => {
    const schema = createUserFormSchema({ editing: true })
    const result = schema.safeParse({
      email: '',
      password: '',
      password_confirm: '',
      full_name: 'Иван Петров',
      phone: '',
      role: 'trainer',
    })

    expect(result.success).toBe(true)
  })

  it('rejects an unknown role', () => {
    const schema = createUserFormSchema({ editing: false })
    const result = schema.safeParse({ ...validUser, role: 'owner' })

    expect(result.success).toBe(false)
  })
})

describe('directory helpers', () => {
  it('exposes all three roles in a stable order', () => {
    expect(USER_ROLE_OPTIONS.map((option) => option.value)).toEqual(['admin', 'trainer', 'client'])
  })

  it('explains automatic profile creation by role', () => {
    expect(profileLabelForRole('client')).toContain('профиль клиента')
    expect(profileLabelForRole('trainer')).toContain('профиль тренера')
    expect(profileLabelForRole('admin')).toContain('не создаётся')
  })

  it('pluralizes room capacity', () => {
    expect(roomCapacityLabel(1)).toBe('1 место')
    expect(roomCapacityLabel(3)).toBe('3 места')
    expect(roomCapacityLabel(12)).toBe('12 мест')
  })

  it('labels account status', () => {
    expect(userStatusLabel(true)).toBe('Активен')
    expect(userStatusLabel(false)).toBe('Заблокирован')
  })
})
