# Как устроены папки и файлы в крупных проектах

Дата: 16.10.2026. Зачем: шаблон `assets/spec-template.md` (разделы «Карта модулей», «Данные», «Что менять, когда добавляешь») должен опираться на то, что повторяется в больших проектах, а не только на наш опыт.

## Как собрано

- 24 проекта. Деревья файлов прочитаны целиком через `gh api repos/OWNER/REPO/git/trees/HEAD?recursive=1` (ни одно дерево не обрезано). Ничего не клонировалось.
- Выборочно прочитаны сами файлы правил: `CODEOWNERS`, `AGENTS.md`, `.import-restrictions`, `biome.json`, `.golangci.yml`, `migrations_lockfile.txt`, README про миграции и т.п.
- Что не проверял: работу самих линтеров (не запускал), полное содержимое `CODEOWNERS`, Bazel (в этой выборке его нет), содержимое каждой проверки в CI. Где сказано «в дереве есть файл X», я видел путь, но не читал, что внутри.
- Числа — по дереву на 16.10.2026. Цифры вида «17 из 24» посчитаны по путям, это не оценка на глаз.

Проекты по видам:

| Вид | Проекты |
|---|---|
| Веб-приложения | discourse, mastodon, zulip, cal.com, sentry, mattermost, n8n, supabase |
| Шаблон и фреймворки | full-stack-fastapi-template, django, next.js |
| Инфраструктура | kubernetes, terraform, grafana, prometheus |
| Базы и брокеры | postgres, redis, kafka |
| Десктоп и клиенты | vscode, electron, bitwarden/clients |
| Компиляторы и инструменты | rust-analyzer, ruff |
| Платформа интеграций | home-assistant/core |

---

## 1. Главное по пунктам

### Что повторяется почти везде

1. **Два уровня деления.** Верхний — крупные части (слои, процессы, сервисы, приложения). Внутри верхнего — папка на фичу или домен. Чисто «по слою» (`models/ views/ services/`) устроены только пять-шесть веб-проектов: mastodon, fastapi-template, mattermost server, ядро discourse и zulip. Остальные идут «по фиче/домену»: HA `homeassistant/components/<интеграция>/`, cal.com `packages/features/<фича>/`, n8n `packages/cli/src/modules/<фича>/`, grafana `pkg/services/<сервис>/`, prometheus (пакет на подсистему), kafka (модуль Gradle на подсистему), rust-analyzer (крейт на стадию).
2. **Зеркало или соседство для тестов.** Тест всегда можно найти по пути кода, без поиска по смыслу. Три варианта (см. раздел 3): рядом с файлом, зеркальное дерево, дерево по виду проверки. Свободно разложенных тестов нет ни у кого.
3. **Файл-владелец в корне.** `CODEOWNERS` или `OWNERS` есть у 16 из 24 (нет у kafka, django, fastapi-template, mastodon, postgres, redis, rust-analyzer, zulip). У kubernetes ещё 590 файлов `OWNERS` в папках.
4. **Правила для ИИ-агентов в репозитории.** Корневой `AGENTS.md` или `CLAUDE.md` у 17 из 24. Вложенные (в папке модуля) — у семи: n8n 31 файл, grafana 12, bitwarden 10, next.js 10, sentry 8, vscode 7, supabase 6. Это ближайший аналог нашей «Карты модулей» у самого кода.
5. **Сгенерированные файлы лежат в репозитории, и для каждого есть команда обновления и проверка в CI.** kubernetes `hack/update-*.sh` и `hack/verify-*`, mattermost `make generated` и `make migrations-extract`, HA `script/hassfest` (генерирует `CODEOWNERS`, `requirements_all.txt`), redis `src/commands/*.json` → `commands.def`, fastapi-template `frontend/src/client/*.gen.ts` через `scripts/generate-client.sh`, n8n `docs/generated/postgres-schema/`, cal.com `docs/api-reference/v2/openapi.json` («не править руками»).
6. **Пример конфига и секретов лежит в репозитории, настоящий — нет.** `.env.example` (cal.com, n8n `.env.local.example`, supabase `docker/.env.example`, mastodon `.env.production.sample`, electron `.env.example`), файл значений по умолчанию плюс образец (grafana `conf/defaults.ini` и `conf/sample.ini`, zulip `zproject/default_settings.py` и `prod_settings_template.py`, postgres `postgresql.conf.sample`, discourse `config/discourse_defaults.conf` и `*.sample`). У fastapi-template `.env` лежит в корне с заглушками `changethis`.
7. **Документы разделены на «для пользователей» и «для разработчиков».** grafana: `docs/` и `contribute/`. zulip: `docs/` целиком для разработчиков, справка в `starlight_help/`. electron: `docs/api/` и `docs/development/`. rust-analyzer: `docs/book/src/contributing/`. discourse: `docs/developer-guides/docs/03-code-internals/`. Папка `docs/` в корне есть у 18 из 24.
8. **Правило «выложенную миграцию не правят, делают новую».** Явно записано у grafana, mattermost (`server/channels/db/migrations/README.md`), n8n (`.agents/review-rules/db-migrations/`), discourse (`.skills/discourse-migration/SKILL.md`).

### Что зависит от вида ПО

| Вид | Как устроено | Примеры |
|---|---|---|
| Веб-приложение на фреймворке (Rails, Django) | Слои фреймворка на верхнем уровне. Миграции — встроенный механизм фреймворка. Плагины/интеграции — отдельная папка с тем же устройством, что у ядра. Тесты — зеркальное дерево | discourse `plugins/chat/{app,config,db,spec}`, mastodon `spec/`, sentry `tests/sentry/<модуль>` |
| Веб-приложение, монорепо на TypeScript | `apps/` (запускаемое) и `packages/` (библиотеки). Границы — правилами линтера. Тесты рядом с кодом | cal.com, n8n, supabase, bitwarden |
| Инфраструктура на Go | `cmd/` (бинарники), `pkg/` или `internal/` (код), `hack/` или `scripts/`, `*_test.go` рядом. Границы — компилятор (`internal/`) и список запретов | kubernetes, terraform, grafana, prometheus |
| Базы и брокеры | Дерево по подсистемам, README в каждой подсистеме, тесты отдельным деревом по виду проверки. Миграций БД нет, есть версии форматов | postgres `src/backend/access/*/README`, redis `tests/{unit,integration}`, kafka `src/main` и `src/test` |
| Десктоп и IDE | Слои × среды выполнения (`common`, `browser`, `node`, `electron-*`). Возможности подключаются как «вклады» | vscode `src/vs/workbench/contrib/<фича>`, electron `shell/{browser,common,renderer}` |
| Компиляторы и инструменты | Один крейт на стадию конвейера. Документ про архитектуру с «инвариантами». Тесты — данные (фикстуры, снимки) | rust-analyzer, ruff `crates/ruff_linter/resources/test/fixtures/` |
| Платформа интеграций | Один пакет на интеграцию с манифестом. Валидатор проверяет манифесты и импорты | HA `manifest.json` и `script/hassfest` |

