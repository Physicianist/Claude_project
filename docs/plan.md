# AICheck — план разработки EdTech-платформы с AI-проверкой (v3.2)

> Репозиторий: https://github.com/Physicianist/Claude_project (пустой, только .gitkeep)
> Локальный путь: `C:\Users\shepe\Projects\AICheck`
> Дата плана: 2026-05-09 (v3.2 — после уточнений по операционным деталям)
> Соло-разработка с Claude Code, MVP полного функционала, бюджет инфры $110-230/мес

> **Операционные решения (зафиксированы):**
> - **Старт разработки на localhost** — домен покупаем в Chunk 14 перед production deploy. CORS = `http://localhost:3000`, OAuth callback URLs временно на localhost.
> - **Package manager: pnpm** для frontend (быстрее npm на монорепо, лучше работает с workspaces). Установится через `npm install -g pnpm` в Chunk 1.
> - **API ключи: placeholder .env workflow** — стартуем с пустыми placeholder-значениями, добавляем реальные ключи по мере необходимости (Mathpix → Chunk 7, OpenAI/Claude посредник → Chunk 8, Mailgun → Chunk 9, OAuth → Chunk 3 опционально). В .env сразу нужны только: `POSTGRES_PASSWORD`, `SECRET_KEY` (JWT), `REDIS_URL`.

---

## 1. Контекст

Проект объединяет в одну платформу разрозненные SaaS-инструменты, которыми сейчас пользуются репетиторы РФ/СНГ: загрузка работ, коммуникация, хранение решений, отчёты родителям, проверка работ, аналитика, маркетплейс. Цель — снять с преподавателя бюрократическую нагрузку через AI-проверку рукописных работ + автоотчёты родителям + аналитику слабых мест ученика.

**Ключевая ценность для репетитора:** экономия 2-4 часов/неделю на рутине проверки и отчётов, объективная аналитика прогресса учеников, повышение качества обратной связи.

**Целевой пользователь:** репетиторы РФ/СНГ с 3-4+ учениками, готовящие к ОГЭ/ЕГЭ/ВПР по STEM-предметам.

---

## 2. Прожарка продукта (критическая оценка)

### ✅ Что работает в пользу проекта

1. **Реальный пробел рынка подтверждён данными.** Анализ топ-10 EdTech РФ показал: никто из конкурентов не проверяет произвольные рукописные работы через AI для частных репетиторов. Skysmart/ЯКласс — только тесты с автопроверкой. Тетрика — CRM без AI. **Яндекс Учебник "Репетитор AI" (запущен октябрь 2025) — НЕ прямой конкурент:** работает только с типовыми задачами из банка ФИПИ по математике и информатике, не проверяет фото рукописных работ. Зарубежный референс (Gradescope от Pearson, $3/студент) дал 5-10x ускорение в STEM — концепция валидирована.

2. **Технология реализуема в бюджете.** OCR (Mathpix формулы + YandexVision текст / Gemini one-shot) ~$0.005-0.025 за работу до 5 страниц + двухуровневый AI-анализ через зарубежного посредника пользователя (**GPT-5.4 mini** для выявления ошибок + **GPT-5.4** для генерации финального комментария) ~$0.01-0.015 за работу = **итого $0.02-0.04** = укладываемся в бюджет $0.05-0.08 с запасом 2-4x. Azure не поддерживает русский handwriting и отброшен.

3. **Рынок растёт.** EdTech РФ в 2025: 154 млрд руб., +12% YoY. Сегмент частных репетиторов перетекает на платформы — спрос растёт.

4. **Соло-разработка реалистична.** С Claude Code 14 чанков укладываются в 5-7 месяцев работы. Стек выбран AI-friendly (FastAPI + Next.js).

### ⚠️ Критические риски

1. **🟡 OpenAI API структурно недоступен из РФ напрямую** (с июля 2024). Митигейшен: **используем зарубежного посредника пользователя** для доступа к GPT-5 mini. Это снимает риск блокировки. Claude Sonnet 4.6 — fallback через того же посредника на случай проблем с OpenAI.

2. **🔴 152-ФЗ + локализация ПДн с 1 июля 2025** — extraterritorial. Зарубежное юрлицо НЕ обходит закон: если работаем с россиянами, ПДн должны храниться в РФ. **Архитектурное решение:** изоляция PII в PostgreSQL на VPS РФ, в Mathpix/Claude уходит только `pseudo_id` + LaTeX без имён.

3. **🔴 Регистрация в РКН обязательна** даже для бесплатного сервиса (включая физлиц, самозанятых, ИП). Без исключений. **Хорошая новость:** подача уведомления онлайн на pd.rkn.gov.ru — бесплатно, 15-30 минут. Это **не блокирует разработку**, делается параллельно.

4. **🟢 Согласие родителей — обходим архитектурно.** Если **репетитор** — пользователь сервиса (не ребёнок), а работы загружаются по псевдониму/имени без ФИО, формальная обязанность отдельного согласия родителя на ПДн ребёнка НЕ возникает. **Решение в UX:** при создании ученика требуется только имя/псевдоним (не ФИО, не паспорт). Email родителя — опциональное поле для отчётов с галочкой согласия в обычной оферте. Это сильно повышает конверсию онбординга.

5. **🟡 Mathpix оптимизирован под формулы (латиница), русский текст — слабее.** Митигейшен — в Chunk 7: реализуем 3 OCR-провайдера через abstract `OCRProvider`:
   - **Mathpix-only** — простая схема, тестируем первой
   - **Гибрид Mathpix (формулы) + YandexVision OCR (русский текст)** — требует image segmentation
   - **Gemini 2.5 Flash one-shot** — всё одной моделью, дёшево
   Валидация на 50 реальных работах → выбор по соотношению качество/цена/сложность. Это **go/no-go для AI-pipeline**.

6. **🟡 Маркетплейс конкурирует с Тетрикой/Profi.ru.** Сетевой эффект соло-разработчик не запустит за 6 месяцев. **Стратегия:** рост через сарафан + органику + реферальную программу, маркетплейс открывается публично только при достижении 50+ активных репетиторов на платформе. До этого — внутренний search для уже зарегистрированных.

### 🎯 Перспективность: 8/10

Сильные стороны: реальный пробел в нише (AI-проверка рукописных работ для репетиторов), доказанная технология, разумный бюджет, Яндекс — не прямой конкурент, есть посредник для OpenAI. Слабые стороны: юр. барьеры (РКН/152-ФЗ — операционная нагрузка), зависимость от посредника для AI-API.

---

## 3. Рекомендации по фичам

### ➕ ДОБАВИТЬ в план

1. **Анонимизация перед AI-вызовом** (критично из-за 152-ФЗ) — архитектурный паттерн.
2. **Псевдонимный профиль ученика** (имя/прозвище вместо ФИО) — обходит требование согласия родителей и повышает конверсию онбординга.
3. **Уровень "строгости" AI** в **профиле учителя** (settings) — strict / medium / loose — меняет промпт Claude.
4. **Шаблоны заданий + дублирование** — частая операция у репетиторов.
5. **Реферальная программа** для приведения учеников: уникальная ссылка-приглашение, статистика рефералов, в будущем — бонусы (бесплатные проверки).
6. **Полноэкранный просмотр загруженных фото** + удаление/замена фото в submission.
7. **Сравнения в аналитике**: Ученик vs Ученик, Ученик vs Группа, Группа vs Группа + фильтры по предмету/теме/периоду.
8. **Юридический трек как отдельный Chunk 0** — параллельно Chunk 1, не блокирует разработку.

### 🔁 ИЗМЕНЕНО

