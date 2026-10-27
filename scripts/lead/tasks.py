"""Открытые задачи из списка задач проекта — со сверкой по веткам.

Тим лид выдаёт владельцу список задач с вывода этого скрипта, а не по памяти. У каждой задачи — статус из
списка, есть ли ветка, есть ли в ней отчёт, слита ли она. Расхождение печатается словами: «ветка слита, а в
списке TODO».

    python tasks.py                 # открытые задачи
    python tasks.py --all           # и принятые, и отменённые
    python tasks.py --code CB       # только один подпроект

Настройка — `kit.toml` в корне репозитория (образец `assets/kit.example.toml`). Без него — значения по
умолчанию: `team/BACKLOG.md`, ветка `master`, ветки задач `task/{id}`, отчёты `team/reports/{code}/{id}-report.md`.
Код возврата: 0 — расхождений нет, 1 — есть расхождения, 2 — ошибка запуска.
"""
import argparse
import os
import re
import subprocess
import sys

try:
    import tomllib
except ImportError:  # Python до 3.11
    tomllib = None

CLOSED = {'DONE', 'CANCELLED'}
ID = re.compile(r'^([A-Z]+)_TASK_\d+$')


def git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                          encoding='utf-8', errors='replace')


def config(repo, path):
    cfg = {'main': 'master', 'branch': 'task/{id}', 'backlog': 'team/BACKLOG.md',
           'report': 'team/reports/{code}/{id}-report.md'}
    path = path or os.path.join(repo, 'kit.toml')
    if tomllib and os.path.exists(path):
        with open(path, 'rb') as f:
            data = tomllib.load(f)
        cfg['main'] = data.get('git', {}).get('main', cfg['main'])
        cfg['branch'] = data.get('git', {}).get('task_branch', cfg['branch'])
        cfg['backlog'] = data.get('files', {}).get('backlog', cfg['backlog'])
        cfg['report'] = data.get('files', {}).get('report', cfg['report'])
    return cfg


def rows(text):
    """Строки таблиц, в шапке которых есть «Статус». Первый столбец — номер задачи."""
    header = None
    for line in text.splitlines():
        if not line.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if header is None:
            header = cells if 'Статус' in cells else []
            continue
        if not header or set(''.join(cells)) <= set('-: '):
            continue
        row = dict(zip(header, cells))
        task = cells[0].strip('`*')
        if ID.match(task):
            yield task, row


def short(text, limit=110):
    text = re.sub(r'`', '', text)
    return text if len(text) <= limit else text[:limit].rstrip() + '…'


def main():
    ap = argparse.ArgumentParser(description='Открытые задачи со сверкой по веткам.')
    ap.add_argument('--repo', default='.')
    ap.add_argument('--config')
    ap.add_argument('--all', action='store_true', help='показать и закрытые задачи')
    ap.add_argument('--code', help='код подпроекта, например CB')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    cfg = config(args.repo, args.config)
    path = os.path.join(args.repo, cfg['backlog'])
    if not os.path.exists(path):
        print('Нет списка задач %s' % path, file=sys.stderr)
        return 2
    with open(path, encoding='utf-8') as f:
        text = f.read()

    seen, mismatch = set(), 0
    for task, row in rows(text):
        if task in seen:
            continue
        seen.add(task)
        code = ID.match(task).group(1)
        status = row.get('Статус', '').strip('` ')
        if args.code and code != args.code:
            continue
        if status in CLOSED and not args.all:
            continue
        branch = cfg['branch'].format(id=task, code=code)
        has_branch = git(args.repo, 'rev-parse', '--verify', '-q', branch).returncode == 0
        notes = []
        if not has_branch:
            state = 'ветки нет'
        else:
            merged = git(args.repo, 'merge-base', '--is-ancestor', branch, cfg['main']).returncode == 0
            ahead = git(args.repo, 'rev-list', '--count', '%s..%s' % (cfg['main'], branch)).stdout.strip()
            report = cfg['report'].format(id=task, code=code)
            has_report = git(args.repo, 'cat-file', '-e', '%s:%s' % (branch, report)).returncode == 0
            if merged and ahead == '0':
                state = 'ветка слита' if git(args.repo, 'rev-list', '--count', '%s..%s' % (
                    branch, cfg['main'])).stdout.strip() != '0' else 'ветка без своих коммитов'
            else:
                state = 'в ветке %s коммит(ов), не слита' % ahead
            if has_report:
                state += ', отчёт есть'
            if state.startswith('ветка слита') and status not in CLOSED:
                notes.append('ветка слита, а в списке %s' % status)
            if has_report and status in {'TODO', 'IN_PROGRESS'} and 'не слита' in state:
                notes.append('отчёт есть, а в списке %s: сдана?' % status)
        mismatch += bool(notes)
        line = '%s — %s — %s — %s' % (task, status or 'без статуса', short(row.get('Название', '')), state)
        if notes:
            line += '. РАСХОЖДЕНИЕ: ' + '; '.join(notes)
        print(line)

    if not seen:
        print('В %s не нашлось таблиц со столбцом «Статус».' % cfg['backlog'], file=sys.stderr)
        return 2
    return 1 if mismatch else 0


if __name__ == '__main__':
    sys.exit(main())
