<script setup lang="ts">
import { Dumbbell, LogIn, UserRound } from '@lucide/vue'
import { RouterLink, useRoute } from 'vue-router'

import { navigation, type NavItem } from '@/router/navigation'

const route = useRoute()

withDefaults(
  defineProps<{
    mobile?: boolean
  }>(),
  {
    mobile: false,
  },
)

function isActive(item: NavItem): boolean {
  if (item.exact) {
    return route.path === item.to
  }

  return route.path === item.to || route.path.startsWith(`${item.to}/`)
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
      <RouterLink to="/" class="flex min-w-0 items-center gap-3" aria-label="На главную страницу">
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
      <div v-for="section in navigation" :key="section.title" class="mb-5 last:mb-0">
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
      <div class="rounded-2xl bg-slate-50 p-3">
        <div class="flex items-center gap-3">
          <span
            class="grid size-9 shrink-0 place-items-center rounded-full bg-slate-200 text-slate-600"
          >
            <UserRound :size="18" aria-hidden="true" />
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-slate-900">Гость</p>
            <p class="truncate text-xs text-slate-500">Авторизация — этап F2</p>
          </div>
        </div>
        <RouterLink
          to="/"
          class="mt-3 inline-flex min-h-9 w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
        >
          <LogIn :size="14" aria-hidden="true" />
          На главную
        </RouterLink>
      </div>
    </div>
  </div>
</template>