1. **SMS-аутентификация — УБРАНА** из основного auth-flow (лишний шаг, снижает конверсию). Замена: **email magic-link + OAuth (Google / VK / Yandex)**. SMS оставляем только для опциональной верификации телефона в профиле репетитора (для маркетплейса).
2. **Маркетплейс — ОСТАВЛЕН в MVP** (Chunk 13). Расчёт: рост через сарафан + реферальную программу + органику, маркетплейс становится публичным после достижения 50+ репетиторов.
3. **Поиск учеников — заменён на реферальную программу.** Полноценный поиск учеников — пост-MVP.
4. **Двухуровневый AI-анализ через зарубежного посредника пользователя:**
   - **GPT-5.4 mini** — базовый анализ: выявление ошибок, теги, score_draft, structured JSON (быстро, дёшево)
   - **GPT-5.4** (полная) — генерация **финального комментария** ученику (качественно, лаконично)
   - **Claude Sonnet 4.6** — fallback при сбоях GPT (через того же посредника)
   - Абстракция `AnalysisProvider` с двумя методами `extract_errors()` и `generate_feedback()`
   
   **Стиль комментариев — лаконичный, как живой учитель** (требование пользователя):
   - Без вводных фраз ("Молодец что попробовал", "Отличная работа")
   - Без эмодзи и шаблонов ("Я заметил, что...")
   - Максимум 2-3 предложения
   - Прямо к делу: "Ошибка в шаге 3 — потерян знак минус"
   Это hard requirement в system prompt (style_contract.py).
5. **Кластеризация работ (Gradescope-style)** — **ОТЛОЖЕНА в пост-MVP/B2B**. По обоснованию пользователя: фича для пулла работ большого класса, не для репетитора 1-на-1. Реактивируется при выходе на B2B (школы, мини-курсы).

### ➖ УБРАНО / ОТЛОЖЕНО

1. **🔻 ИИ-помощник в чате → пост-MVP.**
2. **🔻 Мобильные приложения** (PWA достаточен).
3. **🔻 Активная подписочная монетизация** (инфра готова, в MVP бесплатно).
4. **🔻 Кластеризация ошибок** — на этапе B2B-расширения.

**Итог:** MVP = 14 чанков (включая отдельный legal Chunk 0).

---

## 4. Технологический стек (обновлён)

| Слой | Выбор | Обоснование |
|------|-------|-------------|
| Frontend | **Next.js 15 (App Router) + React 19** | Server Components, image optimization, streaming UI, PWA |
| UI | **Tailwind CSS + shadcn/ui** | Unstyled accessible, исходники в репо |
| Графики | **Recharts + KaTeX** | Лёгкий, гибкий, с LaTeX-метками |
| Календарь | **FullCalendar.io + iCal** | Drag-n-drop, RRULE, Google Calendar export |
| Backend | **FastAPI (Python 3.12) + SQLAlchemy 2.0 async + Pydantic v2** | Нативная AI/ML экосистема |
| DB | **PostgreSQL 16** + **ChromaDB** + **Redis 7** | PII (PG РФ) + RAG ФИПИ + кеш/Celery/WS |
| Очереди | **Celery + Redis** | Retry для нестабильных API, Flower |
| Object Storage | **Selectel S3** (prod) + **MinIO** (dev) | S3-совместимый, в РФ (152-ФЗ) |
| Email | **Mailgun** | REST API, Python SDK, 1k бесплатно |
| Telegram bot | **aiogram 3** | Уведомления (не основной канал) |
| Auth | **Email magic-link** + **OAuth (Google/VK/Yandex)** + JWT (15min/30d) | Без SMS — повышение конверсии |
| Платежи | **ЮКасса** (готова инфра, активация позже) | Российская, работает с самозанятыми/ИП |
| AI - OCR | **3 провайдера через abstract `OCRProvider`:** Mathpix-only / Mathpix+YandexVision гибрид / Gemini 2.5 Flash one-shot | Mathpix силён в формулах, слаб в русском тексте. Гибрид с YandexVision или Gemini one-shot могут быть лучше. Валидация в Chunk 7 на 50 работах. **Azure исключён** — нет русского handwriting |
| AI - анализ (базовый) | **GPT-5.4 mini** через зарубежного посредника | Дёшево, быстро. Извлечение ошибок, тегов, score_draft в structured JSON |
| AI - комментарий | **GPT-5.4** (полная) через того же посредника | Качественная генерация лаконичной обратной связи ученику |
| AI - fallback | **Claude Sonnet 4.6** через посредника | Резерв при сбоях GPT-каналов |
| Хостинг | **Selectel VPS** (4 CPU/8GB) + Docker Compose | Соответствует 152-ФЗ |
| CI/CD | **GitHub Actions** → SSH deploy | Просто, бесплатно |
| Юр.форма | **Самозанятый (старт) → ИП УСН 6% (рост)** | Минимум барьеров, переход без потери базы |

---

## 5. Структура монорепо

```
AICheck/
├── apps/
│   ├── web/              # Next.js 15 frontend (PWA)
│   ├── api/              # FastAPI backend + Celery worker
│   └── bot/              # aiogram Telegram bot
├── packages/
│   └── types/            # Сгенерированные TS-типы из OpenAPI
├── infra/
│   ├── docker-compose.dev.yml    # postgres + redis + chromadb + minio
│   ├── docker-compose.yml        # production
│   ├── nginx/
│   └── scripts/                  # deploy.sh, backup.sh
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── plan.md           # Копия этого плана
│   ├── STATUS.md         # Статус-таблица чанков
│   └── legal/            # Политики, оферта, шаблон согласия
├── rules/                # Перенос текущего CLAUDE.md в правила проекта
├── CLAUDE.md             # Обновлённый под AICheck
├── .github/workflows/    # ci.yml, deploy.yml
├── .env.example
├── Makefile             # make dev, make test, make migrate
└── README.md
```

---

## 6. Доменная модель (PostgreSQL)

**Изоляция PII:** PII-поля только в `User` и опционально `ParentContact`. AI-сервисы получают `pseudo_id` (UUID) + контент.

```
User
  id, role(teacher|student|parent), email (nullable), phone (nullable)
  oauth_provider, pseudo_id (UUID), is_virtual, created_at

TeacherProfile (1:1 User)
  bio, subjects[], grade_levels[], slug (для публичной страницы)
  hourly_rate, ai_strictness_level (strict|medium|loose)  ← УРОВЕНЬ AI
  is_marketplace_visible (bool, false до 50+ юзеров)
  rating, response_time_hours, referral_code (UUID)

StudentProfile (1:1 User или standalone)
  display_name (псевдоним: "Иван И.", не ФИО)  ← ОБХОД СОГЛАСИЯ РОДИТЕЛЯ
  parent_contact_id → ParentContact (nullable)
  grade, virtual_token (для submit без регистрации)

ParentContact (отдельная таблица, не User; PII)
  email, phone (nullable), consent_to_reports (bool)

ReferralProgram
  inviter_id → User (teacher), invitee_id → User (nullable до регистрации)
  invitation_link (UUID), status(pending|registered|active)
  created_at, registered_at

Subject → Topic[] (с fipki_code)

Assignment
  teacher_id, title, description, subject_id, topic_ids[]
  deadline, max_score, target_kind(individual|group|virtual)
  target_id, fipki_reference_ids[] (RAG)
  is_template (bool), parent_template_id → Assignment (nullable, для дублирования)

Submission
  assignment_id, student_id, photo_keys[] (S3), full_screen_view (UX)
  status(uploaded|processing|checked|delivered)
  allow_replace_photos (bool)

Check
  submission_id, mathpix_raw, latex_content
  claude_analysis (jsonb), score_draft, score_final
  error_tags[], teacher_comment
  status(ai_done|teacher_reviewed|sent), strictness_used(strict|medium|loose)

Comment (на чек или на позицию в работе)

Group → Lesson[]

Lesson
  teacher_id, group_id|student_ids[], starts_at, ends_at
  ical_uid, recurrence_rule

Notification (channel: app|email|telegram)

Subscription + Payment (готовы, MVP plan="free")

AnalyticsSnapshot (для быстрых дашбордов)
  type(student|group|comparison), entity_id, period
  metrics (jsonb), generated_at

MarketplaceProfile (TeacherProfile extension, активируется после 50+ юзеров)
  tagline, portfolio_urls[], trial_lesson_price
```

---

## 7. AI Pipeline проверки работы

