"""Разбор ежемесячных отчётов hh.ru «Краткий обзор рынка труда» (stats.hh.ru).

Вход:  data/raw/hh_monthly/stats_monthly-report_2026-<месяц>.pdf
Выход: data/processed/hh_monthly_2026_headline.csv  (общие показатели, по отчёту)
       data/processed/hh_monthly_2026_spheres.csv   (таблицы «Рэнкинг» по сферам и специализациям)

Запуск: .venv/Scripts/python.exe tools/parse_hh_monthly.py
"""
import csv
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hh_monthly"
OUT = ROOT / "data" / "processed"

# Родительный падеж месяцев в тексте сноски («Уровень безработицы в феврале 2026 года»).
MONTH_STEMS = [("январ", 1), ("феврал", 2), ("март", 3), ("апрел", 4), ("ма", 5), ("июн", 6),
               ("июл", 7), ("август", 8), ("сентябр", 9), ("октябр", 10), ("ноябр", 11), ("декабр", 12)]
HEAD_RE = re.compile(r"(\d+,\d)\s+(\d+,\d)%\s+([+–-]?\d+)%\s+([+–-]?\d+)%")
REF_RE = re.compile(r"Уровень безработицы в (\w+) (\d{4}) года")
ROW_RE = re.compile(
    r"^(?P<name>.+?)\s+(?P<sv>\d+(?:,\d+)?)%\s+(?P<sr>\d+(?:,\d+)?)%\s+(?P<hh>\d+,\d+)"
    r"\s+(?P<dv>[+–-]?\d+)%\s+(?P<dr>[+–-]?\d+)%\s*$")


def num(s):
    return float(s.replace(",", ".").replace("–", "-").replace("+", ""))


def month_number(word):
    for stem, m in MONTH_STEMS:
        if word.startswith(stem):
            return m
    raise ValueError(f"неизвестный месяц: {word}")


def parse_report(path):
    tag = path.stem.replace("stats_monthly-report_", "")
    with pdfplumber.open(path) as pdf:
        pages = [(pg.extract_text() or "") for pg in pdf.pages]
    text = "\n".join(pages)
    head_m = HEAD_RE.search(pages[1])
    ref = REF_RE.search(text)
    head = dict(report=tag, hh_index=num(head_m.group(1)), unemployment_pct=num(head_m.group(2)),
                unemp_ref=f"{ref.group(2)}-{month_number(ref.group(1)):02d}",
                d_vacancies_yoy_pct=num(head_m.group(3)), d_resumes_yoy_pct=num(head_m.group(4)))
    rows, section, prev = [], None, ""
    for line in text.split("\n"):
        s = line.strip()
        if "Рэнкинг" in s:
            section = (prev + " | " + s)[:200]
            continue
        m = ROW_RE.match(s)
        if m and section:
            rows.append(dict(report=tag, section=section, name=m.group("name"),
                             share_vacancies_pct=num(m.group("sv")), share_resumes_pct=num(m.group("sr")),
                             hh_index=num(m.group("hh")), d_vacancies_yoy_pct=num(m.group("dv")),
                             d_resumes_yoy_pct=num(m.group("dr"))))
        if s and not m and not s.startswith(("Данные", "Доля", "активных", "вакансий")):
            prev = s
    return head, rows


def main():
    heads, spheres = [], []
    for pdf_path in sorted(RAW.glob("stats_monthly-report_2026-*.pdf")):
        head, rows = parse_report(pdf_path)
        heads.append(head)
        spheres.extend(rows)
        print(f"{head['report']}: строк по сферам {len(rows)}")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [("hh_monthly_2026_headline.csv", heads), ("hh_monthly_2026_spheres.csv", spheres)]:
        with open(OUT / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    print(f"итого: отчётов {len(heads)}, строк по сферам {len(spheres)}")


if __name__ == "__main__":
    main()
