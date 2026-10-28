import type { UserRole } from '@/api/types'

export function hasRoleAccess(
  requiredRoles: readonly UserRole[] | undefined,
  role: UserRole | null,
): boolean {
  if (!requiredRoles || requiredRoles.length === 0) {
    return true
  }

  return role !== null && requiredRoles.includes(role)
}
