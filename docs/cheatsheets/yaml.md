# YAML и pyyaml — шпаргалка

Формат конфигурации: `config/sources.yaml`.

## Синтаксис
```yaml
# комментарий
key: value                # пара ключ: значение (пробел после двоеточия обязателен)
number: 2026
flag: true
text: "строка: с двоеточием и #"   # кавычки, если есть спецсимволы
list: [1, 2, 3]
items:                    # список блоков
  - id: rosstat_orc
    goal: [1, 2]
  - id: cbr_key_rate
    goal: [1]
```
- Отступы — только пробелы (2 пробела), табы запрещены.
- Блок = один элемент списка `- `; поля блока — с отступом.
- Пустое значение: `notes:` даёт `null`.
- Строки с `:` или `#` в значении — в кавычках.

## Чтение и запись (pyyaml)
```python
import yaml

with open("config/sources.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)          # dict

sources = cfg["sources"]             # list[dict]
for s in sources:
    print(s["id"], s["status"])

with open("out.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
```
- Всегда `yaml.safe_load`, не `yaml.load` (небезопасно).
- `encoding="utf-8"` и `allow_unicode=True` — иначе кириллица станет `\uXXXX`.

## Проверка синтаксиса
```
# Windows
python -c "import yaml; yaml.safe_load(open('config/sources.yaml', encoding='utf-8')); print('ok')"
# macOS / Linux
python3 -c "import yaml; yaml.safe_load(open('config/sources.yaml', encoding='utf-8')); print('ok')"
```
- Строки с кириллицей в `-c` на Windows: если ошибка кодировки, `$env:PYTHONUTF8=1` (PowerShell) или `set PYTHONUTF8=1` (cmd).
- macOS/Linux: `export PYTHONUTF8=1` при аналогичной ошибке.

## Ловушки
- `no`, `off`, `yes` в YAML 1.1 — булевы; для строк ставить кавычки (`"no"`).
- Версии вида `2.10` станут числом `2.1` — писать `"2.10"`.
- Дубликат ключа в одном блоке — молча перезапишется; проверять уникальность `id`.
