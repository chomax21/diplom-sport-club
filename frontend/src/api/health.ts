import { apiRootClient } from './client'
import type { HealthResponse } from './types'

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await apiRootClient.get<HealthResponse>('/health')
  return data
}