### Где проекты расходятся и почему

- **Тесты рядом или отдельно.** Рядом: Go (kubernetes 3557 `_test.go`, grafana 5467, mattermost 2706, terraform 692), TypeScript (n8n 7496, bitwarden 1471). Отдельно: Python и Ruby (HA, zulip, django, mastodon, discourse, sentry), Java/Scala (kafka), C (postgres, redis). Причина — привычка языка и инструментов (`pytest`, `rspec`, Gradle `src/test`), а не архитектура.
- **Границы жёсткие или словесные.** Жёсткие там, где у частей разные владельцы или есть коммерческое разделение: kubernetes, vscode, kafka, cal.com, bitwarden, n8n, HA, grafana. Словесные или никаких там, где ядро держат несколько человек: postgres, redis, django, mastodon, zulip. Исключение — rust-analyzer: границу держит Cargo (крейт видит только объявленные зависимости) плюс письменные «инварианты» в документе об архитектуре.
- **Миграции.** Тип хранилища решает формат. ORM-проекты берут формат ORM (Django — 4-значный номер, Rails и Prisma — метка времени, Alembic — хеш). Свой движок миграций пишут те, у кого несколько баз (mattermost с `morph`, n8n с классами TypeScript, grafana с миграциями в Go). У баз и брокеров миграций нет, есть версия формата данных (postgres `catversion.h`, kafka версии сообщений).
- **Один репозиторий или много.** kubernetes держит в `staging/src/k8s.io/*` 34 модуля, которые публикуются в отдельные репозитории. electron хранит чужой код как патчи в `patches/`. Остальные — один репозиторий, внутри пакеты.
- **Что лежит в «Карте».** У крупных нет одной карты. Она раздроблена: `AGENTS.md` по папкам, `README` по подсистемам (postgres 109 README), `ARCHITECTURE.md` на отдельный пакет (kubernetes `staging/src/k8s.io/apiserver/ARCHITECTURE.md`, n8n `packages/@n8n/expression-runtime/ARCHITECTURE.md`). Один общий документ про архитектуру целиком есть у terraform (`docs/architecture.md`), rust-analyzer (`docs/book/src/contributing/architecture.md`), prometheus (`documentation/internal_architecture.md`).

---

## 2. Как модули не дают друг другу лезть

Механизмы, от самых жёстких к самым мягким. В скобках — где видел.

1. **Компилятор или система сборки не даёт увидеть чужое.**
   - Go `internal/` (terraform: `internal/` — 63 пакета).
   - Cargo: крейт видит только то, что записано в его `Cargo.toml` (rust-analyzer 36 крейтов, ruff 55 крейтов).
   - Gradle-модули (kafka: `clients`, `core`, `streams`, `connect`, `raft`, ...).
2. **Список разрешённых и запрещённых импортов в файле, который читает CI.**
   - kubernetes: `.import-restrictions` (70 файлов, сверено 16.10) и `cmd/import-boss`. Правила ищутся в папке и выше, ближайший побеждает; «не описано» считается ошибкой. Пример в `pkg/.import-restrictions`: «`pkg/` не зависит от `cmd/`».
   - kafka: `checkstyle/import-control-<модуль>.xml` на каждый модуль. В `import-control-group-coordinator.xml` стоит комментарий: прежде чем править файл, подумать о слоях проекта.
   - vscode: `.eslint-plugin-local/code-layering.ts` и `code-import-patterns.ts`. Слои `base → platform → editor → workbench → code/server`. При нарушении линтер пишет, к какому слою обращаться нельзя и какие слои разрешены из этой папки.
   - cal.com: `biome.json`, `noRestrictedImports` с текстом причины: «`lib` не импортирует `app-store` (круговые зависимости)», «`app-store` не импортирует `features`», «`features` не импортирует `trpc`».
   - bitwarden: `eslint.config.mjs`, `buildNoRestrictedImports([...])` по областям. Например, `apps/**` не импортирует `bitwarden_license/**`, `apps/browser` не импортирует `**/popup/*`.
   - grafana: `.golangci.yml`, `depguard` по пакетам. Правило для `apimachinery`: этот пакет не должен импортировать ядро Grafana.
   - n8n: `turbo boundaries` плюс `scripts/check-boundaries.mjs`; ESLint-конфиги `backend-network-boundary.ts` и `encryption-boundary.ts`.
3. **Манифест объявляет зависимости, валидатор сверяет с реальными импортами.** HA: `manifest.json` с полем `dependencies`, `script/hassfest/dependencies.py` разбирает код и находит импорты чужих интеграций. Плюс `tests/test_circular_imports.py`.
4. **Публичный вход — один файл на модуль, внутрь не лезут.**
   - cal.com: фича отдаёт наружу `index.ts`, правило `agents/rules/architecture-feature-boundaries.md` (фичи общаются только через опубликованный интерфейс).
   - vscode: у каждого вклада один `.contribution.ts` и один общий файл с API; вклады зависят друг от друга только через этот общий файл, внутрь не лезут.
   - grafana: `contribute/backend/package-hierarchy.md` — типы и интерфейсы в корневом пакете сервиса, реализация в подпакете `<имя>impl`: подпакеты зависят от корня, не наоборот.
   - mattermost: `server/einterfaces/` — интерфейсы, за которыми прячется закрытый код `server/enterprise/`.
5. **Храповик для старого кода.** n8n: старых нарушений 110, `.boundaries-baseline.json` хранит это число, CI падает, только если число выросло; ночная задача число уменьшает. Так вводят правило в проект, где нарушения уже есть.
6. **Письменные инварианты рядом с кодом.** rust-analyzer: в `architecture.md` строки-инварианты, например: крейт `syntax` полностью независим от остального rust-analyzer. Проверяет их Cargo и ревьюер.
7. **Владелец папки.** `CODEOWNERS` (bitwarden: по командам, sentry: в файле сказано, что идеально каждая папка принадлежит команде, а список по общим папкам — плохая практика), `OWNERS` по папкам (kubernetes). HA генерирует `CODEOWNERS` из полей `codeowners` в манифестах интеграций.
8. **Только договорённость и ревью.** postgres, redis, django, zulip, mastodon, fastapi-template. Опора — именование, README в подсистемах, заголовочные файлы как публичный интерфейс (postgres: `src/include/` зеркалит `src/backend/`).

