# Источники: как ведущие компании советуют писать скилы и работать с агентами

Собрано 13.10.2026 тим лидом по слову владельца. Первый проход — что есть и где лежит. Второй проход в тот же день —
ключевые источники дочитаны; выводы о том, как проектировать скилы, записаны в `../skill-design.md`.

Пометки в колонке «Прочитано»: **да** — открыл страницу и прочитал сам; **список** — видел только заголовок в
ленте компании; **пересказ** — сам источник не открылся, сведения из поисковой выдачи, перед опорой на него
нужно открыть оригинал.

## Главное за один экран

1. **Скил — уже общий стандарт, а не приём одной компании.** Формат «папка с `SKILL.md`» придумала Anthropic,
   теперь его читают Claude Code, Codex и ChatGPT, Gemini CLI и Antigravity, Grok Build, Cursor, Copilot и ещё
   около сорока продуктов. Описание стандарта и руководства — на `agentskills.io`.
2. **Свежие руководства Anthropic и OpenAI говорят одно: правил стало слишком много.** Anthropic убрала больше
   80 % системного промпта Claude Code для моделей пятого поколения без потери качества (24.07.2026). OpenAI про
   GPT-6 Astra: большая часть работы — удалить указания, написанные для слабых моделей. Жёсткие запреты,
   пошаговые маршруты и повторы теперь мешают: модель тратит силы на разбор противоречий.
3. **Что осталось ценным в скиле:** то, чего модель не узнает сама, — подводные камни проекта, свои соглашения,
   свои мнения. Очевидное вычёркивается проверкой «ошиблась бы модель без этой строки?».
4. **Описание скила решает, включится ли он.** Короткое, с главным случаем применения в начале, с границей «когда
   не применять». Его проверяют набором примерно из 20 запросов: половина должна включать скил, половина — нет,
   причём «нет» — близкие по словам, а не случайные.
5. **Скил проверяют замерами, а не на глаз.** У Anthropic, OpenAI и в стандарте — один порядок: сначала задачи
   и замер без скила, потом минимум текста, потом сравнение. Каждая ручная поправка агента становится тестом
   или строкой в разделе подводных камней.
6. **Скрипт внутри скила — для того, что должно выходить одинаково.** Это прямо про наши скринеры: проверка
   скриптом, а нейросеть читает только найденное.
7. **Скилы, написанные моделью «из головы», пользы не дают.** Исследование SkillsBench: скилы, собранные
   человеком, дают в среднем +16 пунктов успешности, сгенерированные моделью без материала — ноль.
   Стандарт советует то же: скил вырастает из сделанной задачи и своих документов, а не из общих знаний модели.

## Anthropic

### Руководства и документация

