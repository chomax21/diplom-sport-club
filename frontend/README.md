# Frontend — информационная система спортивного клуба

Адаптивный SPA-интерфейс для API спортивного клуба.

## Стек

- Vue 3 + TypeScript + Vite
- Vue Router, Pinia
- TanStack Query (`@tanstack/vue-query`)
- Axios
- Tailwind CSS 4 + Headless UI Vue
- VeeValidate + Zod
- Chart.js + vue-chartjs
- Vitest + Vue Testing Library
- Playwright для проверки адаптивности и сценариев

## Запуск

```bash
npm install
cp .env.example .env   # при необходимости измените VITE_API_URL
npm run dev
```

Приложение откроется на http://localhost:5173. По умолчанию API доступен на
`http://localhost:8000/api/v1`; если `.env` не создан, используется это же
значение.

## Что уже реализовано

- Адаптивный layout: sidebar на десктопе, drawer на мобильных.
- Header с названием раздела, профилем пользователя и индикатором доступности API.
- Страницы входа и регистрации с валидацией VeeValidate + Zod.
- Хранение access-токена в памяти, refresh-токена в localStorage.
- Восстановление сессии после перезагрузки и single-flight обновление токена при 401.
- Защищённые маршруты, ролевые guard'ы, страница 403 и меню по роли.
- Профиль пользователя, выход и очистка кеша TanStack Query.
- Axios-клиент с базовым URL, заголовком `Authorization` и типизированными ошибками.
- TanStack Query с глобальным обработчиком ошибок.
- Toast-уведомления, error boundary и страница 404.
- Проверка `GET /health` и отображение статуса API.

Рабочие экраны появятся на этапах F3–F7. Демо-аккаунты для проверки ролей
описаны в корневом [README.md](../README.md#демо-данные).

## Команды

```bash
npm run dev          # dev-сервер
npm run build        # type-check + production-сборка
npm run preview      # просмотр production-сборки
npm run test:unit    # Vitest в watch-режиме
npm run test:unit:run
npm run lint         # oxlint + eslint с автоисправлением
npm run format       # Prettier
npm run format:check
```

Для проверок в браузере:

```bash
npx playwright install chromium
```

## Структура

```text
src/
├── api/            # клиент, auth, сессия, типы, ошибки, health
├── app/            # Pinia и QueryClient
├── components/
│   ├── feedback/   # toasts, error boundary, статус API
│   └── layout/     # AppLayout, AppSidebar, AppHeader, AuthShell
├── composables/    # общие composables
├── lib/            # роли, права и общие утилиты
├── router/         # маршруты, meta-типы, навигация и guard'ы
├── stores/         # Pinia: auth и toasts
├── views/          # landing, вход, регистрация, 403, страницы панели
├── assets/         # глобальные стили и дизайн-токены
└── main.ts
```

План этапов и журнал прогресса — в корневом [ROADMAP.md](../ROADMAP.md).