Что видно по этому списку: в больших проектах граница — это **файл с правилами, который читает автомат**, а не абзац в документе. Документ в лучшем случае объясняет, почему правило такое.

---

## 3. Где лежат тесты

| Схема | Кто | Пример пути |
|---|---|---|
| Рядом с файлом | kubernetes, terraform, prometheus, grafana (Go), mattermost, bitwarden, n8n, supabase, часть cal.com | `internal/command/apply_destroy_test.go`, `apps/browser/src/auth/popup/guards/platform-popout.guard.spec.ts` |
| В подпапке `test/` внутри модуля, по средам | vscode | `src/vs/workbench/contrib/debug/test/browser/`, `src/vs/base/test/common/` |
| Зеркальное дерево с тем же путём | discourse, mastodon, sentry, HA, fastapi-template, kafka | `spec/models/` ↔ `app/models/`; `tests/sentry/<модуль>/` ↔ `src/sentry/<модуль>/`; `tests/components/hue/` ↔ `homeassistant/components/hue/`; `backend/tests/api/routes/test_items.py` ↔ `backend/app/api/routes/items.py` |
| Отдельное дерево по виду проверки | postgres, redis, next.js, django, zulip, electron | `src/test/{regress,isolation,recovery,modules}`, `tests/{unit,integration,modules,sentinel}`, `test/{unit,development,production,e2e}`, `tests/<фича>/` у django, `zerver/tests/test_<тема>.py` у zulip, плоский `spec/api-*.spec.ts` у electron |
| Тест как данные | ruff, rust-analyzer, postgres | `crates/ruff_linter/resources/test/fixtures/`, `src/test/regress/expected/` (277 файлов) |

Что общего: выбран **один** способ на проект (иногда два: код и e2e), и имя теста выводится из имени кода. cal.com и n8n смешивают рядом-с-кодом и отдельное дерево для интеграционных и e2e.

Что можно проверять автоматом: у зеркальных схем — «для каждой папки модуля есть папка тестов». Готовой такой проверки в выборке не видел, придётся написать самим.

---

## 4. Миграции: нумерация и столкновения

| Проект | Формат имени | Как сталкиваются номера, что делают |
|---|---|---|
| discourse | метка времени `db/migrate/20120311163914_create_forum_threads.rb`; разрушающие — в `db/post_migrate/` | Генератор `bin/rails g migration ...`; в навыке сказано: метки времени руками не писать, придуманные вручную метки сталкиваются. `SafeMigrate` блокирует переименование и удаление в обычных миграциях; `db/structure.sql` — снимок схемы |
| mastodon | метка времени `db/migrate/20160220174730_create_accounts.rb`, `db/post_migrate/` (82 файла), `db/schema.rb` | Как у Rails: при конфликте `schema.rb` — пересобрать |
| supabase | метка времени `supabase/migrations/<ГГГГММДДччммсс>_<имя>.sql` | Генерирует CLI |
| cal.com (Prisma) | метка времени, папка на миграцию `packages/prisma/migrations/20210605225044_init/migration.sql`; `migration_lock.toml` | Генерирует `prisma migrate dev --name ...` |
| n8n | миллисекунды эпохи и имя класса `packages/@n8n/db/src/migrations/postgresdb/1587669153312-InitialMigration.ts` | Индекс миграций генерируется из имён файлов; `migration-index-sync.ts` падает, если индекс устарел; в правилах ревью замечание вызывает метка, которая не больше всех существующих |
| sentry | четырёхзначный номер `src/sentry/migrations/1119_add_sentryapp_webhook_headers.py` | **`migrations_lockfile.txt`** — в одном файле последняя миграция каждого приложения. Две ветки правят одну строку → конфликт git. Текст в самом файле: конфликт значит, что кто-то выложил миграцию раньше тебя; лечится rebase на master и повторной генерацией своей миграции. Ещё CI `migrations.yml` и `migrations-drift.yml` |
| zulip | четырёхзначный номер `zerver/migrations/0001_squashed_0569.py` | `docs/subsystems/schema-migrations.md`: два пути — удалить свою и перегенерировать после rebase, или `./tools/renumber-migrations`, который сам правит номера и `dependencies`. `./tools/test-migrations` проверяет граф. История сжата в `0001_squashed_0569` |
| django | четырёхзначный номер `django/contrib/auth/migrations/0001_initial.py` | Документация: два разработчика добавили миграцию с одним номером — не страшно, номера нужны только людям для удобства; зависимости записаны в файле; Django сам найдёт два «хвоста» и предложит их выстроить (`makemigrations --merge`) |
| mattermost | порядковый номер `server/channels/db/migrations/postgres/000235_create_property_values_groupid_fieldid_index.up.sql` и `.down.sql` | Создание `make new-migration name=<>` (morph `--sequence`). `make migrations-extract` дописывает файл `migrations.list` — общая точка конфликта. README требует перед PR слить свежий основной код, чтобы не столкнуться по номеру |
| grafana | миграции в Go-коде, регистрируются в `pkg/services/sqlstore/migrations/migrations.go` | Золотой файл `testdata/migration_ids.txt`: новая миграция роняет тест, пока человек не перегенерирует файл. В документе прямо сказано: агент не перегенерирует этот файл сам, а останавливается и спрашивает. Новая миграция названа крайней мерой |
| fastapi-template (Alembic) | хеш `backend/app/alembic/versions/e2412789c190_initialize_models.py` | Совпасть номеру нечему; две ветки дают две «головы», решается `alembic merge` (в шаблоне это не автоматизировано) |
| postgres | миграций БД нет. Для системного каталога есть OID | `src/include/catalog/unused_oids` ищет свободные, `duplicate_oids` ловит дубли, `renumber_oids.pl` сдвигает диапазон; версия каталога `catversion.h` вида `YYYYMMDDN` |
| terraform | миграций нет. Та же беда у `CHANGELOG` | `.changes/v1.16/BUG FIXES-20260901-115602.yaml` — один файл на изменение, имя с временем (changie). Общего файла нет, столкнуться нечему |
| HA | миграции данных внутри интеграции (`homeassistant/components/hue/migration.py`) | Версия записи конфигурации, миграция живёт в папке интеграции |
| kubernetes, redis, kafka, prometheus | миграций БД нет | Версии API (`pkg/apis/<группа>/v1`, `v1beta1`), версии формата сообщений и RDB |

