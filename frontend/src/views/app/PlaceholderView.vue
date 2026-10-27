<script setup lang="ts">
import { ArrowLeft, ClipboardList } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const title = computed(() => route.meta.title ?? 'Раздел')
const description = computed(() => route.meta.description ?? 'Раздел находится в разработке.')
const stage = computed(() => route.meta.stage)
</script>

<template>
  <section class="mx-auto max-w-3xl">
    <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <div class="flex flex-wrap items-center gap-2">
        <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          {{ stage ? `Этап ${stage}` : 'В разработке' }}
        </span>
        <span class="text-xs text-slate-400">Скоро здесь появится рабочий экран</span>
      </div>

      <span class="mt-5 grid size-12 place-items-center rounded-2xl bg-brand-50 text-brand-700">
        <ClipboardList :size="24" aria-hidden="true" />
      </span>

      <h2 class="mt-4 text-2xl font-bold tracking-tight text-slate-900">{{ title }}</h2>
      <p class="mt-2 text-sm leading-6 text-slate-600">{{ description }}</p>

      <div
        class="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-500"
      >
        На этом этапе проверяются навигация, layout и состояния интерфейса. Подключение данных и
        формы появятся позже.
      </div>

      <RouterLink
        to="/app"
        class="mt-6 inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
      >
        <ArrowLeft :size="16" aria-hidden="true" />
        На дашборд
      </RouterLink>
    </div>
  </section>
</template>
