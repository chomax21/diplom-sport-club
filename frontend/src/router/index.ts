import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import ForbiddenView from '@/views/ForbiddenView.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/app/DashboardView.vue'
import PlaceholderView from '@/views/app/PlaceholderView.vue'
import ProfileView from '@/views/app/ProfileView.vue'
import { installAuthGuards } from './guards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: HomeView,
      meta: {
        title: 'Главная',
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        title: 'Вход',
        guestOnly: true,
      },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        title: 'Регистрация',
        guestOnly: true,
      },
    },
    {
      path: '/forbidden',
      name: 'forbidden',
      component: ForbiddenView,
      meta: {
        title: 'Нет доступа',
      },
    },
    {
      path: '/app',
      component: AppLayout,
      meta: {
        requiresAuth: true,
      },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: DashboardView,
          meta: {
            title: 'Дашборд',
            description: 'Обзор клуба и состояние системы',
          },
        },
        {
          path: 'schedule',
          name: 'schedule',
          component: () => import('@/views/app/ScheduleView.vue'),
          meta: {
            title: 'Расписание',
            description: 'Групповые тренировки, фильтры по дате, залу и тренеру, запись клиентов.',
          },
        },
        {
          path: 'schedule/:id',
          name: 'session-detail',
          component: () => import('@/views/app/SessionDetailView.vue'),
          meta: {
            title: 'Тренировка',
            description: 'Детали тренировки, запись и посещаемость.',
          },
        },
        {
          path: 'clients',
          name: 'clients',
          component: PlaceholderView,
          meta: {
            title: 'Клиенты',
            description: 'Список клиентов, профили, поиск и редактирование данных.',
            stage: 'F6',
            roles: ['admin', 'trainer'],
          },
        },
        {
          path: 'trainers',
          name: 'trainers',
          component: PlaceholderView,
          meta: {
            title: 'Тренеры',
            description: 'Профили тренеров, специализация и управление расписанием.',
            stage: 'F6',
            roles: ['admin'],
          },
        },
        {
          path: 'rooms',
          name: 'rooms',
          component: PlaceholderView,
          meta: {
            title: 'Залы',
            description: 'Помещения клуба, вместимость и доступность для тренировок.',
            stage: 'F6',
            roles: ['admin'],
          },
        },
        {
          path: 'memberships',
          name: 'memberships',
          component: PlaceholderView,
          meta: {
            title: 'Абонементы',
            description: 'Виды абонементов, оформление, продление и отмена.',
            stage: 'F5',
            roles: ['admin', 'client'],
          },
        },
        {
          path: 'payments',
          name: 'payments',
          component: PlaceholderView,
          meta: {
            title: 'Платежи',
            description: 'История платежей, статусы, возвраты и детали операций.',
            stage: 'F5',
            roles: ['admin', 'client'],
          },
        },
        {
          path: 'users',
          name: 'users',
          component: PlaceholderView,
          meta: {
            title: 'Пользователи',
            description: 'Учётные записи, роли и блокировка доступа.',
            stage: 'F6',
            roles: ['admin'],
          },
        },
        {
          path: 'reports',
          name: 'reports',
          component: PlaceholderView,
          meta: {
            title: 'Отчёты',
            description: 'Посещаемость, выручка и сводная статистика клуба.',
            stage: 'F7',
            roles: ['admin', 'trainer'],
          },
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfileView,
          meta: {
            title: 'Профиль',
            description: 'Личные данные, контакты и настройки учётной записи.',
          },
        },
        {
          path: 'ui-kit',
          name: 'ui-kit',
          component: () => import('@/views/app/UiKitView.vue'),
          meta: {
            title: 'UI-кит',
            description: 'Компоненты интерфейса и состояния для проверки адаптивности.',
            stage: 'F3',
            roles: ['admin'],
          },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: {
        title: 'Страница не найдена',
      },
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

installAuthGuards(router)

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — СпортКлуб` : 'СпортКлуб'
})

export default router
