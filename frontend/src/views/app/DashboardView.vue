<script setup lang="ts">
import {
  ArrowRight,
  Building,
  CalendarDays,
  ChartColumn,
  Clock3,
  CreditCard,
  Dumbbell,
  MapPin,
  Tags,
  UserCog,
  Users,
  Wallet,
} from '@lucide/vue'
import { computed, type Component } from 'vue'
import { RouterLink } from 'vue-router'

import { getApiErrorMessage } from '@/api/errors'
import type { Membership } from '@/api/memberships'
import type { TrainingSession } from '@/api/schedule'
import type { UserRole } from '@/api/types'
import { AppBadge, EmptyState, SkeletonBlock, StatusBadge } from '@/components/ui'
import { useClientListQuery } from '@/features/directory/queries'
import { useMembershipsQuery } from '@/features/memberships/queries'
import {
  daysUntilDate,
  durationDaysLabel,
  membershipExpiryLabel,
  visitsLeftLabel,
} from '@/features/memberships/status'
import { useAttendanceReportQuery, useRevenueReportQuery } from '@/features/reports/queries'
import { formatCount, formatPercent } from '@/features/reports/utils'
import {
  useMyEnrollmentsQuery,
  useMyTrainerQuery,
  useSessionsQuery,
} from '@/features/schedule/queries'
import {
  addDaysDateInput,
  formatDateLong,
  formatDateShort,
  formatDuration,
  formatTimeRange,
  todayDateInput,
} from '@/lib/datetime'
import { formatMoney } from '@/lib/format'
import { ROLE_BADGE_CLASSES, roleLabel } from '@/lib/roles'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const isAdmin = computed(() => auth.role === 'admin')
const isTrainer = computed(() => auth.role === 'trainer')
const isClient = computed(() => auth.role === 'client')

const firstName = computed(() => auth.user?.full_name.trim().split(/\s+/)[0] ?? 'коллега')
const roleBadgeClass = computed(() =>
  auth.role ? ROLE_BADGE_CLASSES[auth.role] : 'bg-slate-100 text-slate-600',
)

const dashboardDescription = computed(() => {
  const descriptions: Record<UserRole, string> = {
    admin: 'Выручка, посещаемость и ближайшие тренировки клуба за последние 30 дней.',
    trainer: 'Ваши тренировки на сегодня, загрузка групп и быстрый переход к отчётам.',
    client: 'Действующий абонемент, остаток визитов и ближайшая запись на тренировку.',
  }

  return auth.role ? descriptions[auth.role] : 'Обзор информационной системы клуба.'
})

const today = todayDateInput()
const in30Days = addDaysDateInput(30)
const in7Days = addDaysDateInput(7)
const monthAgo = addDaysDateInput(-29)

const activeMembershipsQuery = useMembershipsQuery(
  computed(() => ({ status: 'active', limit: 1 })),
  isClient,
)
const myEnrollmentsQuery = useMyEnrollmentsQuery(isClient)
const clientSessionsQuery = useSessionsQuery(
  computed(() => ({
    date_from: today,
    date_to: in30Days,
    limit: 200,
  })),
  isClient,
)

const activeMembership = computed<Membership | null>(
  () => activeMembershipsQuery.data.value?.items[0] ?? null,
)

const clientNextSession = computed<TrainingSession | null>(() => {
  const activeIds = new Set(
    (myEnrollmentsQuery.data.value?.items ?? [])
      .filter((enrollment) => enrollment.status === 'active')
      .map((enrollment) => enrollment.session_id),
  )
  const now = Date.now()

  return (
    (clientSessionsQuery.data.value?.items ?? [])
      .filter(
        (session) =>
          activeIds.has(session.id) &&
          !session.is_cancelled &&
          new Date(session.starts_at).getTime() >= now,
      )
      .sort((left, right) => left.starts_at.localeCompare(right.starts_at))[0] ?? null
  )
})

