<script setup lang="ts">
import {
  ArrowRight,
  CalendarDays,
  ChartColumn,
  CheckCircle2,
  CreditCard,
  RefreshCw,
  Users,
  Wallet,
} from '@lucide/vue'
import { RouterLink } from 'vue-router'

import ApiStatusBadge from '@/components/feedback/ApiStatusBadge.vue'
import { useHealthQuery } from '@/composables/useHealthQuery'
import { useToastStore } from '@/stores/toasts'

const { data, isFetching, refetch } = useHealthQuery()
const toast = useToastStore()

const metrics = [
  {
    label: 'Клиенты',
    value: '—',
    hint: 'появится в F6',
    icon: Users,
    tone: 'bg-sky-50 text-sky-700',
  },
  {
    label: 'Тренировки',
    value: '—',
    hint: 'появится в F4',
    icon: CalendarDays,
    tone: 'bg-brand-50 text-brand-700',
  },
  {
    label: 'Абонементы',
    value: '—',
    hint: 'появится в F5',
    icon: CreditCard,
    tone: 'bg-violet-50 text-violet-700',
  },
  {
    label: 'Выручка',
    value: '—',
    hint: 'появится в F7',
    icon: Wallet,
    tone: 'bg-amber-50 text-amber-700',
  },
]

const quickLinks = [
  {
    to: '/app/schedule',
    title: 'Расписание',
    text: 'Тренировки, залы и запись',
    icon: CalendarDays,
  },
  {
    to: '/app/clients',
    title: 'Клиенты',
    text: 'Профили и абонементы',
    icon: Users,
  },
  {
    to: '/app/payments',
    title: 'Платежи',
    text: 'История и возвраты',
    icon: Wallet,
  },
  {
    to: '/app/reports',
    title: 'Отчёты',
    text: 'Посещаемость и выручка',
    icon: ChartColumn,
  },
]

const stageItems = [
  'Адаптивный layout: sidebar и drawer',
  'Axios-клиент с типами и ошибками',
  'TanStack Query и глобальные уведомления',
  'Error boundary и страница 404',
  'Индикатор доступности API',
]

function showToast(): void {
  toast.info(
    'Уведомления работают. Ошибки API будут появляться здесь автоматически.',
    'Проверка UI',
  )
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Этап F1</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Обзор клуба
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Каркас приложения готов: навигация, API-клиент и обработка ошибок. Реальные данные
          появятся на следующих этапах.
        </p>
      </div>
      <button
        type="button"
        class="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        @click="showToast"
      >
        Проверить уведомления
      </button>
    </section>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <article
        v-for="metric in metrics"
        :key="metric.label"
        class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm font-medium text-slate-500">{{ metric.label }}</p>
            <p class="mt-2 text-3xl font-bold tracking-tight text-slate-900">{{ metric.value }}</p>
          </div>
          <span :class="['grid size-10 shrink-0 place-items-center rounded-2xl', metric.tone]">
            <component :is="metric.icon" :size="20" aria-hidden="true" />
          </span>
        </div>
        <p class="mt-3 text-xs text-slate-400">{{ metric.hint }}</p>
      </article>
    </section>

    <div class="grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,0.6fr)]">
      <section class="min-w-0 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex flex-wrap items-end justify-between gap-2">
          <div>
            <h3 class="text-lg font-semibold text-slate-900">Быстрый доступ</h3>
            <p class="mt-1 text-sm text-slate-500">Основные разделы клуба</p>
          </div>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            9 разделов
          </span>
        </div>

        <div class="mt-5 grid gap-3 sm:grid-cols-2">
          <RouterLink
            v-for="link in quickLinks"
            :key="link.to"
            :to="link.to"
            class="group flex min-h-24 items-start gap-3 rounded-2xl border border-slate-200 p-4 transition hover:border-brand-200 hover:bg-brand-50/40"
          >
            <span
              class="grid size-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-600 transition group-hover:bg-white group-hover:text-brand-700"
            >
              <component :is="link.icon" :size="19" aria-hidden="true" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="flex items-center justify-between gap-2">
                <span class="text-sm font-semibold text-slate-900">{{ link.title }}</span>
                <ArrowRight
                  :size="15"
                  class="shrink-0 text-slate-300 transition group-hover:text-brand-600"
                  aria-hidden="true"
                />
              </span>
              <span class="mt-1 block text-xs leading-5 text-slate-500">{{ link.text }}</span>
            </span>
          </RouterLink>
        </div>
      </section>

      <div class="min-w-0 space-y-6">
        <section class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <h3 class="text-sm font-semibold text-slate-900">Состояние API</h3>
              <p class="mt-1 text-xs text-slate-500">GET /health</p>
            </div>
            <ApiStatusBadge />
          </div>

          <dl class="mt-4 grid grid-cols-2 gap-3">
            <div class="rounded-2xl bg-slate-50 p-3">
              <dt class="text-xs text-slate-500">Версия</dt>
              <dd class="mt-1 truncate text-sm font-semibold text-slate-900">
                {{ data?.version ?? '—' }}
              </dd>
            </div>
            <div class="rounded-2xl bg-slate-50 p-3">
              <dt class="text-xs text-slate-500">База данных</dt>
              <dd class="mt-1 truncate text-sm font-semibold text-slate-900">
                {{ data?.database ?? '—' }}
              </dd>
            </div>
          </dl>

          <button
            type="button"
            class="mt-4 inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-60"
            :disabled="isFetching"
            @click="refetch()"
          >
            <RefreshCw :size="15" :class="isFetching ? 'animate-spin' : ''" aria-hidden="true" />
            Проверить снова
          </button>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="text-sm font-semibold text-slate-900">Готово в F1</h3>
          <ul class="mt-4 space-y-2.5">
            <li
              v-for="item in stageItems"
              :key="item"
              class="flex items-start gap-2.5 text-sm leading-5 text-slate-600"
            >
              <CheckCircle2
                :size="16"
                class="mt-0.5 shrink-0 text-emerald-600"
                aria-hidden="true"
              />
              <span>{{ item }}</span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>