```
TEACHER                    SYSTEM (RU)                    EXTERNAL API
   |                          |                                |
   |-- POST /submissions ---→ |                                |
   |   [photos]               |                                |
   |                          |-- S3 (Selectel, RU)           |
   |                          |-- Submission row              |
   |                          |-- celery: check_submission    |
   |← submission_id --------- |                                |
   |                          |                                |
   |              [WORKER]                                     |
   |                          |-- preprocessing (Pillow)      |
   |                          |-- ⚠️ ANONYMIZE: только        |
   |                          |   pseudo_id + photo bytes     |
   |                          |-- OCRProvider (выбран в      |
   |                          |   Chunk 7 валидацией):        |
   |                          |   а) Mathpix-only             |
   |                          |   б) Mathpix+YandexVision     |
   |                          |   в) Gemini 2.5 Flash         |
   |                          |   ←──────────────────────────→|
   |                          |   → LaTeX + russian text      |
   |                          |                                |
   |                          |-- ChromaDB RAG: похожие       |
   |                          |   ФИПИ-задачи по topic        |
   |                          |                                |
   |                          |-- AnalysisProvider (2 шага): |
   |                          |   ШАГ 1 (extract_errors):     |
   |                          |   GPT-5.4 mini ←─────────────→|
   |                          |   через зарубежного посредника|
   |                          |   strictness=teacher.setting  |
   |                          |   → JSON {errors[], tags[],   |
   |                          |     score_draft}              |
   |                          |                                |
   |                          |   ШАГ 2 (generate_feedback):  |
   |                          |   GPT-5.4 (полная) ←─────────→|
   |                          |   через того же посредника    |
   |                          |   style_contract: лаконично   |
   |                          |   → 2-3 предложения           |
   |                          |   → comment + improvements[]  |
   |                          |                                |
   |                          |   ↓ (на сбое любого шага)     |
   |                          |   Claude Sonnet 4.6 fallback  |
   |                          |                                |
   |                          |-- Save Check (status=ai_done) |
   |                          |-- WS push к учителю           |
   |                          |                                |
   |← WS: "проверка готова"-- |                                |
   |                          |                                |
   |-- view + edit + approve→ |                                |
   |                          |-- celery: send_report         |
   |                          |   - Mailgun → родителю        |
   |                          |   - Telegram → ученику        |
   |                          |-- celery: update_analytics    |
```

**Анонимизация в коде:**
- `apps/api/app/services/ai/anonymizer.py` — функция `anonymize(payload)`, которая удаляет/маскирует ФИО, телефоны, email перед отправкой в Mathpix/Claude/Gemini.
- Test coverage: snapshot-тесты доказывают, что в payload нет PII.

---

## 7.5. Окружение разработки

**На MVP-этапе (Chunks 1-13):** всё локально.
- **URL:** `http://localhost:3000` (Next.js), `http://localhost:8000` (FastAPI), `http://localhost:9001` (MinIO console)
- **CORS:** `http://localhost:3000` в FastAPI настроен сразу
- **OAuth callback URLs:** `http://localhost:3000/api/auth/callback/{google|vk|yandex}` — регистрируются в провайдерах позже (Chunk 3) с реальными значениями
- **Email:** Mailgun sandbox-домен или вывод в консоль через `EMAIL_BACKEND=console` в dev
- **Telegram bot:** локально через polling (не webhook), webhook регистрируем только в Chunk 14

**В Chunk 14 (production deploy):**
- Купить домен (например, `aicheck.ru` через Reg.ru или Beget)
- Получить SSL через Let's Encrypt
- Перенастроить CORS на production-домен
- Зарегистрировать OAuth callback URLs у провайдеров
- Telegram bot через webhook на `https://bot.aicheck.ru/webhook`

**API ключи (placeholder workflow):**

`.env.example` (в репозитории) содержит все переменные с пустыми/placeholder-значениями:
```env
# Database (нужно сразу для Chunk 1)
POSTGRES_PASSWORD=changeme
DATABASE_URL=postgresql://aicheck:changeme@localhost:5432/aicheck

# Auth (нужно для Chunk 3)
SECRET_KEY=__GENERATE_RANDOM_64_CHARS__

# Redis (нужно для Chunk 1)
REDIS_URL=redis://localhost:6379/0

# S3/MinIO (нужно для Chunk 5)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# Mathpix API (нужно для Chunk 7)
MATHPIX_APP_ID=
MATHPIX_APP_KEY=

# YandexVision (опционально для Chunk 7 гибрид-провайдера)
YANDEX_VISION_API_KEY=
YANDEX_FOLDER_ID=

# Gemini (если выбран как OCR в Chunk 7)
GEMINI_API_KEY=

# OpenAI / Claude через посредника (Chunk 8)
OPENAI_API_BASE=https://__YOUR_PROXY_URL__
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# OAuth (Chunk 3, опционально на старте)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
VK_CLIENT_ID=
VK_CLIENT_SECRET=
YANDEX_CLIENT_ID=
YANDEX_CLIENT_SECRET=

# Email (Chunk 9)
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
EMAIL_BACKEND=console  # console на dev, mailgun на prod

# Telegram (Chunk 12)
TELEGRAM_BOT_TOKEN=
```

`.env` (gitignored) — пользователь заполняет по мере необходимости.

---

## 8. Workflow разработки и git-процесс

**Принцип:** короткие итерации, частые коммиты, без слияния в `main` до завершения чанка.

1. На каждый чанк — отдельная feature-branch (`chunk/01-setup`, `chunk/02-db-schema`, ...)
2. **После каждого изменения** (логически осмысленного, не каждой строки) — `git add . && git commit && git push origin chunk/XX-name`
3. Слияние feature-branch в `main` — **только** после прохождения критериев готовности чанка (см. §9) и обновления `docs/STATUS.md`.
4. Скилл `commit` (доступен в Claude Code) — автоматизирует коммиты после логических блоков работы.
5. Ревью пользователем — перед каждым merge в main.

### Дизайн-референсы для UI-чанков

**Перед началом любого UI-чанка** (Chunks 4, 5, 6, 9, 10, 11, 13) — Claude Code обязан запросить у пользователя:
- Скриншоты сайтов-референсов (стиль, layout, цветовая палитра)
- Figma-макеты, если есть
- Конкретные блоки/компоненты для подражания
- Пожелания по UX (какие действия должны быть на одном экране, что в модалках, тема light/dark)

Если референсов нет — Claude Code предлагает 2-3 варианта на выбор (через AskUserQuestion с preview ASCII-mockups), пользователь выбирает.

---

## 9. План разработки в чанках (14 чанков)

> **Принцип:** чанк = логически замкнутая фича, проверяемая end-to-end. Workflow git: §8.

### Chunk 0 — Юридический трек (ОТДЕЛЬНЫЙ ПАРАЛЛЕЛЬНО)

**Цель:** легальная база для запуска.

**Не код, операционные шаги:**
- [ ] Регистрация самозанятого через "Мой налог" (15 минут, бесплатно)
- [ ] Подача уведомления оператора ПДн в Роскомнадзор через pd.rkn.gov.ru (15-30 минут, бесплатно)
- [ ] Шаблоны документов в `docs/legal/`:
  - `privacy-policy.md` (политика конфиденциальности)
  - `terms-of-service.md` (оферта)
  - `cookie-notice.md`
- [ ] Решить: брать ли согласие родителя как опциональный шаг при добавлении email родителя для отчётов (галочка в форме)

**Готово когда:**
- ИНН самозанятого получен
- Уведомление в РКН подано (статус "в реестре" может прийти позже, не блокирует)
- 3 PDF/MD-документа в репозитории, ссылки на них в footer сайта (готовы к Chunk 14)

**Зависимости:** нет. Запускается одновременно с Chunk 1, завершается до Chunk 14 (production deploy).

---

### Chunk 0.5 — Documentation Bootstrap & GitHub Push (НОВЫЙ — выполняется ПЕРВЫМ)

