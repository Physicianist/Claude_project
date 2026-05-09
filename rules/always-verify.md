# Всегда проверяй результат

> КРИТИЧЕСКИ ВАЖНО: после выполнения любой задачи — проверь результат. Не говори "готово" пока не выполнишь проверку.

## Конкретные проверки

### Backend (Python)

```bash
# Синтаксис
python3 -m py_compile apps/api/app/services/foo.py

# Линтер + типы
cd apps/api && ruff check && mypy app

# Тесты
cd apps/api && pytest -xvs tests/

# Миграции
cd apps/api && alembic upgrade head
cd apps/api && alembic downgrade -1 && alembic upgrade head  # roundtrip
```

### Frontend (TypeScript)

```bash
cd apps/web && pnpm lint
cd apps/web && pnpm typecheck
cd apps/web && pnpm test
cd apps/web && pnpm build  # перед деплоем
```

### Конфиги

```bash
# YAML
python3 -c "import yaml; yaml.safe_load(open('infra/docker-compose.yml'))"

# JSON
python3 -c "import json; json.load(open('.claude/settings.json'))"

# Docker compose
docker compose -f infra/docker-compose.dev.yml config
```

### AI-промпты (Chunk 8+)

```bash
# Snapshot-тесты на стилевой контракт
cd apps/api && pytest tests/ai/test_style_contract.py
```

### Анонимизатор (Chunk 7+)

```bash
# Snapshot-тесты: нет PII в payload
cd apps/api && pytest tests/ai/test_anonymizer.py
```

### Endpoints

```bash
# Smoke test через curl
curl -i http://localhost:8000/health

# С аутентификацией
curl -i -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me
```

### UI

- Открыть `http://localhost:3000`, пройти golden path вручную
- Проверить адаптивность (DevTools → Toggle device toolbar)
- a11y: запустить subagent `accessibility-checker` (Chunk 0.5+)

### Юридическое

- Перед каждым релизом — запустить subagent `legal-reviewer`
- Проверить что страницы /legal/privacy, /legal/terms, /legal/cookies открываются
- Проверить что нет PII в логах (ручной grep)

## Перед "готово" — ПЕРЕЧИСЛИ

Не "всё ок", а конкретно:

```
Проверил:
  ✓ ruff (apps/api)
  ✓ mypy --strict (apps/api/app/services)
  ✓ pytest 18 passed, 0 failed
  ✓ migration up/down работает
  ✓ snapshot-тесты анонимизатора: PII не уходит в Mathpix
  ✓ openapi.json генерируется без ошибок
  ✓ нет хардкода секретов (grep KEY apps/api)
```

## Для важных задач — независимая проверка

Запустить subagent `reviewer` или `code-reviewer` для проверки с чистым контекстом. Особенно важно для:

- **Анонимизатора** — single point of failure для 152-ФЗ
- **AI-промптов** — стилевой контракт легко "разваливается" при правках
- **Миграций** — backward-compatibility, downgrade
- **Auth flow** — утечки токенов, CSRF, XSS
- **Deploy скриптов** — race conditions, idempotency

## Если проверка упала

1. Не паниковать
2. Прочитать ошибку, понять причину
3. Исправить корневую причину (не симптом)
4. Запустить проверку снова
5. Максимум 3 итерации — потом обратиться к пользователю

**Никогда не пропускать проверки и не обходить их (`--no-verify`, `# noqa`, `# type: ignore`) без явного разрешения пользователя.**
