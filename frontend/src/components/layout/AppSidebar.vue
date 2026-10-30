<script setup lang="ts">
import { Dumbbell, LogOut, Settings2 } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ROLE_BADGE_CLASSES, roleLabel, userInitials } from '@/lib/roles'
import { navigation, type NavItem } from '@/router/navigation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

withDefaults(
  defineProps<{
    mobile?: boolean
  }>(),
  {
    mobile: false,
  },
)

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const visibleNavigation = computed(() =>
  navigation
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => auth.hasRole(item.roles)),
    }))
    .filter((section) => section.items.length > 0),
)

const initials = computed(() => userInitials(auth.user?.full_name))
const roleBadgeClass = computed(() =>
  auth.role ? ROLE_BADGE_CLASSES[auth.role] : 'bg-slate-100 text-slate-600',
)

function isActive(item: NavItem): boolean {
  if (item.exact) {
    return route.path === item.to
  }

  return route.path === item.to || route.path.startsWith(`${item.to}/`)
}

async function logout(): Promise<void> {
  auth.logout()
  toast.info('Сессия завершена.', 'Вы вышли из аккаунта')
  await router.replace({ name: 'login' })
}
</script>

<template>
  <div class="flex h-full flex-col">
    <div
      :class="[
        'flex h-16 shrink-0 items-center border-b border-slate-200',
        mobile ? 'pl-4 pr-14' : 'px-4',
      ]"
    >
      <RouterLink to="/app" class="flex min-h-11 min-w-0 items-center gap-3">
        <span
          class="grid size-9 shrink-0 place-items-center rounded-xl bg-brand-600 text-white shadow-lg shadow-brand-600/20"
        >
          <Dumbbell :size="19" aria-hidden="true" />
        </span>
        <span class="min-w-0">
          <span class="block truncate text-sm font-semibold tracking-wide text-slate-900">
            СпортКлуб
          </span>
          <span class="block truncate text-xs text-slate-500">Панель управления</span>
        </span>
      </RouterLink>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-4" aria-label="Основная навигация">
      <div v-for="section in visibleNavigation" :key="section.title" class="mb-5 last:mb-0">
        <p class="px-3 pb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">
          {{ section.title }}
        </p>
        <ul class="space-y-1">
          <li v-for="item in section.items" :key="item.to">
            <RouterLink
              :to="item.to"
              :class="[
                'flex min-h-11 items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition',
                isActive(item)
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
              ]"
              :aria-current="isActive(item) ? 'page' : undefined"
            >
              <component
                :is="item.icon"
                :size="18"
                :stroke-width="1.8"
                class="shrink-0"
                aria-hidden="true"
              />
              <span class="truncate">{{ item.label }}</span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </nav>

    <div class="border-t border-slate-200 p-3">
      <RouterLink
        to="/app/profile"
        class="flex min-h-11 items-center gap-3 rounded-2xl bg-slate-50 p-3 transition hover:bg-slate-100"
      >
        <span class="sr-only">Открыть профиль</span>
        <span
          class="grid size-9 shrink-0 place-items-center rounded-full bg-white text-xs font-bold text-brand-700 shadow-sm"
        >
          {{ initials }}
        </span>
        <span class="min-w-0 flex-1">
          <span class="block truncate text-sm font-medium text-slate-900">
            {{ auth.user?.full_name ?? 'Пользователь' }}
          </span>
          <span
            :class="[
              'mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold',
              roleBadgeClass,
            ]"
          >
            {{ roleLabel(auth.role) }}
          </span>
        </span>
        <Settings2 :size="15" class="shrink-0 text-slate-400" aria-hidden="true" />
      </RouterLink>

      <button
        type="button"
        class="mt-2 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700"
        @click="logout"
      >
        <LogOut :size="14" aria-hidden="true" />
        Выйти из аккаунта
      </button>
    </div>
  </div>
</template>
