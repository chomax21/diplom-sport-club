<script setup lang="ts">
import { Menu as HeadlessMenu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { ChevronDown, LogOut, Menu as MenuIcon, UserRound } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import ApiStatusBadge from '@/components/feedback/ApiStatusBadge.vue'
import { ROLE_BADGE_CLASSES, roleLabel, userInitials } from '@/lib/roles'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const emit = defineEmits<{
  openMenu: []
}>()

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const title = computed(() => route.meta.title ?? 'Панель управления')
const description = computed(() => route.meta.description ?? '')
const initials = computed(() => userInitials(auth.user?.full_name))
const roleBadgeClass = computed(() =>
  auth.role ? ROLE_BADGE_CLASSES[auth.role] : 'bg-slate-100 text-slate-600',
)

async function logout(): Promise<void> {
  auth.logout()
  toast.info('Сессия завершена.', 'Вы вышли из аккаунта')
  await router.replace({ name: 'login' })
}
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-slate-200 bg-white/85 backdrop-blur">
    <div class="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
      <button
        id="mobile-menu-trigger"
        type="button"
        class="grid size-11 shrink-0 place-items-center rounded-xl border border-slate-200 text-slate-600 transition hover:bg-slate-100 lg:hidden"
        aria-label="Открыть меню навигации"
        @click="emit('openMenu')"
      >
        <MenuIcon :size="20" aria-hidden="true" />
      </button>

      <div class="min-w-0 flex-1">
        <h1 class="truncate text-base font-semibold text-slate-900 sm:text-lg">{{ title }}</h1>
        <p v-if="description" class="hidden truncate text-xs text-slate-500 sm:block">
          {{ description }}
        </p>
      </div>

      <div class="hidden sm:block">
        <ApiStatusBadge />
      </div>

      <HeadlessMenu as="div" class="relative shrink-0">
        <MenuButton
          class="flex min-h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-2 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          <span class="sr-only">Меню профиля</span>
          <span
            class="grid size-7 shrink-0 place-items-center rounded-full bg-brand-50 text-[11px] font-bold text-brand-700"
          >
            {{ initials }}
          </span>
          <span class="hidden max-w-40 truncate sm:inline lg:max-w-52">{{
            auth.user?.full_name ?? 'Профиль'
          }}</span>
          <ChevronDown :size="14" class="hidden text-slate-400 sm:block" aria-hidden="true" />
        </MenuButton>

        <Transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="scale-95 opacity-0"
          enter-to-class="scale-100 opacity-100"
          leave-active-class="transition duration-75 ease-in"
          leave-from-class="scale-100 opacity-100"
          leave-to-class="scale-95 opacity-0"
        >
          <MenuItems
            class="absolute right-0 mt-2 w-64 origin-top-right rounded-2xl border border-slate-200 bg-white p-1.5 shadow-card focus:outline-none"
          >
            <div v-if="auth.user" class="border-b border-slate-100 px-3 py-2.5">
              <p class="truncate text-sm font-semibold text-slate-900">{{ auth.user.full_name }}</p>
              <p class="mt-0.5 truncate text-xs text-slate-500">{{ auth.user.email }}</p>
              <span
                :class="[
                  'mt-2 inline-flex rounded-full px-2 py-0.5 text-[11px] font-semibold',
                  roleBadgeClass,
                ]"
              >
                {{ roleLabel(auth.role) }}
              </span>
            </div>

            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/app/profile"
                :class="[
                  'mt-1 flex min-h-11 items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-700',
                  active ? 'bg-slate-100' : '',
                ]"
              >
                <UserRound :size="16" aria-hidden="true" />
                Профиль
              </RouterLink>
            </MenuItem>

            <MenuItem v-slot="{ active }">
              <button
                type="button"
                :class="[
                  'flex min-h-11 w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-rose-600',
                  active ? 'bg-rose-50' : '',
                ]"
                @click="logout"
              >
                <LogOut :size="16" aria-hidden="true" />
                Выйти
              </button>
            </MenuItem>
          </MenuItems>
        </Transition>
      </HeadlessMenu>
    </div>
  </header>
</template>