**Как решают столкновение** — четыре приёма:

1. **Имена, которые не сталкиваются сами:** метка времени из генератора (discourse, mastodon, supabase, Prisma, n8n), хеш (Alembic), имя файла с временем для журнала изменений (terraform). Остаётся порядок: «твоя миграция по времени раньше чужой, но применена после» (n8n держит ревью-правило «выше всех существующих»).
2. **Общий файл «вершины», который правят все новые миграции.** Столкновение превращается в конфликт git, а не в тихую ошибку: sentry `migrations_lockfile.txt`, mattermost `migrations.list`, grafana `testdata/migration_ids.txt`, n8n сгенерированный индекс. Лечится одним способом: rebase, затем перегенерировать.
3. **Инструмент пересчёта:** zulip `tools/renumber-migrations`, postgres `renumber_oids.pl`, Django `makemigrations --merge`. Число меняется автоматом, зависимости правятся в файлах.
4. **Человеческий шлюз:** grafana — перегенерировать золотой файл должен человек, не агент; mattermost — «если миграция уже выложена, не править, добавить новую».

Отдельно про **двухэтапные разрушающие изменения** (это тоже про «Данные/миграции»): discourse (`db/migrate` до выкладки, `db/post_migrate` после; удаление колонки — несколько выкладок; `lib/migration/column_dropper.rb`), mattermost (README: сменить тип колонки за 4 выпуска: добавить, заполнить, перейти на новую, удалить старую), mastodon (`db/post_migrate/`).

И про **начальные данные**: discourse в навыке требует, чтобы новая установка не получала строк данных приложения из миграций. Схема новой установки берётся из `db/structure.sql`, строки в нём не хранятся; начальные данные кладутся в `db/fixtures/`, а CI (`db:check_structure_dump`) проверяет, что после миграций на чистой базе в таблицах приложения пусто.

---

## 5. Прямые аналоги нашему этапу «спецификация»

- **cal.com `SPEC-WORKFLOW.md` и `specs/<фича>/`.** Структура: `CLAUDE.md` (что читать первым), `design.md` (спецификация), `implementation.md` (что сделано; статус ведётся здесь, не в спеке), `decisions.md` (почему так), `prompts.md`, `future-work.md`, `docs/`. Шаблон — `specs/_templates/`. Режим «по запросу»: включается явной просьбой работать по спецификации. Если спеки нет, агент спрашивает, создавать ли её.
  - Разница с нашим шаблоном: у них статус реализации и решения вынесены в отдельные файлы, у нас — в один.
- **n8n `docs/adr/` и `docs/ADR_TEMPLATE.md`** — решения отдельными записями.
- **grafana `pkg/router/specs/2026-08-17-router-discovery-openapi-design.md`** — спеки с датой в имени, лежат рядом с кодом пакета.
- **sentry `src/AGENTS.md`** — раздел с деревьями решений для ИИ-помощника: «пользователь хочет добавить эндпоинт» → список файлов (`src/sentry/api/endpoints/{resource}.py`, `src/sentry/api/urls.py`, `tests/sentry/api/endpoints/test_{resource}.py`, `src/sentry/api/serializers/models/{model}.py`). Это в точности наш раздел «Что менять, когда добавляешь», только по типам задач.

---

## 6. По проектам (пути настоящие, проверены по дереву)

Формат: верх; как делятся модули; тесты; границы и владельцы; миграции и конфиг; доки.

### Веб-приложения

**discourse/discourse** (Rails + Ember)
- Верх: `app/`, `lib/`, `config/`, `db/`, `plugins/`, `frontend/`, `spec/`, `docs/`, `migrations/` (инструменты импорта), `script/`, `themes/`, `.skills/`, `AGENTS.md`, `CODEOWNERS`.
- Модули: `app/` по слоям (`controllers`, `models` 397 файлов, `services` 297, `serializers`, `jobs`, `views`); `plugins/` — 46 плагинов, у каждого свой набор `app/ config/ db/ lib/ spec/ plugin.rb about.json`. Фронтенд — `frontend/discourse/app`.
- Тесты: `spec/` зеркалит `app/` (`spec/models`, `spec/services`, `spec/requests`, `spec/system`); у плагина свой `plugins/chat/spec/`; фронтенд `frontend/discourse/tests/`.
- Границы: `CODEOWNERS` (читал только начало файла: две зоны, разработка платформы и инструменты миграций); в `AGENTS.md` правила: в ядре не называть возможности плагинов; бизнес-логику выносить из контроллеров в `app/services` (только классы `Service::Base`).
- Миграции: `db/migrate/` (1774), `db/post_migrate/` (34), `db/structure.sql`; у плагинов `plugins/<имя>/db/migrate`.
- Конфиг: `config/site_settings.yml`, `config/discourse_defaults.conf`, `config/*.sample`.
- Доки: `docs/developer-guides/docs/03-code-internals/` (сервисы, UI-kit, BEM), `plugins/voice/docs/ARCHITECTURE.md`.

**mastodon/mastodon** (Rails)
- Верх: `app/`, `config/`, `db/`, `lib/`, `spec/`, `streaming/` (отдельное Node-приложение), `chart/`, `docs/`.
- Модули: чисто по слоям: `app/{models 271, controllers 417, services 105, workers 133, policies 51, serializers 156, presenters, validators}`.
- Тесты: `spec/` зеркалит `app/` (`spec/models`, `spec/services`, `spec/requests`, `spec/policies`, `spec/workers`).
- Границы: линтер стиля (`.rubocop/`), правил границ нет, `CODEOWNERS` нет.
- Миграции: `db/migrate/` (547), `db/post_migrate/` (82), `db/schema.rb`. Конфиг: `.env.production.sample`, `config/*.yml`.
- Доки: `docs/DEVELOPMENT.md`, `FEDERATION.md` в корне.

