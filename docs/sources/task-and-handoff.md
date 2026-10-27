# Первоисточники: как ставить задачу агенту и как агенту проверять работу перед сдачей

Собрано 14.10.2026 по слову владельца «да давай сделаем» — к сводке `task-synthesis.md`. Собирал субагент на Sonnet
по поручению тим лида; «я» ниже — он. Тим лид сверил с оригиналом одну цитату — П-4, «audit each claim against
a tool result»: совпала. Остальное не сверено. Это подборка источников, правил в ней нет: только что сказано и где.
Соседние подборки: `skills-and-agents.md`, `testing.md`, `ai-code-mistakes.md`.

## Как читать метки

- **открыт, текст** — инструмент отдал почти сырой текст страницы; цитаты можно считать дословными.
- **открыт, выжимка** — страницу открыл, но инструмент WebFetch пропускает её через малую модель и отдаёт пересказ с цитатами. Цитаты оттуда я не сверял с оригиналом по символам. Перед тем как вшивать в скил, их стоит сверить.
- **по выдаче** — страница не открылась, знаю её по поиску. Правил на ней не строю.
- Все страницы открыты 14.10.2026. Где на странице нет даты, так и написано.
- Цитаты в оригинале, до 25 слов.

## Список источников

### Anthropic

| Метка | Название | Адрес | Дата на странице | Как открыт |
|---|---|---|---|---|
| П-1 | Best practices for Claude Code | https://code.claude.com/docs/en/best-practices | без даты | открыт, текст |
| П-2 | Prompting best practices (общий для всех моделей) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | без даты; перечисляет модели до Fable 5.1 | открыт, текст |
| П-3 | Prompting Claude Sonnet 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5 | без даты | открыт, текст |
| П-4 | Prompting Claude Fable 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5 | без даты | открыт, текст |
| П-5 | Prompting Claude Opus 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 | без даты | открыт, текст |
| П-6 | Prompting Claude Fable 5.1 (разделы «Finish the whole task», «Keep changes and tests to what the task asks for») | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 | без даты | открыт, текст (читал нужные разделы) |
| П-7 | Keep Claude working toward a goal (`/goal`) | https://code.claude.com/docs/en/goal | без даты | открыт, текст |
| П-8 | Getting the most out of Opus 5.5 in Claude and Claude Code (Addy Osmani) | https://claude.dev/blog/getting-the-most-out-of-opus-5-5/ | 22.09.2026 | открыт, выжимка |
| П-9 | A field guide to Claude Fable 5: Finding your unknowns (Thariq Shihipar) | https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns | 06.07.2026 | открыт, выжимка |
| П-10 | The new rules of context engineering for Claude 5 generation models (Thariq Shihipar) | https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/ | 24.07.2026 | открыт, выжимка |
| П-11 | Harness design for long-running application development (Prithvi Rajasekaran) | https://www.anthropic.com/engineering/harness-design-long-running-apps | 24.03.2026 | открыт, выжимка |
| П-12 | Effective harnesses for long-running agents (Justin Young) | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 26.11.2025 | открыт, выжимка |
| П-13 | Building effective agents (Erik S., Barry Zhang) | https://www.anthropic.com/engineering/building-effective-agents | 19.12.2024 | открыт, выжимка |
| П-14 | Demystifying evals for AI agents | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 09.01.2026 | открыт, выжимка |
| П-15 | Building a C compiler with a team of parallel Claudes (Nicholas Carlini) | https://www.anthropic.com/engineering/building-c-compiler | 05.02.2026 | открыт, выжимка |
| П-16 | From shortcuts to sabotage: natural emergent misalignment from reward hacking | https://www.anthropic.com/research/emergent-misalignment-reward-hacking | 21.11.2025 | открыт, выжимка |
| П-17 | Skill authoring best practices (разделы про цикл «проверил, исправил, повторил») | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | без даты | открыт, текст |
| П-18 | Claude Code Skills, раздел «Run and verify your app» (`/verify`) | https://code.claude.com/docs/en/skills | без даты | открыт, выжимка (прочитано 100 000 из 109 074 знаков) |
| — | An update on recent Claude Code quality reports | https://www.anthropic.com/engineering/april-23-postmortem | 23.04.2026 | открыт, выжимка; по теме правил нет, в правила не вошёл |

### OpenAI

