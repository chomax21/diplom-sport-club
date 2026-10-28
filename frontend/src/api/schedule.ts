import { apiClient } from './client'
import type { Page } from './types'

export type EnrollmentStatus = 'active' | 'cancelled' | 'attended' | 'no_show'

export interface TrainingSession {
  id: string
  title: string
  trainer_id: string
  trainer_name: string
  room_id: string
  room_name: string
  starts_at: string
  ends_at: string
  capacity: number
  enrolled_count: number
  available_slots: number
  description: string | null
  is_cancelled: boolean
  created_at: string
}

export interface TrainingSessionListParams {
  date_from?: string
  date_to?: string
  trainer_id?: string
  room_id?: string
  include_cancelled?: boolean
  search?: string
  limit?: number
  offset?: number
}

export interface TrainingSessionPayload {
  title: string
  trainer_id?: string | null
  room_id: string
  starts_at: string
  ends_at: string
  capacity: number
  description?: string | null
}

export interface Enrollment {
  id: string
  session_id: string
  client_id: string
  client_name: string
  client_phone: string | null
  client_email: string
  status: EnrollmentStatus
  is_attended: boolean
  created_at: string
  cancelled_at: string | null
}

export interface EnrollmentListParams {
  include_cancelled?: boolean
  only_upcoming?: boolean
  limit?: number
  offset?: number
}

export interface Room {
  id: string
  name: string
  capacity: number
  description: string | null
  is_active: boolean
}

export interface Trainer {
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

export interface Client {
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

export const scheduleApi = {
  async listSessions(params: TrainingSessionListParams = {}): Promise<Page<TrainingSession>> {
    const { data } = await apiClient.get<Page<TrainingSession>>('/sessions', { params })
    return data
  },

  async getSession(id: string): Promise<TrainingSession> {
    const { data } = await apiClient.get<TrainingSession>(`/sessions/${id}`)
    return data
  },

  async createSession(payload: TrainingSessionPayload): Promise<TrainingSession> {
    const { data } = await apiClient.post<TrainingSession>('/sessions', payload)
    return data
  },

  async updateSession(
    id: string,
    payload: Partial<TrainingSessionPayload>,
  ): Promise<TrainingSession> {
    const { data } = await apiClient.patch<TrainingSession>(`/sessions/${id}`, payload)
    return data
  },

  async cancelSession(id: string): Promise<TrainingSession> {
    const { data } = await apiClient.post<TrainingSession>(`/sessions/${id}/cancel`)
    return data
  },

  async listSessionEnrollments(
    sessionId: string,
    params: EnrollmentListParams = {},
  ): Promise<Page<Enrollment>> {
    const { data } = await apiClient.get<Page<Enrollment>>(`/sessions/${sessionId}/enrollments`, {
      params,
    })
    return data
  },

  async enroll(sessionId: string, clientId?: string): Promise<Enrollment> {
    const { data } = await apiClient.post<Enrollment>(`/sessions/${sessionId}/enrollments`, {
      client_id: clientId ?? null,
    })
    return data
  },

  async myEnrollments(params: EnrollmentListParams = {}): Promise<Page<Enrollment>> {
    const { data } = await apiClient.get<Page<Enrollment>>('/enrollments/my', { params })
    return data
  },

  async cancelEnrollment(id: string): Promise<Enrollment> {
    const { data } = await apiClient.delete<Enrollment>(`/enrollments/${id}`)
    return data
  },

  async markAttendance(id: string): Promise<Enrollment> {
    const { data } = await apiClient.post<Enrollment>(`/enrollments/${id}/attend`)
    return data
  },

  async markNoShow(id: string): Promise<Enrollment> {
    const { data } = await apiClient.post<Enrollment>(`/enrollments/${id}/no-show`)
    return data
  },

  async listRooms(
    params: { include_inactive?: boolean; limit?: number } = {},
  ): Promise<Page<Room>> {
    const { data } = await apiClient.get<Page<Room>>('/rooms', { params })
    return data
  },

  async listTrainers(params: { search?: string; limit?: number } = {}): Promise<Page<Trainer>> {
    const { data } = await apiClient.get<Page<Trainer>>('/trainers', { params })
    return data
  },

  async myTrainer(): Promise<Trainer> {
    const { data } = await apiClient.get<Trainer>('/trainers/me')
    return data
  },

  async listClients(params: { search?: string; limit?: number } = {}): Promise<Page<Client>> {
    const { data } = await apiClient.get<Page<Client>>('/clients', { params })
    return data
  },
}
