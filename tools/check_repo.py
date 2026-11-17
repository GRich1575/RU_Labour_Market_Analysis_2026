#!/usr/bin/env python3
"""Проверки репозитория (C1–C10, см. docs/team/automation_design.md).

Запуск из любой папки:  python tools/check_repo.py
Выход: 0 — нарушений нет; 1 — есть нарушения.
Формат нарушения: путь:строка: что нарушено.

Зависимости: стандартная библиотека и pyyaml. Файлы в data/raw/ не читаются.
Проверяются только файлы под контролем git (git ls-files).
"""

import csv
import functools
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]

SOURCE_FIELDS = [
    "id", "name", "provider", "role", "goal", "indicators", "access", "format",
    "frequency", "geography", "status", "data_2026", "enabled", "notes",
]
STATUS_VALUES = {"to_verify", "verified"}
DATA_2026_VALUES = {"available", "N/A", "unverified"}
MANIFEST_HEADER = [
    "file", "source_id", "period", "sha256", "size_bytes", "downloaded_on",
    "origin_url", "member_id", "status", "notes",
]
MANIFEST_STATUS = {"active", "superseded", "rejected"}
SAMPLE_NAME_RE = re.compile(
    r"^[a-z][a-z0-9_]*_sample_\d{4}(-\d{2}|-Q[1-4])?(to\d{4}(-\d{2}|-Q[1-4])?)?\.csv$"
)
SAMPLE_MAX_ROWS = 200
SAMPLE_MAX_BYTES = 1_048_576

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"github_pat_"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN .*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|api[_-]?key|token)\s*[:=]\s*[\"']?[A-Za-z0-9_\-+/=.]{12,}"),
]
ABS_PATH_RE = re.compile(r"[A-Za-z]:\\|/Users/")
# [текст](цель) или [текст](цель "заголовок"); цель может содержать пробелы
LINK_RE = re.compile(r"\]\(([^)]+?)(?:\s+\"[^\"]*\")?\)")
SUMMARY_RE = re.compile(r"<!--\s*registry-summary:\s*(.*?)\s*-->")

# Сам скрипт и файл исключений описывают шаблоны, поэтому не сканируются (C7–C9).
SELF_FILES = {"tools/check_repo.py", "tools/check_exceptions.yaml"}

violations = []   # (путь, строка, сообщение, правило)
current_rule = ["C0"]


def set_rule(code):
    current_rule[0] = code


def report(path, line, message):
    violations.append((str(path), int(line), message, current_rule[0]))


def load_exceptions():
    path = ROOT / "tools" / "check_exceptions.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("exceptions") or []


def is_excepted(path, line, rule, exceptions):
    """Исключение: тот же файл, то же правило и строка содержит фрагмент `contains`."""
    try:
        lines = file_lines(path)
    except (OSError, UnicodeDecodeError):
        return False
    if not 1 <= line <= len(lines):
        return False
    text = lines[line - 1]
    return any(
        ex.get("file") == path
        and ex.get("rule") == rule
        and ex.get("contains", "")
        and ex["contains"] in text
        for ex in exceptions
    )


def git_files():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True, check=True,
    ).stdout.decode("utf-8")
    return [p for p in out.split("\0") if p]


