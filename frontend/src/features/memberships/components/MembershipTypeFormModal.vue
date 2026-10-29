<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Save } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import type { MembershipType, MembershipTypePayload } from '@/api/memberships'
import { AppButton, AppInput, AppModal, AppSwitch, AppTextarea } from '@/components/ui'
import { membershipTypeSchema, type MembershipTypeFormValues } from '../validation'
import { useCreateMembershipTypeMutation, useUpdateMembershipTypeMutation } from '../queries'
import { useToastStore } from '@/stores/toasts'

const props = withDefaults(
  defineProps<{
    type?: MembershipType | null
  }>(),
  {
    type: null,
  },
)

const emit = defineEmits<{
  saved: []
}>()

const open = defineModel<boolean>({ default: false })

const toast = useToastStore()
const createMutation = useCreateMembershipTypeMutation()
const updateMutation = useUpdateMembershipTypeMutation()

const isEditing = computed(() => Boolean(props.type))
const isSaving = computed(() => createMutation.isPending.value || updateMutation.isPending.value)
const modalTitle = computed(() =>
  isEditing.value ? 'Изменить вид абонемента' : 'Новый вид абонемента',
)

function initialValues(): MembershipTypeFormValues {
  return {
    name: props.type?.name ?? '',
    description: props.type?.description ?? '',
    price: props.type?.price ?? '',
    duration_days: props.type ? String(props.type.duration_days) : '30',
    visits_limit:
      props.type && props.type.visits_limit !== null ? String(props.type.visits_limit) : '',
    is_active: props.type?.is_active ?? true,
  }
}

const { handleSubmit, errors, defineField, isSubmitting, resetForm } = useForm({
  validationSchema: toTypedSchema(membershipTypeSchema),
  initialValues: initialValues(),
})

const [name, nameAttrs] = defineField('name')
const [description, descriptionAttrs] = defineField('description')
const [price, priceAttrs] = defineField('price')
const [durationDays, durationDaysAttrs] = defineField('duration_days')
const [visitsLimit, visitsLimitAttrs] = defineField('visits_limit')
const [isActive, isActiveAttrs] = defineField('is_active')

const serverError = ref('')

watch(
  () => [open.value, props.type] as const,
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

  const payload: MembershipTypePayload = {
    name: values.name.trim(),
    description: values.description.trim() || null,
    price: Number(values.price.replace(',', '.')),
    duration_days: Number(values.duration_days),
    visits_limit: values.visits_limit.trim() ? Number(values.visits_limit) : null,
    is_active: values.is_active,
  }

  try {
    if (props.type) {
      await updateMutation.mutateAsync({ id: props.type.id, payload })
      toast.success('Вид абонемента обновлён.', 'Изменения сохранены')
    } else {
      await createMutation.mutateAsync(payload)
      toast.success('Новый вид абонемента добавлен в каталог.', 'Вид абонемента создан')
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
    description="Стоимость указывается в рублях. Пустое поле «Лимит посещений» означает безлимитный абонемент."
    size="lg"
    :prevent-close="isSubmitting || isSaving"
  >
    <form id="membership-type-form" class="space-y-4" novalidate @submit.prevent="onSubmit">
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
        placeholder="Например, месяц безлимита"
        required
        :error="errors.name"
      />

      <AppTextarea
        v-model="description"
        v-bind="descriptionAttrs"
        label="Описание"
        placeholder="Что входит в абонемент и для кого он подходит"
        :rows="3"
        :error="errors.description"
      />

      <div class="grid gap-4 sm:grid-cols-2">
        <AppInput
          v-model="price"
          v-bind="priceAttrs"
          label="Стоимость, ₽"
          type="text"
          inputmode="decimal"
          placeholder="4500"
          required
          :error="errors.price"
        />
        <AppInput
          v-model="durationDays"
          v-bind="durationDaysAttrs"
          label="Срок действия, дней"
          type="text"
          inputmode="numeric"
          placeholder="30"
          required
          :error="errors.duration_days"
        />
      </div>

      <div class="grid gap-4 sm:grid-cols-2 sm:items-start">
        <AppInput
          v-model="visitsLimit"
          v-bind="visitsLimitAttrs"
          label="Лимит посещений"
          type="text"
          inputmode="numeric"
          placeholder="Оставьте пустым для безлимита"
          :error="errors.visits_limit"
        />
        <AppSwitch
          v-model="isActive"
          v-bind="isActiveAttrs"
          label="Доступен для продажи"
          description="Отключённый вид скрыт из каталога клиентов"
        />
      </div>
    </form>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" :disabled="isSubmitting || isSaving" @click="open = false">
          Отмена
        </AppButton>
        <AppButton type="submit" form="membership-type-form" :loading="isSubmitting || isSaving">
          <template #icon>
            <Save :size="16" aria-hidden="true" />
          </template>
          {{ isEditing ? 'Сохранить изменения' : 'Создать вид' }}
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
