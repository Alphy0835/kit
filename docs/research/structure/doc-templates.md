# Готовые шаблоны документации ПО и принципы её построения

Дата сбора: 16.10.2026. Звёзды и даты — по `gh api` в этот день. Всё прочитано из первоисточников: репозитории, сайты авторов,
документация компаний. Где источник не первичный, это написано рядом. Ничего не скачивалось и не клонировалось.

Зачем: проверить шаблон спецификации `assets/spec-template.md` и правила `references/process/spec.md` на готовых шаблонах и найти,
чего нам не хватает.

## 1. Главное

1. Шаблонов спецификации и дизайн-документов много, а общий скелет у них один: **контекст и мотивация → цели и не-цели →
   дизайн → альтернативы → риски → совместимость → проверка → нерешённое**. Он повторяется в 6–8 шаблонах из 10 (раздел 3).
2. Все зрелые процессы (Rust, Kubernetes, Python, Go, ADR у Microsoft и AWS) держат принятый документ **неизменным**:
   изменение — новый документ со ссылкой на старый. Это ровно наше правило 8.
3. У нас в шаблоне нет четырёх повторяющихся вещей: **рисков**, **совместимости**, **сквозных сценариев** (как запрос идёт
   через модули) и **способа проверить, что решение выполняется**. Подробности — в разделе 4.
4. Наши «Что менять, когда добавляешь» и «Словарь с колонками код/экран/заказчик» **ни в одном шаблоне нет**. Это наши
   находки из замера, источника у них нет. Это не плохо, но в правилах надо так и писать.
5. Лицензия решает, что можно брать целиком: **MADR** (MIT или CC0), **Spec Kit** (MIT), **Go proposals** (BSD-3), **PEP**
   (CC0), **Good Docs** (0BSD / MIT-0) — берём без ограничений. **arc42** и **Diátaxis** (CC BY-SA) — только идеи или с
   условием «делись так же». Сборник Джоэла Хендерсона — запрет на коммерческое использование для его собственных текстов.

## 2. Каталог

Формат: что это, автор, лицензия, ссылка, популярность, разделы шаблона.

### 2.1 Diátaxis — четыре вида документации

- Что: система, которая делит документацию на четыре вида по нужде читателя. Не шаблон страницы, а способ решать, что куда
  писать.
- Автор: Daniele Procida. Сайт https://diataxis.fr, исходники https://github.com/evildmp/diataxis-documentation-framework.
- Лицензия: CC BY-SA 4.0 (файл `LICENSE.rst` в репозитории). Обрати внимание: «делись так же».
- Популярность: 1256 звёзд репозитория. Сайт называет «сотни проектов документации» и приводит Cloudflare, Gatsby, Vonage.
  Число «сотни» взято с сайта, проверить его нечем.
- Виды (определения с сайта):
  - Руководство-урок (tutorial) — учит, делая; ведёт инструктор. Служит обучению.
  - Рецепт (how-to guide) — практические шаги для того, кто уже умеет. Служит цели в реальной работе.
  - Справочник (reference) — нейтральные факты, устроенные как сама вещь. Служит работе.
  - Объяснение (explanation) — контекст и «почему». Служит пониманию.
- Две оси: действие или знание; учёба или работа.
- Правило: виды не смешивать. В уроке — минимум объяснений, ссылка на глубину.
- Совет сайта: **не делить документацию на четыре раздела заранее и не создавать пустых**; улучшать по одной небольшой правке.
  Структура вырастает сама. «Руководство, а не план».
- Для нас: спецификация — это почти целиком «справочник» (факты о том, где что лежит) плюс кусочек «объяснения» (почему так).
  Писать в ней пошаговые инструкции (рецепт) и «как это работает для новичка» (урок) не надо, это другие документы.

### 2.2 The Good Docs Project — шаблоны документации

- Что: сообщество технических писателей, набор шаблонов с подсказками внутри. Шаблоны рассчитаны на открытые проекты.
- Автор: The Good Docs Project (сообщество). Основатель на странице не назван. Cameron Shorter и Alyssa Rock названы в списке
  шаблонов как ведущие базового шаблона.
