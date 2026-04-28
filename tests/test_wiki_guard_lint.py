from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest
from wiki_guard_test_utils import write_page, write_required_root


def test_gather_lint_results_detects_index_wiki_ghost(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[known_page]] | known | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/known_page.md",
        """---
domain: shattered_sea
type: entity
summary: Known
source_count: 1
status: active
visibility: private
tags: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
Known page.
""",
    )
    write_page(
        tmp_path / "wiki/entities/missing_from_index.md",
        """---
domain: shattered_sea
type: entity
summary: Missing from index
source_count: 1
status: draft
visibility: private
tags: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
Unindexed page.
""",
    )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))

    assert "missing_from_index" in results.index.wiki_ghosts


def test_apply_safe_lint_fixes_adds_only_index_rows(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/new_entity.md",
        """---
domain: shattered_sea
type: entity
summary: New entity summary
source_count: 2
status: active
visibility: private
tags: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
Entity body.
""",
    )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))
    applied = wiki_guard.apply_safe_lint_fixes(tmp_path, results)

    assert applied["index_entries_added"] == 1
    updated_index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "| [[new_entity]] | New entity summary | 2 | active | 2026-04-26 |" in updated_index


def test_main_lint_safe_fix_requires_lint_report(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["wiki_guard.py", "--repo-root", str(tmp_path), "--lint-safe-fix"],
    )

    with pytest.raises(SystemExit):
        wiki_guard.main()


