# Основание справок тим лида

Источники и таблицы «основание правил» справок `references/process/`. Из самих справок убраны 16.10.2026 по слову
Владельца: справку читает тим лид в работе, источники ему не нужны. Здесь — для того, кто правит набор.

## `acceptance.md`

- Anthropic, «Best practices for Claude Code»: доказательство, а не утверждение; работа останавливается, когда
  выглядит готовой. https://code.claude.com/docs/en/best-practices
- Anthropic, «Effective harnesses for long-running agents»: агент объявляет победу рано.
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- METR, «Recent Frontier Models Are Reward Hacking», 2025: подмена проверок, запрет в тексте почти не помогает.
  https://metr.org/blog/2025-06-05-recent-reward-hacking
- Google Engineering Practices, «The Standard of Code Review».
  https://google.github.io/eng-practices/review/reviewer/standard.html
- «Where Do AI Coding Agents Fail?», arXiv 2601.15195: упавшая проверка — главный признак отказа.
  https://arxiv.org/html/2601.15195v1
- Пропуски приёмки в нашем проекте, 01.09–16.10.2026, проба роя тестировщиков и проба скила тим лида 16.10.2026.

Основание правил:

| Правило | Основание |
|---|---|
| 1, 5 | Источник и наш замер |
| 2, 3, 4, 9 | Наш замер и проба |
| 6 | Наш замер и проба |
| 7 | Источник и наш замер |
| 8 | Старый регламент |

## `handoff.md`

- Anthropic, «Prompting Claude Fable 5», раздел «Ground progress claims»: каждое заявление — по выводу
  инструмента. https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- Anthropic, «Best practices for Claude Code»: показывать доказательство, а не утверждать; правдоподобный код
  без краёв. https://code.claude.com/docs/en/best-practices
- Anthropic, «Prompting Claude Fable 5.1»: неясное — по самому прямому прочтению, допущение в итоге.
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
- Google Developers Blog, «Meet Jules' sharpest critic»: выход верен на примерах и ломается на новых входах.
  https://developers.googleblog.com/meet-jules-sharpest-critic-and-most-valuable-ally/

Основание правил:

| Правило | Основание |
|---|---|
| 1, 4 | Источник и наш замер |
| 2 | Только наш замер: виды краёв взяты из возвратов |
| 3 | Источник, замер подтверждает частоту |

## `plan.md`

- Work breakdown structure, правило 100 % (по PMI Practice Standard for WBS).
  https://en.wikipedia.org/wiki/Work_breakdown_structure
- METR, «Measuring AI Ability to Complete Long Tasks», 2025: успех падает с длиной задачи.
  https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
- SmartBear, «Best Practices for Code Review»: за 400 строк ревью находит меньше. Это материал вендора.
  https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/
- Anthropic, «Building effective agents»: агент получает «землю» от среды на каждом шаге.
  https://www.anthropic.com/engineering/building-effective-agents
- Пропуски приёмки в нашем проекте, 01.09–16.10.2026: 43 случая.

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Источник и наш замер |
| 2 | Источник и наш замер |
| 3, 4 | Наш замер |
| 5 | Только поправки владельца |

## `reply.md`

- Поправки владельца тим лиду, 19.08–16.10.2026, классы 4, 6, 7, 11, 15.
- Опись старых правил, `docs/rules-inventory.md`, Ж6, Ж7, З1–З3.

Основание правил: все — наш замер и слово владельца.

## `request.md`

- Anthropic, «How we built our multi-agent research system»: расплывчатое поручение — двойная работа и уход не
  туда. https://www.anthropic.com/engineering/multi-agent-research-system
- Scrum Guide 2020: работа начинается с цели продукта. https://scrumguides.org/scrum-guide.html
- Поправки владельца тим лиду, 19.08–16.10.2026, классы 1, 2, 8, 13.

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Источник и наш замер |
| 2, 3 | Только наш замер |
| 4 | Наш замер и скил продакта |

## `return.md`

- Google Engineering Practices, «The Standard of Code Review»: необязательное замечание помечается, приёмку оно
  не держит. https://google.github.io/eng-practices/review/reviewer/standard.html
- Anthropic, «Best practices for Claude Code»: две неудачные поправки — чистый контекст и точнее задача.
  https://code.claude.com/docs/en/best-practices
