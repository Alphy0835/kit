"""Модель чата против поля «Модель» задания.

Хуки плагина. Сменить модель чата хук не может: Claude Code даёт хукам только запомнить модель и остановить
команду. Поэтому скрипт помнит модель каждого чата и на команде исполнителя `/<роль> <задача>` сверяет её с полем
«Модель» задания. Не совпало — команда не уходит агенту, владелец видит, какую модель выбрать. Отправил команду
ещё раз, не переключив, — значит, выбрал нарочно: второй раз пропускает. Смену модели посреди чата не трогает:
проверка идёт только на команде исполнителя.

Запуск хуком (на входе JSON события):
    python model_gate.py --hook
        SessionStart      — запоминает `model`, если Claude Code его прислал (в 2.1.303 не присылает);
        PostModelSwitch   — запоминает `to_model`;
        UserPromptExpansion — сверка на команде исполнителя; сошлась — рабочая копия задачи (`worktree.py`).
Модель чата: запомненная смена модели в том же процессе Claude Code, иначе флаг `--model` процесса — с ним
приложение запускает каждый чат.
Запуск руками — что скажет проверка:
    python model_gate.py <задача> <модель чата> [папка проекта]

Модель чата неизвестна или в задании не названа — пропускает молча: остаётся правило 1 `process/start.md`.
Код возврата всегда 0: сбой хука не должен мешать чату.
"""
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROLES = ('backend', 'frontend', 'qa', 'security', 'designer')
FAMILIES = {
    'haiku': ('haiku', 'хайку'),
    'sonnet': ('sonnet', 'сонет', 'соннет'),
    'opus': ('opus', 'опус'),
    'fable': ('fable', 'фейбл'),
}
NAMES = {'haiku': 'Haiku', 'sonnet': 'Sonnet', 'opus': 'Opus', 'fable': 'Fable'}
TASK_RE = re.compile(r'\b[A-Z][A-Z0-9]*_TASK_\d+\b')


def family(text):
    """Семейство модели по имени или строке поля; None, если не названо или названо два."""
    low = (text or '').lower()
    found = [f for f, words in FAMILIES.items() if any(w in low for w in words)]
    return found[0] if len(found) == 1 else None


def find_root(start):
    path = Path(start).resolve()
    for folder in (path, *path.parents):
        if (folder / 'kit.toml').is_file():
            return folder
    return None


def task_model(root, task_id):
    """Семейство из строки «| Модель | … |» задания или None."""
    fmt = 'team/tasks/{code}/{id}.md'
    try:
        with open(root / 'kit.toml', 'rb') as f:
            fmt = tomllib.load(f).get('files', {}).get('task', fmt)
        text = (root / fmt.format(id=task_id, code=task_id.split('_TASK_')[0])).read_text(encoding='utf-8')
    except (OSError, tomllib.TOMLDecodeError, KeyError, ValueError):
        return None
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 2 and cells[0].strip('*') == 'Модель':
            # До тире — модель, после — причина: в причине может стоять имя другой модели.
            return family(re.split(r'\s[—–-]\s', cells[1], maxsplit=1)[0])
    return None


MODEL_FLAG_RE = re.compile(r'--model[= ]"?([^\s"]+)')


def claude_process():
    """(pid, флаг --model) ближайшего предка claude; (None, None), если не нашёлся."""
    if os.name == 'nt':
        script = ('$p = Get-CimInstance Win32_Process -Filter "ProcessId=%d"; '
                  'for ($i = 0; $i -lt 8 -and $p; $i++) { "{0}`t{1}`t{2}" -f $p.ProcessId, $p.Name, $p.CommandLine; '
                  '$p = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $p.ParentProcessId) }' % os.getpid())
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', script]
    else:
        cmd = ['sh', '-c', 'p=%d; i=0; while [ "$p" -gt 1 ] && [ $i -lt 8 ]; do '
               'printf "%%s\\t%%s\\t%%s\\n" "$p" "$(ps -o comm= -p $p)" "$(ps -o args= -p $p)"; '
               'p=$(ps -o ppid= -p $p | tr -d " "); i=$((i+1)); done' % os.getpid()]
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=15, encoding='utf-8', errors='replace').stdout
    except (OSError, subprocess.SubprocessError):
        return None, None
    for line in out.splitlines():
        pid, name, args = (line.split('\t') + ['', ''])[:3]
        if os.path.basename(name).lower() in ('claude.exe', 'claude'):
            match = MODEL_FLAG_RE.search(args)
            return pid, match.group(1) if match else None
    return None, None


