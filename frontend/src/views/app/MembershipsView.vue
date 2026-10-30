<script setup lang="ts">
import { Ban, CreditCard, Plus, RefreshCw, Tags, Ticket } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { getApiErrorMessage } from '@/api/errors'
import type { Membership, MembershipListParams, MembershipStatus } from '@/api/memberships'
import {
  AppBadge,
  AppButton,
  AppPagination,
  AppSelect,
  ConfirmDialog,
  DataTable,
  EmptyState,
  ErrorState,
  FilterBar,
  SkeletonBlock,
  StatusBadge,
  type TableColumn,
  type TableRow,
} from '@/components/ui'
import MembershipTypeCard from '@/features/memberships/components/MembershipTypeCard.vue'
import PurchaseMembershipModal from '@/features/memberships/components/PurchaseMembershipModal.vue'
import {
  useCancelMembershipMutation,
  useMembershipTypesQuery,
  useMembershipsQuery,
} from '@/features/memberships/queries'
import {
  canCancelMembership,
  membershipExpiryLabel,
  visitsLeftLabel,
} from '@/features/memberships/status'
import { useClientsQuery } from '@/features/schedule/queries'
import { formatDateRange, formatDateShort } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const PAGE_SIZE = 10

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const isAdmin = computed(() => auth.role === 'admin')
const isClient = computed(() => auth.role === 'client')

const statusFilter = ref<string | number>('')
const clientFilter = ref<string | number>('')
const page = ref(1)

const purchaseOpen = ref(false)
const purchaseTypeId = ref<string | null>(null)

const cancelOpen = ref(false)
const cancelTarget = ref<Membership | null>(null)
const cancelError = ref('')

const clientsQuery = useClientsQuery(isAdmin)

const clientsFilterOptions = computed(() => [
  { label: 'Все клиенты', value: '' },
  ...(clientsQuery.data.value?.items ?? []).map((client) => ({
    label: client.full_name,
    value: client.id,
  })),
])

const statusOptions = [
  { label: 'Все статусы', value: '' },
  { label: 'Ожидает', value: 'pending' },
  { label: 'Активен', value: 'active' },
  { label: 'Истёк', value: 'expired' },
  { label: 'Отменён', value: 'cancelled' },
]