- Где сейчас живёт: GitLab https://gitlab.com/tgdp/templates (лицензия MIT-0 по странице репозитория). Копия на GitHub
  https://github.com/thegooddocsproject/templates **заархивирована**, последний коммит 18.09.2022, 703 звезды, лицензия 0BSD
  («делай что хочешь, без указания автора»). Звёзд на GitLab не видно. Две копии могут расходиться: актуальная — GitLab.
- Состав на сайте https://www.thegooddocsproject.dev/template: 24 шаблона в наборах «core», «community», «misc»:
  - core: Concept, How-to, README, Reference, Release notes, Troubleshooting, Tutorial;
  - community: Bug report, Changelog, Code of Conduct (+ три записи об инцидентах), Contributing guide, Our team, README;
  - misc: API getting started, API reference, Contact support, Glossary, Installation guide, Quickstart, SDK Overview, Style
    guide, Terminology system, User personas.
- Разделы (по копии на GitHub):
  - Tutorial: Overview, Background, Before you begin, {Task name}, Summary, Next steps.
  - How-to: Overview, Before you start, Step-by-step guide (Step 1…N), See also.
  - Reference: Overview, {subset of reference entries}, Parameters.
  - Explanation: Overview, Glossary, Explanation Topic.
  - Базовый шаблон: метаданные (название, описание, версия, дата, лицензия, аудитория), открывающий абзац в 1–3 предложения
    («о чём документ и для кого»), подсказки в `{фигурных скобках}`, которые надо заменить или удалить.
- Идея, которая нам полезна: шаблон хранит подсказку рядом с местом; подсказки удаляются из готового документа. Типы
  документов — «задача / понятие / справочник» (в Diátaxis это почти то же).

### 2.3 arc42 — шаблон описания архитектуры

- Что: шаблон из 12 разделов для документа об архитектуре.
- Авторы: Gernot Starke и Peter Hruschka. Сайт https://docs.arc42.org, репозиторий https://github.com/arc42/arc42-template.
- Лицензия: CC BY-SA 4.0. Разрешено использовать и менять в том числе коммерчески, но производный текст — под той же лицензией.
- Популярность: 1310 звёзд, последний выпуск 2026.10.15.3 (свежий). На сайте — 145 советов, 35 примеров; список компаний не
  приведён. Организации сайт не называет.
- Разделы (файлы `EN/adoc/01…12`):
  1. Introduction and Goals — требования (кратко, со ссылкой), 3–5 целей по качеству, заинтересованные стороны.
  2. Architecture Constraints — технические и организационные ограничения.
  3. Context and Scope — деловой контекст, технический контекст (внешние системы и интерфейсы).
  4. Solution Strategy — основные решения и идеи.
  5. Building Block View — модули: общая схема (таблица «имя / ответственность»), далее уровни 2 и 3, интерфейсы.
  6. Runtime View — как модули работают в важных сценариях: шаги, сбои, запуск и остановка.
  7. Deployment View — серверы и развёртывание.
  8. Cross-cutting Concepts — повторяющиеся приёмы (безопасность, журнал, ошибки…).
  9. Architecture Decisions — значимые решения.
  10. Quality Requirements — качество, сценарии.
  11. Risks and Technical Debt.
  12. Glossary.
- Совет авторов: брать только нужное («путешествуй налегке»), но цели по качеству писать всегда.
- Связь с нами: разделы 2, 5, 8, 9, 12 у нас есть под другими названиями; 6, 10, 11 нет.

### 2.4 C4 model — схемы архитектуры

- Что: способ рисовать архитектуру на четырёх уровнях. Это не шаблон текста.
- Автор: Simon Brown. https://c4model.com. Лицензия сайта и примеров — CC BY 4.0.
- Уровни: 1 System context (система, пользователи, соседи); 2 Container (приложения и хранилища); 3 Component (крупные блоки
  внутри контейнера); 4 Code (классы, функции). Добавочные схемы: system landscape, dynamic, deployment.
- Не зависит от нотации и инструмента. Звёзд нет (это сайт). Инструменты: Structurizr DSL (отдельный проект, не проверял).
- Для нас: уровни 2 и 3 — это наша «Карта модулей»; уровень 4 нам не нужен (это код); уровень 1 — наша «Цель» плюс «Интерфейсы
  с внешними системами».

