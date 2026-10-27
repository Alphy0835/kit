"""Проверка спецификации и её связи с репозиторием и заданием.

Тим лид запускает после того, как написал спецификацию, после задачи-каркаса и перед выдачей задания:
    python spec_check.py docs/spec.md                     # разделы, карта модулей против папок
    python spec_check.py docs/spec.md --strict            # после каркаса: путь из карты обязан существовать
    python spec_check.py docs/spec.md --task CB_TASK_123  # и задание: поле «Спецификация», пути внутри карты

Что проверяется:
1. Обязательные разделы шаблона `assets/spec-template.md` есть и заполнены, а не оставлены заготовкой «<…>».
2. Каждый путь из карты модулей есть в репозитории. До каркаса — предупреждение, с `--strict` — стоп.
3. Папка в корне карты, которой нет в карте, — предупреждение, с `--strict` — стоп: у кода нет хозяина.
4. Метки «не определено: …» перечисляются — эту часть ещё нельзя резать на задачи.
5. Карта: строка «Как делим папки», колонки «Вход» и «Может вызывать»; в «Может вызывать» только модули карты,
   карта не разрешает круг; вход есть в репозитории (до каркаса — предупреждение); в kit.toml есть [boundaries].
6. «Данные» говорят о миграциях — есть строка «Файл последней миграции».
7. «Решения» — ссылки на файлы решений, файлы есть.
8. С `--task`: в задании есть поле «Спецификация», а пути из задания под корнями карты лежат внутри модуля карты;
   задание о миграции называет файл последней миграции.
9. В шапке есть «Владелец»; модуль, названный в «Сквозных сценариях», есть в карте.
10. «Схема системы» — блок Mermaid `flowchart` без заготовок «<…>»; стрелка без подписи и схема без рамок
    `subgraph` (границ доверия) — предупреждение.

Код на соответствие карте проверяет `scripts/lint/boundaries.py`, его запускает `handoff/check.py` при каждой сдаче.
Код возврата: 0 — стоп-находок нет, 1 — есть, 2 — ошибка запуска.
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

STOP, WARN, OK = 'СТОП', 'ВНИМАНИЕ', 'ОК'
REQUIRED = ['Цель и вне объёма', 'Стек', 'Карта модулей', 'Данные', 'Словарь', 'Сквозные сценарии',
            'Что менять, когда добавляешь', 'Совместимость', 'Риски и долг', 'Проверка']
# Папки, которые не модули: служебные и сборочные.
IGNORED_DIRS = {'__pycache__', 'node_modules', '.git', '.venv', 'venv', 'dist', 'build', '.pytest_cache'}
PLACEHOLDER = re.compile(r'<[^<>\n]+>')
UNDEFINED = re.compile(r'не определено:\s*(.+)', re.I)
MERMAID = re.compile(r'```mermaid\s*\n(.*?)```', re.S)
ARROW = re.compile(r'-->|-\.->|==>|--[xo]\b')
# Подпись стрелки: «A -->|что| B» или «A -- что --> B».
EDGE_LABEL = re.compile(r'\|[^|]+\||(?:--|-\.|==)\s*[^\s>|-][^>]*?(?:-->|\.->|==>)')


def sections(text):
    """{заголовок второго уровня: текст раздела}."""
    out, name, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m:
            if name is not None:
                out[name] = '\n'.join(buf)
            name, buf = m.group(1), []
        elif name is not None:
            buf.append(line)
    if name is not None:
        out[name] = '\n'.join(buf)
    return out


def table_rows(body):
    """Строки таблиц раздела без шапки и разделителя: списки ячеек."""
    rows, in_table = [], False
    for line in body.splitlines():
        if not line.strip().startswith('|'):
            in_table = False
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not in_table:
            in_table = True  # первая строка таблицы — шапка
            continue
        if set(''.join(cells)) <= set('-: '):
            continue
        rows.append(cells)
    return rows


def filled(body):
    """Раздел заполнен: строка таблицы с двумя ячейками текста; раздел без таблицы — строка текста без «<…>».

    Подсказки шаблона стоят в «<…>», подписи вроде «Вне объёма:» кончаются двоеточием — они не в счёт.
    """
    body = re.sub(r'<[^<>]*\n[^<>]*>', '', body)  # подсказка шаблона на несколько строк
    rows = table_rows(body)
    if any(sum(1 for c in cells if c and not PLACEHOLDER.search(c)) >= 2 for cells in rows):
        return True
    if rows or any(line.strip().startswith('|') for line in body.splitlines()):
        return False  # раздел с таблицей заполнен, только когда заполнена таблица
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(('|', '#')) or s.endswith(':') or PLACEHOLDER.search(s):
            continue
        if re.search(r'\w', s):
            return True
    return False


def norm(path):
    return path.strip().strip('`').replace('\\', '/').strip('/')


def first_table(body):
    """Шапка и строки первой таблицы раздела."""
    header, rows = None, []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith('|'):
            if header is not None:
                break
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if header is None:
            header = cells
        elif not set(''.join(cells)) <= set('-: '):
            rows.append(cells)
    return header or [], rows


def ticked(cell, keep_slash=False):
    """Пути в обратных кавычках, без заготовок «<…>»."""
    out = []
    for t in re.findall(r'`([^`]+)`', cell):
        if PLACEHOLDER.search(t):
            continue
        p = norm(t)
        out.append(p + '/' if keep_slash and t.strip().endswith('/') else p)
    return out


def module_rows(body):
    """Корни и строки карты: {path, entry, calls}.

    entry — путь входа от корня репозитория (папка кончается «/») или None — «весь модуль»;
    calls — множество путей модулей, '*' — любой; None — колонки «Может вызывать» нет.
    """
    roots = []
    m = re.search(r'^Корни:\s*(.+)$', body, re.M)
    if m:
        roots = ticked(m.group(1))
    header, rows = first_table(body)
    col = {h.lower(): i for i, h in enumerate(header)}
    i_entry, i_calls = col.get('вход'), col.get('может вызывать')
    out = []
    for cells in rows:
        paths = ticked(cells[0]) if cells else []
        if not paths:
            continue
        path, entry, calls = paths[0], None, None
        if i_entry is not None and i_entry < len(cells):
            e = ticked(cells[i_entry], keep_slash=True)
            if e:
                entry = e[0] if e[0].rstrip('/') == path or e[0].startswith(path + '/') else path + '/' + e[0]
        if i_calls is not None and i_calls < len(cells):
            raw = cells[i_calls]
            calls = set(ticked(raw)) | ({'*'} if re.search(r'\bлюб|\*', raw) else set())
        out.append({'path': path, 'entry': entry, 'calls': calls})
    return roots, out


def module_map(body):
    """Корни и пути карты модулей."""
    roots, rows = module_rows(body)
    return roots, [r['path'] for r in rows]


def line_value(body, label):
    """Значение строки «Подпись: …» раздела или None, если строки нет или в ней заготовка."""
    m = re.search(r'^\s*(?:[-*]\s*)?%s:\s*(.*)$' % re.escape(label), body, re.M | re.I)
    if not m or not m.group(1).strip() or PLACEHOLDER.search(m.group(1)):
        return None
    return m.group(1).strip()


def allowed_cycles(rows):
    """Круги в колонке «Может вызывать»: карта сама разрешает модулям звать друг друга по кругу."""
    return find_cycles({r['path']: {c for c in (r['calls'] or ()) if c != '*'} for r in rows})


def find_cycles(graph):
    """Круги в графе {модуль: {модули}}: списки [a, b, …, a], каждый круг один раз."""
    found, seen = [], set()

    def walk(node, stack):
        for nxt in sorted(graph.get(node, ())):
            if nxt in stack:
                loop = stack[stack.index(nxt):] + [nxt]
                if frozenset(loop) not in seen:
                    seen.add(frozenset(loop))
                    found.append(loop)
            elif len(stack) < 12:
                walk(nxt, stack + [nxt])

    for start in sorted(graph):
        walk(start, [start])
    return found


def covered(rel, paths):
    """Путь лежит внутри модуля карты или сам ведёт к модулю карты."""
    return any(rel == p or rel.startswith(p + '/') or p.startswith(rel + '/') for p in paths)


def inside(rel, paths):
    return any(rel == p or rel.startswith(p + '/') for p in paths)


def task_path(repo, task_id, config):
    fmt = 'team/tasks/{code}/{id}.md'
    cfg = config or os.path.join(repo, 'kit.toml')
    if tomllib and os.path.exists(cfg):
        with open(cfg, 'rb') as f:
            fmt = tomllib.load(f).get('files', {}).get('task', fmt)
    return os.path.join(repo, fmt.format(id=task_id, code=task_id.split('_TASK_')[0]))


def check_map(body, repo, level, config):
    """Строка «Как делим папки», колонки «Вход» и «Может вызывать», круги, раздел [boundaries] в kit.toml."""
    out = []
    if not line_value(body, 'Как делим папки'):
        out.append((STOP, 'карта модулей', 'нет строки «Как делим папки: …» — агенты разложат код каждый по-своему'))
    header, _ = first_table(body)
    cols = {h.lower() for h in header}
    for need in ('вход', 'может вызывать'):
        if need not in cols:
            out.append((STOP, 'карта модулей', 'нет колонки «%s» — границы не проверить' % need.capitalize()))
    _, rows = module_rows(body)
    known = {r['path'] for r in rows}
    unknown = sorted({c for r in rows for c in (r['calls'] or ()) if c != '*' and c not in known})
    if unknown:
        out.append((STOP, 'карта модулей', 'в «Может вызывать» модули не из карты: %s' % ', '.join(unknown[:8])))
    no_entry = [r['entry'] for r in rows if r['entry'] and not os.path.exists(os.path.join(repo, r['entry'].rstrip('/')))]
    if no_entry:
        out.append((level, 'карта модулей', 'входа нет в репозитории: %s' % ', '.join(no_entry[:8])))
    for loop in allowed_cycles(rows)[:5]:
        out.append((STOP, 'карта модулей', 'карта разрешает круг: %s' % ' → '.join('`%s`' % m for m in loop)))
    cfg = config or os.path.join(repo, 'kit.toml')
    if tomllib and os.path.exists(cfg):
        with open(cfg, 'rb') as f:
            if 'boundaries' not in tomllib.load(f):
                out.append((WARN, 'проверка границ', 'в kit.toml нет раздела [boundaries] — при сдаче границы '
                            'не проверяются'))
    return out


def check_task(text, roots, paths, head=None):
    out = []
    if head and re.search(r'миграц', text, re.I) and head not in {norm(t) for t in re.findall(r'`([^`]+)`', text)}:
        out.append((WARN, 'миграция', 'задание говорит о миграции, а файл последней миграции `%s` не назван — '
                    'две такие задачи не независимы' % head))
    field = re.search(r'^\|\s*Спецификация\s*\|\s*(.*?)\s*\|\s*$', text, re.M) or \
        re.search(r'^\s*(?:[-*]\s*)?\**Спецификация\**:\s*(.+)$', text, re.M)
    if not field or not field.group(1).strip(' -—'):
        out.append((STOP, 'задание', 'нет поля «Спецификация»: какой раздел и какие пути карты меняет задача'))
    else:
        out.append((OK, 'задание', 'поле «Спецификация»: %s' % field.group(1)[:120]))
    named = {norm(t) for t in re.findall(r'`([^`\s]+/[^`\s]*)`', text)}
    under_root = [p for p in named if any(p == r or p.startswith(r + '/') for r in roots)]
    outside = sorted(p for p in under_root if not inside(p, paths))
    if outside:
        out.append((STOP, 'пути задания', 'вне карты модулей: %s — сначала дополни спецификацию'
                    % ', '.join(outside[:8])))
    elif under_root:
        out.append((OK, 'пути задания', '%d путь(ей), все внутри карты' % len(under_root)))
    else:
        out.append((WARN, 'пути задания', 'задание не называет ни одного пути под корнями карты — исполнитель '
                    'сам решит, куда класть код'))
    return out


def check_diagram(body):
    """Раздел «Схема системы»: блок Mermaid, подписи стрелок, рамки границ доверия."""
    m = MERMAID.search(body or '')
    if not m:
        return [(STOP, 'схема системы', 'нет блока ```mermaid — части, стрелки и границы доверия не видны до задач')]
    code = m.group(1)
    lines = [x.strip() for x in code.splitlines() if x.strip() and not x.strip().startswith('%%')]
    if any(PLACEHOLDER.search(re.sub(r'<br\s*/?>', '', x)) for x in lines):
        return [(STOP, 'схема системы', 'в схеме осталась заготовка «<…>»')]
    if not lines or not re.match(r'(flowchart|graph)\b', lines[0]):
        return [(WARN, 'схема системы', 'вид схемы не `flowchart` — правило 10 справки `spec.md`')]
    out = []
    edges = [x for x in lines if ARROW.search(x)]
    bare = [x for x in edges if not EDGE_LABEL.search(x)]
    if not edges:
        out.append((WARN, 'схема системы', 'нет ни одной стрелки — не видно, кто кого зовёт'))
    if bare:
        out.append((WARN, 'схема системы', 'стрелки без подписи «что, как, чем доказывает»: %s'
                    % '; '.join(b[:60] for b in bare[:5])))
    if not any(x.startswith('subgraph') for x in lines):
        out.append((WARN, 'схема системы', 'нет рамок `subgraph` — границы доверия не нарисованы'))
    if not out:
        out.append((OK, 'схема системы', 'стрелок %d, все подписаны, границы доверия есть' % len(edges)))
    return out


def main():
    ap = argparse.ArgumentParser(description='Проверка спецификации и её связи с репозиторием и заданием.')
    ap.add_argument('spec', help='файл спецификации')
    ap.add_argument('--repo', help='корень репозитория (по умолчанию — репозиторий, где лежит спецификация)')
    ap.add_argument('--strict', action='store_true', help='после каркаса: путь карты обязан существовать')
    ap.add_argument('--task', help='номер задания для сверки, например CB_TASK_123')
    ap.add_argument('--config', help='kit.toml (по умолчанию в корне репозитория)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    if not os.path.exists(a.spec):
        print('Ошибка запуска: нет файла %s' % a.spec)
        return 2
    repo = a.repo
    if not repo:
        r = subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(a.spec)), 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        repo = r.stdout.strip() if r.returncode == 0 else os.getcwd()
    with open(a.spec, encoding='utf-8') as f:
        text = f.read()
    secs = sections(text)
    results = []

    for name in REQUIRED:
        if name not in secs:
            results.append((STOP, 'раздел «%s»' % name, 'нет в спецификации'))
        elif not filled(secs[name]):
            results.append((STOP, 'раздел «%s»' % name, 'пустой или заготовка «<…>»'))
    if not any(r[0] == STOP for r in results):
        results.append((OK, 'разделы', 'все %d на месте и заполнены' % len(REQUIRED)))

    roots, paths = module_map(secs.get('Карта модулей', ''))
    level = STOP if a.strict else WARN
    if not roots:
        results.append((STOP, 'карта модулей', 'нет строки «Корни: `папка/`» — непонятно, где искать код без хозяина'))
    missing = [p for p in paths if not os.path.exists(os.path.join(repo, p))]
    if missing:
        results.append((level, 'карта модулей', 'нет в репозитории: %s%s' % (', '.join(missing[:8]),
                        '' if a.strict else ' — создаёт задача-каркас')))
    elif paths:
        results.append((OK, 'карта модулей', '%d путь(ей), все есть в репозитории' % len(paths)))
    for root in roots:
        full = os.path.join(repo, root)
        if not os.path.isdir(full):
            continue
        extra = sorted(d for d in os.listdir(full)
                       if os.path.isdir(os.path.join(full, d)) and d not in IGNORED_DIRS and not d.startswith('.')
                       and not covered('%s/%s' % (root, d) if root else d, paths))
        if extra:
            results.append((level, 'папки без хозяина', 'в `%s/` нет в карте: %s' % (root, ', '.join(extra[:8]))))

    map_body = secs.get('Карта модулей', '')
    results += check_map(map_body, repo, level, a.config)
    results += check_diagram(secs.get('Схема системы'))
    if not line_value(text.split('\n## ', 1)[0], 'Владелец'):
        results.append((WARN, 'шапка', 'нет строки «Владелец: …» — непонятно, кто подтверждает и снимает «не определено»'))
    named = {norm(x) for line in secs.get('Сквозные сценарии', '').splitlines() if not PLACEHOLDER.search(line)
             for x in ticked(line)}
    unknown = sorted(x for x in named if '/' in x and not inside(x, paths))
    if unknown:
        results.append((WARN, 'сквозные сценарии', 'модулей нет в карте: %s' % ', '.join(unknown[:8])))
    data = secs.get('Данные', '')
    head = line_value(data, 'Файл последней миграции')
    if re.search(r'миграц', data, re.I) and not head and not re.search(r'миграций нет', data, re.I):
        results.append((WARN, 'миграции', 'нет строки «Файл последней миграции: `путь`» — столкновение номеров '
                        'у параллельных задач ничем не ловится'))
    spec_dir = os.path.dirname(os.path.abspath(a.spec))
    links = [p for line in secs.get('Решения', '').splitlines() if line.lstrip().startswith(('-', '*'))
             for p in ticked(line) if p.endswith('.md')]
    lost = [p for p in links if not os.path.exists(os.path.join(repo, p)) and not os.path.exists(os.path.join(spec_dir, p))]
    if lost:
        results.append((WARN, 'решения', 'нет файлов: %s' % ', '.join(lost[:8])))
    elif not links and any(sum(1 for c in r if c and not PLACEHOLDER.search(c)) >= 2
                           for r in table_rows(secs.get('Решения', ''))):
        results.append((WARN, 'решения', 'решения записаны в самой спецификации — каждое в свой файл по '
                        '`assets/decision-template.md`, здесь только ссылки'))

    # Строка с заготовкой «<…>» — пример из шаблона, а не открытый вопрос.
    undefined = [m.group(1).strip() for line in text.splitlines() if not PLACEHOLDER.search(line)
                 for m in [UNDEFINED.search(line)] if m]
    if undefined:
        results.append((WARN, 'не определено', '%d: %s — эту часть на задачи не режь'
                        % (len(undefined), '; '.join(u[:80] for u in undefined[:5]))))

    if a.task:
        path = task_path(repo, a.task, a.config)
        if not os.path.exists(path):
            results.append((STOP, 'задание', 'нет файла %s' % path))
        else:
            with open(path, encoding='utf-8') as f:
                results += check_task(f.read(), roots, paths, norm(head.strip('`')) if head else None)

    for kind, what, detail in results:
        print('%-9s %s: %s' % (kind, what, detail))
    stops = sum(1 for r in results if r[0] == STOP)
    print('\nИтог: %s' % ('стоп-находок нет' if not stops else 'стоп-находок %d' % stops))
    return 1 if stops else 0


if __name__ == '__main__':
    sys.exit(main())
