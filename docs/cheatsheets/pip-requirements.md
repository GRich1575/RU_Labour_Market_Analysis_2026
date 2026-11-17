# pip и requirements.txt

Во всех командах — venv активирован (см. [python-venv.md](python-venv.md)).
Запускать через `python -m pip` (Windows: `python`; macOS/Linux: `python3`), чтобы pip совпал с интерпретатором.

## Основные команды
```
python -m pip install --upgrade pip    # Windows: python; macOS/Linux: python3 (или внутри venv: python)
pip install -r requirements.txt        # установить все зависимости проекта
pip install <пакет>                    # добавить пакет
pip list                               # установленные пакеты
pip show pandas                        # версия и путь пакета
pip list --outdated                    # что можно обновить
pip uninstall <пакет>
```
Внутри активированного venv на всех ОС команды одинаковые: `python -m pip ...`
(на macOS/Linux после `source .venv/bin/activate` `python` указывает на venv).

## Проверка без установки
```
pip install --dry-run -r requirements.txt
```

## Фиксация версий
- `requirements.txt` содержит минимальные версии (`pandas>=2.2`).
- Точные версии окружения: `pip freeze > requirements.lock.txt` (файл не коммитить без решения команды).

## Формат строк
```
pandas>=2.2          # не ниже версии
pytest==8.3.0        # строго эта версия
# комментарий        # строки с # игнорируются
```

## Частые проблемы
- Windows: ошибка сборки (`Microsoft Visual C++ 14.0`) → установить колёса: `pip install --only-binary :all: -r requirements.txt`; если колёс нет — Build Tools for Visual Studio.
- macOS: ошибки компиляции → `xcode-select --install`.
- Linux: ошибки сборки → установить `python3-dev` и `build-essential` (Debian/Ubuntu) или `gcc` (Fedora).
- Установка в системный Python вместо venv → см. [python-venv.md](python-venv.md).
