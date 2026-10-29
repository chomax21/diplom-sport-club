<script setup lang="ts">
import { CreditCard, RefreshCw, Wallet } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import type { Payment, PaymentListParams, PaymentStatus } from '@/api/memberships'
import {
  AppBadge,
  AppButton,
  AppPagination,
  AppSelect,
  DataTable,
  ErrorState,
  FilterBar,
  StatusBadge,
  type TableColumn,
  type TableRow,
} from '@/components/ui'
import PaymentDetailModal from '@/features/memberships/components/PaymentDetailModal.vue'
import { usePaymentsQuery } from '@/features/memberships/queries'
import { PAYMENT_METHOD_LABELS } from '@/features/memberships/status'
import { useClientsQuery } from '@/features/schedule/queries'
import { formatDateTime } from '@/lib/datetime'
import { formatMoney } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'

const PAGE_SIZE = 10

const auth = useAuthStore()
const isAdmin = computed(() => auth.role === 'admin')

const statusFilter = ref<string | number>('')
const clientFilter = ref<string | number>('')
const page = ref(1)

const detailOpen = ref(false)
const selectedPaymentId = ref<string | null>(null)

const clientsQuery = useClientsQuery(isAdmin)

const statusOptions = [
  { label: 'Все статусы', value: '' },
  { label: 'Ожидает', value: 'pending' },
  { label: 'Успешно', value: 'succeeded' },
  { label: 'Ошибка', value: 'failed' },
  { label: 'Возврат', value: 'refunded' },
]

const clientsFilterOptions = computed(() => [
  { label: 'Все клиенты', value: '' },
  ...(clientsQuery.data.value?.items ?? []).map((client) => ({
    label: client.full_name,
    value: client.id,
  })),
])

const params = computed<PaymentListParams>(() => {
  const status =
    typeof statusFilter.value === 'string' && statusFilter.value
      ? (statusFilter.value as PaymentStatus)
      : undefined
  const clientId =
    isAdmin.value && typeof clientFilter.value === 'string' && clientFilter.value
      ? clientFilter.value
      : undefined

  return {
    status,
    client_id: clientId,
    limit: PAGE_SIZE,
    offset: (page.value - 1) * PAGE_SIZE,
  }
})

const paymentsQuery = usePaymentsQuery(params)

const payments = computed<Payment[]>(() => paymentsQuery.data.value?.items ?? [])
const total = computed(() => paymentsQuery.data.value?.total ?? 0)

const rows = computed<TableRow[]>(() => payments.value.map((payment) => ({ ...payment })))

const columns = computed<TableColumn[]>(() => {
  const result: TableColumn[] = [{ key: 'created_at', label: 'Дата' }]

  if (isAdmin.value) {
    result.push({ key: 'client_name', label: 'Клиент' })
  }

  result.push(
    { key: 'description', label: 'Назначение' },
    { key: 'amount', label: 'Сумма', align: 'right' },
    { key: 'payment_method', label: 'Способ' },
    { key: 'status', label: 'Статус' },
    {
      key: 'actions',
      label: 'Детали',
      align: 'right',
      hideOnMobile: true,
    },
  )

  return result
})

const hasActiveFilters = computed(
  () => Boolean(statusFilter.value) || (isAdmin.value && Boolean(clientFilter.value)),
)
const activeFilterCount = computed(
  () => (statusFilter.value ? 1 : 0) + (isAdmin.value && clientFilter.value ? 1 : 0),
)

watch([statusFilter, clientFilter], () => {
  page.value = 1
})

function asPayment(row: TableRow): Payment {
  return row as unknown as Payment
}

function resetFilters(): void {
  statusFilter.value = ''
  clientFilter.value = ''
  page.value = 1
}

