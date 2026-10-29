<script setup lang="ts">
import { CalendarDays, Mail, Pencil, Phone } from '@lucide/vue'

import type { TrainerRecord } from '@/api/directory'
import { AppAvatar, AppBadge, AppButton } from '@/components/ui'
import { formatDateShort } from '@/lib/datetime'

defineProps<{
  trainer: TrainerRecord
}>()

const emit = defineEmits<{
  edit: []
}>()
</script>

<template>
  <article
    class="flex min-w-0 flex-col rounded-card border border-slate-200 bg-white p-5 shadow-sm"
  >
    <div class="flex items-start gap-3">
      <AppAvatar :name="trainer.full_name" size="lg" />
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-1.5">
          <AppBadge :tone="trainer.is_active ? 'success' : 'neutral'" dot>
            {{ trainer.is_active ? 'Активен' : 'Заблокирован' }}
          </AppBadge>
        </div>
        <h3 class="mt-1.5 break-words text-base font-semibold text-slate-900">
          {{ trainer.full_name }}
        </h3>
        <p class="mt-0.5 line-clamp-2 text-xs leading-5 text-slate-500">
          {{ trainer.specialization || 'Специализация не указана' }}
        </p>
      </div>
    </div>

    <dl class="mt-4 space-y-2 text-xs text-slate-500">
      <div class="flex min-w-0 items-center gap-2">
        <dt class="shrink-0"><Mail :size="14" aria-hidden="true" /></dt>
        <dd class="min-w-0 truncate text-slate-700">{{ trainer.email }}</dd>
      </div>
      <div class="flex min-w-0 items-center gap-2">
        <dt class="shrink-0"><Phone :size="14" aria-hidden="true" /></dt>
        <dd class="min-w-0 truncate text-slate-700">{{ trainer.phone || 'Телефон не указан' }}</dd>
      </div>
      <div class="flex min-w-0 items-center gap-2">
        <dt class="shrink-0"><CalendarDays :size="14" aria-hidden="true" /></dt>
        <dd class="min-w-0 truncate text-slate-700">
          В клубе с {{ formatDateShort(trainer.created_at) }}
        </dd>
      </div>
    </dl>

    <p class="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">
      {{ trainer.bio || 'Описание профиля не заполнено.' }}
    </p>

    <div class="mt-auto flex justify-end pt-5">
      <AppButton variant="outline" size="sm" @click="emit('edit')">
        <template #icon>
          <Pencil :size="14" aria-hidden="true" />
        </template>
        Изменить
      </AppButton>
    </div>
  </article>
</template>
