"""Тесты для tools/check_repo.py: каждая проверка падает на заведомо плохом примере.

Запуск: python -m pytest -q tests/test_check_repo.py
Каждый тест работает во временной папке (tmp_path), реальный репозиторий не меняется.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import check_repo as cr  # noqa: E402

GOOD_SOURCE = """\
sources:
  - id: cbr_key_rate
    name: Ключевая ставка
    provider: ЦБ РФ
    role: база
    goal: [1]
    indicators: ставка
    access: сайт ЦБ
    format: HTML
    frequency: по решениям
    geography: РФ
    status: verified
    data_2026: available
    enabled: true
    notes: образец
  - id: rosstat_orc
    name: ОРС
    provider: Росстат
    role: база
    goal: [1, 2]
    indicators: безработица
    access: ЕМИСС
    format: XLSX
    frequency: ежемесячно
    geography: РФ
    status: to_verify
    data_2026: unverified
    enabled: false
    notes: нет данных
"""

GOOD_SUMMARY = "<!-- registry-summary: total=2 available=1 enabled=1 na=0 unverified=1 -->"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Временный корень репозитория с валидным минимумом файлов."""
    monkeypatch.setattr(cr, "ROOT", tmp_path)
    monkeypatch.setattr(cr, "violations", [])
    cr._file_lines.cache_clear()
    write(tmp_path, "config/project.yaml", "target_year: 2026\n")
    write(tmp_path, "config/sources.yaml", GOOD_SOURCE)
    write(tmp_path, "PROGRESS.md", f"# P\n{GOOD_SUMMARY}\n")
    write(tmp_path, "docs/stage1/brief.md", f"# B\n{GOOD_SUMMARY}\n")
    yield tmp_path
    cr._file_lines.cache_clear()


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    cr._file_lines.cache_clear()
    return rel


def rules_found():
    return sorted({v[3] for v in cr.violations})


def messages():
    return [v[2] for v in cr.violations]


# C1, C2, C10 ----------------------------------------------------------------

def test_valid_registry_has_no_violations(repo):
    counts = cr.check_sources()
    cr.check_summaries(counts)
    cr.check_project()
    assert cr.violations == []


def test_enabled_without_available_is_c2(repo):
    write(repo, "config/sources.yaml", GOOD_SOURCE.replace(
        "data_2026: unverified\n    enabled: false", "data_2026: unverified\n    enabled: true"))
    cr.check_sources()
    assert "C2" in rules_found()


def test_list_valued_fields_do_not_crash(repo):
    write(repo, "config/sources.yaml", "sources:\n  - id: [x]\n    status: [verified]\n"
          "    data_2026: [N/A]\n    enabled: true\n")
    cr.check_sources()  # не должно падать с TypeError
    assert "C1" in rules_found()


def test_missing_field_is_c1(repo):
    write(repo, "config/sources.yaml", GOOD_SOURCE.replace("    notes: образец\n", ""))
    cr.check_sources()
    assert any("нет полей" in m and "notes" in m for m in messages())


def test_summary_mismatch_is_c10(repo):
    write(repo, "PROGRESS.md", "# P\n<!-- registry-summary: total=3 available=1 enabled=1 na=0 unverified=1 -->\n")
    cr.check_summaries(cr.check_sources())
    assert any("`total`=3" in m for m in messages())


def test_missing_summary_file_is_reported_not_crashing(repo):
    (repo / "docs/stage1/brief.md").unlink()
    cr.check_summaries(cr.check_sources())
    assert any("файл не найден" in m for m in messages())


# C3 -------------------------------------------------------------------------

def test_raw_data_in_git_is_c3(repo):
    cr.check_not_in_git(["data/raw/file.xlsx", "data/raw/README.md", "data/processed/x.csv"])
    found = [v[0] for v in cr.violations]
    assert found == ["data/raw/file.xlsx", "data/processed/x.csv"]


# C4, C5 ---------------------------------------------------------------------

def test_sample_bad_name_is_c4(repo):
    rel = write(repo, "data/samples/cbr/Bad Name.csv", "a;b\n1;2\n")
    cr.check_samples([rel])
    assert "C4" in rules_found()


def test_sample_too_many_rows_is_c5(repo):
    body = "a;b\n" + "1;2\n" * 201
    rel = write(repo, "data/samples/cbr/cbr_key_rate_sample_2026.csv", body)
    cr.check_samples([rel])
    assert "C5" in rules_found()


