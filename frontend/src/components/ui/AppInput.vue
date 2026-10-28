<script setup lang="ts">
import { computed, useId, useSlots } from 'vue'

import { cn } from '@/lib/cn'

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
    type?: string
    placeholder?: string
    autocomplete?: string
    inputmode?: 'none' | 'text' | 'tel' | 'url' | 'email' | 'numeric' | 'decimal' | 'search'
    disabled?: boolean
    readonly?: boolean
    required?: boolean
    size?: 'sm' | 'md'
  }>(),
  {
    type: 'text',
    size: 'md',
    disabled: false,
    readonly: false,
    required: false,
  },
)

const slots = useSlots()
const generatedId = useId()
const inputId = computed(() => props.id ?? `input-${generatedId}`)
const hintId = computed(() => `${inputId.value}-hint`)
const errorId = computed(() => `${inputId.value}-error`)
const hasPrefix = computed(() => Boolean(slots.prefix))
const hasSuffix = computed(() => Boolean(slots.suffix))

const describedBy = computed(() => {
  if (props.error) {
    return errorId.value
  }
  return props.hint ? hintId.value : undefined
})

const classes = computed(() =>
  cn(
    'block w-full rounded-control border bg-white text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500',
    props.size === 'sm' ? 'min-h-10 py-2' : 'min-h-11 py-2.5',
    hasPrefix.value ? 'pl-10' : 'pl-3.5',
    hasSuffix.value ? 'pr-10' : 'pr-3.5',
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
      <span
        v-if="hasPrefix"
        class="pointer-events-none absolute inset-y-0 left-0 grid w-10 place-items-center text-slate-400"
      >
        <slot name="prefix" />
      </span>

      <input
        :id="inputId"
        v-model="model"
        v-bind="$attrs"
        :type="type"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :inputmode="inputmode"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="classes"
        :aria-invalid="Boolean(error)"
        :aria-describedby="describedBy"
      />

      <span v-if="hasSuffix" class="absolute inset-y-0 right-0 grid w-10 place-items-center">
        <slot name="suffix" />
      </span>
    </div>

    <p v-if="error" :id="errorId" class="mt-1.5 text-xs text-rose-600">{{ error }}</p>
    <p v-else-if="hint" :id="hintId" class="mt-1.5 text-xs text-slate-400">{{ hint }}</p>
  </div>
</template>
