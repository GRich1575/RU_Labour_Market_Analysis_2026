# XLSX (Excel) — шпаргалка

Источники: таблицы Росстата, ЕМИСС. Файлы в `data/raw/<id>/` не редактировать.

Библиотека: `openpyxl` (движок для `.xlsx`, подключается pandas автоматически).

## pandas (основной способ)
```python
import pandas as pd

# список листов
xl = pd.ExcelFile("data/raw/rosstat_orc/file.xlsx")
print(xl.sheet_names)

# один лист, пропуск шапки
df = pd.read_excel(xl, sheet_name="Таблица 1", skiprows=3, header=0)

# все листы
sheets = pd.read_excel("file.xlsx", sheet_name=None)
```

## openpyxl (низкий уровень, для сложной разметки)
```python
from openpyxl import load_workbook

wb = load_workbook("file.xlsx", read_only=True, data_only=True)
ws = wb["Таблица 1"]
for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
    print(row)
wb.close()
```
- `data_only=True` — значения формул, а не сами формулы.
- `read_only=True` — экономит память на больших файлах; обязательно `close()`.

## Ловушки
- Шапка и сноски в таблицах Росстата: найти строку заголовка, задать `skiprows`/`usecols`.
- Объединённые ячейки дают `NaN` в каждой второй строке → `df[col].ffill()`.
- Числа могут быть текстом (`"2,2"`): `pd.to_numeric(df[c].astype(str).str.replace(",", "."), errors="coerce")`.
- Формат `.xls` (старый) openpyxl не читает — нужен `xlrd`, либо пересохранить в `.xlsx`.
- Открытый в Excel файл может блокироваться для записи; для чтения не мешает.
