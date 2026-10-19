# Дизайн-система «Атвинта»

Дизайн-система, собранная по сайту [atwinta.ru](https://atwinta.ru/): цвета, типографика, отступы, скругления, эффекты, компоненты, логотипы и иконки. Все значения взяты из CSS сайта (переменные `:root` и классы `text-h-*` / `text-p-*`).

Интерактивная версия: https://claude.ai/artifact/JygQERriLK4tAxKLAcRekB (приватная).

## Структура

```
project/
  README.md            брендбук: голос, цвет, типографика, сетка, движение, иконки
  tokens.json          все токены (цвета в двух темах, типографика, отступы, радиусы, тени, брейкпоинты)
  design-system.json   индекс системы для артефакта
  components/
    bundle.css         стили компонентов, классы at-*
    <Компонент>/       README.md (правила) + preview.html (живое превью)
  assets/
    Logos/             логотип для светлого и тёмного фона
    Icons/             иконки Material Symbols и фирменные пиктограммы
dist/
  tokens.css           CSS-переменные и классы стилей текста, собранные из tokens.json
```

## Как подключить

```html
<link rel="stylesheet" href="dist/tokens.css">
<link rel="stylesheet" href="project/components/bundle.css">

<html data-theme="light">
  <a class="at-btn at-btn--pink" href="#">Отправить</a>
  <h2 class="text-h-l">Лидеры на рынке заказной разработки</h2>
</html>
```

Тёмные секции — `data-theme="dark"` на обёртке.

## Компоненты

Button, Chip, Link, TextField, Checkbox, NumberFact, ServiceLine, ProjectCard, Header. Разметка — в `preview.html` каждого компонента, правила — в его `README.md`.

## Ограничения

- **Stem** — коммерческий шрифт ParaType, в репозиторий не включён. Без лицензии крупные заголовки отображаются Geologica.
- **Geologica** загружается с Google Fonts (OFL).
- Логотип и фирменный стиль принадлежат компании «Атвинта».
- Белый на `pink` (3.74:1) и `dark-gray` на белом (4.42:1) не дотягивают до WCAG AA для мелкого текста — оставлено как на сайте, отмечено в токенах.
