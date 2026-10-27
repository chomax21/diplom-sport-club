<script setup lang="ts">
import { CircleCheck, LoaderCircle, WifiOff } from '@lucide/vue'
import { computed } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import { useHealthQuery } from '@/composables/useHealthQuery'

const { data, error, isPending, isError, isFetching, refetch } = useHealthQuery()

const state = computed(() => {
  if (isPending.value) {
    return 'pending'
  }
  return isError.value ? 'error' : 'success'
})

const tone = computed(() => {
  if (state.value === 'pending') {
    return 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100'
  }
  if (state.value === 'error') {
    return 'border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100'
  }
  return 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
})

const label = computed(() => {
  if (state.value === 'pending') {
    return 'API…'
  }
  return state.value === 'error' ? 'API недоступен' : 'API доступен'
})

const icon = computed(() => {
  if (state.value === 'pending') {
    return LoaderCircle
  }
  return state.value === 'error' ? WifiOff : CircleCheck
})

const tooltip = computed(() => {
  if (state.value === 'pending') {
    return 'Проверка доступности API'
  }
  if (state.value === 'error') {
    return getApiErrorMessage(error.value)
  }
  return `API ${data.value?.version ?? ''} · БД: ${data.value?.database ?? 'ok'}`.trim()
})
</script>

<template>
  <button
    type="button"
    :class="[
      'inline-flex min-h-9 shrink-0 items-center gap-2 rounded-full border px-2.5 py-1.5 text-xs font-medium transition',
      tone,
    ]"
    :title="tooltip"
    :aria-label="tooltip"
    @click="refetch()"
  >
    <component :is="icon" :size="14" :class="isFetching ? 'animate-spin' : ''" aria-hidden="true" />
    <span class="hidden sm:inline">{{ label }}</span>
  </button>
</template>
