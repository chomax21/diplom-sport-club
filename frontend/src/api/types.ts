export type UserRole = 'admin' | 'trainer' | 'client'

export interface CurrentUser {
  id: string
  email: string
  full_name: string
  phone: string | null
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  phone?: string | null
}

export interface Page<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface HealthResponse {
  status: string
  database: string
  version: string
}
