<script setup lang="ts">
import { CircleAlert, RotateCcw, ShieldCheck } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import { getApiErrorMessage } from '@/api/errors'
import {
  AppBadge,
  AppButton,
  AppModal,
  ErrorState,
  LoadingState,
  StatusBadge,
} from '@/components/ui'
import { formatMoney } from '@/lib/format'
import { formatDateTime } from '@/lib/datetime'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'
import { usePaymentQuery, useRefundPaymentMutation } from '../queries'
import { PAYMENT_METHOD_LABELS, canRefundPayment, paymentProviderLabel } from '../status'

const props = withDefaults(
  defineProps<{
    paymentId?: string | null
  }>(),
  {
    paymentId: null,
  },
)

const emit = defineEmits<{
  refunded: []
}>()

const open = defineModel<boolean>({ default: false })

const auth = useAuthStore()
const toast = useToastStore()

const paymentQuery = usePaymentQuery(
  computed(() => props.paymentId),
  computed(() => open.value && Boolean(props.paymentId)),
)
const refundMutation = useRefundPaymentMutation()

const payment = computed(() => paymentQuery.data.value)
const canRefund = computed(() =>
  payment.value ? canRefundPayment(payment.value, auth.role) : false,
)

const confirming = ref(false)
const refundError = ref('')

watch(
  () => [open.value, props.paymentId] as const,
  ([isOpen]) => {
    if (isOpen) {
      confirming.value = false
      refundError.value = ''
    }
  },
  { immediate: true },
)

watch(payment, () => {
  confirming.value = false
})

async function refund(): Promise<void> {
  if (!payment.value) {
    return
  }

  refundError.value = ''

  try {
    await refundMutation.mutateAsync(payment.value.id)
    confirming.value = false
    toast.success('Платёж возвращён, связанный абонемент отменён.', 'Возврат оформлен')
    emit('refunded')
  } catch (error) {
    refundError.value = getApiErrorMessage(error)
  }
}
</script>

<template>
  <AppModal
    v-model="open"
    title="Детали платежа"
    description="Информация об операции и возврат средств."
    size="md"
  >
    <LoadingState v-if="paymentQuery.isPending.value" label="Загружаем платёж…" />

    <ErrorState
      v-else-if="paymentQuery.isError.value"
      title="Не удалось загрузить платёж"
      :description="getApiErrorMessage(paymentQuery.error.value)"
      @retry="paymentQuery.refetch()"
    />

    <div v-else-if="payment" class="space-y-5">
      <section class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Сумма</p>
            <p class="mt-1 text-2xl font-bold tracking-tight text-slate-900">
              {{ formatMoney(payment.amount, payment.currency) }}
            </p>
          </div>
          <StatusBadge kind="payment" :status="payment.status" />
        </div>
        <p class="mt-3 text-sm leading-6 text-slate-600">
          {{ payment.description || 'Назначение не указано.' }}
        </p>
      </section>

      <dl class="grid gap-3 sm:grid-cols-2">
        <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
          <dt class="text-xs font-medium text-slate-500">Клиент</dt>
          <dd class="mt-1 break-words text-sm font-medium text-slate-900">
            {{ payment.client_name }}
          </dd>
        </div>
        <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
          <dt class="text-xs font-medium text-slate-500">Способ оплаты</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900">
            {{ PAYMENT_METHOD_LABELS[payment.payment_method] }}
          </dd>
        </div>
        <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
          <dt class="text-xs font-medium text-slate-500">Создан</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900">
            {{ formatDateTime(payment.created_at) }}
          </dd>
        </div>
        <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
          <dt class="text-xs font-medium text-slate-500">Оплачен</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900">
            {{ payment.paid_at ? formatDateTime(payment.paid_at) : '—' }}
          </dd>
        </div>
        <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
          <dt class="text-xs font-medium text-slate-500">Провайдер</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900">
            {{ paymentProviderLabel(payment.provider) }}
          </dd>
        </div>
        <div class="rounded-2xl border border-slate-100 bg-white p-3.5">
          <dt class="text-xs font-medium text-slate-500">Внешний ID</dt>
          <dd class="mt-1 break-all font-mono text-xs text-slate-700">
            {{ payment.external_id || '—' }}
          </dd>
        </div>
      </dl>

      <div class="rounded-2xl border border-sky-200 bg-sky-50/70 p-4">
        <div class="flex items-start gap-2.5">
          <ShieldCheck :size="18" class="mt-0.5 shrink-0 text-sky-700" aria-hidden="true" />
          <p class="text-xs leading-5 text-sky-800">
            <template v-if="payment.provider === 'manual'">
              Платёж оформлен наличными в клубе. Возврат также выполняется администратором.
            </template>
            <template v-else>
              Демонстрационный mock-провайдер: реальные деньги не списывались и не возвращаются.
              Операция нужна для проверки сценария.
            </template>
          </p>
        </div>
      </div>

      <div
        v-if="payment.status === 'refunded'"
        class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4"
      >
        <p class="text-sm font-semibold text-emerald-800">Возврат оформлен</p>
        <p class="mt-1 text-xs leading-5 text-emerald-700">
          {{
            payment.refunded_at ? formatDateTime(payment.refunded_at) : 'Дата возврата не указана'
          }}. Связанный абонемент отменён.
        </p>
      </div>

      <section
        v-else-if="canRefund"
        class="rounded-2xl border border-slate-200 bg-white p-4"
        aria-labelledby="refund-heading"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div class="min-w-0">
            <h3 id="refund-heading" class="text-sm font-semibold text-slate-900">
              Возврат платежа
            </h3>
            <p class="mt-1 text-xs leading-5 text-slate-500">
              После возврата абонемент будет отменён. Если по нему уже есть посещения, сервер
              отклонит операцию.
            </p>
          </div>
          <AppButton v-if="!confirming" variant="danger" size="sm" @click="confirming = true">
            <template #icon>
              <RotateCcw :size="15" aria-hidden="true" />
            </template>
            Вернуть
          </AppButton>
        </div>

        <div
          v-if="confirming"
          class="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3.5"
          role="alertdialog"
          aria-labelledby="refund-confirm-text"
        >
          <p id="refund-confirm-text" class="text-sm leading-6 text-rose-800">
            Вернуть {{ formatMoney(payment.amount, payment.currency) }} и отменить связанный
            абонемент? Действие необратимо.
          </p>
          <p
            v-if="refundError"
            class="mt-2 rounded-lg border border-rose-300 bg-white p-2 text-xs leading-5 text-rose-700"
            role="alert"
          >
            {{ refundError }}
          </p>
          <div class="mt-3 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <AppButton
              variant="outline"
              size="sm"
              :disabled="refundMutation.isPending.value"
              @click="confirming = false"
            >
              Не возвращать
            </AppButton>
            <AppButton
              variant="danger"
              size="sm"
              :loading="refundMutation.isPending.value"
              @click="refund"
            >
              Подтвердить возврат
            </AppButton>
          </div>
        </div>
      </section>

      <div
        v-else
        class="flex items-start gap-2.5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-xs leading-5 text-slate-600"
      >
        <CircleAlert :size="17" class="mt-0.5 shrink-0 text-slate-400" aria-hidden="true" />
        <p>
          <template v-if="auth.role !== 'admin'"> Возврат оформляет администратор клуба. </template>
          <template v-else>
            Вернуть можно только успешный платёж. Текущий статус:
            <AppBadge tone="neutral">{{ payment.status }}</AppBadge>
          </template>
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end">
        <AppButton variant="outline" @click="open = false">Закрыть</AppButton>
      </div>
    </template>
  </AppModal>
</template>
