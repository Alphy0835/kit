# Основание справок о коде

Источники и таблицы «основание правил» справок `references/code/`. Из самих справок убраны 16.10.2026 по слову
Владельца: справку читает агент в работе, источники ему не нужны. Здесь — для того, кто правит набор.

## `changes.md`

Указатели из шапки: Откуда взято каждое правило — `docs/code-synthesis.md`.

- Anthropic, «Claude prompting best practices», раздел о лишнем рвении: не выходить за просьбу, не дописывать
  комментарии к чужому коду, не делать помощников ради одного вызова.
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI, «Codex Prompting Guide»: сначала искать готовый помощник.
  https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- GitHub, «Agent pull requests are everywhere», 07.05.2026: агент заново пишет помощник, который уже есть.
  https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/
- Google, «What to look for in a code review»: over-engineering, комментарий объясняет «зачем»,
  переформатирование отдельно от правки. https://google.github.io/eng-practices/review/reviewer/looking-for.html

Основание правил:

| Правило | Основание |
|---|---|
| 1, 5 | Только источник |
| 2 | Источник и 4 наших случая |
| 3 | Только наши случаи: 7 задач |
| 4 | Источник и 3 наших случая |

## `config.md`

Указатели из шапки: Откуда взято каждое правило — `docs/code-synthesis.md`.

- The Twelve-Factor App, «Config»: настройка — то, что меняется между развёртываниями; хранится в окружении.
  https://12factor.net/config
- CISQ, ISO/IEC 5055: зашитые литералы и учётные данные — слабое место.
  https://www.it-cisq.org/standards/code-quality-standards/
- Библиотека детекторов Amazon Q: зашитые учётные данные, секреты в журнале.
  https://docs.aws.amazon.com/codeguru/detector-library/python/
- OWASP Secure Coding Practices: обработка ошибок и журнал, защита данных.
  https://owasp.github.io/www-project-secure-coding-practices-quick-reference-guide/stable-en/02-checklist/05-checklist

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Источник |
| 2 | Только наши случаи: 13 задач |
| 3 | Наши случаи: два |
| 4 | Источник и четыре наших случая |

## `errors.md`

Указатели из шапки: Откуда взято каждое правило — `docs/code-synthesis.md`.

- OpenAI, «Codex Prompting Guide»: без широкого перехвата и молчаливых умолчаний, без тихого выхода на плохих
  данных. https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- OpenAI, «Harness engineering», 11.02.2026: разбирать форму данных на границе, а не строить логику на догадках.
  https://openai.com/index/harness-engineering/
- PEP 8, «Programming Recommendations»: называть конкретные исключения, держать `try` коротким.
  https://peps.python.org/pep-0008/
- Google Python Style Guide, 2.4: не ловить `Exception`, если ошибка не пробрасывается.
  https://google.github.io/styleguide/pyguide.html
- OWASP Top 10:2025, A10 — неверная обработка исключительных ситуаций. https://top10.owasp.org/2025
- Anthropic, «Claude prompting best practices»: без защиты от невозможного.
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Основание правил:

| Правило | Основание |
|---|---|
| 1, 2, 3 | Источник и наши случаи: 10 задач с ответом 500, около 20 — с тихой порчей |
| 4 | Источник и один наш случай |
| 5 | Только наш случай |

## `concurrency.md`

Добавлено 18.10.2026 со скилом бекенда. В замере возвратов «Гонки, повторы, тайм-ауты» — 21 замечание, 14 из
них причина возврата, скрипт не ловит ни одного (`docs/measure-returns.md`). Справки по теме не было.

- AWS Builders' Library, «Making retries safe with idempotent APIs»: ключ повтора, повтор без второго действия.
  https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- Stripe, «Idempotent requests»: ключ повтора на запрос, тот же ответ на повтор.
  https://docs.stripe.com/api/idempotent_requests
- AWS Builders' Library, «Timeouts, retries, and backoff with jitter»: тайм-аут у каждого вызова, растущая пауза
  со случайным разбросом. https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Google SRE Book, «Addressing Cascading Failures»: предел повторов на запрос и бюджет повторов, разброс паузы.
  https://sre.google/sre-book/addressing-cascading-failures/
- SQLite, «Transaction»: `BEGIN IMMEDIATE` берёт блокировку записи сразу. https://www.sqlite.org/lang_transaction.html
- Python, `os.replace`: подмена файла одним действием. https://docs.python.org/3/library/os.html
- FastAPI, «Concurrency and async / await»: библиотеку без `await` (большинство баз) зовут из обычного `def`, его
  FastAPI выполняет в пуле потоков. https://fastapi.tiangolo.com/async/
- Python, «Developing with asyncio», раздел «Running Blocking Code»: блокирующий код не вызывать прямо из
  асинхронного. https://docs.python.org/3/library/asyncio-dev.html#running-blocking-code

Правило 7 добавлено 19.10.2026 после разбора правил affaan-m/ECC (`rules/python/fastapi.md`). Остальное оттуда
уже было в наборе (AC-4, AC-5, JWT в `references/security/base/`) или спорит с процессом (80 % покрытия, TDD на
всё, ревью после каждой правки).

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Источники (AWS, Stripe) и наш случай: повторный импорт CN_TASK_030 |
| 2 | Наши случаи: LD_TASK_031, CN_TASK_097 |
| 3 | Источник (SQLite) и наши случаи: CN_TASK_108 — дефект, CN_TASK_072 — верно с первого раза |
| 4 | Источник (`os.replace`) и наш случай: CB_TASK_172, возврат 2 |
| 5 | Источники (AWS, Google SRE) и наш случай: KB_TASK_023 |
| 6 | Только наш случай: CN_TASK_072, тест с арендой 25 мс |
| 7 | Только источники (FastAPI, Python). У донора нарушений нет: `sqlite3` в обычных `def`, `to_thread` в 11 файлах |