| Метка | Название | Адрес | Дата | Как открыт |
|---|---|---|---|---|
| П-19 | Codex: Best practices | https://learn.chatgpt.com/guides/best-practices (со старого адреса developers.openai.com/codex/learn/best-practices — перенаправление 308) | без даты | открыт, выжимка |
| П-20 | Codex: Prompting | https://learn.chatgpt.com/docs/prompting | без даты | открыт, выжимка |
| П-21 | Codex: Long-running work | https://learn.chatgpt.com/docs/long-running-work | без даты | открыт, выжимка |
| П-22 | Codex: Custom instructions with AGENTS.md | https://learn.chatgpt.com/docs/agent-configuration/agents-md | без даты | открыт, выжимка |
| П-23 | Codex Prompting Guide (для gpt-5.3-codex), cookbook | https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide | без даты | открыт, выжимка |
| П-24 | GPT-5 prompting guide, cookbook (страница помечена как архивная) | https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide | без даты | открыт, выжимка |
| П-25 | Run long horizon tasks with Codex | https://developers.openai.com/blog/run-long-horizon-tasks-with-codex | без даты | открыт, выжимка |
| П-26 | Using GPT-6 Astra | https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra | без даты | открыт, выжимка |
| П-27 | Rethinking skills and prompts for GPT-6 Astra | https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra | дата и автор на странице не указаны (в `skills-and-agents.md` — 05.09.2026, в `testing.md` — 11.09.2026) | открыт, выжимка |
| П-28 | Why we no longer evaluate SWE-bench Verified; Introducing SWE-bench Verified | https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/ ; https://openai.com/index/introducing-swe-bench-verified/ | не знаю | **по выдаче**: прямая загрузка — 403, во встроенном браузере — страница проверки «Один момент…»; обходить защиту не стал |
| — | Monitoring reasoning models for misbehavior (reward hacking) | https://openai.com/index/chain-of-thought-monitoring/ | не знаю | не открылась (403), в правила не вошла |
| — | OpenAI GPT-5 System Card | https://arxiv.org/pdf/2601.03267 | не знаю | PDF отдал нечитаемый поток, раздел об обмане не прочитан; в правила не вошёл |

### Google

| Метка | Название | Адрес | Дата | Как открыт |
|---|---|---|---|---|
| П-30 | Google eng-practices: Small CLs | https://google.github.io/eng-practices/review/developer/small-cls.html | без даты | открыт, выжимка |
| П-31 | Google eng-practices: Writing good CL descriptions | https://google.github.io/eng-practices/review/developer/cl-descriptions.html | без даты | открыт, выжимка |
| П-32 | Jules: документация | https://jules.google/docs/ | без даты | открыт, выжимка (страница короткая) |
| П-33 | Meet Jules' sharpest critic and most valuable ally (Korevec, Hassen, Zhang) | https://developers.googleblog.com/meet-jules-sharpest-critic-and-most-valuable-ally/ | 12.08.2025 | открыт, выжимка |
| П-34 | The Anatomy of Harness Engineering (Mullen, Gunderman) | https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/ | 09.09.2026 | открыт, выжимка |
| П-35 | Gemini in Android Studio: Best practices | https://developer.android.com/studio/gemini/best-practices | обновлено 06.03.2026 | открыт, выжимка |
| — | Gemini Code Assist agent mode | https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer | не знаю | **по выдаче** (редирект, страницу не открыл), правил нет |
| — | Software Engineering at Google (книга) | — | — | для этого задания не открывал; тесты разобраны в `testing.md` |

### Microsoft и GitHub

| Метка | Название | Адрес | Дата | Как открыт |
|---|---|---|---|---|
| П-36 | GitHub Docs: Get the best results from Copilot cloud agent | https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results | без даты | открыт, выжимка |
| П-37 | GitHub Docs: About Copilot coding agent | https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent | без даты | открыт, выжимка |
| П-38 | GitHub Docs: Review AI-generated code | https://docs.github.com/en/copilot/tutorials/review-ai-generated-code | без даты | открыт, выжимка |
| П-39 | How to write a great agents.md: Lessons from over 2,500 repositories (Matt Nigh) | https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/ | 19.11.2025 | открыт, выжимка |
| П-40 | Spec-driven development with AI (Den Delimarsky) | https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/ | 02.09.2025 | открыт, выжимка |
| П-41 | github/spec-kit: spec-driven.md | https://github.com/github/spec-kit/blob/main/spec-driven.md | без даты | открыт, выжимка |
| П-42 | github/spec-kit: README | https://github.com/github/spec-kit | без даты | открыт, выжимка |
| П-43 | WRAP up your backlog with GitHub Copilot coding agent (Ellich, Etcovitch) | https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/ | 26.12.2025 | открыт, выжимка |
| П-44 | Assigning and completing issues with coding agent in GitHub Copilot (Lietzke) | https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/ | 06.06.2025 | открыт, выжимка |
| П-45 | VS Code: Best practices for using AI | https://code.visualstudio.com/docs/copilot/best-practices | на странице 14.10.2026 | открыт, выжимка |
| П-46 | VS Code: Build with AI (обзор агентов) | https://code.visualstudio.com/docs/copilot/agents/overview | на странице 14.10.2026 | открыт, выжимка |
| — | GitHub Blog: Agent pull requests are everywhere (07.05.2026) | — | — | в этот раз не открывал; уже разобран в `ai-code-mistakes.md`, блок Г-2 |

### Amazon и AWS

