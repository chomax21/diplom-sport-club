<script setup lang="ts">
import { Inbox } from '@lucide/vue'
import { computed, type Component } from 'vue'

const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    icon?: Component
    compact?: boolean
  }>(),
  {
    title: 'Пока пусто',
    description: 'Когда появятся данные, они отобразятся здесь.',
    compact: false,
  },
)

const resolvedIcon = computed(() => props.icon ?? Inbox)
</script>

<template>
  <div
    :class="[
      'flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/70 text-center',
      compact ? 'px-4 py-6' : 'px-5 py-10',
    ]"
    role="status"
  >
    <span
      :class="[
        'grid place-items-center rounded-2xl bg-white text-slate-400 shadow-sm',
        compact ? 'size-10' : 'size-12',
      ]"
      aria-hidden="true"
    >
      <component :is="resolvedIcon" :size="compact ? 19 : 23" />
    </span>
    <h3 :class="['font-semibold text-slate-900', compact ? 'mt-3 text-sm' : 'mt-4 text-base']">
      {{ title }}
    </h3>
    <p :class="['max-w-md text-sm leading-6 text-slate-500', compact ? 'mt-1' : 'mt-1.5']">
      {{ description }}
    </p>
    <div v-if="$slots.actions" class="mt-4 flex flex-wrap justify-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>
