# pytest — шпаргалка

Тесты в `tests/`, файлы `test_*.py`. Установка: `requirements.txt` (pytest>=8).

## Запуск
```
pytest                       # все тесты
pytest -q                    # кратко
pytest tests/test_loaders.py # один файл
pytest -k sources            # тесты, в имени которых есть "sources"
pytest -x                    # остановиться на первой ошибке
pytest -s                    # показать print()
```
Правило проекта: сначала точечно (`-k`), полный прогон — один раз в конце.

## Пример теста
```python
# tests/test_sources.py
import yaml

def test_all_ids_unique():
    with open("config/sources.yaml", encoding="utf-8") as f:
        ids = [s["id"] for s in yaml.safe_load(f)["sources"]]
    assert len(ids) == len(set(ids))
```

## Параметризация
```python
import pytest

@pytest.mark.parametrize("text,expected", [("2,2", 2.2), ("1 234", 1234.0)])
def test_parse_number(text, expected):
    assert parse_number(text) == expected
```

## Временные файлы
```python
def test_save(tmp_path):
    p = tmp_path / "out.csv"        # папка создаётся и удаляется автоматически
    save(p)
    assert p.exists()
```

## Исключения
```python
import pytest

def test_bad_status():
    with pytest.raises(ValueError):
        validate_status("unknown")
```

## Ловушки
- Тесты не должны ходить в сеть и читать `data/raw/` — использовать маленькие фикстуры в `tests/data/`.
- Имя файла и функции должно начинаться с `test_`, иначе pytest его пропустит.
- `assert` на float — `pytest.approx(x)`.
