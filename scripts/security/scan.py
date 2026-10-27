"""Сканеры безопасности по правке ветки.

Безопасник запускает до охотников, тим лид — при приёмке, если triggers.py назвал повод:
    python scan.py                          # правка текущей ветки против main
    python scan.py --ref task/CB_TASK_123 --tools <папка с программами>
Что гоняется:
- Ruff, правила S (шаблоны опасного кода Python), — только по строкам правки;
- сканер секретов (по умолчанию Betterleaks) — по коммитам ветки;
- OSV-Scanner — по изменённым файлам зависимостей; уязвимость, которой не было до правки, — находка,
  бывшая и раньше — внимание;
- Hadolint — по изменённым Dockerfile, только строки правки.
Программы нет — строка «не проверено», не стоп: безопасник говорит владельцу, что поставить
(references/security/tools.md).

Находка сканера — не приговор. Безопасник отдаёт её опровергателю, как находку охотника.

Код возврата: 0 — находок нет, 1 — есть находка, 2 — ошибка запуска или настройки.
Настройка — раздел [security] файла kit.toml (образец — assets/kit.example.toml).
"""
import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lint'))
import changed  # noqa: E402  — общие помощники: строки правки, Ruff, сканер секретов

FOUND, WARN, SKIP, OK = 'НАХОДКА', 'ВНИМАНИЕ', 'НЕ ПРОВЕРЕНО', 'ОК'

DEFAULTS = {
    # S101 — assert, S105–S107 — пароль в коде (на нашем коде все находки ложные, секреты ловит сканер секретов),
    # S110 и S112 — пустой except (их держит scripts/lint/changed.py), S404, S603, S607 — любой вызов subprocess
    # (опасный вид — S602, shell=True, — остаётся).
    'ruff_ignore': ['S101', 'S105', 'S106', 'S107', 'S110', 'S112', 'S404', 'S603', 'S607'],
    'skip': ['*/tests/*', 'tests/*', '*test_*.py', '*_test.py', '*/migrations/*'],
    'secrets': ['betterleaks', 'git', '--log-opts={base}..{ref}', '--no-banner', '--redact', '--exit-code', '1'],
    'deps': ['requirements*.txt', 'poetry.lock', 'uv.lock', 'Pipfile.lock', 'pdm.lock', 'package-lock.json',
             'pnpm-lock.yaml', 'yarn.lock'],
    'docker': ['Dockerfile*', '*.dockerfile'],
    'tools_dir': '',
}


def load_config(repo, path):
    path = path or os.path.join(repo, 'kit.toml')
    data = {}
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = tomllib.load(f)
    elif path != os.path.join(repo, 'kit.toml'):
        raise changed.Setup('нет файла настройки %s' % path)
    sec = data.get('security', {})
    return data.get('git', {}).get('main', 'main'), {k: sec.get(k, v) for k, v in DEFAULTS.items()}


def tool(name, tools_dir):
    """Полный путь к программе: сначала папка инструментов, потом PATH. Нет — None."""
    if tools_dir:
        found = shutil.which(name, path=tools_dir)
        if found:
            return found
    return shutil.which(name)


def changed_files(repo, base, ref):
    out = changed.git(repo, '-c', 'core.quotepath=false', 'diff', '--name-only', '--no-renames', '--diff-filter=AM',
                      base, ref).stdout
    return [p for p in out.splitlines() if p]


def show(repo, ref, path):
    r = changed.git(repo, 'show', '%s:%s' % (ref, path), check=False)
    return r.stdout if r.returncode == 0 else None


def scan_ruff(repo, base, ref, cfg):
    out = []
    for path, rows in sorted(changed.added_rows(repo, base, ref).items()):
        if not path.endswith('.py') or any(fnmatch.fnmatch(path, g) for g in cfg['skip']):
            continue
        for row, code, message in changed.ruff(path, show(repo, ref, path), ['S'], repo):
            if row in rows and code not in cfg['ruff_ignore']:
                out.append((FOUND, '%s:%d' % (path, row), code, message))
    return out or [(OK, 'ruff S', '', 'на строках правки ничего')]


def scan_secrets(repo, base, ref, cfg):
    command = list(cfg['secrets'])
    if command:
        command[0] = tool(command[0], cfg['tools_dir']) or command[0]
    rows = changed.secrets(repo, base, ref, command)
    # Ответ помощника: СТОП — нашёл, ВНИМАНИЕ — не установлен или выключен.
    return [((FOUND if lvl == changed.STOP else SKIP if lvl == changed.WARN else OK), where, code, msg)
            for lvl, where, code, msg in rows]


