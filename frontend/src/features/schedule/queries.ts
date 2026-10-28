import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'

import {
  scheduleApi,
  type EnrollmentListParams,
  type TrainingSessionListParams,
  type TrainingSessionPayload,
} from '@/api/schedule'
import { useAuthStore } from '@/stores/auth'

export const scheduleKeys = {
  sessions: ['sessions'] as const,
  sessionList: (params: TrainingSessionListParams) => ['sessions', 'list', params] as const,
  sessionDetail: (id: string) => ['sessions', 'detail', id] as const,
  enrollments: ['enrollments'] as const,
  myEnrollments: ['enrollments', 'my'] as const,
  sessionEnrollments: (id: string, includeCancelled: boolean) =>
    ['enrollments', 'session', id, { includeCancelled }] as const,
  rooms: ['rooms'] as const,
  trainers: ['trainers'] as const,
  myTrainer: ['trainers', 'me'] as const,
  clients: ['clients', 'options'] as const,
}

function authenticatedEnabled(enabled: MaybeRefOrGetter<boolean>) {
  const auth = useAuthStore()
  return computed(() => auth.isAuthenticated && Boolean(toValue(enabled)))
}

export function useSessionsQuery(
  params: MaybeRefOrGetter<TrainingSessionListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => scheduleKeys.sessionList(toValue(params))),
    queryFn: () => scheduleApi.listSessions(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function useSessionQuery(id: MaybeRefOrGetter<string>) {
  return useQuery({
    queryKey: computed(() => scheduleKeys.sessionDetail(toValue(id))),
    queryFn: () => scheduleApi.getSession(toValue(id)),
    enabled: authenticatedEnabled(computed(() => Boolean(toValue(id)))),
  })
}

export function useRoomsQuery(enabled: MaybeRefOrGetter<boolean> = true) {
  return useQuery({
    queryKey: scheduleKeys.rooms,
    queryFn: () => scheduleApi.listRooms({ limit: 200 }),
    enabled: authenticatedEnabled(enabled),
    staleTime: 5 * 60_000,
  })
}

export function useTrainersQuery(enabled: MaybeRefOrGetter<boolean> = true) {
  return useQuery({
    queryKey: scheduleKeys.trainers,
    queryFn: () => scheduleApi.listTrainers({ limit: 200 }),
    enabled: authenticatedEnabled(enabled),
    staleTime: 5 * 60_000,
  })
}

export function useMyTrainerQuery(enabled: MaybeRefOrGetter<boolean>) {
  return useQuery({
    queryKey: scheduleKeys.myTrainer,
    queryFn: () => scheduleApi.myTrainer(),
    enabled: authenticatedEnabled(enabled),
    staleTime: 5 * 60_000,
  })
}

export function useMyEnrollmentsQuery(enabled: MaybeRefOrGetter<boolean>) {
  return useQuery({
    queryKey: scheduleKeys.myEnrollments,
    queryFn: () => scheduleApi.myEnrollments({ limit: 200 }),
    enabled: authenticatedEnabled(enabled),
  })
}

export function useSessionEnrollmentsQuery(
  sessionId: MaybeRefOrGetter<string>,
  includeCancelled: MaybeRefOrGetter<boolean>,
  enabled: MaybeRefOrGetter<boolean>,
) {
  const params = computed<EnrollmentListParams>(() => ({
    include_cancelled: toValue(includeCancelled),
    limit: 200,
  }))

  return useQuery({
    queryKey: computed(() =>
      scheduleKeys.sessionEnrollments(toValue(sessionId), toValue(includeCancelled)),
    ),
    queryFn: () => scheduleApi.listSessionEnrollments(toValue(sessionId), toValue(params)),
    enabled: authenticatedEnabled(computed(() => Boolean(toValue(enabled) && toValue(sessionId)))),
  })
}

export function useClientsQuery(enabled: MaybeRefOrGetter<boolean>) {
  return useQuery({
    queryKey: scheduleKeys.clients,
    queryFn: () => scheduleApi.listClients({ limit: 200 }),
    enabled: authenticatedEnabled(enabled),
    staleTime: 2 * 60_000,
  })
}

export function useCreateSessionMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: TrainingSessionPayload) => scheduleApi.createSession(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.sessions })
    },
  })
}

export function useUpdateSessionMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { id: string; payload: Partial<TrainingSessionPayload> }) =>
      scheduleApi.updateSession(variables.id, variables.payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.sessions })
    },
  })
}

export function useCancelSessionMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => scheduleApi.cancelSession(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.sessions })
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.enrollments })
    },
  })
}

export function useEnrollMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { sessionId: string; clientId?: string }) =>
      scheduleApi.enroll(variables.sessionId, variables.clientId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.enrollments })
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.sessions })
    },
  })
}

export function useCancelEnrollmentMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => scheduleApi.cancelEnrollment(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.enrollments })
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.sessions })
    },
  })
}

export function useAttendanceMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { enrollmentId: string; action: 'attend' | 'no_show' }) =>
      variables.action === 'attend'
        ? scheduleApi.markAttendance(variables.enrollmentId)
        : scheduleApi.markNoShow(variables.enrollmentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.enrollments })
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.sessions })
      void queryClient.invalidateQueries({ queryKey: ['memberships'] })
    },
  })
}
