from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from wiki_guard_test_utils import write_page


def _write_env(repo_root: Path, content: str) -> None:
    (repo_root / ".env").write_text(content, encoding="utf-8")


def test_gather_synthesis_candidates_filters_covered_pairs(tmp_path: Path, wiki_guard) -> None:
    _write_env(tmp_path, "OBSIDIAN_VAULT_PATH=.\n")

    write_page(
        tmp_path / "wiki/entities/alpha.md",
        """---
category: entity
tags:
  - shared
summary: Alpha
status: active
---

## Related
[[beta]]
[[gamma]]
""",
    )
    write_page(
        tmp_path / "wiki/entities/delta.md",
        """---
category: entity
tags:
  - shared
summary: Delta
status: active
---

## Related
[[beta]]
[[gamma]]
""",
    )
    write_page(
        tmp_path / "wiki/concepts/theory.md",
        """---
category: concept
tags:
  - shared
summary: Theory
status: contradictory
---

## Related
[[beta]]
[[gamma]]
""",
    )

    write_page(
        tmp_path / "wiki/entities/beta.md",
        """---
category: entity
tags:
  - shared
summary: Beta
status: active
---

## Overview
""",
    )
    write_page(
        tmp_path / "wiki/concepts/gamma.md",
        """---
category: concept
tags:
  - shared
summary: Gamma
status: active
---

## Overview
""",
    )

    write_page(
        tmp_path / "wiki/synthesis/alpha_x_beta.md",
        """---
category: synthesis
tags: [shared]
summary: Existing synthesis
---

## Related
[[alpha]]
[[beta]]
""",
    )
    (tmp_path / "_insights.md").write_text("[[gamma]]\n", encoding="utf-8")

    report = wiki_guard.gather_synthesis_candidates(
        tmp_path,
        top_pair_limit=30,
        top_candidates=5,
        skipped_limit=10,
    )

    assert report.covered_pairs >= 1
    assert len(report.top_candidates) >= 1

    top = report.top_candidates[0]
    assert {top.left_slug, top.right_slug} == {"beta", "gamma"}
    assert top.cross_domain is True
    assert top.hub_involved is True
    assert top.contradiction_signal is True


def test_gather_synthesis_candidates_topic_filter(tmp_path: Path, wiki_guard) -> None:
    _write_env(tmp_path, "OBSIDIAN_VAULT_PATH=.\n")

    write_page(
        tmp_path / "wiki/entities/ship.md",
        """---
category: entity
tags: [naval]
summary: Ship
status: active
---
[[storm]]
""",
    )
    write_page(
        tmp_path / "wiki/entities/captain.md",
        """---
category: entity
tags: [naval]
summary: Captain
status: active
---
[[storm]]
""",
    )
    write_page(
        tmp_path / "wiki/concepts/storm.md",
        """---
category: concept
tags: [weather]
summary: Storm
status: active
---
""",
    )

    report = wiki_guard.gather_synthesis_candidates(
        tmp_path,
        top_pair_limit=30,
        top_candidates=5,
        skipped_limit=10,
        topic_filter="weather",
    )

    assert all("storm" in {item.left_slug, item.right_slug} for item in report.top_candidates)


