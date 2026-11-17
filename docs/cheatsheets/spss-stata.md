# SPSS (.sav) и Stata (.dta) — шпаргалка

Источники: RLMS-HSE, HSE ISIEZ. Файлы в `data/raw/<id>/` не редактировать.

Библиотека: `pyreadstat` (pandas использует её для `read_spss`).

## pandas
```python
import pandas as pd

df = pd.read_spss("data/raw/rlms_hse/file.sav")
df = pd.read_stata("data/raw/hse_isiez/file.dta")
```

## pyreadstat (метки и мета-информация)
```python
import pyreadstat

df, meta = pyreadstat.read_sav("file.sav", apply_value_formats=True)
print(meta.column_names)          # имена переменных
print(meta.column_labels[:5])     # подписи переменных
print(meta.variable_value_labels) # словари: код -> подпись
```
- `apply_value_formats=True` — подставляет подписи значений вместо кодов.
- `meta` сохранять в `data/reference/` (кодбук), чтобы расшифровка не терялась.

## Ловушки
- Коды пропусков в SPSS (например, `-9`, `99`) — заменить на NaN явно.
- Подписи в `apply_value_formats=True` меняют тип колонки на категориальный → сравнения по коду сломаются.
- Большие `.sav` читать по частям: `pyreadstat.read_sav(path, row_limit=1000)` для проверки.
- Кодировка меток — UTF-8 или cp1251; при кракозябрах передать `encoding="cp1251"`.