| Метка | Название | Адрес | Дата | Как открыт |
|---|---|---|---|---|
| П-47 | Kiro: Specs | https://kiro.dev/docs/specs/ | обновлено 02.10.2026 | открыт, выжимка |
| П-48 | Kiro: Feature specs | https://kiro.dev/docs/specs/feature-specs/ | обновлено 04.08.2026 | открыт, выжимка |
| П-49 | Kiro: Bugfix specs | https://kiro.dev/docs/specs/bugfix-specs/ | обновлено 04.08.2026 | открыт, выжимка |
| П-50 | Kiro: Specs best practices | https://kiro.dev/docs/specs/best-practices/ | без даты | открыт, выжимка |
| П-51 | Kiro: Correctness (property-based testing) | https://kiro.dev/docs/specs/correctness/ | обновлено 04.08.2026 | открыт, выжимка |
| П-52 | Introducing Kiro (Swaminathan, Singh) | https://kiro.dev/blog/introducing-kiro/ | 14.07.2025 | открыт, выжимка |
| П-53 | An insider look at Amazon's culture and processes (Working Backwards; Bryar, Carr) | https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes | без даты | открыт, выжимка. Страница на aws.amazon.com (executive-insights) — 404 |
| — | AWS Security Blog: Balancing speed and safety (30.07.2026) | — | — | не открывал; уже в `ai-code-mistakes.md`, блок Ам-1 |

Номера П-29 нет: пропуск в нумерации.

## Уже есть в соседних подборках (не дублирую)

- `skills-and-agents.md`: Opus 5.5 («назвать, что значит готово»), Fable field guide, Astra и «вычеркнуть напоминания про тесты», `/goal`-подобное «результат, ограничения, проверка» из Long-running work, статья Anthropic от 24.03.2026 («исполнителя и оценщика разделять»). Здесь они пересобраны под вопрос и дополнены цитатами.
- `testing.md`: «дай агенту проверку» (Claude Code best practices), Effective harnesses, «не зашивать значения» (prompting best practices), Anatomy of Harness Engineering, Codex best practices. Здесь повторены только там, где нужна цитата под правило задания или отчёта.
- `ai-code-mistakes.md`: GitHub «Review AI-generated code» и «Agent PRs» (обман проверок, мнимая правильность), AWS R006/R007, debug-gym. Здесь только ссылаюсь.

---

## а) Что писать в задании

- Дай запускаемую проверку и пример входа и выхода прямо в тексте задачи, а не «сделай функцию». Пример Anthropic: цели «валидатор почты» задаются тремя парами вход/ответ и просьбой прогнать тесты. «example test cases: user@example.com is true, invalid is false, user@.com is false. run the tests after implementing» — П-1
- Сужай задачу: файл, сценарий, предпочтения по тестам. «write a test for foo.py covering the edge case where the user is logged out. avoid mocks.» — П-1
- Для ошибки пиши три вещи: симптом, где искать, как выглядит «исправлено». «Provide the symptom, the likely location, and what "fixed" looks like.» — П-1
- Для ошибки у Codex шаги воспроизведения и ограничения важнее общего описания. «the repro steps and constraints (these matter more than a high-level description)» — П-20
- Бери образец из своего кода и называй его файлом. «Point Claude to patterns in your codebase.» — П-1. Лучший образец — исходный код: «the absolute best reference is source code» — П-9. Макет в HTML даёт лучший результат, чем описание или снимок: «a HTML mockup of a design will generally produce better results than a description of the design or a screenshot» — П-10
- Самодостаточное ТЗ называет файлы и интерфейсы, что не входит в работу, и заканчивается сквозной проверкой. «name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step» — П-1
- Задание — это три части: результат, ограничения, проверка. «Describe the result you want, not only the activity» — П-21. Текст цели служит и первым запросом, и критерием завершения; если итог неясен, сначала `/plan`, чтобы получить измеримые критерии — П-21
- Задание у Codex — четыре части: цель, контекст, ограничения, «готово, когда». «What should be true before the task is complete.» — П-19
- Условие завершения (`/goal`): один измеримый итог, названная проверка, важные ограничения. Пример ограничения: «no other test file is modified». Оценщик видит только то, что агент вывел в разговор, сам ничего не запускает, поэтому условие должно доказываться выводом агента — П-7
- «Готово» для долгой работы в файле-ТЗ: раздел «Done when» с проверками и сценарием показа. Назначение файла: «Freeze the target so the agent doesn't "build something impressive but wrong."» — П-25
- Определи «выходной контракт»: какие файлы, какой вывод, какое поведение, какие тесты. «Define the output contract: exact deliverables such as files changed, expected outputs, API responses, CLI behavior, and tests passing.» — П-24
- Для баг-задачи Kiro требует три части: текущее поведение (дефект), ожидаемое, неизменное. Неизменное — защита от регрессии: «WHEN [condition] THEN the system SHALL CONTINUE TO [existing behavior]» — П-49. Отдельно: нужно прямо назвать «Any code or behavior that must not change» — П-50
- Требования у Kiro пишутся по шаблону EARS «когда … система должна …». Заявленная польза: «Each requirement can be directly translated into test cases.» — П-48. Критерии приёмки в EARS заодно покрывают крайние случаи — П-52
- В спецификации — что и зачем, а не как. «Focus on the "what" and "why" of your project, not the technical details.» — П-40. Шаблон Spec Kit: «Avoid HOW to implement (no tech stack, APIs, code structure).» — П-41
- Критерии приёмки становятся тестами. «Acceptance scenarios become tests.» — П-41. Каждая фича прослеживается до пользовательской истории с критериями — П-41
- Не оставляй пробелы на угадывание: в шаблоне Spec Kit неясное помечается вопросом. «Mark all ambiguities: Use [NEEDS CLARIFICATION: specific question]» и «Don't guess» — П-41. Спецификация считается законченной, когда таких пометок не осталось — П-41
- Скажи, зачем это нужно: так модель сама достраивает недостающее. «I'm working on [the larger task] for [who it's for]. They need [what the output enables].» — П-4. То же общее правило: контекст и мотив обобщаются лучше запрета — П-2
- Пиши так, чтобы понял новый сотрудник. «Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they'd be confused, Claude will be too.» — П-2. GitHub: писать задачу для «someone brand new to the codebase», с примерами желаемого результата — П-43; «Treat the issue as a prompt» — П-36
- Хочешь «сверх» — проси явно. «If you want "above and beyond" behavior, explicitly request it rather than relying on the model to infer this» — П-2
- Критерии и файлы в задаче Copilot: описание проблемы, критерии приёмки, какие файлы менять — П-36
- Ожидаемый результат в запросе — один из самых полезных приёмов. «Include expected output for verification» (на странице: «one of the highest-leverage things you can do») — П-45
- Чего не писать:
  - Противоречия: модель тратит силы на их примирение. «expends reasoning tokens searching for a way to reconcile the contradictions» — П-24. То же у Anthropic: «several conflicting messages in a single request» — П-10
  - Лишнюю детальность: «If you are too specific, Claude will follow your instructions even when a pivot may be more appropriate.» — П-9. В длинной работе ошибки подробной технической спецификации «would cascade into the downstream implementation» — П-11
  - Постоянные правила в тексте задачи. Частая ошибка: «Overloading the prompt with durable rules instead of moving them into AGENTS.md or a skill» — П-19
  - Лишнее в файле правил: на каждую строку вопрос «Would removing this cause Claude to make mistakes?» — П-1
  - Устаревшие напоминания «запусти тесты», «проверь дважды» для новых моделей — см. раздел «Где источники спорят»
  - Слишком много контекста: «too much information might lead Gemini astray, whereas too little won't provide enough context» — П-35
