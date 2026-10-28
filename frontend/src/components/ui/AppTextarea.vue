<script setup lang="ts">
import { computed, useId } from 'vue'

import { cn } from '@/lib/cn'

defineOptions({
  inheritAttrs: false,
})

const model = defineModel<string>({ default: '' })

const props = withDefaults(
  defineProps<{
    id?: string
    label?: string
    hint?: string
    error?: string | null
    placeholder?: string
    rows?: number
    disabled?: boolean
    readonly?: boolean
    required?: boolean
  }>(),
  {
    rows: 4,
    disabled: false,
    readonly: false,
    required: false,
  },
)

const generatedId = useId()
const inputId = computed(() => props.id ?? `textarea-${generatedId}`)
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
    'block w-full resize-y rounded-control border bg-white px-3.5 py-2.5 text-sm leading-6 text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500',
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

    <textarea
      :id="inputId"
      v-model="model"
      v-bind="$attrs"
      :rows="rows"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :required="required"
      :class="classes"
      :aria-invalid="Boolean(error)"
      :aria-describedby="describedBy"
    />

    <p v-if="error" :id="errorId" class="mt-1.5 text-xs text-rose-600">{{ error }}</p>
    <p v-else-if="hint" :id="hintId" class="mt-1.5 text-xs text-slate-400">{{ hint }}</p>
  </div>
</template>
