import { apiClient } from './client'
import type { Page } from './types'

export type MembershipStatus = 'pending' | 'active' | 'expired' | 'cancelled'
export type PaymentStatus = 'pending' | 'succeeded' | 'failed' | 'refunded'
export type PaymentMethod = 'card' | 'cash' | 'online'

export interface MembershipType {
  id: string
  name: string
  description: string | null
  price: string
  duration_days: number
  visits_limit: number | null
  is_active: boolean
  is_unlimited: boolean
}

export interface MembershipTypeListParams {
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export interface MembershipTypePayload {
  name: string
  description?: string | null
  price: number
  duration_days: number
  visits_limit?: number | null
  is_active?: boolean
}

export interface Membership {
  id: string
  client_id: string
  client_name: string
  membership_type_id: string
  membership_type_name: string
  starts_at: string
  ends_at: string
  visits_left: number | null
  status: MembershipStatus
  created_at: string
}

export interface MembershipListParams {
  status?: MembershipStatus
  client_id?: string
  limit?: number
  offset?: number
}

export interface Payment {
  id: string
  client_id: string
  client_name: string
  membership_id: string | null
  amount: string
  currency: string
  status: PaymentStatus
  provider: string
  external_id: string | null
  payment_method: PaymentMethod
  description: string | null
  paid_at: string | null
  refunded_at: string | null
  created_at: string
}

export interface PaymentListParams {
  status?: PaymentStatus
  client_id?: string
  limit?: number
  offset?: number
}

export interface PurchasePayload {
  membership_type_id: string
  client_id?: string | null
  payment_method: PaymentMethod
}

export interface PurchaseResponse {
  membership: Membership
  payment: Payment
}

export const membershipsApi = {
  async listTypes(params: MembershipTypeListParams = {}): Promise<Page<MembershipType>> {
    const { data } = await apiClient.get<Page<MembershipType>>('/membership-types', { params })
    return data
  },

  async getType(id: string): Promise<MembershipType> {
    const { data } = await apiClient.get<MembershipType>(`/membership-types/${id}`)
    return data
  },

  async createType(payload: MembershipTypePayload): Promise<MembershipType> {
    const { data } = await apiClient.post<MembershipType>('/membership-types', payload)
    return data
  },

  async updateType(id: string, payload: Partial<MembershipTypePayload>): Promise<MembershipType> {
    const { data } = await apiClient.patch<MembershipType>(`/membership-types/${id}`, payload)
    return data
  },

  async deactivateType(id: string): Promise<MembershipType> {
    const { data } = await apiClient.delete<MembershipType>(`/membership-types/${id}`)
    return data
  },

  async listMemberships(params: MembershipListParams = {}): Promise<Page<Membership>> {
    const { data } = await apiClient.get<Page<Membership>>('/memberships', { params })
    return data
  },

  async getMembership(id: string): Promise<Membership> {
    const { data } = await apiClient.get<Membership>(`/memberships/${id}`)
    return data
  },

  async purchase(payload: PurchasePayload): Promise<PurchaseResponse> {
    const { data } = await apiClient.post<PurchaseResponse>('/memberships/purchase', payload)
    return data
  },

  async cancelMembership(id: string): Promise<Membership> {
    const { data } = await apiClient.post<Membership>(`/memberships/${id}/cancel`)
    return data
  },

  async listPayments(params: PaymentListParams = {}): Promise<Page<Payment>> {
    const { data } = await apiClient.get<Page<Payment>>('/payments', { params })
    return data
  },

  async getPayment(id: string): Promise<Payment> {
    const { data } = await apiClient.get<Payment>(`/payments/${id}`)
    return data
  },

  async refundPayment(id: string): Promise<Payment> {
    const { data } = await apiClient.post<Payment>(`/payments/${id}/refund`)
    return data
  },
}