### 2.5 Шаблоны ADR (записи архитектурных решений)

Общая идея: одно решение — один короткий файл; принятый файл не правят; изменение — новый файл, у старого статус «заменён».

- **Michael Nygard, 2011** (первоисточник идеи): статья «Documenting Architecture Decisions»
  https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions. Разделы: Title, Status, Context, Decision,
  Consequences. Запись на 1–2 страницы, файл `doc/arch/adr-NNN.md`, номера по порядку и никогда не повторяются, отменённые
  решения хранятся с пометкой «заменено». Шаблон без явной лицензии; текст статьи — блог автора.
- **MADR** (Markdown Any Decision Records / Architectural): https://github.com/adr/madr, 2559 звёзд, версия 4.0.0, лицензия
  **MIT или CC0-1.0** (на выбор). Авторы — участники организации adr; шаблон ведёт сообщество. Четыре файла:
  - полный `adr-template.md`: метаданные (status, date, decision-makers, consulted, informed) → Context and Problem
    Statement → Decision Drivers → Considered Options → Decision Outcome (+ Consequences, + Confirmation) → Pros and Cons of the
    Options → More Information;
  - `adr-template-minimal.md`: Context and Problem Statement, Considered Options, Decision Outcome, Consequences;
  - те же два без пояснений (`bare`).
  - Новое в 4.0: раздел **Confirmation** — как проверить, что решение выполняется (тест, ревью, проверка границ).
  - Положить в `docs/decisions/`, имя `nnnn-title.md`.
- **joelparkerhenderson/architecture-decision-record**: https://github.com/joelparkerhenderson/architecture-decision-record,
  17 225 звёзд. Это сборник, не один шаблон: 11 шаблонов (Nygard, Tyree и Akerman, MADR, arc42, EdgeX, Alexandrian pattern,
  business case, Planguage, Gareth Morgan, GIG Cymru NHS Wales, «Important Technical Decisions») плюс примеры. Лицензия: свои
  тексты автора — **CC BY-NC-SA** (нельзя коммерчески), чужие шаблоны — под лицензиями их авторов. Не первоисточник для самих
  шаблонов: первоисточник — их авторы. Внутри есть скилы для Claude Code (`skills/architecture-decision-record-skill`), в
  них: когда ADR нужен, а когда нет, как называть файл. Лицензия скилов в репозитории не уточнена.
  - Шаблон Tyree и Akerman (IEEE Software): Issue, Decision, Status, Group, Assumptions, Constraints, Positions, Argument,
    Implications, Related decisions/requirements/artifacts/principles, Notes. Самый подробный из них.
- **Microsoft Well-Architected**: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record.
  ADR — журнал только дописыванием, принятое не правят; запись: проблема и контекст, рассмотренные варианты, итог (с
  компромиссами и **уровнем уверенности**), статус. Записывать только то, что меняет структуру, важные качества или трудно
  откатить. Лицензия страницы не указана.
- **AWS Prescriptive Guidance**: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html.
  Минимум: контекст, решение, последствия. Состояния Proposed → Accepted / Rejected → Superseded. Принятый ADR неизменяем.
  Что считать значимым: структура, нефункциональные требования, зависимости (связность модулей), интерфейсы, приёмы
  построения. При отказе записывать причину, «чтобы не спорить заново».

### 2.6 Дизайн-документы

