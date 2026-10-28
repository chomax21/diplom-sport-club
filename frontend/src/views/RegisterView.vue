<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Eye, EyeOff, LoaderCircle, UserPlus } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { z } from 'zod'

import { getApiErrorMessage } from '@/api/errors'
import AuthShell from '@/components/layout/AuthShell.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const schema = toTypedSchema(
  z
    .object({
      full_name: z
        .string({ error: 'Введите имя и фамилию' })
        .trim()
        .min(2, 'Минимум 2 символа')
        .max(255, 'Слишком длинное имя'),
      email: z
        .string({ error: 'Введите email' })
        .trim()
        .min(1, 'Введите email')
        .email('Некорректный email'),
      phone: z
        .string()
        .trim()
        .max(30, 'Слишком длинный номер')
        .refine(
          (value) => value === '' || /^[+\d][\d\s()-]{5,29}$/.test(value),
          'Некорректный номер телефона',
        ),
      password: z
        .string({ error: 'Придумайте пароль' })
        .min(8, 'Минимум 8 символов')
        .max(128, 'Максимум 128 символов')
        .regex(/[A-Za-zА-Яа-я]/, 'Добавьте хотя бы одну букву')
        .regex(/\d/, 'Добавьте хотя бы одну цифру'),
      confirm_password: z.string({ error: 'Повторите пароль' }).min(1, 'Повторите пароль'),
    })
    .refine((values) => values.password === values.confirm_password, {
      message: 'Пароли не совпадают',
      path: ['confirm_password'],
    }),
)

const { handleSubmit, errors, defineField, isSubmitting } = useForm({
  validationSchema: schema,
  initialValues: {
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
  },
})

const [fullName, fullNameAttrs] = defineField('full_name')
const [email, emailAttrs] = defineField('email')
const [phone, phoneAttrs] = defineField('phone')
const [password, passwordAttrs] = defineField('password')
const [confirmPassword, confirmPasswordAttrs] = defineField('confirm_password')

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const serverError = ref('')

const onSubmit = handleSubmit(async (values) => {
  serverError.value = ''

  try {
    await auth.register({
      full_name: values.full_name.trim(),
      email: values.email.trim(),
      phone: values.phone.trim() || null,
      password: values.password,
    })

    toast.success('Аккаунт клиента создан, вы вошли в систему.', 'Регистрация завершена')
    await router.replace('/app')
  } catch (error) {
    serverError.value = getApiErrorMessage(error)
  }
})

const inputClass =
  'block w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10'
</script>