**zulip/zulip** (Django + TS)
- Верх: `zerver/`, `zproject/`, `web/`, `analytics/`, `corporate/`, `zilencer/`, `docs/`, `tools/`, `scripts/`, `puppet/`.
- Модули: `zerver/models/` (30 файлов по теме), `zerver/lib/` (162), `zerver/actions/`, `zerver/views/`, `zerver/webhooks/` (одна папка на интеграцию, 1628 файлов).
- Тесты: `zerver/tests/test_<тема>.py` (152, плоско), `web/tests`, `web/e2e-tests`.
- Границы: договорённость и проверки в `tools/` (проверка шаблонов, капитализации, схем).
- Миграции: `zerver/migrations/` (790, четыре цифры, сжаты в `0001_squashed_0569`); `tools/renumber-migrations`, `tools/test-migrations`; `docs/subsystems/schema-migrations.md`.
- Конфиг: `zproject/{default_settings,dev_settings,test_settings,prod_settings_template}.py`.
- Доки: `docs/` по темам (`subsystems`, `testing`, `production`, `contributing`, `translating`).

**calcom/cal.com** (Next.js/tRPC, Turbo)
- Верх: `apps/{web,api,docs}`, `packages/{features,lib,prisma,trpc,ui,app-store,emails,embeds,platform,...}`, `specs/`, `agents/`, `.github/CODEOWNERS`.
- Модули: `packages/features/<72 фичи>` (bookings 297 файлов, availability, calendars, ...); общее — `packages/lib`, UI — `packages/ui`.
- Тесты: рядом (`*.test.ts`, 440) и `apps/**/__tests__`, e2e Playwright, `__checks__/` (Checkly).
- Границы: `biome.json` `noRestrictedImports` по пакетам; `agents/rules/architecture-{feature-boundaries,circular-dependencies,vertical-slices,features-modules}.md`; `agents/rules/reference-file-locations.md` — таблица «что где лежит».
- Миграции: Prisma, `packages/prisma/migrations/` (1192 файла), `packages/prisma/schema.prisma`.
- Конфиг: `.env.example`, `.env.appStore.example`.
- Доки: `agents/` (правила и навыки), `specs/`, `SPEC-WORKFLOW.md`, `docs/api-reference/`.

**getsentry/sentry** (Django + React)
- Верх: `src/sentry/` (155 папок-доменов), `static/app` (9984 файла), `tests/`, `migrations_lockfile.txt`, `devservices/`, `self-hosted/`.
- Модули: домены (`integrations` 656, `api` 382, `auth` 131, `issues`, `grouping`, ...); внутри `api/endpoints`, `api/serializers/models`.
- Тесты: `tests/sentry/<домен>` зеркалит `src/sentry/<домен>` (137 папок); отдельно `tests/acceptance`, `tests/snuba`, `tests/js`.
- Границы: `.github/CODEOWNERS` с пометкой, что общие папки без команды-владельца — плохая практика, `.codeowners-config.yml`; 8 вложенных `AGENTS.md`/`CLAUDE.md` (`src/`, `static/`, `tests/`, `src/sentry/issues/*`).
- Миграции: `src/sentry/migrations/` (101, четыре цифры) + `migrations_lockfile.txt` + CI `migrations.yml`, `migrations-drift.yml`, `migration-check.sh`.
- Доки: `docs/` пуст, разработческая документация вне репозитория (develop.sentry.dev), в репозитории — `AGENTS.md`.

**mattermost/mattermost** (Go + React)
- Верх: `server/`, `webapp/`, `api/`, `e2e-tests/`, `docs/`, `tools/`, `CODEOWNERS`.
- Модули: `server/channels/{api4,app,store,jobs,web,wsapi,db,utils}`; слои `api4 → app → store`; `server/public/{model,plugin,pluginapi}` — публичный модуль Go; `server/einterfaces`, `server/enterprise`. `webapp/channels/src/{components,actions,reducers,selectors}`.
- Тесты: рядом `*_test.go` (2706) и `store/storetest/` (общие проверки для всех реализаций хранилища).
- Границы: `server/.golangci.yml` (`depguard` только запрещает `math/rand`); границы — интерфейсами; `CODEOWNERS`; `server/AGENTS.md`, `webapp/AGENTS.md`.
- Миграции: `server/channels/db/migrations/postgres/000001...000235` (up/down), `migrations.list`, `make new-migration`, `make migrations-extract`; README с правилами.
- Конфиг: `server/config/`. Доки: `docs/` (пользовательские), `server/channels/README.md`.

**n8n-io/n8n** (TS, pnpm, Turbo)
- Верх: `packages/`, `docs/`, `scripts/`, `.agents/`, `.boundaries-baseline.json`, `OWNERS`, `knip.ts`.
- Модули: `packages/cli/src/modules/<38 фич>/` с суффиксами файлов `*.module.ts`, `*.controller.ts`, `*.service.ts`, `*.entity.ts`, `*.repository.ts`; общее — `packages/@n8n/*` (57 внутренних пакетов), `packages/core`, `packages/workflow`.
- Тесты: рядом (7496) и `packages/cli/test/`; отдельные конфиги для миграционных тестов (`vitest.config.migration.ts`).
- Границы: `turbo boundaries` + `scripts/check-boundaries.mjs` + `.boundaries-baseline.json`; `packages/@n8n/eslint-config/src/configs/`; `knip.ts` (неиспользуемое); 31 вложенный `AGENTS.md`; `.agents/review-rules/` по областям.
- Миграции: `packages/@n8n/db/src/migrations/{common,postgresdb,sqlite}/`; индекс генерируется, `migration-index-sync.ts` проверяет.
- Доки: `docs/adr/`, `docs/ADR_TEMPLATE.md`, `docs/db.md`, `docs/generated/postgres-schema/` (генерируется `.tbls.postgres.yml`), `ARCHITECTURE.md` у отдельных пакетов.

**supabase/supabase** (Turbo, Next.js)
- Верх: `apps/{studio,docs,www,design-system,ui-library,...}`, `packages/{ui,ui-patterns,pg-meta,shared-data,...}`, `supabase/`, `docker/`, `examples/`, `e2e/`.
- Модули: приложение на папку, общее — пакеты. `examples/` — самостоятельные запускаемые примеры, у части свои `supabase/migrations`.
- Тесты: рядом (980). Границы: `knip.jsonc`, `.github/CODEOWNERS`, вложенные `AGENTS.md` (`apps/studio`, `apps/docs`, `apps/kb`).
- Миграции: `supabase/migrations/` (метка времени). Конфиг: `docker/.env.example`, `supabase/config.toml`.

### Шаблон и фреймворки