def read_text(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def read_lines(rel):
    return read_text(rel).splitlines()


@functools.lru_cache(maxsize=None)
def file_lines(rel):
    """Строки файла, читается один раз за запуск (кэш по пути)."""
    return tuple(read_lines(rel))


def line_of(lines, pattern):
    rx = re.compile(pattern)
    for i, text in enumerate(lines, start=1):
        if rx.search(text):
            return i
    return 1


def load_yaml(rel):
    try:
        return yaml.safe_load("\n".join(read_lines(rel))) or {}
    except (yaml.YAMLError, OSError) as exc:
        report(rel, 1, f"не читается как YAML: {exc}")
        return None


def in_set(value, allowed):
    """Безопасная проверка: нестроковые значения (списки, словари) не совпадают."""
    return isinstance(value, str) and value in allowed


# C1, C2, C10 counts ---------------------------------------------------------

def check_sources():
    """C1 схема реестра, C2 правило 2026. Возвращает счётчики для C10."""
    rel = "config/sources.yaml"
    set_rule("C1")
    lines = read_lines(rel)
    data = load_yaml(rel)
    counts = {"total": 0, "available": 0, "enabled": 0, "na": 0, "unverified": 0}
    if data is None:
        return None
    sources = data.get("sources")
    if not isinstance(sources, list):
        report(rel, 1, "нет списка `sources`")
        return None

    seen_ids = set()
    for src in sources:
        if not isinstance(src, dict):
            report(rel, 1, "блок источника не является словарём")
            continue
        sid = src.get("id")
        where = line_of(lines, rf"^\s*-?\s*id:\s*{re.escape(str(sid))}\s*$")
        missing = [f for f in SOURCE_FIELDS if f not in src]
        if missing:
            report(rel, where, f"{sid}: нет полей {', '.join(missing)}")
        if not isinstance(sid, str) or not re.match(r"^[a-z][a-z0-9_]*$", sid):
            report(rel, where, f"id `{sid}`: допустимы строчные латинские буквы, цифры и `_`")
        elif sid in seen_ids:
            report(rel, where, f"id `{sid}` повторяется")
        if isinstance(sid, str):
            seen_ids.add(sid)

        status = src.get("status")
        if not in_set(status, STATUS_VALUES):
            report(rel, where, f"{sid}: status `{status}` (допустимо: to_verify, verified)")
        d26 = src.get("data_2026")
        if not in_set(d26, DATA_2026_VALUES):
            report(rel, where, f"{sid}: data_2026 `{d26}` (допустимо: available, N/A, unverified)")
        enabled = src.get("enabled")
        if not isinstance(enabled, bool):
            report(rel, where, f"{sid}: enabled должен быть true или false")
        elif enabled and d26 != "available":
            set_rule("C2")
            report(rel, where, f"{sid}: enabled: true, но data_2026 не `available` (правило 2026)")
            set_rule("C1")

        counts["total"] += 1
        if d26 == "available":
            counts["available"] += 1
        if enabled is True:
            counts["enabled"] += 1
        if d26 == "N/A":
            counts["na"] += 1
        if d26 == "unverified":
            counts["unverified"] += 1
    return counts


def check_project():
    set_rule("C1")
    rel = "config/project.yaml"
    data = load_yaml(rel)
    if data is not None and not isinstance(data.get("target_year"), int):
        report(rel, line_of(read_lines(rel), r"target_year"), "target_year должен быть целым числом")


# C10 ------------------------------------------------------------------------

def check_summaries(counts):
    set_rule("C10")
    if counts is None:
        return
    for rel in ["PROGRESS.md", "docs/stage1/brief.md"]:
        try:
            text = read_text(rel)
        except OSError:
            report(rel, 1, "файл не найден (нужен для сверки сводки реестра)")
            continue
        m = SUMMARY_RE.search(text)
        if not m:
            report(rel, 1, "нет маркера <!-- registry-summary: ... -->")
            continue
        line = text.count("\n", 0, m.start()) + 1
        pairs = dict(re.findall(r"(\w+)=(\d+)", m.group(1)))
        for key, expected in counts.items():
            if key not in pairs:
                report(rel, line, f"в маркере нет `{key}` (ожидается {expected})")
            elif int(pairs[key]) != expected:
                report(rel, line, f"`{key}`={pairs[key]} в маркере, в реестре {expected}")


# C3 ------------------------------------------------------------------------

def check_not_in_git(files):
    set_rule("C3")
    for p in files:
        if not (p.startswith("data/raw/") or p.startswith("data/processed/")):
            continue
        if Path(p).name == "README.md":
            continue
        report(p, 1, "данные не должны храниться в git (data/raw/, data/processed/)")


# C4, C5 ---------------------------------------------------------------------

def check_samples(files):
    """Только файлы под контролем git: то же, что проверяет CI."""
    for rel in files:
        if not rel.startswith("data/samples/"):
            continue
        path = ROOT / rel
        set_rule("C4")
        if not SAMPLE_NAME_RE.match(path.name):
            report(rel, 1, "имя образца не по шаблону <id>_sample_<период>.csv")
        set_rule("C5")
        if not path.is_file():
            report(rel, 1, "файл есть в git, но отсутствует на диске")
            continue
        raw = path.read_bytes()
        if len(raw) > SAMPLE_MAX_BYTES:
            report(rel, 1, f"размер {len(raw)} байт > {SAMPLE_MAX_BYTES}")
        if raw.startswith(b"\xef\xbb\xbf"):
            report(rel, 1, "файл с BOM (нужен UTF-8 без BOM)")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            report(rel, 1, "не декодируется как UTF-8")
            continue
        lines = text.splitlines()
        if not lines:
            report(rel, 1, "пустой файл")
            continue
        header = lines[0]
        if ";" not in header or "," in header:
            report(rel, 1, "первая строка: разделитель должен быть `;`, а `,` в заголовке недопустима")
        if len(lines) - 1 > SAMPLE_MAX_ROWS:
            report(rel, 1, f"строк данных {len(lines) - 1} > {SAMPLE_MAX_ROWS}")


# C6 ------------------------------------------------------------------------

def check_manifest():
    set_rule("C6")
    rel = "data/MANIFEST.csv"
    path = ROOT / rel
    if not path.exists():
        return
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows or rows[0] != MANIFEST_HEADER:
        report(rel, 1, "заголовок не совпадает с ожидаемым")
        return
    for n, row in enumerate(rows[1:], start=2):
        if not row:
            continue  # пустая строка между записями — не запись
        if len(row) != len(MANIFEST_HEADER):
            report(rel, n, f"число полей {len(row)}, ожидается {len(MANIFEST_HEADER)}")
            continue
        rec = dict(zip(MANIFEST_HEADER, row))
        if not re.match(r"^[0-9a-f]{64}$", rec["sha256"]):
            report(rel, n, "sha256 должен быть 64 символа hex в нижнем регистре")
        if rec["status"] not in MANIFEST_STATUS:
            report(rel, n, f"status `{rec['status']}` (допустимо: active, superseded, rejected)")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", rec["downloaded_on"]):
            report(rel, n, "downloaded_on должен быть ГГГГ-ММ-ДД")


# C7 ------------------------------------------------------------------------

def check_secrets(files):
    set_rule("C7")
    for p in files:
        try:
            lines = file_lines(p)
        except (UnicodeDecodeError, OSError):
            continue  # бинарные файлы
        for n, line in enumerate(lines, start=1):
            for rx in SECRET_PATTERNS:
                if rx.search(line):
                    report(p, n, "возможный секрет (токен, ключ, пароль)")
                    break


# C8 ------------------------------------------------------------------------

def check_absolute_paths(files):
    set_rule("C8")
    for p in files:
        if not p.endswith((".md", ".py", ".yaml")) or p.startswith("docs/team/"):
            continue
        try:
            lines = file_lines(p)
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, start=1):
            if ABS_PATH_RE.search(line):
                report(p, n, "абсолютный путь (используйте относительные)")


# C9 ------------------------------------------------------------------------

def check_links(files):
    set_rule("C9")
    for p in files:
        if not p.endswith(".md"):
            continue
        base = (ROOT / p).parent
        try:
            lines = file_lines(p)
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, start=1):
            for target in LINK_RE.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = unquote(target.split("#", 1)[0])
                if not target:
                    continue
                if not (base / target).exists():
                    report(p, n, f"битая ссылка: {target}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # кириллица в консоли Windows
    files = [f for f in git_files() if f not in SELF_FILES]
    counts = check_sources()
    check_project()
    check_summaries(counts)
    check_not_in_git(files)
    check_samples(files)
    check_manifest()
    check_secrets(files)
    check_absolute_paths(files)
    check_links(files)

    exceptions = load_exceptions()
    left = [
        v for v in violations
        if not is_excepted(v[0], v[1], v[3], exceptions)
    ]
    for path, line, message, rule in left:
        print(f"{path}:{line}: [{rule}] {message}")
    if left:
        print(f"\ncheck_repo: нарушений: {len(left)}")
        return 1
    print("check_repo: нарушений нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
