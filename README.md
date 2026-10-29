# Информационная система спортивного клуба

REST API и адаптивный SPA-интерфейс для информационной системы спортивного
клуба: клиенты, тренеры, абонементы, расписание групповых тренировок, запись
и посещаемость, платежи и отчётность.

## Стек backend

| Компонент | Технология |
| --- | --- |
| Язык | Python 3.12 |
| Web-фреймворк | FastAPI |
| ORM | SQLAlchemy 2.x (async) + asyncpg |
| СУБД | PostgreSQL 16 |
| Миграции | Alembic |
| Валидация и настройки | Pydantic 2 / pydantic-settings |
| Аутентификация | JWT (PyJWT), Argon2 (pwdlib) |
| Контейнеризация | Docker Compose |
| Тесты и линт | pytest, pytest-asyncio, httpx, aiosqlite, ruff |

## Возможности

- **Аутентификация и роли**: регистрация клиента, вход по email и паролю,
  JWT access/refresh-токены, роли `ADMIN`, `TRAINER`, `CLIENT`, блокировка
  учётных записей.
- **Клиенты и тренеры**: профили, привязанные к учётным записям; управление
  администратором.
- **Абонементы**: справочник видов, покупка клиентом или администратором,
  оплата через mock-провайдера или наличными (только администратор), отмена
  и возврат платежа.
- **Расписание**: залы и групповые тренировки, проверка занятости тренера
  и зала, контроль вместимости.
- **Запись и посещаемость**: запись на тренировку и отмена, запрет
  пересекающихся записей, учёт остатка посещений с учётом будущих записей,
  отметка посещения или неявки, списание визита.
- **Платежи**: история платежей, детали, возвраты; провайдер выбирается
  настройкой `PAYMENT_PROVIDER`.
- **Отчёты**: посещаемость (администратор и тренер) и выручка
  (только администратор).
- **Служебное**: health-check с проверкой БД, OpenAPI-схема, Swagger UI.

## Быстрый старт (Docker)

```bash
cp .env.example .env
# при необходимости замените SECRET_KEY: openssl rand -hex 32
docker compose up -d --build
docker compose exec backend python -m app.seed
```

Миграции применяются автоматически при старте контейнера
(`alembic upgrade head` в команде сервиса `backend`).

Проверка работоспособности:

```bash
curl http://localhost:8000/health
# {"status":"ok","database":"ok","version":"1.0.0"}
```

Сервисы:

- API — http://localhost:8000
- Swagger UI — http://localhost:8000/docs
- ReDoc — http://localhost:8000/redoc
- OpenAPI — http://localhost:8000/openapi.json
- Adminer (профиль `tools`) — `docker compose --profile tools up -d`, затем
  http://localhost:8080

Остановка:

```bash
docker compose down          # без удаления данных
docker compose down -v       # вместе с томом PostgreSQL
```

## Демо-данные

Скрипт `app.seed` идемпотентен: повторный запуск не создаёт дубликаты.
Он добавляет виды абонементов, залы, тренировки, абонемент и платёж клиента.

| Роль | Email | Пароль |
| --- | --- | --- |
| Администратор | `admin@sportsclub.ru` | `Admin12345` |
| Тренер | `trainer@sportsclub.ru` | `Trainer12345` |
| Клиент | `client@sportsclub.ru` | `Client12345` |

Пример входа и запроса с токеном:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sportsclub.ru","password":"Admin12345"}' \
  | jq -r .access_token)

curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

В Swagger UI удобнее использовать кнопку **Authorize** и эндпоинт
`POST /api/v1/auth/token` (OAuth2 password flow).

## Локальная разработка

Требуется Python 3.12 и запущенный PostgreSQL (можно только контейнер `db`).

