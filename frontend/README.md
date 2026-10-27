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
- Header с названием раздела, профилем и индикатором доступности API.
- Axios-клиент с базовым URL, заголовком `Authorization` и типизированными ошибками.
- TanStack Query с глобальным обработчиком ошибок.
- Toast-уведомления.
- Error boundary и страница 404.
- Проверка `GET /health` и отображение статуса API.

Авторизация и рабочие экраны появятся на этапах F2–F7.

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
├── api/            # клиент, типы, ошибки, health
├── app/            # Pinia и QueryClient
├── components/
│   ├── feedback/   # toasts, error boundary, статус API
│   └── layout/     # AppLayout, AppSidebar, AppHeader
├── composables/    # общие composables
├── router/         # маршруты, навигация и meta-типы
├── stores/         # Pinia stores
├── views/          # страницы и placeholder-экраны
├── assets/         # глобальные стили и дизайн-токены
└── main.ts
```

План этапов и журнал прогресса — в корневом [ROADMAP.md](../ROADMAP.md).
