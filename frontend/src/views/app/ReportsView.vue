<script setup lang="ts">
import { BarChart3, Wallet } from '@lucide/vue'
import { computed, ref } from 'vue'

import type { AttendanceReportParams, ReportPeriodParams } from '@/api/reports'
import { AppBadge, AppSelect, DateRangePicker } from '@/components/ui'
import AttendanceReportPanel from '@/features/reports/components/AttendanceReportPanel.vue'
import RevenueReportPanel from '@/features/reports/components/RevenueReportPanel.vue'
import { useTrainersQuery } from '@/features/schedule/queries'
import { addDaysDateInput, todayDateInput } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'

type ReportTab = 'attendance' | 'revenue'

const auth = useAuthStore()
const isAdmin = computed(() => auth.role === 'admin')
const isTrainer = computed(() => auth.role === 'trainer')

const activeTab = ref<ReportTab>('attendance')
const dateFrom = ref<string | null>(addDaysDateInput(-29))
const dateTo = ref<string | null>(todayDateInput())
const trainerId = ref<string | number>('')

const trainersQuery = useTrainersQuery(isAdmin)

const trainerOptions = computed(() => [
  { label: 'Все тренеры', value: '' },
  ...(trainersQuery.data.value?.items ?? [])
    .filter((trainer) => trainer.is_active)
    .map((trainer) => ({
      label: trainer.full_name,
      value: trainer.id,
    })),
])

const attendanceParams = computed<AttendanceReportParams>(() => ({
  date_from: dateFrom.value ?? undefined,
  date_to: dateTo.value ?? undefined,
  trainer_id:
    isAdmin.value && typeof trainerId.value === 'string' && trainerId.value
      ? trainerId.value
      : undefined,
}))

const revenueParams = computed<ReportPeriodParams>(() => ({
  date_from: dateFrom.value ?? undefined,
  date_to: dateTo.value ?? undefined,
}))

const attendanceEnabled = computed(() => activeTab.value === 'attendance')
const revenueEnabled = computed(() => isAdmin.value && activeTab.value === 'revenue')
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Аналитика</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Отчёты</h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          {{
            isAdmin
              ? 'Посещаемость и выручка клуба за выбранный период. Данные совпадают с API и доступны в CSV.'
              : 'Посещаемость ваших тренировок за выбранный период. Тренер видит только собственную статистику.'
          }}
        </p>
      </div>
      <AppBadge v-if="isTrainer" tone="info">Только ваши тренировки</AppBadge>
    </section>

    <div v-if="isAdmin" class="flex flex-wrap gap-2" role="tablist" aria-label="Тип отчёта">
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'attendance'"
        aria-controls="report-panel"
        :class="[
          'inline-flex min-h-11 items-center gap-2 rounded-control px-4 text-sm font-semibold transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
          activeTab === 'attendance'
            ? 'bg-brand-600 text-white shadow-sm'
            : 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
        ]"
        @click="activeTab = 'attendance'"
      >
        <BarChart3 :size="16" aria-hidden="true" />
        Посещаемость
      </button>
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'revenue'"
        aria-controls="report-panel"
        :class="[
          'inline-flex min-h-11 items-center gap-2 rounded-control px-4 text-sm font-semibold transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
          activeTab === 'revenue'
            ? 'bg-brand-600 text-white shadow-sm'
            : 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
        ]"
        @click="activeTab = 'revenue'"
      >
        <Wallet :size="16" aria-hidden="true" />
        Выручка
      </button>
    </div>

    <section class="rounded-panel border border-slate-200 bg-white p-3 shadow-sm sm:p-4">
      <div
        class="grid gap-3"
        :class="isAdmin && activeTab === 'attendance' ? 'lg:grid-cols-3' : 'lg:grid-cols-1'"
      >
        <DateRangePicker
          v-model:from="dateFrom"
          v-model:to="dateTo"
          :class="isAdmin && activeTab === 'attendance' ? 'lg:col-span-2' : ''"
          label="Период отчёта"
          hint="Если период не выбран, API использует последние 30 дней"
        />
        <AppSelect
          v-if="isAdmin && activeTab === 'attendance'"
          v-model="trainerId"
          label="Тренер"
          :options="trainerOptions"
          :disabled="trainersQuery.isPending.value"
          hint="Пустое значение — все тренеры"
        />
      </div>
    </section>

    <div
      v-if="isTrainer"
      class="rounded-2xl border border-sky-200 bg-sky-50/70 p-4 text-xs leading-5 text-sky-800"
    >
      Отчёт по выручке доступен только администратору. Для тренера сервер автоматически ограничивает
      посещаемость его собственными тренировками.
    </div>

    <div id="report-panel" role="tabpanel">
      <AttendanceReportPanel
        v-if="activeTab === 'attendance'"
        :params="attendanceParams"
        :enabled="attendanceEnabled"
      />
      <RevenueReportPanel v-else-if="isAdmin" :params="revenueParams" :enabled="revenueEnabled" />
    </div>
  </div>
</template>