```bash
docker compose up -d db

python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt

cd backend
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Если в системе не установлен пакет `python3-venv` и `venv` создаётся без pip:

```bash
python3 -m venv --without-pip .venv
python3 -m pip --python .venv install -r backend/requirements-dev.txt
```

Настройки читаются из корневого `.env` (пути `../.env` и `.env` относительно
рабочего каталога `backend`). По умолчанию БД доступна на `localhost:5433`.

## Миграции

```bash
cd backend
alembic upgrade head                          # применить все миграции
alembic revision --autogenerate -m "..."      # создать новую миграцию
alembic downgrade -1                          # откатить последнюю
```

## Тесты и качество кода

```bash
cd backend
pytest -q                  # 16 тестов
ruff check .               # линтер
ruff format --check .      # проверка форматирования
```

Тесты используют in-memory SQLite (`aiosqlite`) и не требуют запущенного
PostgreSQL. Покрыты сценарии аутентификации и ролей, покупки и возврата
абонемента, записи на тренировку, лимита мест, пересечений, списания
посещения и отчётов.

## Основные эндпоинты

Все прикладные маршруты имеют префикс `/api/v1`.

| Метод и путь | Назначение | Доступ |
| --- | --- | --- |
| `POST /auth/register` | Регистрация клиента | все |
| `POST /auth/login` | Вход по email и паролю | все |
| `POST /auth/token` | Вход для Swagger (OAuth2) | все |
| `POST /auth/refresh` | Обновление пары токенов | все |
| `GET /auth/me` | Текущий пользователь | авторизованные |
| `GET/POST/PATCH/DELETE /users` | Управление учётными записями | администратор |
| `GET /clients`, `GET /clients/me` | Профили клиентов | staff / клиент |
| `GET/POST/PATCH /trainers` | Профили тренеров | staff / администратор |
| `GET/POST/PATCH /membership-types` | Виды абонементов | все / администратор |
| `POST /memberships/purchase` | Покупка абонемента | клиент / администратор |
| `POST /memberships/{id}/cancel` | Отмена абонемента | клиент / администратор |
| `GET/POST/PATCH/DELETE /rooms` | Залы | все / администратор |
| `GET/POST/PATCH /sessions` | Расписание тренировок | все / staff |
| `GET /sessions/{id}/enrollments` | Записи на тренировку | staff |
| `POST /sessions/{id}/enrollments` | Запись на тренировку | клиент / администратор |
| `POST /enrollments/{id}/attend` | Отметить посещение | staff |
| `POST /enrollments/{id}/no-show` | Отметить неявку | staff |
| `GET /payments` | История платежей | клиент / администратор |
| `POST /payments/{id}/refund` | Возврат платежа | администратор |
| `GET /reports/attendance` | Отчёт по посещаемости | staff |
| `GET /reports/revenue` | Отчёт по выручке | администратор |
| `GET /health` | Проверка API и БД | без префикса |

## Бизнес-правила

- Записаться можно только при наличии действующего абонемента на дату
  тренировки.
- Число активных будущих записей не может превышать остаток посещений
  абонемента.
- Нельзя записаться на две пересекающиеся по времени тренировки.
- Вместимость тренировки не может превышать вместимость зала; тренер и зал
  не могут быть заняты в одно время.
- Отметка посещения списывает один визит, неявка визит не списывает.
- Возврат возможен только по успешному платежу и только если по абонементу
  ещё нет посещений; возврат отменяет абонемент.

## Платёжный провайдер

По умолчанию используется `MockPaymentProvider`: платежи всегда успешны,
но проходят полный жизненный цикл и сохраняют «сырой» ответ в
`Payment.extra`. Наличные оформляются администратором вручную.

Чтобы подключить реальный шлюз (ЮKassa, CloudPayments и т.п.), нужно:

1. Реализовать интерфейс `PaymentProvider` из
   `app/integrations/payments/base.py`.
2. Зарегистрировать класс в `_PROVIDERS`
   (`app/integrations/payments/factory.py`).
3. Указать имя провайдера в `PAYMENT_PROVIDER`.

## Переменные окружения

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `POSTGRES_DB` | `sports_club` | Имя базы данных |
| `POSTGRES_USER` | `sports_club` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | `sports_club` | Пароль PostgreSQL |
| `POSTGRES_PORT` | `5433` | Порт PostgreSQL на хосте |
| `BACKEND_PORT` | `8000` | Порт API на хосте |
| `ADMINER_PORT` | `8080` | Порт Adminer на хосте |
| `DATABASE_URL` | `postgresql+asyncpg://...@localhost:5433/sports_club` | Строка подключения |
| `ENVIRONMENT` | `development` | Окружение; в `production` требуется стойкий `SECRET_KEY` |
| `DEBUG` | `false` | Режим отладки |
| `SECRET_KEY` | — | Ключ подписи JWT, обязателен в production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access-токена |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Время жизни refresh-токена |
| `CORS_ORIGINS` | `["http://localhost:5173", ...]` | Разрешённые Origin'ы (JSON-массив) |
| `PAYMENT_PROVIDER` | `mock` | Платёжный провайдер |
| `DEFAULT_CURRENCY` | `RUB` | Валюта платежей |

