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
├── Readme.md       # Описание проекта и задания
├── backend/        # API, бизнес-логика и хранение данных
├── frontend/       # Пользовательский интерфейс голосования и администрирования
└── web-server/     # Конфигурация nginx для раздачи frontend и проксирования API
```

### Backend

Backend расположен в `backend/`. В нём разделены HTTP-контракты, правила
предметной области и доступ к данным, поэтому router не обращается к PostgreSQL
или Redis напрямую.

```text
backend/
├── Dockerfile                # Образ API: устанавливает зависимости и запускает Uvicorn
├── alembic.ini               # Настройки Alembic
├── requirements.in           # Прямые Python-зависимости
├── requirements.txt          # Зафиксированное дерево зависимостей для установки
├── load_tests/
│   └── locustfile.py         # GET- и POST-сценарии нагрузочного измерения
└── src/
    ├── main.py               # Создаёт FastAPI, CORS и подключает маршруты
    ├── config.py             # Читает настройки из envs/.env и переменных окружения
    ├── apps/                 # Домены приложения
    │   ├── health/           # Endpoint проверки состояния API
    │   ├── auth/             # Вход администратора, выпуск и проверка JWT
    │   ├── poll/             # Публичное получение опроса, cookie участника и учёт голоса
    │   └── admin_poll/       # Создание, список опросов и обезличенные результаты
    ├── settings/             # Общая инфраструктура: DI, PostgreSQL, Redis и базовые контракты
    ├── migrations/           # Alembic-миграции и версии схемы PostgreSQL
    ├── migration_tables.py   # Импортирует модели для формирования metadata миграций
    └── tests/                # Unit- и нагрузочные тесты, запускаемые через pytest
```

Каждый прикладной домен в `src/apps/` организован одинаково: `routers.py` задаёт
HTTP-endpoint’ы и преобразует доменные ошибки в ответы; `schemas.py` описывает
входные и выходные JSON-модели; `services.py` и `repositories.py` содержат
абстрактные контракты. Реализации находятся в `impls/`: сервисы применяют
бизнес-правила и управляют транзакцией, а репозитории выполняют запросы к базе.
ORM-модели опросов, вариантов и голосов находятся в `apps/poll/models.py`.

`settings/di/dependencies.py` собирает реализации через `ServiceFactory`, чтобы
router зависел от контракта, а не от конкретного хранилища. `settings/database.py`
создаёт асинхронный SQLAlchemy engine и пул соединений; `settings/redis.py` —
клиент Redis. Публичный опрос кэшируется в Redis, но окончательная запись голоса
и защита от повторного учёта выполняются атомарно в PostgreSQL.

## Туториал: запуск через Docker Compose

```bash
docker compose up --build -d
docker compose ps
```

### Пул соединений и масштабирование API


Запустите две реплики API так:

```bash
docker compose up --build -d --scale backend=2
docker compose ps
```

Это даёт максимум `2 реплики × 2 worker × (10 + 5) = 60` соединений из лимита
PostgreSQL в 100, оставляя запас 40 соединений. При старте nginx разрешает имя
сервиса `backend` через Docker DNS и распределяет запросы между полученными
адресами реплик. Перед увеличением числа реплик, workers или размера пула сначала
пересчитайте условие:

```text
реплики × workers × (pool_size + max_overflow) <= безопасный лимит PostgreSQL
```

Миграции выполняет одноразовый сервис `migrate` до старта API; это исключает
одновременный запуск Alembic всеми репликами.

| Назначение | Адрес |
|---|---|
| Интерфейс | `http://127.0.0.1/` |
| Администрирование | `http://127.0.0.1/admin/polls` |
| API через nginx | `http://127.0.0.1/api/v1` |
| Health check | `http://127.0.0.1/api/health` |
| OpenAPI | недоступна через nginx: текущая конфигурация проксирует только `/api/` |

## Туториал: ручной запуск

Для разработки без контейнеров нужны Python 3.13, PostgreSQL, Redis и Node.js 22 или
новее. Откройте два терминала: один для backend, другой для frontend.

### 1. Подготовьте PostgreSQL, Redis и backend

Создайте пустую базу PostgreSQL, пользователя с правами на неё и запустите Redis.
Затем создайте
`backend/src/envs/.env` в UTF-8 без BOM. Этот файл содержит локальные секреты и
не должен попадать в Git. Ниже приведён полный пример локальной конфигурации.
Параметры пула соединений, Redis, CORS и URL документации можно не указывать:
для них используются значения по умолчанию из `backend/src/config.py`.

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=voting
DB_PASS=replace-with-local-password
DB_NAME=voting
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
DB_POOL_TIMEOUT_SECONDS=30
DB_POOL_PRE_PING=true
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

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m alembic upgrade head
cd src
../.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Проверьте запуск запросом к `http://127.0.0.1:8000/api/health`. При включённых
в файле окружения настройках OpenAPI доступна по `http://127.0.0.1:8000/docs`.

### 2. Запустите frontend

Во втором терминале выполните из корня репозитория:

```bash
cd frontend
npm ci
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev
```

Откройте адрес, который напечатает Vite (по умолчанию
`http://localhost:5173`). Административная страница находится по пути
`/admin/polls`; публичная страница опроса — по пути `/poll/<poll_id>/vote`.
Перед изменением постоянной конфигурации frontend сверяйтесь с
`frontend/.env.example`; переменные с префиксом `VITE_` не подходят для
секретов.

В Docker Compose для локальной демонстрации заданы `ADMIN_LOGIN=admin` и
`ADMIN_PASSWORD=admin`; замените их перед любым внешним развёртыванием.

Повторное голосование ограничивается cookie `participant_token`: очистка cookie,
новый профиль браузера или другое устройство позволяют получить новый технический
идентификатор и проголосовать снова. IP-адрес не используется как признак
уникальности, а результаты не содержат технических идентификаторов участников.


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

```bash
.venv/bin/python -m pytest -q
```

### Раздельное измерение GET и POST

`src/tests/performance/test_voting_load_profile.py` запускает два независимых
Locust-теста только при явно заданном целевом стенде:

- `test_get_poll_reports_throughput` измеряет только
  `GET /api/v1/polls/{poll_id}` и для каждого запроса получает новую cookie;
- `test_create_vote_reports_throughput` измеряет только
  `POST /api/v1/polls/{poll_id}/votes`. Уникальные participant JWT создаются
  внутри генератора нагрузки и не требуют подготовительного GET-запроса.


Перед запуском создайте отдельный активный single-choice опрос и возьмите UUID
опроса и его варианта. Для POST-only теста передайте генератору тот же тестовый
секрет participant JWT, который настроен на стенде.

```bash
cd backend
export VOTING_LOAD_BASE_URL="http://127.0.0.1"
export VOTING_POLL_ID="UUID-опроса"
export VOTING_OPTION_ID="UUID-варианта"
export VOTING_PARTICIPANT_JWT_SECRET="local-participant-secret-change-before-production"
.venv/bin/python -m pytest src/tests/performance/test_voting_load_profile.py -m performance -q
```

Можно запустить только одно измерение:

```bash
.venv/bin/python -m pytest src/tests/performance/test_voting_load_profile.py -m performance -k get_poll -q
.venv/bin/python -m pytest src/tests/performance/test_voting_load_profile.py -m performance -k create_vote -q
```

Каждый тест запускает 1 667 одновременных пользователей. Это уровень создаваемой
конкуренции, а не обещание получить 1 667 RPS. Измерение начинается после запуска
всех пользователей и продолжается примерно 60 секунд.

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