- Наш замер возвратов, `docs/measure-returns.md`; опись старых правил, `docs/rules-inventory.md`, Е4–Е6, Е11.

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Источник и наш замер |
| 2 | Источник |
| 3 | Наш замер и слово владельца |

## `reviewer.md`

- Cihan и др., «Evaluating Large Language Models for Code Review», 2025. https://arxiv.org/pdf/2505.20206
- Lin и др., «Is Agentic Code Review Helpful?», arXiv 2607.03316, 2026. https://arxiv.org/abs/2607.03316
- Anthropic, «Best practices for Claude Code»: ревьюер найдёт пробелы и в хорошей работе; просить только то, что
  влияет на корректность и требования. https://code.claude.com/docs/en/best-practices
- Наш замер расхода, 14–20.09.2026.

Основание правил:

| Правило | Основание |
|---|---|
| 1, 2 | Источник |
| 3 | Наш замер |

## `root-cause.md`

- Google SRE Book, «Postmortem Culture: Learning from Failure»: поводы заранее, разбор без вины.
  https://sre.google/sre-book/postmortem-culture/
- Atlassian, «Incident management handbook»: формулировка действия после разбора.
  https://pages.eml.atlassian.com/rs/594-ATC-127/images/Atlassian-incident-management-handbook-.pdf
- Five whys: метод и его слабые места — остановка на симптоме, одна причина вместо нескольких.
  https://en.wikipedia.org/wiki/Five_whys
- ISO 9001, п. 10.2, в пересказе Advisera: проверка эффективности действия.
  https://advisera.com/blog/2021/07/19/complete-guide-to-corrective-action-vs-preventive-action/
- Поправки владельца тим лиду, 19.08–16.10.2026.

Основание правил:

| Правило | Основание |
|---|---|
| 1, 2 | Источник |
| 3 | Источник и наш замер |
| 4 | Источник |

## `spec.md`

Правило 1, источники: Источники говорят то же. GitHub Spec Kit пишет план с деревом папок до задач, и в каждой задаче есть путь к
файлу. Anthropic советует для крупной фичи сначала написать спецификацию, а код писать в новой сессии. Kubernetes,
Kafka, VS Code и cal.com держат границы в файле правил, который читает проверка; Shopify и Spring Modulith
гоняют её на каждом слиянии. У n8n — счётчик старых нарушений, который не может расти.

Правило 4, источники: Sentry, Mattermost и Grafana держат файл последней миграции; Discourse и Mattermost удаляют в два
этапа. Раздел «что менять, когда добавляешь» у Sentry есть в `src/AGENTS.md`: «добавляю эндпоинт → эти файлы».

- GitHub, Spec Kit: конституция, spec, plan с деревом папок, tasks с путями, проверка analyze, метка неясности.
  https://github.com/github/spec-kit
- AWS, Kiro: requirements, design, tasks; постоянные файлы tech.md и structure.md. https://kiro.dev/docs/specs/
- Anthropic, «Best practices for Claude Code»: спецификация до кода, файлы и интерфейсы в ней, план не нужен
  для правки в одну фразу. https://code.claude.com/docs/en/best-practices
- Anthropic, «Effective harnesses for long-running agents»: агент-инициализатор, список фич, файл хода работы.
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Microsoft, Well-Architected: Architecture Decision Record, журнал только дописыванием.
  https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
- AWS Prescriptive Guidance, ADR process.
  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html
- MADR — шаблон записи решения (MIT или CC0); Michael Nygard, «Documenting Architecture Decisions», 2011:
  номер не используется повторно. https://adr.github.io/madr/,
  https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Границы в файле правил и проверка на каждом слиянии: Kubernetes `.import-restrictions`, Kafka
  `checkstyle/import-control-*.xml`, n8n `.boundaries-baseline.json` (счётчик), Spring Modulith `verify()`.
  https://github.com/kubernetes/kubernetes, https://github.com/apache/kafka, https://github.com/n8n-io/n8n,
  https://github.com/spring-projects/spring-modulith
- Файл последней миграции: Sentry `migrations_lockfile.txt`, Mattermost `migrations.list`, Grafana
  `migration_ids.txt`. https://github.com/getsentry/sentry, https://github.com/mattermost/mattermost,
  https://github.com/grafana/grafana