**Цель:** залить на GitHub полный документационный пакет ДО написания любого кода. Это единственный артефакт первого этапа — проект, готовый к началу разработки, но без приложений/инфры.

**Шаги:**
1. `mkdir C:\Users\shepe\Projects` (если нет)
2. `git clone https://github.com/Physicianist/Claude_project AICheck`
3. `cd AICheck && git checkout -b chunk/00-docs-bootstrap`
4. Создать структуру **только для документации и конфигов** (не код):
   ```
   AICheck/
   ├── docs/
   │   ├── plan.md                     # копия 1-goofy-flute.md
   │   ├── STATUS.md                   # статус-таблица всех чанков
   │   ├── architecture.md             # высокоуровневая архитектура из §4-7 плана
   │   ├── api.md                      # пустой шаблон, заполняем по чанкам
   │   ├── legal/                      # пустая, наполняется в Chunk 0
   │   └── workflows/
   │       ├── git-workflow.md         # feature-branch + commit policy
   │       └── design-references.md    # как запрашивать дизайн-референсы
   ├── tmp/plans/
   │   └── 1-goofy-flute.md            # локальная копия плана (в .gitignore по умолчанию)
   ├── rules/
   │   ├── plan-do-verify.md           # из глобального CLAUDE.md
   │   ├── clarifying-questions.md     # 5-20 вопросов перед крупными действиями
   │   ├── never-make-up.md            # никогда не выдумывать
   │   ├── always-verify.md            # перечислять что проверил
   │   └── plan-mode.md                # работа с планами
   ├── .claude/
   │   ├── settings.json               # hooks (PostToolUse линтер, Stop статус, и т.д.)
   │   ├── skills/
   │   │   ├── chunk-status.md         # обновление STATUS.md
   │   │   ├── pii-audit.md            # аудит логов на PII
   │   │   ├── legal-check.md          # проверка юр.страниц
   │   │   └── ocr-validate.md         # валидация OCR на ground-truth
   │   └── agents/
   │       ├── mathpix-validator.md    # OCR accuracy validation
   │       ├── prompt-tester.md        # regression тесты промптов
   │       ├── accessibility-checker.md # a11y aудит UI
   │       └── legal-reviewer.md       # 152-ФЗ проверка
   ├── CLAUDE.md                       # проектный, заточенный под AICheck
   ├── README.md                       # описание проекта, ссылка на план
   ├── .gitignore                      # стандартный (Python + Node + .env)
   ├── .env.example                    # шаблон из §7.5
   └── LICENSE                         # MIT или proprietary — спросить у пользователя
   ```

5. **Содержимое CLAUDE.md (проектный):** русский язык, ссылки на rules/, обязательные правила:
   - PII-анонимизация перед любыми AI-вызовами (ссылка на anonymizer.py)
   - style_contract для AI-комментариев (ссылка на §3 плана)
   - feature-branch workflow + commit policy
   - Запросить дизайн-референсы перед каждым UI-чанком
   - Использование skills `commit`, `code-reviewer`, `qa`, `frontend-design`
   - Юридические требования (152-ФЗ, РКН) — обязательная проверка анонимизации
   - Работа через Plan→Do→Verify (ссылка на rules/plan-do-verify.md)

6. **Содержимое .claude/settings.json (hooks):**
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Edit|Write",
           "filePattern": "apps/api/app/services/ai/**",
           "command": "python3 scripts/check_anonymizer.py"
         },
         {
           "matcher": "Edit|Write",
           "filePattern": "apps/api/**/*.py",
           "command": "ruff check apps/api"
         },
         {
           "matcher": "Edit|Write",
           "filePattern": "apps/web/**/*.{ts,tsx}",
           "command": "cd apps/web && pnpm exec eslint"
         }
       ],
       "Stop": [
         { "command": "python3 scripts/update_status.py" }
       ],
       "PreToolUse": [
         {
           "matcher": "Bash",
           "command": "python3 scripts/safety_check.py",
           "blocking": true
         }
       ]
     }
   }
   ```
   Скрипты `scripts/check_anonymizer.py`, `scripts/update_status.py`, `scripts/safety_check.py` — заглушки в Chunk 0.5, реальная логика в соответствующих чанках.

7. **Custom skills и subagents — в виде markdown-файлов** с frontmatter (имя, описание, тулы). Реальная логика — в Chunk 7-14, сейчас только описания.

8. **README.md** — короткое описание проекта с:
   - Что такое AICheck (1-2 абзаца)
   - Технологический стек (краткая таблица из §4)
   - Ссылка на полный план: `docs/plan.md`
   - Текущий статус: `docs/STATUS.md`
   - Как разрабатывать (ссылка на `docs/workflows/git-workflow.md`)
   - License

9. **STATUS.md** — статус-таблица всех 15 чанков (с Chunk 0.5) с колонками: # / Чанк / Зависимости / Статус / Дата начала / Дата завершения / PR #. Все статусы кроме 0.5 — ⬜ Не начато.

10. **Коммит и push:**
    ```
    git add .
    git commit -m "Chunk 0.5: Documentation bootstrap — план, CLAUDE.md, skills, agents, hooks"
    git push origin chunk/00-docs-bootstrap
    ```
11. **Открыть PR на GitHub** (через `gh pr create`) → Approve пользователем → merge в main.

**Готово когда:**
- Репозиторий на GitHub содержит все ~25 файлов документации и конфигов
- Никакого кода (FastAPI/Next.js/Docker) пока нет
- PR создан, проверен и смерджен в main
- `docs/STATUS.md` показывает Chunk 0.5 = ✅ Готово
- Pull-request-URL получен пользователем для ревью

**Зависимости:** нет (это первый чанк, выполняется до Chunk 1)

---

### Chunk 1 — Project Setup & Infrastructure

**Цель:** монорепо + docker-compose + БД + базовый CI + клонирование GitHub.

**Файлы:**
- `infra/docker-compose.dev.yml` (postgres, redis, chromadb, minio)
- `infra/docker-compose.yml` (prod заглушка)
- `apps/api/{Dockerfile, requirements.txt, app/main.py, app/config.py, app/database.py}`
- `apps/web/{Dockerfile, package.json, pnpm-workspace.yaml, next.config.js, app/layout.tsx, app/page.tsx, tailwind.config.ts}`
- `apps/bot/{Dockerfile, requirements.txt, app/main.py}`
- `.github/workflows/ci.yml` (ruff, mypy, eslint, типы)
- `.env.example`, `Makefile`, `README.md`
- `pnpm-workspace.yaml` в корне (определяет workspaces для apps/web, packages/types)

**Документация и правила:**
- `CLAUDE.md` (новый проектный, заточенный под AICheck): обязательная анонимизация в AI-вызовах, style_contract для комментариев, feature-branch workflow, русский язык, ссылки на rules/
- `rules/` — перенос текущего глобального CLAUDE.md (Plan→Do→Verify, проверки, уточняющие вопросы) как референс
- `docs/plan.md` — копия `C:\Users\shepe\.claude\plans\1-goofy-flute.md`
- `tmp/plans/1-goofy-flute.md` — локальная копия по правилу глобального CLAUDE.md
- `docs/STATUS.md` — статус-таблица из §11 плана с колонками "Чанк / Зависимости / Статус / Дата начала / Дата завершения"
- `docs/architecture.md`, `docs/api.md` — заготовки для расширения по чанкам

**Шаги Chunk 1:**
1. `mkdir C:\Users\shepe\Projects` (если нет)
2. `git clone https://github.com/Physicianist/Claude_project AICheck`
3. `cd AICheck && git checkout -b chunk/01-setup`
4. Установить pnpm глобально: `npm install -g pnpm`
5. Создать структуру монорепо (см. §5)
6. Скопировать план в `docs/plan.md` и `tmp/plans/`
7. Создать новый `CLAUDE.md` для проекта + `rules/` с глобальными правилами
8. Создать `docs/STATUS.md` со всеми 14 чанками
9. Базовый docker-compose.dev.yml с postgres+redis+chromadb+minio
10. Минимальные `apps/api`, `apps/web`, `apps/bot` (health check + Hello Page)
11. CI workflow (ruff, eslint, mypy)
12. Запустить `claude-code-setup:claude-automation-recommender` для рекомендаций hooks/skills
13. Создать `.claude/settings.json` с базовыми hooks
14. Коммит + пуш в `chunk/01-setup` ветку

