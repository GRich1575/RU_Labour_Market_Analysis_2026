# HTML / XML — шпаргалка (pandas + lxml)

Источники: страницы ЕМИСС, ЦБ. Сохранять исходный файл в `data/raw/<id>/`, затем парсить локально.

Библиотека: `lxml` (нужна для `read_html` и `read_xml`).

## HTML: таблицы со страницы
```python
import pandas as pd

tables = pd.read_html("data/raw/cbr_key_rate/page.html", encoding="utf-8")
print(len(tables))          # сколько таблиц найдено
df = tables[0]              # выбрать нужную по индексу
```
- Выбор по содержимому: `pd.read_html(path, match="Ключевая ставка")`.
- Прямой URL тоже работает, но сначала сохранить в `raw/` (воспроизводимость).

## XML
```python
df = pd.read_xml("data/raw/source/file.xml", xpath=".//record")
```
- `xpath` — путь к повторяющемуся элементу; проверить в файле до парсинга.
- Пространства имён (`xmlns`): передать `namespaces={"ns": "..."}` и `xpath="//ns:record"`.

## lxml напрямую (сложная структура)
```python
from lxml import etree

tree = etree.parse("file.xml")
values = tree.xpath("//value/text()")
```

## Ловушки
- `read_html` возвращает список: индекс таблицы может сместиться при изменении страницы — фиксировать через `match`.
- Таблицы с многоуровневой шапкой дают `MultiIndex` колонки → `df.columns = df.columns.get_level_values(-1)`.
- Без `lxml` установлено → `ImportError` в `read_html`/`read_xml`.
- Кодировка HTML: часто `windows-1251` → `encoding="windows-1251"`.
