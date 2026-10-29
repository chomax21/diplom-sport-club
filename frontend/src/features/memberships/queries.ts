import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'

import {
  membershipsApi,
  type MembershipListParams,
  type MembershipTypeListParams,
  type MembershipTypePayload,
  type PaymentListParams,
  type PurchasePayload,
} from '@/api/memberships'
import { useAuthStore } from '@/stores/auth'

export const membershipKeys = {
  types: ['membership-types'] as const,
  typeList: (params: MembershipTypeListParams) => ['membership-types', 'list', params] as const,
  memberships: ['memberships'] as const,
  membershipList: (params: MembershipListParams) => ['memberships', 'list', params] as const,
  membershipDetail: (id: string) => ['memberships', 'detail', id] as const,
  payments: ['payments'] as const,
  paymentList: (params: PaymentListParams) => ['payments', 'list', params] as const,
  paymentDetail: (id: string) => ['payments', 'detail', id] as const,
}

function authenticatedEnabled(enabled: MaybeRefOrGetter<boolean>) {
  const auth = useAuthStore()
  return computed(() => auth.isAuthenticated && Boolean(toValue(enabled)))
}

export function useMembershipTypesQuery(
  params: MaybeRefOrGetter<MembershipTypeListParams> = {},
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => membershipKeys.typeList(toValue(params))),
    queryFn: () => membershipsApi.listTypes(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
    staleTime: 60_000,
  })
}

export function useMembershipsQuery(
  params: MaybeRefOrGetter<MembershipListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => membershipKeys.membershipList(toValue(params))),
    queryFn: () => membershipsApi.listMemberships(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function usePaymentsQuery(
  params: MaybeRefOrGetter<PaymentListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => membershipKeys.paymentList(toValue(params))),
    queryFn: () => membershipsApi.listPayments(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function usePaymentQuery(
  id: MaybeRefOrGetter<string | null>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => membershipKeys.paymentDetail(toValue(id) ?? '')),
    queryFn: () => {
      const paymentId = toValue(id)
      if (!paymentId) {
        throw new Error('Не указан платёж')
      }
      return membershipsApi.getPayment(paymentId)
    },
    enabled: authenticatedEnabled(computed(() => Boolean(toValue(id)) && toValue(enabled))),
  })
}

export function useCreateMembershipTypeMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: MembershipTypePayload) => membershipsApi.createType(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: membershipKeys.types })
    },
  })
}

export function useUpdateMembershipTypeMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { id: string; payload: Partial<MembershipTypePayload> }) =>
      membershipsApi.updateType(variables.id, variables.payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: membershipKeys.types })
    },
  })
}

export function useDeactivateMembershipTypeMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => membershipsApi.deactivateType(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: membershipKeys.types })
    },
  })
}

export function usePurchaseMembershipMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: PurchasePayload) => membershipsApi.purchase(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: membershipKeys.memberships })
      void queryClient.invalidateQueries({ queryKey: membershipKeys.payments })
      void queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })
}

export function useCancelMembershipMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => membershipsApi.cancelMembership(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: membershipKeys.memberships })
      void queryClient.invalidateQueries({ queryKey: membershipKeys.payments })
    },
  })
}

export function useRefundPaymentMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => membershipsApi.refundPayment(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: membershipKeys.payments })
      void queryClient.invalidateQueries({ queryKey: membershipKeys.memberships })
      void queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })
}
