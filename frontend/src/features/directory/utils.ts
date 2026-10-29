import type { UserRole } from '@/api/types'
import { roleLabel } from '@/lib/roles'

export const USER_ROLE_OPTIONS: Array<{ label: string; value: UserRole }> = [
  { label: roleLabel('admin'), value: 'admin' },
  { label: roleLabel('trainer'), value: 'trainer' },
  { label: roleLabel('client'), value: 'client' },
]

export function profileLabelForRole(role: UserRole): string {
  if (role === 'client') {
    return 'Для роли «Клиент» автоматически создаётся профиль клиента.'
  }
  if (role === 'trainer') {
    return 'Для роли «Тренер» автоматически создаётся профиль тренера.'
  }
  return 'Администратору профиль клиента или тренера не создаётся.'
}

const placeRules = new Intl.PluralRules('ru-RU')

export function roomCapacityLabel(capacity: number): string {
  const category = placeRules.select(capacity)
  const form = category === 'one' ? 'место' : category === 'few' ? 'места' : 'мест'
  return `${capacity} ${form}`
}

export function userStatusLabel(isActive: boolean): string {
  return isActive ? 'Активен' : 'Заблокирован'
}
