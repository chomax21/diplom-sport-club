export type BadgeTone = 'neutral' | 'brand' | 'success' | 'warning' | 'danger' | 'info' | 'violet'

export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

export interface TableColumn {
  key: string
  label: string
  align?: 'left' | 'center' | 'right'
  headerClass?: string
  cellClass?: string
  hideOnMobile?: boolean
  hideOnDesktop?: boolean
}

export type TableRow = Record<string, unknown>