const clientDaysLeft = computed(() => {
  if (!activeMembership.value) {
    return null
  }
  return daysUntilDate(activeMembership.value.ends_at)
})

const clientDaysLabel = computed(() => {
  if (clientDaysLeft.value === null) {
    return '—'
  }
  return clientDaysLeft.value < 0 ? 'Срок истёк' : durationDaysLabel(clientDaysLeft.value)
})

const clientError = computed(() => {
  const error =
    activeMembershipsQuery.error.value ??
    myEnrollmentsQuery.error.value ??
    clientSessionsQuery.error.value
  return error ? getApiErrorMessage(error) : ''
})

const clientLoading = computed(
  () =>
    activeMembershipsQuery.isPending.value ||
    myEnrollmentsQuery.isPending.value ||
    clientSessionsQuery.isPending.value,
)

const myTrainerQuery = useMyTrainerQuery(isTrainer)
const trainerId = computed(() => myTrainerQuery.data.value?.id ?? '')
const trainerSessionsQuery = useSessionsQuery(
  computed(() => ({
    date_from: today,
    date_to: today,
    trainer_id: trainerId.value,
    limit: 200,
    include_cancelled: false,
  })),
  computed(() => isTrainer.value && Boolean(trainerId.value)),
)

const trainerSessions = computed(() =>
  [...(trainerSessionsQuery.data.value?.items ?? [])].sort((left, right) =>
    left.starts_at.localeCompare(right.starts_at),
  ),
)
const trainerEnrolled = computed(() =>
  trainerSessions.value.reduce((sum, session) => sum + session.enrolled_count, 0),
)
const trainerCapacity = computed(() =>
  trainerSessions.value.reduce((sum, session) => sum + session.capacity, 0),
)
const trainerFillRate = computed(() =>
  trainerCapacity.value > 0 ? Math.round((trainerEnrolled.value / trainerCapacity.value) * 100) : 0,
)

const trainerError = computed(() => {
  const error = myTrainerQuery.error.value ?? trainerSessionsQuery.error.value
  return error ? getApiErrorMessage(error) : ''
})

const trainerLoading = computed(
  () => myTrainerQuery.isPending.value || trainerSessionsQuery.isPending.value,
)

const adminPeriod = computed(() => ({
  date_from: monthAgo,
  date_to: today,
}))

const attendanceQuery = useAttendanceReportQuery(adminPeriod, isAdmin)
const revenueQuery = useRevenueReportQuery(adminPeriod, isAdmin)
const upcomingSessionsQuery = useSessionsQuery(
  computed(() => ({
    date_from: today,
    date_to: in7Days,
    limit: 6,
    include_cancelled: false,
  })),
  isAdmin,
)
const clientsCountQuery = useClientListQuery(
  computed(() => ({ limit: 1 })),
  isAdmin,
)

const revenue = computed(() => revenueQuery.data.value)
const attendance = computed(() => attendanceQuery.data.value)
const upcomingSessions = computed(() => upcomingSessionsQuery.data.value?.items ?? [])

const adminMetrics = computed<
  Array<{ label: string; value: string; hint: string; icon: Component; tone: string }>
>(() => [
  {
    label: 'Выручка за 30 дней',
    value: revenue.value ? formatMoney(revenue.value.total_amount) : '—',
    hint: revenue.value ? `${formatCount(revenue.value.payments_count)} платежей` : 'загрузка',
    icon: Wallet,
    tone: 'bg-emerald-50 text-emerald-700',
  },
  {
    label: 'Посещаемость',
    value: attendance.value ? formatPercent(attendance.value.attendance_rate) : '—',
    hint: attendance.value
      ? `${formatCount(attendance.value.attended_count)} посещений`
      : 'загрузка',
    icon: ChartColumn,
    tone: 'bg-sky-50 text-sky-700',
  },
  {
    label: 'Тренировки',
    value: attendance.value ? formatCount(attendance.value.sessions_count) : '—',
    hint: 'за последние 30 дней',
    icon: CalendarDays,
    tone: 'bg-brand-50 text-brand-700',
  },
  {
    label: 'Клиенты',
    value: clientsCountQuery.data.value ? formatCount(clientsCountQuery.data.value.total) : '—',
    hint: 'в базе клуба',
    icon: Users,
    tone: 'bg-violet-50 text-violet-700',
  },
])

