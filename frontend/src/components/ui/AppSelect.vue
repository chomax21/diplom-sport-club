<script setup lang="ts">
import { ChevronDown } from '@lucide/vue'
import { computed, useId } from 'vue'

import { cn } from '@/lib/cn'
import type { SelectOption } from './types'

defineOptions({
  inheritAttrs: false,
})

const model = defineModel<string | number>({ default: '' })

const props = withDefaults(
  defineProps<{
    id?: string
    label?: string
    hint?: string
    error?: string | null
    placeholder?: string
    options: SelectOption[]
    disabled?: boolean
    required?: boolean
    size?: 'sm' | 'md'
  }>(),
  {
    disabled: false,
    required: false,
    size: 'md',
  },
)

const generatedId = useId()
const inputId = computed(() => props.id ?? `select-${generatedId}`)
const hintId = computed(() => `${inputId.value}-hint`)
const errorId = computed(() => `${inputId.value}-error`)
const describedBy = computed(() => {
  if (props.error) {
    return errorId.value
  }
  return props.hint ? hintId.value : undefined
})

const classes = computed(() =>
  cn(
    'block w-full appearance-none rounded-control border bg-white pl-3.5 pr-10 text-sm text-slate-900 shadow-sm outline-none transition disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500',
    props.size === 'sm' ? 'min-h-11 py-2' : 'min-h-11 py-2.5',
    props.error
      ? 'border-rose-300 focus:border-rose-400 focus:ring-4 focus:ring-rose-500/10'
      : 'border-slate-300 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10',
  ),
)
</script>

<template>
  <div class="min-w-0">
    <label v-if="label" :for="inputId" class="mb-1.5 block text-sm font-medium text-slate-700">
      {{ label }}
      <span v-if="required" class="text-rose-600" aria-hidden="true">*</span>
    </label>

    <div class="relative">
      <select
        :id="inputId"
        v-model="model"
        v-bind="$attrs"
        :disabled="disabled"
        :required="required"
        :class="classes"
        :aria-invalid="Boolean(error)"
        :aria-describedby="describedBy"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>

      <ChevronDown
        :size="16"
        class="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400"
        aria-hidden="true"
      />
    </div>

    <p v-if="error" :id="errorId" class="mt-1.5 text-xs text-rose-600">{{ error }}</p>
    <p v-else-if="hint" :id="hintId" class="mt-1.5 text-xs text-slate-400">{{ hint }}</p>
  </div>
</template>