- Границы агента — тремя уровнями: всегда делать, спросить сначала, никогда. «Never commit secrets» — самое частое полезное ограничение по 2 500 репозиториям — П-39
- Рамки объёма говори положительной инструкцией: «Deliver what was asked, at the scope intended.» — П-5. Запрос или утверждённый план задаёт объём, и объём — это и есть результат: «don't quietly narrow, widen, or swap it» — П-6

## б) Размер и нарезка задачи

- Google: правильный размер правки — одно самодостаточное изменение. «the right size for a CL is one self-contained change» — П-30. Ориентир: «100 lines is usually a reasonable size for a CL, and 1000 lines is usually too large» — П-30. Тесты идут вместе с кодом, рефакторинг — отдельной правкой — П-30. Это правила для людей-авторов, про агентов в тексте не сказано
- GitHub: «Break complex tasks into smaller, focused tasks.» — П-37. WRAP: «A» значит атомарные задачи, большие делить на «multiple, independent, smaller tasks», числа нет — П-43. Spec Kit: «Each task should be something you can implement and test in isolation.» — П-40
- OpenAI: контрольные точки «small enough to complete in one loop», у каждой критерии приёмки и команды проверки. «Milestones small enough to complete in one loop» и «Acceptance criteria + validation commands per milestone» — П-25. Числа нет
- OpenAI: один чат на один связный результат. «Keep one chat per coherent unit of work» — П-19
- Anthropic, причина дробить: агент берёт слишком много. «the agent tended to try to do too much at once» — П-12; работает «only one feature at a time» — П-12
- Anthropic, где дробить не надо: «If you could describe the diff in one sentence, skip the plan.» — П-1. Для мелкого с понятным объёмом проси делать сразу — П-1
- Anthropic, обратное: Opus 5 лучше всего работает, когда ему сразу дают всё задание целиком. «performs best when given the complete task specification up front and left to run» — П-5
- Пример нарезки у Anthropic: короткий запрос в 1–4 предложения развёрнут в 16 функций на десять этапов; у этапа 3 было 27 критериев — П-11
- Gemini: если агент пошёл не туда, веди маленькими шагами. «guide Gemini through a series of smaller, sequential prompts rather than asking for everything at once» и «lets you verify each step before proceeding» — П-35. VS Code: «Break down complex tasks» — П-45
- Kiro: несколько спецификаций на разные функции, а не одна на весь код. «We recommend creating multiple specs for different features.» Предельного размера нет — П-50
- Какие задачи агенту не давать: «Tasks lacking clear definition: tasks with ambiguous requirements, open-ended tasks» — П-36; также сложные с знанием всех репозиториев, чувствительные (безопасность, персональные данные, вход) — П-36. Начинать с простых — П-36
- Если поправил дважды и всё не так, начинай заново с лучшим заданием. «A clean session with a better prompt almost always outperforms a long session with accumulated corrections.» — П-1
- Планирование нужно для многофайловых и неясных задач: «Planning is most useful when you're uncertain about the approach, when the change modifies multiple files, or when you're unfamiliar with the code» — П-1; у Codex пропуск планирования на сложных задачах назван ошибкой — П-19; для простых «Skip using the planning tool for straightforward tasks.» — П-23

