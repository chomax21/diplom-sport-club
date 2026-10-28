<script setup lang="ts">
import { computed } from 'vue'

import { cn } from '@/lib/cn'

type IconButtonVariant = 'ghost' | 'outline' | 'soft' | 'danger'
type IconButtonSize = 'sm' | 'md'

const props = withDefaults(
  defineProps<{
    label: string
    variant?: IconButtonVariant
    size?: IconButtonSize
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    loading?: boolean
  }>(),
  {
    variant: 'ghost',
    size: 'md',
    type: 'button',
    disabled: false,
    loading: false,
  },
)

const variantClasses: Record<IconButtonVariant, string> = {
  ghost: 'text-slate-500 hover:bg-slate-100 hover:text-slate-900',
  outline: 'border border-slate-300 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900',
  soft: 'bg-brand-50 text-brand-700 hover:bg-brand-100',
  danger: 'bg-rose-50 text-rose-700 hover:bg-rose-100',
}

const classes = computed(() =>
  cn(
    'inline-grid shrink-0 place-items-center rounded-control transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:cursor-not-allowed disabled:opacity-60',
    props.size === 'sm' ? 'size-11' : 'size-11',
    variantClasses[props.variant],
  ),
)
</script>

<template>
  <button
    :type="type"
    :class="classes"
    :aria-label="label"
    :title="label"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
  >
    <slot />
  </button>
</template>
