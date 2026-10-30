<script setup lang="ts">
import { CircleCheck, CircleX, Info, TriangleAlert, X } from '@lucide/vue'
import { storeToRefs } from 'pinia'

import { useToastStore, type ToastType } from '@/stores/toasts'

const toastStore = useToastStore()
const { items } = storeToRefs(toastStore)

const icons = {
  success: CircleCheck,
  error: CircleX,
  warning: TriangleAlert,
  info: Info,
} satisfies Record<ToastType, unknown>

const tones: Record<ToastType, { container: string; icon: string }> = {
  success: {
    container: 'border-emerald-200 bg-emerald-50',
    icon: 'text-emerald-600',
  },
  error: {
    container: 'border-rose-200 bg-rose-50',
    icon: 'text-rose-600',
  },
  warning: {
    container: 'border-amber-200 bg-amber-50',
    icon: 'text-amber-600',
  },
  info: {
    container: 'border-sky-200 bg-sky-50',
    icon: 'text-sky-600',
  },
}
</script>

<template>
  <div
    class="pointer-events-none fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 p-4 sm:inset-x-auto sm:bottom-auto sm:right-4 sm:top-4 sm:items-end"
    aria-live="polite"
  >
    <TransitionGroup tag="div" name="toast" class="flex w-full max-w-sm flex-col gap-2">
      <div
        v-for="toast in items"
        :key="toast.id"
        :role="toast.type === 'error' ? 'alert' : 'status'"
        :class="[
          'pointer-events-auto flex w-full items-start gap-3 rounded-2xl border p-4 shadow-card',
          tones[toast.type].container,
        ]"
      >
        <component
          :is="icons[toast.type]"
          :size="20"
          :class="['mt-0.5 shrink-0', tones[toast.type].icon]"
          aria-hidden="true"
        />
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold text-slate-900">{{ toast.title }}</p>
          <p v-if="toast.message" class="mt-1 break-words text-sm leading-5 text-slate-600">
            {{ toast.message }}
          </p>
        </div>
        <button
          type="button"
          class="-m-1 grid size-11 shrink-0 place-items-center rounded-lg text-slate-400 transition hover:bg-white/70 hover:text-slate-700"
          aria-label="Закрыть уведомление"
          @click="toastStore.remove(toast.id)"
        >
          <X :size="16" aria-hidden="true" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
</style>