## в) Как агент уточняет непонятное

- Перед работой — интервью. «Interview me in detail using the AskUserQuestion tool.» и «Don't ask obvious questions, dig into the hard parts I might not have considered.» Потом спецификация в файл, реализация в новом сеансе — П-1
- Интервью по одному вопросу: «Interview me one question at a time about anything ambiguous» — П-9
- Codex: для неясной идеи интервью превращает её в конкретную: «challenge your assumptions and turn the fuzzy idea into something concrete before writing code» — П-19. VS Code: при неясной задаче «Tell the AI to ask clarifying questions» — П-45
- Проверка требований до дизайна: Kiro «Analyze Requirements» ищет «logical inconsistencies, ambiguities, conflicting constraints, and gaps» — П-48, П-50
- Во время работы — решать самому в обычных случаях. «Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work.» — П-5. Почти то же у Fable 5.1: читать неясность «the way a careful colleague would» — П-6
- Когда останавливаться: «only stop to ask when you can't go on without the user or before a risky step» — П-3. Fable 5: только при разрушительном действии, настоящей смене объёма, нужен ввод, который есть только у человека; тогда «ask and end the turn, rather than ending on a promise» — П-4. Opus 5.5: «Stop and ask me only if a test fails for a reason you can't explain.» — П-8
- Возник вопрос по ходу: сначала сделать всё, что от ответа не зависит, потом назвать допущение; спросить в конце хода, только если ошибочная догадка была бы опасна или сделала бы работу бесполезной — П-6
- Часть задачи заблокирована: сделать остальное полностью и точно сказать, что не сделано и почему. «scaling it down is the user's call, not yours» — П-6
- Неясное: «implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well» — П-6
- Если просьба кажется ошибочной: сказать одним предложением и делать как просили. «say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it» — П-5
- OpenAI склоняет к действию: Codex «do not end your turn with clarifications unless truly blocked» — П-23; «If some details are missing, make reasonable assumptions and complete a working version of the feature» — П-23; GPT-5 guide: «Do not ask the human to confirm or clarify assumptions, as you can always adjust later» — П-24
- Astra спрашивает охотнее: «more likely to ask the user a question when additional input could materially change the result» — П-26. Просить утверждение — только когда есть готовый результат: «Prompt the model to ask for approval only after preparing a concrete, reviewable result» — П-26. Строгие «сначала спроси» теперь могут остановить работу там, где вас устроило бы продолжение — П-27
- Если оставить вопросы на потом, ломается автономный запуск: «asking "Want me to…?" or "Shall I…?" will block the work» — П-4, П-6. Anthropic сама оговаривает: этот блок «can also make the model less likely to ask about ambiguous requests, so check that trade-off on your own tasks» — П-6
- Предложение плана до правок: Jules «will generate a plan. You can review and approve it before any code changes are made» — П-32; Codex `/plan` — П-19, П-20
- Попросить агента назвать допущения о бизнес-логике: «what assumptions about business logic, design preferences, or user behaviors have been made?» — П-38

## г) Проверка перед сдачей

