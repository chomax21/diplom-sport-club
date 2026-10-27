<script setup lang="ts">
import { Menu as HeadlessMenu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { ChevronDown, LogIn, Menu as MenuIcon, UserRound } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import ApiStatusBadge from '@/components/feedback/ApiStatusBadge.vue'

const emit = defineEmits<{
  openMenu: []
}>()

const route = useRoute()

const title = computed(() => route.meta.title ?? 'Панель управления')
const description = computed(() => route.meta.description ?? '')
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-slate-200 bg-white/85 backdrop-blur">
    <div class="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        class="grid size-10 shrink-0 place-items-center rounded-xl border border-slate-200 text-slate-600 transition hover:bg-slate-100 lg:hidden"
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

      <ApiStatusBadge />

      <HeadlessMenu as="div" class="relative shrink-0">
        <MenuButton
          class="flex min-h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-2 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          aria-label="Меню профиля"
        >
          <span class="grid size-7 place-items-center rounded-full bg-slate-100 text-slate-600">
            <UserRound :size="16" aria-hidden="true" />
          </span>
          <span class="hidden sm:inline">Гость</span>
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
            class="absolute right-0 mt-2 w-56 origin-top-right rounded-2xl border border-slate-200 bg-white p-1.5 shadow-card focus:outline-none"
          >
            <div class="px-3 py-2 text-xs leading-5 text-slate-500">
              Авторизация появится на этапе F2
            </div>
            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/app/profile"
                :class="[
                  'flex min-h-10 items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-700',
                  active ? 'bg-slate-100' : '',
                ]"
              >
                <UserRound :size="16" aria-hidden="true" />
                Профиль
              </RouterLink>
            </MenuItem>
            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/"
                :class="[
                  'flex min-h-10 items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-700',
                  active ? 'bg-slate-100' : '',
                ]"
              >
                <LogIn :size="16" aria-hidden="true" />
                На главную
              </RouterLink>
            </MenuItem>
          </MenuItems>
        </Transition>
      </HeadlessMenu>
    </div>
  </header>
</template>
