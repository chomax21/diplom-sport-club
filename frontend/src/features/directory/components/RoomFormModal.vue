<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Save } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import type { RoomRecord } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import { AppButton, AppInput, AppModal, AppSwitch, AppTextarea } from '@/components/ui'
import { useToastStore } from '@/stores/toasts'
import { useCreateRoomMutation, useUpdateRoomMutation } from '../queries'
import { roomFormSchema, type RoomFormValues } from '../validation'

const props = withDefaults(
  defineProps<{
    room?: RoomRecord | null
  }>(),
  {
    room: null,
  },
)

const emit = defineEmits<{
  saved: []
}>()

const open = defineModel<boolean>({ default: false })

const toast = useToastStore()
const createMutation = useCreateRoomMutation()
const updateMutation = useUpdateRoomMutation()

const isEditing = computed(() => Boolean(props.room))
const isSaving = computed(() => createMutation.isPending.value || updateMutation.isPending.value)

function initialValues(): RoomFormValues {
  return {
    name: props.room?.name ?? '',
    capacity: props.room ? String(props.room.capacity) : '12',
    description: props.room?.description ?? '',
    is_active: props.room?.is_active ?? true,
  }
}

const { handleSubmit, errors, defineField, isSubmitting, resetForm } = useForm({
  validationSchema: toTypedSchema(roomFormSchema),
  initialValues: initialValues(),
})

const [name, nameAttrs] = defineField('name')
const [capacity, capacityAttrs] = defineField('capacity')
const [description, descriptionAttrs] = defineField('description')
const [isActive, isActiveAttrs] = defineField('is_active')

const serverError = ref('')

watch(
  () => [open.value, props.room?.id] as const,
  ([isOpen]) => {
    if (isOpen) {
      resetForm({ values: initialValues() })
      serverError.value = ''
    }
  },
  { immediate: true },
)

const onSubmit = handleSubmit(async (values) => {
  serverError.value = ''

  const payload = {
    name: values.name.trim(),
    capacity: Number(values.capacity),
    description: values.description.trim() || null,
    is_active: values.is_active,
  }

  try {
    if (props.room) {
      await updateMutation.mutateAsync({ id: props.room.id, payload })
      toast.success('Информация о зале обновлена.', 'Изменения сохранены')
    } else {
      await createMutation.mutateAsync(payload)
      toast.success('Новый зал добавлен в справочник.', 'Зал создан')
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
    :title="isEditing ? 'Изменить зал' : 'Новый зал'"
    description="Название, вместимость и доступность зала для расписания."
    size="md"
    :prevent-close="isSubmitting || isSaving"
  >
    <form id="room-form" class="space-y-4" novalidate @submit.prevent="onSubmit">
      <div
        v-if="serverError"
        class="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
        role="alert"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p class="leading-5">{{ serverError }}</p>
      </div>

      <AppInput
        v-model="name"
        v-bind="nameAttrs"
        label="Название"
        placeholder="Например, зал единоборств"
        required
        :error="errors.name"
      />

      <AppInput
        v-model="capacity"
        v-bind="capacityAttrs"
        label="Вместимость"
        type="text"
        inputmode="numeric"
        placeholder="12"
        required
        :error="errors.capacity"
      />

      <AppTextarea
        v-model="description"
        v-bind="descriptionAttrs"
        label="Описание"
        placeholder="Оборудование и особенности помещения"
        :rows="3"
        :error="errors.description"
      />

      <AppSwitch
        v-model="isActive"
        v-bind="isActiveAttrs"
        label="Доступен для расписания"
        description="Отключённый зал скрывается из выбора при создании тренировки"
      />
    </form>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" :disabled="isSubmitting || isSaving" @click="open = false">
          Отмена
        </AppButton>
        <AppButton type="submit" form="room-form" :loading="isSubmitting || isSaving">
          <template #icon>
            <Save :size="16" aria-hidden="true" />
          </template>
          {{ isEditing ? 'Сохранить изменения' : 'Создать зал' }}
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