const adminError = computed(() => {
  const error =
    revenueQuery.error.value ??
    attendanceQuery.error.value ??
    upcomingSessionsQuery.error.value ??
    clientsCountQuery.error.value
  return error ? getApiErrorMessage(error) : ''
})

const adminLoading = computed(() => revenueQuery.isPending.value || attendanceQuery.isPending.value)

interface QuickLink {
  to: string
  title: string
  text: string
  icon: Component
  roles?: UserRole[]
}

const quickLinks: QuickLink[] = [
  {
    to: '/app/schedule',
    title: 'Расписание',
    text: 'Тренировки, залы и запись',
    icon: CalendarDays,
  },
  {
    to: '/app/memberships',
    title: 'Абонементы',
    text: 'Оформление, остаток и срок',
    icon: CreditCard,
    roles: ['admin', 'client'],
  },
  {
    to: '/app/payments',
    title: 'Платежи',
    text: 'История операций и возвраты',
    icon: Wallet,
    roles: ['admin', 'client'],
  },
  {
    to: '/app/reports',
    title: 'Отчёты',
    text: 'Посещаемость и выручка',
    icon: ChartColumn,
    roles: ['admin', 'trainer'],
  },
  {
    to: '/app/clients',
    title: 'Клиенты',
    text: 'Карточки и контакты',
    icon: Users,
    roles: ['admin', 'trainer'],
  },
  {
    to: '/app/trainers',
    title: 'Тренеры',
    text: 'Профили и специализация',
    icon: Dumbbell,
    roles: ['admin'],
  },
  {
    to: '/app/membership-types',
    title: 'Виды абонементов',
    text: 'Цены и условия',
    icon: Tags,
    roles: ['admin'],
  },
  {
    to: '/app/rooms',
    title: 'Залы',
    text: 'Вместимость и доступность',
    icon: Building,
    roles: ['admin'],
  },
  {
    to: '/app/users',
    title: 'Пользователи',
    text: 'Роли и блокировка доступа',
    icon: UserCog,
    roles: ['admin'],
  },
]

