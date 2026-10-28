<script setup lang="ts">
import {
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  CheckCircle2,
  Dumbbell,
  Server,
  ShieldCheck,
  UserPlus,
  Users,
  Wallet,
} from '@lucide/vue'
import { RouterLink } from 'vue-router'

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
const apiRoot = apiUrl.replace(/\/api\/v1\/?$/, '')

const stack = [
  'Vue 3',
  'TypeScript',
  'Vite',
  'Tailwind CSS',
  'Pinia',
  'Vue Router',
  'TanStack Query',
]

const features = [
  {
    icon: CalendarDays,
    title: 'Расписание',
    text: 'Групповые тренировки, залы, запись и отметки посещения.',
  },
  {
    icon: Users,
    title: 'Клиенты и тренеры',
    text: 'Профили, роли и административное управление.',
  },
  {
    icon: Wallet,
    title: 'Абонементы и платежи',
    text: 'Покупка, отмена, история платежей и возвраты.',
  },
  {
    icon: ShieldCheck,
    title: 'Три роли',
    text: 'Отдельные сценарии для администратора, тренера и клиента.',
  },
]

const nextSteps = [
  'F3 — адаптивный UI-кит',
  'F4 — расписание и запись',
  'F5 — абонементы и платежи',
]
</script>

<template>
  <div class="min-h-dvh bg-slate-50">
    <header class="border-b border-slate-200/80 bg-white/85 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div class="flex min-w-0 items-center gap-3">
          <span
            class="grid size-10 shrink-0 place-items-center rounded-2xl bg-brand-600 text-white shadow-lg shadow-brand-600/20"
          >
            <Dumbbell :size="22" aria-hidden="true" />
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold tracking-wide text-slate-900">СпортКлуб</p>
            <p class="truncate text-xs text-slate-500">Информационная система</p>
          </div>
        </div>

        <span
          class="shrink-0 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
        >
          F2 · вход и роли
        </span>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-4 pb-16 pt-8 sm:px-6 lg:pt-14">
      <section
        class="grid min-w-0 gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] lg:items-center"
      >
        <div class="min-w-0">
          <p class="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">
            Дипломный проект
          </p>
          <h1
            class="mt-3 break-words text-3xl font-bold leading-tight tracking-tight text-slate-900 sm:text-4xl lg:text-5xl"
          >
            Адаптивный интерфейс спортивного клуба
          </h1>
          <p class="mt-4 max-w-2xl text-base leading-7 text-slate-600">
            Клиенты, тренеры, абонементы, расписание, посещаемость и платежи — единая панель для
            трёх ролей. Вход, регистрация и защищённые маршруты уже работают, дальше — рабочие
            экраны.
          </p>

          <div class="mt-6 flex flex-wrap gap-2">
            <span
              v-for="item in stack"
              :key="item"
              class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700"
            >
              {{ item }}
            </span>
          </div>

          <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <RouterLink
              to="/login"
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition hover:bg-brand-700"
            >
              Войти в панель
              <ArrowRight :size="16" aria-hidden="true" />
            </RouterLink>
            <RouterLink
              to="/register"
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Создать аккаунт
              <UserPlus :size="16" aria-hidden="true" />
            </RouterLink>
            <a
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
              :href="`${apiRoot}/docs`"
              target="_blank"
              rel="noreferrer"
            >
              Открыть API
              <ArrowUpRight :size="16" aria-hidden="true" />
            </a>
            <a
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
              href="https://github.com/chomax21/diplom-sport-club/blob/main/ROADMAP.md"
              target="_blank"
              rel="noreferrer"
            >
              План разработки
            </a>
          </div>
        </div>

        <div class="grid min-w-0 gap-4 sm:grid-cols-2 lg:grid-cols-1">
          <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
            <div class="flex items-center gap-3">
              <span class="grid size-10 place-items-center rounded-xl bg-brand-50 text-brand-700">
                <Server :size="20" aria-hidden="true" />
              </span>
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-900">API</p>
                <p class="truncate text-xs text-slate-500">FastAPI + PostgreSQL</p>
              </div>
            </div>
            <p class="mt-4 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-600">
              {{ apiUrl }}
            </p>
          </div>

          <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
            <div class="flex items-center gap-3">
              <span
                class="grid size-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700"
              >
                <CheckCircle2 :size="20" aria-hidden="true" />
              </span>
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-900">Этап F2</p>
                <p class="truncate text-xs text-slate-500">Вход, роли и сессия</p>
              </div>
            </div>
            <ul class="mt-4 space-y-2 text-sm text-slate-600">
              <li v-for="step in nextSteps" :key="step" class="flex gap-2">
                <span class="mt-2 size-1.5 shrink-0 rounded-full bg-brand-500" />
                <span>{{ step }}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section class="mt-14">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold text-slate-900">Что будет в интерфейсе</h2>
            <p class="mt-1 text-sm text-slate-600">Основные модули системы</p>
          </div>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            mobile-first
          </span>
        </div>

        <div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <article
            v-for="feature in features"
            :key="feature.title"
            class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <span class="grid size-11 place-items-center rounded-2xl bg-slate-100 text-slate-700">
              <component :is="feature.icon" :size="21" aria-hidden="true" />
            </span>
            <h3 class="mt-4 text-base font-semibold text-slate-900">{{ feature.title }}</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">{{ feature.text }}</p>
          </article>
        </div>
      </section>
    </main>

    <footer class="border-t border-slate-200 bg-white">
      <div
        class="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6"
      >
        <p>Информационная система спортивного клуба · дипломный проект</p>
        <p>Vue 3 + TypeScript + Tailwind CSS</p>
      </div>
    </footer>
  </div>
</template>
