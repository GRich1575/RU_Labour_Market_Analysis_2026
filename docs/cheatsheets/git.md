# Git — шпаргалка

Ветка работы: `feature/framework`. Основная: `main` (ещё не создана; см. `PROGRESS.md`).

## Состояние
```
git status                 # что изменено
git diff --stat            # сводка по изменениям
git log -n 10 --oneline    # последние коммиты
git branch --show-current  # текущая ветка
```

## Коммит
```
git add <файл>             # конкретные файлы, не "git add ."
git commit -m "Краткое описание"
```
- Не коммитить: `data/raw/`, `data/processed/`, `.venv/`, `.env` (уже в `.gitignore`).
- Перед коммитом проверить `git status` — нет ли лишнего.

## Ветки
```
git switch -c feature/new       # создать и перейти
git switch feature/framework    # перейти
git merge feature/new           # влить в текущую
```

## Отмена (аккуратно)
```
git restore <файл>              # откатить незакоммиченные правки файла
git restore --staged <файл>     # убрать из индекса, правки сохранить
git reset --soft HEAD~1         # отменить последний коммит, правки оставить
```
- `git reset --hard` и `git restore .` удаляют правки без возврата — только после проверки `git status`.

## Удалённый репозиторий
```
git remote -v
git push -u origin feature/framework   # первая отправка ветки
git pull
```
Пуш в origin — решение команды (см. открытые вопросы в `PROGRESS.md`).

## Переводы строк (CRLF / LF)
- Windows: `git config --global core.autocrlf true` — файлы в рабочей копии с CRLF, в репозитории LF.
- macOS / Linux: `git config --global core.autocrlf input` — только LF.
- Проверка: `git ls-files --eol config/sources.yaml` (показывает `i/lf` в индексе и `w/crlf` в рабочей копии).

## Ловушки
- `git add .` может захватить лишние файлы — указывать пути.
- Коммит с именем `Anonymous` — настроить `git config user.name` / `user.email` до первого коммита в команде.
- Правки в `.gitignore` не отслеживают уже добавленные файлы — сначала `git rm --cached <файл>`.
