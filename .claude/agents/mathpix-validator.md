---
name: mathpix-validator
description: Запускает регрессионные тесты OCR-провайдеров на ground-truth датасете. Проверяет accuracy LaTeX и русского текста, время обработки, стоимость. Используй после изменений в apps/api/app/services/ai/ocr/ или раз в квартал.
tools: Read, Bash, Grep, Glob
model: sonnet
---

# mathpix-validator subagent

Запускает регрессионные OCR-тесты и возвращает структурированный отчёт.

## Когда использовать

- После любых изменений в `apps/api/app/services/ai/ocr/*.py`
- После обновления версий внешних SDK (mathpix, google-genai, yandexcloud)
- Перед merge feature-branch с изменениями OCR в main
- Раз в квартал как regression check

## Входные данные

Subagent сам:
1. Находит ground-truth датасет в `apps/api/scripts/ocr_groundtruth/`
2. Если датасета нет — возвращает ошибку с инструкцией как собрать
3. Если датасет < 30 работ — предупреждает что валидация неполная

## Что делает

1. Запускает `python3 apps/api/scripts/validate_ocr.py --providers all --output json`
2. Парсит результаты
3. Сравнивает с базовой линией (предыдущий запуск, сохранён в `tmp/ocr-baseline.json`)
4. Выявляет регрессии (accuracy упала >2%, время выросло >50%, цена выросла >20%)
5. Возвращает отчёт под 500 слов:
   - Текущие метрики по 3 провайдерам
   - Сравнение с baseline
   - Найденные регрессии (если есть)
   - Рекомендация: можно ли мерджить или нужен фикс

## Формат отчёта

```markdown
# OCR Validation Report — 2026-XX-XX

## Текущие метрики

| Провайдер | LaTeX | Текст | p95 время | Цена/стр |
|-----------|-------|-------|-----------|----------|
| mathpix_only | 92.3% | 78.1% | 4.2s | $0.005 |
| ... |

## Сравнение с baseline (2026-XX-XX)

| Провайдер | Δ LaTeX | Δ Текст | Δ Время |
|-----------|---------|---------|---------|
| mathpix_only | -0.5% | +1.2% | +0.3s |

## Регрессии: НЕТ / [список]

## Вердикт: можно мерджить / требуется фикс
```

## Параметры

- `min_dataset_size` — минимум работ для валидной проверки (default 30)
- `regression_threshold_accuracy` — допустимое падение accuracy (default 2%)
- `regression_threshold_time_pct` — допустимый рост времени p95 (default 50%)

## Возвращает

Markdown-отчёт. Не делает write-операций.
