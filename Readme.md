# Voting System

Монорепозиторий сервиса анонимных опросов для национальной компании, проводящей голосования во время телевизионной рекламы.

## Описание

Компания размещает минутные ролики на крупнейших телеканалах. Каждый ролик показывает один вопрос и QR-код или ссылку на голосование. Вопрос может предусматривать выбор одного варианта, нескольких вариантов или A/B. Аудитория одного ролика — примерно 100 миллионов человек; голосование происходит в течение минуты.

Сервис должен позволять:

- Зрителю проголосовать анонимно, без регистрации.
- Ограничить повторное голосование на базовом уровне, достаточном для обычного пользователя, без обещания полной защиты от обхода.
- Администратору создавать опросы и просматривать обезличенные результаты.

Текущий backend реализует получение публичного опроса, учёт голоса через
`POST /api/v1/polls/{poll_id}/votes`, создание опроса через
`POST /api/v1/admin/polls` и получение списка опросов через
`GET /api/v1/admin/polls`, а также агрегированные результаты через
`GET /api/v1/admin/polls/{poll_id}/results`. Голос и опрос сохраняются синхронно: `201 Created`
возвращается только после commit транзакции.

## Структура

```text
voting-system/
├── AGENTS.md       # Общие правила работы агентов
├── README.md       # Описание проекта и задания
├── backend/        # API, бизнес-логика и хранение данных
└── frontend/       # Опциональный пользовательский интерфейс
```

# Voting System API

Базовый URL: ``` /api/v1 ```

Все запросы и ответы используют:  ``` Content-Type: application/json ```

## Ошибки

- ``` 400 Bad Request ```  — бизнес-правила запроса нарушены;
- ``` 401 Unauthorized ```  — нет или невалидна аутентификация/cookie;
- ``` 403 Forbidden ```  — недостаточно прав;
- ``` 404 Not Found ```  — ресурс не найден;
- ``` 409 Conflict ```  — повторное голосование;
- ``` 410 Gone ```  — голосование ещё не началось, завершилось или ресурс больше недоступен;
- ``` 422 Unprocessable Entity ```  — ошибка структурной валидации запроса от Pydantic.

# Public API

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
| `401` | Cookie отсутствует или недействительна |
| `404` | Опрос не найден |
| `409` | Участник уже проголосовал |
| `410` | Голосование ещё не началось или уже завершилось |

# Admin API

Все административные endpoints требуют аутентификации администратора. На этапе
текущей реализации это правило временно не применяется к
`GET /api/v1/admin/polls` и `POST /api/v1/admin/polls`: endpoints доступны без
аутентификации, пока не будет добавлена авторизация.

При отсутствии или некорректной аутентификации: ```401 Unauthorized ```

При недостаточных правах: ```403 Forbidden ```

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
| `401` | Нет аутентификации |
| `403` | Недостаточно прав |

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

### Query parameters

| Параметр | Тип | Default | Описание |
|---|---|---|---|
| `include_empty` | boolean | `true` | Включать варианты без голосов |

Пример:

```http
GET /api/v1/admin/polls/{poll_id}/results?include_empty=false
```

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