**Готово когда:**
- `make dev` поднимает сервисы (postgres, redis, chromadb, minio, api, web, bot)
- `curl localhost:8000/health` → `{"status":"ok"}`
- Next.js на `http://localhost:3000` показывает "AICheck — coming soon"
- CI зелёный (ruff, eslint, mypy без ошибок)
- `git push origin chunk/01-setup` успешен
- Все 5 файлов документации в репозитории (CLAUDE.md, plan.md, STATUS.md, architecture.md, api.md)
- `rules/` содержит копию глобальных правил
- `tmp/plans/1-goofy-flute.md` создан

**Зависимости:** нет

---

### Chunk 2 — Database Schema & Migrations

**Цель:** все ORM-модели + Alembic миграции.

**Файлы:** `apps/api/app/models/{user,teacher_profile,student_profile,parent_contact,referral,subject,topic,assignment,submission,check,comment,group,lesson,notification,subscription,payment,analytics_snapshot,marketplace_profile}.py`, `apps/api/migrations/versions/0001_initial.py`

**Готово когда:**
- `alembic upgrade head` без ошибок, downgrade тоже
- `pseudo_id` UUID присутствует в User/Submission/Assignment
- `display_name` (псевдоним) в StudentProfile
- `ai_strictness_level` в TeacherProfile

**Зависимости:** Chunk 1

---

### Chunk 3 — Authentication (Magic-link + OAuth, БЕЗ SMS)

**Цель:** регистрация и вход через email magic-link + OAuth Google/VK/Yandex.

**Файлы:**
- `apps/api/app/api/v1/auth.py`
- `apps/api/app/services/{auth,email_auth,oauth}.py`
- `apps/web/app/(auth)/{login,verify-email,oauth-callback}/page.tsx`
- `apps/web/lib/auth.ts` + middleware

**Endpoints:**
- `POST /auth/email/request-link` — отправить magic-link на email
- `GET /auth/email/verify?token=...` → JWT pair
- `POST /auth/oauth/{google|vk|yandex}/callback`
- `POST /auth/refresh`
- `POST /auth/logout`

**Готово когда:**
- Регистрация через magic-link работает (ссылка действительна 15 мин, single-use)
- JWT access (15min) + refresh (30d) валидны
- OAuth Google: создание/линковка User
- 401 на защищённых endpoints без токена
- **SMS-кода нет в основном flow**

**Зависимости:** Chunk 1, 2

---

### Chunk 4 — User Profiles, Roles, RBAC + AI Strictness

**Цель:** Teacher/Student/Parent профили, виртуальные ученики, группы, RBAC, настройка строгости AI.

**Файлы:**
- `apps/api/app/api/v1/{users,students,groups,referrals}.py`
- `apps/api/app/core/permissions.py` (RBAC декораторы)
- `apps/web/app/(dashboard)/{profile,students,groups,referrals}/page.tsx`
- `apps/web/components/profile/AISettings.tsx` (выбор strict/medium/loose)

**Endpoints:**
- `GET/PATCH /users/me` (включая `ai_strictness_level`)
- `POST /users/students` (с `display_name`, без ФИО)
- `POST /groups`, `GET /groups`, `PATCH /groups/{id}`
- `POST /referrals/generate` → reusable invitation link
- `GET /referrals` — список приглашённых, статусы

**Дизайн-референсы:** ⚠️ Запросить у пользователя референсы для страниц `/profile`, `/students`, `/groups`, `/referrals` ДО начала разработки.

**Готово когда:**
- Teacher создаёт виртуального ученика по псевдониму "Иван И."
- В профиле учителя есть слайдер/селект уровня строгости AI
- Реферальная ссылка генерируется и приглашённый ученик регистрируется по ней (статус меняется на "registered")
- RBAC: teacher-only endpoints возвращают 403 для student
- Опциональное поле email родителя с галочкой согласия на отчёты

**Зависимости:** Chunk 3

---

### Chunk 5 — Object Storage + File Upload (с полноэкранным просмотром)

**Цель:** загрузка фото работ через presigned URLs, fullscreen viewer, замена/удаление фото.

**Файлы:**
- `apps/api/app/services/storage.py` (boto3 wrapper)
- `apps/api/app/api/v1/uploads.py`
- `apps/web/components/submissions/{PhotoUploader,FullscreenViewer,PhotoGallery}.tsx`
- `apps/web/lib/heic-converter.ts` (HEIC → JPEG в браузере)

**Endpoints:**
- `POST /uploads/presigned` → `{url, key}`
- `POST /uploads/confirm` — подтвердить
- `DELETE /uploads/{key}` — удалить (только если submission ещё не обработана)

**Дизайн-референсы:** ⚠️ Запросить референсы для PhotoUploader, FullscreenViewer, PhotoGallery (можно показать референсы Notion image upload, Telegram media viewer и т.д.) ДО начала.

**Готово когда:**
- Drag-n-drop + клик-выбор файлов
- HEIC автоматически в JPEG
- Файл >10MB отклоняется
- **Полноэкранный просмотр** загруженных фото (zoom, swipe между фото)
- **Замена/удаление** фото работают до момента submission
- В MinIO видны загруженные файлы

**Зависимости:** Chunk 1, 3

---

### Chunk 6 — Assignments & Submissions CRUD (с шаблонами и дублированием)

**Цель:** создание заданий (включая черновики и шаблоны), дублирование, загрузка работ.

**Файлы:**
- `apps/api/app/api/v1/{assignments,submissions}.py`
- `apps/web/app/(dashboard)/assignments/{page,new,[id]/edit}/page.tsx`
- `apps/web/app/(student)/submit/[token]/page.tsx` (для виртуальных)
- `apps/web/components/assignments/{AssignmentCard,AssignmentForm,DuplicateButton}.tsx`

**Дизайн-референсы:** ⚠️ Запросить референсы для AssignmentCard, AssignmentForm, страницы создания/списка заданий (можно показать LMS-системы, Notion-таски, Linear) ДО начала.

**Готово когда:**
- Создание/редактирование/удаление задания + черновик + шаблон
- **Дублирование задания** одной кнопкой (`POST /assignments/{id}/duplicate`)
- Виртуальный ученик загружает работу по `/submit/{assignment_id}?token=...` без регистрации
- Список заданий с пагинацией и фильтрами (по предмету, группе, дедлайну)

**Зависимости:** Chunk 4, 5

---

### Chunk 7 — OCR Pipeline (3 провайдера) + Celery + Анонимизация

**Цель:** Celery воркер + три OCR-провайдера через abstract `OCRProvider` + валидация выбора + анонимизация.

**Файлы:**
- `apps/api/app/celery_app.py`
- `apps/api/app/tasks/check_submission.py`
- `apps/api/app/services/ai/preprocessing.py` (Pillow resize/normalize)
- `apps/api/app/services/ai/anonymizer.py` (удаление PII перед AI-вызовом)
- `apps/api/app/services/ai/ocr/base.py` (`OCRProvider` ABC + `OCRResult` dataclass)
- `apps/api/app/services/ai/ocr/mathpix_only.py` — провайдер 1
- `apps/api/app/services/ai/ocr/mathpix_yandex_hybrid.py` — провайдер 2 (segmentation: формула/текст). **Подход к сегментации:**
  - **Default (простой):** использовать Mathpix Bbox API — Mathpix возвращает координаты найденных формул. Вырезаем регионы формул → отдельный Mathpix-вызов → LaTeX. Маскируем формулы белым цветом → YandexVision OCR на оставшемся → русский текст. Объединяем по координатам.
  - **Fallback (если Bbox-точность < 80%):** PaddleOCR PP-StructureV2 — open-source модель document layout analysis, классифицирует регионы (text/formula/table). 5-7 строк кода, бесплатно.
  - **Не используем YOLO** — оверкилл для соло-проекта, требует 1-2 недели на обучение custom-модели на MFD-1M датасете. Возвращаемся к этому только если первые два не дали удовлетворительного качества (маловероятно).