- **Google.** Официально опубликованного шаблона дизайн-документа я не нашёл. Что есть:
  - «Software Engineering at Google», глава 10 «Documentation» (Tom Manshreck, ред. Riona MacNamara), бесплатно на
    https://abseil.io/resources/swe-book/html/ch10.html, лицензия CC BY-NC-ND 4.0 (нельзя менять, нельзя коммерчески). Это
    книга сотрудников Google, не стандарт компании. Виды: справочник, дизайн-документы, уроки, концептуальная
    документация, посадочные страницы. Дизайн-документы «обычно требуются до крупных проектов»: цели, стратегия реализации,
    главные решения с компромиссами и альтернативами. Правила: у документа одна цель, виды не смешивать; в первых абзацах —
    кто читает, о чём, когда обновлён, где лежит, зачем; документация как код (в системе версий рядом с кодом, у каждого
    владелец, ревью, замер свежести).
  - «Design Docs at Google», Malte Ubl, 06.07.2020, https://www.industrialempathy.com/posts/design-docs-at-google/. **Не
    первоисточник компании**: личный блог инженера Google. Сам автор пишет, что формата нет, а структура — то, что «закрепилось»:
    Context and scope («это не документ с требованиями») → Goals and non-goals → The actual design (обзор, схема системы, API,
    хранение данных, код редко) → Alternatives considered («один из важнейших разделов») → Cross-cutting concerns (безопасность,
    приватность, наблюдаемость). Объём 10–20 страниц для крупного, 1–3 для «мини». Писать, когда решение неочевидно; не писать,
    если это просто «инструкция по реализации».
- **Rust RFC**: https://github.com/rust-lang/rfcs, 6611 звёзд, лицензия Apache-2.0 или MIT. Шаблон `0000-template.md`:
  заголовок (Feature Name, Start Date, RFC PR, Rust Issue) → Summary → Motivation → Guide-level explanation («объясни, как будто
  уже готово») → Reference-level explanation → Drawbacks → Rationale and alternatives → Prior art → Unresolved questions →
  Future possibilities. Процесс нужен для «существенных» изменений; принятый RFC почти не меняют, правки только мелкие.
- **Kubernetes KEP**: https://github.com/kubernetes/enhancements, 3965 звёзд, Apache-2.0. Шаблон
  `keps/NNNN-kep-template/README.md` + `kep.yaml` (авторы, владелец-SIG, статус provisional / implementable / implemented /
  deferred / rejected / withdrawn / replaced, этап alpha/beta/stable, `replaces`, `see-also`). Разделы: Release Signoff Checklist →
  Summary → Motivation (Goals, Non-Goals) → Proposal (User Stories, Notes/Constraints/Caveats, Risks and Mitigations) → Design
  Details (**Test Plan**, Graduation Criteria, Upgrade/Downgrade Strategy, Version Skew Strategy) → **Production Readiness Review**
  (включение и откат, мониторинг, зависимости, масштаб, поиск неисправностей) → Implementation History → Drawbacks →
  Alternatives → Infrastructure Needed. Самый тяжёлый шаблон; опросник готовности к выкладке сделан под Kubernetes.
  KEP нужны «для большинства нетривиальных изменений», процесс должен быть «достаточно лёгким, чтобы быть по умолчанию».
- **Python PEP 1 / PEP 12**: https://peps.python.org/pep-0001/, https://peps.python.org/pep-0012/; репозиторий
  https://github.com/python/peps (5027 звёзд). Лицензия PEP: общественное достояние или CC0-1.0. Шапка (PEP, Title, Author,
  Sponsor, Status, Type, Created, Requires, Replaces, Superseded-By, Resolution…) → Abstract (около 200 слов) → Motivation →
  Specification → Rationale → **Backwards Compatibility** → **Security Implications** → How to Teach This → Reference
  Implementation → Rejected Ideas → Open Issues → Acknowledgements → Footnotes → Change History → Copyright. PEP 1: после принятия
  PEP считается **историческим документом, а не живой спецификацией**; живое описание поддерживают отдельно (справочник языка).
  Мысль для нас: спецификация проекта должна быть живой, поэтому ей нужен владелец и правило «правка вместе с кодом»; решения из
  неё уходят в неизменяемые записи.
- **Go proposals**: https://github.com/golang/proposal, 3458 звёзд, BSD-3-Clause. Шаблон `design/TEMPLATE.md` (40 строк): Proposal
  (Author, Last updated, Discussion at) → Abstract → Background → Proposal → Rationale → Compatibility → Implementation → Open
  issues. Процесс: сначала короткая заявка в трекере; полноценный дизайн-документ только если на обсуждении так решили. Есть и
  отдельный шаблон для изменений языка. В папке `design` 136 файлов.
