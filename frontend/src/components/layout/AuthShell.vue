<script setup lang="ts">
import { CalendarCheck, Dumbbell, ShieldCheck, WalletCards } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = withDefaults(
  defineProps<{
    eyebrow?: string
    title: string
    subtitle: string
    width?: 'md' | 'lg'
  }>(),
  {
    eyebrow: 'Личный кабинет',
    width: 'md',
  },
)

const panelWidthClass = computed(() => (props.width === 'lg' ? 'max-w-lg' : 'max-w-md'))

const features = [
  {
    icon: CalendarCheck,
    title: 'Расписание и запись',
    text: 'Тренировки, залы, запись и посещаемость.',
  },
  {
    icon: WalletCards,
    title: 'Абонементы и оплата',
    text: 'Покупка, история платежей и возвраты.',
  },
  {
    icon: ShieldCheck,
    title: 'Три роли',
    text: 'Клиент, тренер и администратор видят своё.',
  },
]
</script>

<template>
  <div class="min-h-dvh bg-slate-50 lg:grid lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]">
    <a
      href="#auth-main"
      class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-xl focus:bg-white focus:px-4 focus:py-3 focus:text-sm focus:font-semibold focus:text-brand-700 focus:shadow-card"
    >
      Перейти к содержимому
    </a>

    <aside
      class="relative hidden overflow-hidden bg-slate-950 p-10 text-white lg:flex lg:flex-col lg:justify-between xl:p-14"
    >
      <div
        class="pointer-events-none absolute -left-24 top-1/4 size-80 rounded-full bg-brand-500/20 blur-3xl"
        aria-hidden="true"
      />
      <div
        class="pointer-events-none absolute -right-20 bottom-0 size-72 rounded-full bg-sky-500/10 blur-3xl"
        aria-hidden="true"
      />

      <RouterLink to="/" class="relative inline-flex min-h-11 items-center gap-3">
        <span
          class="grid size-11 place-items-center rounded-2xl bg-brand-600 text-white shadow-lg shadow-brand-900/40"
        >
          <Dumbbell :size="22" aria-hidden="true" />
        </span>
        <span>
          <span class="block text-sm font-semibold tracking-wide">СпортКлуб</span>
          <span class="block text-xs text-slate-300">Информационная система</span>
        </span>
      </RouterLink>

      <div class="relative max-w-md">
        <p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand-300">
          Единая панель клуба
        </p>
        <h2 class="mt-4 text-3xl font-bold leading-tight tracking-tight xl:text-4xl">
          Всё расписание, абонементы и отчёты — в одном месте
        </h2>
        <p class="mt-4 text-sm leading-6 text-slate-300">
          Войдите под своей ролью: интерфейс покажет только доступные разделы, а права дополнительно
          проверяются на сервере.
        </p>

        <ul class="mt-8 space-y-4">
          <li v-for="feature in features" :key="feature.title" class="flex items-start gap-3">
            <span
              class="grid size-9 shrink-0 place-items-center rounded-xl bg-white/10 text-brand-300"
            >
              <component :is="feature.icon" :size="18" aria-hidden="true" />
            </span>
            <span>
              <span class="block text-sm font-medium text-white">{{ feature.title }}</span>
              <span class="mt-0.5 block text-xs leading-5 text-slate-300">{{ feature.text }}</span>
            </span>
          </li>
        </ul>
      </div>

      <p class="relative text-xs text-slate-300">Дипломный проект · Vue 3 + TypeScript + FastAPI</p>
    </aside>

    <main
      id="auth-main"
      tabindex="-1"
      class="flex min-h-dvh flex-col scroll-mt-20 focus:outline-none"
    >
      <div
        class="flex items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3.5 sm:px-6 lg:hidden"
      >
        <RouterLink to="/" class="flex min-h-11 min-w-0 items-center gap-2.5">
          <span class="grid size-9 shrink-0 place-items-center rounded-xl bg-brand-600 text-white">
            <Dumbbell :size="18" aria-hidden="true" />
          </span>
          <span class="min-w-0">
            <span class="block truncate text-sm font-semibold text-slate-900">СпортКлуб</span>
            <span class="block truncate text-[11px] text-slate-500">Личный кабинет</span>
          </span>
        </RouterLink>
        <RouterLink
          to="/"
          class="inline-flex min-h-11 shrink-0 items-center rounded-xl px-3 text-xs font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
        >
          На главную
        </RouterLink>
      </div>

      <div class="flex flex-1 items-center justify-center px-4 py-10 sm:px-6">
        <div :class="['w-full', panelWidthClass]">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-brand-700">
            {{ eyebrow }}
          </p>
          <h1 class="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            {{ title }}
          </h1>
          <p class="mt-2 text-sm leading-6 text-slate-600">{{ subtitle }}</p>

          <div class="mt-7">
            <slot />
          </div>

          <div v-if="$slots.footer" class="mt-6 text-sm text-slate-600">
            <slot name="footer" />
          </div>
        </div>
      </div>

      <footer class="px-4 pb-6 text-center text-xs text-slate-400 sm:px-6">
        Информационная система спортивного клуба
      </footer>
    </main>
  </div>
</template>
