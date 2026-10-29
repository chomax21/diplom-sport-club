<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Save, ShieldCheck } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import type { UserRecord } from '@/api/directory'
import { getApiErrorMessage } from '@/api/errors'
import type { UserRole } from '@/api/types'
import { AppButton, AppInput, AppModal, AppSelect } from '@/components/ui'
import { useCreateUserMutation, useUpdateUserMutation } from '../queries'
import { USER_ROLE_OPTIONS, profileLabelForRole } from '../utils'
import { createUserFormSchema, type UserFormValues } from '../validation'
import { useToastStore } from '@/stores/toasts'

const props = withDefaults(
  defineProps<{
    user?: UserRecord | null
    defaultRole?: UserRole
    lockRole?: boolean
  }>(),
  {
    user: null,
    defaultRole: 'client',
    lockRole: false,
  },
)

const emit = defineEmits<{
  saved: []
}>()

const open = defineModel<boolean>({ default: false })

const toast = useToastStore()
const createMutation = useCreateUserMutation()
const updateMutation = useUpdateUserMutation()

const isEditing = computed(() => Boolean(props.user))
const isSaving = computed(() => createMutation.isPending.value || updateMutation.isPending.value)

const modalTitle = computed(() => {
  if (isEditing.value) {
    return 'Изменить пользователя'
  }
  if (props.lockRole && props.defaultRole === 'trainer') {
    return 'Новый тренер'
  }
  if (props.lockRole && props.defaultRole === 'client') {
    return 'Новый клиент'
  }
  return 'Новый пользователь'
})

const submitLabel = computed(() => {
  if (isEditing.value) {
    return 'Сохранить изменения'
  }
  if (props.lockRole && props.defaultRole === 'trainer') {
    return 'Создать тренера'
  }
  if (props.lockRole && props.defaultRole === 'client') {
    return 'Создать клиента'
  }
  return 'Создать пользователя'
})

function initialValues(): UserFormValues {
  return {
    email: props.user?.email ?? '',
    password: '',
    password_confirm: '',
    full_name: props.user?.full_name ?? '',
    phone: props.user?.phone ?? '',
    role: props.user?.role ?? props.defaultRole,
  }
}

const schema = toTypedSchema(createUserFormSchema({ editing: isEditing }))

const { handleSubmit, errors, defineField, isSubmitting, resetForm } = useForm({
  validationSchema: schema,
  initialValues: initialValues(),
})

const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')
const [passwordConfirm, passwordConfirmAttrs] = defineField('password_confirm')
const [fullName, fullNameAttrs] = defineField('full_name')
const [phone, phoneAttrs] = defineField('phone')
const [role, roleAttrs] = defineField('role')

const serverError = ref('')

const selectedRole = computed<UserRole>(() => {
  const value = role.value
  if (value === 'admin' || value === 'trainer' || value === 'client') {
    return value
  }
  return props.defaultRole
})

const roleHint = computed(() => profileLabelForRole(selectedRole.value))

const profileNote = computed(() => {
  if (selectedRole.value === 'admin') {
    return 'Учётная запись администратора не связана с профилем клиента или тренера. Блокировка доступа выполняется на странице пользователей.'
  }
  return `Учётная запись связана с профилем ${
    selectedRole.value === 'trainer' ? 'тренера' : 'клиента'
  } автоматически. Блокировка доступа выполняется на странице пользователей.`
})

watch(
  () => [open.value, props.user] as const,
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

  try {
    if (props.user) {
      await updateMutation.mutateAsync({
        id: props.user.id,
        payload: {
          full_name: values.full_name.trim(),
          phone: values.phone.trim() || null,
        },
      })
      toast.success('Данные пользователя сохранены.', 'Пользователь обновлён')
    } else {
      const created = await createMutation.mutateAsync({
        email: values.email.trim(),
        password: values.password,
        full_name: values.full_name.trim(),
        phone: values.phone.trim() || null,
        role: selectedRole.value,
      })

      const profileMessage =
        created.role === 'trainer'
          ? 'Профиль тренера создан автоматически.'
          : created.role === 'client'
            ? 'Профиль клиента создан автоматически.'
            : 'Учётная запись администратора создана.'

      toast.success(profileMessage, 'Пользователь создан')
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
    :description="
      isEditing
        ? 'Измените имя и телефон. Email и роль назначаются при создании учётной записи.'
        : 'Создайте учётную запись и назначьте роль. Профиль клиента или тренера создаётся автоматически.'
    "
    size="lg"
    :prevent-close="isSubmitting || isSaving"
  >
    <form id="user-form" class="space-y-4" novalidate @submit.prevent="onSubmit">
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
          v-model="email"
          v-bind="emailAttrs"
          label="Email"
          type="email"
          placeholder="user@example.com"
          autocomplete="off"
          required
          :readonly="isEditing"
          :error="errors.email"
          :hint="isEditing ? 'Email нельзя изменить' : undefined"
        />
        <AppInput
          v-model="fullName"
          v-bind="fullNameAttrs"
          label="Полное имя"
          placeholder="Иван Петров"
          required
          :error="errors.full_name"
        />
      </div>

      <template v-if="!isEditing">
        <div class="grid gap-4 sm:grid-cols-2">
          <AppInput
            v-model="password"
            v-bind="passwordAttrs"
            label="Пароль"
            type="password"
            placeholder="Минимум 8 символов"
            autocomplete="new-password"
            required
            :error="errors.password"
          />
          <AppInput
            v-model="passwordConfirm"
            v-bind="passwordConfirmAttrs"
            label="Повторите пароль"
            type="password"
            placeholder="Ещё раз"
            autocomplete="new-password"
            required
            :error="errors.password_confirm"
          />
        </div>
      </template>

      <div class="grid gap-4 sm:grid-cols-2">
        <AppInput
          v-model="phone"
          v-bind="phoneAttrs"
          label="Телефон"
          type="tel"
          placeholder="+7 900 000-00-00"
          :error="errors.phone"
        />
        <AppSelect
          v-model="role"
          v-bind="roleAttrs"
          label="Роль"
          :options="USER_ROLE_OPTIONS"
          :disabled="isEditing || lockRole"
          :error="errors.role"
          :hint="isEditing ? 'Роль нельзя изменить после создания' : roleHint"
        />
      </div>

      <div
        v-if="isEditing"
        class="flex items-start gap-2.5 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs leading-5 text-slate-600"
      >
        <ShieldCheck :size="16" class="mt-0.5 shrink-0 text-slate-400" aria-hidden="true" />
        <p>{{ profileNote }}</p>
      </div>
    </form>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <AppButton variant="outline" :disabled="isSubmitting || isSaving" @click="open = false">
          Отмена
        </AppButton>
        <AppButton type="submit" form="user-form" :loading="isSubmitting || isSaving">
          <template #icon>
            <Save :size="16" aria-hidden="true" />
          </template>
          {{ submitLabel }}
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