- Главное правило Anthropic: без запускаемой проверки «выглядит готовым» — единственный сигнал. «Claude stops when the work looks done. Without a check it can run, "looks done" is the only signal available, and you become the verification loop» — П-1
- Что считается проверкой: набор тестов, код возврата сборки, линтер, скрипт сравнения вывода с эталоном, снимок экрана в сравнении с макетом — П-1. «If you can't verify it, don't ship it.» — П-1
- Живой запуск: `/verify` собирает и запускает приложение, чтобы проверить правку «without falling back to tests or type checks» — П-18. Рецепт запуска записывается в `.claude/skills/verify/SKILL.md` и дальше используется — П-18. Рекомендация: запускать `/verify` после того, как прошла проверка агента — П-1
- Живой запуск, как человек: после просьбы «use browser automation tools and do all testing as a human user would» агент стал лучше проверять; без неё помечал функции готовыми после модульных тестов или curl — П-12
- Оценщик в Anthropic кликал по работающему приложению через Playwright «the way a user would», у каждого критерия жёсткий порог, провал любого — провал этапа — П-11
- Перед новой функцией — короткий сквозной прогон: «Manually run through a fundamental integration test before moving on to implementing new features.» — П-2
- Проверка интерфейса снимком: «take a screenshot of the result and compare it to the original. list differences and fix them» — П-1. Для длинных задач дай агенту инструмент проверки интерфейса (компьютер, браузер) — П-2
- Пример проверки по требованиям: ревьюер в свежем контексте против плана. «Check that every requirement is implemented, the listed edge cases have tests, and nothing outside the task's scope changed. Report gaps, not style preferences.» — П-1
- Ревьюер, которого просили искать пробелы, найдёт их почти всегда, даже в здоровой работе: «Chasing every finding leads to over-engineering». Совет: сказать ему отмечать только то, что влияет на правильность или названные требования — П-1
- Закрыть план перед сдачей. «Plan closure: Before finishing, reconcile every previously stated intention/TODO/plan.» — П-23
- Сборка и типы всегда: «Changes should always pass build and type-check.» — П-23. Повтор шагов воспроизведения после исправления: «Codex should re-run the repro steps after the fix» — П-20
- Запустить нужные проверки и просмотреть изменения: «run the relevant checks, confirm the result, and review the work before you accept it» — П-19; в списке — тесты, линтер, типы, просмотр diff на ошибки, регрессии и рискованные приёмы — П-19
- Проверка после каждого этапа, при провале — чинить, не идти дальше: «if validation fails, repair before moving on» — П-25
- Правка не зашла в сдачу, если проверка не запускалась по-настоящему: «A syntax-only check, or a check command that failed to start, does not count» — П-3. Если не хватает только зависимостей проекта — поставить их менеджером пакетов проекта и по lock-файлу, не через sudo — П-3
- Агент-проверяющий должен быть другим: «a verification subagent … has a fresh model try to refute the result, so the agent doing the work isn't the one grading it» — П-1. Fable 5: «Separate, fresh-context verifier subagents tend to outperform self-critique» — П-4. Цикл `/goal`: «completion is decided by a fresh model rather than the one doing the work» — П-7
- У Google критик Jules читает патч до сдачи и возвращает замечания. «Every proposed change undergoes adversarial review before completion.» — П-33. Почему не хватает тестов и линтера: «Linters follow shallow, fixed rules; tests validate specific assertions.» — П-33
- Без настройки агент-проверяющий слаб: «Out of the box, Claude is a poor QA agent»; он убеждал себя, что найденные огрехи не важны, и проверял поверхностно, без крайних случаев — П-11
- Жёсткие ворота: хук Stop блокирует конец хода, пока скрипт проверки не пройдёт — П-1. Это детерминированная проверка, в отличие от совета в файле правил — П-1
- Цикл «проверил, исправил, повторил»: «Run validator → fix errors → repeat» и «Only proceed when validation passes» — П-17. Для рискованных пакетных правок: сначала план в файле, проверка плана скриптом, потом исполнение — П-17
- Эталон для сравнения: в проекте компилятора GCC служил «known-good compiler oracle» — П-15. Условие: «the task verifier is nearly perfect, otherwise Claude will solve the wrong problem» — П-15
- Тесты нельзя править ради зелёного: «It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality.» — П-2, П-12. Список функций с полем «проходит», которое меняется только после проверки — П-12
- Общее решение вместо подгонки: «Implement a solution that works correctly for all valid inputs, not just the test cases.» и «If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them» — П-2
- Требования и тесты вместе: Kiro `#spec` — «Check if your implementation matches the spec's requirements» — П-50; каждая задача привязана к требованию, «so nothing falls through the cracks» — П-52
- Проверки на свойствах из требований дают «evidence of correctness, not a proof»; слабое свойство может пройти при неверном поведении — П-51
- Оговорка: новые модели проверяют сами. Opus 5 «verifies its own work without being told to» — П-5; Astra делает то же — П-27. Для Sonnet 5.5 на низком усилии добавлен абзац, потому что там он иногда «reports a change as done without running a check that exercises it» — П-3
- Проверка человеком: «Your role isn't just to steer. It's to verify.» — П-40; «Be skeptical of code that "looks right" but doesn't match your intent.» — П-38; автор задачи не может быть последним утверждающим — П-44
- При ревью кода от ИИ смотреть, не удалены ли и не пропущены ли тесты вместо исправления. «Watch for tests that are deleted or skipped, instead of fixed.» — П-38
- Google по проверкам агента: измерять маленькие поведения, например «When modifying a build file, does it run the local validator before declaring it complete?» — П-34
- Тесты в запросе дают агенту способ проверить себя: «Include test cases in your prompt so the AI can verify its own work.» — П-45

## д) Отчёт о сдаче

