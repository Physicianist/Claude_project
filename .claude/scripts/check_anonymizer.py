#!/usr/bin/env python3
"""
Snapshot-тест анонимизатора: убедиться что PII не уходит в AI-сервисы.

Заглушка до Chunk 7. После Chunk 7 этот скрипт будет:
1. Импортировать `apps.api.app.services.ai.anonymizer.anonymize`
2. Прогонять тестовые payload с реальными ФИО/email/phone
3. Проверять что в выходе только pseudo_id и контент
4. Возвращать exit code 0/1
"""
from __future__ import annotations
import sys
from pathlib import Path


def main() -> int:
    anonymizer_path = Path("apps/api/app/services/ai/anonymizer.py")
    if not anonymizer_path.exists():
        print("[anonymizer-check] Skipped — anonymizer not implemented yet (will activate in Chunk 7)")
        return 0

    # TODO Chunk 7: реализовать реальную проверку
    print("[anonymizer-check] TODO — implement actual check after Chunk 7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
