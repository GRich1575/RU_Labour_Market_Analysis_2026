# Виртуальное окружение (venv)

Изолирует библиотеки проекта от системного Python. Папка `.venv/` в git не попадает.

## Создать и активировать

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Cmd (не PowerShell): `.venv\Scripts\activate.bat`. Интерпретатор через лаунчер: `py -3.13 -m venv .venv`.

### macOS (zsh / bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Python из Homebrew: `brew install python@3.13`, затем `python3.13 -m venv .venv`. Системный Python от Apple (Xcode CLT) старый — не использовать.

### Linux / Unix-like (bash / zsh)
```bash
python3 -m venv .venv      # Debian/Ubuntu: сначала sudo apt install python3-venv
source .venv/bin/activate
```
Fish: `source .venv/bin/activate.fish`. Csh/tcsh: `source .venv/bin/activate.csh`.

## Проверка
```
# Windows (PowerShell)
python -c "import sys; print(sys.prefix)"   # путь указывает на .venv
where.exe python                             # первый путь — .venv

# macOS / Linux
python3 -c "import sys; print(sys.prefix)"
which python                                 # первый путь — .venv
```

## Выйти
```
deactivate                                   # все ОС
```

## Пересоздать (если окружение сломано)
```powershell
# Windows
Remove-Item -Recurse -Force .venv
python -m venv .venv
```
```bash
# macOS / Linux
rm -rf .venv
python3 -m venv .venv
```

## Частые проблемы
- Windows: `Activate.ps1 cannot be loaded ... execution policy` → `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (один раз).
- macOS: `xcrun: error: invalid active developer path` → `xcode-select --install`.
- Linux: `ensurepip is not available` → установить `python3.X-venv` для вашей версии (Debian/Ubuntu: `sudo apt install python3.13-venv`).
- Библиотека «не найдена» в Jupyter/IDE → выбрать интерпретатор `.venv\Scripts\python.exe`.
- Не вызывать `pip install` без активированного venv — установится в системный Python.
