<script setup lang="ts">
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  CalendarDays,
  LayoutDashboard,
  LogOut,
  Mail,
  Phone,
  ShieldCheck,
  UserRound,
} from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { ROLE_BADGE_CLASSES, roleDescription, roleLabel, userInitials } from '@/lib/roles'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const user = computed(() => auth.user)

const roleBadgeClass = computed(() =>
  auth.role ? ROLE_BADGE_CLASSES[auth.role] : 'bg-slate-100 text-slate-600',
)

const registeredAt = computed(() => {
  const value = user.value?.created_at
  if (!value) {
    return '—'
  }

  const date = parseISO(value)
  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return format(date, 'd MMMM yyyy', { locale: ru })
})

async function logout(): Promise<void> {
  auth.logout()
  toast.info('Сессия завершена. Данные для входа больше не используются.', 'Вы вышли из аккаунта')
  await router.replace({ name: 'login' })
}
</script>

<template>
  <section class="mx-auto max-w-4xl space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Учётная запись</p>
      <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Профиль</h2>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
        Данные текущей сессии. Редактирование профиля и контактов появится на этапе F6.
      </p>
    </div>

    <div v-if="user" class="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,0.7fr)]">
      <section class="min-w-0 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
          <span
            class="grid size-16 shrink-0 place-items-center rounded-2xl bg-brand-50 text-xl font-bold text-brand-700"
            aria-hidden="true"
          >
            {{ userInitials(user.full_name) }}
          </span>
          <div class="min-w-0">
            <h3 class="break-words text-xl font-bold text-slate-900">{{ user.full_name }}</h3>
            <p class="mt-1 break-all text-sm text-slate-500">{{ user.email }}</p>
            <span
              :class="[
                'mt-2 inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold',
                roleBadgeClass,
              ]"
            >
              {{ roleLabel(user.role) }}
            </span>
          </div>
        </div>

        <dl class="mt-6 grid gap-3 sm:grid-cols-2">
          <div class="rounded-2xl bg-slate-50 p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <Mail :size="14" aria-hidden="true" />
              Email
            </dt>
            <dd class="mt-1.5 break-all text-sm font-medium text-slate-900">{{ user.email }}</dd>
          </div>
          <div class="rounded-2xl bg-slate-50 p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <Phone :size="14" aria-hidden="true" />
              Телефон
            </dt>
            <dd class="mt-1.5 text-sm font-medium text-slate-900">
              {{ user.phone ?? 'Не указан' }}
            </dd>
          </div>
          <div class="rounded-2xl bg-slate-50 p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <ShieldCheck :size="14" aria-hidden="true" />
              Роль
            </dt>
            <dd class="mt-1.5 text-sm font-medium text-slate-900">{{ roleLabel(user.role) }}</dd>
          </div>
          <div class="rounded-2xl bg-slate-50 p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <CalendarDays :size="14" aria-hidden="true" />
              Дата регистрации
            </dt>
            <dd class="mt-1.5 text-sm font-medium text-slate-900">{{ registeredAt }}</dd>
          </div>
        </dl>
      </section>

      <div class="min-w-0 space-y-6">
        <section class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center gap-2.5">
            <span class="grid size-9 place-items-center rounded-xl bg-brand-50 text-brand-700">
              <UserRound :size="18" aria-hidden="true" />
            </span>
            <h3 class="text-sm font-semibold text-slate-900">Доступ</h3>
          </div>
          <p class="mt-3 text-sm leading-6 text-slate-600">{{ roleDescription(user.role) }}.</p>
          <p
            class="mt-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-3 text-xs leading-5 text-slate-500"
          >
            Меню и маршруты строятся по роли, а права повторно проверяются на бэкенде при каждом
            запросе.
          </p>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="text-sm font-semibold text-slate-900">Сессия</h3>
          <p class="mt-2 text-xs leading-5 text-slate-500">
            Access-токен хранится в памяти, refresh-токен — в localStorage. При ответе 401 клиент
            один раз обновляет пару токенов и повторяет запрос.
          </p>
          <div class="mt-4 grid gap-2">
            <RouterLink
              to="/app"
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
            >
              <LayoutDashboard :size="15" aria-hidden="true" />
              На дашборд
            </RouterLink>
            <button
              type="button"
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-100"
              @click="logout"
            >
              <LogOut :size="15" aria-hidden="true" />
              Выйти из аккаунта
            </button>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>
