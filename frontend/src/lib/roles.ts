import type { UserRole } from '@/api/types'

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Администратор',
  trainer: 'Тренер',
  client: 'Клиент',
}

export const ROLE_BADGE_CLASSES: Record<UserRole, string> = {
  admin: 'bg-violet-100 text-violet-700',
  trainer: 'bg-sky-100 text-sky-700',
  client: 'bg-brand-100 text-brand-700',
}

export const ROLE_DESCRIPTIONS: Record<UserRole, string> = {
  admin: 'Полный доступ к управлению клубом',
  trainer: 'Свои тренировки, клиенты и отчёты',
  client: 'Расписание, абонементы и платежи',
}

export function roleLabel(role: UserRole | null | undefined): string {
  return role ? ROLE_LABELS[role] : 'Гость'
}

export function roleDescription(role: UserRole | null | undefined): string {
  return role ? ROLE_DESCRIPTIONS[role] : 'Войдите, чтобы открыть панель'
}

export function userInitials(fullName: string | null | undefined): string {
  if (!fullName) {
    return '?'
  }

  const parts = fullName.trim().split(/\s+/).filter(Boolean).slice(0, 2)

  if (parts.length === 0) {
    return '?'
  }

  return parts.map((part) => part.charAt(0).toUpperCase()).join('')
}
