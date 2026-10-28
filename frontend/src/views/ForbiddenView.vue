<script setup lang="ts">
import { ArrowLeft, LayoutDashboard, LogIn, ShieldAlert, UserRound } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ROLE_BADGE_CLASSES, roleDescription, roleLabel, userInitials } from '@/lib/roles'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const attemptedPath = computed(() => {
  const value = route.query.from
  return typeof value === 'string' && value.startsWith('/app') ? value : null
})

const roleBadgeClass = computed(() =>
  auth.role ? ROLE_BADGE_CLASSES[auth.role] : 'bg-slate-100 text-slate-600',
)

async function switchAccount(): Promise<void> {
  auth.logout()
  toast.info('Войдите под учётной записью с нужными правами.', 'Смена пользователя')
  await router.replace({ name: 'login' })
}
</script>

<template>
  <main class="grid min-h-dvh place-items-center bg-slate-50 px-4 py-10">
    <div
      class="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-6 shadow-card sm:p-8"
    >
      <div class="flex items-center justify-between gap-3">
        <span
          class="grid size-12 place-items-center rounded-2xl bg-amber-50 text-amber-700"
          aria-hidden="true"
        >
          <ShieldAlert :size="24" />
        </span>
        <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          403 · нет доступа
        </span>
      </div>

      <h1 class="mt-5 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
        Недостаточно прав
      </h1>
      <p class="mt-2 text-sm leading-6 text-slate-600">
        Этот раздел недоступен для вашей роли. Пункты меню и маршруты ограничены, а сервер
        дополнительно проверяет каждое действие.
      </p>

      <div v-if="auth.user" class="mt-5 flex items-center gap-3 rounded-2xl bg-slate-50 p-3.5">
        <span
          class="grid size-10 shrink-0 place-items-center rounded-full bg-slate-200 text-sm font-semibold text-slate-600"
        >
          {{ userInitials(auth.user.full_name) }}
        </span>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-slate-900">{{ auth.user.full_name }}</p>
          <p class="truncate text-xs text-slate-500">{{ roleDescription(auth.role) }}</p>
        </div>
        <span
          :class="['shrink-0 rounded-full px-2.5 py-1 text-[11px] font-semibold', roleBadgeClass]"
        >
          {{ roleLabel(auth.role) }}
        </span>
      </div>

      <p
        v-if="attemptedPath"
        class="mt-4 break-all rounded-xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 font-mono text-xs text-slate-500"
      >
        Запрошенный раздел: {{ attemptedPath }}
      </p>

      <div class="mt-6 flex flex-col gap-3 sm:flex-row">
        <RouterLink
          v-if="auth.isAuthenticated"
          to="/app"
          class="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          <LayoutDashboard :size="16" aria-hidden="true" />
          На дашборд
        </RouterLink>
        <RouterLink
          v-else
          to="/login"
          class="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          <LogIn :size="16" aria-hidden="true" />
          Войти
        </RouterLink>

        <button
          v-if="auth.isAuthenticated"
          type="button"
          class="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          @click="switchAccount"
        >
          <UserRound :size="16" aria-hidden="true" />
          Сменить пользователя
        </button>
        <RouterLink
          v-else
          to="/"
          class="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          <ArrowLeft :size="16" aria-hidden="true" />
          На главную
        </RouterLink>
      </div>
    </div>
  </main>
</template>
