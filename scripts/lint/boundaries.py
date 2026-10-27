"""Проверка границ модулей по карте модулей спецификации.

Запускает `handoff/check.py` при каждой сдаче и приёмке, если в kit.toml есть раздел [boundaries]. Руками:
    python boundaries.py docs/spec.md                      # рабочая копия
    python boundaries.py docs/spec.md --ref task/CB_TASK_1 # ветка, без checkout
    python boundaries.py docs/spec.md --baseline docs/boundaries-known.json
    python boundaries.py docs/spec.md --all                # все нарушения, а не первые 20

Что проверяется. Импорты Python и относительные импорты JS/TS между модулями карты:
1. Модуль зовёт модуль, которого нет в его колонке «Может вызывать».
2. Модуль зовёт чужой модуль мимо его входа (колонка «Вход»). `from pkg import name` идёт через вход, если
   `pkg/__init__.py` сам связывает `name`: импортом, присваиванием или в `__all__`.
3. Модули зовут друг друга по кругу.
Вложенный модуль карты — отдельный модуль: связь родителя с ним проверяется так же. Импорт внутри своего модуля и
импорт библиотек не проверяются. Импорт из модуля в код вне карты — предупреждение.

Старые нарушения — список в файле --baseline: {"known": ["<файл> → <куда>: <что>", …]}, без номеров строк.
Нарушение из списка проходит, новое — стоп. Исправленное скрипт просит вычеркнуть (--update-baseline).
Файла нет, а --update-baseline дан — файл создаётся со всеми нынешними нарушениями: так заводят список в старом
проекте. Новое нарушение --update-baseline в список не добавляет: только руками, и это видно в правке.
Код возврата: 0 — стоп-находок нет, 1 — есть, 2 — ошибка запуска.
"""
import argparse
import ast
import json
import os
import posixpath
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lead'))
import spec_check  # noqa: E402

STOP, WARN, OK = 'СТОП', 'ВНИМАНИЕ', 'ОК'
PY = ('.py',)
JS = ('.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx')
JS_IMPORT = re.compile(r'''(?:\bimport\s+(?:[^'";]*?\bfrom\s+)?|\bexport\s+[^'";]*?\bfrom\s+|\brequire\s*\(\s*|\bimport\s*\(\s*)['"]([^'"]+)['"]''')


class Setup(Exception):
    """Ошибка запуска: нет файла, нет ветки, нет карты."""


