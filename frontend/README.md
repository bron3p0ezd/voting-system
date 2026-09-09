# Frontend Voting System

Клиентская часть сервиса анонимных опросов. Стек: React, TypeScript, Vite и Tailwind CSS 4.

## Запуск

Требуется Node.js 22 или новее.

```bash
npm install
Copy-Item .env.example .env.local
npm run dev
```

## Конфигурация окружения

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `VITE_DEV_HOST` | Интерфейс, на котором слушает Vite | `localhost` |
| `VITE_DEV_PORT` | Порт Vite | `5173` |
| `VITE_DEV_ALLOWED_ORIGINS` | Разрешённые CORS-origin через запятую | `http://localhost:5173` |

Если список `VITE_DEV_ALLOWED_ORIGINS` пуст, CORS на dev-сервере отключён. Значения с префиксом `VITE_` доступны клиентскому коду, поэтому не храните в них секреты.

## Проверка

```bash
npm run build
```
