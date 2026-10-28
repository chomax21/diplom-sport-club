<script setup lang="ts">
import { ChevronLeft, ChevronRight } from '@lucide/vue'
import { computed } from 'vue'

import IconButton from './IconButton.vue'

const props = withDefaults(
  defineProps<{
    page: number
    pageSize: number
    total: number
    disabled?: boolean
  }>(),
  {
    disabled: false,
  },
)

const emit = defineEmits<{
  'update:page': [page: number]
}>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const currentPage = computed(() => Math.min(Math.max(1, props.page), totalPages.value))
const rangeStart = computed(() =>
  props.total === 0 ? 0 : (currentPage.value - 1) * props.pageSize + 1,
)
const rangeEnd = computed(() => Math.min(currentPage.value * props.pageSize, props.total))

const pages = computed<Array<number | 'left-ellipsis' | 'right-ellipsis'>>(() => {
  const total = totalPages.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, index) => index + 1)
  }

  const left = Math.max(2, currentPage.value - 1)
  const right = Math.min(total - 1, currentPage.value + 1)
  const result: Array<number | 'left-ellipsis' | 'right-ellipsis'> = [1]

  if (left > 2) {
    result.push('left-ellipsis')
  }

  for (let page = left; page <= right; page += 1) {
    result.push(page)
  }

  if (right < total - 1) {
    result.push('right-ellipsis')
  }

  result.push(total)
  return result
})

function goTo(page: number): void {
  const next = Math.min(Math.max(1, page), totalPages.value)
  if (next !== currentPage.value) {
    emit('update:page', next)
  }
}
</script>

<template>
  <nav
    class="flex flex-col gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:items-center sm:justify-between"
    aria-label="Пагинация"
  >
    <p class="text-center text-xs text-slate-500 sm:text-left">
      <template v-if="total > 0">{{ rangeStart }}–{{ rangeEnd }} из {{ total }}</template>
      <template v-else>Нет записей</template>
    </p>

    <div class="flex items-center justify-between gap-2 sm:justify-end">
      <IconButton
        label="Предыдущая страница"
        variant="outline"
        :disabled="disabled || currentPage <= 1"
        @click="goTo(currentPage - 1)"
      >
        <ChevronLeft :size="17" aria-hidden="true" />
      </IconButton>

      <span class="text-sm font-medium text-slate-600 sm:hidden">
        {{ currentPage }} / {{ totalPages }}
      </span>

      <div class="hidden items-center gap-1 sm:flex">
        <template v-for="item in pages" :key="item">
          <span
            v-if="typeof item !== 'number'"
            class="grid size-11 place-items-center text-sm text-slate-400"
            aria-hidden="true"
          >
            …
          </span>
          <button
            v-else
            type="button"
            :class="[
              'grid size-11 place-items-center rounded-control text-sm font-semibold transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
              item === currentPage
                ? 'bg-brand-600 text-white'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
            ]"
            :aria-current="item === currentPage ? 'page' : undefined"
            :aria-label="`Страница ${item}`"
            :disabled="disabled"
            @click="goTo(item)"
          >
            {{ item }}
          </button>
        </template>
      </div>

      <IconButton
        label="Следующая страница"
        variant="outline"
        :disabled="disabled || currentPage >= totalPages"
        @click="goTo(currentPage + 1)"
      >
        <ChevronRight :size="17" aria-hidden="true" />
      </IconButton>
    </div>
  </nav>
</template>
