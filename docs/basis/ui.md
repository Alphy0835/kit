# Основание справок об экране

Источники и основание правил справок `references/ui/`. Добавлено 19.10.2026 со скилом фронтенда. Случаи —
возвраты фронтенд-задач проекта-донора (заголовки коммитов возврата с 15.08 по 18.10.2026).

## `from-mockup.md`

- Правило проекта-донора D-122: принятый эталон дизайнера, свои цвета не придумывать (опись, К5).
- W3C, WCAG 2.2: 1.3.1, 3.3.2 «Labels or Instructions», 4.1.2 «Name, Role, Value», 1.4.10 «Reflow».
  https://www.w3.org/TR/WCAG22/
- W3C WAI, «Labeling Controls». https://www.w3.org/WAI/tutorials/forms/labels/
- W3C, ARIA Authoring Practices Guide — образцы сложных элементов. https://www.w3.org/WAI/ARIA/apg/
- Google web.dev, «Responsive web design basics». https://web.dev/articles/responsive-web-design-basics

| Правило | Основание |
|---|---|
| 1 | D-122, опись К5 |
| 2 | Старый скил фронтенда: состояния обязательны (опись К4) |
| 3 | CB_TASK_204, возврат 1: подпись разошлась с руководством |
| 4 | `code/changes.md`, правило 2 |
| 5 | WCAG, WAI, APG |
| 6 | web.dev, WCAG 1.4.10; старый скил: «не разваливаться на мобильной ширине» |
| 7 | `code/security.md`, правило 5 |

## `states.md`

- React, «Synchronizing with Effects», раздел о загрузке данных: отбрасывать ответ устаревшего запроса.
  https://react.dev/learn/synchronizing-with-effects
- MDN, `AbortController`. https://developer.mozilla.org/en-US/docs/Web/API/AbortController
- W3C, WCAG 2.2: 3.3.1 «Error Identification», 4.1.3 «Status Messages». https://www.w3.org/TR/WCAG22/
- GOV.UK Design System, «Error message». https://design-system.service.gov.uk/components/error-message/

| Правило | Основание |
|---|---|
| 1 | Старый скил фронтенда (опись К4) |
| 2 | CB_TASK_219, возврат 1 |
| 3 | CN_TASK_108, возврат 1 (подпись ошибки стёрта перерисовкой); CB_TASK_235, возврат 1 (группы после сохранения) |
| 4 | React, MDN; CB_TASK_176, возврат 1 |
| 5 | WD_TASK_003, возврат 1 (код при перезагрузке) |
| 6 | WCAG, GOV.UK |

## `backend-link.md`

| Правило | Основание |
|---|---|
| 1 | CB_TASK_239, возврат 1: `website` вместо `widget` |
| 2 | Общее правило замены элемента; класс «вид значения не тот» из замера возвратов (`docs/measure-returns.md`, «Плохой ввод») |
| 3 | `code/errors.md`, правило 5, со стороны экрана |
| 4 | `code/security.md`, правило 1 |
| 5 | `code/changes.md`, правило 2 |

## `verify.md`

- MDN, атрибут `hidden`: свойство `display` в стилях перебивает его.
  https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/hidden
- Testing Library, «Guiding Principles». https://testing-library.com/docs/guiding-principles/
- Playwright (Microsoft), «Locators»: по роли, подписи, тексту. https://playwright.dev/docs/locators

| Правило | Основание |
|---|---|
| 1 | MDN; опись В9; случай из заметок тим лида донора |
| 2 | CB_TASK_248, возврат 1: нет снимков главного |
| 3 | WCAG 2.1.1 «Keyboard», 2.4.7 «Focus Visible» |
| 4 | Testing Library, Playwright |
| 5 | `ui/backend-link.md`, правило 2 |
