<script setup lang="ts">
import { computed } from 'vue'

import AppBadge from './AppBadge.vue'
import type { BadgeTone } from './types'

type StatusKind = 'membership' | 'enrollment' | 'payment' | 'role'

interface StatusMeta {
  label: string
  tone: BadgeTone
}

const props = defineProps<{
  kind: StatusKind
  status: string
}>()

const statuses: Record<StatusKind, Record<string, StatusMeta>> = {
  membership: {
    pending: { label: 'Ожидает', tone: 'warning' },
    active: { label: 'Активен', tone: 'success' },
    expired: { label: 'Истёк', tone: 'neutral' },
    cancelled: { label: 'Отменён', tone: 'danger' },
  },
  enrollment: {
    active: { label: 'Записан', tone: 'success' },
    cancelled: { label: 'Отменена', tone: 'neutral' },
    attended: { label: 'Посещение', tone: 'info' },
    no_show: { label: 'Неявка', tone: 'danger' },
  },
  payment: {
    pending: { label: 'Ожидает', tone: 'warning' },
    succeeded: { label: 'Успешно', tone: 'success' },
    failed: { label: 'Ошибка', tone: 'danger' },
    refunded: { label: 'Возврат', tone: 'violet' },
  },
  role: {
    admin: { label: 'Администратор', tone: 'violet' },
    trainer: { label: 'Тренер', tone: 'info' },
    client: { label: 'Клиент', tone: 'brand' },
  },
}

const meta = computed<StatusMeta>(
  () => statuses[props.kind][props.status] ?? { label: props.status, tone: 'neutral' },
)
</script>

<template>
  <AppBadge :tone="meta.tone" dot>{{ meta.label }}</AppBadge>
</template>