class Tree:
    """Файлы репозитория: рабочая копия или коммит (через git, без checkout)."""

    def __init__(self, repo, ref=None):
        self.repo, self.ref = repo, ref
        if ref:
            r = subprocess.run(['git', '-C', repo, '-c', 'core.quotepath=false', 'ls-tree', '-r', '--name-only', ref],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode != 0:
                raise Setup('нет ветки или коммита %s' % ref)
            self.files = set(r.stdout.splitlines())
        else:
            self.files = set()
            for top, dirs, names in os.walk(repo):
                dirs[:] = [d for d in dirs if d not in spec_check.IGNORED_DIRS and not d.startswith('.')]
                rel = os.path.relpath(top, repo).replace('\\', '/')
                for n in names:
                    self.files.add(n if rel == '.' else rel + '/' + n)
        self.dirs = {posixpath.dirname(f) for f in self.files}
        for d in list(self.dirs):
            while d:
                d = posixpath.dirname(d)
                self.dirs.add(d)
        self.cache = {}

    def read(self, path):
        if self.ref:
            r = subprocess.run(['git', '-C', self.repo, 'show', '%s:%s' % (self.ref, path)],
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            return r.stdout if r.returncode == 0 else None
        try:
            with open(os.path.join(self.repo, path), encoding='utf-8', errors='replace') as f:
                return f.read()
        except OSError:
            return None

    def bound_names(self, init_path):
        """Имена, которые `__init__.py` связывает сам: импорты, присваивания, функции, классы, `__all__`."""
        if init_path not in self.cache:
            names = set()
            try:
                nodes = ast.parse(self.read(init_path) or '').body
            except SyntaxError:
                nodes = []
            for n in nodes:
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    names.update((a.asname or a.name).split('.')[0] for a in n.names)
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.add(n.name)
                elif isinstance(n, (ast.Assign, ast.AnnAssign)):
                    targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                    names.update(t.id for t in targets if isinstance(t, ast.Name))
                    if (any(isinstance(t, ast.Name) and t.id == '__all__' for t in targets)
                            and isinstance(n.value, (ast.List, ast.Tuple))):
                        names.update(e.value for e in n.value.elts
                                     if isinstance(e, ast.Constant) and isinstance(e.value, str))
            self.cache[init_path] = names
        return self.cache[init_path]


def owner(path, modules):
    """Модуль карты, в котором лежит путь: самый длинный подходящий."""
    best = None
    for m in modules:
        if path == m or path.startswith(m + '/'):
            if best is None or len(m) > len(best):
                best = m
    return best


def py_target(tree, dotted, bases):
    """Путь файла или пакета для имени `a.b.c`, или None — библиотека."""
    tail = dotted.replace('.', '/')
    for base in bases:
        p = posixpath.join(base, tail) if base else tail
        if p + '.py' in tree.files:
            return p + '.py'
        if p in tree.dirs:
            return p + '/__init__.py' if p + '/__init__.py' in tree.files else p
    return None


def py_imports(tree, path, text, bases, entries):
    """(строка, путь цели) для импортов файла Python, которые ведут в репозиторий."""
    try:
        nodes = ast.walk(ast.parse(text))
    except SyntaxError:
        return []
    out, here = [], posixpath.dirname(path)
    for n in nodes:
        if isinstance(n, ast.Import):
            for a in n.names:
                t = py_target(tree, a.name, bases)
                if t:
                    out.append((n.lineno, t))
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                pkg = here
                for _ in range(n.level - 1):
                    pkg = posixpath.dirname(pkg)
                local, mod = [pkg], n.module or ''
            else:
                local, mod = bases, n.module or ''
            base_t = py_target(tree, mod, local) if mod else (local[0] + '/__init__.py' if n.level else None)
            for a in n.names:
                # Имя, которое вход пакета отдаёт сам, берётся из входа, даже если рядом лежит файл с тем же именем.
                if base_t in entries and a.name in tree.bound_names(base_t):
                    t = base_t
                else:
                    t = py_target(tree, '.'.join(x for x in (mod, a.name) if x), local) if a.name != '*' else None
                    t = t or base_t
                if t:
                    out.append((n.lineno, t))
    return out


def js_imports(tree, path, text):
    out, here = [], posixpath.dirname(path)
    for m in JS_IMPORT.finditer(text):
        spec = m.group(1)
        if not spec.startswith('.'):
            continue
        p = posixpath.normpath(posixpath.join(here, spec))
        for c in [p] + [p + e for e in JS] + [p + '/index' + e for e in JS]:
            if c in tree.files:
                out.append((text.count('\n', 0, m.start()) + 1, c))
                break
    return out


def entry_ok(target, entry):
    """Цель импорта — вход модуля. Вход `None` — «весь модуль», годится любой файл."""
    if entry is None:
        return True
    stem = posixpath.splitext(target)[0]
    if entry.endswith('/'):  # вход-папка: импорт самой папки, её __init__.py или index.*
        d = entry.rstrip('/')
        return target == d or stem in (d + '/__init__', d + '/index')
    if posixpath.basename(entry) == '__init__.py' and target == posixpath.dirname(entry):
        return True
    return stem == posixpath.splitext(entry)[0]


def entry_file(entry):
    if entry is None:
        return None
    return entry.rstrip('/') + '/__init__.py' if entry.endswith('/') else entry


def read_known(tree, baseline):
    raw = tree.read(baseline)
    if raw is None:
        return None
    try:
        known = json.loads(raw).get('known')
    except (ValueError, AttributeError):
        known = None
    if not isinstance(known, list):
        raise Setup('файл старых нарушений %s: ждём {"known": ["…", …]}' % baseline)
    return set(known)


def check(repo, spec_rel, ref=None, baseline=None, update=False, limit=20):
    """[(уровень, что, подробно)] и {'issues': всего нарушений, 'new': новых}."""
    tree = Tree(repo, ref)
    text = tree.read(spec_rel)
    if text is None:
        raise Setup('нет файла спецификации %s' % spec_rel)
    roots, rows = spec_check.module_rows(spec_check.sections(text).get('Карта модулей', ''))
    rows = [r for r in rows if r['path']]
    if not rows:
        raise Setup('в карте модулей нет ни одного пути')
    modules = [r['path'] for r in rows]
    by_path = {r['path']: r for r in rows}
    entries = {entry_file(r['entry']) for r in rows if r['entry']}
    bases = ['']
    for r in roots:
        while r:
            bases.append(r)
            r = posixpath.dirname(r)

    found, edges, outside = {}, set(), {}  # found: нарушение без номера строки → номера строк
    for path in sorted(tree.files):
        src = owner(path, modules)
        if not src or not path.endswith(PY + JS):
            continue
        body = tree.read(path)
        if body is None:
            continue
        pairs = py_imports(tree, path, body, bases, entries) if path.endswith(PY) else js_imports(tree, path, body)
        for line, target in pairs:
            dst = owner(target, modules)
            if dst is None:
                if target.endswith(PY + JS):
                    outside.setdefault(target, set()).add(src)
                continue
            if dst == src:
                continue
            edges.add((src, dst))
            allowed = by_path[src]['calls']
            if allowed is not None and '*' not in allowed and dst not in allowed:
                found.setdefault((path, '`%s`: нет в «Может вызывать» у `%s`' % (dst, src)), set()).add(line)
            if not entry_ok(target, by_path[dst]['entry']):
                found.setdefault((path, '%s: мимо входа `%s`' % (target, by_path[dst]['entry'])), set()).add(line)
    issues = {'%s → %s' % k: '%s:%s → %s' % (k[0], ','.join(map(str, sorted(v))), k[1]) for k, v in found.items()}
    graph = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
    for loop in spec_check.find_cycles(graph):
        key = 'круг: %s' % ' → '.join('`%s`' % m for m in loop)
        issues[key] = key

    known = read_known(tree, baseline) if baseline else None
    keys = set(issues)
    new = sorted(keys - known) if known is not None else sorted(keys)
    fixed = sorted(known - keys) if known is not None else []
    out = []
    if not keys:
        out.append((OK, 'границы модулей', '%d модулей карты, нарушений нет' % len(modules)))
    elif known is not None and not new:
        out.append((OK, 'границы модулей', 'нарушений %d, все из списка старых — новых нет' % len(keys)))
    elif known is not None:
        out.append((STOP, 'границы модулей', 'новых нарушений %d (всего %d, в списке старых %d)'
                    % (len(new), len(keys), len(known))))
    else:
        out.append((STOP, 'границы модулей', 'нарушений %d' % len(keys)))
    shown = new if limit is None else new[:limit]
    if known is not None or not (update and baseline):
        out += [(STOP, 'граница', issues[k]) for k in shown]
        if len(new) > len(shown):
            out.append((STOP, 'граница', 'и ещё %d — все: --all' % (len(new) - len(shown))))
    if outside:
        sample = ', '.join('%s (из %s)' % (t, ', '.join('`%s`' % s for s in sorted(v)))
                           for t, v in sorted(outside.items())[:5])
        out.append((WARN, 'код вне карты', 'модули зовут %d файл(ов) без модуля: %s%s — внеси в карту или опиши '
                    'в «Как делим папки»' % (len(outside), sample, '' if len(outside) <= 5 else ', …')))

    if baseline and update and not ref:
        if known is None:
            write, new = sorted(keys), []
            out = [r for r in out if r[1] != 'граница']
            out[0] = (OK, 'границы модулей', 'нарушений %d — записаны в список старых' % len(keys))
        else:
            write = sorted(keys & known)
        if known is None or fixed:
            with open(os.path.join(repo, baseline), 'w', encoding='utf-8') as fh:
                json.dump({'known': write}, fh, ensure_ascii=False, indent=1)
                fh.write('\n')
            out.append((OK, 'список старых', '%s: записано %d' % (baseline, len(write))))
    elif fixed:
        out.append((WARN, 'список старых', 'исправлено %d: %s — вычеркни из %s в той же ветке (--update-baseline)'
                    % (len(fixed), '; '.join(fixed[:3]), baseline)))
    return out, {'issues': len(keys), 'new': len(new)}


def main():
    ap = argparse.ArgumentParser(description='Проверка границ модулей по карте модулей спецификации.')
    ap.add_argument('spec', help='файл спецификации, путь от корня репозитория')
    ap.add_argument('--repo', default='.', help='папка репозитория')
    ap.add_argument('--ref', help='ветка или коммит; без него — рабочая копия')
    ap.add_argument('--baseline', help='файл списка старых нарушений {"known": [...]}')
    ap.add_argument('--update-baseline', action='store_true',
                    help='вычеркнуть исправленные; файла нет — завести со всеми нынешними')
    ap.add_argument('--all', action='store_true', help='показать все нарушения, а не первые 20')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        r = subprocess.run(['git', '-C', a.repo, 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
        repo = r.stdout.strip() if r.returncode == 0 else os.path.abspath(a.repo)
        spec = os.path.relpath(os.path.abspath(a.spec), repo).replace('\\', '/') if os.path.exists(a.spec) else a.spec
        results, stats = check(repo, spec, a.ref, a.baseline, a.update_baseline, None if a.all else 20)
    except Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    for kind, what, detail in results:
        print('%-9s %s: %s' % (kind, what, detail))
    stops = any(r[0] == STOP for r in results)
    print('\nИтог: нарушений %d, новых %d — %s' % (stats['issues'], stats['new'], 'стоп' if stops else 'проходит'))
    return 1 if stops else 0


if __name__ == '__main__':
    sys.exit(main())