- Подборки с выдержками — `docs/research/team-lead/spec.md` и `docs/research/structure/` (сводка — `README.md`).
- Замер потерь проекта-донора без спецификации, 19.08–16.10.2026: 17 случаев, около 25 возвратов из 78 по
  структуре. Лежит вне репозитория: в нём данные проекта.

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Источник и наш замер; проверка на каждой сдаче — источник |
| 2, 3, 4 | Наш замер и источник; строка «Как делим папки» по умолчанию — слово владельца, 16.10.2026 |
| 5 | Наш замер |
| 6 | Источник |
| 7 | Источник и наш замер (грубый) |
| 8 | Источник и наш замер |
| 10 | Источник и проба `docs/probes/team-lead/diagram.md`; сам шаг — слово владельца, 18.10.2026 |
| Сам шаг | Слово владельца, 16.10.2026 |

Правило 10, источники:
- C4 model, Simon Brown, «Container diagram» и «Notation»: схема контейнеров показывает части, которые
  запускаются отдельно, и как они общаются. Каждая линия однонаправленная и подписана, между контейнерами — с
  технологией или протоколом. У схемы заголовок с видом и охватом. https://c4model.com/diagrams/container,
  https://c4model.com/diagrams/notation
- Microsoft, «Getting Started — Microsoft Threat Modeling Tool»: модель угроз начинается со схемы потоков данных,
  границы доверия на ней показывают, где кончается чужой контроль. На разборе схемы недостающую часть нашли за
  пять минут.
  https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started
- GitHub Blog, «Include diagrams in your Markdown files with Mermaid», 14.02.2022: блок `mermaid` GitHub рисует
  сам. https://github.blog/developer-skills/github/include-diagrams-markdown-files-mermaid/
- Mermaid, «C4 Diagrams»: синтаксис C4 помечен как пробный, может меняться, раскладкой управлять нельзя.
  Поэтому берём `flowchart`. https://mermaid.js.org/syntax/c4.html

## `task.md`

- Kiro (AWS), «Bugfix specs»: что не должно измениться — отдельная часть задания.
  https://kiro.dev/docs/specs/bugfix-specs/
- Anthropic, «Prompting Claude Fable 5»: давать причину, а не только просьбу.
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- OpenAI, «GPT-5 prompting guide»: противоречия в запросе.
  https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide
- Anthropic, «Harness design for long-running application development»: ошибки подробной спецификации переходят
  в код. https://www.anthropic.com/engineering/harness-design-long-running-apps

Основание правил:

| Правило | Основание |
|---|---|
| 1 | Наш замер и опись, Ж1 и Ж8 |
| 2 | Источник и наш замер |
| 3, 4 | Только источник |
| 5 | Источник и наш замер, `docs/team-lead-synthesis.md` |
| 6 | Наш замер, `docs/team-lead-synthesis.md` |
| 7 | Источник и наш замер, `process/spec.md` |

Источник к правилу 5: Anthropic, «Effective harnesses for long-running agents».
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

## Добавлено 16.10.2026, после переноса

- Брошенный путь — `handoff.md` правило 5, `acceptance.md` правило 10, `spec.md` правило 8, `task.md` правило 7,
  раздел «Что отвергли и что не сработало» в `assets/decision-template.md`: слово владельца 16.10.2026 — «чтобы не
  ходить по кругу и любой мог понять, как пробовали». Форма записи — по мотивам MADR (Considered Options),
  https://adr.github.io/madr/ (MIT или CC0).
- `spec.md` правило 9 — сквозные сценарии, совместимость, риски и долг, владелец в шапке: сводка
  `docs/research/structure/README.md`, пункты 4, 5, 9, 10 (arc42 раздел 6 и 11, Rust RFC Drawbacks, KEP, PEP, Go
  compatibility); наш случай — старые записи при приёмке (`acceptance.md`, правило 9); включить — слово владельца
  16.10.2026.

## Добавлено 18.10.2026, со скилом бекенда

Справки исполнителя `start.md`, `rework.md`, `local-run.md`. Внешних источников нет: правила взяты из описи
(`docs/rules-inventory.md`) — там у каждого случай из «Рабочей».

