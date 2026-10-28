<script setup lang="ts">
import { watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'

import AppErrorBoundary from '@/components/feedback/AppErrorBoundary.vue'
import ToastViewport from '@/components/feedback/ToastViewport.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

watch(
  () => auth.sessionExpired,
  async (expired) => {
    if (!expired) {
      return
    }

    const shouldRedirect = Boolean(route.meta.requiresAuth)
    const redirect = shouldRedirect ? route.fullPath : '/app'
    auth.acknowledgeSessionExpired()

    if (!shouldRedirect) {
      return
    }

    await router.replace({ name: 'login', query: { redirect } })
    toast.warning('Срок действия сессии истёк. Войдите снова.', 'Требуется вход')
  },
)
</script>

<template>
  <AppErrorBoundary>
    <RouterView />
  </AppErrorBoundary>
  <ToastViewport />
</template>
