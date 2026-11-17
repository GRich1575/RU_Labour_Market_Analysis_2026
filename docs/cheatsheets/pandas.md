# pandas — шпаргалка

Импорт: `import pandas as pd`

## Чтение
```python
df = pd.read_csv("data/processed/x.csv", sep=";", encoding="utf-8-sig", decimal=",")
df = pd.read_excel("raw/file.xlsx", sheet_name="Таблица 1", skiprows=3)
sheets = pd.read_excel("raw/file.xlsx", sheet_name=None)   # dict: имя листа -> DataFrame
df = pd.read_spss("raw/file.sav")                          # нужен pyreadstat
tables = pd.read_html("raw/page.html")                     # list[DataFrame]
df = pd.read_xml("raw/file.xml", xpath=".//record")
```

## Запись
```python
df.to_csv("data/processed/x.csv", sep=";", index=False, encoding="utf-8", decimal=",")
```

## Осмотр
```python
df.head(5)            # первые 5 строк
df.dtypes             # типы колонок
df.shape              # (строки, колонки)
df.columns.tolist()
df.info()
df.describe()
```

## Выбор и фильтр
```python
df["значение"]                          # колонка (Series)
df[["дата", "значение"]]                # несколько колонок (DataFrame)
df[df["регион"] == "РФ"]                # фильтр строк
df.loc[df["значение"] > 5, ["дата"]]    # условие + колонка
df.iloc[0:5]                            # по позиции
```

## Преобразование
```python
df["значение"] = pd.to_numeric(df["значение"], errors="coerce")  # нечисло -> NaN
df["дата"] = pd.to_datetime(df["дата"], format="%Y-%m")
df["дата"] = pd.PeriodIndex(df["дата"], freq="M")
df = df.rename(columns={"old": "new"})
df = df.dropna(subset=["значение"])
df["год"] = df["дата"].dt.year
```

## Группировка и сводка
```python
df.groupby("регион")["значение"].mean()
df.pivot_table(index="дата", columns="регион", values="значение")
df.melt(id_vars=["дата"], var_name="регион", value_name="значение")  # wide -> long
pd.merge(df1, df2, on="регион", how="left")
```

## Ловушки
- Всегда указывать `sep`, `encoding`, `decimal` явно (см. [csv.md](csv.md)).
- `read_excel` без `sheet_name` читает только первый лист.
- `to_numeric(errors="coerce")` молча превращает мусор в NaN — проверять `isna().sum()`.
- `index=False` при записи CSV, иначе появится лишняя колонка.
