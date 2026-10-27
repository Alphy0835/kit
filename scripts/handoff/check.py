"""Проверка ветки задачи перед сдачей и перед приёмкой.

Исполнитель запускает из рабочей копии своей задачи:
    python check.py CB_TASK_123
Тим лид запускает из своей рабочей копии, до слияния:
    python check.py CB_TASK_123 --lead

Если в kit.toml есть раздел [boundaries], проверяются и границы модулей по карте спецификации
(`scripts/lint/boundaries.py`).
Скрипт ничего не сливает и не коммитит. Слияние пробное: `git merge-tree` считает его в памяти.
Код возврата: 0 — стоп-находок нет, 1 — есть стоп-находка, 2 — ошибка запуска или настройки.
Настройка проекта — файл `kit.toml` в корне репозитория (образец — `assets/kit.example.toml`).
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys
import tomllib

STOP, WARN, OK = 'СТОП', 'ВНИМАНИЕ', 'ОК'


class Setup(Exception):
    """Ошибка запуска: нет git, нет настройки, нет ветки."""


def git(repo, *args, check=True):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        raise Setup('git %s: %s' % (' '.join(args), r.stderr.strip()))
    return r


def show(repo, ref, path):
    """Текст файла в коммите или None, если файла там нет."""
    r = git(repo, 'show', '%s:%s' % (ref, path), check=False)
    return r.stdout if r.returncode == 0 else None


def section(text, title):
    """Тело раздела `## <title>…` до следующего заголовка второго уровня."""
    m = re.search(r'^##\s+%s[^\n]*\n(.*?)(?=^##\s|\Z)' % re.escape(title), text, re.S | re.M)
    return m.group(1) if m else None


def field(text, name):
    """Значение строки таблицы `| <name> | значение |` в шапке задания."""
    m = re.search(r'^\|\s*%s\s*\|\s*(.*?)\s*\|\s*$' % re.escape(name), text, re.M)
    return m.group(1).strip() if m else None


def load_config(repo, path):
    path = path or os.path.join(repo, 'kit.toml')
    if not os.path.exists(path):
        raise Setup('нет файла настройки %s — образец в assets/kit.example.toml' % path)
    with open(path, 'rb') as f:
        return tomllib.load(f)


def check_place(repo, branch):
    """Исполнитель: работа идёт в своей рабочей копии, на ветке задачи, всё закоммичено."""
    out = []
    head = git(repo, 'rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()
    if head != branch:
        out.append((STOP, 'ветка', 'сейчас %s, а задача ведётся в %s' % (head, branch)))
    else:
        out.append((OK, 'ветка', head))
    git_dir = os.path.abspath(os.path.join(repo, git(repo, 'rev-parse', '--git-dir').stdout.strip()))
    common = os.path.abspath(os.path.join(repo, git(repo, 'rev-parse', '--git-common-dir').stdout.strip()))
    if git_dir == common:
        out.append((STOP, 'рабочая копия', 'это общая папка репозитория; задача ведётся в своей копии (git worktree)'))
    else:
        out.append((OK, 'рабочая копия', 'своя'))
    dirty = [l for l in git(repo, 'status', '--porcelain').stdout.splitlines() if not l.startswith('??')]
    if dirty:
        out.append((STOP, 'незакоммиченные правки', '%d файл(ов): %s' % (len(dirty), ', '.join(l[3:] for l in dirty[:5]))))
    else:
        out.append((OK, 'незакоммиченные правки', 'нет'))
    return out


def check_merge(repo, main, ref, bookkeeping, lead=False):
    """Пробное слияние ветки со свежим main: есть ли конфликты.

    Конфликт в служебных файлах (список задач, статус в задании) решает тим лид при слиянии,
    поэтому он не останавливает сдачу. Конфликт в остальных файлах решает исполнитель до сдачи.
    """
    # Без quotepath git отдаёт русские пути в кавычках и восьмеричных кодах — шаблоны их не узнают.
    r = git(repo, '-c', 'core.quotepath=false', 'merge-tree', '--write-tree', '--name-only', '--no-messages', main, ref,
            check=False)
    if r.returncode == 0:
        behind = git(repo, 'rev-list', '--count', '%s..%s' % (ref, main)).stdout.strip()
        return [(OK, 'пробное слияние с %s' % main, 'конфликтов нет; %s ушёл вперёд на %s коммит(ов)' % (main, behind))]
    if r.returncode != 1:
        raise Setup('git merge-tree: %s' % r.stderr.strip())
    files = r.stdout.splitlines()[1:]
    service = [p for p in files if any(fnmatch.fnmatch(p, g) for g in bookkeeping)]
    work = [p for p in files if p not in service]
    out = []
    # Тим лиду конфликт в документе — не повод вернуть: обе ветки дописали своё, он сводит при слиянии.
    # Исполнителю — стоп: перед сдачей он вливает свежий main сам.
    docs = [p for p in work if p.endswith('.md')] if lead else []
    work = [p for p in work if p not in docs]
    if docs:
        out.append((WARN, 'пробное слияние с %s' % main, 'конфликт в документах, сведи при слиянии и оставь обе '
                    'части; смысл расходится — тогда возврат: %s' % ', '.join(docs)))
    if work:
        out.append((STOP, 'пробное слияние с %s' % main, 'конфликт в %d файл(ах): %s' % (len(work), ', '.join(work))))
    if service:
        out.append((WARN, 'пробное слияние с %s' % main, 'конфликт в служебных файлах, его решает тим лид при слиянии: %s'
                    % ', '.join(service)))
    return out


def check_reverted(repo, main, ref, task_id=None):
    """Слияние этой ветки откачено в main, а отката отката нет.

    Тогда git считает коммиты ветки уже слитыми: повторное слияние пройдёт без конфликтов, но откаченные
    изменения не вернёт. Вернуть их можно только откатом отката (`git revert <коммит отката>`).
    """
    log = git(repo, 'log', main, '--format=%H%x00%B%x01', '--grep=This reverts commit').stdout
    reverts = {}                                   # коммит отката -> откаченный коммит
    for entry in log.split('\x01'):
        if '\x00' not in entry:
            continue
        h, body = entry.strip().split('\x00', 1)
        m = re.search(r'This reverts commit ([0-9a-f]{7,40})', body)
        if m:
            reverts[h] = git(repo, 'rev-parse', m.group(1), check=False).stdout.strip()
    undone = set(reverts.values())
    out = []
    for rv, target in reverts.items():
        if not target or rv in undone:             # откат сам откачен — изменения вернулись
            continue
        parents = git(repo, 'rev-list', '--parents', '-n', '1', target).stdout.split()[1:]
        if len(parents) < 2:
            continue
        if git(repo, 'merge-base', '--is-ancestor', parents[1], ref, check=False).returncode == 0:
            out.append((STOP, 'откат слияния', 'слияние %s этой ветки откачено в %s коммитом %s. Повторное слияние '
                        'не вернёт откаченное: сначала откат отката (git revert %s)' % (target[:8], main, rv[:8], rv[:8])))
    if out or not task_id:
        return out
    # Откат бывает вписан в другой коммит без строки «This reverts commit». Тогда видно только, что ветка уже
    # сливалась: предупреждаем, а проверяет человек. Номер задачи в тексте слияния ещё не значит, что слита эта
    # ветка («задача X разблокирована»): нужен свой коммит задачи среди слитых.
    own = re.compile(r'\b%s\b' % re.escape(task_id))
    for row in git(repo, 'log', main, '--merges', '--grep=%s' % task_id, '--format=%H %P').stdout.splitlines():
        h, *parents = row.split()
        if len(parents) < 2:
            continue
        merged = git(repo, 'log', '--format=%s', '%s..%s' % (parents[0], parents[1])).stdout.splitlines()
        if not any(own.search(s) for s in merged):
            continue
        if git(repo, 'merge-base', '--is-ancestor', parents[1], ref, check=False).returncode == 0:
            out.append((WARN, 'ветка уже сливалась', 'слиянием %s. Если его откатывали, повторное слияние не вернёт '
                        'откаченное — сверь, что изменения ветки есть в %s после слияния' % (h[:8], main)))
            break
    return out


def check_migrations(repo, main, ref, rules):
    """Номера миграций, добавленные веткой, не заняты в main после точки ответвления."""
    out = []
    base = git(repo, 'merge-base', main, ref).stdout.strip()
    for rule in rules:
        path, rx = rule['file'], re.compile(rule['number'])

        def numbers(commit):
            # Номера считаются по файлу целиком: построчный диф путает соседние одинаковые записи.
            text = show(repo, commit, path) or ''
            return {m.group(1) for line in text.splitlines() for m in [rx.search(line)] if m}

        at_base = numbers(base)
        mine, theirs = numbers(ref) - at_base, numbers(main) - at_base
        if not mine:
            continue
        taken = sorted(mine & theirs, key=lambda x: int(x) if x.isdigit() else x)
        if taken:
            out.append((STOP, 'номер миграции', '%s: номер %s уже занят в %s слитой задачей' % (path, ', '.join(taken), main)))
        else:
            out.append((OK, 'номер миграции', '%s: %s свободен' % (path, ', '.join(sorted(mine)))))
    return out


def added_lines(repo, base, ref):
    """Добавленные строки правки по файлам: {путь: [строки]}."""
    out, path = {}, None
    for line in git(repo, '-c', 'core.quotepath=false', 'diff', '-U0', '--no-color', base, ref).stdout.splitlines():
        if line.startswith('+++ '):
            # Путь с пробелом git заканчивает табуляцией.
            path = line[6:].rstrip('\t') if line.startswith('+++ b/') else None
        elif path and line.startswith('+') and not line.startswith('+++'):
            out.setdefault(path, []).append(line[1:])
    return out


def path_pattern(key):
    """Путь маршрута в регулярное выражение: `{id}` совпадает с любым куском пути, в том числе с `{x}` в f-строке."""
    parts = re.split(r'\{[^}]*\}|<[^>]*>', key)
    return r'[^/"\'?\s]+'.join(re.escape(p) for p in parts)


def via_constant(key, code_text, test_text):
    """Тест зовёт адрес константой из кода: `CODE_PATH = f"{PREFIX}/code"` в правке и `CODE_PATH` в тестах."""
    names = re.findall(r'(\w+)\s*=\s*f?["\'][^"\'\n]*%s["\']' % path_pattern(key), code_text)
    return any(re.search(r'\b%s\b' % re.escape(n), test_text) for n in names)


def entry_file_misses(repo, ref, rule, lines, is_test, test_text):
    """Правка в файле, где объявлены маршруты, а тесты правки не зовут ни один его адрес.

    Ловит тесты «мимо приёмника»: обработчик поменяли, а проверяют прямым вызовом функции. Адрес берётся из
    декоратора строкой или константой этого же файла; тест засчитывается, если в нём есть путь или имя константы.
    """
    route = re.compile(rule['route'])
    # Тест может звать адрес через помощника, который уже лежит в тестовом файле или в conftest.py.
    # Поэтому смотрим изменённые тестовые файлы целиком и все conftest.py рядом с ними.
    test_paths = {p for p in lines if is_test(p)}
    for p in list(test_paths):
        d = p.rsplit('/', 1)[0]
        test_paths.add(d + '/conftest.py')
    test_text = test_text + '\n' + '\n'.join(show(repo, ref, p) or '' for p in sorted(test_paths))
    misses = []
    for path in lines:
        if is_test(path) or not any(fnmatch.fnmatch(path, g) for g in rule.get('code', ['*'])):
            continue
        if any(fnmatch.fnmatch(path, g) for g in rule.get('skip', [])):
            continue
        text = re.sub(r'\(\s*\n\s*', '(', show(repo, ref, path) or '')   # декоратор в две строки
        consts = dict(re.findall(r'^\s*([A-Z][A-Z0-9_]*)\s*=\s*f?["\']([^"\'\n]+)["\']', text, re.M))
        keys = []
        for m in route.finditer(text):
            literal, name = m.group(1), m.group(2) if route.groups > 1 else None
            if literal:
                keys.append((literal, None))
            elif name:
                keys.append((consts.get(name), name))
        if not keys:
            continue
        hit = any((lit and (re.search(path_pattern(lit) + '["\'?]', test_text) or via_constant(lit, text, test_text))) or
                  (name and re.search(r'\b%s\b' % re.escape(name), test_text)) for lit, name in keys)
        if not hit:
            misses.append('%s (адресов в файле: %d)' % (path.rsplit('/', 1)[-1], len(keys)))
    return misses


def check_edges(repo, main, ref, rules, test_globs):
    """Предупреждения о краях: в коде появилось то, что требует особого теста, а в тестах правки его не видно.

    Скрипт находит только механическую часть: новый маршрут, путь с номером, номер миграции. Сам тест он не
    читает и правильность его не проверяет — это делает чтение. Поэтому итог — предупреждение, не стоп.
    """
    base = git(repo, 'merge-base', main, ref).stdout.strip()
    lines = added_lines(repo, base, ref)
    is_test = lambda p: any(fnmatch.fnmatch(p, g) for g in test_globs)
    test_text = '\n'.join(l for p, ls in lines.items() if is_test(p) for l in ls)
    code_text = '\n'.join(l for p, ls in lines.items() if not is_test(p) for l in ls)
    out = []
    for rule in rules:
        if rule.get('kind') == 'entry_file':
            misses = entry_file_misses(repo, ref, rule, lines, is_test, test_text)
            if misses:
                out.append((WARN, rule['name'], '%d: %s' % (len(misses), '; '.join(misses[:6]))))
            continue
        added, need = re.compile(rule['added']), rule['need']
        misses = []
        for path, ls in lines.items():
            if is_test(path) or not any(fnmatch.fnmatch(path, g) for g in rule.get('code', ['*'])):
                continue
            seen = set()
            for i, l in enumerate(ls):
                # Декоратор бывает в две строки: `@router.get(` и путь следующей строкой.
                m = added.search(l) or (added.search(l + ' ' + ls[i + 1].strip()) if i + 1 < len(ls) else None)
                if not m:
                    continue
                key = m.group(1) if m.groups() else m.group(0)
                if (key, i) in seen or (i and (key, i - 1) in seen):
                    continue
                seen.add((key, i))
                rx = need.replace('{path}', path_pattern(key)) if '{path}' in need else need
                if not re.search(rx, test_text) and not via_constant(key, code_text, test_text):
                    misses.append('%s: %s' % (path.rsplit('/', 1)[-1], key.strip()))
        if misses:
            out.append((WARN, rule['name'], '%d: %s' % (len(misses), '; '.join(misses[:6]) + (' …' if len(misses) > 6 else ''))))
    return out


def check_boundaries(repo, ref, rule):
    """Границы модулей по карте спецификации: scripts/lint/boundaries.py на коммите ветки."""
    if not rule.get('spec'):
        return []
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lint'))
    import boundaries
    try:
        rows, _ = boundaries.check(repo, rule['spec'], ref, rule.get('baseline'))
    except boundaries.Setup as e:
        raise Setup('[boundaries]: %s' % e)
    return rows


def check_status(repo, ref, task_path, backlog_path, task_id, want):
    out = []
    task = show(repo, ref, task_path)
    if task is None:
        return [(STOP, 'задание', 'нет файла %s в ветке' % task_path)], None
    # После статуса в поле бывает пояснение: «IN_PROGRESS — ждёт живого прогона». Сравнивается только слово.
    word = lambda s: (re.match(r'[A-Z_]+', s or '') or [''])[0]
    status = word(field(task, 'Статус'))
    if status != want:
        out.append((STOP, 'статус в задании', '%s, а при сдаче нужен %s' % (status, want)))
    else:
        out.append((OK, 'статус в задании', status))
    backlog = show(repo, ref, backlog_path) if backlog_path else None
    if backlog:
        lines = backlog.splitlines()
        header = next((l for l in lines if l.startswith('|') and 'Статус' in l), None)
        row = next((l for l in lines if l.startswith('| %s ' % task_id)), None)
        if header and row:
            cols = [c.strip() for c in header.strip('|').split('|')]
            cells = [c.strip() for c in row.strip('|').split('|')]
            got = word(cells[cols.index('Статус')] if len(cells) > cols.index('Статус') else '')
            if got != status:
                out.append((STOP, 'статус в списке задач', '%s, а в задании %s; статус должен совпадать в обоих местах' % (got, status)))
            else:
                out.append((OK, 'статус в списке задач', got))
    return out, task


def check_report(repo, ref, report_path, task, cfg):
    report = show(repo, ref, report_path)
    if report is None:
        return [(STOP, 'отчёт', 'нет файла %s в ветке' % report_path)]
    out = []
    tcfg, rcfg = cfg.get('task', {}), cfg.get('report', {})
    crit = section(task, tcfg.get('criteria_section', 'Критерии приёмки')) or ''
    n_crit = len(re.findall(r'^- \[', crit, re.M))
    self_check = section(report, rcfg.get('criteria_section', 'Самопроверка по критериям приёмки'))
    if self_check is None:
        out.append((STOP, 'самопроверка по критериям', 'в отчёте нет раздела'))
    else:
        items = re.findall(r'^- \[.\].*(?:\n(?![-\n#]).*)*', self_check, re.M)
        labels = rcfg.get('labels', ['[вживую]', '[тесты]', '[не проверено]'])
        no_label = [i.splitlines()[0][:70] for i in items if not any(l in i for l in labels)]
        if len(items) < n_crit:
            out.append((STOP, 'самопроверка по критериям', 'в задании критериев %d, в отчёте строк %d' % (n_crit, len(items))))
        elif no_label:
            # Не стоп: строка без метки бывает пунктом о форме самого отчёта («метки у каждого критерия»), где
            # проверять вживую нечего. Как проверено на деле, тим лид всё равно решает своей проверкой.
            out.append((WARN, 'метки проверки', '%d строк(и) без метки %s: %s — посмотри, пункт о форме отчёта или '
                        'исполнитель не сказал, как проверял' % (len(no_label), ' / '.join(labels), '; '.join(no_label[:3]))))
        else:
            out.append((OK, 'самопроверка по критериям', '%d из %d, у всех метка' % (len(items), n_crit)))
    # Раздел с нумерованными строками: проверки перед сдачей и ответы на вопросы о краях. Для краёв число строк
    # известно заранее — пропущенный вопрос виден по счёту.
    for title, want in ((rcfg.get('checks_section'), None), (rcfg.get('edges_section'), rcfg.get('edges_count', 8))):
        if not title:
            continue
        body = section(report, title)
        if body is None:
            out.append((STOP, title.lower(), 'в отчёте нет раздела'))
            continue
        rows = re.findall(r'^\d+\.\s*(.*)$', body, re.M)
        empty = [r for r in rows if not r.split(':', 1)[-1].split('—', 1)[-1].strip() or r.rstrip()[-1:] in '—:']
        if not rows or empty:
            out.append((STOP, title.lower(), 'пустых строк %d из %d' % (len(empty), len(rows))))
        elif want and len(rows) < want:
            out.append((STOP, title.lower(), 'ответов %d из %d — на каждый вопрос строка, не относится — «нет»'
                        % (len(rows), want)))
        else:
            out.append((OK, title.lower(), 'заполнены все %d' % len(rows)))
    for name, text, limit in (('задание', task, tcfg.get('max_lines')), ('отчёт', report, rcfg.get('max_lines'))):
        if limit and len(text.splitlines()) > limit:
            out.append((WARN, 'размер', '%s — %d строк при норме %d' % (name, len(text.splitlines()), limit)))
    return out


def main():
    ap = argparse.ArgumentParser(description='Проверка ветки задачи перед сдачей и приёмкой.')
    ap.add_argument('task', help='номер задачи, например CB_TASK_123')
    ap.add_argument('--lead', action='store_true', help='запуск тим лида: смотреть ветку задачи, а не текущую копию')
    ap.add_argument('--repo', default='.', help='папка репозитория (по умолчанию текущая)')
    ap.add_argument('--config', help='файл настройки (по умолчанию kit.toml в корне репозитория)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        repo = git(a.repo, 'rev-parse', '--show-toplevel').stdout.strip()
        cfg = load_config(repo, a.config)
        g, f = cfg.get('git', {}), cfg.get('files', {})
        task_id = a.task
        code = task_id.split('_TASK_')[0]
        main_ref = g.get('main', 'main')
        branch = g.get('task_branch', 'task/{id}').format(id=task_id, code=code)
        ref = branch if a.lead else 'HEAD'
        if git(repo, 'rev-parse', '--verify', '--quiet', ref, check=False).returncode != 0:
            raise Setup('нет ветки %s' % ref)
        results = [] if a.lead else check_place(repo, branch)
        results += check_merge(repo, main_ref, ref, g.get('bookkeeping', []), lead=a.lead)
        results += check_reverted(repo, main_ref, ref, task_id)
        results += check_migrations(repo, main_ref, ref, cfg.get('migrations', []))
        results += check_edges(repo, main_ref, ref, cfg.get('edges', []),
                               cfg.get('tests', {}).get('test_files', ['*/tests/*', 'tests/*', '*test_*.py', '*.test.js']))
        results += check_boundaries(repo, ref, cfg.get('boundaries', {}))
        status_rows, task = check_status(repo, ref, f['task'].format(id=task_id, code=code),
                                         f.get('backlog'), task_id, cfg.get('task', {}).get('handoff_status', 'REVIEW'))
        results += status_rows
        if task is not None:
            results += check_report(repo, ref, f['report'].format(id=task_id, code=code), task, cfg)
    except Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    for level, what, note in results:
        print('%-9s %s: %s' % (level, what, note))
    stops = sum(1 for r in results if r[0] == STOP)
    print('\nИтог: %s' % ('стоп-находок нет' if not stops else 'стоп-находок %d — сдавать нельзя' % stops
                           if not a.lead else 'стоп-находок %d — сливать нельзя' % stops))
    return 1 if stops else 0


if __name__ == '__main__':
    sys.exit(main())
