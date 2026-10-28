<script setup lang="ts">
import { endOfMonth, format, startOfMonth, subDays } from 'date-fns'
import { computed, watch } from 'vue'

import AppButton from './AppButton.vue'
import DatePicker from './DatePicker.vue'

const from = defineModel<string | null>('from', { default: null })
const to = defineModel<string | null>('to', { default: null })

withDefaults(
  defineProps<{
    label?: string
    hint?: string
    disabled?: boolean
    min?: string
    max?: string
  }>(),
  {
    label: 'Период',
    disabled: false,
  },
)

const iso = (date: Date): string => format(date, 'yyyy-MM-dd')

interface RangePreset {
  label: string
  from: string
  to: string
}

const presets = computed<RangePreset[]>(() => {
  const now = new Date()
  return [
    { label: 'Сегодня', from: iso(now), to: iso(now) },
    { label: '7 дней', from: iso(subDays(now, 6)), to: iso(now) },
    { label: '30 дней', from: iso(subDays(now, 29)), to: iso(now) },
    { label: 'Этот месяц', from: iso(startOfMonth(now)), to: iso(endOfMonth(now)) },
  ]
})

const rangeError = computed(() => {
  if (from.value && to.value && from.value > to.value) {
    return 'Дата начала не может быть позже даты окончания.'
  }
  return null
})

watch(from, (value) => {
  if (value && to.value && value > to.value) {
    to.value = value
  }
})

watch(to, (value) => {
  if (value && from.value && value < from.value) {
    from.value = value
  }
})

function applyPreset(preset: RangePreset): void {
  from.value = preset.from
  to.value = preset.to
}

function isPresetActive(preset: RangePreset): boolean {
  return from.value === preset.from && to.value === preset.to
}

function reset(): void {
  from.value = null
  to.value = null
}
</script>

<template>
  <fieldset class="min-w-0" :disabled="disabled">
    <legend class="mb-1.5 block text-sm font-medium text-slate-700">
      {{ label }}
      <span v-if="!from && !to" class="ml-1 font-normal text-slate-400">— не выбран</span>
    </legend>

    <div class="grid gap-3 sm:grid-cols-2">
      <DatePicker v-model="from" label="С" :max="to ?? max" :min="min" :disabled="disabled" />
      <DatePicker v-model="to" label="По" :min="from ?? min" :max="max" :disabled="disabled" />
    </div>

    <div class="mt-3 flex flex-wrap items-center gap-1.5">
      <AppButton
        v-for="preset in presets"
        :key="preset.label"
        size="sm"
        :variant="isPresetActive(preset) ? 'soft' : 'outline'"
        :disabled="disabled"
        @click="applyPreset(preset)"
      >
        {{ preset.label }}
      </AppButton>
      <AppButton v-if="from || to" size="sm" variant="ghost" :disabled="disabled" @click="reset">
        Сбросить
      </AppButton>
    </div>

    <p v-if="rangeError" class="mt-2 text-xs text-rose-600" role="alert">{{ rangeError }}</p>
    <p v-else-if="hint" class="mt-2 text-xs text-slate-400">{{ hint }}</p>
  </fieldset>
</template>
