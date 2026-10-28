<script setup lang="ts">
import { CircleAlert, UserPlus } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import type { TrainingSession } from '@/api/schedule'
import { getApiErrorMessage } from '@/api/errors'
import { AppButton, AppModal, AppSelect, SearchInput } from '@/components/ui'
import { useClientsQuery, useEnrollMutation } from '@/features/schedule/queries'
import { useToastStore } from '@/stores/toasts'

const props = defineProps<{
  session: TrainingSession
}>()

const emit = defineEmits<{
  enrolled: []
}>()

const open = defineModel<boolean>({ default: false })

const toast = useToastStore()
const search = ref('')
const clientId = ref<string | number>('')
const serverError = ref('')

const clientsQuery = useClientsQuery(open)
const enrollMutation = useEnrollMutation()

const clientOptions = computed(() => {
  const term = search.value.trim().toLowerCase()

  return (clientsQuery.data.value?.items ?? [])
    .filter((client) => client.is_active)
    .filter(
      (client) =>
        !term ||
        client.full_name.toLowerCase().includes(term) ||
        client.email.toLowerCase().includes(term) ||
        (client.phone?.toLowerCase().includes(term) ?? false),
    )
    .map((client) => ({
      label: `${client.full_name} · ${client.email}`,
      value: client.id,
    }))
})

watch(open, (isOpen) => {
  if (isOpen) {
    search.value = ''
    clientId.value = ''
    serverError.value = ''
  }
})

async function submit(): Promise<void> {
  serverError.value = ''

  if (!clientId.value) {
    serverError.value = 'Выберите клиента.'
    return
  }

  try {
    const enrollment = await enrollMutation.mutateAsync({
      sessionId: props.session.id,
      clientId: String(clientId.value),
    })

    toast.success(`Клиент записан: ${enrollment.client_name}.`, 'Запись создана')
    open.value = false
    emit('enrolled')
  } catch (error) {
    serverError.value = getApiErrorMessage(error)
  }
}
</script>

<template>
  <AppModal
    v-model="open"
    title="Записать клиента"
    description="Для записи у клиента должен быть действующий абонемент на дату тренировки."
    size="md"
    :prevent-close="enrollMutation.isPending.value"
  >
    <div class="space-y-4">
      <div
        v-if="serverError"
        class="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
        role="alert"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p class="leading-5">{{ serverError }}</p>
      </div>

      <SearchInput
        v-model="search"
        aria-label="Поиск клиента"
        placeholder="Имя, email или телефон…"
      />

      <AppSelect
        v-model="clientId"
        label="Клиент"
        placeholder="Выберите клиента"
        :options="clientOptions"
        :disabled="clientsQuery.isPending.value"
        :hint="
          clientsQuery.isPending.value
            ? 'Загружаем клиентов…'
            : `Доступно клиентов: ${clientOptions.length}`
        "
      />

      <div class="rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-500">
        Свободных мест: {{ session.available_slots }} из {{ session.capacity }}. Если мест нет,
        сервер вернёт конфликт 409.
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton
          variant="outline"
          :disabled="enrollMutation.isPending.value"
          @click="open = false"
        >
          Отмена
        </AppButton>
        <AppButton :loading="enrollMutation.isPending.value" :disabled="!clientId" @click="submit">
          <template #icon>
            <UserPlus :size="16" aria-hidden="true" />
          </template>
          Записать
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