def test_sample_good_passes(repo):
    rel = write(repo, "data/samples/cbr/cbr_key_rate_sample_2026.csv", "a;b\n1;2\n")
    cr.check_samples([rel])
    assert cr.violations == []


# C6 -------------------------------------------------------------------------

HEADER = "file,source_id,period,sha256,size_bytes,downloaded_on,origin_url,member_id,status,notes\n"
SHA = "a" * 64


def test_manifest_blank_line_is_ignored(repo):
    write(repo, "data/MANIFEST.csv", HEADER + f"x.xlsx,rosstat_orc,2026,{SHA},10,2026-11-17,u,,active,\n\n")
    cr.check_manifest(["data/MANIFEST.csv"])
    assert cr.violations == []


def test_manifest_bad_sha_is_c6(repo):
    write(repo, "data/MANIFEST.csv", HEADER + "x.xlsx,rosstat_orc,2026,XYZ,10,2026-11-17,u,,active,\n")
    cr.check_manifest(["data/MANIFEST.csv"])
    assert "C6" in rules_found()


def test_untracked_manifest_is_not_checked(repo):
    write(repo, "data/MANIFEST.csv", HEADER + "x.xlsx,rosstat_orc,2026,XYZ,10,2026-11-17,u,,active,\n")
    cr.check_manifest([])  # файла нет в git — CI его не проверяет
    assert cr.violations == []


# C7 -------------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    "password: hunter2hunter2x",
    'api_key="abcdef123456789"',
    "ghp_" + "a" * 36,
    "gho_" + "a" * 36,
    "sk-ant-" + "a" * 25,
    "AIza" + "a" * 35,
    "-----BEGIN RSA PRIVATE KEY-----",
    "password: P@ssw0rd!2026xy",
])
def test_secret_patterns_match(line):
    assert any(rx.search(line) for rx in cr.SECRET_PATTERNS)


@pytest.mark.parametrize("line", [
    "token = None",
    "token: str",
    "my_token_count = 12",
    "Пароли и токены — в секретах, не в git",
])
def test_secret_patterns_ignore_code_and_prose(line):
    assert not any(rx.search(line) for rx in cr.SECRET_PATTERNS)


def test_check_secrets_reports_file_and_line(repo):
    rel = write(repo, "docs/notes.md", "ok\npassword: hunter2hunter2x\n")
    cr.check_secrets([rel])
    assert [(v[0], v[1], v[3]) for v in cr.violations] == [(rel, 2, "C7")]


# C8 -------------------------------------------------------------------------

def test_absolute_path_is_c8(repo):
    rel = write(repo, "docs/guide.md", "cd D:\\Projects\\x\n")
    cr.check_absolute_paths([rel])
    assert [(v[0], v[3]) for v in cr.violations] == [(rel, "C8")]


def test_absolute_path_in_team_docs_is_allowed(repo):
    rel = write(repo, "docs/team/example.md", "cd D:\\Projects\\x\n")
    cr.check_absolute_paths([rel])
    assert cr.violations == []


# C9 -------------------------------------------------------------------------

def test_broken_link_is_c9(repo):
    rel = write(repo, "docs/a.md", "[x](missing.md)\n")
    cr.check_links([rel])
    assert [v[3] for v in cr.violations] == ["C9"]


def test_link_with_title_and_encoded_space_resolves(repo):
    write(repo, "docs/my guide.md", "# g\n")
    rel = write(repo, "docs/a.md", '[x](my%20guide.md "title") [y](my guide.md)\n')
    cr.check_links([rel])
    assert cr.violations == []


# Exceptions -----------------------------------------------------------------

def test_exception_matches_only_its_rule(repo):
    rel = write(repo, "docs/a.md", "например: cd C:\\Users\\x\n")
    exc = [{"file": rel, "rule": "C8", "line": "например: cd C:\\Users\\x"}]
    assert cr.is_excepted(rel, 1, "C8", exc) is True
    assert cr.is_excepted(rel, 1, "C9", exc) is False


def test_exception_needs_whole_line(repo):
    rel = write(repo, "docs/a.md", "например: cd C:\\Users\\x and [y](missing.md)\n")
    exc = [{"file": rel, "rule": "C8", "line": "например: cd C:"}]
    assert cr.is_excepted(rel, 1, "C8", exc) is False


# Whole-repo gate ------------------------------------------------------------

def test_real_repository_passes():
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "check_repo.py")],
        capture_output=True, text=True, encoding="utf-8", cwd=REPO,
    )
    assert result.returncode == 0, result.stdout + result.stderr
