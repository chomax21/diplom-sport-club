<script setup lang="ts">
import { ArrowLeft, LayoutDashboard } from '@lucide/vue'
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="grid min-h-dvh place-items-center bg-slate-50 px-4">
    <div
      class="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-card"
    >
      <p class="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">404</p>
      <h1 class="mt-2 text-2xl font-bold text-slate-900">Страница не найдена</h1>
      <p class="mt-2 text-sm leading-6 text-slate-600">
        Возможно, ссылка устарела или раздел ещё в разработке.
      </p>
      <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
        <RouterLink
          to="/"
          class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          <ArrowLeft :size="16" aria-hidden="true" />
          На главную
        </RouterLink>
        <RouterLink
          to="/app"
          class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          <LayoutDashboard :size="16" aria-hidden="true" />
          В панель
        </RouterLink>
      </div>
    </div>
  </main>
</template>
