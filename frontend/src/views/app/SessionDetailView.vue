<script setup lang="ts">
import { ArrowLeft, Ban, CalendarDays, Clock3, MapPin, Pencil, UserPlus, Users } from '@lucide/vue'
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { getApiErrorMessage } from '@/api/errors'
import {
  AppBadge,
  AppButton,
  ConfirmDialog,
  ErrorState,
  LoadingState,
  SkeletonBlock,
  StatusBadge,
} from '@/components/ui'
import AdminEnrollModal from '@/features/schedule/components/AdminEnrollModal.vue'
import EnrollmentList from '@/features/schedule/components/EnrollmentList.vue'
import SessionFormModal from '@/features/schedule/components/SessionFormModal.vue'
import {
  useCancelEnrollmentMutation,
  useCancelSessionMutation,
  useEnrollMutation,
  useMyEnrollmentsQuery,
  useMyTrainerQuery,
  useSessionQuery,
} from '@/features/schedule/queries'
import {
  canCancelEnrollment,
  canClientEnroll,
  findSessionEnrollment,
  getSessionAvailability,
  SESSION_AVAILABILITY_META,
} from '@/features/schedule/status'
import { formatDateLong, formatDateTime, formatDuration, formatTimeRange } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const route = useRoute()
const auth = useAuthStore()
const toast = useToastStore()

const sessionId = computed(() => String(route.params.id ?? ''))
const sessionQuery = useSessionQuery(sessionId)
const session = computed(() => sessionQuery.data.value)

const isAdmin = computed(() => auth.role === 'admin')
const isTrainer = computed(() => auth.role === 'trainer')
const isClient = computed(() => auth.role === 'client')
const isStaff = computed(() => isAdmin.value || isTrainer.value)

const myTrainerQuery = useMyTrainerQuery(computed(() => isTrainer.value))
const myEnrollmentsQuery = useMyEnrollmentsQuery(isClient)

const myEnrollment = computed(() => {
  if (!session.value) {
    return null
  }
  return findSessionEnrollment(myEnrollmentsQuery.data.value?.items, session.value.id)
})

const canManage = computed(() => {
  if (!session.value || !isStaff.value) {
    return false
  }
  if (isAdmin.value) {
    return true
  }
  return session.value.trainer_id === myTrainerQuery.data.value?.id
})

const availability = computed(() => (session.value ? getSessionAvailability(session.value) : null))
const availabilityMeta = computed(() =>
  availability.value ? SESSION_AVAILABILITY_META[availability.value] : null,
)

const canEnroll = computed(() =>
  session.value ? canClientEnroll(session.value, myEnrollment.value) : false,
)
const canCancelMyEnrollment = computed(() =>
  session.value ? canCancelEnrollment(session.value, myEnrollment.value) : false,
)

const enrollmentProgress = computed(() => {
  if (!session.value || session.value.capacity <= 0) {
    return 0
  }
  return Math.min(100, Math.round((session.value.enrolled_count / session.value.capacity) * 100))
})

const editOpen = ref(false)
const enrollOpen = ref(false)
const cancelSessionOpen = ref(false)
const cancelEnrollmentOpen = ref(false)
const enrollmentError = ref('')
const cancelSessionError = ref('')
const cancelEnrollmentError = ref('')

const enrollMutation = useEnrollMutation()
const cancelEnrollmentMutation = useCancelEnrollmentMutation()
const cancelSessionMutation = useCancelSessionMutation()

async function enrollSelf(): Promise<void> {
  if (!session.value) {
    return
  }

  enrollmentError.value = ''

  try {
    await enrollMutation.mutateAsync({ sessionId: session.value.id })
    toast.success('Вы записаны на тренировку.', 'Запись создана')
  } catch (error) {
    enrollmentError.value = getApiErrorMessage(error)
  }
}

function openCancelSession(): void {
  cancelSessionError.value = ''
  cancelSessionOpen.value = true
}