- **GitHub Spec Kit** (уже в нашем spec.md): https://github.com/github/spec-kit, MIT, GitHub API показал 141 545 звёзд (число
  необычно большое, но так отдал API). Шаблоны в `templates/`:
  - `constitution-template.md`: принципы проекта, ограничения, порядок изменений, версия.
  - `spec-template.md` (что и зачем, без технологий): User Scenarios & Testing (истории с приоритетами P1–P3, «независимая
    проверка», приёмочные сценарии, пограничные случаи) → Requirements (FR-001…, Key Entities) → Success Criteria (измеримые) →
    Assumptions. Неясное помечается `[NEEDS CLARIFICATION: …]` на месте.
  - `plan-template.md` (как): Summary → Technical Context (язык/версия, зависимости, хранилище, тесты, платформа, тип проекта,
    цели по скорости, ограничения, масштаб) → Constitution Check → Project Structure (дерево папок документов и кода) →
    Complexity Tracking (таблица «что усложнили / зачем / какую простую замену отвергли»). Рядом лежат `research.md`,
    `data-model.md`, `contracts/`, `quickstart.md`.
  - `tasks-template.md`: задачи по фазам Setup → Foundational (блокирует всё остальное) → истории → Polish; каждая задача с
    путём к файлу, метка `[P]` — можно параллельно.
- **AWS Kiro**: https://kiro.dev/docs/specs/. Три файла: `requirements.md` (истории, критерии приёмки; для багов
  `bugfix.md` — текущее, ожидаемое и неизменное поведение), `design.md` (архитектура, диаграммы последовательности, поток
  данных, обработка ошибок, стратегия тестов), `tasks.md`. Про постоянные файлы `tech.md`/`structure.md` страница спецификаций
  ничего не говорит; наш spec.md на них ссылается со страницы «Steering», которую в этом заходе я не открывал.

### 2.7 ARCHITECTURE.md

- Статья matklad (Aleksey Kladov), 06.02.2021, https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html. Первоисточник идеи
  (блог автора). Для проектов примерно от 10 до 200 тысяч строк, лежит рядом с README и CONTRIBUTING.
- Советы: коротко, писать только то, что редко меняется, не пытаться держать в синхроне с кодом, пересматривать пару раз в год.
  Элементы: **обзор «с высоты птичьего полёта»** (какую задачу решает проект) → **карта кода** (крупные модули и связи: «где
  лежит то, что делает X», «что делает то, на что я смотрю») → **имена, а не ссылки** (ссылки протухают; читатель найдёт по
  поиску символа) → **инварианты** (особенно «чего нет»: модель не зависит от представления) → **границы** между слоями и
  системами → **сквозные вопросы** отдельным разделом.
- Пример: `rust-analyzer`, https://github.com/rust-lang/rust-analyzer (16 910 звёзд, Apache-2.0), файл
  `docs/book/src/contributing/architecture.md`. Разделы: Bird's Eye View → Entry Points → Code Map (по папкам и крейтам) →
  Cross-Cutting Concerns (Stability Guarantees, Code generation, Cancellation, Testing, Performance Testing, Error Handling,
  Observability, Configurability, Serialization).
- Расхождение с нами: matklad советует не давать ссылок на файлы, у нас `spec_check.py` проверяет, что путь есть в репозитории.
  Наш подход держится на скрипте: протухший путь скрипт поймает. Это нормально, но стоит помнить: список путей надо держать на
  уровне папок, не файлов.

### 2.8 Руководства по стилю — только про структуру

- **Google developer documentation style guide**: https://developers.google.com/style. Текст CC BY 4.0, примеры кода Apache-2.0.
  - Заголовки: регистр как в предложении; один h1; уровни не пропускать; под заголовком сразу текст, не заголовок под
    заголовком; задачи — инфинитив («Передать данные»), понятия — существительное; без номеров и ссылок в заголовках.
  - Процедуры: нумерованные шаги, **одно действие на шаг**, вводное предложение, результат отдельным абзацем, предварительные
    условия до задачи, необязательный шаг с пометкой «Optional:», цель перед действием, один лучший способ, а не три; один шаг —
    маркированный пункт, не список.
  - Наш рунбук (D-116, ASD-STE100) уже делает то же самое. Совпадение независимое — хороший знак.
