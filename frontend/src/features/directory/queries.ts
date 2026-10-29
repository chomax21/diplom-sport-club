import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'

import {
  directoryApi,
  type ClientListParams,
  type ClientUpdatePayload,
  type RoomListParams,
  type RoomPayload,
  type TrainerListParams,
  type TrainerUpdatePayload,
  type UserCreatePayload,
  type UserListParams,
  type UserUpdatePayload,
} from '@/api/directory'
import { useAuthStore } from '@/stores/auth'

export const directoryKeys = {
  clients: ['clients'] as const,
  clientList: (params: ClientListParams) => ['clients', 'list', params] as const,
  clientDetail: (id: string) => ['clients', 'detail', id] as const,
  trainers: ['trainers'] as const,
  trainerList: (params: TrainerListParams) => ['trainers', 'list', params] as const,
  trainerDetail: (id: string) => ['trainers', 'detail', id] as const,
  rooms: ['rooms'] as const,
  roomList: (params: RoomListParams) => ['rooms', 'list', params] as const,
  users: ['users'] as const,
  userList: (params: UserListParams) => ['users', 'list', params] as const,
}

function authenticatedEnabled(enabled: MaybeRefOrGetter<boolean>) {
  const auth = useAuthStore()
  return computed(() => auth.isAuthenticated && Boolean(toValue(enabled)))
}

export function useClientListQuery(
  params: MaybeRefOrGetter<ClientListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => directoryKeys.clientList(toValue(params))),
    queryFn: () => directoryApi.clients.list(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function useClientQuery(
  id: MaybeRefOrGetter<string | null>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => directoryKeys.clientDetail(toValue(id) ?? '')),
    queryFn: () => {
      const clientId = toValue(id)
      if (!clientId) {
        throw new Error('Не указан клиент')
      }
      return directoryApi.clients.get(clientId)
    },
    enabled: authenticatedEnabled(computed(() => Boolean(toValue(id)) && toValue(enabled))),
  })
}

export function useTrainerListQuery(
  params: MaybeRefOrGetter<TrainerListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => directoryKeys.trainerList(toValue(params))),
    queryFn: () => directoryApi.trainers.list(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function useTrainerQuery(
  id: MaybeRefOrGetter<string | null>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => directoryKeys.trainerDetail(toValue(id) ?? '')),
    queryFn: () => {
      const trainerId = toValue(id)
      if (!trainerId) {
        throw new Error('Не указан тренер')
      }
      return directoryApi.trainers.get(trainerId)
    },
    enabled: authenticatedEnabled(computed(() => Boolean(toValue(id)) && toValue(enabled))),
  })
}

export function useRoomListQuery(
  params: MaybeRefOrGetter<RoomListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => directoryKeys.roomList(toValue(params))),
    queryFn: () => directoryApi.rooms.list(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function useUserListQuery(
  params: MaybeRefOrGetter<UserListParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => directoryKeys.userList(toValue(params))),
    queryFn: () => directoryApi.users.list(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
  })
}

export function useUpdateClientMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { id: string; payload: ClientUpdatePayload }) =>
      directoryApi.clients.update(variables.id, variables.payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: directoryKeys.clients })
      void queryClient.invalidateQueries({ queryKey: directoryKeys.users })
    },
  })
}

export function useUpdateTrainerMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { id: string; payload: TrainerUpdatePayload }) =>
      directoryApi.trainers.update(variables.id, variables.payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: directoryKeys.trainers })
      void queryClient.invalidateQueries({ queryKey: directoryKeys.users })
    },
  })
}

export function useCreateRoomMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: RoomPayload) => directoryApi.rooms.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: directoryKeys.rooms })
    },
  })
}

export function useUpdateRoomMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { id: string; payload: Partial<RoomPayload> }) =>
      directoryApi.rooms.update(variables.id, variables.payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: directoryKeys.rooms })
    },
  })
}

export function useDeactivateRoomMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => directoryApi.rooms.deactivate(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: directoryKeys.rooms })
    },
  })
}

function invalidateDirectoryProfiles(queryClient: ReturnType<typeof useQueryClient>): void {
  void queryClient.invalidateQueries({ queryKey: directoryKeys.users })
  void queryClient.invalidateQueries({ queryKey: directoryKeys.clients })
  void queryClient.invalidateQueries({ queryKey: directoryKeys.trainers })
}

export function useCreateUserMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: UserCreatePayload) => directoryApi.users.create(payload),
    onSuccess: () => {
      invalidateDirectoryProfiles(queryClient)
    },
  })
}

export function useUpdateUserMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables: { id: string; payload: UserUpdatePayload }) =>
      directoryApi.users.update(variables.id, variables.payload),
    onSuccess: () => {
      invalidateDirectoryProfiles(queryClient)
    },
  })
}

export function useDeactivateUserMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => directoryApi.users.deactivate(id),
    onSuccess: () => {
      invalidateDirectoryProfiles(queryClient)
    },
  })
}