**fastapi/full-stack-fastapi-template**
- Верх: `backend/`, `frontend/`, `compose.yml`, `compose.override.yml`, `.env`, `scripts/`, `hooks/`, `development.md`, `deployment.md`.
- Модули: `backend/app/{api/routes, core, models.py, crud.py, alembic}` — слои; `frontend/src/{routes, components, hooks, client}`, `client` генерируется.
- Тесты: `backend/tests/{api/routes, crud, utils}` зеркалит `app`; `frontend/tests/*.spec.ts` (Playwright).
- Границы: нет. Миграции: Alembic, `backend/app/alembic/versions/<хеш>_<имя>.py`. Конфиг: `.env` с `changethis`.
- Это самый маленький проект в выборке (252 файла) и самый близкий к нашему размеру. Всё держится на: трёх папках слоёв, зеркальных тестах, одном файле моделей, генерации клиента.

**django/django**
- Верх: `django/`, `tests/`, `docs/`, `scripts/`, `extras/`, `js_tests/`.
- Модули: подсистемы (`db`, `forms`, `http`, `template`, `views`, `core`, `utils`) + 16 приложений в `django/contrib/` (у каждого свои `migrations/`, `locale/`, `templates/`).
- Тесты: `tests/<фича>/` (222 папки, вроде `tests/auth_tests`, `tests/admin_views`), зеркала нет.
- Границы: нет линтера, `CODEOWNERS` нет. Доки: `docs/{ref,topics,howto,internals,releases}`, `docs/internals/organization.txt`.

**vercel/next.js**
- Верх: `packages/`, `crates/`, `turbopack/crates/`, `test/`, `examples/` (232), `docs/`, `errors/`, `contributing/`, `.github/CODEOWNERS`.
- Модули: `packages/next/src/{build, server, client, shared, lib, ...}`; Rust в `crates/` и `turbopack/crates/` (55).
- Тесты: `test/{unit, development, production, e2e}` по виду запуска; рядом ещё 2298 файлов; манифесты `test/*-manifest.json` решают, что где запускать.
- Пример (`examples/blog-starter`): `src/{app, interfaces, lib}`, `_posts/`, `README.md`, `package.json` — самодостаточная папка. Для сравнения `examples/with-jest` кладёт тесты и в `__tests__/`, и рядом с `page.tsx`.
- Границы: `AGENTS.md` в нескольких местах; `CODEOWNERS`.

### Инфраструктура

**kubernetes/kubernetes**
- Верх: `cmd/` (26 бинарников), `pkg/` (kubelet 952, scheduler 316, controller 780, registry 684, ...), `staging/src/k8s.io/*` (34 публикуемых модуля), `plugin/`, `test/`, `hack/` (125 скриптов), `api/`, `vendor/`, `OWNERS`.
- Тесты: рядом (3557) и `test/{e2e, integration, e2e_node, conformance, fuzz}`.
- Границы: `.import-restrictions` (70), `cmd/import-boss`, `OWNERS` (590), `hack/.import-aliases`, `hack/unwanted-dependencies.json`; `ARCHITECTURE.md` в `staging/src/k8s.io/apiserver` и `client-go`.
- Миграций нет; версии API в `pkg/apis`. Журнал изменений: `CHANGELOG/CHANGELOG-1.xx.md`.
- Генерация: `hack/update-*.sh` и `hack/verify-*`.

**hashicorp/terraform**
- Верх: `internal/` (63 пакета), `docs/`, `.changes/`, `testing/`, `scripts/`, `website/`, `CODEOWNERS`.
- Модули: домены (`configs`, `states`, `plans`, `terraform` 1533 файла, `command` 2525, `backend`, `stacks` 859, `providers`, `addrs`).
- Тесты: рядом `*_test.go`. Границы: компилятор Go (`internal/`), `CODEOWNERS`.
- Доки: `docs/architecture.md`, `docs/planning-behaviors.md`, `docs/resource-instance-change-lifecycle.md`. Журнал: `.changes/` (changie), фрагмент на изменение.

**grafana/grafana**
- Верх: `pkg/` (Go), `public/app/` (React), `apps/` (21 приложение платформы), `packages/` (библиотеки `@grafana/*`), `contribute/`, `docs/`, `conf/`, `devenv/`, `.golangci.yml`.
- Модули: `pkg/services/<77 сервисов>`; `public/app/features/<60 фич>`. Правило из `contribute/backend/package-hierarchy.md`: типы и интерфейсы в корне пакета, реализация в подпакете `<имя>impl`.
- Тесты: рядом (5467 файлов), e2e в `e2e-playwright/`.
- Границы: `depguard` в `.golangci.yml`, `.madgerc` (круговые зависимости JS), `CODEOWNERS`, 12 вложенных `AGENTS.md`.
- Миграции: `pkg/services/sqlstore/migrations/*_mig.go` + золотой файл. Конфиг: `conf/defaults.ini`, `conf/sample.ini`.

**prometheus/prometheus**
- Верх: пакеты на подсистему в корне (`promql`, `scrape`, `storage`, `tsdb`, `rules`, `notifier`, `discovery`, `model`, `web`), `cmd/{prometheus,promtool}`, `documentation/`, `docs/`, `CODEOWNERS`, `MAINTAINERS.md`.
- Тесты: рядом `*_test.go`. Границы: `.golangci.yml` запрещает отдельные пакеты (`sync/atomic`, `regexp`, `io/ioutil`), границ между подсистемами нет; `CODEOWNERS` по подсистемам, синхронизирован с `MAINTAINERS.md`.
- Доки: `documentation/internal_architecture.md`, `tsdb/docs/`. Миграций БД нет.

### Базы и брокеры

**postgres/postgres**
- Верх: `src/{backend, include, bin, common, interfaces, pl, port, test, tools}`, `contrib/` (65 расширений), `doc/src/sgml`.
- Модули: `src/backend/<подсистема>` (`access`, `executor`, `optimizer`, `parser`, `storage`, `utils`, `replication`, ...); заголовки в `src/include/` повторяют структуру.
- Тесты: `src/test/{regress, isolation, recovery, ssl, modules, ...}`; ожидаемые результаты лежат файлами (`src/test/regress/expected/`).
- README в подсистемах (109 файлов): `src/backend/access/heap/README.HOT`, `.../brin/README`. Границ в линтере нет, `CODEOWNERS` нет.
- Конфиги-образцы: `src/backend/utils/misc/postgresql.conf.sample`, `src/backend/libpq/pg_hba.conf.sample`.

**redis/redis**
- Верх: `src/` (плоско, один файл на подсистему: `acl.c`, `aof.c`, `db.c`, `t_hash.c`, ...), `tests/`, `deps/` (jemalloc, lua, hiredis), `utils/`, `redis.conf`.
- Данные как код: `src/commands/*.json` (468) → `commands.def` скриптом `utils/generate-command-code.py`.
- Тесты: `tests/{unit, integration, modules, sentinel}` (Tcl), по виду проверки. Границ в линтере нет; `CODEOWNERS` нет.

