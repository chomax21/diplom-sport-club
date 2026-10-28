import type { Router } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

function safeRedirect(value: unknown): string {
  if (typeof value !== 'string' || !value.startsWith('/app')) {
    return '/app'
  }

  return value
}

export function installAuthGuards(router: Router): void {
  router.beforeEach(async (to) => {
    const auth = useAuthStore()

    if (!auth.initialized) {
      await auth.initialize()
    }

    if (to.meta.guestOnly && auth.isAuthenticated) {
      return safeRedirect(to.query.redirect)
    }

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return {
        name: 'login',
        query: { redirect: to.fullPath },
        replace: true,
      }
    }

    if (to.meta.roles?.length && !auth.hasRole(to.meta.roles)) {
      return {
        name: 'forbidden',
        query: { from: to.fullPath },
        replace: true,
      }
    }

    return true
  })
}
