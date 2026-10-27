"""Проверка чужого пакета, репозитория или файла правил агента до того, как его взять.

    python vet.py pypi <имя> [версия]
    python vet.py npm <имя> [версия]
    python vet.py repo <владелец/имя>          # репозиторий на GitHub
    python vet.py file <путь>                  # скил, правила агента, настройка MCP — подозрительные места
Данные — открытые и бесплатные, без ключей: реестры PyPI и npm, deps.dev, OSV, GitHub. Наружу уходят только имя
пакета, версия и имя репозитория. Режим file в сеть не ходит.

Скрипт отвечает на вопросы, которые видны по данным: есть ли пакет, жив ли, уязвимости версии, лицензия,
скрипты установки, оценка OpenSSF Scorecard. Остальное — references/security/vetting.md, решает безопасник.

Код возврата: 0 — тревог нет, 1 — есть тревога, 2 — ошибка запуска (нет сети, нет пакета в реестре — тоже
тревога, а не ошибка: выдуманное имя — главный случай).
"""
import argparse
import datetime
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ALARM, NOTE, OK = 'ТРЕВОГА', 'ЗАМЕТКА', 'ОК'
TIMEOUT = 20


class Setup(Exception):
    """Ошибка запуска: нет сети, плохой ответ."""


def get(url, data=None):
    """JSON по адресу. 404 — None."""
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={'User-Agent': 'kit-vet', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 — адреса в коде, только https
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise Setup('%s: ответ %s' % (url.split('?')[0], e.code)) from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise Setup('%s: %s' % (url.split('?')[0], e)) from e


def age_days(stamp):
    if not stamp:
        return None
    t = datetime.datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.timezone.utc)
    return (datetime.datetime.now(datetime.timezone.utc) - t).days


def osv(ecosystem, name, version):
    d = get('https://api.osv.dev/v1/query', {'package': {'name': name, 'ecosystem': ecosystem}, 'version': version})
    # Одна уязвимость приходит из нескольких баз под разными номерами: склеиваем по номеру CVE.
    seen = {}
    for v in (d or {}).get('vulns', []):
        cve = next((a for a in v.get('aliases', []) if a.startswith('CVE-')), v['id'])
        seen.setdefault(cve, v['id'])
    return ['%s (%s)' % (cve, vid) if cve != vid else vid for cve, vid in seen.items()]


def depsdev(system, name, version):
    """Лицензии версии и связанный репозиторий из deps.dev."""
    d = get('https://api.deps.dev/v3/systems/%s/packages/%s/versions/%s' % (
        system, urllib.parse.quote(name, safe=''), urllib.parse.quote(version, safe=''))) or {}
    repo = next((p['projectKey']['id'] for p in d.get('relatedProjects', [])
                 if p.get('relationType') == 'SOURCE_REPO'), None)
    return d.get('licenses', []), repo


def scorecard(project):
    d = get('https://api.deps.dev/v3/projects/%s' % urllib.parse.quote(project, safe='')) or {}
    sc = d.get('scorecard') or {}
    weak = [c['name'] for c in sc.get('checks', []) if c.get('score', -1) in range(0, 4)]
    return sc.get('overallScore'), weak


def common(rows, ecosystem, system, name, version, licenses_from_registry):
    vulns = osv(ecosystem, name, version)
    rows.append((ALARM, 'уязвимости версии %s: %s' % (version, ', '.join(vulns[:8]) + (' …' if len(vulns) > 8 else ''))
                 ) if vulns else (OK, 'известных уязвимостей у %s нет' % version))
    licenses, repo = depsdev(system, name, version)
    licenses = licenses or licenses_from_registry
    rows.append((OK, 'лицензия: %s' % ', '.join(licenses)) if licenses else (ALARM, 'лицензия не указана'))
    if repo:
        score, weak = scorecard(repo)
        rows.append((NOTE, 'репозиторий %s, Scorecard %s из 10%s — подсказка, не приговор' % (
            repo, score if score is not None else 'нет', '; слабые проверки: %s' % ', '.join(weak) if weak else '')))
    else:
        rows.append((NOTE, 'репозиторий исходников не найден в deps.dev — сверь ссылку на сайте проекта'))


