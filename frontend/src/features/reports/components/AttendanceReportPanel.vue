<script setup lang="ts">
import { CalendarDays, Download, RefreshCw } from '@lucide/vue'
import { computed } from 'vue'

import type { AttendanceReportParams, DailyAttendance } from '@/api/reports'
import { getApiErrorMessage } from '@/api/errors'
import BarChart from '@/components/charts/BarChart.vue'
import {
  AppBadge,
  AppButton,
  DataTable,
  EmptyState,
  ErrorState,
  SkeletonBlock,
  type TableColumn,
  type TableRow,
} from '@/components/ui'
import { downloadCsv } from '@/lib/csv'
import { formatDateShort } from '@/lib/datetime'
import { useAttendanceReportQuery } from '../queries'
import {
  formatChartDay,
  formatCount,
  formatPercent,
  hasAttendanceData,
  periodLabel,
} from '../utils'

const props = withDefaults(
  defineProps<{
    params: AttendanceReportParams
    enabled?: boolean
  }>(),
  {
    enabled: true,
  },
)

const reportQuery = useAttendanceReportQuery(
  computed(() => props.params),
  computed(() => props.enabled),
)

const report = computed(() => reportQuery.data.value)

const chartLabels = computed(() =>
  (report.value?.by_day ?? []).map((item) => formatChartDay(item.day)),
)

const chartDatasets = computed(() => [
  {
    label: 'Записи',
    data: (report.value?.by_day ?? []).map((item) => item.enrollments),
    color: '#0ea5e9',
  },
  {
    label: 'Посещения',
    data: (report.value?.by_day ?? []).map((item) => item.attended),
    color: '#10b981',
  },
])

const metrics = computed(() => {
  const data = report.value
  return [
    { label: 'Тренировки', value: formatCount(data?.sessions_count ?? 0), hint: 'без отменённых' },
    { label: 'Записи', value: formatCount(data?.enrollments_count ?? 0), hint: 'кроме отменённых' },
    { label: 'Посещения', value: formatCount(data?.attended_count ?? 0), hint: 'отмечено' },
    { label: 'Неявки', value: formatCount(data?.no_show_count ?? 0), hint: 'отмечено' },
    {
      label: 'Посещаемость',
      value: formatPercent(data?.attendance_rate ?? 0),
      hint: 'от завершённых',
    },
  ]
})

const columns: TableColumn[] = [
  { key: 'day', label: 'Дата', hideOnMobile: true },
  { key: 'enrollments', label: 'Записи', align: 'right' },
  { key: 'attended', label: 'Посещения', align: 'right' },
]

const rows = computed<TableRow[]>(() =>
  (report.value?.by_day ?? []).map((item) => ({ ...item, id: item.day })),
)

function asDay(row: TableRow): DailyAttendance {
  return row as unknown as DailyAttendance
}

function exportCsv(): void {
  if (!report.value) {
    return
  }

  downloadCsv(`attendance-${report.value.date_from}-${report.value.date_to}.csv`, [
    ['Период', report.value.date_from, report.value.date_to],
    ['Тренировки', report.value.sessions_count],
    ['Записи', report.value.enrollments_count],
    ['Посещения', report.value.attended_count],
    ['Неявки', report.value.no_show_count],
    ['Посещаемость, %', report.value.attendance_rate],
    [],
    ['Дата', 'Записи', 'Посещения'],
    ...report.value.by_day.map((item) => [item.day, item.enrollments, item.attended]),
  ])
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="min-w-0">
        <h3 class="text-lg font-semibold text-slate-900">Посещаемость</h3>
        <p class="mt-1 text-sm text-slate-500">
          <template v-if="report">
            Период: {{ periodLabel(report.date_from, report.date_to) }}
          </template>
          <template v-else>Сводка по тренировкам и отметкам</template>
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          size="sm"
          :loading="reportQuery.isFetching.value"
          @click="reportQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="14" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton variant="outline" size="sm" :disabled="!report" @click="exportCsv">
          <template #icon>
            <Download :size="14" aria-hidden="true" />
          </template>
          CSV
        </AppButton>
      </div>
    </div>

    <div v-if="reportQuery.isPending.value" class="space-y-4">
      <div class="grid gap-3 sm:grid-cols-3 xl:grid-cols-5">
        <div
          v-for="index in 5"
          :key="index"
          class="rounded-2xl border border-slate-200 bg-white p-4"
        >
          <SkeletonBlock :lines="2" compact />
        </div>
      </div>
      <div class="rounded-card border border-slate-200 bg-white p-5">
        <SkeletonBlock :lines="5" />
      </div>
    </div>

    <ErrorState
      v-else-if="reportQuery.isError.value"
      title="Не удалось построить отчёт по посещаемости"
      :description="getApiErrorMessage(reportQuery.error.value)"
      @retry="reportQuery.refetch()"
    />

    <EmptyState
      v-else-if="report && !hasAttendanceData(report)"
      title="Данных за период нет"
      description="За выбранный период не было тренировок или записей. Измените даты и попробуйте снова."
      :icon="CalendarDays"
    />

    <template v-else-if="report">
      <div class="grid gap-3 sm:grid-cols-3 xl:grid-cols-5">
        <article
          v-for="metric in metrics"
          :key="metric.label"
          class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <p class="text-xs font-medium text-slate-500">{{ metric.label }}</p>
          <p class="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">
            {{ metric.value }}
          </p>
          <p class="mt-1 text-[11px] text-slate-400">{{ metric.hint }}</p>
        </article>
      </div>

      <section class="rounded-card border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h4 class="text-sm font-semibold text-slate-900">Динамика по дням</h4>
            <p class="mt-0.5 text-xs text-slate-500">Записи и фактические посещения</p>
          </div>
          <AppBadge tone="info">{{ chartLabels.length }} дней</AppBadge>
        </div>

        <BarChart
          v-if="chartLabels.length > 0"
          class="mt-4"
          :labels="chartLabels"
          :datasets="chartDatasets"
          aria-label="График посещаемости по дням"
        />
        <EmptyState
          v-else
          class="mt-4"
          compact
          title="Нет данных по дням"
          description="За выбранный период не было тренировок."
        />
      </section>

      <section class="space-y-2">
        <h4 class="text-sm font-semibold text-slate-900">Табличные данные</h4>
        <DataTable
          :columns="columns"
          :rows="rows"
          empty-title="Нет данных по дням"
          empty-text="За выбранный период не было тренировок."
          mobile-title-key="day"
        >
          <template #mobile-title="{ row }">
            <p class="text-sm font-semibold text-slate-900">
              {{ formatDateShort(asDay(row).day) }}
            </p>
          </template>
          <template #cell-day="{ row }">
            <span class="whitespace-nowrap font-medium text-slate-900">
              {{ formatDateShort(asDay(row).day) }}
            </span>
          </template>
          <template #cell-enrollments="{ row }">
            <span class="font-medium text-slate-900">{{ asDay(row).enrollments }}</span>
          </template>
          <template #cell-attended="{ row }">
            <span class="font-medium text-emerald-700">{{ asDay(row).attended }}</span>
          </template>
        </DataTable>
      </section>
    </template>
  </section>
</template>
