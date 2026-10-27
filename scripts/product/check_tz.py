"""Проверка формы ТЗ продукта без модели.

python check_tz.py <файл ТЗ>

Проверяет то, что видно без чтения смысла (references/writing/doc-tz.md):
- в шапке назван режим: гипотеза или система;
- раздел «Идеальный результат» есть и в нём не больше трёх предложений;
- есть раздел «Как это работает», в нём этапы, у каждого этапа есть пункт с галочкой и, кроме
  последнего, переход «Дальше этап N»;
- есть раздел «На будущее» и «Что нужно от заказчика»;
- нет открытых вопросов: знака «?», слов «уточнить», «будет определено», «Открыто»;
- нет внутренних номеров: _TASK_, D-123.

Код возврата: 0 — чисто, 1 — найдены нарушения, 2 — файл не прочитан.
"""
import re
import sys
from pathlib import Path


def sections(text):
    """Разделы второго уровня: заголовок -> текст."""
    out, name, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if name is not None:
                out[name] = "\n".join(buf)
            name, buf = m.group(1).strip().lower(), []
        elif name is not None:
            buf.append(line)
    if name is not None:
        out[name] = "\n".join(buf)
    return out


def find(secs, key):
    for k, v in secs.items():
        if k.startswith(key):
            return v
    return None


def sentences(s):
    s = re.sub(r"\s+", " ", s).strip()
    return [x for x in re.split(r"(?<=[.!?])\s+", s) if x]


def check(text):
    found = []
    head = text.split("\n## ", 1)[0]
    if not re.search(r"Режим:\s*(гипотеза|система)", head, re.I):
        found.append("в шапке нет строки «Режим: гипотеза | система»")
    secs = sections(text)
    res = find(secs, "идеальный результат")
    if res is None:
        found.append("нет раздела «Идеальный результат»")
    elif len(sentences(res)) > 3:
        found.append(f"в «Идеальном результате» {len(sentences(res))} предложений, нужно не больше трёх")
    how = find(secs, "как это работает")
    if how is None:
        found.append("нет раздела «Как это работает»")
    else:
        stages = re.split(r"(?m)^###\s+", how)[1:]
        if not stages:
            found.append("в «Как это работает» нет этапов (заголовков ###)")
        for i, st in enumerate(stages):
            title = st.splitlines()[0].strip()
            if not re.search(r"(?m)^\s*-\s*\[[ xх]\]", st):
                found.append(f"у этапа «{title}» нет пункта с галочкой")
            last = i == len(stages) - 1
            if not last and not re.search(r"Дальше|Переход", st):
                found.append(f"у этапа «{title}» нет перехода «Дальше этап N»")
    for key, name in (("на будущее", "На будущее"), ("что нужно от заказчика", "Что нужно от заказчика")):
        if find(secs, key) is None:
            found.append(f"нет раздела «{name}»")
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("#", "```")):
            continue
        if "?" in line:
            found.append(f"строка {n}: знак «?» — открытый вопрос идёт в вопросы к встрече")
        if re.search(r"уточнит|будет определено|\bОткрыто\b", line, re.I):
            found.append(f"строка {n}: открытый вопрос в ТЗ")
        if re.search(r"_TASK_\d|\bD-\d{2,}", line):
            found.append(f"строка {n}: внутренний номер задачи или решения")
    return found


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 2)
    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    except OSError as e:
        print(f"Файл не прочитан: {e}. Укажи путь к ТЗ в UTF-8.")
        sys.exit(2)
    found = check(text)
    for f in found:
        print(f"НАРУШЕНИЕ  {f}")
    print(f"Нарушений: {len(found)}")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
