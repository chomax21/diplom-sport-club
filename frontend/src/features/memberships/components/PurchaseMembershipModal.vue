<script setup lang="ts">
import { CircleAlert, CreditCard, ShoppingCart, Wallet } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import type { MembershipType, PaymentMethod } from '@/api/memberships'
import {
  AppButton,
  AppModal,
  AppSelect,
  EmptyState,
  ErrorState,
  LoadingState,
} from '@/components/ui'
import { useClientsQuery } from '@/features/schedule/queries'
import { formatMoney } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'
import { durationDaysLabel, visitsLeftLabel } from '../status'
import { useMembershipTypesQuery, usePurchaseMembershipMutation } from '../queries'

const props = withDefaults(
  defineProps<{
    preselectedTypeId?: string | null
  }>(),
  {
    preselectedTypeId: null,
  },
)

const emit = defineEmits<{
  purchased: []
}>()

const open = defineModel<boolean>({ default: false })

const auth = useAuthStore()
const toast = useToastStore()

const isAdmin = computed(() => auth.role === 'admin')

const typesQuery = useMembershipTypesQuery(
  computed(() => ({ limit: 200 })),
  open,
)
const clientsQuery = useClientsQuery(computed(() => open.value && isAdmin.value))
const purchaseMutation = usePurchaseMembershipMutation()

const selectedTypeId = ref<string | number>('')
const selectedClientId = ref<string | number>('')
const paymentMethod = ref<string | number>('card')
const serverError = ref('')

const activeTypes = computed<MembershipType[]>(() =>
  (typesQuery.data.value?.items ?? []).filter((item) => item.is_active),
)

const selectedType = computed<MembershipType | null>(
  () => activeTypes.value.find((item) => item.id === selectedTypeId.value) ?? null,
)

const clientOptions = computed(() =>
  (clientsQuery.data.value?.items ?? [])
    .filter((client) => client.is_active)
    .map((client) => ({
      label: `${client.full_name} · ${client.email}`,
      value: client.id,
    })),
)

const paymentOptions = computed(() => {
  const options = [
    { label: 'Банковская карта', value: 'card' },
    { label: 'Онлайн-оплата', value: 'online' },
  ]

  if (isAdmin.value) {
    options.push({ label: 'Наличные в клубе', value: 'cash' })
  }

  return options
})

const canSubmit = computed(
  () => Boolean(selectedType.value) && (!isAdmin.value || Boolean(selectedClientId.value)),
)

watch(
  () => [open.value, props.preselectedTypeId] as const,
  ([isOpen]) => {
    if (isOpen) {
      selectedTypeId.value = props.preselectedTypeId ?? ''
      selectedClientId.value = ''
      paymentMethod.value = 'card'
      serverError.value = ''
    }
  },
  { immediate: true },
)

async function submit(): Promise<void> {
  serverError.value = ''

  if (!selectedType.value) {
    serverError.value = 'Выберите вид абонемента.'
    return
  }

  if (isAdmin.value && !selectedClientId.value) {
    serverError.value = 'Выберите клиента, на которого оформляется абонемент.'
    return
  }

  try {
    await purchaseMutation.mutateAsync({
      membership_type_id: selectedType.value.id,
      client_id: isAdmin.value ? String(selectedClientId.value) : null,
      payment_method: paymentMethod.value as PaymentMethod,
    })

    toast.success(
      `Абонемент «${selectedType.value.name}» оформлен.`,
      paymentMethod.value === 'cash' ? 'Оплата принята' : 'Платёж прошёл',
    )
    open.value = false
    emit('purchased')
  } catch (error) {
    serverError.value = getApiErrorMessage(error)
  }
}
</script>