const visibleQuickLinks = computed(() => quickLinks.filter((link) => auth.hasRole(link.roles)))
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">
          {{ isAdmin ? 'Обзор клуба' : isTrainer ? 'Рабочий день' : 'Личный кабинет' }}
        </p>
        <div class="mt-1 flex flex-wrap items-center gap-2.5">
          <h2 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Здравствуйте, {{ firstName }}
          </h2>
          <span
            :class="[
              'inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold',
              roleBadgeClass,
            ]"
          >
            {{ roleLabel(auth.role) }}
          </span>
        </div>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          {{ dashboardDescription }}
        </p>
      </div>
      <RouterLink
        to="/app/profile"
        class="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-control border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
      >
        Мой профиль
        <ArrowRight :size="15" aria-hidden="true" />
      </RouterLink>
    </section>

    <div
      v-if="(isClient && clientError) || (isTrainer && trainerError) || (isAdmin && adminError)"
      class="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm leading-6 text-rose-700"
      role="alert"
    >
      Не удалось загрузить часть данных дашборда:
      {{ isClient ? clientError : isTrainer ? trainerError : adminError }}
    </div>

    <!-- CLIENT -->
    <template v-if="isClient">
      <div class="grid min-w-0 gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
        <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-slate-900">Абонемент</p>
              <p class="mt-1 text-xs text-slate-500">Действующий доступ к тренировкам</p>
            </div>
            <CreditCard :size="20" class="shrink-0 text-brand-600" aria-hidden="true" />
          </div>

          <div v-if="clientLoading" class="mt-4">
            <SkeletonBlock :lines="3" />
          </div>

          <div v-else-if="activeMembership" class="mt-4 space-y-4">
            <div class="flex flex-wrap items-center gap-1.5">
              <StatusBadge kind="membership" :status="activeMembership.status" />
              <AppBadge v-if="membershipExpiryLabel(activeMembership)" tone="warning">
                {{ membershipExpiryLabel(activeMembership) }}
              </AppBadge>
            </div>
            <div>
              <h3 class="text-xl font-bold text-slate-900">
                {{ activeMembership.membership_type_name }}
              </h3>
              <p class="mt-1 text-sm text-slate-500">
                Действует до {{ formatDateShort(activeMembership.ends_at) }}
              </p>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-2xl bg-brand-50 p-3.5">
                <p class="text-xs text-brand-700/80">Остаток</p>
                <p class="mt-1 text-lg font-bold text-brand-900">
                  {{ visitsLeftLabel(activeMembership.visits_left) }}
                </p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-3.5">
                <p class="text-xs text-slate-500">Срок</p>
                <p class="mt-1 text-lg font-bold text-slate-900">
                  {{ clientDaysLabel }}
                </p>
              </div>
            </div>
            <RouterLink
              to="/app/memberships"
              class="inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold text-brand-700 hover:text-brand-800"
            >
              Мои абонементы
              <ArrowRight :size="15" aria-hidden="true" />
            </RouterLink>
          </div>

          <EmptyState
            v-else
            class="mt-4"
            compact
            title="Активного абонемента нет"
            description="Купите абонемент, чтобы записываться на тренировки."
          >
            <template #actions>
              <RouterLink
                to="/app/memberships"
                class="inline-flex min-h-10 items-center rounded-control bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"
              >
                Перейти в каталог
              </RouterLink>
            </template>
          </EmptyState>
        </section>

        <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-slate-900">Ближайшая тренировка</p>
              <p class="mt-1 text-xs text-slate-500">Ваша активная запись</p>
            </div>
            <CalendarDays :size="20" class="shrink-0 text-sky-600" aria-hidden="true" />
          </div>

          <div v-if="clientLoading" class="mt-4">
            <SkeletonBlock :lines="3" avatar />
          </div>

          <div v-else-if="clientNextSession" class="mt-4">
            <p class="text-sm font-medium text-brand-700">
              {{ formatDateLong(clientNextSession.starts_at) }}
            </p>
            <h3 class="mt-1 break-words text-xl font-bold text-slate-900">
              {{ clientNextSession.title }}
            </h3>
            <div class="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
              <span class="inline-flex items-center gap-1.5">
                <Clock3 :size="14" aria-hidden="true" />
                {{ formatTimeRange(clientNextSession.starts_at, clientNextSession.ends_at) }}
                · {{ formatDuration(clientNextSession.starts_at, clientNextSession.ends_at) }}
              </span>
              <span class="inline-flex items-center gap-1.5">
                <Dumbbell :size="14" aria-hidden="true" />
                {{ clientNextSession.trainer_name }}
              </span>
              <span class="inline-flex items-center gap-1.5">
                <MapPin :size="14" aria-hidden="true" />
                {{ clientNextSession.room_name }}
              </span>
            </div>
            <RouterLink
              :to="`/app/schedule/${clientNextSession.id}`"
              class="mt-4 inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold text-brand-700 hover:text-brand-800"
            >
              Открыть тренировку
              <ArrowRight :size="15" aria-hidden="true" />
            </RouterLink>
          </div>

          <EmptyState
            v-else
            class="mt-4"
            compact
            title="Записей пока нет"
            description="Выберите тренировку в расписании и запишитесь."
          >
            <template #actions>
              <RouterLink
                to="/app/schedule"
                class="inline-flex min-h-10 items-center rounded-control bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"
              >
                Открыть расписание
              </RouterLink>
            </template>
          </EmptyState>
        </section>
      </div>
    </template>

    <!-- TRAINER -->
    <template v-else-if="isTrainer">
      <div class="grid gap-4 sm:grid-cols-3">
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">Тренировок сегодня</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">
            {{ trainerLoading ? '—' : formatCount(trainerSessions.length) }}
          </p>
          <p class="mt-2 text-xs text-slate-400">по вашему расписанию</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">Записано клиентов</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">
            {{ trainerLoading ? '—' : formatCount(trainerEnrolled) }}
          </p>
          <p class="mt-2 text-xs text-slate-400">на сегодняшние занятия</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">Заполняемость</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">
            {{ trainerLoading ? '—' : formatPercent(trainerFillRate, 0) }}
          </p>
          <p class="mt-2 text-xs text-slate-400">мест занято</p>
        </article>
      </div>

      <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h3 class="text-lg font-semibold text-slate-900">Сегодняшние тренировки</h3>
            <p class="mt-1 text-sm text-slate-500">{{ formatDateLong(today) }}</p>
          </div>
          <RouterLink
            to="/app/schedule"
            class="inline-flex min-h-10 items-center gap-1.5 text-sm font-semibold text-brand-700 hover:text-brand-800"
          >
            Всё расписание
            <ArrowRight :size="15" aria-hidden="true" />
          </RouterLink>
        </div>

        <div v-if="trainerLoading" class="mt-4 space-y-3">
          <SkeletonBlock v-for="index in 3" :key="index" :lines="2" />
        </div>

        <EmptyState
          v-else-if="trainerSessions.length === 0"
          class="mt-4"
          compact
          title="На сегодня тренировок нет"
          description="Проверьте расписание на следующие дни или создайте новую тренировку."
        >
          <template #actions>
            <RouterLink
              to="/app/schedule"
              class="inline-flex min-h-10 items-center rounded-control bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"
            >
              Открыть расписание
            </RouterLink>
          </template>
        </EmptyState>

        <div v-else class="mt-4 space-y-2.5">
          <RouterLink
            v-for="session in trainerSessions"
            :key="session.id"
            :to="`/app/schedule/${session.id}`"
            class="group flex min-w-0 flex-col gap-3 rounded-2xl border border-slate-200 p-4 transition hover:border-brand-200 hover:bg-brand-50/40 sm:flex-row sm:items-center sm:justify-between"
          >
            <div class="flex min-w-0 items-start gap-3">
              <span
                class="shrink-0 rounded-xl bg-slate-50 px-3 py-2 text-center text-sm font-bold text-slate-800 ring-1 ring-slate-100"
              >
                {{ formatTimeRange(session.starts_at, session.ends_at) }}
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-900">{{ session.title }}</p>
                <p class="mt-1 text-xs text-slate-500">
                  {{ session.room_name }} · записано {{ session.enrolled_count }} из
                  {{ session.capacity }}
                </p>
              </div>
            </div>
            <ArrowRight
              :size="16"
              class="hidden shrink-0 text-slate-300 transition group-hover:text-brand-600 sm:block"
              aria-hidden="true"
            />
          </RouterLink>
        </div>
      </section>
    </template>

    <!-- ADMIN -->
    <template v-else-if="isAdmin">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="metric in adminMetrics"
          :key="metric.label"
          class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-slate-500">{{ metric.label }}</p>
              <p class="mt-2 text-2xl font-bold tracking-tight text-slate-900">
                {{ adminLoading && metric.value === '—' ? '…' : metric.value }}
              </p>
            </div>
            <span :class="['grid size-10 shrink-0 place-items-center rounded-2xl', metric.tone]">
              <component :is="metric.icon" :size="20" aria-hidden="true" />
            </span>
          </div>
          <p class="mt-3 text-xs text-slate-400">{{ metric.hint }}</p>
        </article>
      </div>

      <section class="rounded-card border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h3 class="text-lg font-semibold text-slate-900">Ближайшие тренировки</h3>
            <p class="mt-1 text-sm text-slate-500">Ближайшие 7 дней</p>
          </div>
          <RouterLink
            to="/app/reports"
            class="inline-flex min-h-10 items-center gap-1.5 text-sm font-semibold text-brand-700 hover:text-brand-800"
          >
            Открыть отчёты
            <ArrowRight :size="15" aria-hidden="true" />
          </RouterLink>
        </div>

        <div v-if="upcomingSessionsQuery.isPending.value" class="mt-4 space-y-3">
          <SkeletonBlock v-for="index in 3" :key="index" :lines="2" />
        </div>

        <EmptyState
          v-else-if="upcomingSessions.length === 0"
          class="mt-4"
          compact
          title="Ближайших тренировок нет"
          description="Создайте тренировки в расписании, чтобы они появились здесь."
        >
          <template #actions>
            <RouterLink
              to="/app/schedule"
              class="inline-flex min-h-10 items-center rounded-control bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"
            >
              Открыть расписание
            </RouterLink>
          </template>
        </EmptyState>

        <div v-else class="mt-4 space-y-2.5">
          <RouterLink
            v-for="session in upcomingSessions"
            :key="session.id"
            :to="`/app/schedule/${session.id}`"
            class="group flex min-w-0 flex-col gap-3 rounded-2xl border border-slate-200 p-4 transition hover:border-brand-200 hover:bg-brand-50/40 sm:flex-row sm:items-center sm:justify-between"
          >
            <div class="flex min-w-0 items-start gap-3">
              <span
                class="shrink-0 rounded-xl bg-slate-50 px-3 py-2 text-center text-xs font-bold text-slate-800 ring-1 ring-slate-100"
              >
                {{ formatDateShort(session.starts_at) }}
                <span class="mt-0.5 block font-medium text-slate-500">
                  {{ formatTimeRange(session.starts_at, session.ends_at) }}
                </span>
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-900">{{ session.title }}</p>
                <p class="mt-1 text-xs text-slate-500">
                  {{ session.trainer_name }} · {{ session.room_name }} · записано
                  {{ session.enrolled_count }} из {{ session.capacity }}
                </p>
              </div>
            </div>
            <ArrowRight
              :size="16"
              class="hidden shrink-0 text-slate-300 transition group-hover:text-brand-600 sm:block"
              aria-hidden="true"
            />
          </RouterLink>
        </div>
      </section>
    </template>

    <section class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div class="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h3 class="text-lg font-semibold text-slate-900">Быстрый доступ</h3>
          <p class="mt-1 text-sm text-slate-500">Разделы, доступные вашей роли</p>
        </div>
        <AppBadge tone="neutral">{{ visibleQuickLinks.length }}</AppBadge>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <RouterLink
          v-for="link in visibleQuickLinks"
          :key="link.to"
          :to="link.to"
          class="group flex min-h-24 items-start gap-3 rounded-2xl border border-slate-200 p-4 transition hover:border-brand-200 hover:bg-brand-50/40"
        >
          <span
            class="grid size-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-600 transition group-hover:bg-white group-hover:text-brand-700"
          >
            <component :is="link.icon" :size="19" aria-hidden="true" />
          </span>
          <span class="min-w-0 flex-1">
            <span class="flex items-center justify-between gap-2">
              <span class="text-sm font-semibold text-slate-900">{{ link.title }}</span>
              <ArrowRight
                :size="15"
                class="shrink-0 text-slate-300 transition group-hover:text-brand-600"
                aria-hidden="true"
              />
            </span>
            <span class="mt-1 block text-xs leading-5 text-slate-500">{{ link.text }}</span>
          </span>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
