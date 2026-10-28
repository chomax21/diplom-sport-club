<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { CircleAlert, Eye, EyeOff, LoaderCircle, LogIn } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { z } from 'zod'

import { getApiErrorMessage } from '@/api/errors'
import type { UserRole } from '@/api/types'
import AuthShell from '@/components/layout/AuthShell.vue'
import { roleLabel } from '@/lib/roles'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const schema = toTypedSchema(
  z.object({
    email: z
      .string({ error: 'Введите email' })
      .trim()
      .min(1, 'Введите email')
      .email('Некорректный email'),
    password: z.string({ error: 'Введите пароль' }).min(1, 'Введите пароль'),
  }),
)

const { handleSubmit, errors, defineField, isSubmitting, setFieldValue } = useForm({
  validationSchema: schema,
  initialValues: {
    email: '',
    password: '',
  },
})

const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const showPassword = ref(false)
const serverError = ref('')

const redirectTarget = computed(() => {
  const value = route.query.redirect
  return typeof value === 'string' && value.startsWith('/app') ? value : '/app'
})

interface DemoAccount {
  role: UserRole
  email: string
  password: string
}

const demoAccounts: DemoAccount[] = [
  { role: 'admin', email: 'admin@sportsclub.ru', password: 'Admin12345' },
  { role: 'trainer', email: 'trainer@sportsclub.ru', password: 'Trainer12345' },
  { role: 'client', email: 'client@sportsclub.ru', password: 'Client12345' },
]

function fillDemo(account: DemoAccount): void {
  serverError.value = ''
  setFieldValue('email', account.email)
  setFieldValue('password', account.password)
}

const onSubmit = handleSubmit(async (values) => {
  serverError.value = ''

  try {
    const user = await auth.login({
      email: values.email.trim(),
      password: values.password,
    })

    toast.success(`Здравствуйте, ${user.full_name}`, 'Вход выполнен')
    await router.replace(redirectTarget.value)
  } catch (error) {
    serverError.value = getApiErrorMessage(error)
  }
})

const inputClass =
  'block w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10'
</script>

<template>
  <AuthShell
    eyebrow="Вход в систему"
    title="Рады видеть снова"
    subtitle="Введите email и пароль, чтобы открыть панель клуба."
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
        <label for="login-email" class="mb-1.5 block text-sm font-medium text-slate-700">
          Email
        </label>
        <input
          id="login-email"
          v-model="email"
          v-bind="emailAttrs"
          type="email"
          name="email"
          autocomplete="email"
          inputmode="email"
          placeholder="you@example.com"
          :class="[inputClass, errors.email ? 'border-rose-300' : 'border-slate-300']"
          :aria-invalid="Boolean(errors.email)"
          :aria-describedby="errors.email ? 'login-email-error' : undefined"
        />
        <p v-if="errors.email" id="login-email-error" class="mt-1.5 text-xs text-rose-600">
          {{ errors.email }}
        </p>
      </div>

      <div>
        <label for="login-password" class="mb-1.5 block text-sm font-medium text-slate-700">
          Пароль
        </label>
        <div class="relative">
          <input
            id="login-password"
            v-model="password"
            v-bind="passwordAttrs"
            :type="showPassword ? 'text' : 'password'"
            name="password"
            autocomplete="current-password"
            placeholder="Введите пароль"
            :class="[inputClass, 'pr-12', errors.password ? 'border-rose-300' : 'border-slate-300']"
            :aria-invalid="Boolean(errors.password)"
            :aria-describedby="errors.password ? 'login-password-error' : undefined"
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
        <p v-if="errors.password" id="login-password-error" class="mt-1.5 text-xs text-rose-600">
          {{ errors.password }}
        </p>
      </div>

      <button
        type="submit"
        class="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="isSubmitting"
      >
        <LoaderCircle v-if="isSubmitting" :size="17" class="animate-spin" aria-hidden="true" />
        <LogIn v-else :size="17" aria-hidden="true" />
        {{ isSubmitting ? 'Входим…' : 'Войти' }}
      </button>
    </form>

    <div class="mt-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between gap-2">
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Демо-доступ</p>
        <span class="text-[11px] text-slate-400">нажмите, чтобы заполнить</span>
      </div>
      <div class="mt-3 grid gap-2">
        <button
          v-for="account in demoAccounts"
          :key="account.role"
          type="button"
          class="flex min-h-11 items-center justify-between gap-3 rounded-xl border border-slate-200 px-3 py-2 text-left transition hover:border-brand-200 hover:bg-brand-50/50"
          @click="fillDemo(account)"
        >
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800">{{
              roleLabel(account.role)
            }}</span>
            <span class="block truncate text-xs text-slate-500">{{ account.email }}</span>
          </span>
          <span
            class="shrink-0 rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600"
          >
            {{ account.password }}
          </span>
        </button>
      </div>
    </div>

    <template #footer>
      Нет аккаунта?
      <RouterLink
        to="/register"
        class="font-semibold text-brand-700 transition hover:text-brand-800 hover:underline"
      >
        Зарегистрироваться как клиент
      </RouterLink>
    </template>
  </AuthShell>
</template>
