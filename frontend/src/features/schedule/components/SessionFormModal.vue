<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Save } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import type { TrainingSession, TrainingSessionPayload } from '@/api/schedule'
import { AppButton, AppInput, AppModal, AppSelect, AppTextarea, DatePicker } from '@/components/ui'
import { createSessionSchema, type SessionFormValues } from '@/features/schedule/validation'
import {
  useCreateSessionMutation,
  useMyTrainerQuery,
  useRoomsQuery,
  useTrainersQuery,
  useUpdateSessionMutation,
} from '@/features/schedule/queries'
import { getApiErrorMessage } from '@/api/errors'
import { addDaysDateInput, dateInputValue, timeInputValue, toIsoFromDateTime } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const props = withDefaults(
  defineProps<{
    session?: TrainingSession | null
    defaultDate?: string
  }>(),
  {
    session: null,
    defaultDate: undefined,
  },
)

const emit = defineEmits<{
  saved: []
}>()

const open = defineModel<boolean>({ default: false })

const auth = useAuthStore()
const toast = useToastStore()

const isAdmin = computed(() => auth.role === 'admin')
const isTrainer = computed(() => auth.role === 'trainer')

const roomsQuery = useRoomsQuery(open)
const trainersQuery = useTrainersQuery(computed(() => open.value && isAdmin.value))
const myTrainerQuery = useMyTrainerQuery(computed(() => isTrainer.value))

const createMutation = useCreateSessionMutation()
const updateMutation = useUpdateSessionMutation()

const isSaving = computed(() => createMutation.isPending.value || updateMutation.isPending.value)
const modalTitle = computed(() => (props.session ? 'Редактировать тренировку' : 'Новая тренировка'))

