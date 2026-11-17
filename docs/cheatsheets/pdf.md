# PDF — шпаргалка (pdfplumber)

Источники: сборники Росстата, ЦБ. PDF извлекается, результат всегда проверяется вручную.

Импорт: `import pdfplumber`

## Открыть и осмотреть
```python
import pdfplumber

with pdfplumber.open("data/raw/rosstat_part_time/file.pdf") as pdf:
    print(len(pdf.pages))                 # число страниц
    page = pdf.pages[0]                   # нумерация с 0
    print(page.extract_text()[:500])      # текст первых 500 символов
```

## Таблицы
```python
with pdfplumber.open("file.pdf") as pdf:
    tables = pdf.pages[10].extract_tables()   # list[list[list[str|None]]]
    first = tables[0]
```
Перевод в pandas:
```python
import pandas as pd
df = pd.DataFrame(first[1:], columns=first[0])   # первая строка — заголовок
```

## Поиск страницы по тексту
```python
with pdfplumber.open("file.pdf") as pdf:
    hits = [i for i, p in enumerate(pdf.pages) if "безработица" in (p.extract_text() or "")]
```

## Ловушки
- `extract_text()` может вернуть `None` для страницы-скана → `or ""`.
- Сканы (картинки) pdfplumber не читает — нужен OCR; отметить в `notes` реестра.
- Таблицы без линий: `page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})`.
- Номера страниц в сборнике ≠ индексы: `pages[i]` начинается с 0.
- Значения могут содержать неразрывные пробелы (`\xa0`) → `.replace("\xa0", " ")`.
