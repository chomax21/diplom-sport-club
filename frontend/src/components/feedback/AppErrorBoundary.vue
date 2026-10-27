<script setup lang="ts">
import { RefreshCw, TriangleAlert } from '@lucide/vue'
import { onErrorCaptured, ref } from 'vue'

const error = ref<Error | null>(null)

onErrorCaptured((captured) => {
  error.value = captured instanceof Error ? captured : new Error(String(captured))
  console.error('[AppErrorBoundary]', captured)
  return false
})

function retry(): void {
  error.value = null
}

function reload(): void {
  window.location.reload()
}
</script>

<template>
  <div v-if="error" class="grid min-h-dvh place-items-center bg-slate-50 px-4">
    <div class="w-full max-w-lg rounded-3xl border border-rose-200 bg-white p-6 shadow-card sm:p-8">
      <span class="grid size-12 place-items-center rounded-2xl bg-rose-50 text-rose-600">
        <TriangleAlert :size="24" aria-hidden="true" />
      </span>
      <h1 class="mt-4 text-2xl font-bold text-slate-900">Что-то пошло не так</h1>
      <p class="mt-2 text-sm leading-6 text-slate-600">
        Интерфейс столкнулся с непредвиденной ошибкой. Можно попробовать снова или перезагрузить
        страницу.
      </p>
      <pre
        v-if="error.message"
        class="mt-4 max-h-40 overflow-auto rounded-xl bg-slate-950 p-3 text-xs leading-5 text-slate-200"
        >{{ error.message }}</pre>
      <div class="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
          @click="retry"
        >
          <RefreshCw :size="16" aria-hidden="true" />
          Попробовать снова
        </button>
        <button
          type="button"
          class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          @click="reload"
        >
          Перезагрузить страницу
        </button>
      </div>
    </div>
  </div>

  <slot v-else />
</template>