**apache/kafka**
- Верх: `clients`, `core`, `streams`, `connect`, `metadata`, `raft`, `storage`, `server`, `group-coordinator`, `coordinator-common`, ... — модули Gradle; `checkstyle/`, `docs/`, `config/`, `tests/` (системные).
- Тесты: в каждом модуле `src/main` и `src/test` с одинаковыми пакетами; отдельные модули `*-integration-tests`.
- Границы: `checkstyle/import-control-<модуль>.xml`. В корневом `AGENTS.md` таблица раскладки репозитория (путь → за что отвечает).

### Десктоп и клиенты

**microsoft/vscode**
- Верх: `src/vs/{base, platform, editor, workbench, code, server, sessions}`, `extensions/` (107), `build/`, `test/`, `.eslint-plugin-local/`, `.github/instructions/`.
- Модули: слой × среда: внутри слоя папки `common`, `browser`, `node`, `electron-browser`, `electron-main`. Фичи: `src/vs/workbench/contrib/<101>`.
- Тесты: в каждой папке среды подпапка `test/` (`src/vs/base/test/{common,browser,node}`, `contrib/debug/test/browser`); сквозные в `test/{unit, integration, smoke}`.
- Границы: `code-layering.ts`, `code-import-patterns.ts`; описание — `.github/instructions/source-code-organization.instructions.md`; `CODEOWNERS`; вложенные `AGENTS.md`.

**electron/electron**
- Верх: `shell/{browser, common, renderer, utility, app, services}` (C++), `lib/{browser, common, renderer, ...}` (TS), `spec/`, `docs/`, `patches/`, `BUILD.gn`, `DEPS`, `filenames.gni`.
- Тесты: `spec/api-*.spec.ts` плоско. Доки: `docs/api/` (API по модулям), `docs/development/source-code-directory-structure.md`, `docs/development/creating-api.md` (по шагам, что менять при новом API), `docs/CLAUDE.md`, `spec/CLAUDE.md`.
- Чужое: `patches/<проект>/*.patch` + `patches/config.json`. `filenames.gni` — список исходников, его правят при добавлении файла.

**bitwarden/clients**
- Верх: `apps/{web, browser, desktop, cli}`, `libs/` (45), `bitwarden_license/`, `docs/`, `e2e/`.
- Модули: доменные папки `auth`, `vault`, `billing`, `key-management`, `platform`, `tools` повторяются и в `apps/*/src`, и в `libs/`. Общий код — пакеты `@bitwarden/*`.
- Тесты: рядом `*.spec.ts` (1471). Границы: `eslint.config.mjs` с `buildNoRestrictedImports`, `CODEOWNERS` по командам (`@bitwarden/team-auth-dev` и т.д.), 10 вложенных `CLAUDE.md`, `libs/auth/README.md`.
- Клиентские миграции состояния: `libs/common/src/state-migrations`.

### Компиляторы и инструменты

**rust-lang/rust-analyzer**
- Верх: `crates/` (36), `xtask/`, `lib/`, `docs/book/`.
- Модули: крейт на стадию: `parser` → `syntax` → `base-db` → `hir-def` → `hir-ty` → `hir` → `ide-*` → `rust-analyzer`.
- Тесты: внутри файлов и `src/tests/`, фикстуры в крейте `test-fixture`.
- Границы: Cargo + инварианты в `docs/book/src/contributing/architecture.md`; `xtask/src/tidy.rs` проверяет форму манифестов, лицензии, атрибуты тестов.

**astral-sh/ruff**
- Верх: `crates/` (55+), `python/`, `scripts/`, `docs/`, `CODEOWNERS`, `.cargo/deny.toml`.
- Модули: `crates/ruff_linter/src/rules/<плагин>/{mod.rs, rules/<правило>.rs, settings.rs}` (3323 файла); фикстуры `crates/ruff_linter/resources/test/fixtures/<плагин>/<КОД>.py`; снимки `snapshots/`.
- Что менять при новом правиле — делает скрипт `scripts/add_rule.py`; новый плагин — `scripts/add_plugin.py`; схема настроек `ruff.schema.json` генерируется.

### Платформа интеграций

**home-assistant/core**
- Верх: `homeassistant/{components (1535 интеграций), helpers, util, auth}`, `tests/components/<домен>`, `script/{hassfest, scaffold, ...}`, `CODEOWNERS` (генерируется).
- Модуль-интеграция (`homeassistant/components/hue/`): `__init__.py`, `config_flow.py`, `manifest.json` (`domain`, `codeowners`, `requirements`, `dependencies`), `strings.json`, `services.yaml`, `icons.json`, платформы (`light.py`, `sensor.py`, ...).
- Тесты: `tests/components/hue/` — тот же набор файлов с префиксом `test_`.
- Границы: `script/hassfest/` (39 проверок: `manifest.py`, `dependencies.py`, `codeowners.py`, `requirements.py`, `translations.py`, `quality_scale.py`), `tests/test_circular_imports.py`, `.strict-typing` (список модулей со строгой типизацией).
- Новая интеграция: `python -m script.scaffold` (`script/scaffold/`, 79 файлов шаблонов).

---

## 7. Что брать в наш набор

Правки в `assets/spec-template.md`. Не больше десяти, по важности. Все они про одно: убрать из шаблона то, что держится на словах, и дать вместо этого то, что можно проверить скриптом.

1. **«Ось деления» одной строкой в «Корнях».** Спросить заранее: делим по слою, по фиче или слой сверху, фичи внутри. Сейчас шаблон молчит, и агенты выбирают сами.
   - Примеры: слой сверху, фичи внутри — vscode (`workbench/contrib/<фича>`), grafana (`pkg/services/<сервис>`), discourse (`app/` + `plugins/<имя>`). Чисто по слою — mastodon, fastapi-template (подходит для малого проекта). Только по фиче — HA, cal.com `packages/features`.

2. **Заменить колонку «Кому можно вызывать» на две: «Публичный вход» (один файл) и «Может импортировать» (список модулей).** Плюс строка над таблицей «Слои сверху вниз: …, вверх не импортируем».
   - «Кому можно вызывать» превращается в проверку наоборот, и поэтому по ней нельзя написать правило для линтера: правило пишется как «модуль A импортирует только из списка».
   - Примеры: cal.com (`index.ts` фичи + `noRestrictedImports`), vscode (`.contribution.ts` + common-API, слои), kafka (`import-control-<модуль>.xml` — список разрешённого на каждый модуль), HA (`manifest.json` `dependencies`), grafana (корневой пакет сервиса + подпакет `<имя>impl`).

