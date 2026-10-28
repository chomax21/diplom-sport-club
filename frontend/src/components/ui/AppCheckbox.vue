<script setup lang="ts">
import { computed, useId } from 'vue'

const model = defineModel<boolean>({ default: false })

const props = withDefaults(
  defineProps<{
    id?: string
    label: string
    hint?: string
    error?: string | null
    disabled?: boolean
    required?: boolean
  }>(),
  {
    disabled: false,
    required: false,
  },
)

const generatedId = useId()
const inputId = computed(() => props.id ?? `checkbox-${generatedId}`)
const hintId = computed(() => `${inputId.value}-hint`)
const errorId = computed(() => `${inputId.value}-error`)
const describedBy = computed(() => {
  if (props.error) {
    return errorId.value
  }
  return props.hint ? hintId.value : undefined
})
</script>

<template>
  <div class="min-w-0">
    <label
      :for="inputId"
      class="flex min-h-11 cursor-pointer items-start gap-3 rounded-control py-1.5"
      :class="disabled ? 'cursor-not-allowed opacity-60' : ''"
    >
      <input
        :id="inputId"
        v-model="model"
        type="checkbox"
        :disabled="disabled"
        :required="required"
        class="mt-0.5 size-5 shrink-0 rounded border-slate-300 accent-brand-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        :aria-invalid="Boolean(error)"
        :aria-describedby="describedBy"
      />
      <span class="min-w-0 text-sm leading-5 text-slate-700">
        {{ label }}
        <span v-if="required" class="text-rose-600" aria-hidden="true">*</span>
        <span v-if="hint && !error" :id="hintId" class="mt-0.5 block text-xs text-slate-400">
          {{ hint }}
        </span>
      </span>
    </label>
    <p v-if="error" :id="errorId" class="mt-1 text-xs text-rose-600">{{ error }}</p>
  </div>
</template>
