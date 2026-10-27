"""Рабочая копия задачи: заводит её на команде исполнителя и говорит агенту, где работать.

Зовёт хук `model_gate.py` на команде `/<роль> <задача>` после сверки модели: команда остановлена — копия не
заводится. Агенту уходит строка в начало чата: путь, ветка, заведена сейчас или уже была.

Руками — то же самое, если хук не сработал (задачу дали словами, а не командой):
    python worktree.py CB_TASK_123 [папка проекта]

Что делает:
- копии нет, ветки нет — `git worktree add -b <ветка> <путь> <основная>`;
- копии нет, ветка есть (доработка в новом чате) — `git worktree add <путь> <ветка>`;
- копия есть, в том числе по другому пути, — ничего не меняет, печатает последнюю запись журнала ветки и число изменённых файлов: копию,
  возможно, ведёт другой чат.
После заведения копирует файлы из `copy` (настройки вне git, например `.env`), если их нет в копии.

Настройка — `kit.toml`, раздел [worktree]:
    path = "{home}/.kit-worktrees/{repo}/{id}"   # {home}, {repo} — имя папки проекта, {id}, {code}
    copy = [".env"]                              # пути от корня проекта
    roles = ["backend", "frontend", "designer"]  # чьим командам заводить копию
Ветка и основная ветка — из раздела [git].
Код возврата: 0 — копия готова, 1 — завести не вышло, 2 — ошибка запуска.
"""
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

DEFAULTS = {
    'path': '{home}/.kit-worktrees/{repo}/{id}',
    'copy': [],
    'roles': ['backend', 'frontend', 'designer'],
}


def config(root):
    try:
        with open(root / 'kit.toml', 'rb') as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        data = {}
    wt = {**DEFAULTS, **data.get('worktree', {})}
    git = data.get('git', {})
    return wt, git.get('main', 'master'), git.get('task_branch', 'task/{id}')


def git(cwd, *args):
    r = subprocess.run(['git', '-C', str(cwd), *args], capture_output=True, encoding='utf-8', errors='replace',
                       timeout=120)
    return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()


def common_root(root):
    """Корень основной копии: команду могут дать и из чужой рабочей копии."""
    code, out, _ = git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    if code == 0 and out:
        return Path(out).parent
    return root


def paths(root, task_id):
    wt, main, branch_fmt = config(root)
    code = task_id.split('_TASK_')[0]
    fields = dict(home=str(Path.home()), repo=root.name, id=task_id, code=code)
    return Path(wt['path'].format(**fields)), branch_fmt.format(**fields), main, wt


def state_of(path, branch):
    """Текст о копии, которая уже есть: ветка, последняя запись журнала, изменённые файлы."""
    _, current, _ = git(path, 'branch', '--show-current')
    _, last, _ = git(path, 'reflog', '-1', '--date=iso', '--format=%gd: %gs')
    last = last.replace('HEAD@{', '').replace('}:', ':', 1)
    _, dirty, _ = git(path, 'status', '--porcelain')
    changed = len([l for l in dirty.splitlines() if l.strip()])
    lines = ['Рабочая копия уже была: %s.' % path.as_posix()]
    if current != branch:
        lines.append('В ней ветка %s, а не %s — стоп и вопрос владельцу.' % (current or '(без ветки)', branch))
    else:
        lines.append('Ветка %s. Последняя запись журнала ветки — %s. Изменённых файлов: %d.' % (branch, last or 'нет', changed))
        lines.append('Записи последних часов, которых ты не делал, — копию, возможно, ведёт другой чат: стоп и вопрос '
                     'владельцу (process/start.md, правило 2).')
    return current == branch, lines


def checked_out(root, branch):
    """Путь копии, где ветка задачи уже стоит (заведена раньше по другому пути), или None."""
    _, out, _ = git(root, 'worktree', 'list', '--porcelain')
    path = None
    for line in out.splitlines():
        if line.startswith('worktree '):
            path = Path(line[len('worktree '):])
        elif line == 'branch refs/heads/' + branch and path and path.exists():
            return path
    return None


def prepare(root, task_id, role=None):
    """(готово ли, строки для агента). Ничего не печатает."""
    root = common_root(Path(root).resolve())
    path, branch, main, wt = paths(root, task_id)
    if role and role not in wt['roles']:
        return True, []
    if (path / '.git').exists():
        return state_of(path, branch)
    other = checked_out(root, branch)
    if other:
        return state_of(other, branch)
    if path.exists() and any(path.iterdir()):
        return False, ['Папка %s есть, но это не рабочая копия git — завести не вышло, спроси владельца.' % path.as_posix()]
    path.parent.mkdir(parents=True, exist_ok=True)
    has_branch = git(root, 'rev-parse', '--verify', '--quiet', 'refs/heads/' + branch)[0] == 0
    args = ['worktree', 'add', str(path), branch] if has_branch else ['worktree', 'add', '-b', branch, str(path), main]
    code, _, err = git(root, *args)
    if code != 0:
        return False, ['Рабочую копию завести не вышло: git %s — %s' % (' '.join(args[:2]), err.splitlines()[-1] if err else code)]
    copied = []
    for rel in wt['copy']:
        src, dst = root / rel, path / rel
        if src.is_file() and not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)
    _, head, _ = git(path, 'log', '-1', '--format=%h %s')
    how = 'на ветке %s, которая уже была' % branch if has_branch else 'на новой ветке %s от %s' % (branch, main)
    lines = ['Рабочая копия заведена сейчас: %s, %s. Последний коммит: %s.' % (path.as_posix(), how, head)]
    if copied:
        lines.append('Скопированы настройки вне git: %s.' % ', '.join(copied))
    return True, lines


def message(root, task_id, role=None):
    """(готово ли, текст для агента или None, если роли копия не нужна)."""
    ok, lines = prepare(root, task_id, role)
    if not lines:
        return ok, None
    root = common_root(Path(root).resolve())
    path, branch, _, _ = paths(root, task_id)
    path = path if (path / '.git').exists() else (checked_out(root, branch) or path)
    if ok:
        lines.append('Все команды задачи — в этой копии: `cd "%s" && …` или `git -C`. Общая папка проекта — только '
                     'для чтения, её ветку не меняй.' % path.as_posix())
    return ok, ' '.join(lines)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2 or sys.argv[1].startswith('-'):
        print(__doc__)
        return 2
    start = Path(sys.argv[2] if len(sys.argv) > 2 else '.').resolve()
    root = next((f for f in (start, *start.parents) if (f / 'kit.toml').is_file()), None)
    if not root:
        print('нет kit.toml выше папки %s' % start)
        return 2
    ok, text = message(root, sys.argv[1])
    print(text)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
