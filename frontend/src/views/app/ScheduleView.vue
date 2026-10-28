<script setup lang="ts">
import { CalendarX2, Plus, RefreshCw } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import type { Enrollment, TrainingSession, TrainingSessionListParams } from '@/api/schedule'
import { getApiErrorMessage } from '@/api/errors'
import {
  AppBadge,
  AppButton,
  AppSelect,
  AppSwitch,
  DateRangePicker,
  EmptyState,
  ErrorState,
  FilterBar,
  SearchInput,
  SkeletonBlock,
} from '@/components/ui'
import SessionCard from '@/features/schedule/components/SessionCard.vue'
import SessionFormModal from '@/features/schedule/components/SessionFormModal.vue'
import {
  useMyEnrollmentsQuery,
  useRoomsQuery,
  useSessionsQuery,
  useTrainersQuery,
} from '@/features/schedule/queries'
import { addDaysDateInput, dayKey, formatDayHeading, todayDateInput } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'

const PAGE_SIZE = 10
const defaultFrom = todayDateInput()
const defaultTo = addDaysDateInput(30)

const auth = useAuthStore()
const isStaff = computed(() => auth.role === 'admin' || auth.role === 'trainer')
const isTrainer = computed(() => auth.role === 'trainer')
const isClient = computed(() => auth.role === 'client')

const search = ref('')
const dateFrom = ref<string | null>(defaultFrom)
const dateTo = ref<string | null>(defaultTo)
const trainerId = ref<string | number>('')
const roomId = ref<string | number>('')
const includeCancelled = ref(false)
const page = ref(1)

const roomsQuery = useRoomsQuery()
const trainersQuery = useTrainersQuery()
const myEnrollmentsQuery = useMyEnrollmentsQuery(isClient)

const myTrainerId = computed(() => {
  if (!isTrainer.value || !auth.user) {
    return ''
  }

  return (
    trainersQuery.data.value?.items.find(
      (trainer) => trainer.email.toLowerCase() === auth.user?.email.toLowerCase(),
    )?.id ?? ''
  )
})

watch(
  myTrainerId,
  (value) => {
    if (isTrainer.value && value && !trainerId.value) {
      trainerId.value = value
    }
  },
  { immediate: true },
)

const roomOptions = computed(() =>
  (roomsQuery.data.value?.items ?? []).map((room) => ({
    label: room.name,
    value: room.id,
  })),
)

const trainerOptions = computed(() =>
  (trainersQuery.data.value?.items ?? [])
    .filter((trainer) => trainer.is_active)
    .map((trainer) => ({
      label: trainer.full_name,
      value: trainer.id,
    })),
)

const isDefaultTrainerFilter = computed(
  () => isTrainer.value && Boolean(myTrainerId.value) && trainerId.value === myTrainerId.value,
)

const activeFilterCount = computed(() => {
  let count = 0
  if (search.value.trim()) count += 1
  if (trainerId.value && !isDefaultTrainerFilter.value) count += 1
  if (roomId.value) count += 1
  if (isStaff.value && includeCancelled.value) count += 1
  if (dateFrom.value !== defaultFrom || dateTo.value !== defaultTo) count += 1
  return count
})

const hasActiveFilters = computed(() => activeFilterCount.value > 0)

const params = computed<TrainingSessionListParams>(() => ({
  date_from: dateFrom.value ?? undefined,
  date_to: dateTo.value ?? undefined,
  trainer_id: typeof trainerId.value === 'string' && trainerId.value ? trainerId.value : undefined,
  room_id: typeof roomId.value === 'string' && roomId.value ? roomId.value : undefined,
  include_cancelled: isStaff.value ? includeCancelled.value : undefined,
  search: search.value.trim() || undefined,
  limit: PAGE_SIZE,
  offset: (page.value - 1) * PAGE_SIZE,
}))

const sessionsEnabled = computed(() => !isTrainer.value || Boolean(trainerId.value))
const sessionsQuery = useSessionsQuery(params, sessionsEnabled)

const sessions = computed<TrainingSession[]>(() => sessionsQuery.data.value?.items ?? [])
const total = computed(() => sessionsQuery.data.value?.total ?? 0)
const sessionsError = computed(() => getApiErrorMessage(sessionsQuery.error.value))

const enrollmentBySession = computed(() => {
  const map = new Map<string, Enrollment>()
  for (const enrollment of myEnrollmentsQuery.data.value?.items ?? []) {
    map.set(enrollment.session_id, enrollment)
  }
  return map
})

function enrollmentFor(sessionId: string): Enrollment | null {
  return enrollmentBySession.value.get(sessionId) ?? null
}