def test_main_synthesize_report_json_output(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    _write_env(tmp_path, "OBSIDIAN_VAULT_PATH=.\n")

    write_page(
        tmp_path / "wiki/entities/a.md",
        """---
category: entity
tags: [one]
summary: A
status: active
---
[[b]]
[[c]]
""",
    )
    write_page(
        tmp_path / "wiki/entities/b.md",
        """---
category: entity
tags: [one]
summary: B
status: active
---
""",
    )
    write_page(
        tmp_path / "wiki/entities/c.md",
        """---
category: entity
tags: [one]
summary: C
status: active
---
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--synthesize-report",
            "--synthesize-format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["overview"]["candidate_pairs_scanned"] >= 1
    assert len(payload["top_candidates"]) >= 1


def test_synthesis_helpers_and_render_paths(tmp_path: Path, capsys, wiki_guard) -> None:
    import wiki_guard_lib.synthesis_audit as synthesis_audit

    assert synthesis_audit._load_env_map(tmp_path) == {}
    _write_env(tmp_path, "OBSIDIAN_VAULT_PATH=.\nFOO=bar\n")
    assert synthesis_audit._load_env_map(tmp_path)["FOO"] == "bar"
    assert synthesis_audit._resolve_vault_root(tmp_path) == tmp_path

    write_page(tmp_path / "wiki/entities/node.md", "[[other]]\n")
    write_page(tmp_path / "wiki/entities/other.md", "[[node]]\n")
    write_page(tmp_path / "raw/source.md", "[[node]]\n")
    write_page(tmp_path / "_archives/old.md", "[[node]]\n")
    (tmp_path / "index.md").write_text("# index\n", encoding="utf-8")

    scanned = synthesis_audit._iter_markdown_pages(tmp_path)
    scanned_paths = {item.relative_to(tmp_path).as_posix() for item in scanned}
    assert "wiki/entities/node.md" in scanned_paths
    assert "index.md" not in scanned_paths
    assert "raw/source.md" not in scanned_paths
    assert "_archives/old.md" not in scanned_paths

    assert synthesis_audit._hub_slugs(tmp_path) == set()
    (tmp_path / "_insights.md").write_text("[[node]]\n", encoding="utf-8")
    assert synthesis_audit._hub_slugs(tmp_path) == {"node"}

    pages = synthesis_audit._collect_pages(tmp_path)
    target_slugs = {slug for slug, page in pages.items() if not page.is_synthesis}
    write_page(
        tmp_path / "wiki/synthesis/node_x_other.md",
        """---
category: synthesis
---
[[node]]
[[other]]
""",
    )
    pages = synthesis_audit._collect_pages(tmp_path)
    covered = synthesis_audit._covered_pairs(pages, target_slugs)
    assert ("node", "other") in covered

    candidate = wiki_guard.SynthesisCandidate(
        left_slug="node",
        right_slug="other",
        title="node × other",
        score=1,
        cooccurrence_count=1,
        shared_by_pages=["wiki/entities/node.md"],
        cross_domain=False,
        shared_tags=[],
        hub_involved=False,
        contradiction_signal=False,
    )
    assert synthesis_audit._topic_match(candidate, pages, "") is True
    assert synthesis_audit._topic_match(candidate, pages, "missing-token") is False

    report = wiki_guard.SynthesisReport(
        pages_scanned=0,
        candidate_pairs_scanned=0,
        covered_pairs=0,
        topic_filter=None,
        top_candidates=[],
        skipped_candidates=[],
    )
    text = wiki_guard.render_synthesis_report_text(report)
    assert "top candidates" in text
    assert "- none" in text

    raw_json = wiki_guard.render_synthesis_report_json(report)
    payload = json.loads(raw_json)
    assert payload["overview"]["pages_scanned"] == 0

    wiki_guard.print_synthesis_report(report, "text")
    out_text = capsys.readouterr().out
    assert "wiki_guard synthesis report" in out_text

    wiki_guard.print_synthesis_report(report, "json")
    out_json = capsys.readouterr().out
    assert '"top_candidates": []' in out_json


def test_main_synthesize_report_cli_conflict_errors(
    tmp_path: Path, monkeypatch, wiki_guard
) -> None:
    _write_env(tmp_path, "OBSIDIAN_VAULT_PATH=.\n")
    write_page(
        tmp_path / "wiki/entities/a.md",
        """---
category: entity
tags: [one]
summary: A
status: active
---
[[b]]
[[c]]
""",
    )
    write_page(
        tmp_path / "wiki/entities/b.md",
        """---
category: entity
tags: [one]
summary: B
status: active
---
""",
    )
    write_page(
        tmp_path / "wiki/entities/c.md",
        """---
category: entity
tags: [one]
summary: C
status: active
---
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--synthesize-report",
            "--query-prep",
            "--query-question",
            "x",
        ],
    )
    with pytest.raises(SystemExit):
        wiki_guard.main()