- `apps/api/app/services/ai/ocr/gemini_oneshot.py` — провайдер 3
- `apps/api/app/services/ai/ocr/factory.py` — выбор активного провайдера через env
- `apps/api/scripts/validate_ocr.py` — скрипт валидации на ground-truth (50 работ)
- `apps/api/Dockerfile.worker`

**Готово когда:**
- Все 3 OCR-провайдера реализованы и работают на тестовом фото
- Анонимизатор snapshot-тестами доказывает: в payload нет ФИО/email/phone
- Реальное фото → LaTeX + русский текст в БД для всех провайдеров
- Retry x3 при ошибках
- Метрика: время OCR < 30s p95
- **Валидационный отчёт:** `validate_ocr.py` на 50 реальных рукописных работ дал таблицу:
  | Провайдер | Accuracy LaTeX | Accuracy текст | Время | Стоимость/страница |
  | mathpix_only | ... | ... | ... | $0.005 |
  | mathpix_yandex_hybrid | ... | ... | ... | $0.0065 |
  | gemini_oneshot | ... | ... | ... | $0.001-0.005 |
- **Принято решение** какой провайдер дефолтный (зафиксировать в `.env`: `OCR_PROVIDER=...`)
- **Это go/no-go для AI-pipeline.**

**Зависимости:** Chunk 6

---

### Chunk 8 — Двухуровневый AI-анализ + RAG + Strictness + Лаконичный стиль

**Цель:** AnalysisProvider абстракция с двумя методами:
- `extract_errors()` — GPT-5.4 mini, быстрое выявление ошибок и тегов в structured JSON
- `generate_feedback()` — GPT-5.4 (полная), качественная генерация финального лаконичного комментария ученику

Плюс RAG по ФИПИ + промпт по уровню строгости + жёсткий стилевой контракт.

**Файлы:**
- `apps/api/app/services/ai/analysis/base.py` (`AnalysisProvider` ABC + `ExtractedErrors`, `Feedback` dataclasses)
- `apps/api/app/services/ai/analysis/gpt54_mini.py` — реализация `extract_errors()` (основной)
- `apps/api/app/services/ai/analysis/gpt54_full.py` — реализация `generate_feedback()` (для финальных комментариев)
- `apps/api/app/services/ai/analysis/claude_sonnet.py` — fallback для обоих методов при сбое GPT
- `apps/api/app/services/ai/analysis/factory.py` — двухступенчатый pipeline + retry на Claude
- `apps/api/app/services/ai/rag.py`
- `apps/api/app/services/ai/prompts/system_prompt_extract.py` — для GPT-5.4 mini, JSON schema
- `apps/api/app/services/ai/prompts/system_prompt_feedback.py` — для GPT-5.4, лаконичный стиль
- `apps/api/app/services/ai/prompts/{strict,medium,loose}.py` — варианты по строгости
- `apps/api/app/services/ai/prompts/style_contract.py` — анти-AI текст (см. ниже)
- `apps/api/scripts/ingest_fipki.py` — загрузка ФИПИ → ChromaDB

**Стилевой контракт (style_contract.py)** — жёсткие инструкции в system prompt:
```
СТИЛЬ КОММЕНТАРИЯ — КРИТИЧНО:
- Пиши КАК РЕАЛЬНЫЙ УЧИТЕЛЬ, не как нейросеть
- ЗАПРЕЩЕНО: "Молодец что попробовал", "Отличная работа", "Я заметил, что...",
  "Хочется отметить", "Прежде всего", "В целом", эмодзи, восклицательные знаки
- РАЗРЕШЕНО: прямой указ на ошибку и краткая рекомендация
- Максимум 2-3 предложения
- Примеры:
  ✓ "Ошибка в шаге 3 — потерян знак минус. Перепроверь дискриминант."
  ✓ "Уравнение решено верно, но в итоге пропущена единица измерения."
  ✗ "Молодец, что попытался решить эту задачу! Я заметил небольшую ошибку..."
```

**Тесты:** snapshot-тесты на отказ модели от запрещённых паттернов в выводе.

**Готово когда:**
- ingest_fipki: 100+ задач из открытого банка ФИПИ загружены в ChromaDB
- **Шаг 1 (extract):** GPT-5.4 mini получает LaTeX + RAG-контекст + assignment + max_score + strictness, возвращает structured JSON `{errors[], tags[], score_draft}`
- **Шаг 2 (feedback):** GPT-5.4 получает результат шага 1 + style_contract → лаконичный комментарий ученику (2-3 предложения, без AI-маркеров)
- При сбое любого шага — автоматический retry через Claude Sonnet 4.6
- **Strict** даёт на 20-40% более низкие баллы и детальные ошибки
- **Loose** прощает мелкие ошибки, фокус на ключевых
- **Стиль:** комментарии не содержат запрещённых паттернов (snapshot-тесты на 50 примерах)
- Анонимизатор: в payload только pseudo_id
- Стоимость одного полного анализа измерена и < $0.02

**Зависимости:** Chunk 7

---

### Chunk 9 — Human-in-Loop Review + Real-time + Reports

**Цель:** UI проверки teacher → отправка ученику + отчёт родителю.

**Файлы:**
- `apps/api/app/api/v1/checks.py`
- `apps/api/app/api/websocket.py`
- `apps/api/app/tasks/send_report.py`
- `apps/api/app/services/{email,report}.py` (Mailgun + HTML)
- `apps/web/app/(dashboard)/submissions/[id]/review/page.tsx`
- `apps/web/components/submissions/{CheckReviewPanel,MathRenderer,ErrorTagPills,SideBySideViewer}.tsx`
- `apps/web/lib/websocket.ts`

**Дизайн-референсы:** ⚠️ Это **самый важный UI-экран**. Запросить референсы side-by-side review (Gradescope, GitHub PR review, Notion comments). HTML-шаблон отчёта родителю — также запросить референсы.

**Готово когда:**
- Side-by-side: оригинал фото + распарсенный LaTeX + ошибки + теги + черновик-комментарий + score_draft
- Teacher редактирует comment/score → Approve → send_report task
- Отчёт родителю на email за < 1 минуты (только если consent_to_reports=true)
- WebSocket пушит "AI завершил проверку"

**Зависимости:** Chunk 8

---

### Chunk 10 — Analytics Dashboard + AI Insights + Сравнения

**Цель:** дашборд учителя/ученика + AI-инсайты + сравнения и фильтры.

**Файлы:**
- `apps/api/app/api/v1/analytics.py`
- `apps/api/app/services/analytics.py`
- `apps/api/app/tasks/update_analytics.py`
- `apps/web/app/(dashboard)/analytics/page.tsx`
- `apps/web/components/analytics/{ErrorTagsChart,ProgressChart,TopicMasteryHeatmap,AIInsightsPanel,ComparisonView,FiltersPanel}.tsx`

**Метрики:**
- По ученику: динамика баллов, теги ошибок, теплокарта тем
- По группе: средние, проблемные темы, "группа риска"
- **Сравнения:** Ученик vs Ученик, Ученик vs Группа, Группа vs Группа
- **Фильтры:** период, предмет, тема, тип задания

**AI Insights** — Claude генерирует тексты:
- "У 3 учеников растёт частота арифметических ошибок — рекомендую повторить тему X"
- "Группа A в среднем на 15% слабее группы B по теме 'квадратные уравнения'"

**Дизайн-референсы:** ⚠️ Запросить референсы дашбордов (Tableau, Linear Insights, Stripe Dashboard, Notion analytics). Расположение фильтров, графики, цветовая схема.

**Готово когда:**
- После 5+ проверок дашборд показывает реальные данные
- Сравнения работают для всех 3 типов
- Фильтры применяются ко всем графикам
- AI Insights генерируются раз в сутки + по запросу

