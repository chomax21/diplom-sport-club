import 'vue-router'

import type { UserRole } from '@/api/types'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    description?: string
    stage?: string
    requiresAuth?: boolean
    guestOnly?: boolean
    roles?: UserRole[]
  }
}