function openDetails(payment: Payment): void {
  selectedPaymentId.value = payment.id
  detailOpen.value = true
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Финансы</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          {{ isAdmin ? 'Платежи и возвраты' : 'Мои платежи' }}
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          {{
            isAdmin
              ? 'История оплат, статусы операций и возврат средств с отменой абонемента.'
              : 'История покупок абонементов и статусы платежей. Возврат оформляет администратор.'
          }}
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="paymentsQuery.isFetching.value"
          @click="paymentsQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
      </div>
    </section>

    <section class="rounded-2xl border border-sky-200 bg-sky-50/70 p-4">
      <div class="flex items-start gap-2.5">
        <CreditCard :size="18" class="mt-0.5 shrink-0 text-sky-700" aria-hidden="true" />
        <div class="min-w-0 text-xs leading-5 text-sky-800">
          <p class="font-semibold">Демонстрационный режим оплаты</p>
          <p class="mt-0.5">
            Платежи проводятся через mock-провайдера: реальные списания не выполняются. Наличные
            оформляет администратор, такие операции помечены как «Оплата в клубе».
          </p>
        </div>
      </div>
    </section>

    <FilterBar
      :active-count="activeFilterCount"
      :has-active-filters="hasActiveFilters"
      :columns="2"
      @reset="resetFilters"
    >
      <AppSelect v-model="statusFilter" label="Статус" :options="statusOptions" />
      <AppSelect
        v-if="isAdmin"
        v-model="clientFilter"
        label="Клиент"
        :options="clientsFilterOptions"
        :disabled="clientsQuery.isPending.value"
      />
    </FilterBar>

    <ErrorState
      v-if="paymentsQuery.isError.value"
      title="Не удалось загрузить платежи"
      :description="getApiErrorMessage(paymentsQuery.error.value)"
      @retry="paymentsQuery.refetch()"
    />

    <div v-else class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <p class="text-sm text-slate-500">
          Найдено: <span class="font-semibold text-slate-900">{{ total }}</span>
        </p>
        <AppBadge v-if="isAdmin" tone="violet">Администратор</AppBadge>
      </div>

      <DataTable
        :columns="columns"
        :rows="rows"
        :loading="paymentsQuery.isPending.value"
        empty-title="Платежей нет"
        :empty-text="
          hasActiveFilters
            ? 'По выбранным фильтрам платежи не найдены. Попробуйте сбросить фильтры.'
            : 'Платежи появятся после покупки первого абонемента.'
        "
      >
        <template #mobile-title="{ row }">
          <div class="flex flex-wrap items-center gap-1.5">
            <p class="text-sm font-semibold text-slate-900">
              {{ formatMoney(asPayment(row).amount, asPayment(row).currency) }}
            </p>
            <StatusBadge kind="payment" :status="asPayment(row).status" />
          </div>
          <p class="mt-1 truncate text-xs text-slate-500">
            {{ asPayment(row).description || 'Назначение не указано' }}
          </p>
        </template>

        <template #cell-created_at="{ row }">
          <span class="whitespace-nowrap text-slate-700">
            {{ formatDateTime(asPayment(row).created_at) }}
          </span>
        </template>

        <template #cell-client_name="{ row }">
          <span class="font-medium text-slate-900">{{ asPayment(row).client_name }}</span>
        </template>

        <template #cell-description="{ row }">
          <span class="text-slate-700">
            {{ asPayment(row).description || 'Назначение не указано' }}
          </span>
        </template>

        <template #cell-amount="{ row }">
          <span class="whitespace-nowrap font-semibold text-slate-900">
            {{ formatMoney(asPayment(row).amount, asPayment(row).currency) }}
          </span>
        </template>

        <template #cell-payment_method="{ row }">
          <span class="whitespace-nowrap text-slate-600">
            {{ PAYMENT_METHOD_LABELS[asPayment(row).payment_method] }}
          </span>
        </template>

        <template #cell-status="{ row }">
          <StatusBadge kind="payment" :status="asPayment(row).status" />
        </template>

        <template #cell-actions="{ row }">
          <AppButton variant="ghost" size="sm" @click="openDetails(asPayment(row))">
            <template #icon>
              <Wallet :size="15" aria-hidden="true" />
            </template>
            Детали
          </AppButton>
        </template>

        <template #mobile-actions="{ row }">
          <AppButton variant="ghost" size="sm" @click="openDetails(asPayment(row))">
            <Wallet :size="15" aria-hidden="true" />
            <span class="sr-only">Детали платежа</span>
          </AppButton>
        </template>
      </DataTable>

      <AppPagination
        v-if="total > PAGE_SIZE"
        v-model:page="page"
        :page-size="PAGE_SIZE"
        :total="total"
      />
    </div>

    <PaymentDetailModal
      v-model="detailOpen"
      :payment-id="selectedPaymentId"
      @refunded="paymentsQuery.refetch()"
    />
  </div>
</template>
