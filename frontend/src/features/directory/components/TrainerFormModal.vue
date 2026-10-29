<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Save } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import type { TrainerRecord } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import { AppButton, AppInput, AppModal, AppTextarea } from '@/components/ui'
import { useToastStore } from '@/stores/toasts'
import { useUpdateTrainerMutation } from '../queries'
import { trainerEditSchema, type TrainerEditValues } from '../validation'

const props = withDefaults(
  defineProps<{
    trainer?: TrainerRecord | null
  }>(),
  {
    trainer: null,
  },
)

const emit = defineEmits<{
  saved: []
}>()

const open = defineModel<boolean>({ default: false })

const toast = useToastStore()
const updateMutation = useUpdateTrainerMutation()

const isSaving = computed(() => updateMutation.isPending.value)

function initialValues(): TrainerEditValues {
  return {
    full_name: props.trainer?.full_name ?? '',
    phone: props.trainer?.phone ?? '',
    specialization: props.trainer?.specialization ?? '',
    bio: props.trainer?.bio ?? '',
  }
}

const { handleSubmit, errors, defineField, isSubmitting, resetForm } = useForm({
  validationSchema: toTypedSchema(trainerEditSchema),
  initialValues: initialValues(),
})

const [fullName, fullNameAttrs] = defineField('full_name')
const [phone, phoneAttrs] = defineField('phone')
const [specialization, specializationAttrs] = defineField('specialization')
const [bio, bioAttrs] = defineField('bio')

const serverError = ref('')

watch(
  () => [open.value, props.trainer?.id] as const,
  ([isOpen]) => {
    if (isOpen) {
      resetForm({ values: initialValues() })
      serverError.value = ''
    }
  },
  { immediate: true },
)

const onSubmit = handleSubmit(async (values) => {
  if (!props.trainer) {
    return
  }

  serverError.value = ''

  try {
    await updateMutation.mutateAsync({
      id: props.trainer.id,
      payload: {
        full_name: values.full_name.trim(),
        phone: values.phone.trim() || null,
        specialization: values.specialization.trim() || null,
        bio: values.bio.trim() || null,
      },
    })
    toast.success('Профиль тренера обновлён.', 'Изменения сохранены')
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
    title="Изменить тренера"
    description="Имя, контакты и специализация. Email и роль меняются только при создании учётной записи."
    size="lg"
    :prevent-close="isSubmitting || isSaving"
  >
    <form id="trainer-form" class="space-y-4" novalidate @submit.prevent="onSubmit">
      <div
        v-if="serverError"
        class="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
        role="alert"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p class="leading-5">{{ serverError }}</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <AppInput
          v-model="fullName"
          v-bind="fullNameAttrs"
          label="Полное имя"
          required
          :error="errors.full_name"
        />
        <AppInput
          :model-value="trainer?.email ?? ''"
          label="Email"
          readonly
          hint="Email назначается при создании пользователя"
        />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <AppInput
          v-model="phone"
          v-bind="phoneAttrs"
          label="Телефон"
          type="tel"
          placeholder="+7 900 000-00-00"
          :error="errors.phone"
        />
        <AppInput
          v-model="specialization"
          v-bind="specializationAttrs"
          label="Специализация"
          placeholder="Функциональный тренинг, ОФП"
          :error="errors.specialization"
        />
      </div>

      <AppTextarea
        v-model="bio"
        v-bind="bioAttrs"
        label="О тренере"
        placeholder="Опыт, направления и особенности занятий"
        :rows="4"
        :error="errors.bio"
      />
    </form>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" :disabled="isSubmitting || isSaving" @click="open = false">
          Отмена
        </AppButton>
        <AppButton type="submit" form="trainer-form" :loading="isSubmitting || isSaving">
          <template #icon>
            <Save :size="16" aria-hidden="true" />
          </template>
          Сохранить изменения
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