const roomOptions = computed(() =>
  (roomsQuery.data.value?.items ?? []).map((room) => ({
    label: `${room.name} · до ${room.capacity} мест`,
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

const schema = toTypedSchema(
  createSessionSchema({
    requireTrainer: isAdmin,
    rooms: computed(() => roomsQuery.data.value?.items ?? []),
  }),
)

function initialValues(): SessionFormValues {
  if (props.session) {
    return {
      title: props.session.title,
      room_id: props.session.room_id,
      trainer_id: props.session.trainer_id,
      date: dateInputValue(props.session.starts_at),
      start_time: timeInputValue(props.session.starts_at),
      end_time: timeInputValue(props.session.ends_at),
      capacity: String(props.session.capacity),
      description: props.session.description ?? '',
    }
  }

  return {
    title: '',
    room_id: '',
    trainer_id: '',
    date: props.defaultDate ?? addDaysDateInput(1),
    start_time: '18:00',
    end_time: '19:00',
    capacity: '12',
    description: '',
  }
}

const { handleSubmit, errors, defineField, isSubmitting, resetForm, setFieldValue } = useForm({
  validationSchema: schema,
  initialValues: initialValues(),
})

const [title, titleAttrs] = defineField('title')
const [roomId, roomIdAttrs] = defineField('room_id')
const [trainerId, trainerIdAttrs] = defineField('trainer_id')
const [date, dateAttrs] = defineField('date')
const [startTime, startTimeAttrs] = defineField('start_time')
const [endTime, endTimeAttrs] = defineField('end_time')
const [capacity, capacityAttrs] = defineField('capacity')
const [description, descriptionAttrs] = defineField('description')

const serverError = ref('')

const selectedRoom = computed(() =>
  roomsQuery.data.value?.items.find((room) => room.id === roomId.value),
)

watch(
  () => [open.value, props.session] as const,
  ([isOpen]) => {
    if (isOpen) {
      resetForm({ values: initialValues() })
      serverError.value = ''
    }
  },
  { immediate: true },
)

watch(roomId, () => {
  const room = selectedRoom.value
  if (!room) {
    return
  }

  const current = Number(capacity.value)
  if (!Number.isFinite(current) || current <= 0 || current > room.capacity) {
    setFieldValue('capacity', String(room.capacity))
  }
})

const onSubmit = handleSubmit(async (values) => {
  serverError.value = ''

  try {
    const payload: TrainingSessionPayload = {
      title: values.title.trim(),
      room_id: values.room_id,
      starts_at: toIsoFromDateTime(values.date, values.start_time),
      ends_at: toIsoFromDateTime(values.date, values.end_time),
      capacity: Number(values.capacity),
      description: values.description.trim() || null,
    }

    if (isAdmin.value) {
      payload.trainer_id = values.trainer_id || null
    }

    if (props.session) {
      await updateMutation.mutateAsync({ id: props.session.id, payload })
      toast.success('Изменения тренировки сохранены.', 'Тренировка обновлена')
    } else {
      await createMutation.mutateAsync(payload)
      toast.success('Тренировка добавлена в расписание.', 'Тренировка создана')
    }

    open.value = false
    emit('saved')
  } catch (error) {
    serverError.value = getApiErrorMessage(error)
  }
})
</script>

<template>
  <AppModal
    v-model="open"
    :title="modalTitle"
    description="Время указывается в вашем часовом поясе. Проверка занятости зала и тренера выполняется на сервере."
    size="lg"
    :prevent-close="isSubmitting || isSaving"
  >
    <form id="session-form" class="space-y-4" novalidate @submit.prevent="onSubmit">
      <div
        v-if="serverError"
        class="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
        role="alert"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p class="leading-5">{{ serverError }}</p>
      </div>

      <AppInput
        v-model="title"
        v-bind="titleAttrs"
        label="Название тренировки"
        placeholder="Например, функциональный тренинг"
        required
        :error="errors.title"
      />

      <div class="grid gap-4 sm:grid-cols-2">
        <AppSelect
          v-model="roomId"
          v-bind="roomIdAttrs"
          label="Зал"
          placeholder="Выберите зал"
          :options="roomOptions"
          required
          :error="errors.room_id"
          :hint="selectedRoom ? `Вместимость зала: ${selectedRoom.capacity}` : undefined"
          :disabled="roomsQuery.isPending.value"
        />

        <template v-if="isAdmin">
          <AppSelect
            v-model="trainerId"
            v-bind="trainerIdAttrs"
            label="Тренер"
            placeholder="Выберите тренера"
            :options="trainerOptions"
            required
            :error="errors.trainer_id"
            :disabled="trainersQuery.isPending.value"
          />
        </template>
        <AppInput
          v-else
          :model-value="myTrainerQuery.data.value?.full_name ?? 'Ваш профиль тренера'"
          label="Тренер"
          readonly
          hint="Тренер назначается автоматически"
        />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <DatePicker v-model="date" v-bind="dateAttrs" label="Дата" required :error="errors.date" />
        <AppInput
          v-model="capacity"
          v-bind="capacityAttrs"
          label="Вместимость"
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          required
          :error="errors.capacity"
          :hint="selectedRoom ? `Не больше ${selectedRoom.capacity}` : undefined"
        />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <AppInput
          v-model="startTime"
          v-bind="startTimeAttrs"
          label="Начало"
          type="time"
          required
          :error="errors.start_time"
        />
        <AppInput
          v-model="endTime"
          v-bind="endTimeAttrs"
          label="Окончание"
          type="time"
          required
          :error="errors.end_time"
        />
      </div>

      <AppTextarea
        v-model="description"
        v-bind="descriptionAttrs"
        label="Описание"
        placeholder="Что взять с собой, уровень подготовки и другие детали"
        :rows="3"
        :error="errors.description"
      />
    </form>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" :disabled="isSubmitting || isSaving" @click="open = false">
          Отмена
        </AppButton>
        <AppButton type="submit" form="session-form" :loading="isSubmitting || isSaving">
          <template #icon>
            <Save :size="16" aria-hidden="true" />
          </template>
          {{ session ? 'Сохранить изменения' : 'Создать тренировку' }}
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
