<script setup lang="ts">
import { ChevronDown, SlidersHorizontal } from '@lucide/vue'
import { computed, ref, useId } from 'vue'

import AppBadge from './AppBadge.vue'
import AppButton from './AppButton.vue'

const props = withDefaults(
  defineProps<{
    activeCount?: number
    hasActiveFilters?: boolean
    columns?: 1 | 2 | 3 | 4
  }>(),
  {
    activeCount: 0,
    hasActiveFilters: false,
    columns: 4,
  },
)

const emit = defineEmits<{
  reset: []
}>()

const open = ref(false)
const panelId = `filters-${useId()}`

const gridClasses = computed(() => {
  if (props.columns === 1) {
    return 'lg:grid-cols-1'
  }
  if (props.columns === 2) {
    return 'lg:grid-cols-2'
  }
  if (props.columns === 3) {
    return 'lg:grid-cols-3'
  }
  return 'lg:grid-cols-4'
})
</script>

<template>
  <section class="rounded-panel border border-slate-200 bg-white p-3 shadow-sm sm:p-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="flex min-w-0 items-center gap-2">
        <SlidersHorizontal :size="17" class="shrink-0 text-slate-500" aria-hidden="true" />
        <h2 class="text-sm font-semibold text-slate-900">Фильтры</h2>
        <AppBadge v-if="activeCount > 0" tone="brand">{{ activeCount }}</AppBadge>
      </div>

      <div class="flex items-center gap-1.5">
        <AppButton v-if="hasActiveFilters" size="sm" variant="ghost" @click="emit('reset')">
          Сбросить
        </AppButton>
        <AppButton
          class="md:hidden"
          size="sm"
          variant="outline"
          :aria-expanded="open"
          :aria-controls="panelId"
          @click="open = !open"
        >
          <template #icon>
            <SlidersHorizontal :size="14" aria-hidden="true" />
          </template>
          {{ open ? 'Скрыть' : 'Показать' }}
          <ChevronDown
            :size="14"
            :class="['transition-transform', open ? 'rotate-180' : '']"
            aria-hidden="true"
          />
        </AppButton>
      </div>
    </div>

    <div
      :id="panelId"
      :class="['mt-3 gap-3 sm:grid-cols-2', gridClasses, open ? 'grid' : 'hidden md:grid']"
    >
      <slot />
    </div>
  </section>
</template>
