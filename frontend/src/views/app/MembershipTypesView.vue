<script setup lang="ts">
import { CircleCheck, Pencil, Plus, RefreshCw, Tags, Ticket } from '@lucide/vue'
import { computed, ref } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import type { MembershipType } from '@/api/memberships'
import {
  AppBadge,
  AppButton,
  AppSwitch,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  SkeletonBlock,
} from '@/components/ui'
import MembershipTypeCard from '@/features/memberships/components/MembershipTypeCard.vue'
import MembershipTypeFormModal from '@/features/memberships/components/MembershipTypeFormModal.vue'
import {
  useDeactivateMembershipTypeMutation,
  useMembershipTypesQuery,
  useUpdateMembershipTypeMutation,
} from '@/features/memberships/queries'
import { useToastStore } from '@/stores/toasts'

const toast = useToastStore()

const includeInactive = ref(false)
const formOpen = ref(false)
const editingType = ref<MembershipType | null>(null)

const deactivateOpen = ref(false)
const deactivateTarget = ref<MembershipType | null>(null)
const deactivateError = ref('')

const params = computed(() => ({
  include_inactive: includeInactive.value,
  limit: 200,
}))

const typesQuery = useMembershipTypesQuery(params)
const deactivateMutation = useDeactivateMembershipTypeMutation()
const updateMutation = useUpdateMembershipTypeMutation()

const types = computed(() => typesQuery.data.value?.items ?? [])
const activeCount = computed(() => types.value.filter((item) => item.is_active).length)

function openCreate(): void {
  editingType.value = null
  formOpen.value = true
}

function openEdit(type: MembershipType): void {
  editingType.value = type
  formOpen.value = true
}

function openDeactivate(type: MembershipType): void {
  deactivateTarget.value = type
  deactivateError.value = ''
  deactivateOpen.value = true
}

async function deactivateType(): Promise<void> {
  if (!deactivateTarget.value) {
    return
  }

  deactivateError.value = ''

  try {
    await deactivateMutation.mutateAsync(deactivateTarget.value.id)
    deactivateOpen.value = false
    toast.success(
      'Вид абонемента скрыт из каталога. Оформленные абонементы продолжают действовать.',
      'Вид отключён',
    )
    deactivateTarget.value = null
  } catch (error) {
    deactivateError.value = getApiErrorMessage(error)
  }
}

async function activateType(type: MembershipType): Promise<void> {
  try {
    await updateMutation.mutateAsync({ id: type.id, payload: { is_active: true } })
    toast.success(`«${type.name}» снова доступен для продажи.`, 'Вид включён')
  } catch (error) {
    toast.error(getApiErrorMessage(error), 'Не удалось включить вид')
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Каталог</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Виды абонементов
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Настройте стоимость, срок действия и лимит посещений. Отключённые виды остаются в истории,
          но недоступны клиентам для покупки.
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="typesQuery.isFetching.value"
          @click="typesQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton @click="openCreate">
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          Новый вид
        </AppButton>
      </div>
    </section>

    <section
      class="flex flex-col gap-3 rounded-panel border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
    >
      <AppSwitch
        v-model="includeInactive"
        label="Показывать отключённые"
        description="В каталоге клиентов отключённые виды не отображаются"
      />
      <div class="flex shrink-0 items-center gap-2">
        <AppBadge tone="success">{{ activeCount }} активных</AppBadge>
        <AppBadge tone="neutral">{{ types.length }} всего</AppBadge>
      </div>
    </section>

    <div v-if="typesQuery.isPending.value" class="grid gap-3 sm:grid-cols-2">
      <div
        v-for="index in 6"
        :key="index"
        class="rounded-card border border-slate-200 bg-white p-5 shadow-sm"
      >
        <SkeletonBlock :lines="4" />
      </div>
    </div>

    <ErrorState
      v-else-if="typesQuery.isError.value"
      title="Не удалось загрузить виды абонементов"
      :description="getApiErrorMessage(typesQuery.error.value)"
      @retry="typesQuery.refetch()"
    />

    <EmptyState
      v-else-if="types.length === 0"
      title="Видов абонементов нет"
      description="Создайте первый вид, чтобы клиенты могли покупать абонементы."
      :icon="Ticket"
    >
      <template #actions>
        <AppButton size="sm" @click="openCreate">
          <template #icon>
            <Plus :size="15" aria-hidden="true" />
          </template>
          Создать вид
        </AppButton>
      </template>
    </EmptyState>

    <div v-else class="grid gap-3 sm:grid-cols-2">
      <MembershipTypeCard v-for="item in types" :key="item.id" :type="item" show-status>
        <template #actions>
          <div class="flex flex-wrap justify-end gap-1.5">
            <AppButton variant="outline" size="sm" @click="openEdit(item)">
              <template #icon>
                <Pencil :size="14" aria-hidden="true" />
              </template>
              Изменить
            </AppButton>
            <AppButton
              v-if="item.is_active"
              variant="ghost"
              size="sm"
              @click="openDeactivate(item)"
            >
              Отключить
            </AppButton>
            <AppButton
              v-else
              variant="soft"
              size="sm"
              :loading="
                updateMutation.isPending.value && updateMutation.variables.value?.id === item.id
              "
              @click="activateType(item)"
            >
              <template #icon>
                <CircleCheck :size="14" aria-hidden="true" />
              </template>
              Включить
            </AppButton>
          </div>
        </template>
      </MembershipTypeCard>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white p-4 text-xs leading-5 text-slate-500">
      <div class="flex items-start gap-2.5">
        <Tags :size="16" class="mt-0.5 shrink-0 text-slate-400" aria-hidden="true" />
        <p>
          Изменение стоимости не затрагивает уже оформленные абонементы: цена фиксируется в платеже
          в момент покупки.
        </p>
      </div>
    </div>

    <MembershipTypeFormModal v-model="formOpen" :type="editingType" @saved="typesQuery.refetch()" />

    <ConfirmDialog
      v-model="deactivateOpen"
      title="Отключить вид абонемента?"
      message="Он исчезнет из каталога, и клиенты не смогут его купить. Уже оформленные абонементы продолжат действовать."
      confirm-label="Отключить вид"
      cancel-label="Оставить"
      :loading="deactivateMutation.isPending.value"
      :error="deactivateError"
      @confirm="deactivateType"
    />
  </div>
</template>
