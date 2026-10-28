<script setup lang="ts">
import { Search, X } from '@lucide/vue'

import AppInput from './AppInput.vue'

const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    placeholder?: string
    ariaLabel?: string
    disabled?: boolean
  }>(),
  {
    placeholder: 'Поиск…',
    ariaLabel: 'Поиск',
    disabled: false,
  },
)
</script>

<template>
  <AppInput
    v-model="model"
    type="search"
    :label="label"
    :placeholder="placeholder"
    :aria-label="ariaLabel"
    :disabled="disabled"
    autocomplete="off"
  >
    <template #prefix>
      <Search :size="17" aria-hidden="true" />
    </template>
    <template #suffix>
      <button
        v-if="model"
        type="button"
        class="grid size-9 place-items-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        aria-label="Очистить поиск"
        :disabled="disabled"
        @click="model = ''"
      >
        <X :size="15" aria-hidden="true" />
      </button>
    </template>
  </AppInput>
</template>
