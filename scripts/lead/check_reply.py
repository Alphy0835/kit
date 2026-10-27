"""Проверка ответа тим лида владельцу.

Ловит то, что повторялось в поправках владельца, хотя правило было записано:
нет блока «Что дальше», команда задачи вне блока кода, путь к файлу текстом, номер решения.

Запуск на черновик:
    python check_reply.py ответ.md
    python check_reply.py < ответ.md
Запуск хуком Stop из шапки скила тим лида: хук живёт с вызова скила до конца сессии. На входе JSON события,
ответ — поле `last_assistant_message`, запасной путь — журнал чата.
    python check_reply.py --hook

Код возврата: 0 — находок нет, 1 — есть находки (с файла), 2 — есть находки (хук: модель получит их и поправит
ответ один раз). Справка — `references/process/reply.md`.
"""
import argparse
import json
import re
import sys

FENCE = re.compile(r'^ *```.*?^ *```[^\n]*$', re.S | re.M)
LINK = re.compile(r'\[[^\]]*\]\([^)]*\)')
TASK_CMD = re.compile(r'(?:^|(?<=[\s`(«"]))/(?:[a-z][\w-]*:)?[a-z][\w-]*[ \t]+[A-Z]+_TASK_\d+', re.M)
ABS_PATH = re.compile(r'(?<![\w/])(?:[A-Za-z]:[\\/][^\s`)»"]+|/[a-z]/Users/[^\s`)»"]+)')
DECISION = re.compile(r'(?<![\w-])D-\d{2,3}(?!\d)')
NEXT = re.compile(r'что дальше', re.I)


def findings(text):
    """Список находок по тексту ответа."""
    out = []
    if not NEXT.search(text):
        out.append('Нет блока «Что дальше»: последним блоком — следующие шаги владельца.')
    prose = LINK.sub(' ', FENCE.sub(' ', text))
    for m in TASK_CMD.finditer(prose):
        out.append('Команда задачи вне блока кода: «%s». Одна команда — отдельный блок ```.' % m.group(0).strip())
    for m in ABS_PATH.finditer(prose):
        out.append('Путь к файлу текстом: «%s». Приложи файл или дай ссылку, которая открывается щелчком.'
                   % m.group(0).rstrip('.,;:'))
    seen = set()
    for m in DECISION.finditer(prose):
        if m.group(0) not in seen:
            seen.add(m.group(0))
            out.append('Номер решения «%s»: скажи словами, что решили, номер владельцу ничего не говорит.'
                       % m.group(0))
    return out


def text_blocks(content):
    if isinstance(content, str):
        return [content]
    return [b.get('text', '') for b in content or [] if isinstance(b, dict) and b.get('type') == 'text']


def last_reply(path):
    """Запасной путь: последний текст модели из журнала, если событие его не принесло."""
    last = ''
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get('type') == 'assistant':
                text = '\n'.join(t for t in text_blocks(entry.get('message', {}).get('content')) if t.strip())
                if text:
                    last = text
    return last


def main():
    ap = argparse.ArgumentParser(description='Проверка ответа тим лида владельцу.')
    ap.add_argument('file', nargs='?', help='файл с текстом ответа; без него — стандартный ввод')
    ap.add_argument('--hook', action='store_true', help='запуск хуком Stop')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    if args.hook:
        sys.stdin.reconfigure(encoding='utf-8')
        event = json.load(sys.stdin)
        if event.get('stop_hook_active'):
            return 0
        text = event.get('last_assistant_message')
        if text is None and event.get('transcript_path'):
            text = last_reply(event['transcript_path'])
        found = findings(text) if text and text.strip() else []
        if found:
            print('Проверка ответа владельцу (references/process/reply.md). Поправь и ответь заново:\n- '
                  + '\n- '.join(found), file=sys.stderr)
            return 2
        return 0

    if args.file:
        with open(args.file, encoding='utf-8') as f:
            text = f.read()
    else:
        sys.stdin.reconfigure(encoding='utf-8')
        text = sys.stdin.read()
    found = findings(text)
    for item in found:
        print('- ' + item)
    if not found:
        print('Находок нет.')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
