import { useQuery } from '@tanstack/vue-query'

import { getHealth } from '@/api/health'

export const HEALTH_QUERY_KEY = ['health'] as const

export function useHealthQuery() {
  return useQuery({
    queryKey: HEALTH_QUERY_KEY,
    queryFn: getHealth,
    refetchInterval: 30_000,
    retry: 0,
    meta: {
      silent: true,
    },
  })
}
