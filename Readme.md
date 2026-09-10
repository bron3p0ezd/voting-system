# Voting System

Монорепозиторий сервиса анонимных опросов для национальной компании, проводящей голосования во время телевизионной рекламы.

## Описание

Компания размещает минутные ролики на крупнейших телеканалах. Каждый ролик показывает один вопрос и QR-код или ссылку на голосование. Вопрос может предусматривать выбор одного варианта, нескольких вариантов или A/B. Аудитория одного ролика — примерно 100 миллионов человек; голосование происходит в течение минуты.

Сервис должен позволять:

- Зрителю проголосовать анонимно, без регистрации.
- Ограничить повторное голосование на базовом уровне, достаточном для обычного пользователя, без обещания полной защиты от обхода.
- Администратору создавать опросы и просматривать обезличенные результаты.

## Технологии и причины выбора

| Часть | Технологии | Почему выбраны |
|---|---|---|
| Backend | Python 3.13, FastAPI, Pydantic | FastAPI даёт типизированные HTTP-контракты и автоматическую OpenAPI-документацию, а Pydantic валидирует входные данные до выполнения бизнес-логики. |
| Данные | PostgreSQL, Redis, SQLAlchemy 2.0 async, asyncpg, Alembic | PostgreSQL поддерживает транзакции и уникальные ограничения для конкурентно-безопасного базового учёта одного голоса; Redis кэширует публичные данные опроса, а SQLAlchemy и Alembic отделяют доступ к данным и версионируют схему. |
| Frontend | React, TypeScript, Vite, Tailwind CSS | React подходит для интерактивных форм голосования и администрирования, TypeScript описывает контракты API на клиенте, Vite упрощает локальную разработку и сборку, Tailwind CSS — единообразное оформление без отдельного набора CSS-компонентов. |
| Развёртывание | Docker Compose, nginx | Compose воспроизводимо поднимает локальные PostgreSQL, API и интерфейс; nginx отдаёт собранный frontend и проксирует запросы `/api/` к backend через единый адрес. |

## Структура

```text
voting-system/
├── AGENTS.md       # Общие правила работы агентов
├── README.md       # Описание проекта и задания
├── backend/        # API, бизнес-логика и хранение данных
├── frontend/       # Пользовательский интерфейс голосования и администрирования
└── web-server/     # Конфигурация nginx для раздачи frontend и проксирования API
```

## Туториал: запуск через Docker Compose

```powershell
docker compose up --build -d
docker compose ps
```

Access-log успешных HTTP-запросов отключён в production-запуске Uvicorn, чтобы
синхронный вывод в stdout не ограничивал пропускную способность при высокой
нагрузке. Ошибки приложения и сервера продолжают журналироваться.

| Назначение | Адрес |
|---|---|
| Интерфейс | `http://127.0.0.1/` |
| Администрирование | `http://127.0.0.1/admin/polls` |
| API через nginx | `http://127.0.0.1/api/v1` |
| Health check | `http://127.0.0.1/api/health` |
| OpenAPI | `http://127.0.0.1/docs` |

## Туториал: ручной запуск

Для разработки без контейнеров нужны Python 3.13, PostgreSQL и Node.js 22 или
новее. Откройте два PowerShell-окна: одно для backend, другое для frontend.

### 1. Подготовьте PostgreSQL, Redis и backend

Создайте пустую базу PostgreSQL, пользователя с правами на неё и запустите Redis.
Затем создайте
`backend/src/envs/.env` в UTF-8 без BOM. Этот файл содержит локальные секреты и
не должен попадать в Git. Все перечисленные параметры обязательны:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=voting
DB_PASS=replace-with-local-password
DB_NAME=voting
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
POLL_CACHE_TTL_SECONDS=60
ADMIN_JWT_SECRET=replace-with-random-local-secret
ADMIN_LOGIN=admin
ADMIN_PASSWORD=replace-with-local-admin-password
PARTICIPANT_JWT_SECRET=replace-with-random-local-secret
JWT_ALG=HS256
TEST_DB_HOST=127.0.0.1
TEST_DB_PORT=5432
TEST_DB_USER=voting
TEST_DB_PASS=replace-with-local-password
TEST_DB_NAME=voting_test
TEST_ADMIN_JWT_SECRET=replace-with-random-local-test-secret
TEST_PARTICIPANT_JWT_SECRET=replace-with-random-local-test-secret
TEST_JWT_ALG=HS256
ALLOW_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
DOCS_URL_ENABLED=/docs
REDOC_URL_ENABLED=/redoc
OPENAPI_URL_ENABLED=/openapi.json
```

Из каталога `backend` установите зависимости, примените миграции и запустите
сервер:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m alembic upgrade head
Set-Location src
..\.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Проверьте запуск запросом к `http://127.0.0.1:8000/api/health`. При включённых
в файле окружения настройках OpenAPI доступна по `http://127.0.0.1:8000/docs`.

### 2. Запустите frontend

Во втором PowerShell-окне выполните:

```powershell
Set-Location frontend
npm ci
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
npm run dev
```

