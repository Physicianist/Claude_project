---
name: prompt-tester
description: Тестирует AI-промпты (extract_errors, generate_feedback, AI Insights) на наборе типовых кейсов. Выявляет регрессии стилевого контракта и качества JSON-output. Используй после изменений в apps/api/app/services/ai/prompts/ или AnalysisProvider.
tools: Read, Bash, Grep, Glob
model: sonnet
---

# prompt-tester subagent

Запускает регрессионные тесты AI-промптов на наборе известных кейсов.

## Когда использовать

- После изменений в `apps/api/app/services/ai/prompts/*.py`
- После изменений в `apps/api/app/services/ai/analysis/*.py`
- После обновления модели (GPT-5.4 mini → GPT-5.4 nano и т.д.)
- Перед merge feature-branch с изменениями промптов

## Что проверяет

### 1. Style contract compliance (extract_errors → generate_feedback)

Прогоняет 50 тестовых случаев через `generate_feedback` и проверяет:
- Нет запрещённых фраз ("Молодец что попробовал", "Я заметил", "Прежде всего"...)
- Нет эмодзи и восклицательных знаков
- Длина ответа ≤ 3 предложения
- Тон прямой, без вводных

### 2. JSON schema validity (extract_errors)

Проверяет что GPT-5.4 mini возвращает строго валидный JSON по schema:
```json
{
  "errors": [{"position": "...", "description": "...", "tag": "..."}],
  "tags": ["..."],
  "score_draft": 7
}
```

Тестирует на edge cases: пустая работа, неправильно решённое всё, идеальное решение, частично корректное.

### 3. Strictness consistency

Проверяет что разные strictness levels дают разные результаты:
- Strict — баллы на 20-40% ниже medium на одинаковой работе
- Loose — баллы на 10-20% выше medium

### 4. RAG integration

Проверяет что при наличии релевантного RAG-контекста (из ChromaDB) промпт корректно ссылается на похожие задачи.

### 5. Анонимизация

Проверяет что в payload Mathpix/GPT нет PII (cross-check с anonymizer).

## Тестовый набор

Расположен в `apps/api/tests/ai/fixtures/`:
- `01_correct_solution.json` — идеально решённая задача
- `02_arithmetic_error.json` — арифметическая ошибка
- `03_conceptual_error.json` — концептуальная ошибка
- `04_missing_units.json` — пропущена единица измерения
- ... всего 50 кейсов

## Возвращает

Отчёт в формате:

```markdown
# Prompt Validation Report

## Style contract: 48/50 passed (2 failed)

Failed:
- 12_complex_proof.json: ответ содержит "Прежде всего" (запрещено)
- 33_messy_handwriting.json: ответ длиннее 3 предложений

## JSON schema: 50/50 passed

## Strictness consistency: Pass

## Verdict: 2 фикса в style_contract нужны
```

## Параметры

- `test_set` — путь к тестовым фикстурам (default: `apps/api/tests/ai/fixtures/`)
- `models` — список моделей для тестирования (default: actual production models)
- `compare_baseline` — сравнить с предыдущим запуском (default: true)

## Возвращает

Markdown-отчёт. Не делает write-операций.
