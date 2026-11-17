# Шпаргалки по технологиям проекта

| Файл | Тема | Где используется |
|---|---|---|
| [python-venv.md](python-venv.md) | виртуальное окружение | везде |
| [pip-requirements.md](pip-requirements.md) | установка библиотек | `requirements.txt` |
| [pandas.md](pandas.md) | таблицы, чтение/запись | расчёты, `data/` |
| [numpy.md](numpy.md) | массивы, пропуски | расчёты |
| [yaml.md](yaml.md) | формат YAML, pyyaml | `config/sources.yaml` |
| [csv.md](csv.md) | формат CSV, кодировка | `data/processed/`, `data/reference/` |
| [xlsx.md](xlsx.md) | Excel, openpyxl | таблицы Росстата, ЕМИСС |
| [pdf.md](pdf.md) | pdfplumber | сборники Росстата, ЦБ |
| [html-xml.md](html-xml.md) | read_html / read_xml, lxml | страницы ЕМИСС, ЦБ |
| [json-requests.md](json-requests.md) | JSON, requests | API hh.ru, ряды ЦБ |
| [spss-stata.md](spss-stata.md) | pyreadstat | RLMS-HSE, HSE ISIEZ |
| [pytest.md](pytest.md) | тесты | `tests/` (этап 2+) |
| [git.md](git.md) | git: ветки, коммиты | весь репозиторий |
| [markdown.md](markdown.md) | Markdown | документация, `PROGRESS.md` |

Установка библиотек и программ: `docs/prerequisites.md`.

## Платформы
Команды даны для трёх систем, где они отличаются:
- **Windows** — PowerShell (основной); `cmd` отмечен отдельно.
- **macOS** — zsh/bash; Python через Homebrew (`python3`).
- **Linux / Unix-like** — bash/zsh; Python через пакетный менеджер (`python3`).

Различия по умолчанию: разделители путей (`\` и `/`), команда запуска Python (`python` или `python3`), просмотр файла (`Get-Content -TotalCount` или `head -n`), переводы строк (CRLF или LF).
