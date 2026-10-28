<script setup lang="ts">
import { LoaderCircle } from '@lucide/vue'

withDefaults(
  defineProps<{
    label?: string
    description?: string
    compact?: boolean
  }>(),
  {
    label: 'Загрузка…',
    compact: false,
  },
)
</script>

<template>
  <div
    :class="[
      'flex flex-col items-center justify-center text-center text-slate-500',
      compact ? 'gap-2 py-6' : 'gap-3 py-10',
    ]"
    role="status"
    aria-live="polite"
  >
    <LoaderCircle
      :size="compact ? 22 : 28"
      class="animate-spin text-brand-600"
      aria-hidden="true"
    />
    <div>
      <p :class="compact ? 'text-sm font-medium' : 'text-sm font-semibold text-slate-700'">
        {{ label }}
      </p>
      <p v-if="description" class="mt-1 text-xs text-slate-400">{{ description }}</p>
    </div>
  </div>
</template>