Откройте адрес, который напечатает Vite (по умолчанию
`http://localhost:5173`). Административная страница находится по пути
`/admin/polls`; публичная страница опроса — по пути `/poll/<poll_id>/vote`.
Перед изменением постоянной конфигурации frontend сверяйтесь с
`frontend/.env.example`; переменные с префиксом `VITE_` не подходят для
секретов.

В Docker Compose для локальной демонстрации заданы `ADMIN_LOGIN=admin` и
`ADMIN_PASSWORD=admin`; замените их перед любым внешним развёртыванием.


## Public API

## Получить опрос

```http
GET /api/v1/polls/{poll_id}
```

### Path parameters

| Параметр | Тип | Описание |
|---|---|---|
| `poll_id` | UUID | Идентификатор опроса |

### Response

`200 OK`

```json
{
  "id": "UUID",
  "question": "string",
  "selection_type": "single | multiple",
  "min_selections": "integer",
  "max_selections": "integer",
  "starts_at": "datetime",
  "ends_at": "datetime",
  "options": [
    {
      "id": "UUID",
      "text": "string",
      "position": "integer"
    }
  ]
}
```

При первом запросе без корректной cookie сервер устанавливает cookie `participant_token`.
Её значение — подписанный JWT с payload вида:

```json
{
  "sub": "7cc7444e-9809-4bc4-bc04-6ca1f7522e77"
}
```

`sub` — случайный UUID технического участника, а не идентификатор пользователя.

### Status codes

| Код | Описание |
|---|---|
| `200` | Опрос найден |
| `404` | Опрос не существует |
| `410` | Опрос удалён или недоступен публично |

## Отправить голос

```http
POST /api/v1/polls/{poll_id}/votes
```
Для запроса требуется ранее установленная cookie `participant_token`.

### Path parameters

| Параметр | Тип | Описание |
|---|---|---|
| `poll_id` | UUID | Идентификатор опроса |

### Request

```json
{
  "option_ids": [
    "UUID"
  ]
}
```

### Поля

| Поле | Тип | Описание |
|---|---|---|
| `option_ids` | list(UUID) | Выбранные варианты ответа |

`option_ids` должны быть уникальными. Все варианты должны принадлежать указанному опросу.

Для `single`: ```option_ids.length = 1```

Для `multiple`:  ```min_selections <= option_ids.length <= max_selections```

### Response

`201 Created`

```json
{
  "poll_id": "UUID",
  "counted_at": "datetime"
}
```

`201 Created` возвращается только после устойчивого сохранения голоса.
Параметры опроса и допустимые варианты для этой проверки берутся из Redis-кэша;
при промахе они загружаются из PostgreSQL и кэшируются. Сама запись выполняется
одной PostgreSQL-командой: она повторно проверяет принадлежность вариантов,
создаёт голос через `INSERT ... ON CONFLICT DO NOTHING` и добавляет выбранные
варианты. Затем сервис выполняет commit и только после его успешного завершения
возвращает `201`.

### Status codes

| Код | Описание |
|---|---|
| `201` | Голос учтён |
| `400` | Некорректный выбор вариантов |
| `401` | Cookie отсутствует или недействительна; обновите страницу для получения новой cookie |
| `404` | Опрос не найден |
| `409` | Участник уже проголосовал |
| `410` | Голосование ещё не началось или уже завершилось |

## Тестирование

В backend добавлены `pytest`, `pytest-asyncio` и Locust. После установки
зависимостей запускайте pytest из каталога `backend`:

```powershell
.\.venv\Scripts\python -m pytest -q
```

### Нагрузка 100 000 голосов за минуту

`src/tests/performance/test_voting_load_profile.py` запускает Locust как pytest-тест
только при явно заданном целевом стенде. Это предотвращает случайную генерацию
нагрузки на локальный или внешний адрес. Сценарий каждого виртуального участника
раз в секунду открывает `GET /api/v1/polls/{poll_id}`, получает новую
`participant_token`, а затем отправляет `POST /api/v1/polls/{poll_id}/votes` с
одним вариантом. Поэтому профиль `sustained` с 1 667 пользователями создаёт не
менее 100 000 успешных голосов за минуту. Профиль `peak` удерживает минимум
8 000 голосов/с как нижнюю границу кратковременного телевизионного пика.

Перед запуском создайте отдельный активный single-choice опрос и возьмите UUID
опроса и его варианта. Нагрузочный стенд должен использовать отдельную тестовую
PostgreSQL-базу: сценарий создаёт до 1,2 млн голосов за один запуск.

```powershell
Set-Location backend
$env:VOTING_LOAD_BASE_URL = "http://127.0.0.1"
$env:VOTING_POLL_ID = "UUID-опроса"
$env:VOTING_OPTION_ID = "UUID-варианта"
.\.venv\Scripts\python -m pytest src/tests/performance/test_voting_load_profile.py -m performance -q
```

По умолчанию запускается `sustained`. Он измеряет полные 60 секунд после
завершения запуска всех users и завершается с ошибкой, если скорость успешных
голосов ниже 1 667/с, p95 любого public endpoint выше 500 мс или error rate
выше 0,1%. Cookie передаётся нагрузочным клиентом явно: production-cookie имеет
флаг `Secure`, а локальный HTTP-стенд иначе её не отправляет.