const params = computed<MembershipListParams>(() => {
  const status =
    typeof statusFilter.value === 'string' && statusFilter.value
      ? (statusFilter.value as MembershipStatus)
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

const membershipsQuery = useMembershipsQuery(params)
const catalogQuery = useMembershipTypesQuery(
  computed(() => ({ limit: 200 })),
  isClient,
)
const cancelMutation = useCancelMembershipMutation()

const memberships = computed<Membership[]>(() => membershipsQuery.data.value?.items ?? [])
const total = computed(() => membershipsQuery.data.value?.total ?? 0)
const activeCatalog = computed(() =>
  (catalogQuery.data.value?.items ?? []).filter((item) => item.is_active),
)

const rows = computed<TableRow[]>(() => memberships.value.map((membership) => ({ ...membership })))

const columns = computed<TableColumn[]>(() => {
  const result: TableColumn[] = [{ key: 'membership_type_name', label: 'Абонемент' }]

  if (isAdmin.value) {
    result.push({ key: 'client_name', label: 'Клиент' })
  }

  result.push(
    { key: 'period', label: 'Период' },
    { key: 'visits_left', label: 'Остаток' },
    { key: 'status', label: 'Статус' },
  )

  if (isAdmin.value) {
    result.push({
      key: 'actions',
      label: 'Действия',
      align: 'right',
      hideOnMobile: true,
    })
  }

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

function asMembership(row: TableRow): Membership {
  return row as unknown as Membership
}

function resetFilters(): void {
  statusFilter.value = ''
  clientFilter.value = ''
  page.value = 1
}

function openPurchase(typeId?: string): void {
  purchaseTypeId.value = typeId ?? null
  purchaseOpen.value = true
}

function openCancel(membership: Membership): void {
  cancelTarget.value = membership
  cancelError.value = ''
  cancelOpen.value = true
}

async function cancelMembership(): Promise<void> {
  if (!cancelTarget.value) {
    return
  }

  cancelError.value = ''

  try {
    await cancelMutation.mutateAsync(cancelTarget.value.id)
    cancelOpen.value = false
    toast.success('Абонемент отменён, остаток посещений обнулён.', 'Абонемент отменён')
    cancelTarget.value = null
  } catch (error) {
    cancelError.value = getApiErrorMessage(error)
  }
}

function onPurchased(): void {
  void membershipsQuery.refetch()
  void catalogQuery.refetch()
}

function goToTypes(): void {
  void router.push({ name: 'membership-types' })
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Абонементы</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          {{ isAdmin ? 'Абонементы клиентов' : 'Мои абонементы' }}
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          {{
            isAdmin
              ? 'Оформляйте абонементы клиентам, следите за сроками и отменяйте их при необходимости.'
              : 'Покупайте абонементы, следите за остатком посещений и сроком действия.'
          }}
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="membershipsQuery.isFetching.value"
          @click="membershipsQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton v-if="isAdmin" variant="outline" @click="goToTypes">
          <template #icon>
            <Tags :size="16" aria-hidden="true" />
          </template>
          Виды абонементов
        </AppButton>
        <AppButton v-if="isAdmin || isClient" @click="openPurchase()">
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          {{ isAdmin ? 'Оформить абонемент' : 'Купить абонемент' }}
        </AppButton>
      </div>
    </section>

    <section v-if="isClient" class="space-y-3">
      <div class="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h3 class="text-lg font-semibold text-slate-900">Каталог абонементов</h3>
          <p class="mt-1 text-sm text-slate-500">Доступные виды и стоимость</p>
        </div>
        <AppBadge v-if="activeCatalog.length > 0" tone="neutral">
          {{ activeCatalog.length }}
        </AppBadge>
      </div>

      <div v-if="catalogQuery.isPending.value" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="index in 3"
          :key="index"
          class="rounded-card border border-slate-200 bg-white p-5 shadow-sm"
        >
          <SkeletonBlock :lines="4" />
        </div>
      </div>

      <ErrorState
        v-else-if="catalogQuery.isError.value"
        compact
        title="Не удалось загрузить каталог"
        :description="getApiErrorMessage(catalogQuery.error.value)"
        @retry="catalogQuery.refetch()"
      />

      <EmptyState
        v-else-if="activeCatalog.length === 0"
        compact
        title="Каталог пока пуст"
        description="Администратор ещё не опубликовал виды абонементов."
        :icon="Ticket"
      />

      <div v-else class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <MembershipTypeCard v-for="item in activeCatalog" :key="item.id" :type="item">
          <template #actions>
            <AppButton size="sm" @click="openPurchase(item.id)">Купить</AppButton>
          </template>
        </MembershipTypeCard>
      </div>
    </section>

    <section class="space-y-4">
      <div class="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h3 class="text-lg font-semibold text-slate-900">
            {{ isAdmin ? 'Все абонементы' : 'История абонементов' }}
          </h3>
          <p class="mt-1 text-sm text-slate-500">Найдено: {{ total }}</p>
        </div>
      </div>

      <FilterBar
        :active-count="activeFilterCount"
        :has-active-filters="hasActiveFilters"
        :columns="isAdmin ? 2 : 1"
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
        v-if="membershipsQuery.isError.value"
        title="Не удалось загрузить абонементы"
        :description="getApiErrorMessage(membershipsQuery.error.value)"
        @retry="membershipsQuery.refetch()"
      />

      <DataTable
        v-else
        :columns="columns"
        :rows="rows"
        :loading="membershipsQuery.isPending.value"
        empty-title="Абонементов нет"
        :empty-text="
          isAdmin
            ? 'Оформите первый абонемент клиенту или измените фильтры.'
            : 'Купите абонемент из каталога выше, чтобы начать тренироваться.'
        "
      >
        <template #mobile-title="{ row }">
          <p class="truncate text-sm font-semibold text-slate-900">
            {{ asMembership(row).membership_type_name }}
          </p>
          <p class="mt-0.5 truncate text-xs text-slate-500">
            {{
              isAdmin
                ? asMembership(row).client_name
                : formatDateRange(asMembership(row).starts_at, asMembership(row).ends_at)
            }}
          </p>
        </template>

        <template #cell-membership_type_name="{ row }">
          <div class="min-w-0">
            <p class="font-semibold text-slate-900">
              {{ asMembership(row).membership_type_name }}
            </p>
            <p class="mt-0.5 text-xs text-slate-500">
              Оформлен {{ formatDateShort(asMembership(row).created_at) }}
            </p>
          </div>
        </template>

        <template #cell-client_name="{ row }">
          <span class="font-medium text-slate-900">{{ asMembership(row).client_name }}</span>
        </template>

        <template #cell-period="{ row }">
          <span class="whitespace-nowrap text-slate-700">
            {{ formatDateRange(asMembership(row).starts_at, asMembership(row).ends_at) }}
          </span>
        </template>

        <template #cell-visits_left="{ row }">
          <span class="font-medium text-slate-900">
            {{ visitsLeftLabel(asMembership(row).visits_left) }}
          </span>
        </template>

        <template #cell-status="{ row }">
          <div class="flex flex-col items-start gap-1">
            <StatusBadge kind="membership" :status="asMembership(row).status" />
            <span
              v-if="membershipExpiryLabel(asMembership(row))"
              class="text-[11px] text-amber-700"
            >
              {{ membershipExpiryLabel(asMembership(row)) }}
            </span>
          </div>
        </template>

        <template #cell-actions="{ row }">
          <AppButton
            v-if="canCancelMembership(asMembership(row), auth.role)"
            variant="ghost"
            size="sm"
            @click="openCancel(asMembership(row))"
          >
            <template #icon>
              <Ban :size="15" aria-hidden="true" />
            </template>
            Отменить
          </AppButton>
          <span v-else class="text-xs text-slate-400">—</span>
        </template>

        <template #mobile-actions="{ row }">
          <AppButton
            v-if="canCancelMembership(asMembership(row), auth.role)"
            variant="ghost"
            size="sm"
            @click="openCancel(asMembership(row))"
          >
            <Ban :size="15" aria-hidden="true" />
            <span class="sr-only">Отменить абонемент</span>
          </AppButton>
        </template>

        <template #empty-action>
          <AppButton size="sm" @click="openPurchase()">
            <template #icon>
              <CreditCard :size="15" aria-hidden="true" />
            </template>
            {{ isAdmin ? 'Оформить абонемент' : 'Купить абонемент' }}
          </AppButton>
        </template>
      </DataTable>

      <AppPagination
        v-if="!membershipsQuery.isError.value && total > PAGE_SIZE"
        v-model:page="page"
        :page-size="PAGE_SIZE"
        :total="total"
      />
    </section>

    <div class="rounded-2xl border border-slate-200 bg-white p-4 text-xs leading-5 text-slate-500">
      <p class="font-semibold text-slate-700">Как это работает</p>
      <p class="mt-1">
        Абонемент начинает действовать с даты оформления. Отмена обнуляет остаток посещений, но не
        возвращает платёж — возврат оформляет администратор.
      </p>
      <RouterLink
        to="/app/payments"
        class="mt-1 inline-flex min-h-11 items-center font-semibold text-brand-700 underline"
      >
        Перейти в раздел «Платежи»
      </RouterLink>
    </div>

    <PurchaseMembershipModal
      v-model="purchaseOpen"
      :preselected-type-id="purchaseTypeId"
      @purchased="onPurchased"
    />

    <ConfirmDialog
      v-model="cancelOpen"
      title="Отменить абонемент?"
      message="Абонемент будет отменён, остаток посещений обнулится. Платёж при этом не возвращается: возврат оформляется в разделе «Платежи»."
      confirm-label="Отменить абонемент"
      cancel-label="Оставить"
      :loading="cancelMutation.isPending.value"
      :error="cancelError"
      @confirm="cancelMembership"
    />
  </div>
</template>