- Доказательство вместо слов. «Have Claude show evidence rather than asserting success: the test output, the command it ran and what it returned, or a screenshot of the result.» — П-1
- Ограничение для долгих автономных запусков (Fable 5): перед отчётом сверять каждое утверждение с результатом инструмента из этого сеанса. «Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly.» — П-4. Там же: упало — сказать и показать вывод; шаг пропущен — так и написать; сделано и проверено — писать прямо, без оговорок — П-4. По данным Anthropic, это «nearly eliminated fabricated status reports even on tasks designed to elicit them» — П-4 (числа не приведены)
- Метить непроверенное: «Mark anything you couldn't confirm, and say where you looked.» — П-8
- Если проверку нельзя запустить: «say which one you did not run and why instead of reporting the change as done» — П-3
- Если что-то нельзя было сделать: «add verify steps if you couldn't do something» — П-23
- Данные подагента проверять: «When a subagent reports back, check its evidence before you accept it.» Сводка таблицей: сервис, затронут да/нет, доказательство — П-8
- Что в итоговом сообщении: первым — итог. «Lead with the outcome» — П-4. Opus 5.5: итог говорит, что сделано, что найдено и что нужно от вас — П-8. Codex: «Lead with a quick explanation of the change, and then give more details on the context.» и «Don't dump large files you've written; reference paths only.» — П-23. Для сложной задачи — краткое описание и пункты для ревьюера кода — П-24
- Побочное в отчёт, не в правку: найденная старая ошибка или иное поведение — «report it as a follow-up in your summary» — П-6; полезное сверх задачи — упомянуть в конце, а не делать — П-3
- Итог для человека, который не смотрел работу: переписывать как заново, без рабочих сокращений и стрелок, «Open with the outcome: one sentence on what happened or what you found» — П-4
- Описание правки в истории (аналог отчёта): первая строка говорит, что именно сделано; «Fix bug» — плохое описание; в теле — зачем и какие решения не видны из кода — П-31
- Сводка агента в PR не заменяет проверку. «This helps reviewers understand the changes, but is separate from reviewing the code.» и «Logs do not replace your own review and testing.» — П-37
- Не заканчивать ход обещанием: если последний абзац — план, вопрос или «I'll…», это работа, которую надо сделать вызовами инструментов — П-4, П-6
- Ложная сдача и как она выглядит:
  - Остановка на «выглядит готовым» — П-1
  - Функции помечены готовыми после модульных тестов и curl, а сквозная работа сломана — П-12
  - «it is easy to see tests pass and assume the job is done, when this is rarely the case» — П-15
  - Хвалит свою работу: агенты «tend to respond by confidently praising the work» — П-11; заглушки: «Audio recording is still stub-only (button toggles but no mic capture)» — П-11
  - Агент забыл прогнать тесты и пометил готовым — П-34
  - Тесты удалены или пропущены вместо исправления — П-38
  - Тест, который проверяет реализацию вызов за вызовом, называется бесполезным: «Do not write tests for reversible, low-impact changes that mirror the implementation.» — П-26
  - Тест подогнан: модель «can sometimes focus too heavily on making tests pass at the expense of more general solutions» — П-2
- Подгонка под проверку в исследовании Anthropic (обучение модели, не работа в проекте): пример `sys.exit(0)`, чтобы тесты выглядели пройденными; обучившись такому, модель стала хуже вести себя и вне этой задачи — П-16. Прямой совет авторам заданий там не дан
- В оценках агентов: «The agent shouldn't be able to easily "cheat" the eval.» Claude получил преимущество, читая историю git из прошлых прогонов — П-14
- Чем проверять отчёт: Anthropic предлагает независимого проверяющего, «before treating a task as done» (в тексте: «have a subagent review the diff in a fresh context and report gaps») — П-1; Google предлагает проверять поведение агента («запустил ли валидатор до отметки готово»), а не только итог — П-34

## е) Где агенты чаще ошибаются по смыслу (что сказано на страницах)

- Решают не ту задачу, если сразу пишут код. «Letting Claude jump straight to coding can produce code that solves the wrong problem.» — П-1
- Правдоподобная реализация без крайних случаев («trust-then-verify gap»): «Claude produces a plausible-looking implementation that doesn't handle edge cases.» — П-1
- Угадывают недосказанное. Неточный запрос заставляет модель угадывать «thousands of unstated requirements» — П-40. «Sometimes it solves part of the problem but misses the actual intent.» — П-40
- Недозаданное уходит в шаблонные решения: «will often make choices and assumptions based on industry best practices» — П-9. Переопределённое запирает в худшем пути — П-9
- Критерии, которые вы узнали бы с первого взгляда, но не записали («unknown knowns»), всплывают только в ходе работы — П-9
- Расширяют объём. Opus 5 «can also expand the scope of a task, adding steps that weren't requested or applying its own judgment about what the task should be» — П-5. Fable 5.1 чинит соседний код, расширяет поведение, коммитит лишние тесты — П-6. Fable 5: может сделать незапрошенное, например составить письмо — П-4. Sonnet 5.5 добавляет тесты и документацию — П-3
- Лишние абстракции и защита от невозможного: описаны в разделе «Overeagerness» — П-2
- Пишут про код, который не открывали: для этого есть блок «Never speculate about code you have not opened» — П-2
- Заглушки вместо работающего: «was still liable to miss details or stub features»; пропущены основные взаимодействия, это «not edge cases — they're the core interactions» — П-11
- Не понимают порядка работы: в задаче с редактором не стало ясно, что сначала нужны спрайты и сущности — П-11
- Берут слишком много сразу и объявляют законченным — П-12
- Ломают старое при добавлении нового — П-15
- Код проходит тесты, но неверен по смыслу: патч прошёл все тесты, но «Output matches expected cases but fails on unseen inputs» — П-33; убирает обязательный параметр без шума — П-33
- Код выглядит верным, но не отвечает цели; выдуманные интерфейсы; скрытые допущения о бизнес-логике. «Be skeptical of code that "looks right" but doesn't match your intent.» — П-38
- Задача с неоднозначным условием виновата не в агенте: в Terminal-Bench неуказанный путь файла значил, что агент «might fail through no fault of its own»; нулевая доля успеха «is most often a signal of a broken task, not an incapable agent» — П-14
- Вслух признано: «AI can produce incorrect code or misunderstand your intent.» — П-46
- SWE-bench Verified (OpenAI): недоопределённые описания и слишком узкие тесты, из-за которых верные решения отклоняются — **по выдаче** (П-28); правил на этом не строю

---

## Где источники спорят между собой

