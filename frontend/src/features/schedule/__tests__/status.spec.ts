import { describe, expect, it } from 'vitest'

import type { Enrollment, TrainingSession } from '@/api/schedule'
import {
  canCancelEnrollment,
  canClientEnroll,
  findSessionEnrollment,
  getSessionAvailability,
} from '../status'

const future = new Date(Date.now() + 86_400_000).toISOString()
const past = new Date(Date.now() - 86_400_000).toISOString()

function makeSession(overrides: Partial<TrainingSession> = {}): TrainingSession {
  return {
    id: 'session-1',
    title: 'Тестовая тренировка',
    trainer_id: 'trainer-1',
    trainer_name: 'Иван Тренеров',
    room_id: 'room-1',
    room_name: 'Зал 1',
    starts_at: future,
    ends_at: future,
    capacity: 10,
    enrolled_count: 2,
    available_slots: 8,
    description: null,
    is_cancelled: false,
    created_at: past,
    ...overrides,
  }
}

function makeEnrollment(overrides: Partial<Enrollment> = {}): Enrollment {
  return {
    id: 'enrollment-1',
    session_id: 'session-1',
    client_id: 'client-1',
    client_name: 'Анна Клиентова',
    client_phone: null,
    client_email: 'anna@example.com',
    status: 'active',
    is_attended: false,
    created_at: past,
    cancelled_at: null,
    ...overrides,
  }
}

describe('session availability', () => {
  it('detects available, full, cancelled and past sessions', () => {
    expect(getSessionAvailability(makeSession())).toBe('available')
    expect(getSessionAvailability(makeSession({ available_slots: 0 }))).toBe('full')
    expect(getSessionAvailability(makeSession({ is_cancelled: true }))).toBe('cancelled')
    expect(getSessionAvailability(makeSession({ starts_at: past, ends_at: past }))).toBe('past')
  })

  it('allows enrollment only when a place is free and there is no active booking', () => {
    const session = makeSession()
    expect(canClientEnroll(session, null)).toBe(true)
    expect(canClientEnroll(session, makeEnrollment({ status: 'cancelled' }))).toBe(true)
    expect(canClientEnroll(session, makeEnrollment({ status: 'active' }))).toBe(false)
    expect(canClientEnroll(session, makeEnrollment({ status: 'attended' }))).toBe(false)
  })

  it('allows cancellation only for an active future booking', () => {
    const futureSession = makeSession()
    const pastSession = makeSession({ starts_at: past, ends_at: past })

    expect(canCancelEnrollment(futureSession, makeEnrollment())).toBe(true)
    expect(canCancelEnrollment(pastSession, makeEnrollment())).toBe(false)
    expect(canCancelEnrollment(futureSession, makeEnrollment({ status: 'attended' }))).toBe(false)
  })
})

describe('findSessionEnrollment', () => {
  it('finds an enrollment by session id', () => {
    const enrollments = [
      makeEnrollment({ id: 'other', session_id: 'session-2' }),
      makeEnrollment({ id: 'target' }),
    ]

    expect(findSessionEnrollment(enrollments, 'session-1')?.id).toBe('target')
    expect(findSessionEnrollment(enrollments, 'missing')).toBeNull()
  })
})
