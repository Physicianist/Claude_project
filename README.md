# AICheck

> EdTech-платформа для репетиторов РФ/СНГ: AI-проверка рукописных STEM-работ, автоотчёты родителям, аналитика прогресса, маркетплейс.

## Что это

AICheck объединяет в одну платформу разрозненные SaaS-инструменты, которыми пользуются репетиторы: загрузка работ, проверка, отчёты, аналитика, расписание, поиск учеников. Цель — снять с преподавателя бюрократическую нагрузку через AI-проверку рукописных работ + автоотчёты родителям + аналитику слабых мест ученика.

**Ключевая ценность:** экономия 2-4 часов/неделю на рутине, объективная аналитика, повышение качества обратной связи.

**Целевой пользователь:** репетиторы РФ/СНГ с 3-4+ учениками, готовящие к ОГЭ/ЕГЭ/ВПР по STEM-предметам.

## Технологический стек

| Слой | Выбор |
|------|-------|
| Frontend | Next.js 15 (App Router) + React 19 + Tailwind + shadcn/ui + Recharts + KaTeX + FullCalendar |
| Backend | FastAPI 3.12 + SQLAlchemy 2.0 async + Pydantic v2 |
| DB | PostgreSQL 16 + ChromaDB (RAG) + Redis 7 |
| Очереди | Celery + Redis |
| Storage | Selectel S3 (prod) + MinIO (dev) |
| Email | Mailgun |
| Telegram | aiogram 3 |
| Auth | Email magic-link + OAuth (Google/VK/Yandex) + JWT |
| Платежи | ЮКасса (готова инфра) |
| AI - OCR | 3 провайдера: Mathpix-only / Mathpix+YandexVision / Gemini 2.5 Flash |
| AI - анализ | GPT-5.4 mini (extract) + GPT-5.4 (feedback) через посредника + Claude Sonnet 4.6 (fallback) |
| Хостинг | Selectel VPS + Docker Compose |
| CI/CD | GitHub Actions |

## Документация

- **[Полный план разработки](docs/plan.md)** — 15 чанков, архитектура, AI pipeline, бюджет
- **[Статус чанков](docs/STATUS.md)** — что уже готово
- **[Архитектура](docs/architecture.md)** — высокоуровневое описание системы
- **[API спецификация](docs/api.md)** — endpoints (заполняется по чанкам)
- **[Git workflow](docs/workflows/git-workflow.md)** — feature-branch + commit policy
- **[Дизайн-референсы](docs/workflows/design-references.md)** — как запрашивать ссылки до UI-чанков
- **[Юридические шаблоны](docs/legal/)** — privacy, terms, согласие родителей

## Правила разработки

- **[CLAUDE.md](CLAUDE.md)** — проектный файл правил для Claude Code
- **[rules/](rules/)** — расширенные правила (Plan→Do→Verify, проверки, plan mode)
- **[.claude/](.claude/)** — настройки Claude Code: hooks, custom skills, custom agents

## Как разрабатывать

1. Прочитать [docs/plan.md](docs/plan.md) и [CLAUDE.md](CLAUDE.md)
2. Проверить [docs/STATUS.md](docs/STATUS.md) — какой чанк следующий
3. Создать feature-branch: `git checkout -b chunk/NN-name`
4. Запросить дизайн-референсы у пользователя (для UI-чанков)
5. Реализовать → коммитить часто на ветку
6. Выполнить критерии готовности из плана
7. Push → создать PR через веб → ревью → merge в main
8. Обновить [docs/STATUS.md](docs/STATUS.md)

## Контакты

Правообладатель: GitHub `Physicianist`

## License

Proprietary — All rights reserved. См. [LICENSE](LICENSE).
