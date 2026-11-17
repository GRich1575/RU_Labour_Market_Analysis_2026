# JSON и requests — шпаргалка

Источники: API hh.ru (JSON), ряды ЦБ (JSON/XML). Ответ API сохранять как есть в `data/raw/<id>/`.

## requests: GET с параметрами и таймаутом
```python
import requests

r = requests.get(
    "https://api.hh.ru/vacancies",
    params={"text": "аналитик", "area": 113, "per_page": 20},
    headers={"User-Agent": "labour-market-study/1.0 (contact via repo owner)"},
    timeout=30,
)
r.raise_for_status()        # исключение при 4xx/5xx
data = r.json()             # dict или list
```
- Всегда `timeout=` — иначе запрос может висеть бесконечно.
- Не хранить ключи API в коде: `os.environ["KEY"]`, файл `.env` (в `.gitignore`).

## Сохранить сырой ответ
```python
from pathlib import Path

out = Path("data/raw/hh_vacancies/2026-11.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(r.text, encoding="utf-8")
```

## Пагинация
```python
page = 0
while True:
    r = requests.get(url, params={"page": page, "per_page": 100}, timeout=30)
    r.raise_for_status()
    body = r.json()                       # парсим один раз
    items = body["items"]
    if not items or page >= body["pages"] - 1:
        break
    page += 1
```

## JSON в таблицу
```python
import json, pandas as pd

with open("raw.json", encoding="utf-8") as f:
    obj = json.load(f)
df = pd.json_normalize(obj["items"])     # вложенные поля -> колонки с точкой
```

## Ловушки
- Лимиты API (hh.ru и др.): задержка между запросами `time.sleep(0.5)`; соблюдать условия сервиса.
- `r.encoding` может быть неверным — для JSON использовать `r.json()` или `r.content.decode("utf-8")`.
- `json.dump(..., ensure_ascii=False)` — иначе кириллица в виде `\uXXXX`.
- Ответ с ошибкой может быть валидным JSON (`{"errors": ...}`) — проверять ключи, не только статус.
