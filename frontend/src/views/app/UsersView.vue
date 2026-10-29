<script setup lang="ts">
import { Ban, CheckCircle2, Pencil, Plus, RefreshCw, ShieldCheck } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import type { UserRecord, UserListParams } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import type { UserRole } from '@/api/types'
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppPagination,
  AppSelect,
  ConfirmDialog,
  DataTable,
  ErrorState,
  FilterBar,
  SearchInput,
  StatusBadge,
  type TableColumn,
  type TableRow,
} from '@/components/ui'
import UserFormModal from '@/features/directory/components/UserFormModal.vue'
import {
  useDeactivateUserMutation,
  useUpdateUserMutation,
  useUserListQuery,
} from '@/features/directory/queries'
import { USER_ROLE_OPTIONS } from '@/features/directory/utils'
import { formatDateShort } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const PAGE_SIZE = 10

const auth = useAuthStore()
const toast = useToastStore()

const search = ref('')
const roleFilter = ref<string | number>('')
const page = ref(1)

const createOpen = ref(false)
const editOpen = ref(false)
const selectedUser = ref<UserRecord | null>(null)

const blockOpen = ref(false)
const blockTarget = ref<UserRecord | null>(null)
const blockError = ref('')

const roleFilterOptions = computed(() => [{ label: 'Все роли', value: '' }, ...USER_ROLE_OPTIONS])

const params = computed<UserListParams>(() => {
  const role =
    typeof roleFilter.value === 'string' && roleFilter.value
      ? (roleFilter.value as UserRole)
      : undefined

  return {
    role,
    search: search.value.trim() || undefined,
    limit: PAGE_SIZE,
    offset: (page.value - 1) * PAGE_SIZE,
  }
})

const usersQuery = useUserListQuery(params)
const deactivateMutation = useDeactivateUserMutation()
const updateMutation = useUpdateUserMutation()

const users = computed<UserRecord[]>(() => usersQuery.data.value?.items ?? [])
const total = computed(() => usersQuery.data.value?.total ?? 0)
const rows = computed<TableRow[]>(() => users.value.map((user) => ({ ...user })))

const columns: TableColumn[] = [
  { key: 'full_name', label: 'Пользователь', hideOnMobile: true },
  { key: 'role', label: 'Роль' },
  { key: 'phone', label: 'Телефон' },
  { key: 'status', label: 'Статус' },
  { key: 'created_at', label: 'Создан' },
  { key: 'actions', label: 'Действия', align: 'right', hideOnMobile: true },
]

const hasActiveFilters = computed(() => Boolean(search.value.trim()) || Boolean(roleFilter.value))
const activeFilterCount = computed(() => (search.value.trim() ? 1 : 0) + (roleFilter.value ? 1 : 0))

watch([search, roleFilter], () => {
  page.value = 1
})

function asUser(row: TableRow): UserRecord {
  return row as unknown as UserRecord
}

function isSelf(user: UserRecord): boolean {
  return auth.user?.id === user.id
}

function resetFilters(): void {
  search.value = ''
  roleFilter.value = ''
  page.value = 1
}

function openEdit(user: UserRecord): void {
  selectedUser.value = user
  editOpen.value = true
}

function openBlock(user: UserRecord): void {
  blockTarget.value = user
  blockError.value = ''
  blockOpen.value = true
}

async function blockUser(): Promise<void> {
  if (!blockTarget.value) {
    return
  }

  blockError.value = ''

  try {
    await deactivateMutation.mutateAsync(blockTarget.value.id)
    blockOpen.value = false
    toast.success(
      'Пользователь не сможет войти в систему. Данные и история сохранятся.',
      'Доступ заблокирован',
    )
    blockTarget.value = null
  } catch (error) {
    blockError.value = getApiErrorMessage(error)
  }
}

