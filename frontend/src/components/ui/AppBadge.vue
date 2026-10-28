<script setup lang="ts">
import { computed } from 'vue'

import { cn } from '@/lib/cn'

type BadgeTone = 'neutral' | 'brand' | 'success' | 'warning' | 'danger' | 'info' | 'violet'

const props = withDefaults(
  defineProps<{
    tone?: BadgeTone
    dot?: boolean
    size?: 'sm' | 'md'
  }>(),
  {
    tone: 'neutral',
    dot: false,
    size: 'sm',
  },
)

const toneClasses: Record<BadgeTone, string> = {
  neutral: 'bg-slate-100 text-slate-600',
  brand: 'bg-brand-50 text-brand-700',
  success: 'bg-emerald-50 text-emerald-700',
  warning: 'bg-amber-50 text-amber-700',
  danger: 'bg-rose-50 text-rose-700',
  info: 'bg-sky-50 text-sky-700',
  violet: 'bg-violet-50 text-violet-700',
}

const classes = computed(() =>
  cn(
    'inline-flex items-center gap-1.5 rounded-full font-semibold',
    props.size === 'sm' ? 'px-2.5 py-1 text-[11px]' : 'px-3 py-1.5 text-xs',
    toneClasses[props.tone],
  ),
)
</script>

<template>
  <span :class="classes">
    <span v-if="dot" class="size-1.5 shrink-0 rounded-full bg-current" aria-hidden="true" />
    <slot />
  </span>
</template>
