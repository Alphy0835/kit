"""Выбор и прогон тестов по правке ветки.

Исполнитель запускает из рабочей копии своей задачи:
    python tests.py CB_TASK_123
Посмотреть выбор без прогона:
    python tests.py CB_TASK_123 --dry-run
Тим лид запускает в своей копии сразу после слияния, на слитом коде; HEAD~1 — main до слияния:
    python tests.py CB_TASK_123 --base HEAD~1

Откуда берутся тесты, по каждому набору тестов (suite) из `kit.toml`:
1. Файлы из поля «Тесты» задания.
2. Тесты, которые ветка добавила или изменила.
3. Тесты, которые импортируют изменённый модуль напрямую; для файлов не на Python — тесты, где встречается
   имя файла.
4. Тесты-переписи из настройки `always` — всегда, если набор задет.
Полный прогон — если поле говорит «полный» или задет общий файл из `full_when`. Если правка задела только
документы, тесты кода не запускаются, кроме названных в поле.

Код возврата: 0 — зелёно или нечего запускать; 1 — тесты красные; 2 — ошибка запуска или настройки;
3 — сбой окружения: два повтора не дали итоговой строки.
"""
import argparse
import fnmatch
import glob
import os
import re
import subprocess
import sys
import time
import tomllib

# Итоговая строка pytest: с рамкой «===» в обычном режиме и без неё при -q.
SUMMARY = re.compile(r'^(?:=+ )?(?:\d+ \w+.*|no tests ran.*) in [\d.]+s\b.*$', re.M)
CRASH = re.compile(r'worker .* crashed|node down|INTERNALERROR', re.I)


class Setup(Exception):
    pass


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise Setup('git %s: %s' % (' '.join(args), r.stderr.strip()))
    return r.stdout