def vet_pypi(name, version):
    d = get('https://pypi.org/pypi/%s/json' % urllib.parse.quote(name))
    if not d:
        return [(ALARM, 'пакета «%s» нет в PyPI — имя выдумано или с опечаткой' % name)]
    info, releases = d['info'], d.get('releases', {})
    rows = []
    if info['name'].lower().replace('_', '-') != name.lower().replace('_', '-'):
        rows.append((NOTE, 'в реестре имя «%s»' % info['name']))
    version = version or info['version']
    if version not in releases:
        return rows + [(ALARM, 'версии %s в PyPI нет' % version)]
    stamps = sorted(f['upload_time_iso_8601'] for files in releases.values() for f in files)
    first, last = (age_days(stamps[0]), age_days(stamps[-1])) if stamps else (None, None)
    rows.append((ALARM if first is not None and first < 90 else OK,
                 'первый выпуск %s дн. назад, выпусков %d' % (first, len(releases))))
    rows.append((ALARM if last is not None and last > 365 else OK, 'последний выпуск %s дн. назад' % last))
    if any(f.get('yanked') for f in releases.get(version, [])):
        rows.append((ALARM, 'версия %s отозвана автором' % version))
    if re.match(r'0\.|.*(?:a|b|rc|dev)\d*$', version):
        rows.append((NOTE, 'версия %s — не стабильная (0.x, альфа, бета)' % version))
    if not any(f['packagetype'] == 'bdist_wheel' for f in releases.get(version, [])):
        rows.append((NOTE, 'у %s нет готовой сборки (wheel): при установке исполнится код сборки' % version))
    lic = info.get('license_expression') or (info.get('license') or '')[:60]
    common(rows, 'PyPI', 'pypi', name, version, [lic] if lic else [])
    return rows


def vet_npm(name, version):
    d = get('https://registry.npmjs.org/%s' % urllib.parse.quote(name, safe='@'))
    if not d:
        return [(ALARM, 'пакета «%s» нет в npm — имя выдумано или с опечаткой' % name)]
    version = version or d.get('dist-tags', {}).get('latest')
    manifest = d.get('versions', {}).get(version)
    if not manifest:
        return [(ALARM, 'версии %s в npm нет' % version)]
    times = d.get('time', {})
    rows = [(ALARM if (age_days(times.get('created')) or 0) < 90 else OK,
             'пакет создан %s дн. назад, выпусков %d' % (age_days(times.get('created')), len(d.get('versions', {})))),
            (ALARM if (age_days(times.get('modified')) or 0) > 365 else OK,
             'последнее изменение %s дн. назад' % age_days(times.get('modified')))]
    if manifest.get('deprecated'):
        rows.append((ALARM, 'версия помечена устаревшей: %s' % str(manifest['deprecated'])[:100]))
    hooks = {k: v for k, v in (manifest.get('scripts') or {}).items() if k in ('preinstall', 'install', 'postinstall')}
    rows.append((ALARM, 'скрипты установки: %s' % '; '.join('%s: %s' % kv for kv in hooks.items())[:200])
                if hooks else (OK, 'скриптов установки нет'))
    deps = len(manifest.get('dependencies') or {})
    rows.append((NOTE if deps > 20 else OK, 'прямых зависимостей: %d' % deps))
    lic = manifest.get('license')
    common(rows, 'npm', 'npm', name, version, [lic] if isinstance(lic, str) else [])
    return rows


