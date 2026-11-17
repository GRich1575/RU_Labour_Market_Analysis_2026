# NumPy — шпаргалка

Импорт: `import numpy as np`. Используется как основа pandas; напрямую — для расчётов по массивам.

## Массивы
```python
a = np.array([1.0, 2.5, np.nan])
np.arange(0, 10, 2)          # [0 2 4 6 8]
np.linspace(0, 1, 5)         # 5 равномерных точек от 0 до 1
np.zeros(3); np.ones((2, 3))
a.shape; a.dtype; a.ndim
```

## Пропуски
```python
np.isnan(a)                  # маска NaN
np.nanmean(a)                # среднее без NaN
np.nansum(a); np.nanmax(a)
```
- `np.nan == np.nan` → `False`. Проверять только через `np.isnan` / `pd.isna`.

## Условия и выбор
```python
np.where(a > 2, "высокая", "низкая")
a[a > 2]                     # булева маска
np.clip(a, 0, 10)
```

## Статистика и суммы
```python
np.mean(a); np.median(a); np.std(a, ddof=1)   # ddof=1 — выборочное стд.
np.round(a, 2)
np.cumsum(a)
np.diff(a)                    # разности соседних значений (прирост)
```

## Логарифмы и проценты
```python
np.log(a)                     # натуральный
np.log(a) - np.log(a.shift(1))  # темп роста (в pandas)
100 * (a / a[0] - 1)           # изменение к базе, %
```

## Ловушки
- Целочисленный массив не сохранит NaN: используйте `float`.
- `np.round` банковское (к чётному); для отчётов округлять в pandas/форматировании.
- Не сравнивать float через `==` — `np.isclose(a, b)`.
