---
name: pii-audit
description: Аудит проекта на утечки PII (ФИО, email, phone) в логах, Sentry, payload AI-вызовов. Запускать перед каждым релизом и при изменениях в anonymizer.py. Критично для соответствия 152-ФЗ.
---

# pii-audit

Проверяет проект на утечки персональных данных в местах, где их быть не должно.

## Когда использовать

- Перед релизом (Chunk 14)
- После изменений в `apps/api/app/services/ai/anonymizer.py`
- После добавления нового AI-провайдера (Mathpix, Claude, GPT, Gemini)
- При расширении логирования
- Регулярно (раз в месяц) как audit

## Что проверяет

### 1. Логи приложения
```bash
grep -rE "[А-ЯЁ][а-яё]+ [А-ЯЁ]\.[А-ЯЁ]\." apps/api/logs/
grep -rE "[\w.+-]+@[\w-]+\.[\w.-]+" apps/api/logs/
grep -rE "\+7\d{10}|\b8\d{10}" apps/api/logs/
```

### 2. Snapshot AI-payload
Запускает pytest на `apps/api/tests/ai/test_anonymizer.py`:
- Проверяет 50 тестовых payload
- Все должны вернуться без PII в Mathpix/Claude/GPT/Gemini-полях

### 3. Database
```sql
-- PII должны быть только в User и ParentContact
-- Никогда не должны быть в Submission, Check, AnalyticsSnapshot
SELECT * FROM checks WHERE claude_analysis::text ~ 'Иван|Мария|@gmail';
```

### 4. Внешние сервисы
- Sentry events — проверить не уходят ли ФИО
- Mailgun — only к адресу родителя, без раскрытия других учеников
- Telegram — только pseudo_id ученика, не ФИО

## Что делает

1. Запускает все 4 проверки
2. Создаёт отчёт в `tmp/pii-audit-{date}.md`:
   - Прошло
   - Найдены утечки (с указанием места)
3. При критичных находках блокирует release и открывает issue

## Параметры

- `scope` — `logs` / `database` / `external` / `all` (default)
- `verbose` — детальный вывод

## Критичность

**P0 (блокирует deploy):** PII в payload AI-сервисов, в Sentry, в Telegram-уведомлениях.

**P1 (исправить срочно):** PII в логах приложения (ротация решит со временем, но утечка плохо).

**P2 (рассмотреть):** PII во внутренних сервисных метриках, не доступных извне.

## Файлы

- `apps/api/tests/ai/test_anonymizer.py` — основные snapshot-тесты
- `apps/api/app/services/ai/anonymizer.py` — модуль анонимизации
- `tmp/pii-audit-*.md` — отчёты
