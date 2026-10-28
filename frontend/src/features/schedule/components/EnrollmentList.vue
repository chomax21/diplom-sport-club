<script setup lang="ts">
import { Check, X } from '@lucide/vue'
import { computed, ref } from 'vue'

import type { Enrollment, TrainingSession } from '@/api/schedule'
import { getApiErrorMessage } from '@/api/errors'
import {
  AppBadge,
  AppButton,
  AppSwitch,
  DataTable,
  EmptyState,
  ErrorState,
  IconButton,
  StatusBadge,
} from '@/components/ui'
import type { TableColumn, TableRow } from '@/components/ui'
import { useAttendanceMutation, useSessionEnrollmentsQuery } from '@/features/schedule/queries'
import { formatDateTime } from '@/lib/datetime'
import { useToastStore } from '@/stores/toasts'

const props = defineProps<{
  session: TrainingSession
}>()

const toast = useToastStore()
const includeCancelled = ref(false)
const attendanceError = ref('')

const enrollmentsQuery = useSessionEnrollmentsQuery(
  computed(() => props.session.id),
  includeCancelled,
  true,
)

const attendanceMutation = useAttendanceMutation()

const columns: TableColumn[] = [
  { key: 'client_name', label: 'Клиент', hideOnMobile: true },
  { key: 'contact', label: 'Контакты' },
  { key: 'status', label: 'Статус' },
  { key: 'created_at', label: 'Записан' },
  { key: 'actions', label: '', align: 'right', hideOnMobile: true },
]

const rows = computed<TableRow[]>(() =>
  (enrollmentsQuery.data.value?.items ?? []).map((enrollment) => ({ ...enrollment })),
)

const total = computed(() => enrollmentsQuery.data.value?.total ?? 0)
const pendingEnrollmentId = computed(() => attendanceMutation.variables.value?.enrollmentId ?? null)

function statusOf(row: TableRow): string {
  return String(row.status)
}

function markRow(row: TableRow, action: 'attend' | 'no_show'): Promise<void> {
  return mark(row as unknown as Enrollment, action)
}

async function mark(enrollment: Enrollment, action: 'attend' | 'no_show'): Promise<void> {
  attendanceError.value = ''

  try {
    await attendanceMutation.mutateAsync({ enrollmentId: enrollment.id, action })
    toast.success(
      action === 'attend'
        ? `Посещение отмечено: ${enrollment.client_name}.`
        : `Неявка отмечена: ${enrollment.client_name}.`,
      action === 'attend' ? 'Посещение' : 'Неявка',
    )
  } catch (error) {
    attendanceError.value = getApiErrorMessage(error)
  }
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex min-w-0 items-center gap-2">
        <h2 class="text-lg font-semibold text-slate-900">Записанные клиенты</h2>
        <AppBadge tone="neutral">{{ total }}</AppBadge>
      </div>
      <div class="sm:max-w-xs">
        <AppSwitch
          v-model="includeCancelled"
          label="Отменённые"
          description="Показывать отменённые записи"
        />
      </div>
    </div>

    <div
      v-if="attendanceError"
      class="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
      role="alert"
    >
      {{ attendanceError }}
    </div>

    <div v-if="enrollmentsQuery.isPending.value">
      <DataTable :columns="columns" :rows="[]" loading />
    </div>

    <ErrorState
      v-else-if="enrollmentsQuery.isError.value"
      title="Не удалось загрузить записи"
      :description="getApiErrorMessage(enrollmentsQuery.error.value)"
      compact
      @retry="enrollmentsQuery.refetch()"
    />

    <EmptyState
      v-else-if="rows.length === 0"
      title="Записей пока нет"
      description="Клиенты появятся здесь после записи на тренировку."
      compact
    />

    <DataTable
      v-else
      :columns="columns"
      :rows="rows"
      mobile-title-key="client_name"
      mobile-subtitle-key="client_email"
    >
      <template #cell-client_name="{ row }">
        <div class="min-w-0">
          <p class="font-medium text-slate-900">{{ row.client_name }}</p>
          <p class="truncate text-xs text-slate-500">{{ row.client_email }}</p>
        </div>
      </template>

      <template #cell-contact="{ row }">
        <div class="min-w-0 text-sm">
          <p class="break-all text-slate-700">{{ row.client_email }}</p>
          <p class="mt-0.5 text-xs text-slate-500">{{ row.client_phone ?? 'Телефон не указан' }}</p>
        </div>
      </template>

      <template #cell-status="{ row }">
        <StatusBadge kind="enrollment" :status="statusOf(row)" />
      </template>

      <template #cell-created_at="{ row }">
        <span class="text-xs text-slate-500">{{ formatDateTime(String(row.created_at)) }}</span>
      </template>

      <template #cell-actions="{ row }">
        <div v-if="statusOf(row) === 'active'" class="flex items-center justify-end gap-1">
          <AppButton
            size="sm"
            variant="soft"
            :loading="pendingEnrollmentId === row.id"
            @click="markRow(row, 'attend')"
          >
            <template #icon>
              <Check :size="14" aria-hidden="true" />
            </template>
            Посетил
          </AppButton>
          <IconButton
            label="Отметить неявку"
            variant="danger"
            :disabled="pendingEnrollmentId === row.id"
            @click="markRow(row, 'no_show')"
          >
            <X :size="16" aria-hidden="true" />
          </IconButton>
        </div>
        <span v-else class="text-xs text-slate-400">—</span>
      </template>

      <template #mobile-actions="{ row }">
        <div v-if="statusOf(row) === 'active'" class="flex items-center gap-1">
          <IconButton
            label="Отметить посещение"
            variant="soft"
            :disabled="pendingEnrollmentId === row.id"
            @click="markRow(row, 'attend')"
          >
            <Check :size="16" aria-hidden="true" />
          </IconButton>
          <IconButton
            label="Отметить неявку"
            variant="danger"
            :disabled="pendingEnrollmentId === row.id"
            @click="markRow(row, 'no_show')"
          >
            <X :size="16" aria-hidden="true" />
          </IconButton>
        </div>
      </template>
    </DataTable>
  </section>
</template>