| Что | Дата | Прочитано | Суть |
|---|---|---|---|
| [The new rules of context engineering for Claude 5 generation models](https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/) | 24.07.2026 | да | Самое важное из свежего. Шесть пар «было → стало»: правила → суждение, примеры → устройство инструмента, всё сразу → подгрузка по мере надобности, повторы → короткие описания, память в `CLAUDE.md` → автопамять, простые планы → богатые образцы (код, макет, тесты, рубрики). Команда `/doctor` в Claude Code сама ужимает скилы и `CLAUDE.md` |
| [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | действующая | да | Главный справочник по написанию. Числа: имя до 64 знаков, описание до 1024, тело `SKILL.md` до 500 строк, ссылки на файлы — на один уровень вглубь, оглавление в файлах длиннее 100 строк. Три степени свободы указаний, цикл «проверил — исправил — повторил», чек-лист перед выпуском |
| [Getting the most out of Opus 5.5](https://claude.dev/blog/getting-the-most-out-of-opus-5-5/) | 22.09.2026 | да | Назвать, что значит «готово», и отпустить; убрать «думай внимательно»; в `CLAUDE.md` — когда останавливаться и когда нет; большую работу делить на субагентов с проверкой доказательств; просить помечать непроверенное |
| [Lessons from building Claude Code: How we use skills](https://claude.dev/blog/lessons-from-building-claude-code-how-we-use-skills/) | 03.06.2026 | да | Разбор нескольких сотен собственных скилов Anthropic. Девять типов скилов; лучшие попадают ровно в один. Приёмы: не писать очевидное, раздел подводных камней — самое ценное, скил — папка со скриптами, не вести модель по шагам, настройки в `config.json`, память скила в файле, хуки по требованию, замер использования хуком |
| [The Complete Guide to Building Skills for Claude](https://claude.com/resources/guides/the-complete-guide-to-building-skills-for-claude) | 2026 | да (5 глав из 6) | Руководство на 33 страницы. Начинать с 2–3 сценариев; цель — включение на 90 % уместных запросов; три вида тестов: включение, работа, сравнение с прогоном без скила; пять шаблонов построения; разбор поломок: не включается — править описание, не следует — короче и критичное наверх, критичные проверки — скриптом |
| [A field guide to Claude Fable: finding your unknowns](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns) | 06.07.2026 | да | Как ставить задачу моделям пятого поколения: четыре вида неизвестного и приёмы — проход по слепым зонам, прототипы, интервью, образцы (лучший образец — исходный код), план, заметки по ходу работы |
| [Automating eval design and hillclimbing with Claude](https://claude.dev/blog/automating-eval-design-and-hillclimbing/) | 28.09.2026 | да | Как строить замеры: задачи как в жизни, запас до 100 %, малый разброс, отдельные рабочая и проверочная части, провалы в промпт не вставлять. Команды `/claude-api build-eval` и `/claude-api hillclimb` |
| [Building effective agent automations](https://claude.dev/blog/building-effective-agent-automations/) | 08.10.2026 | список | Разбор образцовой автоматизации по расписанию |
| [Using Claude Code: Spending your effort](https://claude.dev/blog/spending-your-effort/) | 25.09.2026 | список | Как выбирать уровень усилий модели |
| [What a task costs on Opus 5.5](https://claude.dev/blog/what-a-task-costs-on-opus-5-5/) | 25.09.2026 | список | Цена задачи — полезно для выбора модели под скил |
| [Getting started with Claude Code mods](https://claude.dev/blog/getting-started-with-claude-code-mods/) | 01.10.2026 | список | Моды Claude Code |
| [Скилы в Claude Code](https://code.claude.com/docs/en/skills) | действующая | да | Поля шапки: запрет самовключения, разрешённые инструменты, модель, запуск в субагенте, хуки, пути, аргументы. Подстановка вывода команды в текст скила. После сжатия контекста остаются первые 5000 токенов каждого скила, на все — 25 000. Правило, которое должно выполняться всегда, — в хук |
| [anthropics/skills](https://github.com/anthropics/skills) и [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | действующее | да (skill-creator) | Образцовые скилы. `skill-creator` ведёт цикл: черновик, 2–3 запроса, прогон со скилом и без, оценка, правка. Советует объяснять «почему»; запреты прописными — признак плохого скила |

Инженерный блог Anthropic (`anthropic.com/engineering`), свежие записи ленты — **список**, кроме статьи от
24.03.2026: она прочитана. Её суть — исполнителя и оценщика разделять; до начала работы договориться, что значит
«готово»; каждая часть обвязки — допущение о слабости модели, с новой моделью их убирают по одному.

| Что | Дата |
|---|---|
| [How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude) | 25.05.2026 |
| [An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) | 23.04.2026 |
| [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) | 08.04.2026 |
| [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 24.03.2026 |
| [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) | 05.02.2026 |
| [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 09.01.2026 |
| [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 26.11.2025 |
| [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | 16.10.2025 |
| [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 29.09.2025 |
| [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 11.09.2025 |

Статьи 2025 года писались под прежние модели. Где они расходятся со статьёй от 24.07.2026 — верить свежей.

### Курсы

Anthropic Academy, каталог — [anthropic.skilljar.com](https://anthropic.skilljar.com/). Каталог открылся без входа;
для прохождения нужна запись на площадке. Платность на странице каталога не указана.

| Курс | Зачем нам |
|---|---|
| [Introduction to agent skills](https://anthropic.skilljar.com/introduction-to-agent-skills) | Прямо по теме: собрать, настроить и раздать скилы в Claude Code |
| [Introduction to subagents](https://anthropic.skilljar.com/introduction-to-subagents) | Субагенты и разделение контекста |
| [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action) | Долгие самостоятельные сессии: настройка, автоматизация, проверка |
| [Claude Code 101](https://anthropic.skilljar.com/claude-code-101) | Основа |
| [Introduction to Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol) и [Advanced Topics](https://anthropic.skilljar.com/model-context-protocol-advanced-topics) | Инструменты для скилов |
| [AI Fluency for Builders](https://anthropic.skilljar.com/ai-fluency-for-builders) | Общий подход к работе с ИИ для тех, кто строит продукт |

Сторонняя площадка: [Agent Skills with Anthropic](https://www.deeplearning.ai/short-courses/agent-skills-with-anthropic/)
на DeepLearning.AI — **пересказ**. 10 уроков, 2 ч 19 мин, ведёт Эли Шоппик из Anthropic, вышел в конце января
2026. Уроки бесплатны, проверочное задание и сертификат — по платной подписке.

### Выступления

Конференция Code with Claude 2026: Сан-Франциско 06.05, Лондон 19.05, Токио 10.06. Записи —
[страница записей](https://claude.com/code-with-claude/san-francisco#recordings). Страницы докладов открывал,
сами записи не смотрел.

| Доклад | Кто | Зачем нам |
|---|---|---|
| [Beyond the basics with Claude Code](https://claude.com/code-with-claude/session/ldn-beyond-the-basics-with-claude-code) | Дейзи Холлман | `CLAUDE.md` как следует, знания команды в скилах, безопасный авторежим |
| [The prompting playbook](https://claude.com/code-with-claude/session/tyo-the-prompting-playbook) | Ханна Моран | Принципы промптинга для агентов, которые планируют и действуют |
| [Memory and dreaming for self-learning agents](https://claude.com/code-with-claude/session/sf-memory-and-dreaming-for-self-learning-agents) | Махеш Мураг | Память агента |
| [The expanding toolkit](https://claude.com/code-with-claude/session/sf-the-expanding-toolkit) | Лукас Гонсалес | Набор инструментов платформы |
| [What's new in Claude Code](https://claude.com/code-with-claude/session/sf-whats-new-in-claude-code) | Диксон Цай | Новое в Claude Code |
| [Stop babysitting your agents](https://claude.com/code-with-claude/session/tyo-stop-babysitting-your-agents) | Токио | Как перестать нянчить агентов |
| [Caching, harnesses, and advisors](https://claude.com/code-with-claude/session/sf-caching-harnesses-and-advisors-building-on-claude-at-github-scale) | GitHub и Anthropic | Обвязка агента в большом масштабе |

## OpenAI

| Что | Дата | Прочитано | Суть |
|---|---|---|---|
| [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | 05.09.2026 (дата — пересказ) | да | Пара к статье Anthropic. Описание скила — как можно короче; широкое «когда работаешь с базами» включает скил не к месту; корневой файл большого скила — короткий указатель; подробные маршруты вредят; из `AGENTS.md` убрать «прочитай всё перед правкой» и «запусти тесты»; заранее сказать, что значит «готово» |
| [Using GPT-6 Astra: промптинг и переход](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra) | 09.2026 | да | Пять тем: инициатива, следование указаниям, стиль письма, передача субагентам, проверка. Советуют проверить каждый скил и файл указаний; просить модель назвать точный `SKILL.md` и строку, из-за которой она остановилась; список запрещённых слов-штампов |
| [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills) | 2026 | да | Метод проверки скила: сначала четыре вида целей (итог, ход, стиль, расход), 10–20 запросов с пометкой «должен включиться», сначала проверки скриптом по журналу запуска, оценка по рубрике — только для качественного |
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | действующая | да | Устройство скилов в Codex и ChatGPT. Список описаний занимает не больше 2 % окна (или 8000 знаков); при нехватке места описания урезаются, поэтому главное — в начало. «Инструкции важнее скриптов; скрипт — когда нужен одинаковый результат» |
| [Shell + Skills + Compaction: tips for long-running agents](https://developers.openai.com/blog/skills-shell-tips) | 2026 | да | Описание скила — правило выбора с блоком «применять / не применять»; у Glean без отрицательных примеров выбор скила упал примерно на 20 %; шаблоны и образцы — внутрь скила; для надёжности называть скил явно |
| [Custom Code Review rules for Codex](https://developers.openai.com/blog/custom-code-review-rules-for-codex) | 2026 | да | Прямо к скринерам. Правило ревью — узкое, неочевидное, с «безопасным путём»; механические проверки оставить скриптам сборки; каждое правило проверять на контрпримере |
| [Using skills to accelerate OSS maintenance](https://developers.openai.com/blog/skills-agents-sdk) | 2026 | да | В постоянном файле — короткие правила «если такая работа — вызови такой скил». Модель раз за разом выводит один порядок — это скрипт. Скрипт — механика, модель — суждение |
| [15 lessons learned building ChatGPT Apps](https://developers.openai.com/blog/15-lessons-building-chatgpt-apps) | 2026 | список | Уроки, упакованные в скил Codex |
| [Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) | 2026 | список | Долгие задачи |
| [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) и [Long-running work](https://learn.chatgpt.com/docs/long-running-work) | действующие | да | Постоянные указания складываются от общих к ближним, предел — 32 КБ; правила ревью — в файле рядом с кодом. Цель долгой работы — три части: результат, ограничения, проверка |
| [Prompting](https://learn.chatgpt.com/docs/prompting) | действующая | список | Документация Codex по промптам |
| [openai/skills](https://github.com/openai/skills) | действующее | список | Образцовые скилы OpenAI и их `skill-creator` |

Курсы и записи — [OpenAI Academy](https://academy.openai.com/); платность на странице не указана:

| Что | Дата |
|---|---|
| [Codex bootcamp 101: Agentic coding](https://academy.openai.com/home/videos/september-23-codex-bootcamp-101-2026-09-24) | 23.09.2026 |
| [Codex bootcamp 201: Team workflows](https://academy.openai.com/home/videos/september-30-codex-bootcamp-201-2026-10-01) | 30.09.2026 |
| [Codex bootcamp 301: Advanced automation](https://academy.openai.com/home/videos/codex-bootcamp-301-advanced-automation-2026-10-07) | 07.10.2026 |
| [Build with AI](https://academy.openai.com/pages/courses) — курсы по Codex и API | — |

DevDay 2026 прошёл 29.09.2026. [Итоги](https://openai.com/index/devday-2026-recap/) не открылись (защита от
роботов); записи докладов не найдены — смотреть на канале OpenAI в YouTube.

## Google

| Что | Дата | Прочитано | Суть |
|---|---|---|---|
| [5-Day AI Agents: Intensive Vibe Coding Course](https://www.kaggle.com/learn-guide/5-day-agents-vibecoding) | 15–19.06.2026, теперь в своём темпе | да (страница курса) | Бесплатный курс Google и Kaggle, 353 тыс. участников. На каждый день — документ, подкаст, практика, запись эфира. **День 3 целиком про скилы** (документ «Agent Skills»: как не дать контексту «протухнуть», подгрузка по мере надобности). День 4 — безопасность и проверка кода, написанного агентами. День 5 — разработка от спецификации, агенты-ревьюеры кода |
| [Agent Skills](https://www.kaggle.com/whitepaper-agent-skills) — документ дня 3 того же курса | 05.2026 | вступление и оглавление — да, остальное — пересказ | 62 страницы. Скил как «процедурная память»; один агент с набором скилов вместо многих агентов; два пути к первому скилу — перевести уже известное или закрепить только что сделанное; проверочные случаи раньше текста скила; скил проверять в наборе с остальными; лестница «чтение — черновик — действие». Пересказ — по разбору [explainx.ai](https://explainx.ai/blog/kaggle-agent-skills-whitepaper-guide-2026) |
| [Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) | обновлено 13.10.2026 | да | Общий справочник по промптам Gemini; отдельные разделы про Gemini 3 и про агентов. Шаблон системных указаний агенту: план перед действием, оценка риска, не повторять неудавшийся вызов |
| [Agent Skills в Gemini CLI](https://geminicli.com/docs/cli/skills/) и [создание скилов](https://geminicli.com/docs/cli/creating-skills/) | действующая | пересказ | Тот же стандарт; чем скил отличается от `GEMINI.md` |
| [Скилы в Antigravity](https://antigravity.google/docs/skills) | действующая | пересказ | Папка `.agents/skills/`; описание — в третьем лице и с ключевыми словами |
| [Agent Factory: 100X engineering with AI agents in Antigravity 2.0](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-100x-engineering-with-ai-agents-in-google-antigravity-20) | 18.06.2026 | пересказ | Видео и разбор: скил как «шпаргалка для агента», ревью кода в мире агентов |
| [Developer highlights from I/O 2026](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/) | 05.2026 | пересказ | Обзор объявлений для разработчиков |

Для практики курса нужны учётные записи Kaggle и Google AI Studio.

## xAI (Grok)

Своего руководства по написанию скилов у xAI нет — есть документация продукта.

| Что | Дата | Прочитано | Суть |
|---|---|---|---|
| [Grok Build: Skills, Plugins & Marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces) | 11.08.2026 | да | Grok Build читает скилы, плагины, хуки и `CLAUDE.md` из папок Claude Code без настройки, а также `AGENTS.md`. Вывод: скил, написанный по стандарту, переносим |
| [Grok Build: AGENTS.md](https://docs.x.ai/build/features/project-rules), [Subagents](https://docs.x.ai/build/features/subagents), [Hooks](https://docs.x.ai/build/features/hooks) | 2026 | список | Остальная документация продукта |
| Руководство по промптам для текстовых моделей Grok | — | не открылось | В оглавлении документации значится, страница отдала ошибку 404 |

## Общий стандарт и независимые источники

| Что | Дата | Прочитано | Суть |
|---|---|---|---|
| [agentskills.io — спецификация](https://agentskills.io/specification) | действующая | да | Точный формат скила: шапка, три ступени подгрузки, ссылки на файлы на один уровень вглубь |
| [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) | действующая | да | Начинать с настоящей задачи и своих документов; «добавь, чего агент не знает, убери, что знает»; значение по умолчанию вместо списка вариантов; раздел подводных камней — самое ценное; до 500 строк и 5000 токенов |
| [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) | действующая | да | Метод настройки описания: около 20 запросов, по 3 прогона, порог 0,5, деление 60/40 на рабочую и проверочную части, до пяти кругов; не вписывать слова из провалившихся запросов |
| [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) и [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts) | действующая | да | Проверка: прогоны со скилом и без, утверждения после первого прогона, оценка с доказательством; «правила добавляются, результат не растёт — убирай». Скрипт для агента: без вопросов по ходу, с `--help`, понятными ошибками, структурным выводом и кодами возврата |
| [SkillsBench](https://arxiv.org/abs/2602.12670) | 02.2026 | да (основной текст) | 86 задач, 11 областей, 7308 прогонов. Скилы от человека: +16,2 пункта в среднем, от +4,5 в разработке программ до +51,9 в медицине; в 16 задачах из 84 — хуже, чем без скила. Скилы от самой модели: −1,3. 2–3 скила на задачу лучше, чем 4 и больше; «всеобъемлющие» скилы −2,9, «подробные» +18,8. Слабая модель со скилами обошла сильную без них |
| [Vercel, «AGENTS.md outperforms skills in our agent evals»](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) | 01.2026 | да | Сжатый указатель на 8 КБ в `AGENTS.md` дал 100 % прохождения, скил — 53 % сам по себе и 79 % с прямым указанием; без указания скил не включался в 56 % случаев. Формулировка указания меняла исход. Авторы оговаривают: для действий по явной команде скилы лучше. Замер узкий — одна библиотека |
| [The Context Course](https://huggingface.co/learn/context-course/unit0/introduction) | 2026 | да (вводная) | Курс Hugging Face: скилы, MCP, плагины, субагенты, хуки, свой агент с нуля. Нужна учётная запись Hugging Face |
| Cursor, «Best practices for coding with agents» | 01.2026 | пересказ | Правила — постоянный контекст, скилы — по надобности |

## Где источники расходятся

- **Форма описания скила.** Anthropic: в третьем лице («Обрабатывает таблицы…»). Стандарт: повелительно («Применяй,
  когда…») и «лучше настойчиво». OpenAI: как можно короче и без нажима. Общее у всех — сказать, когда применять,
  и главное поставить в начало. Что лучше у нас — покажет замер включения.
- **Примеры в скиле.** Справочник Anthropic советует пары «вход — выход». Статья от 24.07.2026 говорит, что новым
  моделям примеры сужают поиск. Примеры оставлять там, где нужен точный вид результата.
- **Скил или строка в постоянном файле.** Замер Vercel против включения по описанию. То, что нужно всегда, — в
  `CLAUDE.md`; то, что нужно иногда, — в скил.

## Что не закрыто

- Не открылись: итоги DevDay 2026, OpenAI Cookbook, руководство xAI по промптам. Сборник советов Codex
  (`learn.chatgpt.com/guides/best-practices`) отдал 404.
- Записи выступлений и курсы не просмотрены — в списке только их страницы.
- Документ Google «Agent Skills» прочитан по разбору: просмотрщик отдаёт текст только первых четырёх страниц.
  Чтобы прочитать оригинал, нужно скачать файл — с разрешения владельца.
- Не дочитаны: последняя глава руководства Anthropic, «Equipping agents for the real world with Agent Skills»,
  документация Codex по промптам.
- Ошибки ИИ при написании кода собраны отдельно — `ai-code-mistakes.md`. Нормативы написания кода в этот
  проход не входили.
