<script setup lang="ts">
import { CalendarDays, Ticket } from '@lucide/vue'
import { computed } from 'vue'

import type { MembershipType } from '@/api/memberships'
import { AppBadge } from '@/components/ui'
import { formatMoney } from '@/lib/format'

import { durationDaysLabel, visitsLeftLabel } from '../status'

const props = withDefaults(
  defineProps<{
    type: MembershipType
    showStatus?: boolean
  }>(),
  {
    showStatus: false,
  },
)

const visitsLabel = computed(() => visitsLeftLabel(props.type.visits_limit))
</script>

<template>
  <article
    class="flex min-w-0 flex-col rounded-card border border-slate-200 bg-white p-5 shadow-sm"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="flex flex-wrap items-center gap-1.5">
          <AppBadge tone="brand">{{ visitsLabel }}</AppBadge>
          <AppBadge v-if="showStatus && !type.is_active" tone="neutral" dot>Отключён</AppBadge>
          <AppBadge v-else-if="showStatus" tone="success" dot>Доступен</AppBadge>
        </div>
        <h3 class="mt-2 break-words text-base font-semibold leading-6 text-slate-900">
          {{ type.name }}
        </h3>
      </div>

      <span
        class="grid size-10 shrink-0 place-items-center rounded-2xl bg-brand-50 text-brand-700"
        aria-hidden="true"
      >
        <Ticket :size="19" />
      </span>
    </div>

    <p class="mt-2 text-sm leading-6 text-slate-600">
      {{ type.description || 'Описание не добавлено.' }}
    </p>

    <div class="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
      <span class="inline-flex items-center gap-1.5">
        <CalendarDays :size="14" aria-hidden="true" />
        {{ durationDaysLabel(type.duration_days) }}
      </span>
      <span class="font-semibold text-slate-700">{{ visitsLabel }}</span>
    </div>

    <div class="mt-auto flex items-end justify-between gap-3 pt-5">
      <p class="text-2xl font-bold tracking-tight text-slate-900">
        {{ formatMoney(type.price) }}
      </p>
      <slot name="actions" />
    </div>
  </article>
</template>
