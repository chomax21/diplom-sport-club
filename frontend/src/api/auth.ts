import { apiClient } from './client'
import type { CurrentUser, LoginPayload, RegisterPayload, TokenPair } from './types'

export const authApi = {
  async login(payload: LoginPayload): Promise<TokenPair> {
    const { data } = await apiClient.post<TokenPair>('/auth/login', payload)
    return data
  },

  async register(payload: RegisterPayload): Promise<CurrentUser> {
    const { data } = await apiClient.post<CurrentUser>('/auth/register', payload)
    return data
  },

  async me(): Promise<CurrentUser> {
    const { data } = await apiClient.get<CurrentUser>('/auth/me')
    return data
  },
}