const groups = computed(() => {
  const map = new Map<string, TrainingSession[]>()

  for (const session of sessions.value) {
    const key = dayKey(session.starts_at)
    const list = map.get(key)
    if (list) {
      list.push(session)
    } else {
      map.set(key, [session])
    }
  }

  return Array.from(map.entries()).map(([key, items]) => ({
    key,
    label: formatDayHeading(key),
    items,
  }))
})

const formOpen = ref(false)
const formDefaultDate = ref(defaultFrom)

watch([search, dateFrom, dateTo, trainerId, roomId, includeCancelled], () => {
  page.value = 1
})

function resetFilters(): void {
  search.value = ''
  dateFrom.value = defaultFrom
  dateTo.value = defaultTo
  trainerId.value = isTrainer.value ? myTrainerId.value : ''
  roomId.value = ''
  includeCancelled.value = false
  page.value = 1
}

function openCreate(): void {
  const today = todayDateInput()
  formDefaultDate.value =
    dateFrom.value && dateFrom.value > today ? dateFrom.value : addDaysDateInput(1)
  formOpen.value = true
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">Расписание</p>
        <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Тренировки клуба
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          {{
            isClient
              ? 'Выбирайте подходящую тренировку и записывайтесь. Запись можно отменить до начала занятия.'
              : 'Создавайте тренировки, следите за заполняемостью и отмечайте посещения клиентов.'
          }}
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <AppButton
          variant="outline"
          :loading="sessionsQuery.isFetching.value"
          @click="sessionsQuery.refetch()"
        >
          <template #icon>
            <RefreshCw :size="15" aria-hidden="true" />
          </template>
          Обновить
        </AppButton>
        <AppButton v-if="isStaff" @click="openCreate">
          <template #icon>
            <Plus :size="16" aria-hidden="true" />
          </template>
          Новая тренировка
        </AppButton>
      </div>
    </section>

    <FilterBar
      :active-count="activeFilterCount"
      :has-active-filters="hasActiveFilters"
      :columns="3"
      @reset="resetFilters"
    >
      <SearchInput
        v-model="search"
        aria-label="Поиск тренировок"
        placeholder="Название тренировки…"
      />
      <DateRangePicker
        v-model:from="dateFrom"
        v-model:to="dateTo"
        class="sm:col-span-2"
        label="Период"
      />
      <AppSelect
        v-model="trainerId"
        label="Тренер"
        :options="trainerOptions"
        placeholder="Все тренеры"
        :disabled="isTrainer && Boolean(myTrainerId)"
      />
      <AppSelect v-model="roomId" label="Зал" :options="roomOptions" placeholder="Все залы" />
      <AppSwitch
        v-if="isStaff"
        v-model="includeCancelled"
        label="Отменённые"
        description="Показывать отменённые тренировки"
      />
    </FilterBar>

    <div v-if="sessionsQuery.isPending.value" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="index in 6"
        :key="index"
        class="rounded-card border border-slate-200 bg-white p-5 shadow-sm"
      >
        <SkeletonBlock :lines="4" />
      </div>
    </div>

    <ErrorState
      v-else-if="sessionsQuery.isError.value"
      title="Не удалось загрузить расписание"
      :description="sessionsError"
      @retry="sessionsQuery.refetch()"
    />

    <EmptyState
      v-else-if="sessions.length === 0"
      title="Тренировок не найдено"
      description="Измените период или фильтры, чтобы увидеть другие занятия."
      :icon="CalendarX2"
    >
      <template #actions>
        <AppButton v-if="hasActiveFilters" variant="outline" size="sm" @click="resetFilters">
          Сбросить фильтры
        </AppButton>
        <AppButton v-if="isStaff" size="sm" @click="openCreate">
          <template #icon>
            <Plus :size="15" aria-hidden="true" />
          </template>
          Создать тренировку
        </AppButton>
      </template>
    </EmptyState>

    <template v-else>
      <section
        v-for="group in groups"
        :key="group.key"
        class="space-y-3"
        :aria-labelledby="`schedule-day-${group.key}`"
      >
        <div class="flex items-center gap-2">
          <h3 :id="`schedule-day-${group.key}`" class="text-sm font-semibold text-slate-900">
            {{ group.label }}
          </h3>
          <AppBadge tone="neutral">{{ group.items.length }}</AppBadge>
        </div>
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <SessionCard
            v-for="session in group.items"
            :key="session.id"
            :session="session"
            :enrollment="enrollmentFor(session.id)"
          />
        </div>
      </section>

      <AppPagination
        v-if="total > PAGE_SIZE"
        v-model:page="page"
        :page-size="PAGE_SIZE"
        :total="total"
      />
    </template>

    <SessionFormModal
      v-model="formOpen"
      :default-date="formDefaultDate"
      @saved="sessionsQuery.refetch()"
    />
  </div>
</template>
