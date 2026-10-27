"""Линтер и поиск секретов только по строкам правки.

Исполнитель запускает из рабочей копии задачи перед сдачей, тим лид — перед слиянием:
    python changed.py                 # правка текущей ветки против main
    python changed.py --ref task/CB_TASK_123
Строки, которых правка не трогала, не проверяются: старый долг кода задачу не останавливает.

Код возврата: 0 — стоп-находок нет, 1 — есть стоп-находка, 2 — ошибка запуска или настройки.
Настройка — раздел [lint] файла kit.toml в корне репозитория (образец — assets/kit.example.toml).
Ruff нужен в окружении (python -m ruff). Сканер секретов — внешняя программа из настройки;
не установлен — предупреждение, не стоп.
"""
import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib

STOP, WARN, OK = 'СТОП', 'ВНИМАНИЕ', 'ОК'

# Правила по темам возвратов (docs/code-synthesis.md): стоп — мёртвый код и проглоченная ошибка,
# предупреждение — широкий перехват, потерянный след ошибки, закомментированный код, сложность, имена.
# ANN401 (Any) не взят: на истории «Рабочей» 177 находок, замечаний по теме нет. Проект меняет списки в kit.toml.
DEFAULTS = {
    'stop': ['F401', 'F841', 'S110', 'S112'],
    'warn': ['BLE001', 'TRY400', 'B904', 'ERA001', 'E741', 'C901'],
    'skip': ['*/tests/*', 'tests/*', '*test_*.py', '*/migrations/*'],
    # Betterleaks — продолжение Gitleaks от его автора, ключи те же. Флаг --validation не ставить: он шлёт ключ в сервис.
    'secrets': ['betterleaks', 'git', '--log-opts={base}..{ref}', '--no-banner', '--redact', '--exit-code', '1'],
}


class Setup(Exception):
    """Ошибка запуска: нет git, нет ruff, нет ветки."""


def git(repo, *args, check=True):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        raise Setup('git %s: %s' % (' '.join(args), r.stderr.strip()))
    return r


def added_rows(repo, base, ref):
    """Номера добавленных строк по файлам в новой версии: {путь: {номер, ...}}."""
    out, path = {}, None
    for line in git(repo, '-c', 'core.quotepath=false', 'diff', '-U0', '--no-color', '--no-renames', base, ref).stdout.splitlines():
        if line.startswith('+++ '):
            # Путь с пробелом git заканчивает табуляцией.
            path = line[6:].rstrip('\t') if line.startswith('+++ b/') else None
        elif path and line.startswith('@@'):
            m = re.match(r'@@ -\S+ \+(\d+)(?:,(\d+))? @@', line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            out.setdefault(path, set()).update(range(start, start + count))
    return {p: rows for p, rows in out.items() if rows}


def ruff(path, text, rules, cwd):
    """Находки Ruff в тексте файла: [(строка, код, сообщение)]. Настройки проекта не читаются."""
    r = subprocess.run([sys.executable, '-m', 'ruff', 'check', '--isolated', '--no-cache', '--output-format', 'json',
                        '--select', ','.join(rules), '--stdin-filename', path, '-'],
                       input=text, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode not in (0, 1):
        raise Setup('ruff: %s' % (r.stderr.strip() or 'код %s' % r.returncode))
    return [(f['location']['row'], f['code'], f['message']) for f in json.loads(r.stdout or '[]')]


def lint(repo, base, ref, cfg):
    """Находки по строкам правки: [(уровень, файл:строка, код, сообщение)]."""
    stop, warn = cfg['stop'], cfg['warn']
    out = []
    for path, rows in sorted(added_rows(repo, base, ref).items()):
        if not path.endswith('.py') or any(fnmatch.fnmatch(path, g) for g in cfg['skip']):
            continue
        text = git(repo, 'show', '%s:%s' % (ref, path)).stdout
        for row, code, message in ruff(path, text, stop + warn, repo):
            if row in rows:
                level = STOP if any(code.startswith(s) for s in stop) else WARN
                out.append((level, '%s:%d' % (path, row), code, message))
    return out


def secrets(repo, base, ref, command):
    """Сканер секретов по коммитам правки. Не установлен — предупреждение."""
    if not command:
        return [(WARN, 'секреты', '', 'сканер в настройке выключен')]
    if not shutil.which(command[0]):
        return [(WARN, 'секреты', '', 'сканер %s не установлен — секреты не проверены' % command[0])]
    args = [a.format(base=base, ref=ref) for a in command]
    r = subprocess.run(args, cwd=repo, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode == 0:
        return [(OK, 'секреты', '', 'сканер ничего не нашёл')]
    # Вывод сканера не печатаем целиком: в нём может быть сам секрет, если сканер его не скрыл.
    found = len(re.findall(r'(?im)^\s*(?:Finding|RuleID):', r.stdout + r.stderr))
    return [(STOP, 'секреты', '', 'сканер нашёл возможный секрет%s — запусти его сам: %s'
             % (' (%d)' % found if found else '', ' '.join(args)))]


def load_config(repo, path):
    path = path or os.path.join(repo, 'kit.toml')
    data = {}
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = tomllib.load(f)
    elif path != os.path.join(repo, 'kit.toml'):
        raise Setup('нет файла настройки %s' % path)
    lint_cfg = dict(DEFAULTS, **data.get('lint', {}))
    return data.get('git', {}).get('main', 'main'), lint_cfg


def main():
    ap = argparse.ArgumentParser(description='Линтер и поиск секретов по строкам правки.')
    ap.add_argument('--repo', default='.', help='папка репозитория (по умолчанию текущая)')
    ap.add_argument('--base', help='с чем сравнивать (по умолчанию main из kit.toml)')
    ap.add_argument('--ref', default='HEAD', help='что проверять (по умолчанию текущая ветка)')
    ap.add_argument('--config', help='файл настройки (по умолчанию kit.toml в корне репозитория)')
    ap.add_argument('--no-secrets', action='store_true', help='не запускать сканер секретов')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        repo = git(a.repo, 'rev-parse', '--show-toplevel').stdout.strip()
        main_ref, cfg = load_config(repo, a.config)
        base = git(repo, 'merge-base', a.base or main_ref, a.ref).stdout.strip()
        found = lint(repo, base, a.ref, cfg)
        if not a.no_secrets:
            found += secrets(repo, base, a.ref, cfg['secrets'])
    except Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    for level, where, code, message in found:
        print('%-9s %s %s %s' % (level, where, code, message))
    stops = sum(1 for f in found if f[0] == STOP)
    lint_count = sum(1 for f in found if f[2])
    print('\nИтог: %s. Находок линтера на строках правки: %d.' % (
        'стоп-находок нет' if not stops else 'стоп-находок %d' % stops, lint_count))
    if stops:
        print('Стоп снимается правкой. Если строка верна, поставь # noqa: <код> и одной фразой — почему.')
    return 1 if stops else 0


if __name__ == '__main__':
    sys.exit(main())
