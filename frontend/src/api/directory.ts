import { apiClient } from './client'
import type { Page, UserRole } from './types'

export interface ClientRecord {
  id: string
  user_id: string
  full_name: string
  email: string
  phone: string | null
  birth_date: string | null
  notes: string | null
  emergency_contact: string | null
  is_active: boolean
  created_at: string
}

export interface ClientListParams {
  search?: string
  limit?: number
  offset?: number
}

export interface ClientUpdatePayload {
  full_name?: string
  phone?: string | null
  birth_date?: string | null
  notes?: string | null
  emergency_contact?: string | null
}

export interface TrainerRecord {
  id: string
  user_id: string
  full_name: string
  email: string
  phone: string | null
  specialization: string | null
  bio: string | null
  is_active: boolean
  created_at: string
}

export interface TrainerListParams {
  search?: string
  limit?: number
  offset?: number
}

export interface TrainerUpdatePayload {
  full_name?: string
  phone?: string | null
  specialization?: string | null
  bio?: string | null
}

export interface RoomRecord {
  id: string
  name: string
  capacity: number
  description: string | null
  is_active: boolean
}

export interface RoomListParams {
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export interface RoomPayload {
  name: string
  capacity: number
  description?: string | null
  is_active?: boolean
}

export interface UserRecord {
  id: string
  email: string
  full_name: string
  phone: string | null
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface UserListParams {
  role?: UserRole
  search?: string
  limit?: number
  offset?: number
}

export interface UserCreatePayload {
  email: string
  password: string
  full_name: string
  phone?: string | null
  role: UserRole
}

export interface UserUpdatePayload {
  full_name?: string
  phone?: string | null
  is_active?: boolean
}

export const directoryApi = {
  clients: {
    async list(params: ClientListParams = {}): Promise<Page<ClientRecord>> {
      const { data } = await apiClient.get<Page<ClientRecord>>('/clients', { params })
      return data
    },

    async get(id: string): Promise<ClientRecord> {
      const { data } = await apiClient.get<ClientRecord>(`/clients/${id}`)
      return data
    },

    async update(id: string, payload: ClientUpdatePayload): Promise<ClientRecord> {
      const { data } = await apiClient.patch<ClientRecord>(`/clients/${id}`, payload)
      return data
    },
  },

  trainers: {
    async list(params: TrainerListParams = {}): Promise<Page<TrainerRecord>> {
      const { data } = await apiClient.get<Page<TrainerRecord>>('/trainers', { params })
      return data
    },

    async get(id: string): Promise<TrainerRecord> {
      const { data } = await apiClient.get<TrainerRecord>(`/trainers/${id}`)
      return data
    },

    async update(id: string, payload: TrainerUpdatePayload): Promise<TrainerRecord> {
      const { data } = await apiClient.patch<TrainerRecord>(`/trainers/${id}`, payload)
      return data
    },
  },

  rooms: {
    async list(params: RoomListParams = {}): Promise<Page<RoomRecord>> {
      const { data } = await apiClient.get<Page<RoomRecord>>('/rooms', { params })
      return data
    },

    async get(id: string): Promise<RoomRecord> {
      const { data } = await apiClient.get<RoomRecord>(`/rooms/${id}`)
      return data
    },

    async create(payload: RoomPayload): Promise<RoomRecord> {
      const { data } = await apiClient.post<RoomRecord>('/rooms', payload)
      return data
    },

    async update(id: string, payload: Partial<RoomPayload>): Promise<RoomRecord> {
      const { data } = await apiClient.patch<RoomRecord>(`/rooms/${id}`, payload)
      return data
    },

    async deactivate(id: string): Promise<RoomRecord> {
      const { data } = await apiClient.delete<RoomRecord>(`/rooms/${id}`)
      return data
    },
  },

  users: {
    async list(params: UserListParams = {}): Promise<Page<UserRecord>> {
      const { data } = await apiClient.get<Page<UserRecord>>('/users', { params })
      return data
    },

    async get(id: string): Promise<UserRecord> {
      const { data } = await apiClient.get<UserRecord>(`/users/${id}`)
      return data
    },

    async create(payload: UserCreatePayload): Promise<UserRecord> {
      const { data } = await apiClient.post<UserRecord>('/users', payload)
      return data
    },

    async update(id: string, payload: UserUpdatePayload): Promise<UserRecord> {
      const { data } = await apiClient.patch<UserRecord>(`/users/${id}`, payload)
      return data
    },

    async deactivate(id: string): Promise<UserRecord> {
      const { data } = await apiClient.delete<UserRecord>(`/users/${id}`)
      return data
    },
  },
}
