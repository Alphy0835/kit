# Безопасник: как учат профессии и какие нормативы считаются основой

Дата сбора: 16.10.2026. Страницы открыты напрямую (WebFetch/WebSearch), ничего не скачивалось и не устанавливалось. Тексты не копированы: пересказ своими словами. Страницы читала быстрая модель-пересказчик, поэтому номера требований и списки сверены по выдаче, но не по печатному тексту. Что не открылось — в разделе 7.

Сокращения источников (ссылки даны в тексте рядом с каждым утверждением):
- T10 = [OWASP Top 10:2025](https://top10.owasp.org/2025/0x00_2025-Introduction)
- ASVS = [OWASP ASVS 5.0.0, май 2025](https://github.com/OWASP/ASVS), главы лежат в [папке 5.0/en](https://github.com/OWASP/ASVS/tree/master/5.0/en)
- WSTG = [Web Security Testing Guide v4.2](https://wstg.owasp.org/v4.2/)
- CS = [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/Glossary.html)
- LLM10 = [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)
- API10 = [OWASP API Security Top 10 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10)
- CWE25 = [CWE Top 25 за 2025](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)
- SSDF = [NIST SP 800-218 v1.1](https://csrc.nist.gov/pubs/sp/800/218/final)
- PS = [PortSwigger Web Security Academy](https://portswigger.net/web-security/all-topics)

---

## 0. Что считать «последним выпуском» (на 16.10.2026)

- OWASP Top 10 — выпуск 2025. Десять пунктов: A01 Broken Access Control (в него вошёл SSRF), A02 Security Misconfiguration, A03 Software Supply Chain Failures (расширенный прежний «уязвимые компоненты»), A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging & Alerting Failures, A10 Mishandling of Exceptional Conditions (новый). Источник: [T10, введение](https://top10.owasp.org/2025/0x00_2025-Introduction).
- ASVS — версия 5.0.0, май 2025. Источник: [репозиторий ASVS](https://github.com/OWASP/ASVS). Семнадцать глав: кодирование и очистка, проверка данных и бизнес-логика, фронтенд, API и веб-сервисы, файлы, аутентификация, сессии, авторизация, самодостаточные токены, OAuth/OIDC, криптография, защищённая связь, конфигурация, защита данных, безопасное кодирование и архитектура, журналы и ошибки, WebRTC. Источник списка: [папка 5.0/en](https://github.com/OWASP/ASVS/tree/master/5.0/en).
- WSTG — v4.2 (версия 5.0 ещё в разработке). Источник: [страница проекта](https://owasp.org/www-project-web-security-testing-guide/).
- OWASP Top 10 for LLM Applications — выпуск 2025: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded Consumption. Источник: [LLM10](https://genai.owasp.org/llm-top-10/).
- OWASP API Security Top 10 — выпуск 2023: API1 Broken Object Level Authorization, API2 Broken Authentication, API3 Broken Object Property Level Authorization, API4 Unrestricted Resource Consumption, API5 Broken Function Level Authorization, API6 Unrestricted Access to Sensitive Business Flows, API7 SSRF, API8 Security Misconfiguration, API9 Improper Inventory Management, API10 Unsafe Consumption of APIs. Источник: [API10](https://api-security.owasp.org/editions/2023/en/0x11-t10).
- SAMM — версия 2.2.0; пять функций (управление, проектирование, реализация, проверка, эксплуатация) и пятнадцать практик. Источники: [проект](https://owasp.org/www-project-samm/), [модель](https://owaspsamm.org/model/).
- CWE Top 25 — за 2025 год; на странице нет более нового списка. Первая десятка: XSS (79), SQL-инъекция (89), CSRF (352), отсутствие проверки прав (862), запись за границы (787), обход пути (22), use-after-free (416), чтение за границы (125), команды ОС (78), внедрение кода (94). Источник: [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html).
- NIST SSDF — утверждена v1.1 (февраль 2022) ([NIST](https://csrc.nist.gov/pubs/sp/800/218/final)); черновик Rev.1 (версия 1.2) вышел 17.12.2025, приём замечаний закрыт 30.01.2026, окончательной версии на странице нет ([черновик](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd)).

---

## 1. Чему учат по порядку

### 1.1. Какие программы просмотрены

Восемь источников, где темы видны по первоисточнику (считаю, сколько из них называют тему):

| Метка | Источник | Что это |
|---|---|---|
| PS | [Web Security Academy](https://portswigger.net/web-security/all-topics) | бесплатный учебник, 31 тема |
| WSTG | [WSTG v4.2](https://wstg.owasp.org/v4.2/) | руководство по тестированию, 12 групп |
| ASVS | [ASVS 5.0](https://github.com/OWASP/ASVS/tree/master/5.0/en) | перечень требований, 17 глав |
| T10 | [Top 10:2025](https://top10.owasp.org/2025/0x00_2025-Introduction) | десять классов рисков |
| API | [API Top 10 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10) | десять рисков API |
| CWE | [CWE Top 25 2025](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html) | 25 слабостей |
| OSCP | [PEN-200](https://www.offsec.com/courses/pen-200/) | платный курс пентестера, на странице — только области тем |
| OSWE | [WEB-300](https://www.offsec.com/courses/web-300/) | платный курс по веб, на странице — только названные темы |

Важно: PS, OSCP и OSWE — это «как учат». WSTG — «как проверяют». ASVS, T10, API, CWE — «что считается ошибкой». Совпадение обучения и нормативов и есть основа.

### 1.2. Порядок обучения (как строит PortSwigger)

Страница тем у PortSwigger идёт так: сначала серверные (SQL-инъекция, аутентификация, обход пути, внедрение команд, бизнес-логика, раскрытие информации, управление доступом, загрузка файлов, гонки, SSRF, XXE, NoSQL, тестирование API, обман кэша), потом клиентские (XSS, CSRF, CORS, clickjacking, DOM, WebSocket), потом сложные (десериализация, атаки на LLM, GraphQL, внедрение шаблонов, отравление кэша, заголовок Host, смешивание запросов, OAuth, JWT, prototype pollution, «основные навыки»). Источник: [список тем](https://portswigger.net/web-security/all-topics). Начальный путь «серверные уязвимости (новичок)» идёт так: обход пути, управление доступом, аутентификация, SSRF, загрузка файлов, внедрение команд ОС, SQL-инъекция. Источник: [путь для новичка](https://portswigger.net/web-security/learning-paths/server-side-vulnerabilities-apprentice). Остальные пути не открылись.

WSTG ведёт по другому порядку: сбор сведений, конфигурация и развёртывание, управление учётными записями, аутентификация, авторизация, сессии, проверка ввода, обработка ошибок, слабая криптография, бизнес-логика, клиентская часть, API. Источник: [WSTG v4.2](https://wstg.owasp.org/v4.2/).

Российские курсы (только вторичные пересказы, программа с сайта не открылась): у Яндекс Практикума в карточках курса веб-пентеста названы OWASP, HTTP/WebSocket, Burp Suite, SQLMap, Kali, Shodan, криптография и элементы DevSecOps; у Skillbox «Пентестер с нуля» — шесть модулей, атаки на инфраструктуру и Active Directory, мониторинг и реагирование. Источник: [обзор на Хабре](https://habr.com/ru/articles/1018808) (вторичный) и [поиск по Skillbox](https://career.habr.com/courses/6281-pentester-s-nulya) (вторичный). HackerU не искал.

### 1.3. Список тем и в скольких из восьми они названы

Правило подсчёта: тема считается названной, если я видел её на странице (для WSTG — на уровне названия группы, подтем не открывал; это отмечено «гр.»).

| № | Тема | Где названа | Сколько из 8 |
|---|---|---|---|
| 1 | Аутентификация | PS, WSTG (4.4), ASVS (V6), T10 (A07), API (API2), CWE (306), OSCP (подбор паролей), OSWE (обход аутентификации) | 8 |
| 2 | SQL-инъекция | PS, WSTG (гр. ввод), ASVS (1.2.4), T10 (A05), CWE (89), OSCP, OSWE (слепая) | 7 |
| 3 | XSS | PS, WSTG (гр. клиент/ввод), ASVS (1.2.1, 3.2.2), T10 (A05, по [карте CS](https://cheatsheetseries.owasp.org/IndexTopTen.html) для 2021), CWE (79), OSCP, OSWE | 7 |
| 4 | Раскрытие информации, ошибки, неверные настройки | PS, WSTG (4.2, 4.8), ASVS (V13, V16), T10 (A02, A10), API (API8), CWE (200) | 6 |
| 5 | Внедрение команд ОС | PS, WSTG (гр. ввод), ASVS (1.2.5), T10 (A05), CWE (78, 77), OSCP | 6 |
| 6 | Управление доступом и права на объект (IDOR) | PS, WSTG (4.5), ASVS (V8), T10 (A01), API (API1, API3, API5), CWE (862, 863, 639, 284) | 6 |
| 7 | SSRF | PS, ASVS (13.2.4, 13.2.5), T10 (A01), API (API7), CWE (918), OSWE | 6 |
| 8 | Бизнес-логика и гонки | PS (оба), WSTG (4.10), ASVS (V2, 15.4), T10 (A06), API (API6) | 5 |
| 9 | Сессии и токены (в т.ч. JWT, OAuth) | PS (JWT, OAuth), WSTG (4.6), ASVS (V7, V9, V10), OSWE (угон сессии) | 4 |
| 10 | Тестирование API (REST, GraphQL) | PS, WSTG (4.12), ASVS (V4), API | 4 |
| 11 | Загрузка файлов и обход пути | PS, ASVS (V5), CWE (22, 434), OSCP | 4 |
| 12 | Криптография | WSTG (4.9), ASVS (V11), T10 (A04), OSCP | 4 |
| 13 | CSRF | PS, WSTG (гр. клиент), ASVS (3.5), CWE (352) | 4 |
| 14 | Десериализация | PS, T10 (A08, по [карте CS](https://cheatsheetseries.owasp.org/IndexTopTen.html)), CWE (502), OSWE (.NET) | 4 |
| 15 | Клиентская часть: CORS, clickjacking, DOM, WebSocket | PS, WSTG (4.11), ASVS (V3, 4.4) | 3 |
| 16 | Сбор сведений, разведка | WSTG (4.1), OSCP, PS (раскрытие информации) | 3 |
| 17 | Исчерпание ресурсов, защита от перебора | ASVS (2.4.1, 6.3.1), API (API4), CWE (770) | 3 |
| 18 | Цепочка поставок, зависимости | T10 (A03), ASVS (V15), [LLM10](https://genai.owasp.org/llm-top-10/) (LLM03) | 3 |
| 19 | Журналирование и реагирование | T10 (A09), ASVS (V16) | 2 |
| 20 | Атаки на LLM и агентов | PS (Web LLM attacks), LLM10 | 2 (вне восьми — свой список OWASP) |
| 21 | Сложные: смешивание запросов, отравление кэша, SSTI, prototype pollution, XXE, NoSQL, Host | PS (все), ASVS (XXE 1.5.1, prototype pollution 15.3) | 2 |
| 22 | Память: переполнение, use-after-free, чтение/запись за границы | CWE (787, 416, 125, 120, 121, 122, 476), OSWE (разработка эксплойтов) | 2 |
| 23 | Повышение прав в ОС, Active Directory, обход антивирусов, облако | OSCP | 1 |

Вывод для подборки: ядро, которое есть почти везде (в пяти и более источниках) — аутентификация, права доступа, инъекции (SQL, команды ОС, XSS), SSRF, раскрытие информации, бизнес-логика. Темы 18, 19 и 20 (зависимости, журналы, LLM) в учебниках почти не учат, но нормативы их требуют — безопасник должен брать их из нормативов, а не из курсов.

Страницы курсов OffSec показывают только области, не полный состав: у PEN-200 — 20+ модулей, у WEB-300 — 17 модулей; платные ([PEN-200](https://www.offsec.com/courses/pen-200/), [WEB-300](https://www.offsec.com/courses/web-300/)).

---

## 2. Что из этого касается нашего стека

Условные обозначения: «код» — проверка чтением кода и тестами; «стенд» — проверка на запущенном локальном стенде (боевой сервер не трогаем). Колонка «как проверить» — моё предложение по методике, опирается на группы WSTG ([WSTG v4.2](https://wstg.owasp.org/v4.2/)) и разделы PortSwigger ([темы](https://portswigger.net/web-security/all-topics)); самих тестов WSTG я не открывал.

### 2.1. Касается нас напрямую

| Тема | Где у нас | Что безопасник должен уметь проверить | Как |
|---|---|---|---|
| Права доступа и IDOR | панель с ролями, API, вебхуки, чаты клиентов | у каждой функции есть проверка роли; у каждого запроса с id есть проверка владельца; нет доступа к чужому клиенту подменой id; поля, не положенные роли, не отдаются | код: найти каждую точку входа и проверить, что проверка есть и стоит до действия; стенд: две учётки с разными ролями, подмена id и метода. Нормы: [ASVS V8](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x17-V8-Authorization.md), [API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization) |
| Аутентификация и сессии панели | вход в панель, токены | пароль хранится хешем Argon2id или аналогом; новый токен после входа; завершение сессии при отключении учётки; защита от перебора | код + стенд: перебор, повторное использование старого токена. Нормы: [ASVS V6](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x15-V6-Authentication.md), [V7](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x16-V7-Session-Management.md), [Password Storage CS](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) |
| SQL-инъекция | SQLite и PostgreSQL | нет SQL, собранного из строк; имена колонок и порядок сортировки идут из белого списка | код: поиск сборки запросов f-строкой и конкатенацией; стенд: кавычка и логические выражения в каждом параметре. Нормы: [SQL Injection Prevention CS](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), [ASVS 1.2.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x10-V1-Encoding-and-Sanitization.md) |
| XSS | виджет на сайте, панель | данные вставляются как текст, не как HTML; безопасные приёмы DOM; санитайзер там, где HTML нужен | код: поиск `innerHTML` и аналогов; стенд: вставка тестовой строки в каждое поле, что потом отображается. Нормы: [XSS Prevention CS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) |
| Команды ОС и выполнение кода | возможные вызовы утилит, обработка файлов | нет `eval`, `exec`, запуска команд из строки пользователя | код: поиск таких вызовов. Нормы: [ASVS 1.2.5, 1.3.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x10-V1-Encoding-and-Sanitization.md), [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html) (78, 94, 77) |
| SSRF | вызовы Bitrix24, вебхуки, ссылки в чатах, вызовы ИИ | адреса наружу собираются кодом из фиксированных частей, а не берутся целиком у пользователя; внутренние адреса недоступны | код: все места с HTTP-клиентом; стенд: подсунуть адрес внутреннего порта. Нормы: [SSRF CS](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [API7](https://api-security.owasp.org/editions/2023/en/0x11-t10) |
| Вебхуки и входящие запросы ботов | Telegram, MAX, Bitrix24 | проверка подписи по сырому телу, метка времени, повтор события не повторяет действие, лимит размера | код + стенд: подделанный запрос, повтор старого запроса. Норма: [Webhook Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html) |
| LLM и база знаний | ответы ИИ, поиск по базе | текст из базы, чата и ответов ИИ считается недоверенным; права проверяет код, не модель; у инструментов минимум прав; поиск по базе учитывает права | код: путь от запроса к вызову ИИ и от ответа ИИ к действию; стенд: подсунуть в документ базы команду-ловушку. Нормы: [LLM10](https://genai.owasp.org/llm-top-10/), [LLM Prompt Injection CS](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html), [AI Agent CS](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html), [RAG CS](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html); у PortSwigger это раздел «Web LLM attacks» ([темы](https://portswigger.net/web-security/all-topics)) |
| Бизнес-логика и гонки | очередь юристов, лимиты, распределение лидов | шаги нельзя пропустить; операции в транзакции; ограниченный ресурс нельзя взять дважды | код: места «прочитал — проверил — записал»; стенд: два одновременных запроса. Нормы: [ASVS 2.3.1, 2.3.3, 2.3.4, 15.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x11-V2-Validation-and-Business-Logic.md) |
| Загрузка и пути файлов | вложения в чатах, документы базы знаний | тип, размер, имя файла задаёт сервер; файл не исполняется | код + стенд: файл с двойным расширением, с `../` в имени. Нормы: [File Upload CS](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html), [ASVS V5](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x14-V5-File-Handling.md) |
| Секреты | токены ботов, ключи Bitrix24 и ИИ | нет секретов в коде, образах и журналах; ротация возможна | код: поиск секретов в репозитории и истории; Docker: переменные окружения. Нормы: [Secrets Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [ASVS 13.3.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md) |
| Docker и настройки | один сервер, Docker | не от root, без сокета Docker в контейнере, порты привязаны к 127.0.0.1, режим отладки выключен, документация API закрыта | код: Dockerfile, compose; стенд: сканирование портов стенда. Нормы: [Docker Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html), [ASVS V13](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md) |
| Зависимости | Python и JS | см. раздел 4 | — |
| Журналы и ошибки | все сервисы | клиенту — общий ответ; в журнале есть входы, отказы в правах; в журнале нет паролей и токенов | код + стенд: вызвать ошибку и прочитать ответ и журнал. Нормы: [Logging CS](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html), [Error Handling CS](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html), [ASVS V16](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md) |
| Ограничение частоты | вход, вызовы ИИ, вебхуки | есть лимиты на запросы, на размер, на число вызовов ИИ | стенд: серия запросов. Нормы: [ASVS 2.4.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x11-V2-Validation-and-Business-Logic.md), [API4](https://api-security.owasp.org/editions/2023/en/0x11-t10) |
| CSRF, CORS, куки | панель на сайте | куки с Secure/HttpOnly/SameSite; CORS по списку источников | стенд: запрос с чужого источника. Нормы: [ASVS V3](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x12-V3-Web-Frontend-Security.md), [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html) |

В списке CS есть листы, прямо про наш стек: [FastAPI Security](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html), Django Security, Django REST Framework, Webhook Security, Docker Security, Secrets Management, LLM Prompt Injection Prevention, AI Agent Security, RAG Security, MCP Security, Secure Coding with AI, Mass Assignment, Multi Tenant Security, REST Security, NoSQL Security, JavaScript and TypeScript Security, Software Supply Chain Security ([общий указатель](https://cheatsheetseries.owasp.org/Glossary.html)). Листы про aiohttp нет.

### 2.2. Касается слабо или частично

- Тестирование API и GraphQL. У нас REST и вебхуки; GraphQL нет (по описанию стека). Берём только REST-часть: [ASVS V4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x13-V4-API-and-Web-Service.md), [API10](https://api-security.owasp.org/editions/2023/en/0x11-t10).
- Криптография — только не писать своё и верно хранить пароли и ключи: [ASVS V11](https://github.com/OWASP/ASVS/tree/master/5.0/en), [Password Storage CS](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- WebSocket: нужно, если виджет работает через WebSocket ([ASVS 4.4.x](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x13-V4-API-and-Web-Service.md)).
- Сбор сведений о цели — только в смысле «что видно снаружи нашего стенда»: [WSTG 4.1](https://wstg.owasp.org/v4.2/).
- Десериализация: в Python опасны `pickle` и небезопасная загрузка YAML (вывод из [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html), пункт 502); проверять поиском по коду.

### 2.3. Нас не касается

- Бинарная эксплуатация и ошибки памяти (CWE 787, 416, 125, 120, 121, 122, 476 в [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)): Python и JS управляют памятью сами.
- Повышение прав в ОС, Active Directory, боковое перемещение, обход антивирусов, облачные атаки (области [PEN-200](https://www.offsec.com/courses/pen-200/)).
- Разработка эксплойтов, .NET-десериализация (темы [WEB-300](https://www.offsec.com/courses/web-300/)).
- Смешивание HTTP-запросов, отравление кэша: актуально только если перед нашим сервисом стоит кэширующий прокси ([PS](https://portswigger.net/web-security/all-topics); [ASVS 4.2.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x13-V4-API-and-Web-Service.md)).
- WebRTC ([ASVS V17](https://github.com/OWASP/ASVS/tree/master/5.0/en)) и мобильное: у нас нет.

---

## 3. Правила безопасного кода для исполнителя (в двух и более нормативах)

Критерий отбора: правило названо не меньше чем в двух разных документах из просмотренных. Порядок — по важности для нашего стека. В колонке «Закрывает» — класс слабости; номера CWE взяты из [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html), где они есть в списке.

1. **Запросы к базе — только с параметрами; имена таблиц и порядок сортировки — из белого списка.** Где: [ASVS 1.2.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x10-V1-Encoding-and-Sanitization.md); [SQL Injection Prevention CS](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html); [Google, гл. 12](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html). Закрывает: SQL-инъекция (CWE-89).
2. **Права проверять на сервере, на каждом запросе, по умолчанию отказ.** Где: [ASVS 8.2.1, 8.3.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x17-V8-Authorization.md); [Authorization CS](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html); [T10 A01](https://top10.owasp.org/2025/0x00_2025-Introduction). Закрывает: нет проверки прав (CWE-862, CWE-863, CWE-306).
3. **Проверять право на конкретный объект, а не только на тип действия; случайный id — не защита.** Где: [ASVS 8.2.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x17-V8-Authorization.md); [Authorization CS](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html); [API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization). Закрывает: доступ к чужому объекту, подмена ключа (CWE-639).
4. **Принимать от клиента только разрешённые поля: отдельная схема ввода, лишние поля — отказ, ответ отдавать по схеме.** Где: [Mass Assignment CS](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html); [ASVS 15.3](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md); [API10 (API3)](https://api-security.owasp.org/editions/2023/en/0x11-t10). Закрывает: массовое присвоение, лишние данные в ответе.
5. **Любой ввод проверять на сервере по белому списку (тип, формат, смысл); неверное отвергать, а не «чинить»; размер ограничивать до разбора.** Где: [ASVS 2.2.1, 2.2.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x11-V2-Validation-and-Business-Logic.md); [Input Validation CS](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html). Закрывает: неверная проверка ввода (CWE-20). Заметка: проверка ввода не заменяет параметры запроса и кодирование вывода (оба листа это говорят).
6. **Вывод кодировать под место вставки; в DOM писать `textContent`, не `innerHTML`; HTML очищать проверенным санитайзером.** Где: [ASVS 1.2.1, 1.3.1, 3.2.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x10-V1-Encoding-and-Sanitization.md); [XSS Prevention CS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html); [Google, гл. 12](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html). Закрывает: XSS (CWE-79).
7. **Не запускать команды ОС строкой с данными пользователя и не вызывать `eval`/`exec` на чужом тексте.** Где: [ASVS 1.2.5, 1.3.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x10-V1-Encoding-and-Sanitization.md); [OS Command Injection Defense CS](https://cheatsheetseries.owasp.org/IndexTopTen.html) (лист числится в карте A03, текст не открывал); [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html). Закрывает: CWE-78, CWE-77, CWE-94.
8. **Запросы наружу по адресу от пользователя: белый список хостов, свои схема и порт, редиректы выключены, IP проверять при соединении.** Где: [SSRF Prevention CS](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html); [ASVS 13.2.4, 13.2.5](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md); [API7](https://api-security.owasp.org/editions/2023/en/0x11-t10); [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html). Закрывает: SSRF (CWE-918).
9. **Секреты — не в коде, не в образах Docker, не в журналах; хранить в хранилище секретов, выдавать по минимуму прав, при утечке отзывать.** Где: [Secrets Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html); [ASVS 13.3.1, 13.3.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md); [Docker Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html); [CI/CD Security CS](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html). Закрывает: утечка секретов (CWE-200).
10. **Пароли хранить хешем Argon2id (или scrypt/PBKDF2/bcrypt по списку); длина не меньше 8, лучше 15; сверять с частыми паролями; без правил состава.** Где: [Password Storage CS](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html); [ASVS 6.2.1, 6.2.4, 6.2.5](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x15-V6-Authentication.md). Закрывает: слабое хранение учётных данных.
11. **Сессии: новый токен после входа, случайный, не короче 128 бит; сессия кончается при отключении учётки; JWT — проверять подпись, срок, издателя, алгоритм задавать самим.** Где: [ASVS 7.2.3, 7.2.4, 7.4.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x16-V7-Session-Management.md); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html); [T10 A07](https://top10.owasp.org/2025/0x00_2025-Introduction). Закрывает: угон и подделка сессий.
12. **Куки с Secure, HttpOnly, SameSite; изменяющие запросы защищены от CSRF; CORS — по фиксированному списку, без `*` вместе с куками.** Где: [ASVS 3.3.1, 3.4.2, 3.5.x](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x12-V3-Web-Frontend-Security.md); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html); [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html). Закрывает: CSRF (CWE-352).
13. **Загрузка файлов: белый список типов, имя задаёт сервер, проверка содержимого, лимит размера до разбора, хранить вне исполняемой папки.** Где: [File Upload CS](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html); [ASVS 5.2.1, 5.2.2, 5.3.1, 5.3.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x14-V5-File-Handling.md); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html). Закрывает: опасные файлы (CWE-434).
14. **Пути к файлам строить из доверенных данных; имя от пользователя проверять жёстко.** Где: [ASVS 5.3.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x14-V5-File-Handling.md); [File Upload CS](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html); [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html); [PS: path traversal](https://portswigger.net/web-security/learning-paths/server-side-vulnerabilities-apprentice). Закрывает: обход пути (CWE-22).
15. **Недоверенные данные не десериализовать (`pickle`, небезопасный YAML); использовать форматы без исполнения кода.** Где: [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html) (CWE-502); [T10 A08 и карта листов CS](https://cheatsheetseries.owasp.org/IndexTopTen.html) (лист Deserialization, текст не открывал); [Google, гл. 12](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html) (безопасная десериализация, например Protocol Buffers). Закрывает: CWE-502.
16. **Ошибки: клиенту — общий ответ, подробности в журнал; при сбое проверки не «пропускать дальше».** Где: [ASVS 16.5.1, 16.5.3](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md); [Error Handling CS](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html); [T10 A10](https://top10.owasp.org/2025/0x00_2025-Introduction); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html). Закрывает: утечка сведений (CWE-200), «открыто при сбое».
17. **Журнал: писать входы, отказы в правах, сбои проверок; не писать пароли, токены, ПДн; данные кодировать от подделки записей.** Где: [Logging CS](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html); [ASVS 16.2.5, 16.3.x, 16.4.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md); [T10 A09](https://top10.owasp.org/2025/0x00_2025-Introduction); [Webhook CS](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html) (секрет вебхука убирать из журналов). Закрывает: невидимые атаки, утечки через журнал.
18. **Лимиты: на частоту входа и запросов, размер тела, число и стоимость вызовов ИИ, рекурсию агентов.** Где: [ASVS 2.4.1, 6.3.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x11-V2-Validation-and-Business-Logic.md); [API4](https://api-security.owasp.org/editions/2023/en/0x11-t10); [AI Agent CS](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html); [LLM10 (LLM10)](https://genai.owasp.org/llm-top-10/); [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html). Закрывает: исчерпание ресурсов (CWE-770), расход денег на ИИ.
19. **Многошаговые действия — по порядку и в транзакции; ограниченный ресурс блокировать от двойного взятия; гонки учитывать.** Где: [ASVS 2.3.1, 2.3.3, 2.3.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x11-V2-Validation-and-Business-Logic.md) и [15.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md); [API6](https://api-security.owasp.org/editions/2023/en/0x11-t10); [PS: гонки и бизнес-логика](https://portswigger.net/web-security/all-topics); [Secure Code Review CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html). Закрывает: пропуск шагов, двойное взятие, TOCTOU.
20. **Зависимости: проверенный источник, закреплённые версии, срок исправления известных дыр, перечень (SBOM).** Где: [ASVS 15.1.1, 15.1.2, 15.2.1, 15.2.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md); [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures); [Software Supply Chain Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html); [CI/CD Security CS](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html); [SSDF PW.4](https://pages.nist.gov/nccoe-devsecops/mapping-ssdf.html). Закрывает: подмена и дыры в чужих пакетах. Подробности — раздел 4.
21. **Пакет, который предложил ИИ, сначала проверить в реестре (существует ли, возраст, скачивания, автор).** Где: [Secure Coding with AI CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html); [MCP Security CS](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html) (проверка опечаточных имён); [Software Supply Chain Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html) (проверка проекта перед использованием). Закрывает: поддельные пакеты по галлюцинации модели.
22. **Текст из ответов ИИ, базы знаний, чатов и страниц — недоверенные данные; права проверяет код вне модели; инструменту модели — минимум прав; опасное — с подтверждением человека, привязанным к точному действию.** Где: [LLM Prompt Injection CS](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html); [AI Agent CS](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html); [MCP Security CS](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html); [LLM10: LLM01, LLM05, LLM06](https://genai.owasp.org/llm-top-10/). Закрывает: внедрение подсказок, лишние полномочия агента, небезопасный вывод.
23. **База знаний для ИИ: права проверять при выборке, до попадания текста в модель; клиентов разделять; при отказе в праве отдавать пусто.** Где: [RAG Security CS](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html); [AI Agent CS](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) (память изолировать по пользователю); [ASVS 8.2.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x17-V8-Authorization.md). Закрывает: утечка чужих данных через поиск, отравление документов.
24. **Контейнер: не от root, без сокета Docker, лишние возможности убрать, порты — на 127.0.0.1, образы закреплены и просканированы.** Где: [Docker Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html); [CI/CD Security CS](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html) (без привилегированных контейнеров, без root); [ASVS 13.2.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md) (минимум прав у серверных учёток), [15.2.5](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md). Закрывает: выход из контейнера, лишние права (T10 A02).
25. **Боевой режим: отладка выключена, нет тестового кода и примеров, нет учёток по умолчанию, служебные страницы и документация API закрыты.** Где: [ASVS 13.4.2, 13.4.5, 13.2.3, 6.3.2, 15.2.3](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md); [FastAPI Security CS](https://cheatsheetseries.owasp.org/cheatsheets/FastAPI_Security_Cheat_Sheet.html); [CISA Secure by Design](https://www.cisa.gov/securebydesign/pledge) (цель: меньше общих паролей по умолчанию); [T10 A02](https://top10.owasp.org/2025/0x00_2025-Introduction). Закрывает: неверные настройки.

### Правила из одного источника, но важные нам (в список из 25 не вошли)

- Вебхук: подпись HMAC по сырому телу, сравнение за постоянное время, окно по метке времени, дедупликация по id события, ответ 200 только после надёжной постановки в очередь. Источник один: [Webhook Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html). Схожая мысль в API10 («небезопасное использование API») — текст пункта не открывал.
- Криптографию не писать самим: [Google, гл. 12](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html); практика SDL «определять и применять стандарты криптографии» ([SDL](https://www.microsoft.com/en-us/securityengineering/sdl/practices)) — по заголовку, текст не открывал.
- Правило для самого безопасника: сгенерированные ИИ тесты безопасности не считать доказательством, критичные тесты писать вручную: [Secure Coding with AI CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html).

---

## 4. Как проверяют чужой код и зависимости по нормативам

### 4.1. Выбор библиотеки

- Смотреть: ведётся ли проект, популярность, стабильный релиз, история дыр и как мейнтейнеры их закрывали, число мейнтейнеров, наличие тестов безопасности, лицензия. Сертификаты — подсказка, не доказательство. Источник: [Software Supply Chain Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html).
- Брать популярные, поддерживаемые библиотеки с хорошей историей; постоянно обновлять; не писать свою криптографию. Источник: [Google, гл. 12](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html).
- Перед выбором оценить по руководству OpenSSF (лист CS на него ссылается, само руководство не открывал). Источник: [Vulnerable Dependency Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).
- Брать только из доверенных репозиториев и по защищённым каналам; предпочитать подписанные пакеты. Источники: [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures); [ASVS 15.1.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md).
- Для практик NIST: повторно использовать уже проверенное ПО, а не дублировать (PW.4), проверять сторонние компоненты на всём жизненном цикле (PW.4.4). Источники: [NCCoE: карта SSDF](https://pages.nist.gov/nccoe-devsecops/mapping-ssdf.html), [расшифровка PW.4 в поиске](https://myctrl.tools/frameworks/nist-800-218/pw-4) (сайт не первоисточник — только для сверки).
- Убирать неиспользуемые зависимости и функции. Источник: [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures).

### 4.2. Закрепление версий

- Закреплять проверенные версии и фиксировать их файлом блокировки; хеши проверять; приватный реестр с входной проверкой пакетов; сужать область имён против подмены зависимостей. Источники: [CI/CD Security CS](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html), [Software Supply Chain Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html), [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures) («закреплять сознательно выбранные версии»).
- Сторонние GitHub Actions закреплять по хешу коммита, а не по метке. Источник: [Secure Coding with AI CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html).
- Образы Docker и пакеты ОС в образе закреплять. Источник: [Docker Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html).
- Проверять, что компоненты и их транзитивные зависимости идут из ожидаемого репозитория (защита от подмены зависимостей). Источник: [ASVS 15.2.4](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md) (уровень 3).

### 4.3. Проверка известных уязвимостей

- Начинать автоматический анализ зависимостей с первого дня: позже накапливается завал. Источник: [Vulnerable Dependency Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).
- Брать инструмент с несколькими источниками данных (одной базы CVE мало), с возможностью отмечать ложные срабатывания. Бесплатные, названные в листе: OWASP Dependency-Check, npm Audit, OWASP Dependency-Track, Trivy, Grype. Платные (Snyk, JFrog Xray) нам не подходят по правилу D-006. Источник: [Vulnerable Dependency Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).
- Следить за NVD, OSV и каталогом известных эксплуатируемых уязвимостей CISA. Источники: [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures), [Software Supply Chain Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html).
- Задать срок исправления по риску и не иметь в продакшене компонентов с истёкшим сроком. Источники: [ASVS 15.1.1, 15.2.1](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md) (уровень 1).
- Разбор находки: чинить прямые зависимости (транзитивные трогать осторожно); если исправления нет — обход, проверка, достижим ли уязвимый вызов, тест на регрессию; без вариантов — искать замену; подавлять находку только по конкретной CVE и после проверки патча. Источник: [Vulnerable Dependency Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).
- Вести перечень компонентов (SBOM) и держать его в CI. Источники: [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures), [ASVS 15.1.2](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md) (уровень 2), [практика SDL 5 «безопасность цепочки поставок»](https://www.microsoft.com/en-us/securityengineering/sdl/practices/sscs) (пересказ через поиск).
- Обновления раскатывать поэтапно, не всем сразу. Источник: [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures).

### 4.4. Проверка готового решения или шаблона

- Выбрать вид ревью: полный (новое приложение, большой релиз) или по изменениям (запрос на слияние). Идти от точек входа, прослеживать путь данных от источника (ввод, загрузки, API, переменные окружения) до приёмников (запросы, запись файлов, вывод, журнал, внешние вызовы); использовать анализаторы для приоритета, решение — за человеком. Источник: [Secure Code Review CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html).
- Проверять в первую очередь: клиентская проверка вместо серверной, собранный строкой SQL и команды, слабая аутентификация и сессии, недостающие проверки прав, жёстко зашитые секреты, подробные ошибки, чувствительное в журналах. Источник: [Secure Code Review CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html).
- Разбирать весь diff, а не описание: смотреть правки вне задачи — файлы блокировки, CI, тесты; сборочные файлы (скрипты package.json, CI, Dockerfile, Makefile) считать критичными; искать невидимые символы (bidi, нулевой ширины). Источник: [Secure Coding with AI CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html).
- В шаблоне не должно быть тестового кода, примеров и функций разработчика на боевом сервере. Источник: [ASVS 15.2.3](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md).
- Рискованные компоненты и места с «опасной функциональностью» записать; на третьем уровне — изолировать (песочница, контейнер, сеть). Источники: [ASVS 15.1.4, 15.1.5, 15.2.5](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md).
- Анализ чужого открытого кода тем же статическим анализом, что и своего, с ручной проверкой находок. Источник: [Software Supply Chain Security CS](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html). Практика SDL «проверка безопасности»: статический анализ в рабочем процессе разработчика, динамический на собранном приложении, ручной тест на проникновение. Источник: [SDL: security testing](https://www.microsoft.com/en-us/securityengineering/sdl/practices/security-testing).
- NIST SSDF: PW.7 — проверка человекочитаемого кода, PW.8 — тест исполняемого кода, RV.1–RV.3 — найти, оценить, найти корневую причину. Источник: [NCCoE: карта SSDF](https://pages.nist.gov/nccoe-devsecops/mapping-ssdf.html).
- Тесты для проверки безопасности: Google советует проверять тесты ревью-ем (сломается ли тест, если сломать логику) и запускать статические проверки в CI. Источник: [Google, гл. 13](https://google.github.io/building-secure-and-reliable-systems/raw/ch13.html).

---

## 5. Где источники расходятся

1. **«Закреплять» против «обновлять».** T10 A03 советует закреплять выбранные версии и обновлять «только когда нужно» ([A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures)); ASVS 15.2.1 требует, чтобы в продакшене не было компонентов за сроком исправления ([ASVS V15](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md)); Vulnerable Dependency Management CS про закрепление молчит ([лист](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)). Как сводить: закрепить и иметь срок обновления по риску.
2. **Транзитивные зависимости.** Лист CS советует работать только с прямыми, считая смену транзитивных рискованной ([лист](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)); T10 и ASVS 15.2.4 просят учитывать и источник транзитивных ([A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures), [ASVS V15](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md)). Как сводить: считать и учитывать все, чинить через прямые.
3. **Журналы.** В ASVS 5.0 в главе про журналы нет ни одного требования первого уровня ([V16](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md)), а в Top 10 это отдельный пункт A09, в SDL — отдельная практика ([T10](https://top10.owasp.org/2025/0x00_2025-Introduction), [SDL](https://www.microsoft.com/en-us/securityengineering/sdl/practices)). Как сводить: начальный минимум брать из листа Logging CS.
4. **SSRF.** Top 10:2025 влил SSRF в A01 ([T10](https://top10.owasp.org/2025/0x00_2025-Introduction)), а API Top 10 и CWE Top 25 держат его отдельным пунктом ([API10](https://api-security.owasp.org/editions/2023/en/0x11-t10), [CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)). В листе CS указатель к Top 10 всё ещё по версии 2021 ([указатель](https://cheatsheetseries.owasp.org/IndexTopTen.html)) — сверяться с ним по именам листов, не по номерам пунктов.
5. **Список опасностей.** CWE Top 25 забит ошибками памяти (787, 416, 125, 120, 121, 122, 476), OWASP-списки веба — нет ([CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)). Для Python и JS эти пункты брать не нужно.
6. **Код-ревью.** Google пишет, что одним ревью обойтись нельзя, нужна автоматика и безопасные по типам библиотеки ([гл. 12](https://google.github.io/building-secure-and-reliable-systems/raw/ch12.html)); Secure Code Review CS и SSDF PW.7 делают ревью центральным шагом ([CS](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html), [SSDF](https://pages.nist.gov/nccoe-devsecops/mapping-ssdf.html)). Как сводить: и то, и то.
7. **Проверка ввода.** Input Validation CS: белый список, неверное отвергать, но это не защита от инъекций ([лист](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)); SQL Injection Prevention CS не советует экранирование как основной приём ([лист](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)). Старые материалы учат «чистить вход» — это устаревший подход.
8. **Версии документов не совпадают по времени.** ASVS 5.0 вышел в мае 2025, WSTG на 4.2 (5.0 в разработке), SSDF 1.1 утверждён, а 1.2 — черновик ([ASVS](https://github.com/OWASP/ASVS), [WSTG](https://owasp.org/www-project-web-security-testing-guide/), [SSDF Rev.1](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd)). Номера тестов WSTG и номера требований ASVS поэтому не ссылаются друг на друга.
9. **Учёба и нормативы.** Курсы (PEN-200: повышение прав, Active Directory) и учебник PortSwigger почти не касаются цепочки поставок, журналов и настроек, а нормативы ставят их в верхние строки ([PEN-200](https://www.offsec.com/courses/pen-200/), [PS](https://portswigger.net/web-security/all-topics), [T10](https://top10.owasp.org/2025/0x00_2025-Introduction)).
10. **Параметры паролей.** ASVS требует минимум 8 и рекомендует 15, без правил состава ([ASVS 6.2.1, 6.2.5](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x15-V6-Authentication.md)); для хеша Password Storage CS даёт точные параметры Argon2id (m=19456, t=2, p=1) ([лист](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)). Противоречия нет, но числа живут в разных документах.
11. **Случайные id.** API1 советует среди мер использовать случайные значения (GUID) для id записей ([API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization)); Authorization CS прямо говорит не полагаться на трудно угадываемые id и проверять доступ к объекту ([лист](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)). Как сводить: случайные id — слой сверху, проверка права на объект обязательна.
12. **Окно подписи вебхука.** Пять минут названо как значение по умолчанию у Stripe ([Webhook CS](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html)); у Telegram, MAX и Bitrix24 свои схемы, которых листы не описывают.

---

## 6. Чего не брать (тяжело для одного человека и агентов)

- **SAMM целиком** (15 практик, оценка зрелости организации): не про наш размер. Брать разве что идею «оценить и улучшать» ([SAMM](https://owaspsamm.org/model/)).
- **ASVS уровень 3** и все требования уровня 2 подряд. Сам ASVS говорит, что уровни выбирают по риску, а стартапу с малым объёмом чувствительных данных хватает первого ([ASVS, что это](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x03-What-is-the-ASVS.md)). Для нас разумно: весь уровень 1 + выбранные требования уровня 2 из глав V2, V8, V13, V15, V16 (мой выбор по нашему стеку).
- **Полный WSTG** вручную: двенадцать групп и сотни тестов; брать группы 4.4–4.7, 4.10–4.12 как карту, а запуск оформлять скриптами ([WSTG](https://wstg.owasp.org/v4.2/)).
- **Курсы OSCP и OSWE** целиком: платные, тратят время на Active Directory, повышение прав, обход антивирусов, .NET-эксплойты ([PEN-200](https://www.offsec.com/courses/pen-200/), [WEB-300](https://www.offsec.com/courses/web-300/)). Берём только веб-часть через бесплатный PortSwigger, который называет себя бесплатным ([страница](https://portswigger.net/web-security)).
- **Ошибки памяти из CWE Top 25** ([CWE25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)).
- **Подписание артефактов и цепочки доказательств (Sigstore, in-toto), независимая сборка, раздельные обязанности в CI** ([CI/CD Security CS](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html), [T10 A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures)): для одного сервера избыточно; на первом шаге — SBOM и закрепление.
- **Централизованный SIEM, круглосуточный разбор тревог** ([CI/CD Security CS](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)): хватит файловых журналов с нужными событиями.
- **Платные сканеры** (Snyk, JFrog Xray; список в [Vulnerable Dependency Management CS](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)): нарушают правило D-006; есть бесплатные Dependency-Check, Trivy, Grype, npm audit.
- **Непрерывный фаззинг и санитайзеры** ([Google, гл. 13](https://google.github.io/building-secure-and-reliable-systems/raw/ch13.html)): нужен прежде всего для кода на C/C++; для Python — только на разборе файлов и чужих форматов.
- **Планы аварий, кризисное управление, «культура безопасности»** — главы IV–V книги Google ([оглавление](https://google.github.io/building-secure-and-reliable-systems/raw/toc.html)).
- **Сертификация процессов по ГОСТ Р 56939-2024 и приказам ФСТЭК**: это для разработчиков средств защиты информации (приказ ФСТЭК № 240 от 01.12.2023, по вторичному пересказу [Контур.Норматив](https://normativ.kontur.ru/document/1/502199-prikaz-fstek-rf-ot-01-12-2023-n-240)). В ГОСТе 25 процессов, среди них моделирование угроз, анализ сторонних компонентов, управление секретами ([anti-malware.ru](https://www.anti-malware.ru/analytics/Technology_Analysis/GOST-R-56939-2024-Secure-Development-Audit), вторичный). Использовать как справку: полезные идеи совпадают с SSDF и ASVS. Решение о ГОСТ — за пользователем и заказчиком.
- **Любые проверки боевого сервера** — запрещены по роли.

---

## 7. Что не проверено

Общее: страницы пересказывала быстрая модель; номера требований и перечни сверены по её выдаче. Для критичных мест (например, список требований ASVS в скриптах) нужно открыть исходный файл руками.

- **OWASP Top 10:2025.** Открыты введение (список из 10 пунктов) и страница A03. Остальные девять страниц не читал. Лицензия по странице A03 — CC BY 3.0.
- **ASVS 5.0.** Прочитаны главы V1, V2, V3, V4, V5, V6, V7, V8, V13, V15, V16. Не открыты V9–V12, V14, V17, приложения; общее число требований и деление по уровням в точных числах не найдено (в файле «что такое ASVS» сказано: уровень 1 — около 20 % требований, уровни 1+2 — около 70 %, уровень 3 — остальное). По спискам видно, что у ASVS 5.0 нет требований первого уровня в V16.
- **WSTG.** Известны только 12 названий групп (v4.2); подтем и конкретных тестов не открывал. Список групп с [wstg.owasp.org/v4.2](https://wstg.owasp.org/v4.2/).
- **OWASP Top 10 for LLM.** Только названия 10 пунктов; тексты пунктов не открывал.
- **API Security Top 10.** Список из 10 и страница API1; остальные пункты не читал. Лицензия на страницах не указана (только © проекта), в репозитории не проверял.
- **SAMM.** Только перечень функций и практик; уровни зрелости не открывал.
- **Cheat Sheet Series.** Прочитаны ~25 листов (Vulnerable Dependency Management, Software Supply Chain Security, LLM Prompt Injection, Webhook, Secrets Management, SQL Injection, XSS, SSRF, Authorization, Docker, Secure Coding with AI, Secure Code Review, FastAPI, Mass Assignment, AI Agent, RAG, Error Handling, Logging, File Upload, Password Storage, Input Validation, CI/CD, MCP). Только по названию в указателе: Deserialization, OS Command Injection Defense, JWT, Session Management, Multi Tenant Security, REST Security, GitHub Actions Security, Authorization Testing Automation, Django Security, Nodejs Security.
- **CWE Top 25.** Список прочитан; страницы отдельных слабостей не открывал. Список за 2026 год ещё не вышел (на странице новее 2025 нет; обычно выходит к концу года — это моё предположение).
- **NIST SSDF.** PDF-файлы SP 800-218 и черновика Rev.1 открылись как бинарные, текст не прочитан. Названия практик взяты со страницы NIST NCCoE ([карта SSDF](https://pages.nist.gov/nccoe-devsecops/mapping-ssdf.html)), это первоисточник NIST, но не сам документ. Что изменилось в Rev.1 — только из пересказа поиска (добавлены PO.6 и PW.10; сказано в презентации NIST от мая 2026, саму презентацию не открывал). Подзадачи (например PW.4.1, PW.4.4) известны из результатов поиска.
- **Microsoft SDL.** Прочитаны перечень десяти практик и страница «security testing». Остальные страницы практик вернули ошибку 404 по прямым адресам; про цепочку поставок (практика 5) — только пересказ в результатах поиска, страницу `.../practices/sscs` напрямую не читал.
- **Google, «Building Secure and Reliable Systems».** Прочитаны оглавление, главы 12 и 13. Страница sre.google показывает книгу с кнопкой «читать онлайн»; лицензия на странице не указана — брать только пересказ. Главы про минимальные привилегии (5) и атакующих (2) не читал.
- **CISA Secure by Design.** Три принципа и семь целей обязательства прочитаны. Основной документ («Secure by Design», PDF) не открывал.
- **PortSwigger.** Прочитаны список тем и путь «серверные уязвимости (новичок)». Остальные пути обучения не открылись (страница «Learning paths» вернула только заголовок), общего числа лабораторных нет. На странице сказано, что Academy бесплатна.
- **OSCP/OSWE.** Прочитаны области тем на страницах курса, а не сам план (PDF с планом не открывал). Оба курса платные.
- **Российское.** Страницы программ Яндекс Практикума («Кибербезопасность: веб-пентест») и Skillbox не дали состава программы: у Практикума текст обрезан, у Skillbox адрес вернул 404. Состав взят из вторичных обзоров (Хабр Карьера, Хабр). HackerU не проверял. Текст ГОСТ Р 56939-2024 не открывал (платный/через Росстандарт); состав из двух вторичных статей: 25 процессов, из них новые относительно 2016 года — моделирование угроз, композиционный анализ, управление секретами ([anti-malware.ru](https://www.anti-malware.ru/analytics/Technology_Analysis/GOST-R-56939-2024-Secure-Development-Audit)). Список всех 25 процессов по пунктам 5.1–5.25 не нашёл. Сайт fstec.ru с этой машины не открылся (отказ соединения). Приказы ФСТЭК № 240 и № 230 — только по вторичным ссылкам, номера и даты нужно сверить в первоисточнике.
- **Что ещё нужно будет сделать.** Список проверочных скриптов и готовых автотестеров в эту часть не входит (задача соседних частей подборки). Каждый тест из WSTG стоит смотреть при сборке конкретных скриптов.

---

## Лицензии: что можно брать целиком

| Документ | Лицензия | Что это значит для нас | Откуда |
|---|---|---|---|
| OWASP ASVS | CC BY-SA 4.0 | можно брать и переделывать с указанием автора; результат — под той же лицензией | [репозиторий](https://github.com/OWASP/ASVS), [файл о ASVS](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x01-Frontispiece.md) |
| OWASP WSTG | CC BY-SA 4.0 | то же | [проект](https://owasp.org/www-project-web-security-testing-guide/) |
| OWASP SAMM | CC BY-SA 4.0 | то же | [проект](https://owasp.org/www-project-samm/) |
| OWASP Cheat Sheet Series | CC BY-SA 4.0 (по подписи страницы) | то же | [указатель](https://cheatsheetseries.owasp.org/IndexTopTen.html) |
| OWASP Developer Guide | CC BY-SA 4.0 | то же | [проект](https://owasp.org/www-project-developer-guide/) |
| OWASP Top 10 for LLM (genai.owasp.org) | CC BY-SA 4.0, «если не указано иное» | то же, с оговоркой | [страница](https://genai.owasp.org/llm-top-10/) |
| OWASP Top 10:2025 | CC BY 3.0 | можно брать и переделывать, достаточно указать автора | [A03](https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures) |
| OWASP API Security Top 10 | на странице не указана (стоит © проекта) | пока только пересказ, ссылка | [API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization) |
| MITRE CWE и Top 25 | бесплатно для любых целей; в копии нужно сохранить авторскую пометку MITRE и текст лицензии | можно использовать, пометку не терять | [условия CWE](https://cwe.mitre.org/about/termsofuse.html) |
| NIST SSDF, CISA, Microsoft SDL, Google, PortSwigger, OffSec, курсы | не проверялись | считать, что целиком брать нельзя; только пересказ и ссылка | — |

Для набора скилов: если переносить в скил куски ASVS или Cheat Sheet (а не пересказ), файл-копия получается под CC BY-SA 4.0 и обязана нести указание автора и ссылку. Безопаснее в скиле держать свои короткие правила и ссылки на номера требований.

---

## Итог для набора скилов (кратко)

- Основа правил для исполнителей: ASVS 5.0 (уровень 1 + выбранный уровень 2) и профильные листы Cheat Sheet Series.
- Основа «чему учить безопасника проверять»: PortSwigger (бесплатно, 31 тема) плюс 12 групп WSTG как карта.
- Свести вместе три пласта: учебные темы (раздел 1), правила кода (раздел 3), проверка чужого кода и зависимостей (раздел 4).
- Для нас особенно важны: права и IDOR, инъекции, SSRF, вебхуки, секреты, LLM/RAG, гонки в очередях, Docker, зависимости.
