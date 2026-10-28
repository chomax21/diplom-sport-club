import type { BadgeTone } from '@/components/ui'
import type { Enrollment, TrainingSession } from '@/api/schedule'
import { isPastDate } from '@/lib/datetime'

export type SessionAvailability = 'cancelled' | 'past' | 'full' | 'available'

interface AvailabilityMeta {
  label: string
  tone: BadgeTone
}

export const SESSION_AVAILABILITY_META: Record<SessionAvailability, AvailabilityMeta> = {
  cancelled: { label: 'Отменена', tone: 'danger' },
  past: { label: 'Завершена', tone: 'neutral' },
  full: { label: 'Мест нет', tone: 'warning' },
  available: { label: 'Запись открыта', tone: 'success' },
}

export function getSessionAvailability(session: TrainingSession): SessionAvailability {
  if (session.is_cancelled) {
    return 'cancelled'
  }
  if (isPastDate(session.starts_at)) {
    return 'past'
  }
  if (session.available_slots <= 0) {
    return 'full'
  }
  return 'available'
}

export function findSessionEnrollment(
  enrollments: Enrollment[] | undefined,
  sessionId: string,
): Enrollment | null {
  return enrollments?.find((enrollment) => enrollment.session_id === sessionId) ?? null
}

export function activeEnrollmentForSession(
  enrollments: Enrollment[] | undefined,
  sessionId: string,
): Enrollment | null {
  const enrollment = findSessionEnrollment(enrollments, sessionId)
  return enrollment?.status === 'active' ? enrollment : null
}

export function canClientEnroll(session: TrainingSession, enrollment: Enrollment | null): boolean {
  return (
    getSessionAvailability(session) === 'available' &&
    (!enrollment || enrollment.status === 'cancelled')
  )
}

export function canCancelEnrollment(
  session: TrainingSession,
  enrollment: Enrollment | null,
): boolean {
  return enrollment?.status === 'active' && !session.is_cancelled && !isPastDate(session.starts_at)
}

export function isSessionPast(session: TrainingSession): boolean {
  return isPastDate(session.starts_at)
}