- **Microsoft Writing Style Guide**: https://learn.microsoft.com/en-us/style-guide/welcome/. Лицензия двусмысленна: репозиторий
  `MicrosoftDocs/microsoft-style-guide` — CC BY 4.0 (192 звезды, заархивирован с ноября 2024), а на сайте написано «All rights
  reserved». Копировать текст не стоит. По структуре: «лучшая инструкция — та, что не нужна»; если нужна — картинка, видео,
  одно предложение или нумерованная процедура. Шаблонов статей в открытом репозитории `MicrosoftDocs/contribute` я не нашёл.

### 2.9 Docs-as-code (Write the Docs)

- https://www.writethedocs.org/guide/docs-as-code/ . Авторы: Eric Holscher и сообщество Write the Docs. Лицензия CC BY-NC-SA 4.0.
- Суть: документация живёт теми же инструментами, что и код: система версий, текстовая разметка (Markdown, reStructuredText,
  AsciiDoc), трекер задач, ревью, автоматические проверки. Можно блокировать слияние функции без документации. Из той же
  мысли в книге Google: владелец у каждого документа, замер свежести.
- Для нас: наш `spec_check.py` — это и есть «автоматические проверки документации»; правило 8 «меняешь в той же ветке» — это
  «блокировать слияние без документации».

### 2.10 Файлы сообщества GitHub

- Какие файлы GitHub понимает как «файлы здоровья сообщества» (https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file):
  README, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, SUPPORT.md, ACCESSIBILITY.md, FUNDING.yml, шаблоны задач и запросов
  на слияние, форма сообщения об уязвимости. Лицензию нельзя вынести в общий файл — только в каждый репозиторий.
- README по GitHub: зачем проект, чем полезен, как начать, где помощь, кто ведёт. Шаблонов самих файлов GitHub не даёт. Это
  документация сайта github/docs (21 026 звёзд, CC BY 4.0), не шаблон. Шаблоны README, CONTRIBUTING, Code of Conduct, Bug report
  есть у Good Docs (2.2).

## 3. Что повторяется в трёх шаблонах и больше (главный итог)

Обозначения: Р = Rust RFC, K = KEP, P = PEP, G = Go, U = Ubl (блог инженера Google), A = arc42, M = MADR и Nygard,
S = Spec Kit (spec и plan), D = Kiro (requirements и design), W = ARCHITECTURE.md (matklad и rust-analyzer). Всего 10 источников.
Сравнивал названия и смысл разделов, не слова.

| Раздел | Где есть | Сколько |
|---|---|---|
| Контекст, мотивация, проблема (зачем это) | Р Motivation, K Motivation, P Motivation, G Background, U Context and scope, A 1 и 3, M Context, S User Scenarios, D requirements | 9 из 10 |
| Сводка в 1 абзац (Summary, Abstract) | Р, K, P, G, S plan, W Bird's eye | 6 |
| Цели и не-цели (границы) | K Goals / Non-Goals, U Goals and non-goals, A 1 (цели качества) и 2, S Assumptions (что вне), Р Unresolved (вне объёма) | 5 (явные «не-цели» только K, U) |
| Сам дизайн, подробности | Р Reference-level, K Design Details, P Specification, G Proposal, U The actual design, A 5–7, S plan, D design.md | 8 |
| Альтернативы и почему отвергнуты | Р Rationale and alternatives, K Alternatives, P Rationale и Rejected Ideas, G Rationale, U Alternatives considered, A 9, M Considered Options, S Complexity Tracking | 8 |
| Риски, недостатки, последствия | Р Drawbacks, K Drawbacks и Risks and Mitigations, A 11, M Consequences, S Complexity Tracking | 5 |
| Совместимость и миграция | P Backwards Compatibility, G Compatibility, K Upgrade/Downgrade и Version Skew, Р (миграция в Guide-level) | 4 |
| Как проверить, тесты | K Test Plan, S Independent Test и приёмочные сценарии, M Confirmation (MADR 4), A 10, D design.md Testing, W Testing, P (тесты в реализации) | 6 |
| Нерешённое | Р Unresolved questions, P Open Issues, G Open issues, S NEEDS CLARIFICATION | 4 |
| Сквозные вопросы (безопасность, наблюдаемость, ошибки) | U Cross-cutting concerns, A 8, W Cross-Cutting Concerns, P Security Implications, K Production Readiness Review (мониторинг, масштаб), D Error handling | 6 |
| Карта модулей, структура | A 5 Building Block, W Code Map, S Project Structure, C4 уровни 2–3, Kiro structure.md | 5 |
| Данные, сущности | S Key Entities и data-model.md, U Data storage, A 8 (доменная модель), D design.md | 4 |
| Ограничения и стек | A 2, S Technical Context, U (нет), Kiro tech.md | 3 |
| Статус и метаданные шапки (владелец, дата, замена) | Р, K (kep.yaml), P (шапка), G, M Status, S | 6 |
| Реализация, этапы, история | G Implementation, K Implementation History и Graduation, P Reference Implementation и Change History, S tasks | 4 |
| Примеры использования, истории | Р Motivation (случаи), K User Stories, S User Stories, D requirements | 4 |
| Сквозные сценарии, порядок работы системы | A 6 Runtime View, U схема системы, D sequence diagrams, S quickstart.md | 4 |
| Глоссарий | A 12, Good Docs Glossary | 2 (ниже порога) |
| Заметка «когда не нужно писать» | U («не пиши, если это инструкция»), K (FAQ), Р («существенные»), G, наш spec.md | 4 |