<template>
  <AppModal
    v-model="open"
    title="Оформить абонемент"
    description="Выберите вид абонемента, клиента и способ оплаты. Платёж обрабатывается демонстрационным провайдером."
    size="lg"
    :prevent-close="purchaseMutation.isPending.value"
  >
    <LoadingState v-if="typesQuery.isPending.value" label="Загружаем виды абонементов…" />

    <ErrorState
      v-else-if="typesQuery.isError.value"
      title="Не удалось загрузить каталог"
      :description="getApiErrorMessage(typesQuery.error.value)"
      @retry="typesQuery.refetch()"
    />

    <div v-else class="space-y-5">
      <div
        v-if="serverError"
        class="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700"
        role="alert"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p class="leading-5">{{ serverError }}</p>
      </div>

      <section aria-labelledby="purchase-type-heading">
        <h3 id="purchase-type-heading" class="text-sm font-semibold text-slate-900">
          1. Вид абонемента
        </h3>

        <EmptyState
          v-if="activeTypes.length === 0"
          class="mt-3"
          compact
          title="Каталог пуст"
          description="Администратор ещё не добавил виды абонементов."
        />

        <div
          v-else
          class="mt-3 grid gap-2.5 sm:grid-cols-2"
          role="radiogroup"
          aria-label="Вид абонемента"
        >
          <button
            v-for="item in activeTypes"
            :key="item.id"
            type="button"
            role="radio"
            :aria-checked="selectedTypeId === item.id"
            :class="[
              'min-w-0 rounded-2xl border p-3 text-left transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
              selectedTypeId === item.id
                ? 'border-brand-500 bg-brand-50/70 ring-2 ring-brand-500/20'
                : 'border-slate-200 bg-white hover:border-brand-200 hover:bg-slate-50',
            ]"
            @click="selectedTypeId = item.id"
          >
            <span class="flex items-start justify-between gap-2">
              <span class="min-w-0 text-sm font-semibold leading-5 text-slate-900">
                {{ item.name }}
              </span>
              <span class="shrink-0 text-sm font-bold text-slate-900">
                {{ formatMoney(item.price) }}
              </span>
            </span>
            <span class="mt-1.5 block text-xs leading-5 text-slate-500">
              {{ durationDaysLabel(item.duration_days) }} ·
              {{ visitsLeftLabel(item.visits_limit) }}
            </span>
          </button>
        </div>
      </section>

      <section v-if="isAdmin" aria-labelledby="purchase-client-heading">
        <h3 id="purchase-client-heading" class="mb-2 text-sm font-semibold text-slate-900">
          2. Клиент
        </h3>
        <AppSelect
          v-model="selectedClientId"
          :options="clientOptions"
          placeholder="Выберите клиента"
          :disabled="clientsQuery.isPending.value"
          :hint="
            clientsQuery.isError.value
              ? 'Не удалось загрузить клиентов. Обновите страницу.'
              : 'Абонемент будет оформлен на выбранного клиента.'
          "
        />
      </section>

      <section aria-labelledby="purchase-payment-heading">
        <h3 id="purchase-payment-heading" class="mb-2 text-sm font-semibold text-slate-900">
          {{ isAdmin ? '3. Способ оплаты' : '2. Способ оплаты' }}
        </h3>
        <AppSelect v-model="paymentMethod" :options="paymentOptions" />
      </section>

      <div class="rounded-2xl border border-sky-200 bg-sky-50/70 p-4">
        <div class="flex items-start gap-2.5">
          <Wallet :size="18" class="mt-0.5 shrink-0 text-sky-700" aria-hidden="true" />
          <div class="min-w-0 text-xs leading-5 text-sky-800">
            <p class="font-semibold">Демонстрационная оплата</p>
            <p class="mt-0.5">
              {{
                paymentMethod === 'cash'
                  ? 'Наличные принимает администратор в клубе. Абонемент активируется сразу после оформления.'
                  : 'Платёж имитируется mock-провайдером: реальные деньги не списываются, но операция появляется в истории платежей.'
              }}
            </p>
          </div>
        </div>
      </div>

      <div
        v-if="selectedType"
        class="flex flex-col gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="min-w-0">
          <p class="text-sm font-semibold text-slate-900">{{ selectedType.name }}</p>
          <p class="mt-0.5 text-xs text-slate-500">
            {{ durationDaysLabel(selectedType.duration_days) }} ·
            {{ visitsLeftLabel(selectedType.visits_limit) }}
          </p>
        </div>
        <p class="text-xl font-bold text-slate-900">{{ formatMoney(selectedType.price) }}</p>
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-center text-xs text-slate-500 sm:text-left">
          <span class="inline-flex items-center gap-1.5">
            <CreditCard :size="14" aria-hidden="true" />
            Списание не выполняется
          </span>
        </p>
        <div class="flex flex-col-reverse gap-2 sm:flex-row">
          <AppButton
            variant="outline"
            :disabled="purchaseMutation.isPending.value"
            @click="open = false"
          >
            Отмена
          </AppButton>
          <AppButton
            :loading="purchaseMutation.isPending.value"
            :disabled="!canSubmit"
            @click="submit"
          >
            <template #icon>
              <ShoppingCart :size="16" aria-hidden="true" />
            </template>
            Оформить{{ selectedType ? ` за ${formatMoney(selectedType.price)}` : '' }}
          </AppButton>
        </div>
      </div>
    </template>
  </AppModal>
</template>
