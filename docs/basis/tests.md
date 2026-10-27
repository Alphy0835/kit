# Основание справок о тестах

Источники и таблицы «основание правил» справок `references/tests/`. Из самих справок убраны 16.10.2026 по слову
Владельца: справку читает агент в работе, источники ему не нужны. Здесь — для того, кто правит набор.

## `what-to-test.md`

Указатели из шапки: Испытан на учебном проекте — `docs/probes/tests-reference/README.md`. Откуда взято каждое правило — `docs/tests-synthesis.md`.

- Google, «Software Engineering at Google», гл. 11–13: поведение через открытый вход, тесты вызовов хрупкие,
  покрытие не равно проверке. https://abseil.io/resources/swe-book/html/ch12.html
- Google Testing Blog, «Change-Detector Tests Considered Harmful», 2015.
  https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html
- Google Testing Blog, «Code Coverage Best Practices», 2020.
  https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Anthropic, «Best practices for Claude Code»: просить тест на названный случай.
  https://code.claude.com/docs/en/best-practices
- Google, «Software Engineering at Google», гл. 13: настоящая зависимость, подделка, заглушка.
  https://abseil.io/resources/swe-book/html/ch13.html
- Anthropic, «Claude prompting best practices»: модель иногда проходит тест частным решением.
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Основание правил:

| Правило | Основание |
|---|---|
| 1, 3 | Источник и наши случаи |
| 2, 4 | Только наши случаи: возвраты и живые прогоны |
| 5, 6 | Только источник. В нашем замере этих ошибок почти нет |

## `which-to-run.md`

Указатели из шапки: Испытан на учебном проекте — `docs/probes/tests-reference/README.md`. Откуда взято каждое правило — `docs/tests-synthesis.md`.

- Google, «Software Engineering at Google», гл. 23: до слияния — быстрые тесты своего проекта, остальное
  после. https://abseil.io/resources/swe-book/html/ch23.html
- Stripe, «Selective Test Execution at Stripe», 2026: выбор по изменённым файлам и обязательные тесты.
  https://stripe.dev/blog/selective-test-execution-at-stripe-fast-ci-for-a-50m-line-ruby-monorepo
- Shopify, «Spark Joy by Running Fewer Tests», 2020: связь не отследить — гонять всё; полный набор при выпуске.
  https://shopify.engineering/spark-joy-by-running-fewer-tests
- Microsoft, «Use Test Impact Analysis»: затронутые, ранее падавшие и новые тесты.
  https://learn.microsoft.com/en-us/azure/devops/pipelines/test/test-impact-analysis
- OpenAI, «Rethinking skills and prompts», 09.2026: общее напоминание о тестах даёт лишние прогоны.
  https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

Основание правил:

| Правило | Основание |
|---|---|
| 1, 3, 5 | Источник и наш замер |
| 2 | Источник и наши случаи |
| 4, 6, 7 | Только наши случаи и замер |
| 8 | Только источник. В нашем замере прогон по файлам идёт секунды |