Файл `.env` не попадает в git (см. `.gitignore`); шаблон — `.env.example`.

## Структура проекта

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/       # HTTP-слой: роутеры и зависимости
│   │   ├── core/                   # настройки, БД, безопасность, ошибки
│   │   ├── integrations/payments/  # PaymentProvider и mock-реализация
│   │   ├── models/                 # SQLAlchemy-модели
│   │   ├── schemas/                # Pydantic-схемы
│   │   ├── services/               # бизнес-логика
│   │   ├── main.py                 # сборка FastAPI-приложения
│   │   └── seed.py                 # демо-данные
│   ├── alembic/                    # миграции
│   ├── tests/                      # pytest-тесты
│   ├── Dockerfile
│   ├── pyproject.toml              # настройки ruff и pytest
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios-клиент, auth, расписание, типы, ошибки
│   │   ├── app/                    # Pinia и QueryClient
│   │   ├── components/             # layout, auth-shell, feedback и UI-кит
│   │   ├── composables/            # общие composables
│   │   ├── features/schedule/      # карточки, форма тренировки, queries
│   │   ├── lib/                    # роли, права, даты, cn и утилиты
│   │   ├── router/                 # маршруты, навигация, meta и guard'ы
│   │   ├── stores/                 # Pinia: auth и toasts
│   │   ├── views/                  # landing, вход, панель, расписание и UI-кит
│   │   └── assets/                 # Tailwind и дизайн-токены
│   ├── .env.example                # VITE_API_URL
│   ├── README.md
│   └── package.json
├── docker-compose.yml
├── .env.example
├── README.md
└── ROADMAP.md
```

## Доменная модель

`User` — учётная запись с ролью; `ClientProfile` и `TrainerProfile` —
профили, связанные с пользователем. `MembershipType` описывает вид
абонемента, `Membership` — оформленный абонемент клиента. `Room` и
`TrainingSession` образуют расписание, `Enrollment` — запись клиента на
тренировку, `Attendance` — факт посещения. `Payment` хранит платёж, его
статус, провайдера и внешний идентификатор.

## Frontend

Адаптивный SPA на Vue 3 + TypeScript + Vite. Завершены этапы F0–F7:
layout и навигация, API-клиент с обработкой ошибок, TanStack Query,
toast-уведомления, вход и регистрация, восстановление сессии, автоматическое
обновление токена и ролевые guard'ы. Добавлен UI-кит и рабочий раздел
расписания: фильтры, карточки, детальная страница, создание и отмена
тренировок, запись клиента, список записавшихся и отметки посещаемости.
Раздел абонементов включает каталог, покупку через mock-провайдера, отмену,
историю платежей, детали операции и возврат с отменой абонемента. Админ
управляет видами абонементов на отдельной странице. Справочники включают
карточки клиентов с поиском и редактированием, профили тренеров, CRUD залов
и управление пользователями с ролями и блокировкой доступа. Дашборды
адаптированы под роль, а отчёты по посещаемости и выручке содержат фильтры
периода, графики Chart.js, табличные дубли, пустые состояния и экспорт CSV.

После запуска доступны демо-аккаунты из раздела «Демо-данные»; меню и
маршруты автоматически ограничиваются ролью пользователя. Расписание
доступно по адресу http://localhost:5173/app/schedule, абонементы —
http://localhost:5173/app/memberships, платежи —
http://localhost:5173/app/payments, клиенты —
http://localhost:5173/app/clients, тренеры —
http://localhost:5173/app/trainers, залы — http://localhost:5173/app/rooms,
пользователи — http://localhost:5173/app/users, отчёты —
http://localhost:5173/app/reports, страница UI-кита — администратору по
адресу http://localhost:5173/app/ui-kit.

```bash
cd frontend
npm install
cp .env.example .env   # при необходимости измените VITE_API_URL
npm run dev
```

Приложение откроется на http://localhost:5173. Подробности —
[frontend/README.md](frontend/README.md).

## План разработки

Поэтапный план фронтенда, критерии готовности и журнал прогресса —
[ROADMAP.md](ROADMAP.md).
