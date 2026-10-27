import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import HomeView from '@/views/HomeView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import DashboardView from '@/views/app/DashboardView.vue'
import PlaceholderView from '@/views/app/PlaceholderView.vue'

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
      path: '/app',
      component: AppLayout,
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
          component: PlaceholderView,
          meta: {
            title: 'Расписание',
            description: 'Групповые тренировки, фильтры по дате, залу и тренеру, запись клиентов.',
            stage: 'F4',
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
          },
        },
        {
          path: 'profile',
          name: 'profile',
          component: PlaceholderView,
          meta: {
            title: 'Профиль',
            description: 'Личные данные, контакты и настройки учётной записи.',
            stage: 'F2',
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

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — СпортКлуб` : 'СпортКлуб'
})

export default router
