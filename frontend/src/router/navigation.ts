import {
  Building,
  CalendarDays,
  ChartColumn,
  CreditCard,
  Dumbbell,
  LayoutDashboard,
  UserCog,
  Users,
  Wallet,
} from '@lucide/vue'
import type { Component } from 'vue'

export interface NavItem {
  label: string
  to: string
  icon: Component
  exact?: boolean
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
      },
      {
        label: 'Тренеры',
        to: '/app/trainers',
        icon: Dumbbell,
      },
      {
        label: 'Залы',
        to: '/app/rooms',
        icon: Building,
      },
      {
        label: 'Абонементы',
        to: '/app/memberships',
        icon: CreditCard,
      },
      {
        label: 'Платежи',
        to: '/app/payments',
        icon: Wallet,
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
      },
      {
        label: 'Отчёты',
        to: '/app/reports',
        icon: ChartColumn,
      },
    ],
  },
]
