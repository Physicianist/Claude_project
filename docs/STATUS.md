# Статус разработки AICheck

> Обновляется после каждого завершённого чанка. Полный план — [docs/plan.md](plan.md).

## Легенда статусов

- ⬜ Не начато
- 🟦 В работе
- ✅ Готово
- ⏸ На паузе / заблокировано

---

## Чанки разработки

| # | Чанк | Зависимости | Статус | Дата начала | Дата завершения | PR # |
|---|------|-------------|--------|-------------|-----------------|------|
| 0 | Юридический трек (РКН, самозанятый, документы) | — параллельно | ⬜ | | | — |
| 0.5 | Documentation Bootstrap & GitHub Push (план, CLAUDE.md, skills, agents, hooks) | — | 🟦 | 2026-05-09 | | TBD |
| 1 | Project Setup & Infrastructure (монорепо код, docker, apps, CI) | 0.5 | ⬜ | | | — |
| 2 | Database Schema & Migrations | 1 | ⬜ | | | — |
| 3 | Authentication (Magic-link + OAuth, без SMS) | 2 | ⬜ | | | — |
| 4 | User Profiles + RBAC + AI Strictness + Referrals | 3 | ⬜ | | | — |
| 5 | Object Storage + Fullscreen + Replace/Delete | 1, 3 | ⬜ | | | — |
| 6 | Assignments + Submissions CRUD + Templates | 4, 5 | ⬜ | | | — |
| 7 | OCR Pipeline (3 провайдера) + Celery + анонимизация | 6 | ⬜ | | | — |
| 8 | Двухуровневый AI-анализ (GPT-5.4 mini + GPT-5.4) + RAG + style_contract | 7 | ⬜ | | | — |
| 9 | Human-in-Loop Review + Reports + WebSocket | 8 | ⬜ | | | — |
| 10 | Analytics Dashboard + AI Insights + Comparisons | 9 | ⬜ | | | — |
| 11 | Calendar / Schedule + iCal Export | 4 | ⬜ | | | — |
| 12 | Telegram Bot (уведомления) | 9 | ⬜ | | | — |
| 13 | Marketplace + Public Pages + Payment Skeleton | 4 | ⬜ | | | — |
| 14 | Production Deploy + Security + Legal Pages | все | ⬜ | | | — |

---

## Go/No-Go контрольные точки

- **После Chunk 0.5:** ревью документационного пакета пользователем, merge PR в main → старт Chunk 1.
- **После Chunk 7:** валидация Mathpix/гибрида/Gemini на 50 реальных работах → выбор OCR_PROVIDER. Это go/no-go для AI-pipeline.
- **После Chunk 9:** первый бета-тест с 3-5 знакомыми репетиторами.
- **После Chunk 14:** закрытый запуск с 10-20 репетиторами через сарафан + реферальную программу.
- **После 50+ репетиторов:** открытие маркетплейса публично.
- **После 500к/мес выручки + 100+ активных репетиторов:** заявка в ФРИИ (5 млн руб за 7%).

---

## Метрики MVP (целевые)

- 30+ активных репетиторов через 3 месяца после запуска
- > 80% retention на 4-й неделе
- NPS > 40
- Среднее время проверки одной работы < 5 минут (с момента загрузки)
- Стоимость одной AI-проверки = $0.04-0.06 (в бюджете $0.05-0.08)

---

## История изменений

| Дата | Событие | PR |
|------|---------|----|
| 2026-05-09 | План v3.3 утверждён, начало Chunk 0.5 | TBD |