**Зависимости:** Chunk 9

---

### Chunk 11 — Calendar / Schedule + iCal Export

**Цель:** расписание занятий + iCal-экспорт.

**Файлы:**
- `apps/api/app/api/v1/lessons.py`
- `apps/api/app/services/calendar.py` (icalendar lib)
- `apps/web/app/(dashboard)/schedule/page.tsx` (FullCalendar)

**Дизайн-референсы:** ⚠️ Запросить референсы календаря (Google Calendar, Cal.com, Linear scheduling).

**Готово когда:**
- FullCalendar отображает занятия (week/month view)
- Создание/перенос/удаление через drag-n-drop
- iCal feed URL подключается к Google Calendar
- Поддержка повторяющихся занятий (RRULE)

**Зависимости:** Chunk 4

---

### Chunk 12 — Telegram Bot (уведомления)

**Цель:** aiogram бот, привязка к аккаунту, push-уведомления.

**Файлы:**
- `apps/bot/app/{main,handlers,keyboards,services}.py`
- `apps/api/app/services/telegram.py`

**Готово когда:**
- `/start` показывает deeplink-кнопку для привязки
- "Работа Иванова проверена: 8/10" приходит в Telegram учителя
- Родителю: "Отчёт по работе ребёнка отправлен" (если привязан Telegram)

**Зависимости:** Chunk 9

---

### Chunk 13 — Marketplace + Public Teacher Pages

**Цель:** маркетплейс с фильтрами + публичная страница преподавателя по slug + skeleton платежей.

**Файлы:**
- `apps/api/app/api/v1/{marketplace,payments}.py`
- `apps/api/app/services/payments/yukassa.py` (skeleton)
- `apps/web/app/marketplace/page.tsx` (каталог)
- `apps/web/app/teacher/[slug]/page.tsx` (публичная страница)
- `apps/web/components/marketplace/{TeacherCard,FilterPanel,LeadForm}.tsx`

**Логика:**
- На MVP-старте `is_marketplace_visible=false` для всех (маркетплейс закрыт)
- Публичная страница `teacher/{slug}` доступна сразу (для шеринга в соцсетях/реферальных ссылок)
- Маркетплейс открывается публично после преодоления порога 50+ репетиторов
- Skeleton платежей (модели, ЮКасса webhook) — на будущее, в MVP всё бесплатно

**Endpoints:**
- `GET /marketplace/teachers` (с фильтрами subject, grade, price_max — рендерится в "coming soon", если порог не достигнут)
- `GET /marketplace/teachers/{slug}` (публично)
- `POST /marketplace/leads` (заявка от ученика)
- `POST /payments/checkout` (skeleton)
- `POST /payments/webhook/yukassa` (skeleton)

**Дизайн-референсы:** ⚠️ Запросить референсы маркетплейса (Profi.ru, Тетрика, Superprof) и публичных страниц репетитора (карточки на Profi.ru, профили YouTube-учителей, Linktree).

**Готово когда:**
- Публичная страница `/teacher/{slug}` рендерится с bio, предметами, рейтингом
- Лид-форма отправляет уведомление учителю
- Платёжный webhook принимает события (без активации)
- Маркетплейс рендерит "Скоро откроется" пока счётчик репетиторов < 50

**Зависимости:** Chunk 4

---

### Chunk 14 — Production Deploy + Security + Legal Pages

**Цель:** боевой деплой + юридические страницы + hardening.

**Файлы:**
- `infra/scripts/{deploy,backup}.sh`
- `infra/nginx/nginx.conf` (SSL, rate limiting, CSP)
- `.github/workflows/deploy.yml`
- `apps/web/app/legal/{privacy,terms,cookies}/page.tsx`
- `docs/legal/*.md` уже готовы из Chunk 0

**Чеклист:**
- [ ] Let's Encrypt SSL на домене
- [ ] nginx rate limit: 10 r/s на /auth, 100 r/s на /api
- [ ] PostgreSQL: dedicated user, минимальные права
- [ ] Cron pg_dump каждые 6 часов → Selectel S3
- [ ] UptimeRobot мониторит /health
- [ ] **Уведомление в РКН подано (из Chunk 0)**
- [ ] Политика конфиденциальности и оферта опубликованы
- [ ] DPA с Anthropic, Mathpix получены/подписаны
- [ ] GitHub Actions: push в main → deploy за < 2 мин
- [ ] Все секреты в env vars
- [ ] CSP headers, защита от XSS

**Готово когда:**
- HTTPS работает без ошибок SSL
- `/health` отвечает с production VPS
- Deploy через GitHub Actions без manual steps
- pg_dump создаётся и загружается в S3
- Все юридические страницы опубликованы и линкованы из футера

**Зависимости:** все предыдущие чанки + Chunk 0 (legal)

---

## 10. Бюджет инфраструктуры

| Сервис | План | Цена/мес |
|--------|------|----------|
| Selectel VPS 4CPU/8GB | Cloud Server | ~$40 |
| Selectel S3 (100 GB) | Object Storage | ~$5 |
| Mailgun | Flex 5k | $0-15 |
| Домен `.ru` (+ резерв `.com`) | — | ~$12 |
| **Mathpix API** | usage | $10-30 |
| **YandexVision OCR** (если гибрид) | usage | $5-10 |
| **GPT-5.4 mini** (extract — основной) | usage | $5-15 |
| **GPT-5.4** (feedback — полная) | usage | $10-25 |
| **Claude Sonnet 4.6** (fallback) | usage | $5-15 |
| **Gemini 2.5 Flash** (если выбран как OCR) | usage | $5-15 |
| **Маржа посредника** (за переадресацию AI API) | оценочно | +10-15% |
| **Резерв** | — | $10-20 |
| **Итого MVP** | | **~$110-230** |

---

## 11. Статус-таблица чанков (копировать в `docs/STATUS.md`)

| # | Чанк | Зависимости | Статус |
|---|------|-------------|--------|
| 0 | Юридический трек (РКН, самозанятый, документы) | — (параллельно) | ⬜ |
| 0.5 | **Documentation Bootstrap & GitHub Push** (план, CLAUDE.md, skills, agents, hooks) | — | ⬜ |
| 1 | Project Setup & Infrastructure | 0.5 | ⬜ |
| 2 | Database Schema & Migrations | 1 | ⬜ |
| 3 | Auth (Magic-link + OAuth) | 2 | ⬜ |
| 4 | User Profiles + RBAC + AI Strictness + Referrals | 3 | ⬜ |
| 5 | Object Storage + Fullscreen + Replace/Delete | 1, 3 | ⬜ |
| 6 | Assignments + Submissions CRUD + Templates | 4, 5 | ⬜ |
| 7 | Mathpix + Celery + Gemini Fallback | 6 | ⬜ |
| 8 | Claude + RAG + Strictness | 7 | ⬜ |
| 9 | Human-in-Loop Review + Reports + WS | 8 | ⬜ |
| 10 | Analytics + AI Insights + Comparisons | 9 | ⬜ |
| 11 | Calendar + iCal | 4 | ⬜ |
| 12 | Telegram Bot | 9 | ⬜ |
| 13 | Marketplace + Public Pages + Payment Skeleton | 4 | ⬜ |
| 14 | Production Deploy + Security + Legal Pages | все | ⬜ |

---

## 12. Claude Code Automation Setup (для AICheck-проекта)

После клонирования репозитория в Chunk 1 — выполнить настройку автоматизации Claude Code. Это сильно ускорит дальнейшую работу.

### 🪝 Hooks (`.claude/settings.json`)

| Hook | Команда | Назначение |
|------|---------|------------|
| `PostToolUse` (Edit/Write) | `python3 scripts/check_anonymizer.py` | После каждой правки в `app/services/ai/` — запустить snapshot-тест анонимизатора |
| `PostToolUse` (Edit) | `ruff check apps/api && eslint apps/web` | Авто-линт после изменений |
| `Stop` | `python3 scripts/update_status.py` | Обновить `docs/STATUS.md` после завершения сессии |
| `UserPromptSubmit` | проверка наличия CLAUDE.md и rules/ | Гарантирует, что правила загружены в каждый запрос |
| `PreToolUse` (Bash) | проверка опасных команд (rm -rf, force push в main) | Блокировка деструктивных действий |