Чего нет ни в одном (наше): «Что менять, когда добавляешь», колонки код/экран/заказчик в словаре, виды идентификаторов.

## 4. Что брать в наш набор

Сверка с `assets/spec-template.md` (разделы: Цель и вне объёма, Стек, Карта модулей, Данные, Словарь, Интерфейсы, Что менять
когда добавляешь, Сквозное, Проверка, Решения, Не определено).

1. **Добавить раздел «Риски и долг»** (одна таблица: риск, что будет, что делаем). Есть в Rust (Drawbacks), KEP (Risks and
   Mitigations), arc42 11, в ADR («Consequences»). У нас нет. Кроме того, это даёт место для известных дыр («циклы остались»).
   Источники: https://github.com/rust-lang/rfcs/blob/master/0000-template.md, arc42 `EN/adoc/11_technical_risks.adoc`.
2. **Добавить раздел «Совместимость: что нельзя сломать»**. Есть в PEP (Backwards Compatibility, без него «могут отклонить»), Go
   (Compatibility), KEP (Upgrade/Downgrade). У нас такой нужды хватает: старый путь живёт, пока по нему идут клиенты, коннекторы
   работают параллельно. Источники: https://peps.python.org/pep-0001/, https://github.com/golang/proposal/blob/master/design/TEMPLATE.md.
3. **Добавить «Сквозные сценарии»** (1–3 пути данных через модули по шагам, с местом сбоя). Это arc42 раздел 6 «Runtime View» и
   схема системы у Ubl. Сейчас у нас модули и интерфейсы описаны по отдельности, а путь через них нигде не виден.
   Источники: https://github.com/arc42/arc42-template/blob/master/EN/adoc/06_runtime_view.adoc,
   https://www.industrialempathy.com/posts/design-docs-at-google/.
4. **Решения: перенести в отдельные неизменяемые записи, а в спецификации оставить таблицу ссылок.** Сейчас таблица «Решения» в
   самой спецификации правится на месте, что спорит с нашим правилом 8. Nygard, Microsoft, AWS, MADR: одно решение — один файл
   `NNNN-название.md`, номер не используется повторно, у замены статус «заменено №…». Взять MADR как есть (MIT или CC0). Колонку
   «Что отвергли» оставить: это MADR «Considered Options». Источники: https://github.com/adr/madr/tree/main/template,
   https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions,
   https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html.
5. **В запись решения добавить два поля: «Подтверждение» и «Уверенность».** «Подтверждение» (MADR 4, Confirmation) — как
   проверить, что решение выполняется; у нас это `тест границ`, и его надо назвать там, где решение принято. «Уверенность»
   (Microsoft) — пометка, что решение принято со слабой уверенностью, чтобы вернуться. Источники: MADR `adr-template.md`,
   https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record.
