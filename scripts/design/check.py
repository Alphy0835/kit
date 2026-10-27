"""Проверка выгрузки макетов: ширины кадров, цвета и шрифты вне токенов, контраст текста, незаполненные шаблоны.

Запуск: python check.py <папка выгрузки> --widths 375,1440 [--tokens <файл токенов>]

Папка — эталон с холста: макеты `*.html`, токены `*.css` с переменными `--имя: значение`, раскладка `canvas.json`
и снимки. Стоп — нет кадра нужной ширины. Внимание — цвет или шрифт вне токенов, низкий контраст, кадр чужой
ширины, макет без снимка: их смотрит человек, скрипт видит не всё (цвет из картинки, фон из соседнего слоя).
Текст с привязкой данных `{{…}}` и цвет недоступного элемента (токен с `disabled` в имени) в контраст не идут:
значение подставится позже, недоступное WCAG из нормы исключает.
"""
import argparse
import html.parser
import json
import pathlib
import re
import struct
import sys

OK, WARN, STOP = 'ОК', 'ВНИМАНИЕ', 'СТОП'
HEX = re.compile(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
RGB = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)')
VAR = re.compile(r'var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


def norm_hex(h):
    h = h.lstrip('#').upper()
    return '#' + (''.join(c * 2 for c in h) if len(h) == 3 else h)


def load_tokens(files):
    tokens = {}
    for f in files:
        for name, value in re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', f.read_text(encoding='utf-8')):
            tokens[name] = value.strip()
    return tokens


def resolve(value, tokens, depth=0):
    while depth < 10 and VAR.search(value):
        value = VAR.sub(lambda m: tokens.get(m.group(1), m.group(0)), value)
        depth += 1
    return value


def to_rgb(value):
    """Первый сплошной цвет в значении; полупрозрачный — None (поверх чего он лежит, скрипт не знает)."""
    m = HEX.search(value)
    if m:
        h = norm_hex(m.group(0))[1:]
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = RGB.search(value)
    if m and (m.group(4) is None or float(m.group(4)) >= 1):
        return tuple(int(m.group(i)) for i in (1, 2, 3))
    return None


def luminance(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_style(text):
    out = {}
    for part in text.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            out[k.strip().lower()] = v.strip()
    return out


def px(value, base):
    m = re.match(r'([\d.]+)\s*(px|rem|em)?', value or '')
    if not m:
        return base
    n = float(m.group(1))
    return n * 16 if m.group(2) == 'rem' else n * base if m.group(2) == 'em' else n


class Page(html.parser.HTMLParser):
    """Обходит макет и для каждого куска текста считает контраст с унаследованными цветом, фоном и размером."""

    def __init__(self, tokens):
        super().__init__(convert_charrefs=True)
        self.tokens = tokens
        self.disabled = {to_rgb(v) for k, v in tokens.items() if 'disabled' in k} - {None}
        self.stack = [{'color': None, 'bg': None, 'size': 16.0, 'weight': 400, 'tag': ''}]
        self.low = []                              # (контраст, нужно, текст, цвет, фон)
        self.checked = 0
        self.in_style = False
        self.styles = []

    def handle_starttag(self, tag, attrs):
        if tag == 'style':
            self.in_style = True
        top = dict(self.stack[-1], tag=tag)
        style = parse_style(dict(attrs).get('style') or '')
        if tag == 'body':
            style = {**self.body_rule(), **style}
        if 'color' in style:
            top['color'] = to_rgb(resolve(style['color'], self.tokens)) or top['color']
        bg = style.get('background-color') or style.get('background')
        if bg:
            rgb = to_rgb(resolve(bg, self.tokens))
            if rgb:
                top['bg'] = rgb
        if 'font-size' in style:
            top['size'] = px(resolve(style['font-size'], self.tokens), top['size'])
        if 'font-weight' in style:
            w = resolve(style['font-weight'], self.tokens)
            top['weight'] = 700 if w == 'bold' else int(w) if w.isdigit() else top['weight']
        if re.fullmatch(r'h[1-6]|strong|b|th', tag) and 'font-weight' not in style:
            top['weight'] = max(top['weight'], 600)
        if tag not in VOID:
            self.stack.append(top)

    def body_rule(self):
        for css in self.styles:
            m = re.search(r'(?:^|[\s,}])body\s*\{([^}]*)\}', css)
            if m:
                return parse_style(m.group(1))
        return {}

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
            return
        text = data.strip()
        top = self.stack[-1]
        if not text or top['tag'] in ('script', 'title') or not top['color'] or not top['bg']:
            return
        if '{{' in text or top['color'] in self.disabled:
            return
        large = top['size'] >= 24 or (top['size'] >= 18.66 and top['weight'] >= 700)
        need = 3.0 if large else 4.5
        c = contrast(top['color'], top['bg'])
        self.checked += 1
        if c < need:
            self.low.append((c, need, text[:40], top['color'], top['bg']))


def image_width(path):
    data = path.read_bytes()[:64]
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>I', data[16:20])[0]
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        kind = data[12:16]
        if kind == b'VP8 ':
            return struct.unpack('<H', data[26:28])[0] & 0x3FFF
        if kind == b'VP8L':
            b = data[21:25]
            return 1 + (((b[1] & 0x3F) << 8) | b[0])
        if kind == b'VP8X':
            return 1 + int.from_bytes(data[24:27], 'little')
    return None


def hex_str(rgb):
    return '#%02X%02X%02X' % rgb


def main():
    ap = argparse.ArgumentParser(description='Проверка выгрузки макетов с холста.')
    ap.add_argument('folder', help='папка выгрузки (эталон)')
    ap.add_argument('--widths', required=True, help='ширины кадров из задания через запятую, например 375,1440')
    ap.add_argument('--tokens', action='append', help='файл токенов; по умолчанию все *.css папки')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    root = pathlib.Path(a.folder)
    if not root.is_dir():
        print('Ошибка запуска: нет папки %s' % root)
        return 2
    widths = [int(w) for w in a.widths.split(',') if w.strip()]
    token_files = [pathlib.Path(t) for t in a.tokens] if a.tokens else sorted(root.rglob('*.css'))
    tokens = load_tokens(token_files)
    token_hex = {norm_hex(m) for v in tokens.values() for m in HEX.findall(v)}
    token_fonts = {v.split(',')[0].strip().strip('\'"').lower() for k, v in tokens.items() if 'font' in k and ',' in v}
    pages = sorted(p for p in root.rglob('*.html'))
    out = []
    if not pages:
        print('Ошибка запуска: в %s нет макетов *.html' % root)
        return 2

    # Ширины кадров: раскладка холста знает ширину каждого макета.
    boards = {}
    for cj in root.rglob('canvas.json'):
        for name, b in (json.loads(cj.read_text(encoding='utf-8')).get('boards') or {}).items():
            if isinstance(b, dict) and 'w' in b:
                boards[name] = int(b['w'])
    if boards:
        missing = [w for w in widths if w not in boards.values()]
        other = sorted('%s %d' % (n, w) for n, w in boards.items() if w not in widths)
        if missing:
            out.append((STOP, 'ширины кадров', 'нет ни одного кадра шириной %s px из задания'
                        % ', '.join(map(str, missing))))
        else:
            out.append((OK, 'ширины кадров', 'есть %s px' % ', '.join(map(str, widths))))
        if other:
            out.append((WARN, 'кадры другой ширины', '%s — это сборка из нескольких экранов или ошибка ширины?'
                        % '; '.join(other)))
    else:
        out.append((WARN, 'ширины кадров', 'нет canvas.json с размерами кадров — ширины не проверены'))

    # Снимки: у каждого макета свой.
    shots = [p for p in root.rglob('*') if p.suffix.lower() in ('.png', '.webp') and 'shot' in str(p.parent).lower()]
    stems = {p.stem.lower() for p in shots}
    no_shot = [p.name for p in pages if not any(s.startswith(p.name.split('.')[0].lower()) for s in stems)]
    if no_shot:
        out.append((WARN, 'снимки', 'нет снимка у макетов: %s' % ', '.join(no_shot)))
    elif shots:
        sw = sorted({w for w in (image_width(p) for p in shots) if w})
        out.append((OK, 'снимки', 'у каждого макета есть; ширины снимков %s px' % ', '.join(map(str, sw))))

    # Цвета, шрифты, шаблоны, контраст.
    stray, fonts, low, checked = {}, {}, [], 0
    for p in pages:
        text = p.read_text(encoding='utf-8')
        for h in {norm_hex(x) for x in HEX.findall(text)} - token_hex:
            stray.setdefault(h, []).append(p.name)
        for fam in re.findall(r'font-family\s*:\s*([^;"\'}]+)', text):
            first = resolve(fam, tokens).split(',')[0].strip().strip('\'"').lower()
            if token_fonts and first not in token_fonts and 'mono' not in first:
                fonts.setdefault(first, set()).add(p.name)
        page = Page(tokens)
        page.feed(text)
        checked += page.checked
        low += [(c, need, p.name, t, fg, bg) for c, need, t, fg, bg in page.low]
    if stray:
        rows = ['%s (%s)' % (h, ', '.join(sorted(set(f))[:3])) for h, f in sorted(stray.items())]
        out.append((WARN, 'цвета вне токенов', '%d: %s' % (len(rows), '; '.join(rows[:12]))))
    elif token_hex:
        out.append((OK, 'цвета', 'все цвета макетов есть в токенах'))
    if fonts:
        out.append((WARN, 'шрифты вне токенов', '; '.join('%s (%s)' % (f, ', '.join(sorted(n)[:3]))
                                                       for f, n in sorted(fonts.items()))))
    if low:
        worst = {}
        for c, need, name, t, fg, bg in sorted(low):
            worst.setdefault((hex_str(fg), hex_str(bg), need), (c, name, t))
        rows = ['%s на %s — %.2f:1 при норме %.1f («%s», %s)' % (fg, bg, c, need, t, name)
                for (fg, bg, need), (c, name, t) in sorted(worst.items(), key=lambda kv: kv[1][0])]
        out.append((WARN, 'контраст', '%d пар ниже нормы: %s' % (len(rows), '; '.join(rows[:8]))))
    elif not checked:
        out.append((WARN, 'контраст', 'не проверен: ни у одного текста скрипт не нашёл и цвет, и фон в атрибутах '
                    'style — сверь контраст сам'))
    else:
        out.append((OK, 'контраст', 'проверено %d кусков текста, все не ниже нормы WCAG' % checked))

    for level, what, note in out:
        print('%-9s %s: %s' % (level, what, note))
    stops = sum(1 for r in out if r[0] == STOP)
    print('\nИтог: %s' % ('стоп-находок нет' if not stops else 'стоп-находок %d' % stops))
    return 1 if stops else 0


if __name__ == '__main__':
    sys.exit(main())
