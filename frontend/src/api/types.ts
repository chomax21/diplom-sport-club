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
