"""Поводы позвать безопасника — по правке ветки.

Тим лид запускает при приёмке, безопасник — первым шагом проверки:
    python triggers.py                     # правка текущей ветки против main
    python triggers.py --ref task/CB_TASK_123
Скрипт смотрит добавленные строки и изменённые файлы и называет поводы: новый вход снаружи, права, вход и
сессия, секреты, вебхук, вызов ИИ, запрос к базе, вывод в страницу, исполнение команд, файлы и внешние адреса,
предел, зависимости, выкладка, файлы правил агентов, исправление прошлой находки. У повода — номера классов из
references/security/classes.md: по ним безопасник выбирает охотников.

Повод — не дыра. Скрипт не судит, защищён ли код: он говорит, что правка задела место, где дыры бывают.

Код возврата: 0 — поводов нет, 1 — есть повод (позвать безопасника), 2 — ошибка запуска или настройки.
Настройка — раздел [security] файла kit.toml (образец — assets/kit.example.toml): свои поводы, пропуски.
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys
import tomllib

# Классы — номера разделов references/security/classes.md.
# added — регулярное выражение по добавленной строке кода; files — шаблоны путей изменённых файлов.
TRIGGERS = [
    {'name': 'Новый вход снаружи', 'classes': [1, 2, 5],
     'added': r'''@\w+\.(?:get|post|put|patch|delete|route|websocket|api_route)\(|\bAPIRouter\(|add_url_rule\(|'''
              r'''\b(?:app|router)\.(?:get|post|put|patch|delete|use|all)\(\s*["'`/]'''},
    {'name': 'Права и роли', 'classes': [2, 1],
     'added': r'''(?i)(?:\bpermissions?\b|\bperms?\b|is_admin|is_superuser|superadmin|has_perm\w*|'''
              r'''allowed_roles|check_access|Depends\(\s*require_\w+|dependencies\s*=|status_code\s*=\s*403)'''},
    {'name': 'Вход и сессия', 'classes': [3, 9],
     'added': r'''(?i)(?:password|passwd|reset_token|set_cookie|\bjwt\b|\blogout\b|session_id|invalidate|'''
              r'''bcrypt|argon2|pbkdf2|\botp\b|httponly|samesite)'''},
    {'name': 'Секрет и данные наружу', 'classes': [4],
     'added': r'''(?i)(?:(?:\blog(?:ger|ging)?\.\w+\(|\bprint\(|\bdetail\s*=|\braise\s+\w+\().*'''
              r'''(?:token|secret|api_?key|password|authorization|bearer)'''
              r'''|(?:getenv|environ)\b.*(?:TOKEN|SECRET|KEY|PASSWORD)'''
              r'''|getLogger\(\s*["'](?:httpx|httpcore|urllib3|requests|aiohttp)'''
              # Правка скрывает секреты — значит, секрет где-то рядом идёт наружу. Проба 16.10: исполнитель
              # скрыл секреты для панели, а в журнал процесса они ушли открытым текстом.
              r'''|\bredact\w*|\bmask_(?:secret|token|key)\w*|REDACTED'''
              r'''|https?://[^\s"']*\{[^}]*(?:token|key|secret)[^}]*\})''',
     'files': ['.env', '*/.env', '.env.local', '*/.env.local', '*.pem', '*.key', '*id_rsa*', '*credentials*.json']},
    {'name': 'Новый секрет в настройке', 'classes': [4],
     'in_files': ['*.env.example', '*.env.sample', '*/.env.example', '*/.env.sample'],
     'added': r'''(?i)^\s*\w*(?:TOKEN|SECRET|API_?KEY|PASSWORD|PRIVATE_KEY)\w*\s*='''},
    {'name': 'Вебхук и события чужих систем', 'classes': [5],
     'added': r'''(?i)(?:webhook|signature|\bhmac\b|x-[\w-]*signature|secret_token|compare_digest)'''},
    {'name': 'Вызов ИИ и база знаний', 'classes': [8, 9],
     'added': r'''(?i)(?:\banthropic\b|\bopenai\b|messages\.create|chat\.completions|system_prompt|\bprompt\b|'''
              r'''\bembedding|knowledge|\brag\b|\bllm\b)'''},
    {'name': 'Запрос к базе', 'classes': [6, 1],
     'added': r'''(?i)(?:execute(?:many)?\(\s*f["']|execute(?:many)?\([^)]*(?:["']\s*%|\.format\()|'''
              r'''\btext\(\s*f["']|\.raw\(|ORDER BY\s*["']?\s*[+{])'''},
    {'name': 'Вывод в страницу', 'classes': [7],
     'added': r'''(?:innerHTML|outerHTML|insertAdjacentHTML|dangerouslySetInnerHTML|\|\s*safe\b|\bMarkup\(|'''
              r'''document\.write|v-html|autoescape\s*=\s*False)'''},
    {'name': 'Исполнение команд и разбор данных', 'classes': [6],
     'added': r'''(?:\bsubprocess\b|os\.system\(|os\.popen\(|shell\s*=\s*True|\beval\(|\bexec\(|\bpickle\b|'''
              r'''yaml\.load\(|marshal\.loads|verify\s*=\s*False|new Function\()'''},
    {'name': 'Файлы и загрузки', 'classes': [10],
     'added': r'''(?:\bsend_file\(|\bFileResponse\(|\bUploadFile\b|request\.files|\bsend_from_directory\(|'''
              r'''os\.path\.join\([^)]*\b(?:request|filename)\b)'''},
    # Запрос наружу сам по себе частый. Повод — когда в том же файле правка трогает ключ: ключ уходит с запросом
    # и может вернуться в тексте ошибки или журнале.
    {'name': 'Запрос на внешний адрес', 'classes': [10, 4], 'weak': True,
     'strong_if': r'''(?i)(?:token|secret|api_?key|authorization|bearer|password)''',
     'added': r'''(?:\brequests\.(?:get|post|put|request)\(|\bhttpx\.(?:get|post|AsyncClient|Client)\b|\baiohttp\b|'''
              r'''\burlopen\(|\bfetch\(|\b\w*http\w*\.request\()'''},
    {'name': 'Предел и дорогие действия', 'classes': [9, 3], 'weak': True,
     'added': r'''(?i)(?:rate_?limit|throttl|max_attempts|lockout|retry_after|\b429\b|broadcast|рассылк)'''},
    {'name': 'Зависимости', 'classes': [11],
     'files': ['requirements*.txt', '*/requirements*.txt', 'pyproject.toml', '*/pyproject.toml', '*.lock',
               'Pipfile*', '*/Pipfile*', 'package.json', '*/package.json', 'package-lock.json',
               '*/package-lock.json', 'pnpm-lock.yaml', '*/pnpm-lock.yaml']},
    {'name': 'Docker и выкладка', 'classes': [11, 4],
     'files': ['Dockerfile*', '*/Dockerfile*', '*docker-compose*', '*compose*.y*ml', '.github/workflows/*',
               '*deploy*', '*nginx*', '*.service']},
    {'name': 'Файлы правил агентов', 'classes': [], 'see': 'references/security/vetting.md, раздел 3', 'docs': True,
     'files': ['CLAUDE.md', '*/CLAUDE.md', 'AGENTS.md', '*/AGENTS.md', '.claude/*', '*/.claude/*', '.mcp.json',
               '*/.mcp.json', '*SKILL.md', '*.cursorrules']},
]

# Слова в сообщениях коммитов ветки: правка исправляет находку — её перепроверяет безопасник.
FIX_WORDS = r'(?i)(?:безопасн|уязвим|утечк|\bsecurity\b|\bvuln|CVE-\d|\bxss\b|injection|инъекц|чужо[йг]о? )'

DEFAULTS = {
    'code': ['*.py', '*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx', '*.vue', '*.svelte', '*.html', '*.jinja', '*.j2',
             '*.sql', '*.sh', '*.ps1'],
    'skip': ['*/tests/*', 'tests/*', '*test_*.py', '*_test.py', '*.test.js', '*.spec.js', '*.test.ts',
             '*.spec.ts', '*/node_modules/*', '*/vendor/*', '*.min.js'],
}


class Setup(Exception):
    """Ошибка запуска: нет git, нет ветки, плохая настройка."""


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, encoding='utf-8',
                       errors='replace')
    if r.returncode != 0:
        raise Setup('git %s: %s' % (' '.join(args), r.stderr.strip()))
    return r.stdout


def added_lines(repo, base, ref):
    """Добавленные строки по файлам: {путь: [(номер, текст)]} и множество всех изменённых путей."""
    out, changed, path, row = {}, set(), None, 0
    diff = git(repo, '-c', 'core.quotepath=false', 'diff', '-U0', '--no-color', '--no-renames', base, ref)
    for line in diff.splitlines():
        if line.startswith('diff --git '):
            path = None
        elif line.startswith('--- '):
            if line.startswith('--- a/'):
                changed.add(line[6:].rstrip('\t'))
        elif line.startswith('+++ '):
            path = line[6:].rstrip('\t') if line.startswith('+++ b/') else None
            if path:
                changed.add(path)
        elif line.startswith('@@'):
            m = re.match(r'@@ -\S+ \+(\d+)', line)
            row = int(m.group(1))
        elif path and line.startswith('+'):
            out.setdefault(path, []).append((row, line[1:]))
            row += 1
    return out, changed


def match_any(path, globs):
    return any(fnmatch.fnmatch(path, g) or fnmatch.fnmatch(os.path.basename(path), g) for g in globs)


def load_config(repo, path):
    path = path or os.path.join(repo, 'kit.toml')
    data = {}
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = tomllib.load(f)
    elif path != os.path.join(repo, 'kit.toml'):
        raise Setup('нет файла настройки %s' % path)
    sec = data.get('security', {})
    cfg = {k: sec.get(k, v) for k, v in DEFAULTS.items()}
    triggers = list(TRIGGERS)
    for t in sec.get('triggers', []):
        if 'name' not in t or not (t.get('added') or t.get('files')):
            raise Setup('[[security.triggers]]: нужны name и added или files')
        triggers.append({'classes': [], **t})
    for t in triggers:
        if t.get('added'):
            try:
                t['re'] = re.compile(t['added'])
            except re.error as e:
                raise Setup('повод «%s»: плохое выражение: %s' % (t['name'], e)) from e
    return data.get('git', {}).get('main', 'main'), cfg, triggers


def find(added, changed, messages, cfg, triggers):
    """Поводы: [(повод, [места])]. Место — «файл:строка  текст» или «файл»."""
    found = []
    for t in triggers:
        hits, strong = [], False
        for path in sorted(changed):
            # Документ о выкладке — не выкладка. Файлы правил агентов — исключение: это инструкции.
            if path.endswith('.md') and not t.get('docs'):
                continue
            if t.get('files') and match_any(path, t['files']):
                hits.append(path)
        if t.get('re'):
            for path, rows in sorted(added.items()):
                if t.get('in_files'):
                    if not match_any(path, t['in_files']):
                        continue
                elif not match_any(path, cfg['code']) or match_any(path, cfg['skip']):
                    continue
                file_hits = []
                for row, text in rows:
                    # Комментарий и импорт — не код, который что-то делает: повод в них ничего не меняет.
                    if re.match(r'\s*(?:#|//|\* |/\*|from\s+\S+\s+import\b|import\s|\}\s*from\s)', text):
                        continue
                    if t['re'].search(text):
                        file_hits.append('%s:%d  %s' % (path, row, text.strip()[:110]))
                if file_hits and t.get('strong_if') and any(re.search(t['strong_if'], x) for _, x in rows):
                    strong = True
                    file_hits = [h + '   ← в файле правка трогает ключ' for h in file_hits]
                hits += file_hits
        if hits:
            found.append((dict(t, weak=False) if strong else t, hits))
    fixes = [m for m in messages if re.search(FIX_WORDS, m)]
    if fixes:
        found.append(({'name': 'Исправление прошлой находки', 'classes': [],
                       'see': 'references/security/lead.md, раздел 7'}, fixes))
    return found


def main():
    ap = argparse.ArgumentParser(description='Поводы позвать безопасника по правке ветки.')
    ap.add_argument('--repo', default='.', help='папка репозитория (по умолчанию текущая)')
    ap.add_argument('--base', help='с чем сравнивать (по умолчанию main из kit.toml)')
    ap.add_argument('--ref', default='HEAD', help='что проверять (по умолчанию текущая ветка)')
    ap.add_argument('--config', help='файл настройки (по умолчанию kit.toml в корне репозитория)')
    ap.add_argument('--limit', type=int, default=5, help='сколько мест печатать на повод (по умолчанию 5)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        repo = git(a.repo, 'rev-parse', '--show-toplevel').strip()
        main_ref, cfg, triggers = load_config(repo, a.config)
        base = git(repo, 'merge-base', a.base or main_ref, a.ref).strip()
        added, changed = added_lines(repo, base, a.ref)
        messages = git(repo, 'log', '--format=%h %s', '%s..%s' % (base, a.ref)).splitlines()
    except Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    found = find(added, changed, messages, cfg, triggers)
    strong = [f for f in found if not f[0].get('weak')]
    classes = set()
    # Сначала поводы, потом заметки: заметка одна безопасника не зовёт, но его охотник её увидит.
    for t, hits in strong + [f for f in found if f[0].get('weak')]:
        if not t.get('weak'):
            classes.update(t['classes'])
        where = ('классы %s' % ', '.join(map(str, t['classes']))) if t['classes'] else t.get('see', '')
        print('%-8s%s — %s' % ('ЗАМЕТКА' if t.get('weak') else 'ПОВОД', t['name'], where))
        for h in hits[:a.limit]:
            print('        %s' % h)
        if len(hits) > a.limit:
            print('        … ещё %d' % (len(hits) - a.limit))
    if not strong:
        print('Итог: поводов нет%s. Изменённых файлов: %d.' % (
            ', заметок %d' % len(found) if found else '', len(changed)))
        return 0
    print('\nИтог: поводов %d — позвать безопасника (skills/security/SKILL.md).%s' % (
        len(strong), ' Классы для охотников: %s.' % ', '.join(map(str, sorted(classes))) if classes else ''))
    return 1


if __name__ == '__main__':
    sys.exit(main())
