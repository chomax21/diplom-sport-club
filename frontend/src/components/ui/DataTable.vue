<script setup lang="ts">
import { computed } from 'vue'

import EmptyState from './EmptyState.vue'
import SkeletonBlock from './SkeletonBlock.vue'
import type { TableColumn, TableRow } from './types'

const props = withDefaults(
  defineProps<{
    columns: TableColumn[]
    rows: TableRow[]
    rowKey?: string
    loading?: boolean
    emptyTitle?: string
    emptyText?: string
    mobileTitleKey?: string
    mobileSubtitleKey?: string
    skeletonRows?: number
  }>(),
  {
    rowKey: 'id',
    loading: false,
    emptyTitle: 'Нет данных',
    emptyText: 'Измените фильтры или добавьте первую запись.',
    mobileTitleKey: 'name',
    skeletonRows: 5,
  },
)

const desktopColumns = computed(() => props.columns.filter((column) => !column.hideOnDesktop))
const mobileColumns = computed(() => props.columns.filter((column) => !column.hideOnMobile))

const alignClasses = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
}

function getRowKey(row: TableRow, index: number): string | number {
  const value = row[props.rowKey]

  if (typeof value === 'string' || typeof value === 'number') {
    return value
  }

  return index
}

function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }
  if (typeof value === 'boolean') {
    return value ? 'Да' : 'Нет'
  }
  if (value instanceof Date) {
    return value.toLocaleDateString('ru-RU')
  }

  return String(value)
}
</script>

<template>
  <div class="min-w-0" :aria-busy="loading || undefined">
    <div v-if="loading" class="space-y-3" role="status" aria-label="Загрузка таблицы">
      <div
        v-for="index in 3"
        :key="index"
        class="rounded-2xl border border-slate-200 bg-white p-4 md:hidden"
      >
        <SkeletonBlock :lines="2" avatar />
      </div>

      <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white md:block">
        <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
          <SkeletonBlock :lines="1" compact />
        </div>
        <div
          v-for="index in skeletonRows"
          :key="index"
          class="flex gap-4 border-b border-slate-100 px-4 py-4 last:border-b-0"
        >
          <div
            v-for="column in desktopColumns"
            :key="column.key"
            class="h-3.5 flex-1 animate-pulse rounded bg-slate-200"
          />
        </div>
      </div>
      <span class="sr-only">Загрузка данных таблицы</span>
    </div>

    <EmptyState v-else-if="rows.length === 0" :title="emptyTitle" :description="emptyText">
      <template v-if="$slots['empty-action']" #actions>
        <slot name="empty-action" />
      </template>
    </EmptyState>

    <template v-else>
      <div class="space-y-3 md:hidden">
        <article
          v-for="(row, index) in rows"
          :key="getRowKey(row, index)"
          class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <slot name="mobile-title" :row="row">
                <p class="truncate text-sm font-semibold text-slate-900">
                  {{ displayValue(row[mobileTitleKey]) }}
                </p>
                <p v-if="mobileSubtitleKey" class="mt-0.5 truncate text-xs text-slate-500">
                  {{ displayValue(row[mobileSubtitleKey]) }}
                </p>
              </slot>
            </div>
            <div class="flex shrink-0 items-center gap-1">
              <slot name="mobile-actions" :row="row" />
            </div>
          </div>

          <dl class="mt-3 space-y-2 border-t border-slate-100 pt-3">
            <div
              v-for="column in mobileColumns"
              :key="column.key"
              class="flex items-start justify-between gap-4 text-sm"
            >
              <dt class="shrink-0 text-slate-500">{{ column.label }}</dt>
              <dd class="min-w-0 text-right font-medium text-slate-900">
                <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                  {{ displayValue(row[column.key]) }}
                </slot>
              </dd>
            </div>
          </dl>
        </article>
      </div>

      <div class="hidden overflow-hidden rounded-panel border border-slate-200 bg-white md:block">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th
                  v-for="column in desktopColumns"
                  :key="column.key"
                  scope="col"
                  :class="[
                    'whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500',
                    alignClasses[column.align ?? 'left'],
                    column.headerClass,
                  ]"
                >
                  {{ column.label }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(row, index) in rows"
                :key="getRowKey(row, index)"
                class="transition hover:bg-slate-50/70"
              >
                <td
                  v-for="column in desktopColumns"
                  :key="column.key"
                  :class="[
                    'px-4 py-3 align-middle text-slate-700',
                    alignClasses[column.align ?? 'left'],
                    column.cellClass,
                  ]"
                >
                  <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                    {{ displayValue(row[column.key]) }}
                  </slot>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
