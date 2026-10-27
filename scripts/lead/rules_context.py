"""Правила владельца в начале чата.

Хук SessionStart плагина: в проекте с `kit.toml` подкладывает агенту два файла правил — общий файл владельца
(на все проекты) и файл продукта. Срабатывает на старте, возобновлении и после сжатия контекста, поэтому правила
не теряются. В проекте без `kit.toml` молчит.

Пути:
    общий файл — переменная окружения KIT_OWNER_RULES, иначе ~/.claude/kit/owner.md;
    файл продукта — `[rules] project` в kit.toml, иначе team/RULES.md.

Запуск хуком:
    python rules_context.py --hook          (на входе JSON события, поле `cwd`)
Запуск руками — посмотреть, что получит агент:
    python rules_context.py [папка проекта]

Код возврата всегда 0: сбой хука не должен мешать чату. Справка — `references/process/owner-rules.md`.
"""
import argparse
import json
import os
import sys
import tomllib
from pathlib import Path

HEAD = ("Правила владельца для этого проекта. Выполняй их наравне с правилами скила. Правило противоречит скилу "
        "или другому правилу — скажи владельцу до работы, не выбирай молча. Новое правило записывает тим лид: "
        "references/process/owner-rules.md.")


def find_root(start):
    """Ближайшая вверх папка с kit.toml или None."""
    path = Path(start).resolve()
    for folder in (path, *path.parents):
        if (folder / "kit.toml").is_file():
            return folder
    return None


def rules_text(path):
    """Строки правил из файла: только пункты списка, без заголовков и пояснений шаблона."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    return [line for line in lines if line.lstrip().startswith(("- ", "* "))]


def build(root):
    owner = Path(os.environ.get("KIT_OWNER_RULES") or Path.home() / ".claude" / "kit" / "owner.md")
    project_rel = "team/RULES.md"
    try:
        with open(root / "kit.toml", "rb") as f:
            project_rel = tomllib.load(f).get("rules", {}).get("project", project_rel)
    except (OSError, tomllib.TOMLDecodeError):
        pass
    project = root / project_rel

    parts = []
    for title, path in (("Общие правила владельца", owner), ("Правила продукта", project)):
        rules = rules_text(path)
        parts.append(f"## {title} ({path})\n" + ("\n".join(rules) if rules else "Пока пусто."))
    return HEAD + "\n\n" + "\n\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs="?", default=".")
    parser.add_argument("--hook", action="store_true")
    args = parser.parse_args()

    start = args.folder
    if args.hook:
        try:
            start = json.load(sys.stdin).get("cwd") or os.getcwd()
        except (ValueError, AttributeError):
            start = os.getcwd()

    root = find_root(start)
    if root is None:
        return 0
    text = build(root)
    if args.hook:
        out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}
        sys.stdout.write(json.dumps(out, ensure_ascii=True))
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
