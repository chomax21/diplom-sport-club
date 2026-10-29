<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CalendarDays, CircleAlert, FileText, Mail, Pencil, Phone, Save } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppInput,
  AppModal,
  AppTextarea,
  DatePicker,
  ErrorState,
  LoadingState,
} from '@/components/ui'
import { formatDateShort, formatDateTime } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'
import { useClientQuery, useUpdateClientMutation } from '../queries'
import { clientEditSchema, type ClientEditValues } from '../validation'

const props = withDefaults(
  defineProps<{
    clientId?: string | null
  }>(),
  {
    clientId: null,
  },
)

const emit = defineEmits<{
  saved: []
}>()

const open = defineModel<boolean>({ default: false })

const auth = useAuthStore()
const toast = useToastStore()

const clientQuery = useClientQuery(
  computed(() => props.clientId),
  computed(() => open.value && Boolean(props.clientId)),
)
const updateMutation = useUpdateClientMutation()

const client = computed(() => clientQuery.data.value)
const isAdmin = computed(() => auth.role === 'admin')

const editing = ref(false)
const serverError = ref('')

function initialValues(): ClientEditValues {
  return {
    full_name: client.value?.full_name ?? '',
    phone: client.value?.phone ?? '',
    birth_date: client.value?.birth_date ?? null,
    emergency_contact: client.value?.emergency_contact ?? '',
    notes: client.value?.notes ?? '',
  }
}

const { handleSubmit, errors, defineField, isSubmitting, resetForm } = useForm({
  validationSchema: toTypedSchema(clientEditSchema),
  initialValues: initialValues(),
})

const [fullName, fullNameAttrs] = defineField('full_name')
const [phone, phoneAttrs] = defineField('phone')
const [birthDate, birthDateAttrs] = defineField('birth_date')
const [emergencyContact, emergencyContactAttrs] = defineField('emergency_contact')
const [notes, notesAttrs] = defineField('notes')

watch(
  () => [open.value, client.value?.id] as const,
  ([isOpen]) => {
    if (isOpen) {
      editing.value = false
      serverError.value = ''
      resetForm({ values: initialValues() })
    }
  },
  { immediate: true },
)

function startEditing(): void {
  editing.value = true
  serverError.value = ''
  resetForm({ values: initialValues() })
}

function cancelEditing(): void {
  editing.value = false
  serverError.value = ''
  resetForm({ values: initialValues() })
}

const onSubmit = handleSubmit(async (values) => {
  if (!client.value) {
    return
  }

  serverError.value = ''

  try {
    await updateMutation.mutateAsync({
      id: client.value.id,
      payload: {
        full_name: values.full_name.trim(),
        phone: values.phone.trim() || null,
        birth_date: values.birth_date,
        emergency_contact: values.emergency_contact.trim() || null,
        notes: values.notes.trim() || null,
      },
    })
    editing.value = false
    toast.success('Карточка клиента обновлена.', 'Изменения сохранены')
    emit('saved')
  } catch (error) {
    serverError.value = getApiErrorMessage(error)
  }
})
</script>

<template>
  <AppModal
    v-model="open"
    title="Карточка клиента"
    description="Контактные данные и заметки администратора."
    size="lg"
    :prevent-close="isSubmitting"
  >
    <LoadingState v-if="clientQuery.isPending.value" label="Загружаем карточку клиента…" />

    <ErrorState
      v-else-if="clientQuery.isError.value"
      title="Не удалось загрузить клиента"
      :description="getApiErrorMessage(clientQuery.error.value)"
      @retry="clientQuery.refetch()"
    />

    <template v-else-if="client">
      <div v-if="!editing" class="space-y-5">
        <section
          class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center"
        >
          <AppAvatar :name="client.full_name" size="lg" />
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-1.5">
              <AppBadge tone="brand">Клиент</AppBadge>
              <AppBadge :tone="client.is_active ? 'success' : 'neutral'" dot>
                {{ client.is_active ? 'Активен' : 'Заблокирован' }}
              </AppBadge>
            </div>
            <h3 class="mt-1.5 break-words text-xl font-bold text-slate-900">
              {{ client.full_name }}
            </h3>
            <p class="mt-0.5 break-all text-sm text-slate-500">{{ client.email }}</p>
          </div>
        </section>

        <dl class="grid gap-3 sm:grid-cols-2">
          <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <Mail :size="14" aria-hidden="true" />
              Email
            </dt>
            <dd class="mt-1 break-all text-sm font-medium text-slate-900">{{ client.email }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <Phone :size="14" aria-hidden="true" />
              Телефон
            </dt>
            <dd class="mt-1 text-sm font-medium text-slate-900">{{ client.phone || '—' }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <CalendarDays :size="14" aria-hidden="true" />
              Дата рождения
            </dt>
            <dd class="mt-1 text-sm font-medium text-slate-900">
              {{ client.birth_date ? formatDateShort(client.birth_date) : '—' }}
            </dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
            <dt class="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <Phone :size="14" aria-hidden="true" />
              Экстренный контакт
            </dt>
            <dd class="mt-1 break-words text-sm font-medium text-slate-900">
              {{ client.emergency_contact || '—' }}
            </dd>
          </div>
        </dl>

        <section class="rounded-2xl border border-slate-200 bg-white p-4">
          <h3 class="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <FileText :size="15" aria-hidden="true" />
            Заметки
          </h3>
          <p class="mt-2 whitespace-pre-line text-sm leading-6 text-slate-600">
            {{ client.notes || 'Заметок пока нет.' }}
          </p>
        </section>

        <p class="text-xs text-slate-400">
          Профиль создан {{ formatDateTime(client.created_at) }} · ID {{ client.id }}
        </p>
      </div>

      <form v-else id="client-form" class="space-y-4" novalidate @submit.prevent="onSubmit">
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
            v-model="phone"
            v-bind="phoneAttrs"
            label="Телефон"
            type="tel"
            placeholder="+7 900 000-00-00"
            :error="errors.phone"
          />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <DatePicker
            v-model="birthDate"
            v-bind="birthDateAttrs"
            label="Дата рождения"
            :error="errors.birth_date"
          />
          <AppInput
            v-model="emergencyContact"
            v-bind="emergencyContactAttrs"
            label="Экстренный контакт"
            placeholder="Имя и телефон"
            :error="errors.emergency_contact"
          />
        </div>

        <AppTextarea
          v-model="notes"
          v-bind="notesAttrs"
          label="Заметки"
          placeholder="Особенности здоровья, предпочтения и другая информация"
          :rows="4"
          :error="errors.notes"
        />
      </form>
    </template>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <template v-if="editing">
          <AppButton variant="outline" :disabled="isSubmitting" @click="cancelEditing">
            Отмена
          </AppButton>
          <AppButton type="submit" form="client-form" :loading="isSubmitting">
            <template #icon>
              <Save :size="16" aria-hidden="true" />
            </template>
            Сохранить
          </AppButton>
        </template>
        <template v-else>
          <AppButton variant="outline" @click="open = false">Закрыть</AppButton>
          <AppButton v-if="isAdmin && client" @click="startEditing">
            <template #icon>
              <Pencil :size="15" aria-hidden="true" />
            </template>
            Редактировать
          </AppButton>
        </template>
      </div>
    </template>
  </AppModal>
</template>
