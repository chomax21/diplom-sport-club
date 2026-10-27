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

## Запуск

```bash
npm install
cp .env.example .env   # при необходимости измените VITE_API_URL
npm run dev
```

Приложение откроется на http://localhost:5173. По умолчанию API доступен на
`http://localhost:8000/api/v1`; если `.env` не создан, используется это же
значение.

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

## Структура

```text
src/
├── api/          # HTTP-клиент и эндпоинты
├── components/   # UI-компоненты и layout
├── composables/  # общие composables
├── router/       # маршруты и guard'ы
├── stores/       # Pinia
├── views/        # страницы
├── assets/       # глобальные стили и дизайн-токены
└── main.ts
```

План этапов и журнал прогресса — в корневом [ROADMAP.md](../ROADMAP.md).
