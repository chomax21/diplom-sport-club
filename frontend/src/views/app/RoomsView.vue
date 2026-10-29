<script setup lang="ts">
import { Building2, Pencil, Plus, RefreshCw, Users } from '@lucide/vue'
import { computed, ref } from 'vue'

import type { RoomRecord } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import {
  AppBadge,
  AppButton,
  AppSwitch,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  SkeletonBlock,
} from '@/components/ui'
import RoomFormModal from '@/features/directory/components/RoomFormModal.vue'
import {
  useDeactivateRoomMutation,
  useRoomListQuery,
  useUpdateRoomMutation,
} from '@/features/directory/queries'
import { roomCapacityLabel } from '@/features/directory/utils'
import { useToastStore } from '@/stores/toasts'

const toast = useToastStore()

const includeInactive = ref(false)
const formOpen = ref(false)
const editingRoom = ref<RoomRecord | null>(null)

const deactivateOpen = ref(false)
const deactivateTarget = ref<RoomRecord | null>(null)
const deactivateError = ref('')

const params = computed(() => ({
  include_inactive: includeInactive.value,
  limit: 200,
}))

const roomsQuery = useRoomListQuery(params)
const deactivateMutation = useDeactivateRoomMutation()
const updateMutation = useUpdateRoomMutation()

const rooms = computed<RoomRecord[]>(() => roomsQuery.data.value?.items ?? [])
const activeCount = computed(() => rooms.value.filter((room) => room.is_active).length)

function openCreate(): void {
  editingRoom.value = null
  formOpen.value = true
}

function openEdit(room: RoomRecord): void {
  editingRoom.value = room
  formOpen.value = true
}

function openDeactivate(room: RoomRecord): void {
  deactivateTarget.value = room
  deactivateError.value = ''
  deactivateOpen.value = true
}

async function deactivateRoom(): Promise<void> {
  if (!deactivateTarget.value) {
    return
  }

  deactivateError.value = ''

  try {
    await deactivateMutation.mutateAsync(deactivateTarget.value.id)
    deactivateOpen.value = false
    toast.success(
      'Зал скрыт из выбора при создании тренировок. Существующее расписание не изменилось.',
      'Зал отключён',
    )
    deactivateTarget.value = null
  } catch (error) {
    deactivateError.value = getApiErrorMessage(error)
  }
}

async function activateRoom(room: RoomRecord): Promise<void> {
  try {
    await updateMutation.mutateAsync({ id: room.id, payload: { is_active: true } })
    toast.success(`«${room.name}» снова доступен в расписании.`, 'Зал включён')
  } catch (error) {
    toast.error(getApiErrorMessage(error), 'Не удалось включить зал')
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Клуб</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Залы</h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Помещения клуба, вместимость и доступность для расписания. Отключённый зал остаётся в
          истории тренировок.
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="roomsQuery.isFetching.value"
          @click="roomsQuery.refetch()"
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
          Новый зал
        </AppButton>
      </div>
    </section>

    <section
      class="flex flex-col gap-3 rounded-panel border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
    >
      <AppSwitch
        v-model="includeInactive"
        label="Показывать отключённые"
        description="В расписании доступны только активные залы"
      />
      <div class="flex shrink-0 items-center gap-2">
        <AppBadge tone="success">{{ activeCount }} активных</AppBadge>
        <AppBadge tone="neutral">{{ rooms.length }} всего</AppBadge>
      </div>
    </section>

    <div v-if="roomsQuery.isPending.value" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="index in 4"
        :key="index"
        class="rounded-card border border-slate-200 bg-white p-5 shadow-sm"
      >
        <SkeletonBlock :lines="4" />
      </div>
    </div>

    <ErrorState
      v-else-if="roomsQuery.isError.value"
      title="Не удалось загрузить залы"
      :description="getApiErrorMessage(roomsQuery.error.value)"
      @retry="roomsQuery.refetch()"
    />

    <EmptyState
      v-else-if="rooms.length === 0"
      title="Залы не добавлены"
      description="Создайте первый зал, чтобы планировать тренировки."
      :icon="Building2"
    >
      <template #actions>
        <AppButton size="sm" @click="openCreate">
          <template #icon>
            <Plus :size="15" aria-hidden="true" />
          </template>
          Новый зал
        </AppButton>
      </template>
    </EmptyState>

    <div v-else class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="room in rooms"
        :key="room.id"
        class="flex min-w-0 flex-col rounded-card border border-slate-200 bg-white p-5 shadow-sm"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-1.5">
              <AppBadge :tone="room.is_active ? 'success' : 'neutral'" dot>
                {{ room.is_active ? 'Доступен' : 'Отключён' }}
              </AppBadge>
            </div>
            <h3 class="mt-2 break-words text-base font-semibold text-slate-900">
              {{ room.name }}
            </h3>
          </div>
          <span
            class="grid size-10 shrink-0 place-items-center rounded-2xl bg-brand-50 text-brand-700"
            aria-hidden="true"
          >
            <Building2 :size="19" />
          </span>
        </div>

        <p class="mt-2 text-sm leading-6 text-slate-600">
          {{ room.description || 'Описание не добавлено.' }}
        </p>

        <p class="mt-3 inline-flex items-center gap-1.5 text-xs text-slate-500">
          <Users :size="14" aria-hidden="true" />
          Вместимость:
          <span class="font-semibold text-slate-700">{{ roomCapacityLabel(room.capacity) }}</span>
        </p>

        <div class="mt-auto flex flex-wrap justify-end gap-1.5 pt-5">
          <AppButton variant="outline" size="sm" @click="openEdit(room)">
            <template #icon>
              <Pencil :size="14" aria-hidden="true" />
            </template>
            Изменить
          </AppButton>
          <AppButton v-if="room.is_active" variant="ghost" size="sm" @click="openDeactivate(room)">
            Отключить
          </AppButton>
          <AppButton
            v-else
            variant="soft"
            size="sm"
            :loading="
              updateMutation.isPending.value && updateMutation.variables.value?.id === room.id
            "
            @click="activateRoom(room)"
          >
            Включить
          </AppButton>
        </div>
      </article>
    </div>

    <RoomFormModal v-model="formOpen" :room="editingRoom" @saved="roomsQuery.refetch()" />

    <ConfirmDialog
      v-model="deactivateOpen"
      title="Отключить зал?"
      message="Зал исчезнет из выбора при создании тренировок. Уже созданные тренировки и их расписание останутся без изменений."
      confirm-label="Отключить зал"
      cancel-label="Оставить"
      :loading="deactivateMutation.isPending.value"
      :error="deactivateError"
      @confirm="deactivateRoom"
    />
  </div>
</template>
