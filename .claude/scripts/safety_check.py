#!/usr/bin/env python3
"""
Pre-tool-use hook для Bash-команд: блокирует опасные операции.

Принимает hook input через stdin (JSON с tool_input.command) и возвращает
exit code 0 (разрешить) или 2 (заблокировать) с сообщением в stderr.
"""
from __future__ import annotations
import json
import re
import sys


# Опасные паттерны команд, которые надо блокировать
DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\brm\s+-rf?\s+/(?:\s|$)"), "rm -rf на корне файловой системы"),
    (re.compile(r"\brm\s+-rf?\s+~(?:\s|$|/)"), "rm -rf на домашней директории"),
    (re.compile(r"git\s+push\s+(?:--force|-f)\s+(?:origin\s+)?main\b"), "force push в main"),
    (re.compile(r"git\s+reset\s+--hard\s+(?:origin/)?main\b"), "reset --hard на main"),
    (re.compile(r"git\s+config\s+--global\b"), "изменение глобального git config"),
    (re.compile(r"docker\s+(?:rm|kill)\s+-f\s+\$\(docker\s+ps"), "массовое удаление контейнеров"),
    (re.compile(r"DROP\s+DATABASE\b", re.IGNORECASE), "DROP DATABASE"),
    (re.compile(r"TRUNCATE\s+TABLE\b", re.IGNORECASE), "TRUNCATE TABLE"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    for pattern, description in DANGEROUS_PATTERNS:
        if pattern.search(command):
            print(
                f"[safety-check] Blocked: {description}\n"
                f"   Command: {command}\n"
                f"   If this is really needed, ask user to run manually.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