<template>
  <AuthShell
    eyebrow="Регистрация клиента"
    title="Создайте аккаунт"
    subtitle="После регистрации вы сразу попадёте в личный кабинет. Тип аккаунта — клиент клуба."
    width="lg"
  >
    <form class="space-y-4" novalidate @submit.prevent="onSubmit">
      <div
        v-if="serverError"
        class="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
        role="alert"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p class="leading-5">{{ serverError }}</p>
      </div>

      <div>
        <label for="register-name" class="mb-1.5 block text-sm font-medium text-slate-700">
          Имя и фамилия
        </label>
        <input
          id="register-name"
          v-model="fullName"
          v-bind="fullNameAttrs"
          type="text"
          name="full_name"
          autocomplete="name"
          placeholder="Иван Петров"
          :class="[inputClass, errors.full_name ? 'border-rose-300' : 'border-slate-300']"
          :aria-invalid="Boolean(errors.full_name)"
          :aria-describedby="errors.full_name ? 'register-name-error' : undefined"
        />
        <p v-if="errors.full_name" id="register-name-error" class="mt-1.5 text-xs text-rose-600">
          {{ errors.full_name }}
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label for="register-email" class="mb-1.5 block text-sm font-medium text-slate-700">
            Email
          </label>
          <input
            id="register-email"
            v-model="email"
            v-bind="emailAttrs"
            type="email"
            name="email"
            autocomplete="email"
            inputmode="email"
            placeholder="you@example.com"
            :class="[inputClass, errors.email ? 'border-rose-300' : 'border-slate-300']"
            :aria-invalid="Boolean(errors.email)"
            :aria-describedby="errors.email ? 'register-email-error' : undefined"
          />
          <p v-if="errors.email" id="register-email-error" class="mt-1.5 text-xs text-rose-600">
            {{ errors.email }}
          </p>
        </div>

        <div>
          <label for="register-phone" class="mb-1.5 block text-sm font-medium text-slate-700">
            Телефон <span class="font-normal text-slate-400">— необязательно</span>
          </label>
          <input
            id="register-phone"
            v-model="phone"
            v-bind="phoneAttrs"
            type="tel"
            name="phone"
            autocomplete="tel"
            inputmode="tel"
            placeholder="+7 999 123-45-67"
            :class="[inputClass, errors.phone ? 'border-rose-300' : 'border-slate-300']"
            :aria-invalid="Boolean(errors.phone)"
            :aria-describedby="errors.phone ? 'register-phone-error' : undefined"
          />
          <p v-if="errors.phone" id="register-phone-error" class="mt-1.5 text-xs text-rose-600">
            {{ errors.phone }}
          </p>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label for="register-password" class="mb-1.5 block text-sm font-medium text-slate-700">
            Пароль
          </label>
          <div class="relative">
            <input
              id="register-password"
              v-model="password"
              v-bind="passwordAttrs"
              :type="showPassword ? 'text' : 'password'"
              name="password"
              autocomplete="new-password"
              placeholder="Минимум 8 символов"
              :class="[
                inputClass,
                'pr-12',
                errors.password ? 'border-rose-300' : 'border-slate-300',
              ]"
              :aria-invalid="Boolean(errors.password)"
              :aria-describedby="
                errors.password ? 'register-password-error' : 'register-password-hint'
              "
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 grid w-11 place-items-center rounded-r-xl text-slate-400 transition hover:text-slate-700"
              :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
              @click="showPassword = !showPassword"
            >
              <EyeOff v-if="showPassword" :size="18" aria-hidden="true" />
              <Eye v-else :size="18" aria-hidden="true" />
            </button>
          </div>
          <p
            v-if="errors.password"
            id="register-password-error"
            class="mt-1.5 text-xs text-rose-600"
          >
            {{ errors.password }}
          </p>
          <p v-else id="register-password-hint" class="mt-1.5 text-xs text-slate-400">
            Буква и цифра, не короче 8 символов
          </p>
        </div>

        <div>
          <label
            for="register-password-confirm"
            class="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Повторите пароль
          </label>
          <div class="relative">
            <input
              id="register-password-confirm"
              v-model="confirmPassword"
              v-bind="confirmPasswordAttrs"
              :type="showConfirmPassword ? 'text' : 'password'"
              name="confirm_password"
              autocomplete="new-password"
              placeholder="Ещё раз"
              :class="[
                inputClass,
                'pr-12',
                errors.confirm_password ? 'border-rose-300' : 'border-slate-300',
              ]"
              :aria-invalid="Boolean(errors.confirm_password)"
              :aria-describedby="
                errors.confirm_password ? 'register-password-confirm-error' : undefined
              "
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 grid w-11 place-items-center rounded-r-xl text-slate-400 transition hover:text-slate-700"
              :aria-label="showConfirmPassword ? 'Скрыть пароль' : 'Показать пароль'"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <EyeOff v-if="showConfirmPassword" :size="18" aria-hidden="true" />
              <Eye v-else :size="18" aria-hidden="true" />
            </button>
          </div>
          <p
            v-if="errors.confirm_password"
            id="register-password-confirm-error"
            class="mt-1.5 text-xs text-rose-600"
          >
            {{ errors.confirm_password }}
          </p>
        </div>
      </div>

      <button
        type="submit"
        class="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="isSubmitting"
      >
        <LoaderCircle v-if="isSubmitting" :size="17" class="animate-spin" aria-hidden="true" />
        <UserPlus v-else :size="17" aria-hidden="true" />
        {{ isSubmitting ? 'Создаём аккаунт…' : 'Зарегистрироваться' }}
      </button>
    </form>

    <template #footer>
      Уже есть аккаунт?
      <RouterLink
        to="/login"
        class="font-semibold text-brand-700 transition hover:text-brand-800 hover:underline"
      >
        Войти
      </RouterLink>
    </template>
  </AuthShell>
</template>
