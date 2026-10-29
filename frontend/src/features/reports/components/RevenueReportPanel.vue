<script setup lang="ts">
import { Download, RefreshCw, Wallet } from '@lucide/vue'
import { computed } from 'vue'

import type { ReportPeriodParams, RevenueByMembershipType } from '@/api/reports'
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
import { formatMoney } from '@/lib/format'
import { useRevenueReportQuery } from '../queries'
import {
  formatAverageCheck,
  formatChartDay,
  formatCount,
  formatPercent,
  hasRevenueData,
  periodLabel,
} from '../utils'

const props = withDefaults(
  defineProps<{
    params: ReportPeriodParams
    enabled?: boolean
  }>(),
  {
    enabled: true,
  },
)

const reportQuery = useRevenueReportQuery(
  computed(() => props.params),
  computed(() => props.enabled),
)

const report = computed(() => reportQuery.data.value)

const chartLabels = computed(() =>
  (report.value?.by_day ?? []).map((item) => formatChartDay(item.day)),
)

const chartDatasets = computed(() => [
  {
    label: 'Выручка, ₽',
    data: (report.value?.by_day ?? []).map((item) => Number(item.amount)),
    color: '#10b981',
  },
])

const metrics = computed(() => [
  {
    label: 'Выручка',
    value: formatMoney(report.value?.total_amount ?? '0'),
    hint: 'успешные платежи',
  },
  {
    label: 'Платежи',
    value: formatCount(report.value?.payments_count ?? 0),
    hint: 'за период',
  },
  {
    label: 'Возвраты',
    value: formatMoney(report.value?.refunded_amount ?? '0'),
    hint: 'оформлено за период',
  },
  {
    label: 'Средний чек',
    value: formatMoney(
      formatAverageCheck(report.value?.total_amount ?? '0', report.value?.payments_count ?? 0),
    ),
    hint: 'на один платёж',
  },
])

const columns: TableColumn[] = [
  { key: 'membership_type_name', label: 'Вид абонемента', hideOnMobile: true },
  { key: 'payments_count', label: 'Платежи', align: 'right' },
  { key: 'amount', label: 'Сумма', align: 'right' },
  { key: 'share', label: 'Доля', align: 'right' },
]

const rows = computed<TableRow[]>(() =>
  (report.value?.by_membership_type ?? []).map((item) => ({
    ...item,
    id: item.membership_type_name,
  })),
)

function asType(row: TableRow): RevenueByMembershipType {
  return row as unknown as RevenueByMembershipType
}

function typeShare(row: TableRow): string {
  const total = Number(report.value?.total_amount ?? 0)
  if (total <= 0) {
    return '—'
  }
  return formatPercent((Number(asType(row).amount) / total) * 100)
}

function exportCsv(): void {
  if (!report.value) {
    return
  }

  downloadCsv(`revenue-${report.value.date_from}-${report.value.date_to}.csv`, [
    ['Период', report.value.date_from, report.value.date_to],
    ['Выручка', report.value.total_amount],
    ['Платежи', report.value.payments_count],
    ['Возвраты', report.value.refunded_amount],
    [],
    ['Вид абонемента', 'Платежи', 'Сумма'],
    ...report.value.by_membership_type.map((item) => [
      item.membership_type_name,
      item.payments_count,
      item.amount,
    ]),
    [],
    ['Дата', 'Платежи', 'Сумма'],
    ...report.value.by_day.map((item) => [item.day, item.payments_count, item.amount]),
  ])
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="min-w-0">
        <div class="flex flex-wrap items-center gap-2">
          <h3 class="text-lg font-semibold text-slate-900">Выручка</h3>
          <AppBadge tone="violet">mock-платежи</AppBadge>
        </div>
        <p class="mt-1 text-sm text-slate-500">
          <template v-if="report">
            Период: {{ periodLabel(report.date_from, report.date_to) }}
          </template>
          <template v-else>Итоги по успешным платежам и возвратам</template>
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
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="index in 4"
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
      title="Не удалось построить отчёт по выручке"
      :description="getApiErrorMessage(reportQuery.error.value)"
      @retry="reportQuery.refetch()"
    />

    <EmptyState
      v-else-if="report && !hasRevenueData(report)"
      title="Платежей за период нет"
      description="За выбранный период не было успешных платежей. Измените даты и попробуйте снова."
      :icon="Wallet"
    />

    <template v-else-if="report">
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
            <h4 class="text-sm font-semibold text-slate-900">Выручка по дням</h4>
            <p class="mt-0.5 text-xs text-slate-500">Суммы успешных платежей</p>
          </div>
          <AppBadge tone="success">{{ chartLabels.length }} дней с оплатами</AppBadge>
        </div>

        <BarChart
          v-if="chartLabels.length > 0"
          class="mt-4"
          :labels="chartLabels"
          :datasets="chartDatasets"
          aria-label="График выручки по дням"
        />
        <EmptyState
          v-else
          class="mt-4"
          compact
          title="Нет платежей по дням"
          description="За выбранный период успешных платежей не было."
        />
      </section>

      <section class="space-y-2">
        <h4 class="text-sm font-semibold text-slate-900">Разбивка по видам абонементов</h4>
        <DataTable
          :columns="columns"
          :rows="rows"
          empty-title="Нет данных по видам"
          empty-text="Успешных платежей за период нет."
          mobile-title-key="membership_type_name"
        >
          <template #cell-membership_type_name="{ row }">
            <span class="font-medium text-slate-900">
              {{ asType(row).membership_type_name }}
            </span>
          </template>
          <template #cell-payments_count="{ row }">
            <span class="text-slate-700">{{ asType(row).payments_count }}</span>
          </template>
          <template #cell-amount="{ row }">
            <span class="whitespace-nowrap font-semibold text-slate-900">
              {{ formatMoney(asType(row).amount) }}
            </span>
          </template>
          <template #cell-share="{ row }">
            <span class="whitespace-nowrap text-slate-600">{{ typeShare(row) }}</span>
          </template>
        </DataTable>
      </section>

      <p class="text-xs leading-5 text-slate-400">
        Отчёт учитывает только успешные платежи. Возвраты показаны отдельно и не уменьшают сумму
        успешных оплат за период.
      </p>
    </template>
  </section>
</template>
