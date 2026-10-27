"""Браузер тестировщика на локальном стенде: один браузер на всю проверку, команды по одной.

Тестировщик не пишет скрипт на каждую проверку. Тот, кто запускает тестировщика, открывает браузер командой
`start` и входит на стенд; дальше тестировщик подаёт команды: открыть, прочитать текст, нажать, вписать.
Браузер живёт между командами, поэтому вход, открытые формы и состояние страницы сохраняются.

    python stand.py start --base http://127.0.0.1:8100 [--accounts FILE --role РОЛЬ] [--dir ПАПКА]
    python stand.py open /#bot              адрес от --base или полный локальный адрес
    python stand.py text [--find СЛОВА] [--max 4000]
    python stand.py elements [--find СЛОВА]  видимые кнопки, ссылки и поля с номерами
    python stand.py click "Сохранить" [--in "Версия 2"] | click --n 12 [--accept]
    python stand.py fill "Название" "Осенняя акция" | fill --n 7 "текст"
    python stand.py select "Тип" "MAX" | check "Согласен" | press Enter
    python stand.py wait "Сохранено" [--timeout 20]
    python stand.py shot снимок.png
    python stand.py tabs | tab 2 | close-tab   вкладки стенда; новая вкладка после click становится текущей
    python stand.py url | back | stop

Работает только с локальными адресами: localhost, 127.0.0.1, [::1], *.localhost, *.test.
Пароль нигде не печатается: `start` берёт его из файла учёток и вписывает сам.
Файл учёток — строки «роль | логин | пароль».
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
INTERACTIVE = (
    "a[href], button, input:not([type=hidden]), textarea, select, summary, "
    "[role=button], [role=tab], [role=link], [role=menuitem], [role=checkbox], [role=switch], "
    "[contenteditable=true]"
)


def fail(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def is_local(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in ("localhost", "127.0.0.1", "::1") or host.endswith((".localhost", ".test"))


def state_dir(args) -> Path:
    return Path(args.dir or os.environ.get("STAND_DIR") or ".stand").resolve()


def load_state(args) -> dict:
    path = state_dir(args) / "state.json"
    if not path.exists():
        fail("Браузер не открыт. Его открывает тот, кто запускает проверку: stand.py start --base <адрес>")
    return json.loads(path.read_text(encoding="utf-8"))


def browser_path() -> str:
    for candidate in EDGE_PATHS + CHROME_PATHS:
        if Path(candidate).exists():
            return candidate
    fail("Не нашёл Edge или Chrome")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def connect(state: dict):
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{state['port']}", timeout=10000)
    except Exception:
        pw.stop()
        fail("Браузер не отвечает. Откройте заново: stand.py start")
    context = browser.contexts[0]
    pages = local_pages(context)
    chosen = [p for p in pages if tab_id(p) == state.get("tab")]
    page = chosen[0] if chosen else (pages[-1] if pages else context.new_page())
    page.set_default_timeout(15000)
    page.bring_to_front()
    return pw, browser, page


def local_pages(context) -> list:
    """Вкладки стенда. Чужие адреса тестировщику не показываются, служебные страницы браузера — тоже."""
    return [p for p in context.pages if p.url == "about:blank" or is_local(p.url)]


def tab_id(page) -> str:
    session = page.context.new_cdp_session(page)
    try:
        return session.send("Target.getTargetInfo")["targetInfo"]["targetId"]
    finally:
        session.detach()


SIDE_SCROLL_JS = """() => {
  // Прокручиваться вбок может не страница, а область внутри неё: проверяем все области с прокруткой
  const boxes = [document.scrollingElement, ...[...document.querySelectorAll('body *')].filter(e => {
    const o = getComputedStyle(e).overflowX;
    return (o === 'auto' || o === 'scroll') && e.clientWidth;
  })];
  const out = [];
  for (const box of boxes) {
    if (box.scrollWidth <= box.clientWidth + 1) continue;
    const edge = box === document.scrollingElement ? box.clientWidth : box.getBoundingClientRect().left + box.clientWidth;
    const wide = [...box.querySelectorAll('*')].filter(e => {
      const r = e.getBoundingClientRect();
      const st = getComputedStyle(e);
      // Текст может вылезать из коробки элемента, а сама коробка остаётся в границах
      const spill = e.scrollWidth > e.clientWidth + 1 && st.overflowX === 'visible' && e.clientWidth;
      return r.width && (r.right > edge + 1 || spill) && st.position !== 'fixed';
    });
    const deepest = wide.filter(e => !wide.some(c => c !== e && e.contains(c))).slice(0, 3)
      .map(e => '<' + e.tagName.toLowerCase() + '> «' + (e.innerText || e.value || '').trim().slice(0, 40) + '»');
    out.push([box.scrollWidth, box.clientWidth, deepest]);
  }
  return out;
}"""


def side_scroll(page) -> str:
    """Есть ли прокрутка вбок у страницы или у области внутри неё: на снимке её легко не заметить."""
    found = page.evaluate(SIDE_SCROLL_JS)
    if not found:
        return "Прокрутки вбок нет"
    scroll, client, wide = found[0]
    return (f"Прокрутка вбок есть: содержимое {scroll} px при ширине области {client} px. "
            "За край выходят: " + ("; ".join(wide) or "не определить"))


SCROLL_JS = """(saved) => {
  // Путь до области прокрутки: тег и номер среди соседей от body
  const path = e => { const out = []; for (; e && e !== document.body; e = e.parentElement)
    out.unshift([...e.parentElement.children].indexOf(e)); return out.join('/'); };
  const find = key => key.split('/').reduce((e, i) => e && e.children[+i], document.body);
  if (saved) { for (const [key, top] of saved) { const e = key === '' ? document.scrollingElement : find(key);
    if (e) e.scrollTo({top, behavior: 'instant'}); } return null; }
  return [document.scrollingElement, ...document.querySelectorAll('body *')]
    .filter(e => e.scrollHeight > e.clientHeight + 1)
    .map(e => [e === document.scrollingElement ? '' : path(e), e.scrollTop]);
}"""


def fit_width(page, state: dict) -> None:
    # Подмена ширины живёт, пока подключён скрипт. Новая подмена — это смена размера окна, и страница может
    # сама прыгнуть к своему разделу. Поэтому прокрутку прошлой команды возвращаем на место
    if state.get("width"):
        page.set_viewport_size({"width": state["width"], "height": 900})
        if state.get("scroll") and state.get("scroll_url") == page.url:
            page.evaluate(SCROLL_JS, state["scroll"])


def save_tab(args, state: dict, page) -> None:
    state["tab"] = tab_id(page)
    try:
        state["scroll"], state["scroll_url"] = page.evaluate(SCROLL_JS, None), page.url
    except Exception:
        state["scroll"] = None
    (state_dir(args) / "state.json").write_text(json.dumps(state), encoding="utf-8")


def credentials(accounts: str, role: str) -> tuple[str, str]:
    for line in Path(accounts).read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3 and parts[0] == role:
            return parts[1], parts[2]
    fail(f"В файле учёток нет роли «{role}»")


def cmd_start(args) -> None:
    if not is_local(args.base):
        fail("Только локальный стенд: localhost, 127.0.0.1, *.localhost, *.test")
    folder = state_dir(args)
    folder.mkdir(parents=True, exist_ok=True)
    port = free_port()
    profile = tempfile.mkdtemp(prefix="stand-profile-")
    flags = [
        browser_path(),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile}",
        "--no-first-run",
        "--no-default-browser-check",
        # Чистый браузер: без входа в учётную запись, синхронизации и расширений с машины человека
        "--inprivate",
        "--disable-sync",
        "--disable-extensions",
        "--disable-component-extensions-with-background-pages",
        "--disable-background-networking",
        "--disable-default-apps",
        "--no-service-autorun",
        "--password-store=basic",
        "--lang=ru-RU",
        "--window-size=1400,900",
    ]
    if not args.show:
        flags.append("--headless=new")
    proc = subprocess.Popen(flags + ["about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    state = {"port": port, "base": args.base.rstrip("/"), "pid": proc.pid, "profile": profile}
    for _ in range(40):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
            break
        except OSError:
            time.sleep(0.25)
    (folder / "state.json").write_text(json.dumps(state), encoding="utf-8")
    pw, browser, page = connect(state)
    try:
        page.goto(state["base"] + (args.login_path or "/"))
        if args.accounts:
            login, password = credentials(args.accounts, args.role)
            user_field = page.locator(args.user_field or "input[type=email]:visible, input[type=text]:visible").first
            user_field.fill(login)
            page.locator(args.pass_field or "input[type=password]:visible").first.fill(password)
            if args.submit:
                page.locator(args.submit).first.click()
            else:
                page.keyboard.press("Enter")
            page.wait_for_timeout(1500)
            if page.locator("input[type=password]:visible").count():
                fail("Вход не прошёл: на странице всё ещё поле пароля")
        save_tab(args, state, page)
        print(f"Браузер открыт, страница: {page.url}")
        print(f"Папка состояния: {folder}")
    finally:
        pw.stop()


def target_url(state: dict, where: str) -> str:
    # Git Bash на Windows превращает «/#bot» в «C:/Program Files/Git/#bot» — возвращаем как было
    mangled = re.match(r"^[A-Za-z]:[\\/].*?[\\/]Git[\\/](.*)$", where)
    if mangled:
        where = "/" + mangled.group(1)
    url = where if re.match(r"^[a-z]+://", where) else urljoin(state["base"] + "/", where.lstrip("/"))
    if where.startswith("/#") or where.startswith("#"):
        url = state["base"] + "/" + where.lstrip("/")
    if not is_local(url):
        fail("Адрес не локальный — открывать нельзя")
    return url


def visible_text(page) -> str:
    text = page.evaluate("() => document.body ? document.body.innerText : ''")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    out, blank = [], False
    for line in lines:
        if not line:
            if not blank:
                out.append("")
            blank = True
            continue
        out.append(line)
        blank = False
    return "\n".join(out).strip()


def print_text(page, find: str | None, limit: int) -> None:
    text = visible_text(page)
    if find:
        lines = text.splitlines()
        hits = [i for i, line in enumerate(lines) if find.lower() in line.lower()]
        if not hits:
            print(f"На странице нет «{find}»")
            return
        keep = sorted({j for i in hits for j in range(max(0, i - 3), min(len(lines), i + 4))})
        chunks, prev = [], None
        for j in keep:
            if prev is not None and j != prev + 1:
                chunks.append("…")
            chunks.append(lines[j])
            prev = j
        text = "\n".join(chunks)
    if len(text) > limit:
        text = text[:limit] + f"\n… обрезано, всего {len(text)} знаков: уточните --find"
    print(text)


LIST_JS = """
([selector, find]) => {
  const seen = [];
  let n = 0;
  document.querySelectorAll('[data-qa-n]').forEach(e => e.removeAttribute('data-qa-n'));
  for (const el of document.querySelectorAll(selector)) {
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    if (!r.width || !r.height || st.visibility === 'hidden' || st.display === 'none') continue;
    n += 1;
    el.setAttribute('data-qa-n', String(n));
    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute('type') || '').toLowerCase();
    let kind = el.getAttribute('role') || tag;
    if (tag === 'a') kind = 'ссылка';
    else if (tag === 'button' || kind === 'button') kind = 'кнопка';
    else if (tag === 'select') kind = 'список';
    else if (tag === 'textarea') kind = 'поле';
    else if (tag === 'input') kind = (type === 'checkbox' ? 'галочка' : type === 'radio' ? 'переключатель' : 'поле');
    else if (kind === 'tab') kind = 'вкладка';
    const shown = tag === 'select' ? '' : (el.innerText || '').trim();
    let label = shown;
    if (!label && el.labels && el.labels.length) label = el.labels[0].innerText.trim();
    const aria = el.getAttribute('aria-label') || el.getAttribute('title') || '';
    if (!label) label = aria || el.getAttribute('placeholder') || el.getAttribute('name') || '';
    label = label.replace(/\\s+/g, ' ').slice(0, 80);
    let extra = '';
    // Подпись для чтения с экрана — не то, что видно глазами: говорим об этом прямо
    if (shown && aria && shown !== aria) extra += ` (подпись для чтения с экрана «${aria}»)`;
    if (!shown && aria && !['input', 'textarea', 'select'].includes(tag)) extra += ' (на экране значок без текста)';
    const ph = el.getAttribute('placeholder');
    if (ph && ph !== label) extra += ` (подсказка в поле «${ph}»)`;
    if (tag === 'input' || tag === 'textarea') {
      if (type === 'checkbox' || type === 'radio') extra = el.checked ? ' [отмечено]' : ' [не отмечено]';
      else if (el.value) extra = ` = «${String(el.value).slice(0, 60)}»`;
    }
    if (tag === 'select' && el.selectedOptions.length) extra = ` = «${el.selectedOptions[0].text}»`;
    if (el.disabled) extra += ' [недоступно]';
    seen.push({el, n, kind, label, extra, ctx: ''});
  }
  const count = {};
  seen.forEach(x => { count[x.kind + x.label] = (count[x.kind + x.label] || 0) + 1; });
  // У повторяющихся элементов подпись — первая строка самого широкого блока, где такой элемент один
  for (const x of seen) {
    if (count[x.kind + x.label] < 2) continue;
    const twins = seen.filter(y => y.kind === x.kind && y.label === x.label).map(y => y.el);
    let row = x.el;
    for (let up = x.el.parentElement; up; up = up.parentElement) {
      if (twins.filter(t => up.contains(t)).length > 1) break;
      row = up;
    }
    const first = (row.innerText || '').split('\\n').map(t => t.trim()).find(t => t && t !== x.label);
    x.ctx = (first || '').replace(/\\s+/g, ' ').slice(0, 50);
  }
  return seen
    .filter(x => !find || (x.label + x.extra + x.ctx).toLowerCase().includes(find.toLowerCase()))
    .map(x => `[${x.n}] ${x.kind} «${x.label}»${x.extra}` + (count[x.kind + x.label] > 1 && x.ctx ? ` — в «${x.ctx}»` : ''));
}
"""


def numbered(page, n: int):
    loc = page.locator(f'[data-qa-n="{n}"]')
    if not loc.count():
        fail(f"Нет элемента [{n}]: страница изменилась. Сначала stand.py elements")
    return loc.first


BLOCKS = "tr, li, [role=row], article, section, fieldset, form, dialog, div"


SCOPE_JS = """
(within) => {
  document.querySelectorAll('[data-qa-scope]').forEach(e => e.removeAttribute('data-qa-scope'));
  const visible = el => { const r = el.getBoundingClientRect(); return r.width && r.height; };
  const hits = [...document.body.querySelectorAll('*')].filter(el =>
    visible(el) && (el.innerText || '').includes(within) &&
    ![...el.children].some(ch => (ch.innerText || '').includes(within)));
  // От надписи вверх до первого блока с кнопками или ссылками: это строка или карточка
  let rows = [];
  for (const hit of hits) {
    let row = hit;
    for (let up = hit; up && up !== document.body; up = up.parentElement) {
      row = up;
      if (up.querySelector('a[href], button, input, select, textarea, [role=button]')) break;
    }
    if (!rows.includes(row)) rows.push(row);
  }
  rows = rows.filter(row => !rows.some(other => other !== row && row.contains(other)));
  rows.forEach((row, i) => row.setAttribute('data-qa-scope', String(i + 1)));
  return rows.map(row => (row.innerText || '').split('\\n').map(t => t.trim()).filter(Boolean).slice(0, 2).join(' · ').slice(0, 80));
}
"""


def scope(page, within: str | None):
    """Строка или карточка страницы с текстом within. Таких несколько — отказ со списком."""
    if not within:
        return page
    found = page.evaluate(SCOPE_JS, within)
    if not found:
        fail(f"На странице нет блока с текстом «{within}»")
    if len(found) > 1:
        rows = "\n".join(f"  {i}. {text}" for i, text in enumerate(found, 1))
        fail(f"Блоков с текстом «{within}» несколько ({len(found)}):\n{rows}\nУточните --in или нажмите по номеру: elements и --n")
    return page.locator('[data-qa-scope="1"]')


def by_text(page, text: str, within: str | None = None):
    root = scope(page, within)
    exact = re.compile(r"^\s*" + re.escape(text) + r"\s*$", re.I)
    for loc in (
        root.get_by_role("button", name=exact),
        root.get_by_role("link", name=exact),
        root.get_by_role("tab", name=exact),
        root.get_by_role("menuitem", name=exact),
        root.locator(INTERACTIVE).filter(has_text=exact),
        root.locator(INTERACTIVE).filter(has_text=text),
        root.get_by_text(text, exact=True),
    ):
        visible = loc.locator("visible=true")
        if visible.count():
            if visible.count() > 1:
                # Нажать первый наугад — значит нажать не то: в пробах так открывали чужую строку и чужой раздел
                items = page.evaluate(LIST_JS, [INTERACTIVE, text])
                fail(f"Элементов «{text}» несколько ({visible.count()}) — не нажимаю. Выберите номер: click --n N "
                     "или сузьте блоком: --in \"текст строки\"\n" + "\n".join(items[:15]))
            return visible.first
    fail(f"Не нашёл видимого элемента «{text}». Посмотрите список: stand.py elements --find \"{text[:20]}\"")


FIELD_JS = """
([label, scoped]) => {
  document.querySelectorAll('[data-qa-field]').forEach(e => e.removeAttribute('data-qa-field'));
  const root = scoped ? document.querySelector('[data-qa-scope="1"]') : document;
  const norm = t => (t || '').replace(/\\s+/g, ' ').trim().toLowerCase();
  const shown = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const names = el => {
    const out = [];
    if (el.labels) for (const l of el.labels) out.push(l.innerText);
    out.push(el.getAttribute('aria-label'), el.getAttribute('placeholder'), el.getAttribute('title'));
    const by = el.getAttribute('aria-labelledby');
    if (by) by.split(/\\s+/).forEach(id => { const t = document.getElementById(id); if (t) out.push(t.innerText); });
    return out.map(norm).filter(Boolean);
  };
  // Поле видно само или видна его подпись: так рисуют свои галочки и переключатели
  const all = [...root.querySelectorAll('input:not([type=hidden]), select, textarea, [role=checkbox], [role=switch], [contenteditable=true]')]
    .filter(el => shown(el) || [...(el.labels || [])].some(shown));
  const want = norm(label);
  let found = all.filter(el => names(el).includes(want));
  if (!found.length) found = all.filter(el => names(el).some(n => n.includes(want)));
  found.forEach((el, i) => el.setAttribute('data-qa-field', String(i + 1)));
  return found.length;
}
"""


def field(page, label: str, within: str | None = None):
    scope(page, within)
    count = page.evaluate(FIELD_JS, [label, bool(within)])
    if not count:
        fail(f"Не нашёл поле «{label}». Посмотрите список: stand.py elements")
    if count > 1:
        print(f"Полей «{label}» несколько ({count}), взято первое. Точнее — elements и --n")
    return page.locator('[data-qa-field="1"]')


def is_on(el) -> bool:
    return el.evaluate(
        "e => e.matches('input') ? e.checked : e.getAttribute('aria-checked') === 'true'"
    )


def settle(page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass
    page.wait_for_timeout(300)


def run(args) -> None:
    state = load_state(args)
    if args.cmd == "stop":
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(state["pid"]), "/T", "/F"], capture_output=True)
            else:
                os.kill(state["pid"], 15)
        except Exception:
            pass
        (state_dir(args) / "state.json").unlink(missing_ok=True)
        print("Браузер закрыт")
        return
    pw, browser, page = connect(state)
    fit_width(page, state)
    dialogs: list[str] = []

    def on_dialog(d):
        dialogs.append(d.message)
        d.accept() if getattr(args, "accept", False) else d.dismiss()

    page.on("dialog", on_dialog)
    try:
        if args.cmd == "open":
            want = target_url(state, args.where)
            if args.new:
                page = page.context.new_page()
                page.on("dialog", on_dialog)
            page.goto(want)
            settle(page)
            if page.url.rstrip("/") != want.rstrip("/"):
                print(f"Страница не ушла на {want}, осталась {page.url}: смотрите текст — может быть, правки не сохранены")
            else:
                print(f"Открыто: {page.url}")
            print_text(page, None, 1500)
        elif args.cmd == "text":
            print_text(page, args.find, args.max)
        elif args.cmd == "elements":
            items = page.evaluate(LIST_JS, [INTERACTIVE, args.find or ""])
            print("\n".join(items[: args.max]) if items else "Видимых элементов нет")
            if len(items) > args.max:
                print(f"… ещё {len(items) - args.max}: уточните --find")
        elif args.cmd == "click":
            el = numbered(page, args.n) if args.n else by_text(page, args.text, args.within)
            before = {tab_id(p) for p in page.context.pages}
            try:
                el.click(timeout=5000)
            except Exception as e:
                cover = re.search(r"<([^>]{1,120})> intercepts pointer events", str(e))
                if cover:
                    fail(f"Нажатие не подтверждено: поверх элемента лежит <{cover.group(1)}>. Прочитайте экран (text): "
                         "меню могло открыться. Если не открылось — закройте меню или окно (press Escape)")
                fail("Не нажать за 5 с: элемент не готов. Посмотрите экран: stand.py text или shot")
            settle(page)
            page.wait_for_timeout(700)
            fresh = [p for p in page.context.pages if tab_id(p) not in before]
            for new in fresh:
                if is_local(new.url) or new.url == "about:blank":
                    new.wait_for_load_state()
                    page = new
                    page.bring_to_front()
                    print(f"Открылась новая вкладка, работаю в ней: {page.url}. Вернуться — stand.py tabs и tab N")
                else:
                    new.close()
                    print("Открылась вкладка с нелокальным адресом — закрыта")
            if not fresh:
                print(f"Нажато. Страница: {page.url}")
        elif args.cmd == "tabs":
            for i, p in enumerate(local_pages(page.context), 1):
                mark = " ← текущая" if p == page else ""
                print(f"[{i}] {p.url}{mark}")
        elif args.cmd == "tab":
            pages = local_pages(page.context)
            if not 1 <= args.n <= len(pages):
                fail(f"Вкладки [{args.n}] нет. Список: stand.py tabs")
            page = pages[args.n - 1]
            page.bring_to_front()
            print(f"Текущая вкладка: {page.url}")
        elif args.cmd == "close-tab":
            pages = local_pages(page.context)
            if len(pages) < 2:
                fail("Это последняя вкладка — не закрываю")
            page.close()
            page = [p for p in local_pages(page.context)][-1]
            page.bring_to_front()
            print(f"Вкладка закрыта. Текущая: {page.url}")
        elif args.cmd == "fill":
            el = numbered(page, args.n) if args.n else field(page, args.label, getattr(args, "within", None))
            try:
                el.fill(args.value * args.repeat)
            except Exception as e:
                if "type=number" in str(e) or "Cannot type text" in str(e):
                    print(f"Поле только для чисел: браузер не даёт вписать «{args.value}». Это поведение поля, а не сбой")
                    sys.exit(1)
                raise
            print("Вписано: " + repr(el.input_value()) if el.evaluate("e => 'value' in e") else "Вписано")
        elif args.cmd == "select":
            el = numbered(page, args.n) if args.n else field(page, args.label, getattr(args, "within", None))
            options = el.evaluate("e => [...e.options].map(o => o.text.trim())")
            if args.value not in options:
                fail(f"В списке нет «{args.value}». Пункты: " + "; ".join(options))
            el.select_option(label=args.value)
            settle(page)
            page.wait_for_timeout(500)
            # Список может перерисоваться после выбора соседнего поля — читаем, что стоит сейчас
            now = el.evaluate("e => e.selectedOptions.length ? e.selectedOptions[0].text.trim() : ''")
            if now != args.value:
                print(f"Не получилось: в списке стоит «{now}». Пункты: " + "; ".join(options))
                sys.exit(1)
            print(f"Выбрано: «{now}»")
        elif args.cmd == "check":
            el = numbered(page, args.n) if args.n else field(page, args.label)
            want = not args.off
            if is_on(el) != want:
                target = el
                if not el.is_visible():
                    target = el.evaluate_handle("e => (e.labels && e.labels[0]) || e")
                target.click()
                page.wait_for_timeout(300)
            # Отчитываемся тем, что стоит на странице, а не тем, что пытались сделать.
            # После клика страница может перерисовать галочку — тогда ищем её заново
            try:
                now = is_on(el)
            except Exception:
                el = numbered(page, args.n) if args.n else field(page, args.label)
                now = is_on(el)
            if now != want:
                print("Не получилось: галочка " + ("осталась снятой" if want else "осталась отмеченной"))
                sys.exit(1)
            print("Отмечено" if want else "Снято")
        elif args.cmd == "press":
            page.keyboard.press(args.key)
            settle(page)
            print("Нажата клавиша")
        elif args.cmd == "wait":
            try:
                page.wait_for_function(
                    "t => document.body && document.body.innerText.includes(t)",
                    arg=args.text,
                    timeout=args.timeout * 1000,
                )
                print(f"Появилось: «{args.text}»")
            except Exception:
                print(f"За {args.timeout} с не появилось: «{args.text}»")
                sys.exit(1)
        elif args.cmd == "shot":
            page.screenshot(path=args.file, full_page=args.full)
            print(f"Снимок: {Path(args.file).resolve()}")
            print(side_scroll(page))
        elif args.cmd == "url":
            print(page.url)
        elif args.cmd == "back":
            page.go_back()
            settle(page)
            print(f"Назад: {page.url}")
        elif args.cmd == "width":
            # Ширину помним в состоянии и ставим при каждом подключении: подмена живёт, пока подключён скрипт
            state["width"] = args.px if args.px else None
            fit_width(page, state)
            print(f"Ширина страницы: {page.evaluate('() => window.innerWidth')} px")
            print(side_scroll(page))
        elif args.cmd == "scroll":
            # Клавиши End и PageDown листают, только если фокус в прокручиваемой области: листаем сами
            if args.text:
                shown = [e for e in page.get_by_text(args.text).all() if e.is_visible()]
                if not shown:
                    fail(f"На странице нет видимого текста «{args.text}». Раздел мог быть свёрнут: откройте его")
                el = shown[0]
                el.scroll_into_view_if_needed(timeout=5000)
                print(f"Показан «{args.text}»")
            else:
                page.evaluate("""(where) => { for (const e of [document.scrollingElement, ...document.querySelectorAll('body *')]) {
                    if (e.scrollHeight > e.clientHeight + 1) e.scrollTo({top: where === 'top' ? 0 : e.scrollHeight, behavior: 'instant'}); } }""",
                              "top" if args.top else "end")
                page.wait_for_timeout(300)
                print("Страница пролистана " + ("в начало" if args.top else "до конца"))
        elif args.cmd == "reload":
            page.reload()
            settle(page)
            print(f"Страница загружена заново: {page.url}")
        save_tab(args, state, page)
        if dialogs:
            verb = "принято" if getattr(args, "accept", False) else "отклонено"
            for message in dialogs:
                print(f"Окно подтверждения «{message}» — {verb}")
    finally:
        pw.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Браузер тестировщика на локальном стенде")
    parser.add_argument("--dir", help="папка состояния браузера (по умолчанию .stand или STAND_DIR)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start")
    p.add_argument("--base", required=True)
    p.add_argument("--accounts")
    p.add_argument("--role", default="суперадмин")
    p.add_argument("--login-path", default="/login")
    p.add_argument("--user-field")
    p.add_argument("--pass-field")
    p.add_argument("--submit")
    p.add_argument("--show", action="store_true", help="показать окно браузера")

    sub.add_parser("stop")
    sub.add_parser("url")
    sub.add_parser("back")
    sub.add_parser("reload")
    p = sub.add_parser("scroll")
    p.add_argument("text", nargs="?", help="пролистать до элемента с этим текстом; без текста — до конца")
    p.add_argument("--top", action="store_true", help="в начало")
    p = sub.add_parser("width")
    p.add_argument("px", type=int)
    sub.add_parser("tabs")
    sub.add_parser("close-tab")
    p = sub.add_parser("tab")
    p.add_argument("n", type=int)
    p = sub.add_parser("open")
    p.add_argument("where")
    p.add_argument("--new", action="store_true", help="открыть в новой вкладке")
    p = sub.add_parser("text")
    p.add_argument("--find")
    p.add_argument("--max", type=int, default=4000)
    p = sub.add_parser("elements")
    p.add_argument("--find")
    p.add_argument("--max", type=int, default=80)
    p = sub.add_parser("click")
    p.add_argument("--in", dest="within", help="искать внутри блока с этим текстом")
    p.add_argument("text", nargs="?")
    p.add_argument("--n", type=int)
    p.add_argument("--accept", action="store_true", help="принять окно подтверждения")
    p = sub.add_parser("fill")
    p.add_argument("--in", dest="within", help="искать внутри блока с этим текстом")
    p.add_argument("label", nargs="?")
    p.add_argument("value")
    p.add_argument("--n", type=int)
    p.add_argument("--repeat", type=int, default=1, help="повторить значение N раз: длинный ввод без скрипта")
    p = sub.add_parser("select")
    p.add_argument("label", nargs="?")
    p.add_argument("value")
    p.add_argument("--n", type=int)
    p = sub.add_parser("check")
    p.add_argument("label", nargs="?")
    p.add_argument("--n", type=int)
    p.add_argument("--off", action="store_true")
    p = sub.add_parser("press")
    p.add_argument("key")
    p = sub.add_parser("wait")
    p.add_argument("text")
    p.add_argument("--timeout", type=int, default=20)
    p = sub.add_parser("shot")
    p.add_argument("file")
    p.add_argument("--full", action="store_true")

    args = parser.parse_args()
    if args.cmd in ("click",) and not (args.text or args.n):
        fail("Укажите текст элемента или --n")
    if args.cmd == "fill" and not (args.label or args.n):
        fail("Укажите поле или --n")
    if args.cmd == "start":
        cmd_start(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
