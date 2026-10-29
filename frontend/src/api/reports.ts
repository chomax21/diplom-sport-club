import { apiClient } from './client'

export interface ReportPeriodParams {
  date_from?: string
  date_to?: string
}

export interface AttendanceReportParams extends ReportPeriodParams {
  trainer_id?: string
}

export interface DailyAttendance {
  day: string
  enrollments: number
  attended: number
}

export interface AttendanceReport {
  date_from: string
  date_to: string
  sessions_count: number
  enrollments_count: number
  attended_count: number
  no_show_count: number
  attendance_rate: number
  by_day: DailyAttendance[]
}

export interface RevenueByMembershipType {
  membership_type_name: string
  payments_count: number
  amount: string
}

export interface DailyRevenue {
  day: string
  payments_count: number
  amount: string
}

export interface RevenueReport {
  date_from: string
  date_to: string
  payments_count: number
  total_amount: string
  refunded_amount: string
  by_membership_type: RevenueByMembershipType[]
  by_day: DailyRevenue[]
}

export const reportsApi = {
  async attendance(params: AttendanceReportParams = {}): Promise<AttendanceReport> {
    const { data } = await apiClient.get<AttendanceReport>('/reports/attendance', { params })
    return data
  },

  async revenue(params: ReportPeriodParams = {}): Promise<RevenueReport> {
    const { data } = await apiClient.get<RevenueReport>('/reports/revenue', { params })
    return data
  },
}
