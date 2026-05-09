---
name: ocr-validate
description: Валидация OCR-провайдеров (Mathpix-only / Mathpix+YandexVision гибрид / Gemini one-shot) на ground-truth наборе из 50 реальных рукописных работ. Запускается в Chunk 7 для go/no-go выбора OCR_PROVIDER.
---

# ocr-validate

Валидирует качество OCR на эталонном наборе и выбирает дефолтный провайдер.

## Когда использовать

- В Chunk 7 — обязательная go/no-go проверка перед началом Chunk 8
- При изменениях в `apps/api/app/services/ai/ocr/`
- Раз в квартал — regression-тест

## Подготовка эталонного набора

1. Собрать 50 реальных рукописных работ от знакомых репетиторов:
   - 30 математика (формулы + русский текст)
   - 10 физика (формулы + чертежи)
   - 10 химия (формулы + текст)

2. Для каждого фото подготовить ground-truth:
   - `apps/api/scripts/ocr_groundtruth/<id>.png` — оригинал
   - `apps/api/scripts/ocr_groundtruth/<id>.json` — `{ "latex": "...", "text": "..." }`

## Что делает

Запускает `python3 apps/api/scripts/validate_ocr.py`:

1. Прогоняет все 50 работ через каждого из 3 провайдеров:
   - `mathpix_only`
   - `mathpix_yandex_hybrid`
   - `gemini_oneshot`

2. Для каждой работы вычисляет:
   - Accuracy LaTeX (Levenshtein distance, normalized)
   - Accuracy текста (CER — Character Error Rate)
   - Время обработки (p50, p95)
   - Стоимость

3. Выдаёт сводную таблицу:

```
Провайдер              | Accuracy LaTeX | Accuracy текст | Время p95 | Стоимость/стр
mathpix_only           | 92%            | 78%            | 4.2 s     | $0.005
mathpix_yandex_hybrid  | 91%            | 94%            | 6.8 s     | $0.0065
gemini_oneshot         | 89%            | 92%            | 3.1 s     | $0.003
```

4. Рекомендация дефолтного провайдера на основе:
   - Если Accuracy LaTeX < 85% у всех — alarm, нужен fallback на YOLO custom training
   - Если Accuracy текста < 80% у `mathpix_only` — выбираем гибрид или Gemini
   - При прочих равных — выбираем самый быстрый и дешёвый

5. Записывает выбор в `.env`: `OCR_PROVIDER=...`

6. Создаёт отчёт `tmp/ocr-validation-{date}.md` с таблицей и рекомендацией

## Критерии Go/No-Go

- **Go:** хотя бы один провайдер показывает Accuracy LaTeX ≥ 85% И Accuracy текста ≥ 80%
- **No-Go:** все три провайдера ниже порога → нужно либо подождать улучшений, либо добавить YOLO custom-training (увеличит scope на 1-2 недели)

## Параметры

- `dataset_path` — путь к папке с ground-truth (default: `apps/api/scripts/ocr_groundtruth/`)
- `providers` — список провайдеров для проверки (default: все 3)
- `output_format` — `markdown` (default) / `json`

## Файлы

- `apps/api/scripts/validate_ocr.py` — главный скрипт
- `apps/api/scripts/ocr_groundtruth/` — ground-truth dataset
- `apps/api/app/services/ai/ocr/` — провайдеры
- `tmp/ocr-validation-*.md` — отчёты