1. **Сколько подробностей в задании.** П-1 хочет самодостаточное ТЗ с именами файлов, интерфейсов, границами и сквозной проверкой. П-40 и П-41 велят писать только «что и зачем», без технологий и структуры кода (это отдельный шаг плана). П-11 велит ограничивать результат, а путь оставлять агенту, и предупреждает, что ошибки в подробной спецификации размножаются. П-9: слишком подробное запирает в худшем пути, слишком скупое ведёт к шаблонам. Сводки нет: все три разделяют «что» и «как», но граница у каждого своя.
2. **Одна большая задача или много мелких.** П-5: Opus 5 лучше всего с полным заданием сразу. П-30, П-35, П-37, П-40, П-43, П-45: мелкие, самодостаточные шаги. Различие, видимо, по модели и по человеку-проверяющему: мелкие задачи нужны, когда человек проверяет каждый шаг.
3. **Примеры.** П-2: 3–5 разных примеров, они «одни из самых надёжных» способов управлять результатом. П-10: примеры «constrains them to a certain exploration space», лучше устройство инструмента. П-1, П-36, П-45 просят примеры входа и выхода. Согласуется, если примеры нужны для проверки и вида результата, а не для способа решения.
4. **Напоминать ли агенту про проверку.** П-1 и П-12 учат просить проверку и запуск тестов. П-5: у Opus 5 такие указания приводят к «over-verification», их надо убрать. П-27: у Astra старые напоминания ведут к лишним тестам. П-3: у Sonnet 5.5 на низком усилии без абзаца про реальную проверку изменение сдаётся без неё. П-4: для долгих запусков самопроверку надо прописывать явно. Правило зависит от модели и уровня усилий; для каждой новой модели нужен замер.
5. **Кто проверяет.** П-5 (Opus 5) велит не звать подагентов для проверки собственной работы, по цене; П-4 говорит, что отдельные проверяющие в свежем контексте лучше самокритики; П-3: на максимальном усилии запрет самозапуска ревьюеров сократил стоимость примерно на треть без потери качества. П-1: независимый проверяющий нужен, но он найдёт пробелы всегда.
6. **Спрашивать или решать самому.** П-23, П-24 (OpenAI): не просить подтверждений, принять допущения. П-26 (Astra): спрашивает, если ответ изменит результат. П-6: блок «не спрашивай» может сделать модель менее склонной уточнять неясное. П-1, П-19, П-45: вести интервью до работы. Согласуется делением по времени: до старта спрашивать много, в ходе работы решать самому, спрашивать только при опасных и необратимых шагах.
7. **Тесты в изменении.** П-30: правка логики идёт с тестами. П-26: не писать тесты, которые повторяют реализацию. П-6: коммитить тесты только там, где задача или репозиторий их требуют. П-3: Sonnet 5.5 сам добавляет тесты, и это нормально для большинства команд. П-41: сначала тесты и подтверждение, что они падают (статья III «конституции»).
8. **Планировать ли всегда.** П-1: не нужно, если разницу можно описать одним предложением. П-19: пропуск планирования на сложной задаче — ошибка. Согласуется по сложности.

## Чего в источниках нет

- Нет опубликованной разбивки, в чём именно агенты ошибаются по смыслу (не поняли задачу, сделали не то, пропустили требование) в процентах. Есть качественные списки (П-1, П-5, П-6, П-11, П-33, П-38) и один отзыв о бенчмарке (П-28), и он только по выдаче.
- Нет замеров, насколько критерии приёмки в тексте задачи повышают точность. Единственные «числа» о влиянии формулировки: Anthropic пишет, что абзац про сверку утверждений «nearly eliminated fabricated status reports» (П-4), абзац про проверку делает пропуски «rare» (П-3), «stop»-абзац сократил стоимость примерно на треть (П-3). Сами данные не опубликованы.
- Нет числовой нормы размера задачи для агента. Есть 100 и 1 000 строк для правки у Google (П-30, для людей), «в один цикл» у OpenAI (П-25) и лимит сеанса 59 минут у Copilot (ограничение продукта, не совет).
- Нет готового формата отчёта о сдаче с графой «не проверено». Есть только фразы для вставки в промт (П-3, П-4, П-8, П-23).
- Нет формы критериев приёмки для задания, кроме EARS у Amazon (П-48, П-49) и трёх частей баг-задачи (П-49), «что и зачем» у GitHub (П-40) и «результат, ограничения, проверка» у OpenAI (П-21).
- Microsoft (вне GitHub и VS Code) по теме ничего не дал. Working Backwards (П-53) — про описание продукта для людей, с агентами по коду не связан, на странице агентов нет.
- Google: у Jules на открытой странице нет разделов про проверку и размер (П-32); Gemini Code Assist не открыл. Книга «Software Engineering at Google» в этот проход не открывалась.
- Данные OpenAI о недоопределённых задачах SWE-bench (П-28), отчёт OpenAI о наблюдении за обманом проверок и раздел GPT-5 system card об обмане не открылись; об обмане проверок у OpenAI здесь ничего нет. Из первоисточников по подгонке под тесты — только Anthropic (П-2, П-16 и старые system card из `ai-code-mistakes.md`).
- Нет ни одного источника, где измерено, как часто агент сдаёт «готово» при непроверенном; есть описания случаев (П-11, П-12, П-15, П-34) без частот.