async function cancelSession(): Promise<void> {
  if (!session.value) {
    return
  }

  cancelSessionError.value = ''

  try {
    await cancelSessionMutation.mutateAsync(session.value.id)
    cancelSessionOpen.value = false
    toast.success('Тренировка отменена, активные записи закрыты.', 'Тренировка отменена')
  } catch (error) {
    cancelSessionError.value = getApiErrorMessage(error)
  }
}

function openCancelEnrollment(): void {
  cancelEnrollmentError.value = ''
  cancelEnrollmentOpen.value = true
}

async function cancelMyEnrollment(): Promise<void> {
  if (!myEnrollment.value) {
    return
  }

  cancelEnrollmentError.value = ''

  try {
    await cancelEnrollmentMutation.mutateAsync(myEnrollment.value.id)
    cancelEnrollmentOpen.value = false
    toast.success('Запись на тренировку отменена.', 'Запись отменена')
  } catch (error) {
    cancelEnrollmentError.value = getApiErrorMessage(error)
  }
}
</script>

<template>
  <div class="space-y-6">
    <RouterLink
      to="/app/schedule"
      class="inline-flex min-h-11 items-center gap-1.5 rounded-control px-1 text-sm font-medium text-slate-600 transition hover:text-slate-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
    >
      <ArrowLeft :size="16" aria-hidden="true" />
      К расписанию
    </RouterLink>

    <div
      v-if="sessionQuery.isPending.value"
      class="rounded-card border border-slate-200 bg-white p-6 shadow-sm"
    >
      <SkeletonBlock :lines="6" avatar />
    </div>

    <ErrorState
      v-else-if="sessionQuery.isError.value"
      title="Тренировка не найдена"
      :description="getApiErrorMessage(sessionQuery.error.value)"
      @retry="sessionQuery.refetch()"
    />

    <template v-else-if="session">
      <header class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-1.5">
            <AppBadge v-if="availabilityMeta" :tone="availabilityMeta.tone" dot>
              {{ availabilityMeta.label }}
            </AppBadge>
            <StatusBadge v-if="myEnrollment" kind="enrollment" :status="myEnrollment.status" />
            <AppBadge v-if="isTrainer && canManage" tone="info">Ваша тренировка</AppBadge>
          </div>
          <h2
            :class="[
              'mt-2 break-words text-2xl font-bold tracking-tight sm:text-3xl',
              session.is_cancelled ? 'text-slate-500 line-through' : 'text-slate-900',
            ]"
          >
            {{ session.title }}
          </h2>
          <p class="mt-2 text-sm leading-6 text-slate-600">
            {{ formatDateLong(session.starts_at) }} ·
            {{ formatTimeRange(session.starts_at, session.ends_at) }} ·
            {{ formatDuration(session.starts_at, session.ends_at) }}
          </p>
        </div>

        <div v-if="canManage" class="flex flex-wrap gap-2">
          <AppButton v-if="!session.is_cancelled" variant="outline" @click="editOpen = true">
            <template #icon>
              <Pencil :size="15" aria-hidden="true" />
            </template>
            Редактировать
          </AppButton>
          <AppButton v-if="!session.is_cancelled" variant="danger" @click="openCancelSession">
            <template #icon>
              <Ban :size="15" aria-hidden="true" />
            </template>
            Отменить
          </AppButton>
        </div>
      </header>

      <div
        v-if="session.is_cancelled"
        class="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm leading-6 text-rose-700"
        role="alert"
      >
        Тренировка отменена. Активные записи закрыты, записаться на неё нельзя.
      </div>

      <div class="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,0.7fr)]">
        <div class="min-w-0 space-y-6">
          <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <h3 class="text-lg font-semibold text-slate-900">О тренировке</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              {{ session.description || 'Описание не добавлено.' }}
            </p>

            <dl class="mt-5 grid gap-3 sm:grid-cols-2">
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                  <CalendarDays :size="14" aria-hidden="true" />
                  Дата
                </dt>
                <dd class="mt-1.5 text-sm font-medium text-slate-900">
                  {{ formatDateLong(session.starts_at) }}
                </dd>
              </div>
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                  <Clock3 :size="14" aria-hidden="true" />
                  Время
                </dt>
                <dd class="mt-1.5 text-sm font-medium text-slate-900">
                  {{ formatTimeRange(session.starts_at, session.ends_at) }}
                  <span class="font-normal text-slate-500">
                    · {{ formatDuration(session.starts_at, session.ends_at) }}
                  </span>
                </dd>
              </div>
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <dt class="text-xs font-medium text-slate-500">Тренер</dt>
                <dd class="mt-1.5 text-sm font-medium text-slate-900">
                  {{ session.trainer_name }}
                </dd>
              </div>
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                  <MapPin :size="14" aria-hidden="true" />
                  Зал
                </dt>
                <dd class="mt-1.5 text-sm font-medium text-slate-900">
                  {{ session.room_name }}
                </dd>
              </div>
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                  <Users :size="14" aria-hidden="true" />
                  Вместимость
                </dt>
                <dd class="mt-1.5 text-sm font-medium text-slate-900">
                  {{ session.capacity }} мест
                </dd>
              </div>
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <dt class="text-xs font-medium text-slate-500">Создана</dt>
                <dd class="mt-1.5 text-sm font-medium text-slate-900">
                  {{ formatDateTime(session.created_at) }}
                </dd>
              </div>
            </dl>
          </section>
        </div>

        <aside class="min-w-0 space-y-4">
          <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm">
            <div class="flex items-start justify-between gap-3">
              <h3 class="text-lg font-semibold text-slate-900">Запись</h3>
              <AppBadge v-if="availabilityMeta" :tone="availabilityMeta.tone" dot>
                {{ availabilityMeta.label }}
              </AppBadge>
            </div>

            <div class="mt-4 flex items-end justify-between gap-3">
              <p class="text-2xl font-bold text-slate-900">
                {{ session.enrolled_count }}
                <span class="text-sm font-medium text-slate-400">/ {{ session.capacity }}</span>
              </p>
              <p class="text-xs text-slate-500">{{ session.available_slots }} свободно</p>
            </div>
            <div
              class="mt-2 h-2 overflow-hidden rounded-full bg-slate-100"
              role="progressbar"
              :aria-valuenow="session.enrolled_count"
              aria-valuemin="0"
              :aria-valuemax="session.capacity"
              :aria-label="`Заполненность: ${session.enrolled_count} из ${session.capacity}`"
            >
              <div
                :class="[
                  'h-full rounded-full',
                  session.available_slots > 0 && !session.is_cancelled
                    ? 'bg-brand-500'
                    : 'bg-amber-500',
                ]"
                :style="{ width: `${enrollmentProgress}%` }"
              />
            </div>

            <div v-if="isClient" class="mt-5">
              <LoadingState
                v-if="myEnrollmentsQuery.isPending.value"
                compact
                label="Проверяем запись…"
              />

              <div
                v-else-if="myEnrollmentsQuery.isError.value"
                class="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
                role="alert"
              >
                Не удалось проверить вашу запись.
                <button
                  type="button"
                  class="ml-1 font-semibold underline"
                  @click="myEnrollmentsQuery.refetch()"
                >
                  Повторить
                </button>
              </div>

              <template v-else>
                <div v-if="myEnrollment?.status === 'active'">
                  <p class="text-sm leading-6 text-slate-600">Вы записаны на эту тренировку.</p>
                  <AppButton
                    v-if="canCancelMyEnrollment"
                    variant="danger"
                    block
                    class="mt-3"
                    @click="openCancelEnrollment"
                  >
                    Отменить запись
                  </AppButton>
                  <p v-else class="mt-2 text-xs leading-5 text-slate-400">
                    Отмена доступна только до начала тренировки.
                  </p>
                </div>

                <div
                  v-else-if="
                    myEnrollment?.status === 'attended' || myEnrollment?.status === 'no_show'
                  "
                >
                  <p class="text-sm leading-6 text-slate-600">
                    По этой тренировке уже есть отметка посещения.
                  </p>
                </div>

                <div v-else-if="canEnroll">
                  <AppButton block :loading="enrollMutation.isPending.value" @click="enrollSelf">
                    Записаться на тренировку
                  </AppButton>
                  <p class="mt-2 text-xs leading-5 text-slate-400">
                    Нужен действующий абонемент на дату тренировки. Свободных мест:
                    {{ session.available_slots }}.
                  </p>
                </div>

                <p v-else-if="session.is_cancelled" class="text-sm leading-6 text-slate-500">
                  Запись на отменённую тренировку недоступна.
                </p>
                <p
                  v-else-if="session.available_slots <= 0"
                  class="text-sm leading-6 text-slate-500"
                >
                  Свободных мест нет.
                </p>
                <p v-else class="text-sm leading-6 text-slate-500">Тренировка уже завершилась.</p>

                <div
                  v-if="enrollmentError"
                  class="mt-3 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm leading-5 text-rose-700"
                  role="alert"
                >
                  {{ enrollmentError }}
                </div>
              </template>
            </div>

            <div v-else-if="isStaff" class="mt-5 space-y-2">
              <AppButton
                v-if="isAdmin && !session.is_cancelled"
                variant="outline"
                block
                @click="enrollOpen = true"
              >
                <template #icon>
                  <UserPlus :size="16" aria-hidden="true" />
                </template>
                Записать клиента
              </AppButton>
              <p v-if="!canManage" class="text-xs leading-5 text-slate-500">
                Управлять тренировкой может администратор или тренер, который её ведёт.
              </p>
              <p v-else class="text-xs leading-5 text-slate-500">
                Отметки посещения доступны в списке записавшихся ниже.
              </p>
            </div>
          </section>

          <section
            v-if="isClient"
            class="rounded-card border border-slate-200 bg-white p-5 shadow-sm"
          >
            <h3 class="text-sm font-semibold text-slate-900">Правила записи</h3>
            <ul class="mt-3 space-y-2 text-xs leading-5 text-slate-500">
              <li>Нужен действующий абонемент на дату тренировки.</li>
              <li>Нельзя записаться на две пересекающиеся тренировки.</li>
              <li>Отменить запись можно до начала занятия.</li>
              <li>Отметку посещения ставит тренер или администратор.</li>
            </ul>
          </section>
        </aside>
      </div>

      <EnrollmentList v-if="isStaff && canManage" :session="session" />
    </template>

    <SessionFormModal
      v-if="session"
      v-model="editOpen"
      :session="session"
      @saved="sessionQuery.refetch()"
    />

    <AdminEnrollModal
      v-if="session && isAdmin"
      v-model="enrollOpen"
      :session="session"
      @enrolled="sessionQuery.refetch()"
    />

    <ConfirmDialog
      v-model="cancelSessionOpen"
      title="Отменить тренировку?"
      message="Все активные записи будут отменены. Клиенты увидят тренировку как отменённую."
      confirm-label="Отменить тренировку"
      cancel-label="Не отменять"
      :loading="cancelSessionMutation.isPending.value"
      :error="cancelSessionError"
      @confirm="cancelSession"
    />

    <ConfirmDialog
      v-model="cancelEnrollmentOpen"
      title="Отменить запись?"
      message="Вы сможете записаться снова, если останутся свободные места и действует абонемент."
      confirm-label="Отменить запись"
      cancel-label="Оставить"
      :loading="cancelEnrollmentMutation.isPending.value"
      :error="cancelEnrollmentError"
      @confirm="cancelMyEnrollment"
    />
  </div>
</template>
