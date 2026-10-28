<script setup lang="ts">
import { TriangleAlert } from '@lucide/vue'

import AppButton from './AppButton.vue'
import AppModal from './AppModal.vue'

const open = defineModel<boolean>({ default: false })

withDefaults(
  defineProps<{
    title?: string
    message: string
    confirmLabel?: string
    cancelLabel?: string
    tone?: 'danger' | 'primary'
    loading?: boolean
    error?: string | null
  }>(),
  {
    title: 'Подтвердите действие',
    confirmLabel: 'Подтвердить',
    cancelLabel: 'Отмена',
    tone: 'danger',
    loading: false,
    error: null,
  },
)

const emit = defineEmits<{
  confirm: []
}>()
</script>

<template>
  <AppModal v-model="open" :title="title" size="sm" :prevent-close="loading">
    <div class="flex items-start gap-3">
      <span
        :class="[
          'grid size-11 shrink-0 place-items-center rounded-2xl',
          tone === 'danger' ? 'bg-rose-50 text-rose-700' : 'bg-brand-50 text-brand-700',
        ]"
        aria-hidden="true"
      >
        <TriangleAlert :size="21" />
      </span>
      <div class="min-w-0 pt-0.5">
        <p class="text-sm leading-6 text-slate-600">{{ message }}</p>
        <p
          v-if="error"
          class="mt-3 rounded-xl border border-rose-200 bg-rose-50 p-2.5 text-xs leading-5 text-rose-700"
          role="alert"
        >
          {{ error }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" :disabled="loading" @click="open = false">
          {{ cancelLabel }}
        </AppButton>
        <AppButton
          :variant="tone === 'danger' ? 'danger' : 'primary'"
          :loading="loading"
          @click="emit('confirm')"
        >
          {{ confirmLabel }}
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