def test_main_lint_fail_on_manual_returns_non_zero(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/lone_page.md",
        """---
domain: shattered_sea
type: entity
summary: Lone page
source_count: 1
status: active
visibility: private
tags: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
No inbound links.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--lint-report",
            "--lint-fail-on-manual",
        ],
    )

    code = wiki_guard.main()

    assert code == 3


def test_main_lint_report_json_contains_manual_and_safe_sections(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/manual_page.md",
        """---
domain: shattered_sea
type: entity
summary: Manual page
source_count: 1
status: active
visibility: private
tags: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
No inbound links.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--lint-report",
            "--lint-format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / ".claude/tmp/lint_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert code == 0
    assert report_path.exists()
    assert "lint report written to .claude/tmp/lint_report.json" in out
    assert "summary: critical=" in out
    assert "manual_required" in payload
    assert "safe_auto_fixable" in payload
    assert payload["safe_auto_fixable"]["index_wiki_ghosts"] == ["manual_page"]


def test_main_lint_agent_applies_agent_defaults(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "content").mkdir()
    (tmp_path / "content/index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[known_page]] | known | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "content/entities/known_page.md",
        """---
type: entity
summary: Known
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
Known page.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--lint-agent",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / ".claude/tmp/lint_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert code == 0
    assert report_path.exists()
    assert payload["gaps_meta"]["max_pages_per_gap"] == 3
    assert payload["gaps_meta"]["returned"] <= 10
    assert "lint report written to .claude/tmp/lint_report.json" in out


def test_lint_helpers_basics(wiki_guard) -> None:
    assert wiki_guard.parse_iso_date(None) is None
    assert wiki_guard.parse_iso_date("2026-13-40") is None
    assert str(wiki_guard.parse_iso_date("2026-04-26")) == "2026-04-26"

    assert wiki_guard.strip_frontmatter("body\n") == "body\n"
    assert wiki_guard.strip_frontmatter("---\na: b\n---\n\nBody\n") == "\nBody\n"

    assert wiki_guard.levenshtein_distance("abc", "abc") == 0
    assert wiki_guard.levenshtein_distance("abc", "axc") == 1


def test_classify_dead_link_typo_and_stub(wiki_guard) -> None:
    kind, likely = wiki_guard.classify_dead_link("th_shattered_sea", {"the_shattered_sea"})
    assert kind == "typo_likely"
    assert likely == "the_shattered_sea"

    kind, likely = wiki_guard.classify_dead_link("totally_new", {"the_shattered_sea"})
    assert kind == "stub_worthy"
    assert likely is None


def test_gather_lint_results_excludes_templates_from_inventory(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "content").mkdir()
    (tmp_path / "content/index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[real_page]] | real | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "content/entities/real_page.md",
        """---
type: entity
summary: Real page
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
Links to [[real_page]].
""",
    )
    write_page(
        tmp_path / "content/templates/npc_universal_profile.md",
        """---
type: entity
summary: Template
source_count: 1
status: active
updated: 2026-04-26
---

## Connections
- [[FACTION_NAME]]
""",
    )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))

    assert results.pages_audited == 1
    assert results.dead_links == []
    assert results.index.wiki_ghosts == []


def test_gather_lint_results_normalizes_escaped_wikilink_alias(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "content").mkdir()
    (tmp_path / "content/index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[source_page]] | source | 1 | active | 2026-04-26 |
| [[the_antheri_ruins]] | ruins | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "content/entities/source_page.md",
        r"""---
type: entity
summary: Source page
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
Points at [[the_antheri_ruins\|the Shelfworks]].
""",
    )
    write_page(
        tmp_path / "content/entities/the_antheri_ruins.md",
        """---
type: entity
summary: Ruins
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
Ruins.
""",
    )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))

    assert results.dead_links == []
    assert [orphan.slug for orphan in results.orphans] == ["source_page"]


def test_gather_lint_results_filters_gap_terms_covered_by_existing_slug_tokens(
    tmp_path: Path, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "content").mkdir()
    (tmp_path / "content/index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[the_drowned_maw]] | maw | 1 | active | 2026-04-26 |
| [[the_shattered_sea]] | sea | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "content/entities/the_drowned_maw.md",
        """---
type: entity
summary: Maw
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
The Maw.
""",
    )
    write_page(
        tmp_path / "content/entities/the_shattered_sea.md",
        """---
type: entity
summary: Sea
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
The sea.
""",
    )
    for index in range(3):
        write_page(
            tmp_path / f"content/entities/page_{index}.md",
            f"""---
type: entity
summary: Page {index}
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
The Maw threatens the Scatter.
""",
        )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))
    gap_terms = {gap.term for gap in results.gaps}

    assert "Maw" not in gap_terms
    assert "The Maw" not in gap_terms


def test_collect_ingestion_dates_and_suggest_related_pages(wiki_guard) -> None:
    log_text = """
    - [2026-04-20T00:00:00Z] INGEST source=\"raw/a.md\"
    - [2026-04-21T00:00:00Z] OTHER
    - [2026-04-22T00:00:00Z] INGEST source=\"raw/b.md\"
    """
    dates = wiki_guard.collect_ingestion_dates(log_text)
    assert [str(x) for x in dates] == ["2026-04-20", "2026-04-22"]

    links = ["a", "b", "a", "current", "c"]
    suggested = wiki_guard.suggest_related_pages(links, "current", limit=2)
    assert suggested == ["a", "b"]


def test_gather_lint_results_detects_stale_contradiction_and_gaps(
    tmp_path: Path, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[alpha]] | Alpha summary | 1 | active | 2026-01-01 |
| [[beta]] | Beta summary | 1 | active | 2026-01-01 |
| [[index_only]] | TODO stale | 1 | draft | 2026-01-01 |

## Notes
""",
        encoding="utf-8",
    )
    (tmp_path / "log.md").write_text(
        """# Audit
- [2026-02-01T00:00:00Z] INGEST source=\"raw/a.md\"
- [2026-03-01T00:00:00Z] INGEST source=\"raw/b.md\"
- [2026-04-01T00:00:00Z] INGEST source=\"raw/c.md\"
- [2026-04-20T00:00:00Z] INGEST source=\"raw/d.md\"
""",
        encoding="utf-8",
    )

    write_page(
        tmp_path / "wiki/entities/alpha.md",
        """---
domain: shattered_sea
type: entity
summary: Alpha summary
source_count: 1
status: active
visibility: private
tags: []
related: []
created: 2026-01-01
updated: 2026-01-01
---

## Overview
Mentions Azure Crown and Coral Gate.
Links [[beta]] and [[gamma_typo]].
""",
    )
    write_page(
        tmp_path / "wiki/entities/beta.md",
        """---
domain: shattered_sea
type: entity
summary: Beta summary
source_count: 1
status: draft
visibility: private
tags: []
related: []
created: 2026-01-01
updated: 2026-01-01
---

## Overview
Mentions Azure Crown and Coral Gate.
Links [[alpha]].
""",
    )
    write_page(
        tmp_path / "wiki/entities/contradiction_page.md",
        """---
domain: shattered_sea
type: entity
summary: Contradiction summary
source_count: 1
status: contradictory
visibility: private
tags: []
related: []
created: 2026-01-01
updated: 2026-01-01
---

## Contradictions

- Source A says east, Source B says west.

## Overview
Mentions Azure Crown and Coral Gate.
""",
    )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))

    assert "index_only" in results.index.index_ghosts
    assert "contradiction_page" in results.index.wiki_ghosts
    assert "alpha" in [s.slug for s in results.stale]
    assert "beta" in [s.slug for s in results.stale]
    assert any(s.reason == "draft_aged" and s.slug == "beta" for s in results.stale)
    assert len(results.contradictions) == 1
    assert results.contradictions[0].slug == "contradiction_page"
    assert results.contradictions[0].open_days == 115
    assert any(item.target == "gamma_typo" for item in results.dead_links)
    assert len(results.gaps) >= 1


