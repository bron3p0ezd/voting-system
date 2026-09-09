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
| Данные | PostgreSQL, SQLAlchemy 2.0 async, asyncpg, Alembic | PostgreSQL поддерживает транзакции и уникальные ограничения для конкурентно-безопасного базового учёта одного голоса; SQLAlchemy отделяет работу с БД от доменной логики, а Alembic версионирует схему. |
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

### 1. Подготовьте PostgreSQL и backend

Создайте пустую базу PostgreSQL и пользователя с правами на неё. Затем создайте
`backend/src/envs/.env` в UTF-8 без BOM. Этот файл содержит локальные секреты и
не должен попадать в Git. Все перечисленные параметры обязательны:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=voting
DB_PASS=replace-with-local-password
DB_NAME=voting
ADMIN_JWT_SECRET=replace-with-random-local-secret
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

### Status codes

| Код | Описание |
|---|---|
| `201` | Голос учтён |
| `400` | Некорректный выбор вариантов |
| `401` | Cookie отсутствует или недействительна; обновите страницу для получения новой cookie |
| `404` | Опрос не найден |
| `409` | Участник уже проголосовал |
| `410` | Голосование ещё не началось или уже завершилось |

## Admin API

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
