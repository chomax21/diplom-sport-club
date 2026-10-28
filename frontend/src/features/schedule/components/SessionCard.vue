<script setup lang="ts">
import { ArrowRight, Clock3, MapPin, Users, Dumbbell } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import type { Enrollment, TrainingSession } from '@/api/schedule'
import { AppBadge, StatusBadge } from '@/components/ui'
import { formatDuration, formatTimeRange } from '@/lib/datetime'

import { getSessionAvailability, SESSION_AVAILABILITY_META } from '../status'

const props = defineProps<{
  session: TrainingSession
  enrollment?: Enrollment | null
}>()

const availability = computed(() => getSessionAvailability(props.session))
const availabilityMeta = computed(() => SESSION_AVAILABILITY_META[availability.value])
const progress = computed(() => {
  if (props.session.capacity <= 0) {
    return 0
  }
  return Math.min(100, Math.round((props.session.enrolled_count / props.session.capacity) * 100))
})

const cardClass = computed(() =>
  props.session.is_cancelled
    ? 'border-rose-200 bg-rose-50/40'
    : 'border-slate-200 bg-white hover:border-brand-200',
)
</script>

<template>
  <RouterLink
    :to="`/app/schedule/${session.id}`"
    :class="[
      'group flex min-w-0 flex-col rounded-card border p-4 shadow-sm transition hover:shadow-card focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 sm:p-5',
      cardClass,
    ]"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="flex flex-wrap items-center gap-1.5">
          <AppBadge :tone="availabilityMeta.tone" dot>{{ availabilityMeta.label }}</AppBadge>
          <StatusBadge v-if="enrollment" kind="enrollment" :status="enrollment.status" />
        </div>
        <h3
          :class="[
            'mt-2 break-words text-base font-semibold leading-6',
            session.is_cancelled ? 'text-slate-500 line-through' : 'text-slate-900',
          ]"
        >
          {{ session.title }}
        </h3>
      </div>

      <span
        class="shrink-0 rounded-xl bg-slate-50 px-3 py-2 text-center text-sm font-bold text-slate-800 ring-1 ring-slate-100"
      >
        {{ formatTimeRange(session.starts_at, session.ends_at) }}
      </span>
    </div>

    <div class="mt-3 flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-slate-500">
      <span class="inline-flex min-w-0 items-center gap-1.5">
        <Dumbbell :size="14" class="shrink-0" aria-hidden="true" />
        <span class="truncate">{{ session.trainer_name }}</span>
      </span>
      <span class="inline-flex min-w-0 items-center gap-1.5">
        <MapPin :size="14" class="shrink-0" aria-hidden="true" />
        <span class="truncate">{{ session.room_name }}</span>
      </span>
      <span class="inline-flex items-center gap-1.5">
        <Clock3 :size="14" class="shrink-0" aria-hidden="true" />
        {{ formatDuration(session.starts_at, session.ends_at) }}
      </span>
    </div>

    <div class="mt-auto pt-4">
      <div class="flex items-center justify-between gap-3 text-xs">
        <span class="inline-flex items-center gap-1.5 text-slate-500">
          <Users :size="14" aria-hidden="true" />
          Записано {{ session.enrolled_count }} из {{ session.capacity }}
        </span>
        <span
          :class="[
            'font-semibold',
            session.available_slots > 0 && !session.is_cancelled
              ? 'text-emerald-700'
              : 'text-amber-700',
          ]"
        >
          {{
            session.is_cancelled
              ? 'Отменена'
              : session.available_slots > 0
                ? `Свободно ${session.available_slots}`
                : 'Мест нет'
          }}
        </span>
      </div>

      <div
        class="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100"
        role="progressbar"
        :aria-valuenow="session.enrolled_count"
        aria-valuemin="0"
        :aria-valuemax="session.capacity"
        :aria-label="`Заполненность: ${session.enrolled_count} из ${session.capacity}`"
      >
        <div
          :class="[
            'h-full rounded-full transition-all',
            session.is_cancelled
              ? 'bg-rose-300'
              : session.available_slots > 0
                ? 'bg-brand-500'
                : 'bg-amber-500',
          ]"
          :style="{ width: `${progress}%` }"
        />
      </div>

      <div class="mt-3 flex items-center justify-end gap-1 text-sm font-semibold text-brand-700">
        Подробнее
        <ArrowRight :size="15" class="transition group-hover:translate-x-0.5" aria-hidden="true" />
      </div>
    </div>
  </RouterLink>
</template>
