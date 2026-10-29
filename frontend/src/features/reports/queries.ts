import { keepPreviousData, useQuery } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'

import { reportsApi, type AttendanceReportParams, type ReportPeriodParams } from '@/api/reports'
import { useAuthStore } from '@/stores/auth'

export const reportKeys = {
  reports: ['reports'] as const,
  attendance: (params: AttendanceReportParams) => ['reports', 'attendance', params] as const,
  revenue: (params: ReportPeriodParams) => ['reports', 'revenue', params] as const,
}

function authenticatedEnabled(enabled: MaybeRefOrGetter<boolean>) {
  const auth = useAuthStore()
  return computed(() => auth.isAuthenticated && Boolean(toValue(enabled)))
}

export function useAttendanceReportQuery(
  params: MaybeRefOrGetter<AttendanceReportParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => reportKeys.attendance(toValue(params))),
    queryFn: () => reportsApi.attendance(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
    staleTime: 60_000,
  })
}

export function useRevenueReportQuery(
  params: MaybeRefOrGetter<ReportPeriodParams>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  return useQuery({
    queryKey: computed(() => reportKeys.revenue(toValue(params))),
    queryFn: () => reportsApi.revenue(toValue(params)),
    enabled: authenticatedEnabled(enabled),
    placeholderData: keepPreviousData,
    staleTime: 60_000,
  })
}
