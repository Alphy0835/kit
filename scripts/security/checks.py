"""Какие группы базы типовых проверок задела правка ветки.

Безопасник запускает первым шагом, рядом с triggers.py:
    python checks.py                       # правка текущей ветки против main
    python checks.py --ref task/CB_TASK_123
Группы — файлы references/security/base/*.md. Две строки в начале файла — вход скрипта: «Строки:» —
регулярное выражение по добавленным строкам кода, «Пути:» — шаблоны путей изменённых файлов. Новая группа
подхватывается сама.

По каждой названной группе безопасник запускает одного проверяющего (references/security/checker.md) и даёт
ему файл группы и список изменённых файлов, которые печатает скрипт.

Код возврата: 0 — правка не задела ни одной группы, 1 — задела, 2 — ошибка запуска или настройки.
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triggers import Setup, added_lines, git, load_config, match_any  # noqa: E402

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'references',
                                     'security', 'base'))
SKIP_LINE = re.compile(r'\s*(?:#|//|\* |/\*|from\s+\S+\s+import\b|import\s|\}\s*from\s)')


def load_groups(base_dir):
    """Группы: [{name, path, re, paths, agent, script}]."""
    groups = []
    for path in sorted(glob.glob(os.path.join(base_dir, '*.md'))):
        if os.path.basename(path) == 'README.md':
            continue
        with open(path, encoding='utf-8') as f:
            text = f.read()
        title = re.search(r'^#\s+(.+)$', text, re.M)
        lines = re.search(r'^Строки:\s*`(.+)`\s*$', text, re.M)
        paths = re.search(r'^Пути:\s*(.+)$', text, re.M)
        if not title or not lines or not paths:
            raise Setup('%s: нужны заголовок, строки «Строки:» и «Пути:»' % path)
        try:
            rx = re.compile(lines.group(1))
        except re.error as e:
            raise Setup('%s: плохое выражение в «Строки:»: %s' % (path, e)) from e
        globs = re.findall(r'`([^`]+)`', paths.group(1))
        globs = globs[0].split() if globs else []
        checks = re.findall(r'^Проверка:\s*(.+)$', text, re.M)
        groups.append({'name': title.group(1).strip(), 'path': path, 're': rx, 'paths': globs,
                       'agent': sum(1 for c in checks if not c.startswith('скрипт ') or 'агент' in c),
                       'script': sum(1 for c in checks if c.startswith('скрипт') and 'агент' not in c)})
    if not groups:
        raise Setup('нет групп в %s' % base_dir)
    return groups


def find(groups, added, changed, cfg):
    """[(группа, [места])]. Место — «файл:строка  текст» или «файл»."""
    found = []
    code = [p for p in sorted(changed) if match_any(p, cfg['code']) and not match_any(p, cfg['skip'])]
    for g in groups:
        hits = [p for p in code if g['paths'] and match_any(p, g['paths'])]
        for path in code:
            for row, text in added.get(path, []):
                if not SKIP_LINE.match(text) and g['re'].search(text):
                    hits.append('%s:%d  %s' % (path, row, text.strip()[:110]))
        if hits:
            found.append((g, hits))
    return found, code


def main():
    ap = argparse.ArgumentParser(description='Группы базы типовых проверок по правке ветки.')
    ap.add_argument('--repo', default='.', help='папка репозитория (по умолчанию текущая)')
    ap.add_argument('--base', help='с чем сравнивать (по умолчанию main из kit.toml)')
    ap.add_argument('--ref', default='HEAD', help='что проверять (по умолчанию текущая ветка)')
    ap.add_argument('--config', help='файл настройки (по умолчанию kit.toml в корне репозитория)')
    ap.add_argument('--groups', default=BASE, help='папка базы (по умолчанию references/security/base)')
    ap.add_argument('--limit', type=int, default=3, help='сколько мест печатать на группу (по умолчанию 3)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        groups = load_groups(a.groups)
        repo = git(a.repo, 'rev-parse', '--show-toplevel').strip()
        main_ref, cfg, _ = load_config(repo, a.config)
        base = git(repo, 'merge-base', a.base or main_ref, a.ref).strip()
        added, changed = added_lines(repo, base, a.ref)
    except Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    found, code = find(groups, added, changed, cfg)
    if not found:
        print('Итог: правка не задела ни одной группы базы. Файлов кода в правке: %d.' % len(code))
        return 0
    for g, hits in found:
        print('ГРУППА  %s — %s; записей для проверяющего: %d, за скриптом: %d' % (
            g['name'], os.path.relpath(g['path'], os.path.join(BASE, '..', '..', '..')).replace('\\', '/'),
            g['agent'], g['script']))
        for h in hits[:a.limit]:
            print('        %s' % h)
        if len(hits) > a.limit:
            print('        … ещё %d' % (len(hits) - a.limit))
    print('\nРепозиторий (дать проверяющему, все пути — от него): %s' % repo)
    print('Файлы кода в правке (дать проверяющему):')
    for p in code:
        print('        %s' % p)
    print('\nИтог: групп %d — по проверяющему на группу (references/security/checker.md, модель Haiku).' %
          len(found))
    return 1


if __name__ == '__main__':
    sys.exit(main())