def state_dir():
    base = os.environ.get('CLAUDE_PLUGIN_DATA') or Path.home() / '.claude' / 'kit'
    path = Path(base) / 'model-gate'
    path.mkdir(parents=True, exist_ok=True)
    return path


def load(session):
    try:
        return json.loads((state_dir() / ('%s.json' % session)).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def save(session, data):
    (state_dir() / ('%s.json' % session)).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def verdict(want, have, task_id):
    """Текст для владельца или None, если модели совпали."""
    if not want or not have or want == have:
        return None
    return ('В задании %s стоит %s, чат работает на %s. Выбери %s в меню модели и отправь команду снова. '
            'Нарочно оставляешь %s — отправь команду ещё раз, второй раз пропущу.'
            % (task_id, NAMES[want], NAMES[have], NAMES[want], NAMES[have]))


def on_expansion(event):
    name = (event.get('command_name') or '').split(':')[-1]
    match = TASK_RE.search(event.get('command_args') or '')
    if name not in ROLES or not match:
        return None
    root = find_root(event.get('cwd') or '.')
    if not root:
        return None
    task_id = match.group(0)
    session = event.get('session_id') or 'unknown'
    want = task_model(root, task_id)
    if not want:
        return None
    data = load(session)
    pid, flag = claude_process()
    # Запомненная смена модели верна только для того же процесса: приложение перезапускает чат с новым флагом.
    model = data.get('model') if data.get('pid') == pid else flag
    text = verdict(want, family(model), task_id)
    if not text:
        return None
    key = '%s:%s' % (task_id, model)
    if key in data.get('warned', []):
        return None
    data.setdefault('warned', []).append(key)
    save(session, data)
    return {'decision': 'block', 'reason': text}


def hook():
    # Байты и utf-8 явно: в Windows поток по умолчанию в cp1251, а путь проекта русский.
    event = json.loads(sys.stdin.buffer.read().decode('utf-8'))
    kind = event.get('hook_event_name')
    session = event.get('session_id') or 'unknown'
    if kind in ('SessionStart', 'PostModelSwitch'):
        model = event.get('model') if kind == 'SessionStart' else event.get('to_model')
        # Вне проекта набора не пишем: плагин стоит на все папки, файлы копились бы от каждого чата.
        if model and find_root(event.get('cwd') or '.'):
            data = load(session)
            data['model'] = model
            data['pid'] = claude_process()[0]
            save(session, data)
        return
    if kind == 'UserPromptExpansion':
        out = on_expansion(event) or prepare_worktree(event)
        if out:
            sys.stdout.write(json.dumps(out, ensure_ascii=True))


def prepare_worktree(event):
    """Модель сошлась — заводим рабочую копию задачи и говорим агенту, где она (`worktree.py`)."""
    name = (event.get('command_name') or '').split(':')[-1]
    match = TASK_RE.search(event.get('command_args') or '')
    root = find_root(event.get('cwd') or '.')
    if name not in ROLES or not match or not root:
        return None
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import worktree
    _, text = worktree.message(root, match.group(0), name)
    if not text:
        return None
    return {'hookSpecificOutput': {'hookEventName': 'UserPromptExpansion', 'additionalContext': text}}


def main():
    if '--hook' in sys.argv:
        try:
            hook()
        except Exception:  # хук не ломает чат ни при какой поломке
            pass
        return 0
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        print(__doc__)
        return 0
    root = find_root(sys.argv[3] if len(sys.argv) > 3 else '.')
    if not root:
        print('нет kit.toml выше папки')
        return 0
    want = task_model(root, sys.argv[1])
    print(verdict(want, family(sys.argv[2]), sys.argv[1]) or 'совпадает или нечего сверять (в задании: %s)' % want)
    return 0


if __name__ == '__main__':
    sys.exit(main())
