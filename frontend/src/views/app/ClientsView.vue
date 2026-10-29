<script setup lang="ts">
import { Eye, Plus, RefreshCw, Users } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import type { ClientRecord } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppPagination,
  DataTable,
  ErrorState,
  FilterBar,
  SearchInput,
  type TableColumn,
  type TableRow,
} from '@/components/ui'
import ClientDetailModal from '@/features/directory/components/ClientDetailModal.vue'
import UserFormModal from '@/features/directory/components/UserFormModal.vue'
import { useClientListQuery } from '@/features/directory/queries'
import { formatDateShort } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'

const PAGE_SIZE = 10

const auth = useAuthStore()
const isAdmin = computed(() => auth.role === 'admin')

const search = ref('')
const page = ref(1)

const detailOpen = ref(false)
const selectedClientId = ref<string | null>(null)
const createOpen = ref(false)

const params = computed(() => ({
  search: search.value.trim() || undefined,
  limit: PAGE_SIZE,
  offset: (page.value - 1) * PAGE_SIZE,
}))

const clientsQuery = useClientListQuery(params)

const clients = computed<ClientRecord[]>(() => clientsQuery.data.value?.items ?? [])
const total = computed(() => clientsQuery.data.value?.total ?? 0)
const rows = computed<TableRow[]>(() => clients.value.map((client) => ({ ...client })))

const columns: TableColumn[] = [
  { key: 'full_name', label: 'Клиент', hideOnMobile: true },
  { key: 'phone', label: 'Телефон' },
  { key: 'birth_date', label: 'Дата рождения' },
  { key: 'status', label: 'Статус' },
  { key: 'created_at', label: 'В клубе с' },
  { key: 'actions', label: 'Действия', align: 'right', hideOnMobile: true },
]

watch(search, () => {
  page.value = 1
})

function asClient(row: TableRow): ClientRecord {
  return row as unknown as ClientRecord
}

function openDetails(client: ClientRecord): void {
  selectedClientId.value = client.id
  detailOpen.value = true
}

function resetFilters(): void {
  search.value = ''
  page.value = 1
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Клуб</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Клиенты</h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          {{
            isAdmin
              ? 'Ищите клиентов, открывайте карточки и обновляйте контактные данные.'
              : 'Просматривайте карточки клиентов. Редактирование доступно администратору.'
          }}
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="clientsQuery.isFetching.value"
          @click="clientsQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton v-if="isAdmin" @click="createOpen = true">
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          Новый клиент
        </AppButton>
      </div>
    </section>

    <div
      v-if="!isAdmin"
      class="rounded-2xl border border-sky-200 bg-sky-50/70 p-4 text-xs leading-5 text-sky-800"
    >
      Тренер может просматривать карточки клиентов. Изменение данных и создание клиентов доступны
      администратору.
    </div>

    <FilterBar
      :active-count="search.trim() ? 1 : 0"
      :has-active-filters="Boolean(search.trim())"
      :columns="1"
      @reset="resetFilters"
    >
      <SearchInput
        v-model="search"
        aria-label="Поиск клиентов"
        placeholder="Имя, email или телефон…"
      />
    </FilterBar>

    <div class="space-y-4">
      <p class="text-sm text-slate-500">
        Найдено: <span class="font-semibold text-slate-900">{{ total }}</span>
      </p>

      <ErrorState
        v-if="clientsQuery.isError.value"
        title="Не удалось загрузить клиентов"
        :description="getApiErrorMessage(clientsQuery.error.value)"
        @retry="clientsQuery.refetch()"
      />

      <DataTable
        v-else
        :columns="columns"
        :rows="rows"
        :loading="clientsQuery.isPending.value"
        empty-title="Клиенты не найдены"
        :empty-text="
          search.trim()
            ? 'Попробуйте изменить поисковый запрос.'
            : 'Создайте первого клиента или зарегистрируйте его через форму входа.'
        "
      >
        <template #mobile-title="{ row }">
          <div class="flex items-center gap-2.5">
            <AppAvatar :name="asClient(row).full_name" size="sm" />
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-900">
                {{ asClient(row).full_name }}
              </p>
              <p class="mt-0.5 truncate text-xs text-slate-500">{{ asClient(row).email }}</p>
            </div>
          </div>
        </template>

        <template #cell-full_name="{ row }">
          <div class="flex min-w-0 items-center gap-2.5">
            <AppAvatar :name="asClient(row).full_name" size="sm" />
            <div class="min-w-0">
              <p class="truncate font-semibold text-slate-900">{{ asClient(row).full_name }}</p>
              <p class="mt-0.5 truncate text-xs text-slate-500">{{ asClient(row).email }}</p>
            </div>
          </div>
        </template>

        <template #cell-phone="{ row }">
          <span class="whitespace-nowrap text-slate-700">{{ asClient(row).phone || '—' }}</span>
        </template>

        <template #cell-birth_date="{ row }">
          <span class="whitespace-nowrap text-slate-700">
            {{ asClient(row).birth_date ? formatDateShort(asClient(row).birth_date!) : '—' }}
          </span>
        </template>

        <template #cell-status="{ row }">
          <AppBadge :tone="asClient(row).is_active ? 'success' : 'neutral'" dot>
            {{ asClient(row).is_active ? 'Активен' : 'Заблокирован' }}
          </AppBadge>
        </template>

        <template #cell-created_at="{ row }">
          <span class="whitespace-nowrap text-slate-700">
            {{ formatDateShort(asClient(row).created_at) }}
          </span>
        </template>

        <template #cell-actions="{ row }">
          <AppButton variant="ghost" size="sm" @click="openDetails(asClient(row))">
            <template #icon>
              <Eye :size="15" aria-hidden="true" />
            </template>
            Открыть
          </AppButton>
        </template>

        <template #mobile-actions="{ row }">
          <AppButton variant="ghost" size="sm" @click="openDetails(asClient(row))">
            <Eye :size="15" aria-hidden="true" />
            <span class="sr-only">Открыть карточку клиента</span>
          </AppButton>
        </template>

        <template #empty-action>
          <AppButton v-if="isAdmin" size="sm" @click="createOpen = true">
            <template #icon>
              <Plus :size="15" aria-hidden="true" />
            </template>
            Новый клиент
          </AppButton>
          <AppButton v-else variant="outline" size="sm" @click="resetFilters">
            Сбросить поиск
          </AppButton>
        </template>
      </DataTable>

      <AppPagination
        v-if="!clientsQuery.isError.value && total > PAGE_SIZE"
        v-model:page="page"
        :page-size="PAGE_SIZE"
        :total="total"
      />
    </div>

    <div
      v-if="
        clients.length === 0 &&
        !clientsQuery.isPending.value &&
        !clientsQuery.isError.value &&
        !search
      "
      class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-center text-xs text-slate-500"
    >
      <Users :size="18" class="mx-auto mb-2 text-slate-400" aria-hidden="true" />
      Новые клиенты появляются после регистрации или создания пользователя с ролью «Клиент».
    </div>

    <ClientDetailModal
      v-model="detailOpen"
      :client-id="selectedClientId"
      @saved="clientsQuery.refetch()"
    />

    <UserFormModal
      v-model="createOpen"
      default-role="client"
      lock-role
      @saved="clientsQuery.refetch()"
    />
  </div>
</template>
