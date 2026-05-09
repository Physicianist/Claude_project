# Git Workflow

## Принципы

1. **Каждый чанк → feature-branch.** Имя: `chunk/NN-name` (например, `chunk/01-setup`, `chunk/07-ocr-pipeline`).
2. **Коммиты часто.** После каждого логически осмысленного изменения, не накапливать.
3. **Push часто.** Не держать локально несколько дней. Push даёт пользователю видимость прогресса.
4. **Merge в `main` — только после критериев готовности чанка** + одобрения PR пользователем.
5. **Никогда не амендить опубликованные коммиты.** Создавать новый коммит.
6. **Никогда не делать force push в `main`.** Только в feature-branch если нужно.
7. **Никогда не обновлять git config** без явного разрешения пользователя.
8. **Никогда не пропускать pre-commit hooks** (`--no-verify`). Если hook упал — починить причину.

## Стандартный flow

```bash
# 1. Старт нового чанка
git checkout main
git pull origin main
git checkout -b chunk/07-ocr-pipeline

# 2. Работа с частыми коммитами
# ... меняем файлы ...
git add apps/api/app/services/ai/ocr/base.py
git commit -m "Chunk 7: добавил OCRProvider abstract base class"
git push origin chunk/07-ocr-pipeline

# ... ещё изменения ...
git add apps/api/app/services/ai/ocr/mathpix_only.py
git commit -m "Chunk 7: реализован Mathpix-only провайдер"
git push origin chunk/07-ocr-pipeline

# 3. Завершение чанка
# - убедиться что все критерии готовности из docs/plan.md выполнены
# - запустить тесты: make test
# - запустить линтеры: make lint
# - обновить docs/STATUS.md (статус чанка → 🟦 → ✅, проставить дату)

git add docs/STATUS.md
git commit -m "Chunk 7: complete — обновлён STATUS"
git push origin chunk/07-ocr-pipeline

# 4. Создать PR через веб-интерфейс GitHub:
#    https://github.com/Physicianist/Claude_project/compare/main...chunk/07-ocr-pipeline
#    Заголовок: "Chunk 7: OCR Pipeline (3 провайдера) + Celery + анонимизация"
#    Описание: ссылка на план + чеклист критериев готовности

# 5. Ревью пользователем → одобрение → merge в main

# 6. Локально удалить feature-branch
git checkout main
git pull origin main
git branch -d chunk/07-ocr-pipeline
```

## Формат commit-сообщений

```
Chunk N: краткое описание (имп. форма)

[опционально] Подробности в виде bullet-points:
- что добавлено
- что изменено
- какая проблема решена

[опционально] Co-authored с Claude:
Co-Authored-By: Claude <noreply@anthropic.com>
```

Примеры:

```
Chunk 7: добавил OCRProvider ABC с тремя реализациями
```

```
Chunk 8: внедрил двухуровневый AI-анализ

- GPT-5.4 mini для extract_errors (structured JSON)
- GPT-5.4 для generate_feedback с применением style_contract
- Claude Sonnet 4.6 как fallback при сбое любого шага
- Snapshot-тесты на 50 примерах для проверки анти-AI стиля
```

## Что коммитить НЕЛЬЗЯ

- `.env` файлы с реальными секретами
- `node_modules/`, `__pycache__/`, `.next/` и другие build-артефакты
- Большие бинарные файлы (>5 МБ) без LFS
- Временные/локальные конфиги (`docker-compose.override.yml`, `.scratchpad/`)
- Логи, базы данных, dump-файлы

Все эти паттерны — в [`.gitignore`](../../.gitignore).

## Защита `main`

После Chunk 14 — настроить branch protection rules на GitHub:
- Require pull request before merging
- Require status checks (CI должен пройти)
- Require linear history (no merge commits)
- Restrict who can push (только владелец репозитория)

## Если всё пошло не так

- **Коммит с секретом** — не паниковать, сразу: `git rebase -i` (если ещё не запушено) или объявить ключ скомпрометированным и создать новый, плюс добавить в `.gitignore`.
- **Конфликт при merge** — не разрушать работу, а разрешать через `git merge` (не `git reset --hard`).
- **Пропустил `git pull`** — `git pull --rebase` чтобы избежать merge-commits.
- **Потерял ветку** — `git reflog` показывает все HEAD-движения, можно восстановить.
