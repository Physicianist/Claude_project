#!/usr/bin/env python3
"""
Обновляет docs/STATUS.md в конце сессии: проставляет дату последней активности.

Заглушка. Реальная логика после Chunk 1: парсить текущую feature-branch (chunk/NN),
обновлять статус соответствующего чанка в STATUS.md.
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import date


def main() -> int:
    status_path = Path("docs/STATUS.md")
    if not status_path.exists():
        print("[status-update] STATUS.md not found, skipping")
        return 0

    # TODO Chunk 1+: реализовать реальное обновление статус-таблицы
    # На основе git branch: chunk/NN-name -> найти строку в STATUS.md -> обновить дату
    print(f"[status-update] TODO — current date: {date.today()}, parse git branch and update STATUS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
