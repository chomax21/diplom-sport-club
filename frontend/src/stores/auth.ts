import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import { clearTokens, getRefreshToken } from '@/api/authToken'
import { applyTokenPair, onSessionExpired, refreshAccessToken } from '@/api/session'
import type { CurrentUser, LoginPayload, RegisterPayload, UserRole } from '@/api/types'
import { queryClient } from '@/app/queryClient'
import { hasRoleAccess } from '@/lib/permissions'

export type AuthStatus = 'idle' | 'restoring' | 'authenticating' | 'authenticated' | 'guest'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<CurrentUser | null>(null)
  const status = ref<AuthStatus>('idle')
  const initialized = ref(false)
  const sessionExpired = ref(false)

  let initPromise: Promise<void> | null = null

  const isAuthenticated = computed(() => user.value !== null)
  const role = computed<UserRole | null>(() => user.value?.role ?? null)

  function resetSession(): void {
    clearTokens()
    user.value = null
    status.value = 'guest'
    queryClient.clear()
  }

  onSessionExpired(() => {
    user.value = null
    status.value = 'guest'
    initialized.value = true
    sessionExpired.value = true
    queryClient.clear()
  })

  async function restoreSession(): Promise<void> {
    status.value = 'restoring'

    if (!getRefreshToken()) {
      status.value = 'guest'
      return
    }

    const accessToken = await refreshAccessToken(true)
    if (!accessToken) {
      user.value = null
      status.value = 'guest'
      return
    }

    try {
      user.value = await authApi.me()
      status.value = 'authenticated'
    } catch {
      resetSession()
    }
  }

  /**
   * Восстанавливает сессию после перезагрузки страницы. Повторные вызовы
   * (например, из guard'а и из компонента) используют один промис.
   */
  function initialize(): Promise<void> {
    if (initialized.value) {
      return Promise.resolve()
    }

    if (initPromise) {
      return initPromise
    }

    status.value = 'restoring'
    initPromise = restoreSession().finally(() => {
      initialized.value = true
      initPromise = null
    })

    return initPromise
  }

  async function login(payload: LoginPayload): Promise<CurrentUser> {
    status.value = 'authenticating'

    try {
      const tokens = await authApi.login(payload)
      applyTokenPair(tokens)
      user.value = await authApi.me()
      status.value = 'authenticated'
      initialized.value = true
      sessionExpired.value = false
      return user.value
    } catch (error) {
      resetSession()
      throw error
    }
  }

  async function register(payload: RegisterPayload): Promise<CurrentUser> {
    const created = await authApi.register(payload)
    await login({ email: payload.email, password: payload.password })
    return created
  }

  function logout(): void {
    resetSession()
    initialized.value = true
    sessionExpired.value = false
  }

  function hasRole(requiredRoles?: readonly UserRole[]): boolean {
    return hasRoleAccess(requiredRoles, role.value)
  }

  function acknowledgeSessionExpired(): void {
    sessionExpired.value = false
  }

  return {
    user,
    status,
    initialized,
    sessionExpired,
    isAuthenticated,
    role,
    initialize,
    login,
    register,
    logout,
    hasRole,
    acknowledgeSessionExpired,
  }
})