3. **Раздел «Инварианты» (3–5 строк «X ничего не знает про Y») над таблицей модулей, и каждому — проверку.** Для старого кода — храповик: счётчик нарушений в файле, CI падает, если он вырос.
   - Примеры: rust-analyzer `architecture.md` (строки-инварианты), kubernetes `pkg/.import-restrictions` (запрет `pkg/` на зависимость от `cmd/`), n8n `.boundaries-baseline.json` (110) + `scripts/check-boundaries.mjs`.
   - «Тест границ» из шаблона оставить; добавить в него «в живом проекте — храповик».

4. **Строка «Тесты» в «Корнях»: схема (рядом / зеркало / по виду проверки) и правило имени.** Для зеркальной схемы — проверка «у каждой папки модуля есть папка тестов» (в выборке такой проверки я не нашёл ни у одного проекта, это предложение).
   - Примеры: HA `tests/components/<домен>`, sentry `tests/sentry/<модуль>`, fastapi-template `backend/tests/api/routes/test_<x>.py`; рядом — kubernetes, terraform, n8n.
   - Мелочь, но экономит агентам поиск: «тест для `app/services/foo.py` — это `tests/services/test_foo.py`».

5. **Колонка «Владелец» в карте (необязательная) и «Локальный гид» у модулей крупнее порога.** Гид — короткий `AGENTS.md` в папке модуля: пути, правила, «как добавить X». Не копия карты.
   - Примеры: n8n (31 вложенный `AGENTS.md`), sentry (`src/AGENTS.md` с деревом решений «добавляю эндпоинт → файлы»), bitwarden (`apps/web/CLAUDE.md`), grafana, `CODEOWNERS` (16 из 24).
   - Для малого проекта порог — один гид на весь `backend/` и на `frontend/`; владельцы — роли, а не люди.

6. **Строка «Не править руками» в «Корнях»: сгенерированное, чужое, с командой пересборки и проверкой.**
   - Примеры: fastapi-template (`frontend/src/client/*.gen.ts`, `scripts/generate-client.sh`), cal.com (`openapi.json`), mattermost (`migrations.list`, `make generated`), HA (`CODEOWNERS`, `requirements_all.txt` из `script/hassfest`), kubernetes (`vendor/`, `staging/`, `hack/update-*` и `hack/verify-*`), electron (`patches/`), redis (`src/commands/*.json` → `commands.def`).

7. **«Данные»: колонка «Файл схемы» и строка «Начальные данные — отдельно от миграций».**
   - Файл схемы — один источник: discourse `db/structure.sql`, mastodon `db/schema.rb`, cal.com `packages/prisma/schema.prisma`, n8n `docs/generated/postgres-schema/`.
   - Начальные данные: discourse `db/fixtures/` и CI-проверка «после миграций на чистой базе строк нет» (`db:check_structure_dump`), mastodon `db/seeds.rb`.
   - Из шаблона убрать формулировку «как параллельные задачи не берут один номер» без механизма (см. пункт 8).

8. **«Миграции»: фиксированный набор полей вместо свободной фразы.** Поля: имя и нумерация (метка времени из генератора или порядковый номер); **файл-вершина** (путь, где записана последняя миграция, его правит каждая новая); команда создания; проверка в CI; правило «выложенную не правим»; правило «разрушающее — в два этапа».
   - Для нас лучше всего подходит «файл-вершина»: параллельные задачи правят одну строку, второй получает конфликт git и знает, что делать (rebase, перегенерировать). Примеры: sentry `migrations_lockfile.txt` (текст в самом файле объясняет, как разрешить), mattermost `migrations.list` + требование слить свежий код перед PR, grafana `testdata/migration_ids.txt` (перегенерирует человек, агентам запрещено), n8n сгенерированный индекс.
   - Если нужны метки времени — «никогда не писать руками, только генератором» (discourse). Если порядковые номера — инструмент пересчёта (zulip `tools/renumber-migrations`).
   - Тим лиду: в задание, которое создаёт миграцию, писать «правишь файл-вершину», тогда две такие задачи нельзя пометить как независимые.
   - Разрушающие изменения: discourse `db/migrate` и `db/post_migrate`, mattermost (колонку меняют за несколько выпусков).

9. **«Что менять, когда добавляешь»: добавить колонку «Чем проверить, что ничего не забыто» и строки «Модуль», «Эндпоинт/команду», «Сгенерированное», «Строку интерфейса (перевод)».** Сейчас строки только «Настройка / Маршрут / Миграция / Право».
   - Примеры: sentry `src/AGENTS.md` (дерево «добавляю эндпоинт» → endpoint, urls, serializer, тест, apidocs), HA (`script/scaffold` создаёт заготовку интеграции, `script/hassfest` проверяет манифест, зависимости, переводы), ruff (`scripts/add_rule.py`), redis (новая команда → `src/commands/<cmd>.json` → генерация `commands.def`), electron (`docs/development/creating-api.md`).
   - Проверка — команда или тест, а не «посмотреть»: hassfest, `make migrations-extract`, `tools/test-migrations`, `hack/verify-*`.

10. **«Настройку» разложить на три файла: значения по умолчанию, образец с заглушками, документация. Секретов в репозитории нет, в образце — заглушки.**
    - Примеры: grafana `conf/defaults.ini` + `conf/sample.ini`, zulip `default_settings.py` + `prod_settings_template.py`, cal.com `.env.example`, fastapi-template `.env` (`changethis`), discourse `config/site_settings.yml` + `config/discourse_defaults.conf`.
    - В строке «Настройка» таблицы «Что менять» тогда: схема/дефолт, образец, документ, место чтения в коде — четыре пути, а не «см. конфиг».

### Что не брать

- Для малого проекта не брать весь набор разом: из 24 разобранных работают так только очень большие (kubernetes, vscode, n8n). Минимум, который видно и у маленького fastapi-template, и у больших: слои по папкам, зеркальные тесты, генерируемые файлы с командой, пример конфига, файл-вершина миграций, один автоматический тест на импорты.
- `CODEOWNERS` на каждую папку и `OWNERS` на каждый каталог (kubernetes) — не для нас; роли и так разведены скилами.
- Свой валидатор манифестов (HA `hassfest`) — только если у нас появятся плагины или интеграции с общим форматом.
