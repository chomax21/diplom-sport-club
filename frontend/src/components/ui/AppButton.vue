<script setup lang="ts">
import { LoaderCircle } from '@lucide/vue'
import { computed } from 'vue'

import { cn } from '@/lib/cn'

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'soft'
type ButtonSize = 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant
    size?: ButtonSize
    type?: 'button' | 'submit' | 'reset'
    loading?: boolean
    disabled?: boolean
    block?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    type: 'button',
    loading: false,
    disabled: false,
    block: false,
  },
)

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-brand-600 text-white shadow-sm shadow-brand-600/20 hover:bg-brand-700 active:bg-brand-800',
  secondary: 'bg-slate-900 text-white shadow-sm hover:bg-slate-800 active:bg-slate-950',
  outline:
    'border border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50',
  ghost: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
  danger:
    'bg-rose-600 text-white shadow-sm shadow-rose-600/20 hover:bg-rose-700 active:bg-rose-800',
  soft: 'bg-brand-50 text-brand-700 hover:bg-brand-100',
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'min-h-11 min-w-11 rounded-control px-3 text-xs',
  md: 'min-h-11 min-w-11 rounded-control px-4 text-sm',
  lg: 'min-h-12 min-w-12 rounded-control px-5 text-sm',
}

const classes = computed(() =>
  cn(
    'inline-flex items-center justify-center gap-2 whitespace-nowrap font-semibold transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none',
    sizeClasses[props.size],
    variantClasses[props.variant],
    props.block && 'w-full',
  ),
)
</script>

<template>
  <button
    :type="type"
    :class="classes"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
  >
    <LoaderCircle v-if="loading" :size="16" class="animate-spin" aria-hidden="true" />
    <slot v-else name="icon" />
    <slot />
    <slot name="suffix" />
  </button>
</template>
