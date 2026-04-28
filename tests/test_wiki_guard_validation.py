from __future__ import annotations

import sys
from pathlib import Path

from wiki_guard_test_utils import write_page, write_required_root


def test_gather_issues_reports_clean_repo(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    page = """---
domain: shattered_sea
type: concept
source_count: 1
status: active
visibility: private
tags: [test]
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Links to [[other_page]].
"""
    other = page.replace("[[other_page]]", "No links")
    write_page(tmp_path / "wiki/concepts/root_page.md", page)
    write_page(tmp_path / "wiki/concepts/other_page.md", other)

    issues = wiki_guard.gather_issues(tmp_path)

    assert issues == []


def test_gather_issues_flags_missing_root_file(tmp_path: Path, wiki_guard) -> None:
    (tmp_path / "index.md").write_text("ok\n", encoding="utf-8")
    (tmp_path / "hot.md").write_text("ok\n", encoding="utf-8")
    write_page(tmp_path / "wiki/concepts/example_page.md", "---\ninvalid: true\n---\n")

    issues = wiki_guard.gather_issues(tmp_path)

    assert any(i.level == "error" and i.path == "log.md" for i in issues)


def test_regression_invalid_yaml_frontmatter_does_not_crash(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    write_page(
        tmp_path / "wiki/concepts/bad_yaml.md",
        "---\ntype: [bad\n---\n\n## Overview\n",
    )

    issues = wiki_guard.gather_issues(tmp_path)

    assert any(
        i.path == "wiki/concepts/bad_yaml.md"
        and i.level == "warn"
        and "missing or invalid YAML frontmatter" in i.message
        for i in issues
    )


def test_gather_issues_flags_dead_wikilinks(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    write_page(
        tmp_path / "wiki/concepts/page_with_link.md",
        """---
domain: shattered_sea
type: concept
source_count: 1
status: active
visibility: private
tags: [test]
related: []
created: 2026-04-26
updated: 2026-04-26

---

## Overview

Broken reference [[missing_page]].
""",
    )

    issues = wiki_guard.gather_issues(tmp_path)

    assert any("dead wikilink: [[missing_page]]" in i.message for i in issues)


def test_parse_frontmatter_invalid_shapes(wiki_guard) -> None:
    assert wiki_guard.parse_frontmatter("no frontmatter") is None
    assert wiki_guard.parse_frontmatter("---\nname: a") is None
    assert wiki_guard.parse_frontmatter("---\n- item\n---\n") is None


def test_parse_frontmatter_valid_dict(wiki_guard) -> None:
    data = wiki_guard.parse_frontmatter("---\nname: ok\n---\n\nbody\n")
    assert data == {"name": "ok"}


def test_gather_issues_missing_wiki_dir_is_error(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)

    issues = wiki_guard.gather_issues(tmp_path)

    assert any(i.level == "error" and i.path == "wiki" for i in issues)


def test_gather_issues_flags_filename_snake_case(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    write_page(
        tmp_path / "wiki/concepts/NotSnake.md",
        """---
domain: shattered_sea
type: concept
source_count: 1
status: active
visibility: private
tags: [test]
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
""",
    )

    issues = wiki_guard.gather_issues(tmp_path)

    assert any(i.path == "wiki/concepts/NotSnake.md" and "snake_case" in i.message for i in issues)


def test_print_report_formats_output(capsys, wiki_guard) -> None:
    wiki_guard.print_report([])
    out = capsys.readouterr().out
    assert "no issues found" in out

    wiki_guard.print_report([wiki_guard.Issue("warn", "wiki/x.md", "oops")])
    out = capsys.readouterr().out
    assert "found 1 issue" in out
    assert "[warn] wiki/x.md: oops" in out


def test_main_returns_strict_failure_on_warn(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    write_required_root(tmp_path)
    write_page(tmp_path / "wiki/concepts/a.md", "---\ninvalid: true\n---\n")

    monkeypatch.setattr(
        sys,
        "argv",
        ["wiki_guard.py", "--repo-root", str(tmp_path), "--strict"],
    )

    code = wiki_guard.main()

    assert code == 1


def test_main_returns_success_without_strict_on_warn(
    tmp_path: Path, monkeypatch, wiki_guard
) -> None:
    write_required_root(tmp_path)
    write_page(tmp_path / "wiki/concepts/a.md", "---\ninvalid: true\n---\n")

    monkeypatch.setattr(
        sys,
        "argv",
        ["wiki_guard.py", "--repo-root", str(tmp_path)],
    )

    code = wiki_guard.main()

    assert code == 0


def test_main_returns_error_when_wiki_missing(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    write_required_root(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["wiki_guard.py", "--repo-root", str(tmp_path)],
    )

    code = wiki_guard.main()

    assert code == 1