6. **Шапка спецификации: добавить владельца, дату и «заменяет / заменена»**. В Rust, KEP, PEP, Go, MADR шапка именно такая.
   У нас только «Статус» и «ТЗ продукта». Для живой спецификации владелец обязателен (книга Google: у каждого документа владелец и
   дата). Источники: kep.yaml https://github.com/kubernetes/enhancements/tree/master/keps/NNNN-kep-template,
   https://abseil.io/resources/swe-book/html/ch10.html.
7. **Метку «не определено» писать на месте, а не только в конце.** Spec Kit ставит `[NEEDS CLARIFICATION: …]` в строке, где пробел,
   и пока метка есть, план не идёт. У нас метка собирается в один раздел, и пробел в середине может потеряться. Оставить
   раздел как сводку, а метку ставить и на месте (скрипт и так считает). Источник:
   https://github.com/github/spec-kit/blob/main/templates/spec-template.md.
8. **Названия и оговорки, которые у нас уже совпадают с источниками, не трогать.** «Цель и вне объёма» = Goals/Non-goals (KEP,
   Ubl); «Карта модулей» = Building Block View (arc42) и Code Map (matklad); «Стек» = Technical Context (Spec Kit); «Сквозное» =
   Cross-cutting (Ubl, arc42, rust-analyzer); «Не определено» = Unresolved questions (Rust). Из `ARCHITECTURE.md` взять в «Карту
   модулей» строку «Инварианты: чего быть не должно» (например «модель не зависит от экрана»); у нас это сейчас спрятано в
   колонке «Кому можно вызывать». Источник: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html.
9. **Что у нас иначе и в правилах прямо написать «нашей находкой, источника нет»**: «Что менять, когда добавляешь», колонки
   код/экран/заказчик в «Словаре», виды идентификаторов. Ни в одном из 10 шаблонов их нет. В `references/process/spec.md` правила
   2–4 уже опираются на «наш замер», так что противоречия нет; нужно только, чтобы скрипт не принимал их за «общепринятое».
10. **Брать целиком готовые шаблоны под разрешающими лицензиями, в нужные папки набора**:
    - MADR minimal/полный (MIT или CC0) → `assets/adr-template.md` с русскими заголовками; перевод разрешён. Источник:
      https://github.com/adr/madr/tree/main/template.
    - Короткий шаблон Go (BSD-3, 40 строк) → образец «мини-спецификации» для малых правок, вместе со словами «сначала короткая
      заявка, документ только если попросили». Источник: https://github.com/golang/proposal/blob/master/design/TEMPLATE.md.
    - Good Docs: README, How-to, Troubleshooting, Release notes (0BSD / MIT-0) → `assets/docs/` как шаблоны документов для
      исполнителей, если понадобятся. Источник: https://gitlab.com/tgdp/templates (актуальная копия),
      https://github.com/thegooddocsproject/templates (заархивирована, 0BSD).
    - **Не копировать текст**: arc42 и Diátaxis (CC BY-SA: производный текст пришлось бы выпускать под той же лицензией),
      сборник Хендерсона (CC BY-NC-SA), Microsoft Style Guide (лицензия двусмысленна), книгу Google (CC BY-NC-ND). Структуру и идеи
      брать можно, они не защищены, но тексты — своими словами и со ссылкой.

Не брать: KEP целиком (опросник готовности под Kubernetes: кластер, версии, feature gates) и PEP целиком (правила публичного
обсуждения). Это процессы открытых проектов с сотнями участников. Из них брать только отдельные разделы (Test Plan, Risks,
Compatibility).

## 5. Чего я не проверил

- Google не публикует шаблон дизайн-документа. Я не нашёл его, но искал только через поиск и главу книги; полного перебора
  `google.github.io/eng-practices` не делал.
- Страницу Kiro про «Steering» (`tech.md`, `structure.md`) не открывал: страница спецификаций о них молчит. Наш spec.md на них
  ссылается; ссылку надо перепроверить.
- Структура Structurizr DSL, шаблоны Microsoft Learn для статей (в открытом репозитории их нет) и IEEE 29148 (платный
  стандарт требований) не смотрел.
- Звёзды Spec Kit (141 545) выглядят завышенными; так отдал `gh api`. Если число пойдёт в документ, сверить на странице.
- Число «сотни проектов» у Diátaxis — слова сайта, подтверждения нет.
