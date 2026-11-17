# Домашнее задание (необязательно): настройка компьютера

Цель: подготовить компьютер, чтобы работать с проектом. Задание не обязательное, но упрощает работу на этапах 2–7.

Время: 1–2 часа. Нужны права администратора на компьютере.

---

## Что понадобится

| Программа | Зачем | Ссылка |
|---|---|---|
| Python 3.11 или новее | язык, на котором написан проект | https://www.python.org/downloads/ |
| Git | история изменений и загрузка проекта | https://git-scm.com/downloads |
| Visual Studio Code | редактор кода и текстов | https://code.visualstudio.com/ |
| Аккаунт GitHub | доступ к репозиторию | https://github.com/signup |
| LibreOffice (необязательно) | открыть CSV и XLSX без Excel | https://www.libreoffice.org/download/ |

Проверка: после установки каждая программа должна открываться без ошибок.

---

## Шаг 1. Выберите свою систему

- **Windows 10 / 11** — раздел A.
- **macOS** — раздел B.
- **Linux (Ubuntu, Debian, Fedora и др.)** — раздел C.

Не знаете, какая у вас система? Windows: «Параметры → Система → О системе». macOS: меню Apple → «Об этом Mac».

---

## Раздел A. Windows

### A1. Python
1. Откройте https://www.python.org/downloads/ и скачайте установщик Python 3.13 (или новее).
2. Запустите установщик.
3. **Обязательно** отметьте галочку «Add python.exe to PATH» внизу окна.
4. Нажмите «Install Now».
5. Проверка: откройте PowerShell (Пуск → введите `powershell` → Enter) и выполните:
   ```powershell
   python --version
   ```
   Должно появиться `Python 3.13.x`.

Альтернатива: `winget install Python.Python.3.13` в PowerShell.

### A2. Git
1. Скачайте установщик с https://git-scm.com/download/win.
2. Установите с настройками по умолчанию (нажимайте «Next»).
3. Проверка:
   ```powershell
   git --version
   ```

Альтернатива: `winget install Git.Git`.

### A3. Visual Studio Code
1. Скачайте https://code.visualstudio.com/ и установите.
2. Проверка: откройте VS Code.

Альтернатива: `winget install Microsoft.VisualStudioCode`.

### A4. Политика запуска скриптов (один раз)
Чтобы включить виртуальное окружение в PowerShell, выполните:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Ответьте `Y` (да), если спросят.

Переходите к разделу D.

---

## Раздел B. macOS

### B1. Homebrew (менеджер программ)
Откройте «Терминал» (Launchpad → «Другие» → «Терминал») и выполните команду с сайта https://brew.sh/ (раздел «Install Homebrew»). Команда начинается с `/bin/bash -c "$(curl ...`.

Если появится запрос установить Command Line Tools — согласитесь.

### B2. Python и Git
```bash
brew install python@3.13 git
```
Проверка:
```bash
python3 --version
git --version
```
Для проекта используйте `python3` (не `python`), если на Mac нет отдельной ссылки `python`.

### B3. Visual Studio Code
```bash
brew install --cask visual-studio-code
```
Или скачайте с https://code.visualstudio.com/.

Переходите к разделу D.

---

## Раздел C. Linux

Команды для Ubuntu / Debian. Для Fedora: `sudo dnf install python3 python3-pip git`.

### C1. Python, venv, Git
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```
Проверка:
```bash
python3 --version
git --version
```

### C2. Visual Studio Code
Скачайте `.deb` или через магазин приложений: https://code.visualstudio.com/docs/setup/linux

Переходите к разделу D.

---

## Раздел D. Общие шаги (все системы)

### D1. Аккаунт GitHub
1. Зарегистрируйтесь на https://github.com/signup.
2. Сообщите координатору логин — доступ к репозиторию выдаётся вручную, если репозиторий закрытый.

### D2. Загрузка проекта
Выберите папку, например `Projects` в домашней папке. Выполните в терминале (PowerShell на Windows, Terminal на macOS/Linux):

```
git clone https://github.com/GRich1575/RU_Labour_Market_Analysis_2026.git
```

Если Git запросит логин и пароль: пароль на GitHub больше не работает, используйте токен — https://github.com/settings/tokens (или войдите через VS Code: «Accounts» → «Sign in with GitHub»).

Перейдите в папку проекта:
```
cd RU_Labour_Market_Analysis_2026
```

### D3. Виртуальное окружение и библиотеки

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Установка занимает несколько минут. Когда строка приглашения начинается с `(.venv)`, окружение включено.

### D4. Проверка установки
Выполните (окружение должно быть включено):
```
python -c "import pandas, yaml, requests; print('Готово: pandas', pandas.__version__)"
```
Если видно `Готово: pandas ...` — установка прошла.

---

## Частые проблемы

| Ошибка | Что делать |
|---|---|
| `python` не найден (Windows) | переустановите Python с галочкой «Add python.exe to PATH» |
| `Activate.ps1 cannot be loaded` | выполните шаг A4 |
| `git` не найден | закройте и откройте терминал заново; если не помогло — переустановите Git |
| `No module named 'pandas'` | окружение не включено: повторите активацию (шаг D3) |
| `Permission denied` (macOS/Linux) | не используйте `sudo pip`; используйте только `.venv` |

Подробнее: `docs/prerequisites.md`, шпаргалки в `docs/cheatsheets/`.

---

## Задание (необязательно)
1. Выполните проверку D4.
2. Откройте папку проекта в VS Code: «File → Open Folder».
3. Откройте `config/sources.yaml`. Найдите источник `cbr_key_rate` и прочитайте поля `enabled` и `data_2026`.
4. Откройте `docs/cheatsheets/git.md` и выполните `git status` в терминале. Запишите результат.

Результат можно показать координатору. Не публикуйте логины, токены и пароли.