### 🛠 Skills (custom + плагинные)

**Использовать готовые плагины:**
- `commit` — автокоммит после логических блоков (включён через скилл из глобальной конфигурации)
- `code-reviewer` — независимое ревью перед merge feature-branch в main
- `qa` — генерация и запуск тестов перед approve чанка
- `frontend-design` — для построения UI с продуманным дизайном (Chunk 4-13 UI)
- `claude-md-management:revise-claude-md` — обновлять CLAUDE.md проекта после крупных изменений
- `claude-code-setup:claude-automation-recommender` — **запустить в Chunk 1** для конкретных рекомендаций под текущий codebase

**Custom skills для AICheck:**
- `chunk-status` — пометить чанк готовым в `docs/STATUS.md`
- `pii-audit` — аудит логов и БД на наличие утечек PII (запускать перед каждым релизом)
- `legal-check` — проверка наличия и доступности юридических страниц
- `ocr-validate` — валидация качества OCR на ground-truth наборе

### 🤖 Subagents (custom)

- `mathpix-validator` — запускать после изменений в `app/services/ai/ocr/`, проверяет accuracy на эталонном датасете
- `prompt-tester` — тестирует промпты Claude/GPT на наборе типовых кейсов, выявляет регрессии
- `accessibility-checker` — a11y-аудит UI компонентов (WCAG AA минимум)
- `legal-reviewer` — после изменений в `docs/legal/` проверяет соответствие 152-ФЗ

### 🔌 MCP Servers (рекомендованы)

- `filesystem` — для безопасной работы с файлами проекта
- `playwright` — для e2e-тестов UI (особенно critical flow: загрузка фото → проверка → отчёт)
- `postgres` — прямая работа с БД при дебаге миграций
- `github` — автоматизация PR, ревью, статусов чеков
- `context7` — документация библиотек (FastAPI, Next.js, SQLAlchemy, Anthropic SDK) — уже доступен

### 🧩 Workflow для feature-разработки (через `feature-dev`)

Стандартный flow для каждого UI-чанка:
1. **Explore** (`feature-dev:code-explorer`) — понять существующую архитектуру в текущем монорепо
2. **Plan** (`feature-dev:code-architect`) — продумать blueprint фичи
3. **Запросить дизайн-референсы** у пользователя
4. **Implement** — пишем код, коммитим часто
5. **Review** (`feature-dev:code-reviewer`) — независимое ревью с фильтром high-confidence issues
6. **QA** (`qa` skill) — генерация и запуск тестов
7. **Commit + push** (`commit` skill) на feature-branch
8. **Merge в main** при достижении критериев готовности чанка

### 🎯 Конкретные действия в Chunk 1

После клонирования репозитория и базового setup'а:
1. Запустить `claude-code-setup:claude-automation-recommender` для финальных рекомендаций
2. Создать `.claude/settings.json` с базовыми hooks (выше)
3. Создать `.claude/agents/` с 4 custom subagents
4. Создать `.claude/skills/` с 4 custom skills
5. Запустить `claude-md-management:revise-claude-md` для генерации проектного `CLAUDE.md` из накопленных знаний
6. Перенести текущий глобальный `CLAUDE.md` в `rules/` проекта как референс

---

## 13. Верификация

### End-to-end сценарий MVP

1. **Регистрация репетитора** через email magic-link
2. **Создание ученика** по псевдониму ("Иван И.") — без ФИО, без паспортного согласия
3. **Опциональная привязка email родителя** с галочкой согласия на отчёты
4. **Создание группы** из 3 учеников
5. **Реферальная ссылка** для приглашения ещё одного ученика
6. **Создание задания на группу** (с шаблона или дублированием)
7. **Загрузка фото работы** учеником через `/submit/...?token=...` (виртуальный) или через свой кабинет
8. **AI-проверка** за < 60 секунд, WebSocket-уведомление учителю
9. **Просмотр результата** с side-by-side оригинала и LaTeX, теги ошибок, черновик-комментарий, score_draft (по выбранному уровню строгости)
10. **Approve учителем** → отчёт родителю на email + Telegram-уведомление ученику
11. **Аналитика** обновляется, видны сравнения "Ученик vs Группа"
12. **Календарь** с занятиями + экспорт `.ics`
13. **Публичная страница** `teacher/{slug}` с реферальной ссылкой работает

### Технические проверки
- [ ] `make test` зелёный
- [ ] `npm run typecheck` зелёный
- [ ] `mypy apps/api` зелёный
- [ ] PostgreSQL: explain plan на топ-запросах < 50ms
- [ ] Lighthouse PWA score > 90
- [ ] Стоимость проверки одной работы = $0.04-0.06 (в бюджете)
- [ ] Snapshot-тесты анонимизатора: PII не уходит в API

### Юридические проверки
- [ ] Политика конфиденциальности и оферта опубликованы
- [ ] Уведомление в РКН подано (статус виден в реестре или подтверждение)
- [ ] Никакие PII не уходят в Mathpix/Claude/Gemini API (audit log)
- [ ] Все базы данных физически на серверах в РФ
- [ ] Самозанятый/ИП оформлен

---

## 14. Дальнейшие шаги (после одобрения плана)

1. **Сначала Chunk 0.5** (documentation bootstrap) — выгружаем на GitHub весь документационный пакет, никакого кода. Получаем PR, пользователь ревьюит, мержим в main.
2. **Затем параллельно:** Chunk 0 (юр. трек) + Chunk 1 (setup инфраструктуры — код, docker, apps).
3. **После Chunk 7 — обязательная валидация Mathpix** на 50+ реальных работах. Go/no-go для AI-pipeline.
4. **После Chunk 9** — первый бета-тест с 3-5 знакомыми репетиторами.
5. **После Chunk 14** — закрытый запуск с 10-20 репетиторами через сарафан + реферальную программу.
6. **После 50+ репетиторов** — открытие маркетплейса публично.
7. **После 500к/мес выручки + 100+ активных репетиторов** — заявка в ФРИИ (5 млн руб за 7%) для Series-A trajectory.

### Метрики успеха MVP
- 30+ активных репетиторов через 3 месяца
- > 80% retention на 4-й неделе
- NPS > 40
- Среднее время проверки одной работы < 5 минут (с момента загрузки)
- Стоимость проверки укладывается в $0.05-0.08

### Дизайн-референсы
**Когда присылать:** до Chunk 5 (когда начинается UI с фото). Минимум — до Chunk 9 (полноценный dashboard). Если есть Figma-макеты — сразу. Если только идеи/референсы — формат: ссылки на сайты + комментарии "вот этот блок похож на нужное".

---

## 15. Решённые и открытые вопросы

### Решённые (из обсуждения):
- ✅ **Доменное имя:** **`.ru`** (рекомендация). Российская аудитория + 152-ФЗ + локализация в РФ + повышенное доверие. Параллельно зарезервировать `.com` (~$10/год) для будущей международной экспансии
- ✅ Тарифы подписки: рассчитать после первого месяца usage data
- ✅ Расширение на не-STEM (русский, литература): отдельный pipeline пост-MVP
- ✅ B2B (школы/мини-курсы) + кластеризация: после product-market fit
- ✅ Венчурное финансирование (ФРИИ): после 500к/мес выручки + 100+ юзеров
- ✅ Уровень дозволенности AI: в профиле учителя (Chunk 4)
- ✅ Дизайн-референсы: запрашиваются перед каждым UI-чанком

### На обсуждение перед стартом:
- Имя сервиса для домена: AICheck.ru? AICheck.app? (зарезервировать оба варианта если оба свободны)
- Решение по OCR-провайдеру (Chunk 7) — будет принято после валидации на 50 работах
- Точные SLA посредника для GPT/Claude API (доступность, гарантии)
