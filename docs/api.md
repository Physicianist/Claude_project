# API Specification — AICheck

> Заполняется по чанкам. Полная актуальная спецификация всегда доступна по `GET /openapi.json` (FastAPI автогенерация) после Chunk 1.

## Базовый URL

- **Dev:** `http://localhost:8000`
- **Prod:** `https://api.aicheck.ru` (после Chunk 14)

## Аутентификация

После Chunk 3:
- **Bearer JWT** в `Authorization: Bearer <access_token>`
- Access token живёт 15 минут
- Refresh token (single-use) живёт 30 дней
- `POST /api/v1/auth/refresh` — получить новую пару

## Endpoints (по чанкам)

### Chunk 1 — Health
- `GET /health` → `{"status": "ok", "version": "..."}`

### Chunk 3 — Auth
- `POST /api/v1/auth/email/request-link`
- `GET /api/v1/auth/email/verify?token=...`
- `POST /api/v1/auth/oauth/{google|vk|yandex}/callback`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

### Chunk 4 — Users / Students / Groups / Referrals
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/students`
- `GET /api/v1/users/students`
- `POST /api/v1/groups`
- `GET /api/v1/groups`
- `PATCH /api/v1/groups/{id}`
- `POST /api/v1/referrals/generate`
- `GET /api/v1/referrals`

### Chunk 5 — Uploads
- `POST /api/v1/uploads/presigned`
- `POST /api/v1/uploads/confirm`
- `DELETE /api/v1/uploads/{key}`

### Chunk 6 — Assignments / Submissions
- `POST /api/v1/assignments`
- `GET /api/v1/assignments` (с фильтрами)
- `GET /api/v1/assignments/{id}`
- `PATCH /api/v1/assignments/{id}`
- `DELETE /api/v1/assignments/{id}`
- `POST /api/v1/assignments/{id}/duplicate`
- `POST /api/v1/assignments/{id}/submissions`
- `GET /api/v1/assignments/{id}/submissions`
- `GET /api/v1/submissions/{id}`

### Chunk 9 — Checks (review)
- `GET /api/v1/checks/{id}`
- `PATCH /api/v1/checks/{id}` (approve + edit)
- `WS /ws/teacher/{user_id}` — real-time updates

### Chunk 10 — Analytics
- `GET /api/v1/analytics/teacher/overview`
- `GET /api/v1/analytics/students/{id}/progress`
- `GET /api/v1/analytics/groups/{id}/overview`
- `GET /api/v1/analytics/comparisons` (Ученик vs Ученик / Ученик vs Группа / Группа vs Группа)
- `GET /api/v1/analytics/insights` — Claude-generated text insights

### Chunk 11 — Lessons / Schedule
- `POST /api/v1/lessons`
- `GET /api/v1/lessons?from=&to=`
- `PATCH /api/v1/lessons/{id}`
- `DELETE /api/v1/lessons/{id}`
- `GET /api/v1/lessons/{id}/ical` → `.ics` файл
- `GET /api/v1/schedule/export` → iCal feed URL

### Chunk 13 — Marketplace / Payments
- `GET /api/v1/marketplace/teachers?subject=&grade=&price_max=`
- `GET /api/v1/marketplace/teachers/{slug}`
- `POST /api/v1/marketplace/leads`
- `POST /api/v1/payments/checkout`
- `POST /api/v1/payments/webhook/yukassa`
- `GET /api/v1/payments/subscription`

## Стандартные ответы

### Успех
```json
{
  "data": { ... },
  "meta": { "total": 42, "page": 1 }
}
```

### Ошибка
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "details": { ... }
  }
}
```

## Коды ошибок

| HTTP | Код | Описание |
|------|-----|----------|
| 400 | VALIDATION_ERROR | Невалидные данные запроса |
| 401 | UNAUTHORIZED | Токен отсутствует или истёк |
| 403 | FORBIDDEN | Нет прав на действие (RBAC) |
| 404 | NOT_FOUND | Ресурс не найден |
| 409 | CONFLICT | Конфликт состояния (например, дубликат) |
| 422 | UNPROCESSABLE_ENTITY | Валидация Pydantic |
| 429 | RATE_LIMITED | Превышен rate limit |
| 500 | INTERNAL_ERROR | Серверная ошибка |

## Rate limits

После Chunk 14:
- `/auth/*` — 10 запросов/секунда на IP
- `/api/*` — 100 запросов/секунда на пользователя
- `/uploads/*` — 30 запросов/минуту на пользователя