def test_render_lint_report_text_and_json_category_filters(wiki_guard) -> None:
    results = wiki_guard.LintResults(
        pages_audited=2,
        index_entries=1,
        ingestion_events=4,
        orphans=[wiki_guard.OrphanFinding("alpha", 0, ["beta"])],
        dead_links=[
            wiki_guard.DeadLinkFinding(
                "gamma",
                ["alpha"],
                1,
                "stub_worthy",
                None,
            )
        ],
        index=wiki_guard.IndexAuditFinding(["ghost_idx"], ["ghost_wiki"], ["alpha"]),
        stale=[wiki_guard.StaleFinding("alpha", "2026-01-01", 1, 3, "single_source")],
        contradictions=[
            wiki_guard.ContradictionFinding("alpha", "2026-01-01", 10, "Conflict line")
        ],
        gaps=[wiki_guard.EntityGapFinding("Azure Crown", 3, ["alpha", "beta", "gamma"], "low")],
    )

    text = wiki_guard.render_lint_report_text(results, "index")
    assert "Index Gaps" in text
    assert "Orphan Pages" not in text
    assert "Auto-fix boundary" in text

    raw_json = wiki_guard.render_lint_report_json(results, "dead_links")
    payload = json.loads(raw_json)
    assert "dead_links" in payload
    assert "index" not in payload
    assert payload["manual_required"]["orphans"] == ["alpha"]

    gaps_json = wiki_guard.render_lint_report_json(
        results,
        "gaps",
        max_gaps=1,
        max_gap_pages=2,
    )
    gaps_payload = json.loads(gaps_json)
    assert len(gaps_payload["gaps"]) == 1
    assert len(gaps_payload["gaps"][0]["pages"]) == 2
    assert gaps_payload["gaps_meta"]["truncated"] is False


def test_lint_report_output_file_writes_full_report(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/manual_page.md",
        """---
domain: shattered_sea
type: entity
summary: Manual page
source_count: 1
status: active
visibility: private
tags: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview
No inbound links.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--lint-report",
            "--lint-format",
            "json",
            "--lint-output-file",
            "tmp/lint-report.json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / "tmp/lint-report.json"

    assert code == 0
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["pages_audited"] == 1
    assert "lint report written to tmp/lint-report.json" in out


def test_entity_gap_detection_filters_noise_terms(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[alpha]] | Alpha summary | 1 | active | 2026-04-26 |
| [[beta]] | Beta summary | 1 | active | 2026-04-26 |
| [[gamma]] | Gamma summary | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    for slug in ("alpha", "beta", "gamma"):
        write_page(
            tmp_path / f"wiki/entities/{slug}.md",
            """---
summary: Test
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
Campaign Timeline Day Sea Shattered.
Azure Crown appears in every page.
""",
        )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))
    terms = {item.term for item in results.gaps}

    assert "Azure Crown" in terms
    assert "Campaign" not in terms
    assert "Timeline" not in terms
    assert "Day" not in terms
    assert "Sea" not in terms
    assert "Shattered" not in terms


def test_update_index_with_wiki_ghosts_is_idempotent(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|

## Notes
""",
        encoding="utf-8",
    )
    pages = {
        "ghost": {
            "frontmatter": {
                "summary": "Has | pipe",
                "source_count": 1,
                "status": "active",
                "updated": "bad-date",
            }
        }
    }

    added_first = wiki_guard.update_index_with_wiki_ghosts(
        tmp_path,
        ["ghost"],
        pages,
        today=date(2026, 4, 26),
    )
    added_second = wiki_guard.update_index_with_wiki_ghosts(
        tmp_path,
        ["ghost"],
        pages,
        today=date(2026, 4, 26),
    )

    assert added_first == 1
    assert added_second == 0
    index_text = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "| [[ghost]] | Has / pipe | 1 | active | 2026-04-26 |" in index_text


def test_gather_lint_results_supports_content_layout(tmp_path: Path, wiki_guard) -> None:
    write_page(
        tmp_path / "content/index.md",
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[known_page]] | Known summary | 1 | active | 2026-04-26 |

## Notes
""",
    )
    write_page(tmp_path / "content/log.md", "# Log\n")
    write_page(
        tmp_path / "content/entities/known_page.md",
        """---
summary: Known summary
source_count: 1
status: active
updated: 2026-04-26
---

## Overview
Linked nowhere.
""",
    )

    results = wiki_guard.gather_lint_results(tmp_path, today=date(2026, 4, 26))

    assert results.pages_audited == 1
    assert results.index_entries == 1
    assert results.orphans[0].slug == "known_page"