Для проверки пика используйте отдельный прогон:

```powershell
$env:VOTING_LOAD_PROFILE = "peak"
.\.venv\Scripts\python -m pytest src/tests/performance/test_voting_load_profile.py -m performance -q
```

Результат одного запуска не является заявлением о производительности. Для
подтверждения характеристики фиксируйте вместе с итогом версию образа, число
uvicorn workers, конфигурацию PostgreSQL и connection pool, CPU/RAM, сетевую
топологию, длительность прогрева и вывод Locust. Если один генератор нагрузки
не удерживает 1 667 голосов/с или peak-профиль 8 000 голосов/с, запускайте
Locust в distributed-режиме с отдельными workers и не интерпретируйте ограничение
генератора как пропускную способность сервиса.

## Admin API

Административные endpoint’ы требуют заголовок `Authorization: Bearer <access_token>`.
Токен содержит роль `admin`, подписывается отдельным `ADMIN_JWT_SECRET` и действует
60 минут — это фиксированное правило `AdminTokenPolicy`. Публичные endpoint’ы
опросов и голосования токен администратора не требуют.

## Войти как администратор

```http
POST /api/v1/auth/admin/login
Content-Type: application/json
```

```json
{
  "login": "admin",
  "password": "string"
}
```

При корректных учётных данных из `ADMIN_LOGIN` и `ADMIN_PASSWORD` endpoint вернёт:

```json
{
  "access_token": "JWT",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Неверные учётные данные возвращают `401 Unauthorized`; отсутствие, истечение или
неверная роль токена при обращении к административным endpoint’ам также возвращают `401`.

## Создать опрос

```http
POST /api/v1/admin/polls
```

### Request

```json
{
  "question": "string",
  "selection_type": "single | multiple",
  "min_selections": "integer",
  "max_selections": "integer",
  "starts_at": "datetime",
  "ends_at": "datetime",
  "options": [
    "string"
  ]
}
```

### Поля

| Поле | Тип | Описание |
|---|---|---|
| `question` | string | Текст вопроса |
| `selection_type` | `single \| multiple` | Тип выбора |
| `min_selections` | integer | Минимальное число выбранных вариантов |
| `max_selections` | integer | Максимальное число выбранных вариантов |
| `starts_at` | datetime | Начало голосования |
| `ends_at` | datetime | Завершение голосования |
| `options` | string[] | Варианты ответа |

### Правила валидации

Для `single`:

```text
min_selections = 1
max_selections = 1
```

Для `multiple`:

```text
min_selections > 0
max_selections > 0
min_selections <= max_selections
max_selections <= options.length
```

Дополнительно:

```text
options.length >= 2
ends_at > starts_at
```

### Response

`201 Created`

```json
{
  "id": "UUID",
  "question": "string",
  "selection_type": "single | multiple",
  "min_selections": "integer",
  "max_selections": "integer",
  "starts_at": "datetime",
  "ends_at": "datetime",
  "options": [
    {
      "id": "UUID",
      "text": "string",
      "position": "integer"
    }
  ]
}
```

### Status codes

| Код | Описание |
|---|---|
| `201` | Опрос создан |
| `400` | Ошибка валидации |
| `401` | Требуется авторизация администратора |
| `422` | Ошибка структурной валидации запроса |

## Получить список опросов

```http
GET /api/v1/admin/polls
```

Административный endpoint возвращает все опросы, включая ещё не открытые и уже завершённые.

### Response

`200 OK`

```json
[
  {
    "id": "UUID",
    "question": "string",
    "selection_type": "single | multiple",
    "min_selections": "integer",
    "max_selections": "integer",
    "starts_at": "datetime",
    "ends_at": "datetime",
    "options": [
      {
        "id": "UUID",
        "text": "string",
        "position": "integer"
      }
    ]
  }
]
```

### Status codes

| Код | Описание |
|---|---|
| `200` | Список опросов получен |
| `401` | Требуется авторизация администратора |

## Получить результаты

```http
GET /api/v1/admin/polls/{poll_id}/results
```

### Path parameters

| Параметр | Тип | Описание |
|---|---|---|
| `poll_id` | UUID | Идентификатор опроса |

### Response

`200 OK`

```json
{
  "poll_id": "UUID",
  "total_participants": "integer",
  "results": [
    {
      "option_id": "UUID",
      "text": "string",
      "votes": "integer",
      "participant_percentage": "decimal"
    }
  ]
}
```

### Поля результата

| Поле | Тип | Описание |
|---|---|---|
| `poll_id` | UUID | Идентификатор опроса |
| `total_participants` | integer | Количество уникальных участников |
| `results` | array | Результаты по вариантам |
| `option_id` | UUID | Идентификатор варианта |
| `text` | string | Текст варианта |
| `votes` | integer | Количество голосов |
| `participant_percentage` | decimal | Процент участников, выбравших вариант |

Процент вычисляется как: ``` votes / total_participants * 100 ```.

| Код | Описание |
|---|---|
| `200` | Результаты получены |
| `401` | Требуется авторизация администратора |
| `404` | Опрос не найден |