| Справка | Правило | Строка описи |
|---|---|---|
| `start.md` | 1 модель | А6 |
| `start.md` | 2 рабочая копия и ветка | А1, А2, А3; память о занятой рабочей копии (TEAM_TASK_005, 07.10) |
| `start.md` | 3 что читать | А7 |
| `start.md` | 4 код по карте | К1; `spec.md`, правила 1 и 2 |
| `start.md` | 5 не обходить | Г8; правило открытости, вариант Г (`docs/structure.md`, раздел 12) |
| `start.md` | 6 только задача | Г7 |
| `start.md` | 7 после сжатия | А8 |
| `rework.md` | 1 класс ошибки | Д1 |
| `rework.md` | 2 сначала ветка | Г1 |
| `rework.md` | 3 та же ветка | Д2 |
| `rework.md` | 4 без «заодно» | Е4 со стороны исполнителя |
| `local-run.md` | 1 из своей копии | А11 |
| `local-run.md` | 2 порты | А9 |
| `local-run.md` | 3 учётка сама | А10 |
| `local-run.md` | 4 настоящий вход | `docs/measure-returns.md`: живой запрос нашёл 30 дефектов |
| `local-run.md` | 5 внешняя система | В7 |
| `local-run.md` | 6 проверка должна уметь упасть | В8 |
| `local-run.md` | 7 секреты по имени | И1 |
| `local-run.md` | 8 убрать за собой | А5 |

## Добавлено 19.10.2026, после пробы бекенда

`task.md`, правило 8 (модель): счёт моделей в заданиях проекта-донора — Sonnet 554, Opus 43, Fable 1, Haiku 0 (поле «Модель» всех заданий на 19.10.2026); старое правило — регламент донора, раздел «Выбор модели»; проба — `docs/probes/backend/README.md`. `handoff.md`: восьмой вопрос о краях и правило о несделанном пункте — та же проба. Имён и цен моделей в справке нет: они устаревают (опись, Ж4).

## Добавлено 19.10.2026, со скилом дизайнера

`task.md`, правило 9, и `acceptance.md`, правило 12: задачи дизайнера проекта-донора — пять задач, один возврат
(RG_TASK_017: образец вида не назван в версии задания, по которой шла работа; ширины; нет сверки с сайтом). Контраст
3,4:1 найден `scripts/design/check.py` на уже принятой выгрузке. Подробно — `docs/basis/design.md`.
`handoff.md`, правило 2, — после пробы фронтенда: ответы о краях разделом «Края», `scripts/handoff/check.py` их
считает (`docs/probes/frontend/README.md`).

## Добавлено 19.10.2026, правила владельца и ревьюер

`owner-rules.md`: решение владельца 19.10.2026 — правила, которые не годятся в скил (как ему писать, порядок
приёмки в его проектах), живут в двух файлах вне скилов: общем и продуктовом. Подкладывает их хук плагина
`hooks/hooks.json` → `scripts/lead/rules_context.py` на SessionStart, только в проекте с `kit.toml`. Предел в 40
строк и перенос выше — по опыту проекта-донора: решений больше ста тридцати, регламент читают выборочно.
`reviewer.md`, «Когда звать»: решение владельца 19.10.2026 в проекте-доноре — ревьюер только на доступ, миграции,
гонки и секреты, остальное тим лид принимает сам; причина — сроки. Прежняя формулировка «не звать, когда правка
мала» оставляла ревьюера по умолчанию.

## Добавлено 23.10.2026, сверка модели хуком

`start.md`, правило 1: просьба владельца 23.10.2026 — модель чата должна сама вставать по полю «Модель», а
выбор владельца посреди чата оставаться. Сменить модель своего чата не может ни хук, ни сам агент: хукам
Claude Code даёт только запомнить модель (SessionStart, PostModelSwitch) и остановить команду
(UserPromptExpansion); инструмент приложения `set_session_model` свой чат переключать отказывается. Поэтому
`scripts/handoff/model_gate.py` останавливает команду исполнителя с чужой моделью и пропускает повтор — это
нарочный выбор владельца. Источник: Claude Code, «Hooks reference», разделы PreModelSwitch, PostModelSwitch,
UserPromptExpansion, https://code.claude.com/docs/en/hooks