async function unblockUser(user: UserRecord): Promise<void> {
  try {
    await updateMutation.mutateAsync({ id: user.id, payload: { is_active: true } })
    toast.success('Пользователь снова может войти в систему.', 'Доступ восстановлен')
  } catch (error) {
    toast.error(getApiErrorMessage(error), 'Не удалось восстановить доступ')
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Управление</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Пользователи
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Учётные записи, роли и блокировка доступа. Роль назначается при создании, а блокировка
          сохраняет историю и профиль.
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="usersQuery.isFetching.value"
          @click="usersQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton @click="createOpen = true">
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          Новый пользователь
        </AppButton>
      </div>
    </section>

    <div class="rounded-2xl border border-sky-200 bg-sky-50/70 p-4">
      <div class="flex items-start gap-2.5">
        <ShieldCheck :size="18" class="mt-0.5 shrink-0 text-sky-700" aria-hidden="true" />
        <div class="min-w-0 text-xs leading-5 text-sky-800">
          <p class="font-semibold">Роли и профили</p>
          <p class="mt-0.5">
            Роль выбирается при создании. Для клиента и тренера профиль создаётся автоматически.
            Удаление в прототипе означает блокировку входа: данные, абонементы и история
            сохраняются.
          </p>
        </div>
      </div>
    </div>

    <FilterBar
      :active-count="activeFilterCount"
      :has-active-filters="hasActiveFilters"
      :columns="2"
      @reset="resetFilters"
    >
      <SearchInput
        v-model="search"
        aria-label="Поиск пользователей"
        placeholder="Имя, email или телефон…"
      />
      <AppSelect v-model="roleFilter" label="Роль" :options="roleFilterOptions" />
    </FilterBar>

    <div class="space-y-4">
      <p class="text-sm text-slate-500">
        Найдено: <span class="font-semibold text-slate-900">{{ total }}</span>
      </p>

      <ErrorState
        v-if="usersQuery.isError.value"
        title="Не удалось загрузить пользователей"
        :description="getApiErrorMessage(usersQuery.error.value)"
        @retry="usersQuery.refetch()"
      />

      <DataTable
        v-else
        :columns="columns"
        :rows="rows"
        :loading="usersQuery.isPending.value"
        empty-title="Пользователи не найдены"
        :empty-text="
          hasActiveFilters
            ? 'По выбранным фильтрам ничего не найдено. Попробуйте сбросить фильтры.'
            : 'Создайте первого пользователя клуба.'
        "
      >
        <template #mobile-title="{ row }">
          <div class="flex items-center gap-2.5">
            <AppAvatar :name="asUser(row).full_name" size="sm" />
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-900">
                {{ asUser(row).full_name }}
                <span v-if="isSelf(asUser(row))" class="text-xs font-medium text-brand-700"
                  >· вы</span
                >
              </p>
              <p class="mt-0.5 truncate text-xs text-slate-500">{{ asUser(row).email }}</p>
            </div>
          </div>
        </template>

        <template #cell-full_name="{ row }">
          <div class="flex min-w-0 items-center gap-2.5">
            <AppAvatar :name="asUser(row).full_name" size="sm" />
            <div class="min-w-0">
              <p class="flex flex-wrap items-center gap-1.5 text-sm font-semibold text-slate-900">
                <span class="truncate">{{ asUser(row).full_name }}</span>
                <AppBadge v-if="isSelf(asUser(row))" tone="brand" size="sm">Вы</AppBadge>
              </p>
              <p class="mt-0.5 truncate text-xs text-slate-500">{{ asUser(row).email }}</p>
            </div>
          </div>
        </template>

        <template #cell-role="{ row }">
          <StatusBadge kind="role" :status="asUser(row).role" />
        </template>

        <template #cell-phone="{ row }">
          <span class="whitespace-nowrap text-slate-700">{{ asUser(row).phone || '—' }}</span>
        </template>

        <template #cell-status="{ row }">
          <AppBadge :tone="asUser(row).is_active ? 'success' : 'neutral'" dot>
            {{ asUser(row).is_active ? 'Активен' : 'Заблокирован' }}
          </AppBadge>
        </template>

        <template #cell-created_at="{ row }">
          <span class="whitespace-nowrap text-slate-700">
            {{ formatDateShort(asUser(row).created_at) }}
          </span>
        </template>

        <template #cell-actions="{ row }">
          <div class="flex items-center justify-end gap-1">
            <AppButton
              variant="ghost"
              size="sm"
              aria-label="Изменить пользователя"
              title="Изменить"
              @click="openEdit(asUser(row))"
            >
              <template #icon>
                <Pencil :size="15" aria-hidden="true" />
              </template>
            </AppButton>
            <span v-if="isSelf(asUser(row))" class="px-2 text-xs text-slate-400">Это вы</span>
            <AppButton
              v-else-if="asUser(row).is_active"
              variant="ghost"
              size="sm"
              aria-label="Заблокировать пользователя"
              title="Заблокировать"
              @click="openBlock(asUser(row))"
            >
              <template #icon>
                <Ban :size="15" aria-hidden="true" />
              </template>
            </AppButton>
            <AppButton
              v-else
              variant="soft"
              size="sm"
              aria-label="Разблокировать пользователя"
              title="Разблокировать"
              :loading="
                updateMutation.isPending.value &&
                updateMutation.variables.value?.id === asUser(row).id
              "
              @click="unblockUser(asUser(row))"
            >
              <template #icon>
                <CheckCircle2 :size="15" aria-hidden="true" />
              </template>
            </AppButton>
          </div>
        </template>

        <template #mobile-actions="{ row }">
          <AppButton variant="ghost" size="sm" @click="openEdit(asUser(row))">
            <Pencil :size="15" aria-hidden="true" />
            <span class="sr-only">Изменить пользователя</span>
          </AppButton>
          <AppButton
            v-if="!isSelf(asUser(row)) && asUser(row).is_active"
            variant="ghost"
            size="sm"
            @click="openBlock(asUser(row))"
          >
            <Ban :size="15" aria-hidden="true" />
            <span class="sr-only">Заблокировать пользователя</span>
          </AppButton>
          <AppButton
            v-else-if="!isSelf(asUser(row))"
            variant="soft"
            size="sm"
            @click="unblockUser(asUser(row))"
          >
            <CheckCircle2 :size="15" aria-hidden="true" />
            <span class="sr-only">Разблокировать пользователя</span>
          </AppButton>
        </template>

        <template #empty-action>
          <AppButton size="sm" @click="createOpen = true">
            <template #icon>
              <Plus :size="15" aria-hidden="true" />
            </template>
            Новый пользователь
          </AppButton>
        </template>
      </DataTable>

      <AppPagination
        v-if="!usersQuery.isError.value && total > PAGE_SIZE"
        v-model:page="page"
        :page-size="PAGE_SIZE"
        :total="total"
      />
    </div>

    <UserFormModal v-model="createOpen" @saved="usersQuery.refetch()" />

    <UserFormModal v-model="editOpen" :user="selectedUser" @saved="usersQuery.refetch()" />

    <ConfirmDialog
      v-model="blockOpen"
      title="Заблокировать пользователя?"
      message="Пользователь не сможет войти в систему. Профиль, абонементы, платежи и история посещений сохранятся."
      confirm-label="Заблокировать"
      cancel-label="Оставить доступ"
      :loading="deactivateMutation.isPending.value"
      :error="blockError"
      @confirm="blockUser"
    />
  </div>
</template>
