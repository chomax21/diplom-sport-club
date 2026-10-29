import {
  Building,
  CalendarDays,
  ChartColumn,
  CreditCard,
  Dumbbell,
  LayoutDashboard,
  Tags,
  UserCog,
  Users,
  Wallet,
} from '@lucide/vue'
import type { Component } from 'vue'

import type { UserRole } from '@/api/types'

export interface NavItem {
  label: string
  to: string
  icon: Component
  exact?: boolean
  roles?: UserRole[]
}

export interface NavSection {
  title: string
  items: NavItem[]
}

export const navigation: NavSection[] = [
  {
    title: 'Обзор',
    items: [
      {
        label: 'Дашборд',
        to: '/app',
        icon: LayoutDashboard,
        exact: true,
      },
      {
        label: 'Расписание',
        to: '/app/schedule',
        icon: CalendarDays,
      },
    ],
  },
  {
    title: 'Клуб',
    items: [
      {
        label: 'Клиенты',
        to: '/app/clients',
        icon: Users,
        roles: ['admin', 'trainer'],
      },
      {
        label: 'Тренеры',
        to: '/app/trainers',
        icon: Dumbbell,
        roles: ['admin'],
      },
      {
        label: 'Залы',
        to: '/app/rooms',
        icon: Building,
        roles: ['admin'],
      },
      {
        label: 'Абонементы',
        to: '/app/memberships',
        icon: CreditCard,
        roles: ['admin', 'client'],
      },
      {
        label: 'Виды абонементов',
        to: '/app/membership-types',
        icon: Tags,
        roles: ['admin'],
      },
      {
        label: 'Платежи',
        to: '/app/payments',
        icon: Wallet,
        roles: ['admin', 'client'],
      },
    ],
  },
  {
    title: 'Управление',
    items: [
      {
        label: 'Пользователи',
        to: '/app/users',
        icon: UserCog,
        roles: ['admin'],
      },
      {
        label: 'Отчёты',
        to: '/app/reports',
        icon: ChartColumn,
        roles: ['admin', 'trainer'],
      },
    ],
  },
]
