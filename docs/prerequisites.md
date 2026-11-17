# Требования и окружение

## 1. Программы
| Что | Версия | Зачем |
|---|---|---|
| Python | 3.11+ (проверено на 3.13) | язык проекта |
| Git | любая современная | версии, ветки |
| Excel / LibreOffice | любая | просмотр XLSX и CSV (CSV открывать с кодировкой UTF-8, разделитель `;`) |
| Текстовый редактор | VS Code / Notepad++ | правка `config/sources.yaml` (UTF-8, без табов) |

## 2. Получение репозитория и окружение Python
Путь к папке у каждого свой. Примеры ниже используют `<путь-к-репозиторию>` — подставьте свой.

Клонирование (любая ОС):
```
git clone <url-репозитория> <путь-к-репозиторию>
```

Windows (PowerShell):
```powershell
cd <путь-к-репозиторию>          # например: cd C:\Users\<имя>\Projects\RU_Labour_Market_Analysis_2026
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
macOS / Linux (bash / zsh):
```bash
cd <путь-к-репозиторию>          # например: cd ~/Projects/RU_Labour_Market_Analysis_2026
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Все относительные пути в проекте (`config/`, `data/`, `docs/`) — от корня репозитория; запускать команды из корня.

Виртуальное окружение `.venv/` не попадает в git (см. `.gitignore`). Окружение привязано к папке — при переносе репозитория пересоздать его.

Если `Activate.ps1` запрещён политикой: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (один раз).

## 3. Python-библиотеки (`requirements.txt`)
| Библиотека | Для чего |
|---|---|
| pandas | таблицы, чтение и запись CSV/XLSX, расчёты |
| numpy | числовые операции (зависимость pandas) |
| pyyaml | чтение `config/sources.yaml` |
| requests | загрузка файлов и JSON по API (hh.ru и др.) |
| openpyxl | чтение XLSX (`pandas.read_excel`) |
| pyreadstat | SPSS `.sav` / Stata (`pandas.read_spss`, RLMS-HSE, HSE) |
| lxml | HTML (`pandas.read_html`) и XML (`pandas.read_xml`) |
| pdfplumber | таблицы из PDF-сборников Росстата и ЦБ |
| pytest | тесты (с этапа 2) |

Позже (этап 4, дашборды): `streamlit`, `plotly` — добавляются в `requirements.txt` в момент начала этапа.

## 4. Форматы файлов
| Формат | Где используется | Правило в проекте |
|---|---|---|
| YAML (`.yaml`) | `config/sources.yaml` — реестр источников; позже периоды, параметры | UTF-8; отступы 2 пробела; без табов; строки в кавычках, если есть `:` или `#` |
| CSV (`.csv`) | `data/processed/`, `data/reference/`, часть источников | UTF-8, разделитель `;`, десятичная запятая или точка — фиксируется в заголовке README таблицы; заголовок в первой строке |
| XLSX (`.xlsx`) | таблицы Росстата, ЕМИСС | не редактировать; читать `pandas.read_excel(sheet_name=...)` |
| PDF (`.pdf`) | сборники Росстата, ЦБ | не редактировать; таблицы извлекать `pdfplumber`, результат проверять вручную |
| JSON (`.json`) | API hh.ru, ряды ЦБ | сохранять как есть в `data/raw/<id>/` |
| HTML / XML | страницы ЕМИСС, ЦБ | сохранять как есть в `data/raw/<id>/` |
| SPSS (`.sav`), Stata (`.dta`) | RLMS-HSE, HSE ISIEZ | читать через `pyreadstat`; метки значений — в `data/reference/` |
| Markdown (`.md`) | документация, `PROGRESS.md` | UTF-8, ≤60 строк для `PROGRESS.md` |

### Стандарт обработанной таблицы (`data/processed/`)
Длинный формат, один показатель на файл:
```
дата;регион;показатель;значение;единица;источник
2026-01;РФ;безработица;2.2;%;rosstat_orc
```
- Даты: `ГГГГ-ММ` (месяц), `ГГГГ-КК` (квартал).
- Идентификатор источника в колонке `источник` — `id` из `config/sources.yaml`.

### Стандарт реестра источников (`config/sources.yaml`)
Каждый блок — один источник, обязательные поля:
`id`, `name`, `provider`, `role`, `goal`, `indicators`, `access`, `format`, `frequency`, `geography`, `status`, `notes`.
- `id` — латиница и `_`, уникален, совпадает с папкой `data/raw/<id>/`.
- `status`: `to_verify` (не проверено) или `verified` (проверено вручную).

## 5. Ограничения и проверки
- Сырые данные (`data/raw/`) и обработанные (`data/processed/`) в git не попадают; справочники `data/reference/` — попадают.
- Персональных данных и ключей API в репозиторий не добавлять (`.env` игнорируется).
- Перед загрузкой по API проверять условия использования источника (лимиты hh.ru, ЕМИСС).
