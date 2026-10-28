<script setup lang="ts">
import { CircleAlert, RotateCw } from '@lucide/vue'

import AppButton from './AppButton.vue'

withDefaults(
  defineProps<{
    title?: string
    description?: string
    retryLabel?: string
    compact?: boolean
  }>(),
  {
    title: 'Не удалось загрузить данные',
    description: 'Проверьте соединение и попробуйте ещё раз.',
    retryLabel: 'Повторить',
    compact: false,
  },
)

const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <div
    :class="[
      'flex flex-col items-center justify-center rounded-2xl border border-rose-200 bg-rose-50/70 text-center',
      compact ? 'px-4 py-6' : 'px-5 py-10',
    ]"
    role="alert"
  >
    <span
      :class="[
        'grid place-items-center rounded-2xl bg-white text-rose-600 shadow-sm',
        compact ? 'size-10' : 'size-12',
      ]"
      aria-hidden="true"
    >
      <CircleAlert :size="compact ? 19 : 23" />
    </span>
    <h3 :class="['font-semibold text-slate-900', compact ? 'mt-3 text-sm' : 'mt-4 text-base']">
      {{ title }}
    </h3>
    <p :class="['max-w-md text-sm leading-6 text-slate-600', compact ? 'mt-1' : 'mt-1.5']">
      {{ description }}
    </p>
    <div class="mt-4 flex flex-wrap justify-center gap-2">
      <slot name="actions">
        <AppButton variant="outline" size="sm" @click="emit('retry')">
          <template #icon>
            <RotateCw :size="14" aria-hidden="true" />
          </template>
          {{ retryLabel }}
        </AppButton>
      </slot>
    </div>
  </div>
</template>