def osv_vulns(exe, path, text):
    """Уязвимости файла зависимостей: {(пакет, версия, id): (оценка, синоним)}."""
    folder = tempfile.mkdtemp(prefix='kit-osv-')
    try:
        target = os.path.join(folder, os.path.basename(path))
        with open(target, 'w', encoding='utf-8') as f:
            f.write(text)
        r = subprocess.run([exe, 'scan', 'source', '-L', target, '--format', 'json'], capture_output=True,
                           text=True, encoding='utf-8', errors='replace')
        if r.returncode not in (0, 1):
            raise changed.Setup('osv-scanner, %s: %s' % (path, (r.stderr.strip().splitlines() or ['?'])[-1]))
        out = {}
        for res in json.loads(r.stdout or '{}').get('results', []):
            # Пакеты, записанные в файле, приходят с видом «lockfile». Косвенные — те, что сканер сам вычислил
            # для requirements.txt: их версия — его догадка, а не то, что стоит на сервере.
            direct = res.get('source', {}).get('type') == 'lockfile'
            for p in res.get('packages', []):
                score = {i: g.get('max_severity', '') for g in p.get('groups', []) for i in g.get('ids', [])}
                for v in p.get('vulnerabilities', []):
                    alias = next((a for a in v.get('aliases', []) if a.startswith('CVE-')), '')
                    out[(p['package']['name'], p['package']['version'], v['id'])] = (
                        score.get(v['id'], ''), alias, direct)
        return out
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def scan_deps(repo, base, ref, files, cfg):
    targets = [p for p in files if any(fnmatch.fnmatch(os.path.basename(p), g) for g in cfg['deps'])]
    if not targets:
        return []
    exe = tool('osv-scanner', cfg['tools_dir'])
    if not exe:
        return [(SKIP, 'зависимости', '', 'osv-scanner не установлен — изменены %s' % ', '.join(targets))]
    out = []
    for path in targets:
        now = osv_vulns(exe, path, show(repo, ref, path))
        before_text = show(repo, base, path)
        before = osv_vulns(exe, path, before_text) if before_text else {}
        # Строка на пакет: одна уязвимость приходит из нескольких баз под разными номерами — склеиваем по CVE.
        packages = {}
        for (name, version, vid), (score, alias, direct) in now.items():
            p = packages.setdefault((name, version), {'ids': {}, 'direct': direct, 'old': True})
            key = alias or vid
            p['ids'][key] = max(p['ids'].get(key, ''), score, key=lambda s: float(s or 0))
            if not any(k[0] == name and k[2] == vid for k in before):
                p['old'] = False
        for (name, version), p in sorted(packages.items()):
            worst = max(p['ids'].values(), key=lambda s: float(s or 0))
            ids = sorted(p['ids'], key=lambda k: -float(p['ids'][k] or 0))
            out.append((WARN if p['old'] else FOUND, path, '%s %s' % (name, version), '%d шт.%s: %s%s%s%s' % (
                len(ids), ', высшая оценка %s' % worst if worst else '', ', '.join(ids[:4]),
                ' …' if len(ids) > 4 else '',
                '' if p['direct'] else '; косвенный: версию вычислил сканер — сверь с установленной',
                '; было и до правки' if p['old'] else '')))
        if not now:
            out.append((OK, path, '', 'известных уязвимостей нет'))
    return out


def scan_docker(repo, base, ref, files, cfg):
    targets = [p for p in files if any(fnmatch.fnmatch(os.path.basename(p), g) for g in cfg['docker'])]
    if not targets:
        return []
    exe = tool('hadolint', cfg['tools_dir'])
    if not exe:
        return [(SKIP, 'Dockerfile', '', 'hadolint не установлен — изменены %s' % ', '.join(targets))]
    rows_by_file = changed.added_rows(repo, base, ref)
    out = []
    for path in targets:
        r = subprocess.run([exe, '--format', 'json', '-'], input=show(repo, ref, path), capture_output=True,
                           text=True, encoding='utf-8', errors='replace')
        rows = rows_by_file.get(path, set())
        for f in json.loads(r.stdout or '[]'):
            if f.get('line') in rows and f.get('level') in ('error', 'warning'):
                out.append((FOUND, '%s:%d' % (path, f['line']), f['code'], f['message']))
    return out or [(OK, 'Dockerfile', '', 'на строках правки ничего')]


def main():
    ap = argparse.ArgumentParser(description='Сканеры безопасности по правке ветки.')
    ap.add_argument('--repo', default='.', help='папка репозитория (по умолчанию текущая)')
    ap.add_argument('--base', help='с чем сравнивать (по умолчанию main из kit.toml)')
    ap.add_argument('--ref', default='HEAD', help='что проверять (по умолчанию текущая ветка)')
    ap.add_argument('--config', help='файл настройки (по умолчанию kit.toml в корне репозитория)')
    ap.add_argument('--tools', help='папка с программами (по умолчанию [security] tools_dir, потом PATH)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        repo = changed.git(a.repo, 'rev-parse', '--show-toplevel').stdout.strip()
        main_ref, cfg = load_config(repo, a.config)
        if a.tools:
            cfg['tools_dir'] = a.tools
        base = changed.git(repo, 'merge-base', a.base or main_ref, a.ref).stdout.strip()
        files = changed_files(repo, base, a.ref)
        found = scan_ruff(repo, base, a.ref, cfg)
        found += scan_secrets(repo, base, a.ref, cfg)
        found += scan_deps(repo, base, a.ref, files, cfg)
        found += scan_docker(repo, base, a.ref, files, cfg)
    except changed.Setup as e:
        print('Ошибка запуска: %s' % e)
        return 2
    for level, where, code, message in found:
        print('%-13s %s %s %s' % (level, where, code, message))
    hits = sum(1 for f in found if f[0] == FOUND)
    skipped = [f[1] for f in found if f[0] == SKIP]
    print('\nИтог: находок %d%s.%s' % (
        hits, ', не проверено: %s' % ', '.join(skipped) if skipped else '',
        ' Находки — опровергателю (references/security/lead.md, раздел 5).' if hits else ''))
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