def vet_repo(full):
    d = get('https://api.github.com/repos/%s' % full)
    if not d:
        return [(ALARM, 'репозитория %s нет или он закрыт' % full)]
    rows = []
    if d.get('fork'):
        rows.append((ALARM, 'это копия (fork) репозитория %s — сверь, что берёшь оригинал' % d['parent']['full_name']))
    if d.get('archived'):
        rows.append((ALARM, 'репозиторий в архиве — не сопровождается'))
    pushed = age_days(d.get('pushed_at'))
    rows.append((ALARM if pushed is not None and pushed > 365 else OK, 'последняя правка %s дн. назад' % pushed))
    rows.append((NOTE, 'создан %s дн. назад, звёзд %d' % (age_days(d.get('created_at')), d.get('stargazers_count', 0))))
    lic = (d.get('license') or {}).get('spdx_id')
    rows.append((OK, 'лицензия: %s' % lic) if lic and lic != 'NOASSERTION' else (ALARM, 'лицензия не определена'))
    score, weak = scorecard('github.com/%s' % full)
    rows.append((NOTE, 'Scorecard %s из 10%s — подсказка, не приговор' % (
        score if score is not None else 'нет', '; слабые проверки: %s' % ', '.join(weak) if weak else '')))
    return rows


# Подозрительное в инструкциях для агента. Подсветка, а не приговор: скрытую просьбу простыми словами скрипт не
# видит, файл читается целиком.
FILE_PATTERNS = [
    ('сетевой вызов', r'(?i)\b(?:curl|wget|Invoke-WebRequest|iwr|Invoke-RestMethod|nc|ncat)\b|https?://'),
    ('команда оболочки', r'(?i)\b(?:bash\s+-c|sh\s+-c|powershell\s+-|eval\s|exec\s|rm\s+-rf|chmod\s+\+x)'),
    ('закодированный кусок', r'[A-Za-z0-9+/]{60,}={0,2}'),
    ('просьба скрыть или забыть', r'(?i)(?:ignore (?:all |the )?previous|disregard|do not (?:tell|mention|reveal)|'
                                  r'don\'t tell|игнорируй|не говори|не сообщай|забудь (?:все|прежн))'),
    ('чтение секретов', r'(?i)(?:\.env\b|\.ssh|id_rsa|\.aws|credentials|api[_-]?key|token|secret|password)'),
    ('комментарий HTML', r'<!--'),
]
INVISIBLE = re.compile('[​-‏‪-‮⁠-⁤﻿\U000e0000-\U000e007f]')


def vet_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.read().splitlines()
    rows = []
    for n, line in enumerate(lines, 1):
        if INVISIBLE.search(line):
            rows.append((ALARM, 'строка %d: невидимые символы — %s' % (n, repr(INVISIBLE.findall(line)[:5]))))
        for label, rx in FILE_PATTERNS:
            if re.search(rx, line):
                level = ALARM if label in ('просьба скрыть или забыть', 'закодированный кусок') else NOTE
                rows.append((level, 'строка %d: %s — %s' % (n, label, line.strip()[:120])))
    rows.append((NOTE, 'строк %d. Подсветка не заменяет чтение целиком' % len(lines)))
    return rows


def main():
    ap = argparse.ArgumentParser(description='Проверка чужого пакета, репозитория или файла правил агента.')
    ap.add_argument('kind', choices=['pypi', 'npm', 'repo', 'file'])
    ap.add_argument('name', help='имя пакета, владелец/имя репозитория или путь к файлу')
    ap.add_argument('version', nargs='?', help='версия пакета (по умолчанию последняя)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        rows = {'pypi': lambda: vet_pypi(a.name, a.version), 'npm': lambda: vet_npm(a.name, a.version),
                'repo': lambda: vet_repo(a.name), 'file': lambda: vet_file(a.name)}[a.kind]()
    except (Setup, OSError) as e:
        print('Ошибка запуска: %s' % e)
        return 2
    for level, message in rows:
        print('%-8s %s' % (level, message))
    alarms = sum(1 for r in rows if r[0] == ALARM)
    print('\nИтог: тревог %d. Решение — по references/security/vetting.md.' % alarms)
    return 1 if alarms else 0


if __name__ == '__main__':
    sys.exit(main())