def matches(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def tests_field(repo, cfg, task_id, ref):
    path = cfg['files']['task'].format(id=task_id, code=task_id.split('_TASK_')[0])
    r = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (ref, path)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        return ''
    text = r.stdout
    m = re.search(r'^\|\s*Тесты\s*\|\s*(.*?)\s*\|\s*$', text, re.M)
    return m.group(1) if m else ''


def field_tokens(value):
    """Пути из поля: всё в обратных кавычках, разбитое по пробелам, что похоже на тест."""
    out = []
    for chunk in re.findall(r'`([^`]+)`', value):
        for tok in chunk.split():
            tok = tok.strip('"\'')
            if re.search(r'(^|/)tests?(/|$)|test_[^/]*\.py$|\.test\.js$', tok) and not tok.startswith('-'):
                out.append(tok)
    return out


def js_tests_named(value):
    return any(t.endswith('.js') for t in field_tokens(value))


def resolve(repo, suite, token):
    """Путь из поля в путь от корня набора; None, если такого файла или папки нет."""
    root = os.path.join(repo, suite['root'])
    # Путь от корня репозитория («Коннектор/tests/…») тоже годится, если он лежит внутри набора.
    for base in [root] + [os.path.join(repo, p) for p in suite.get('paths', [])] + [repo]:
        cand = os.path.normpath(os.path.join(base, token))
        inside = os.path.commonpath([os.path.normcase(cand), os.path.normcase(os.path.normpath(root))]) == \
            os.path.normcase(os.path.normpath(root))
        if inside and glob.glob(cand):
            return os.path.relpath(cand, root).replace(os.sep, '/')
    return None


def module_name(rel):
    """`app/alerts/telegram.py` -> `app.alerts.telegram`; `pkg/__init__.py` -> `pkg`."""
    mod = rel[:-3].replace('/', '.')
    return mod[:-9] if mod.endswith('.__init__') else mod


def importers(root, py_files, targets):
    """Файлы из py_files, которые импортируют один из модулей targets.

    Совпадение точное: `from a.b import x`, `import a.b`, `from a import b`. Импорт подмодуля `a.b.c`
    не считается импортом `a.b`: правка `__init__` пакета иначе тянет все тесты его подмодулей.
    """
    out = set()
    pats = []
    for t in targets:
        parent, _, last = t.rpartition('.')
        rx = r'^\s*(from\s+%s\s+import\b|import\s+%s\s*(,|$|\s+as\b))' % (re.escape(t), re.escape(t))
        if parent:
            rx += r'|^\s*from\s+%s\s+import\s+[^\n]*\b%s\b' % (re.escape(parent), re.escape(last))
        pats.append(re.compile(rx, re.M))
    for f in py_files:
        try:
            text = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        if any(p.search(text) for p in pats):
            out.add(f)
    return out


def select(repo, cfg, suite, changed, field_value):
    """Возвращает (режим, файлы тестов, пояснения). Режим: skip, docs, full, list."""
    root_rel = suite['root'].rstrip('/') + '/'
    mine = [p for p in changed if any(p.startswith(x) for x in suite.get('paths', [root_rel]))]
    notes = []
    named = []
    for tok in field_tokens(field_value):
        r = resolve(repo, suite, tok)
        # JS-тесты гоняет свой запуск (`js` в настройке набора), pytest их не соберёт.
        if r and not r.endswith('.js'):
            named.append(r)
    if not mine:
        if named:
            return 'docs', sorted(set(named)), ['набор не задет правкой — запускаются только названные в поле «Тесты»']
        return 'skip', [], ['набор не задет правкой']
    docs = cfg.get('tests', {}).get('docs_only', ['*.md'])
    code = [p for p in mine if not matches(p, docs)]
    if not code:
        return 'docs', sorted(set(named)), ['задеты только документы — тесты кода не запускаются, только названные в поле']
    shared = [p for p in code if matches(p, suite.get('full_when', []))]
    if re.search(r'(^|[\s(`])полный', field_value):
        return 'full', [], ['в поле «Тесты» сказано «полный»']
    if shared:
        return 'full', [], ['задет общий файл: %s' % ', '.join(shared[:5])]
    root = os.path.join(repo, suite['root'])
    tests_dir = suite.get('tests', 'tests')
    all_tests = sorted(os.path.relpath(p, root).replace(os.sep, '/')
                       for p in glob.glob(os.path.join(root, tests_dir, '**', 'test_*.py'), recursive=True))
    rel = [p[len(root_rel):] for p in code if p.startswith(root_rel)]
    touched_tests = [p for p in rel if p in all_tests]
    py = [p for p in rel if p.endswith('.py') and p not in all_tests and not p.startswith(tests_dir + '/')]
    other = [p for p in rel if not p.endswith('.py') and not p.startswith(tests_dir + '/')]
    by_import = importers(root, all_tests, {module_name(p) for p in py})
    by_name = set()
    for p in other:
        base = os.path.basename(p)
        for t in all_tests:
            if base in open(os.path.join(root, t), encoding='utf-8', errors='replace').read():
                by_name.add(t)
    always = [a for a in suite.get('always', []) if a in all_tests]
    picked = set(named) | set(touched_tests) | by_import | by_name | set(always)
    extra = sorted(picked - set(named) - set(always))
    if named and extra:
        notes.append('вне поля «Тесты» добавлено %d: %s — напиши в отчёте, что правка вышла за список'
                     % (len(extra), ', '.join(extra[:8]) + (' …' if len(extra) > 8 else '')))
    return 'list', sorted(picked), notes


def run(cmd, cwd, timeout):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        out, code = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, code = (e.stdout or '') if isinstance(e.stdout, str) else '', None
    return out, code, time.time() - t0


def run_pytest(suite, root, files):
    """Прогон с повторами при сбое окружения. Возвращает код итога: 0, 1, 2 или 3.

    Решает код возврата самого pytest: 0 — зелёно, 1 и 2 (прерван ошибкой сбора) — красно, 4 и 5 — неверный
    запуск. Код 5 — pytest не собрал ни одного теста из переданных: выбор пустой или не тех файлов, это не зелёно.
    Сбой окружения — срок вышел, код 3 или упал воркер; тогда повтор.
    Итоговая строка нужна только для вывода: при `-qq` в addopts pytest её не печатает.
    """
    attempts = [suite.get('command', ['python', '-m', 'pytest'])] + suite.get('retry', [])[:2]
    timeout = suite.get('timeout_seconds', 1200)
    for i, cmd in enumerate(attempts):
        print('  запуск: %s' % ' '.join(cmd + (['<%d файл(ов)>' % len(files)] if files else [])))
        out, code, took = run(cmd + files, root, timeout)
        found = SUMMARY.findall(out)
        summary = found[-1].strip('= ') if found else 'итоговой строки нет'
        if code is None:
            print('  сбой окружения: прогон не уложился в %d с' % timeout)
        elif code == 3 or CRASH.search(out):
            print('  сбой окружения: внутренняя ошибка pytest или упал воркер (код %s)' % code)
        elif code in (4, 5):
            why = 'тестов не собрано — выбор пустой или не тех файлов' if code == 5 else 'неверный запуск pytest'
            print('  %s (код %d):\n' % (why, code) + '\n'.join('    ' + l for l in out.strip().splitlines()[-5:]))
            return 2
        elif code in (0, 1, 2):
            print('  итог: %s (код %d, %.0f с)' % (summary, code, took))
            if code in (1, 2):
                print('\n'.join(['    ' + l for l in out.splitlines() if l.startswith(('FAILED', 'ERROR'))][:20]))
            return 0 if code == 0 else 1
        else:
            print('  сбой окружения: неожиданный код %s' % code)
        if i + 1 < len(attempts):
            print('  повтор %d из 2' % (i + 1))
    return 3


def main():
    ap = argparse.ArgumentParser(description='Выбор и прогон тестов по правке ветки.')
    ap.add_argument('task')
    ap.add_argument('--base', help='с чем сравнивать правку (по умолчанию main из настройки)')
    ap.add_argument('--ref', default='HEAD', help='что проверять (по умолчанию текущая копия); с --dry-run — любая ветка')
    ap.add_argument('--repo', default='.')
    ap.add_argument('--config')
    ap.add_argument('--dry-run', action='store_true', help='показать выбор, не запускать')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        repo = git(a.repo, 'rev-parse', '--show-toplevel').strip()
        cfg_path = a.config or os.path.join(repo, 'kit.toml')
        if not os.path.exists(cfg_path):
            raise Setup('нет файла настройки %s' % cfg_path)
        cfg = tomllib.load(open(cfg_path, 'rb'))
        base = a.base or cfg.get('git', {}).get('main', 'main')
        if a.ref != 'HEAD' and not a.dry_run:
            raise Setup('прогон идёт по файлам на диске — --ref годится только с --dry-run')
        mb = git(repo, 'merge-base', base, a.ref).strip()
        if a.ref == 'HEAD':
            # Текущая копия: правка — и закоммиченное, и то, что ещё лежит на диске. Исполнитель гоняет
            # тесты до коммита.
            changed = [l for l in git(repo, 'diff', '--name-only', '-z', mb).split('\0') if l]
            changed += [l for l in git(repo, 'ls-files', '--others', '--exclude-standard', '-z').split('\0')
                        if l and l not in changed]
        else:
            changed = [l for l in git(repo, 'diff', '--name-only', '-z', mb, a.ref).split('\0') if l]
        field_value = tests_field(repo, cfg, a.task, a.ref)
        if not changed:
            fresh = git(repo, 'rev-parse', a.ref).strip() == git(repo, 'rev-parse', base).strip() \
                and git(repo, 'rev-parse', '--abbrev-ref', a.ref).strip() != base
            merged = not fresh and subprocess.run(
                ['git', '-C', repo, 'merge-base', '--is-ancestor', a.ref, base]).returncode == 0
            if merged:
                raise Setup('ветка уже входит в историю %s (слита или слита и откачена), сравнивать не с чем. '
                            'После своего слияния сравнивай с коммитом до него: --base HEAD~1' % base)
            print('Правка против %s пустая: ветка не меняет ни одного файла. Тесты не нужны.' % base)
            return 0
        suites = cfg.get('tests', {}).get('suite', [])
        if not suites:
            raise Setup('в настройке нет ни одного [[tests.suite]]')
    except Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    print('Правка: %d файл(ов) против %s.' % (len(changed), base))
    prose = re.sub(r'`[^`]+`', '', field_value).strip(' ;,.')
    if re.search(r'найди|grep|которые задевает|тесты docs', prose):
        print('В поле «Тесты» есть указание словами — скрипт его не выполняет, сделай сам: «%s»' % prose[:200])
    lost = [t for t in field_tokens(field_value) if not any(resolve(repo, s, t) for s in suites)]
    if lost:
        print('ВНИМАНИЕ: в поле «Тесты» есть пути, которых нет ни в одном наборе: %s — опечатка в задании '
              'или тест ещё не написан' % ', '.join(lost))
    if js_tests_named(field_value) and not any(s.get('js') for s in suites):
        print('В поле «Тесты» есть JS-тесты, а ни у одного набора нет запуска `js` — запусти их сам')
    codes = set()
    for suite in suites:
        root = os.path.join(repo, suite['root'])
        mode, files, notes = select(repo, cfg, suite, changed, field_value)
        print('\n[%s] %s' % (suite['name'], {'skip': 'не задет', 'docs': 'только документы', 'full': 'полный прогон',
                                              'list': 'выбрано файлов: %d' % len(files)}[mode]))
        for n in notes:
            print('  ' + n)
        js = suite.get('js')
        js_hit = js and any(matches(p, js.get('when', [])) for p in changed)
        if mode in ('list', 'docs') and files:
            print('  ' + ' '.join(files))
        if mode == 'list' and not files:
            # pytest без списка гоняет весь набор: «выбрано 0» не должно молча стать полным прогоном.
            print('  на правку не нашлось ни одного теста: напиши тест на изменённое поведение '
                  'или назови тесты в поле «Тесты»; прогон не делаю')
        elif mode == 'skip' or (mode == 'docs' and not files):
            pass
        elif a.dry_run:
            print('  ожидаемо около %s с; прогон не делаю (--dry-run)' % suite.get('expected_seconds', '?'))
        else:
            print('  ожидаемо около %s с, срок %s с' % (suite.get('expected_seconds', '?'), suite.get('timeout_seconds', 1200)))
            codes.add(run_pytest(suite, root, [] if mode == 'full' else files))
        if js_hit:
            print('  JS: %s' % ' '.join(js['command']))
            if not a.dry_run:
                out, code, took = run(js['command'], root, suite.get('timeout_seconds', 1200))
                tail = [l for l in out.splitlines() if re.match(r'^(?:#|ℹ) (pass|fail|tests)\b', l)]
                print('  итог JS: %s (код %s, %.0f с)' % (', '.join(tail) or 'нет итога', code, took))
                codes.add(0 if code == 0 else 1)
    for lint in cfg.get('tests', {}).get('lint', []):
        if not a.dry_run and any(p.endswith('.py') for p in changed):
            out, code, _ = run(lint, repo, 300)
            print('\nЛинтер %s: %s' % (' '.join(lint), 'чисто' if code == 0 else 'есть замечания (код %s)' % code))
            if code != 0:
                print('\n'.join('  ' + l for l in out.splitlines()[:20]))
            codes.add(0 if code == 0 else 1)
    if a.dry_run:
        print('\nИтог: выбор показан, тесты не запускались')
        return 0
    if not codes:
        print('\nИтог: тесты не запускались — зелёным это не считается')
        return 0
    # Красный тест важнее сбоя окружения: он уже доказывает, что сдавать нельзя.
    worst = next((c for c in (1, 3, 2) if c in codes), 0)
    print('\nИтог: %s' % {0: 'зелёно', 1: 'красно — сдавать нельзя', 2: 'неверный запуск — проверь настройку',
                          3: 'сбой окружения после двух повторов — напиши тим лиду'}[worst])
    return worst


if __name__ == '__main__':
    sys.exit(main())
