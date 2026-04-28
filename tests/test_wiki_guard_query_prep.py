from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from wiki_guard_test_utils import write_page, write_required_root


def test_gather_query_prep_ranks_primary_and_secondary(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[the_drowned_maw]] | Planar fissure in the sea | 1 | active | 2026-04-26 |
| [[leviathan]] | Creature crossing from elemental water | 1 | draft | 2026-04-26 |
| [[umberlee]] | Sea deity with claim over storms | 1 | draft | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/the_drowned_maw.md",
        """---
domain: shattered_sea
type: concept
summary: Planar fissure in the sea
source_count: 1
status: active
visibility: private
tags:
  - planar
  - maw
aliases:
  - Drowned Maw
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

The Drowned Maw is a planar rupture where currents destabilize.
It links to [[leviathan]].
""",
    )
    write_page(
        tmp_path / "wiki/entities/leviathan.md",
        """---
domain: shattered_sea
type: concept
summary: Creature crossing from elemental water
source_count: 1
status: draft
visibility: private
tags:
  - creature
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Leviathan emerged from a breach near the drowned maw.
""",
    )
    write_page(
        tmp_path / "wiki/entities/umberlee.md",
        """---
domain: shattered_sea
type: concept
summary: Sea deity with claim over storms
source_count: 1
status: draft
visibility: private
tags:
  - deity
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Umberlee is a sea deity.
""",
    )

    result = wiki_guard.gather_query_prep(
        tmp_path,
        question="What is the relationship between drowned maw and leviathan?",
        top_k=2,
    )

    assert result.query_type in {"factual", "synthesis"}
    assert len(result.primary) >= 1
    assert result.primary[0].slug in {"the_drowned_maw", "leviathan"}
    assert any(item.slug == "leviathan" for item in result.secondary + result.primary)


def test_gather_query_prep_public_filter_excludes_internal(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[public_page]] | Public summary | 1 | active | 2026-04-26 |
| [[internal_page]] | Internal summary | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/public_page.md",
        """---
domain: shattered_sea
type: concept
summary: Public summary
source_count: 1
status: active
visibility: public
tags:
  - lore
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Public context.
""",
    )
    write_page(
        tmp_path / "wiki/entities/internal_page.md",
        """---
domain: shattered_sea
type: concept
summary: Internal summary
source_count: 1
status: active
visibility: private
tags:
  - lore
  - visibility/internal
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Internal context.
""",
    )

    result = wiki_guard.gather_query_prep(
        tmp_path,
        question="Give me lore summary",
        top_k=3,
        public_only=True,
    )

    assert all(item.slug != "internal_page" for item in result.primary)
    assert result.excluded_internal_count == 1


def test_main_query_prep_json_output(tmp_path: Path, monkeypatch, capsys, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[the_drowned_maw]] | Planar fissure in the sea | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/the_drowned_maw.md",
        """---
domain: shattered_sea
type: concept
summary: Planar fissure in the sea
source_count: 1
status: active
visibility: private
tags:
  - planar
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

The Drowned Maw is dangerous.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
            "--query-question",
            "Drowned Maw",
            "--query-format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["question"] == "Drowned Maw"
    assert payload["primary"][0]["slug"] == "the_drowned_maw"


def test_main_query_agent_writes_default_json_file(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "content").mkdir()
    (tmp_path / "content/index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[the_drowned_maw]] | Planar fissure in the sea | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "content/entities/the_drowned_maw.md",
        """---
type: concept
summary: Planar fissure in the sea
source_count: 1
status: active
updated: 2026-04-26
tags:
  - planar
---

## Overview
The Drowned Maw is dangerous.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-agent",
            "--query-question",
            "Drowned Maw",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / ".claude/tmp/query_prep.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert code == 0
    assert report_path.exists()
    assert payload["question"] == "Drowned Maw"
    assert payload["primary"][0]["slug"] == "the_drowned_maw"
    assert "query prep written to .claude/tmp/query_prep.json" in out
    assert "summary: type=" in out


def test_main_query_prep_requires_question(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    write_required_root(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
        ],
    )

    with pytest.raises(SystemExit):
        wiki_guard.main()


def test_query_prep_render_and_print_paths(tmp_path: Path, capsys, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[sentinels_of_the_eyrie]] | Monastic order | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/sentinels_of_the_eyrie.md",
        """---
domain: shattered_sea
type: concept
summary: Monastic order
source_count: 1
status: active
visibility: private
tags:
  - faction
aliases:
  - Sentinels
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Sentinels monitor the Drowned Maw.
""",
    )

    result = wiki_guard.gather_query_prep(
        tmp_path,
        question="Summarize sentinels and maw",
        top_k=1,
        fast_mode=False,
        snippet_context=1,
        max_snippets=1,
    )

    text_report = wiki_guard.render_query_prep_text(result)
    assert "query prep" in text_report
    assert "primary pages" in text_report

    json_report = wiki_guard.render_query_prep_json(result)
    parsed = json.loads(json_report)
    assert parsed["query_type"] == "synthesis"

    wiki_guard.print_query_prep(result, "text")
    text_out = capsys.readouterr().out
    assert "suggested read order" in text_out

    wiki_guard.print_query_prep(result, "json")
    json_out = capsys.readouterr().out
    assert '"primary"' in json_out


def test_gather_query_prep_fast_mode_and_empty_tokens(tmp_path: Path, wiki_guard) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[alpha_entry]] | Alpha summary | 1 | draft | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/alpha_entry.md",
        """---
domain: shattered_sea
type: concept
summary: Alpha summary
source_count: 1
status: draft
visibility: private
tags: []
aliases: []
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Alpha body.
""",
    )

    result = wiki_guard.gather_query_prep(
        tmp_path,
        question="the and of",
        top_k=1,
        fast_mode=True,
        snippet_context=0,
    )

    assert result.mode == "index_only"
    assert result.primary == []


def test_query_prep_internal_helpers_cover_branchy_inputs(wiki_guard) -> None:
    query_prep = sys.modules["wiki_guard_lib.query_prep"]

    assert query_prep._normalize_list("not-a-list") == []
    assert query_prep._normalize_list([" alpha ", "", 3, "beta"]) == ["alpha", "beta"]

    assert query_prep._detect_query_type("compare alpha versus beta") == "comparative"
    assert query_prep._detect_query_type("find a conflict in sources") == "contradiction_scan"
    assert query_prep._detect_query_type("wiki health status") == "meta"
    assert query_prep._detect_query_type("plain factual question") == "factual"

    assert query_prep._extract_snippets("alpha\nbeta", [], context=1, max_snippets=1) == []
    assert query_prep._extract_snippets("alpha\nbeta", ["gamma"], context=1, max_snippets=1) == []


def test_build_candidate_handles_malformed_info_and_mixed_links(wiki_guard) -> None:
    query_prep = sys.modules["wiki_guard_lib.query_prep"]

    malformed_candidate = query_prep._build_candidate(
        slug="alpha_entry",
        info={
            "frontmatter": "bad-data",
            "text": 42,
            "rel_path": 99,
            "links": "not-a-list",
        },
        index_summary="Alpha summary",
        question_tokens=["alpha"],
        fast_mode=False,
        snippet_context=1,
        max_snippets=1,
    )

    assert malformed_candidate is not None
    assert malformed_candidate.summary == "Alpha summary"
    assert malformed_candidate.status == "unknown"
    assert malformed_candidate.visibility == "unknown"
    assert malformed_candidate.rel_path == ""
    assert malformed_candidate.outbound_links == []
    assert malformed_candidate.snippets == []

    mixed_links_candidate = query_prep._build_candidate(
        slug="beta_entry",
        info={
            "frontmatter": {
                "summary": "Beta summary",
                "aliases": ["Beta Alias"],
                "tags": ["sea-lore"],
                "status": " active ",
                "visibility": " public ",
            },
            "text": "Beta summary appears here.",
            "rel_path": "wiki/entities/beta_entry.md",
            "links": ["gamma_entry", 7, "delta_entry"],
        },
        index_summary="",
        question_tokens=["beta", "alias", "sea", "lore"],
        fast_mode=True,
        snippet_context=1,
        max_snippets=1,
    )

    assert mixed_links_candidate is not None
    assert mixed_links_candidate.status == "active"
    assert mixed_links_candidate.visibility == "public"
    assert mixed_links_candidate.source_count == 0
    assert mixed_links_candidate.source_refs == []
    assert mixed_links_candidate.outbound_links == ["gamma_entry", "delta_entry"]
    assert mixed_links_candidate.snippets == []


def test_gather_query_prep_secondary_filtered_index_only_and_text_output(
    tmp_path: Path, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[alpha_page]] | Alpha summary | 1 | active | 2026-04-26 |
| [[beta_page]] | Alpha ally | 1 | draft | 2026-04-26 |
| [[internal_page]] | Alpha internal | 1 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/alpha_page.md",
        """---
domain: shattered_sea
type: concept
summary: Alpha summary
source_count: 1
status: active
visibility: private
tags:
  - alpha
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Alpha references [[beta_page]].
""",
    )
    write_page(
        tmp_path / "wiki/entities/beta_page.md",
        """---
domain: shattered_sea
type: concept
summary: Alpha ally
source_count: 1
status: draft
visibility: public
tags:
  - ally
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Beta supports Alpha.
""",
    )
    write_page(
        tmp_path / "wiki/entities/internal_page.md",
        """---
domain: shattered_sea
type: concept
summary: Alpha internal
source_count: 1
status: active
visibility: private
tags:
  - alpha
  - visibility/internal
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Internal Alpha note.
""",
    )

    result = wiki_guard.gather_query_prep(
        tmp_path,
        question="Alpha",
        top_k=1,
        fast_mode=False,
    )

    assert [item.slug for item in result.primary] == ["alpha_page"]
    assert [item.slug for item in result.secondary] == ["beta_page"]

    filtered_result = wiki_guard.gather_query_prep(
        tmp_path,
        question="Alpha",
        top_k=1,
        fast_mode=True,
        public_only=True,
    )

    assert filtered_result.mode == "filtered_index_only"
    assert filtered_result.excluded_internal_count == 1

    report = wiki_guard.QueryPrepResult(
        question="Alpha",
        query_type="factual",
        mode="normal",
        filtered=False,
        top_k=1,
        primary=[
            wiki_guard.QueryPrepCandidate(
                slug="alpha_page",
                rel_path="wiki/entities/alpha_page.md",
                score=10,
                match_reasons=[],
                summary="",
                source_count=0,
                source_refs=[],
                status="active",
                visibility="private",
                tags=[],
                aliases=[],
                outbound_links=[],
                snippets=[],
            )
        ],
        secondary=[
            wiki_guard.QueryPrepCandidate(
                slug="beta_page",
                rel_path="wiki/entities/beta_page.md",
                score=4,
                match_reasons=["summary:alpha"],
                summary="Beta summary",
                source_count=0,
                source_refs=[],
                status="draft",
                visibility="public",
                tags=[],
                aliases=[],
                outbound_links=[],
                snippets=[],
            )
        ],
        excluded_internal_count=0,
    )

    text_report = wiki_guard.render_query_prep_text(report)
    assert "via=none" in text_report
    assert "- [[beta_page]] score=4" in text_report
    assert "  summary:" not in text_report


def test_gather_query_prep_extracts_source_metadata_and_skips_frontmatter_snippets(
    tmp_path: Path, wiki_guard
) -> None:
    write_required_root(tmp_path)
    (tmp_path / "index.md").write_text(
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[storm_anchor]] | Anchor in the drowned maw | 2 | active | 2026-04-26 |

## Notes
""",
        encoding="utf-8",
    )
    write_page(
        tmp_path / "wiki/entities/storm_anchor.md",
        """---
domain: shattered_sea
type: concept
summary: Anchor in the drowned maw
source_count: "2"
status: active
visibility: private
tags:
  - drowned_maw
sources:
  - "[[Campaign-Timeline]]"
  - "[[The-Shattered-Sea]]"
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

This anchor stabilizes the drowned maw currents.
""",
    )

    result = wiki_guard.gather_query_prep(
        tmp_path,
        question="What anchors the drowned maw?",
        top_k=1,
        fast_mode=False,
        snippet_context=1,
        max_snippets=1,
    )

    assert result.primary
    candidate = result.primary[0]
    assert candidate.source_count == 2
    assert candidate.source_refs == ["[[Campaign-Timeline]]", "[[The-Shattered-Sea]]"]
    assert all("domain: shattered_sea" not in snippet for snippet in candidate.snippets)


def test_main_query_prep_with_query_log_appends_line(
    tmp_path: Path, monkeypatch, wiki_guard
) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir(parents=True, exist_ok=True)
    write_page(
        content_root / "index.md",
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[storm_anchor]] | Anchor in the drowned maw | 2 | active | 2026-04-26 |

## Notes
""",
    )
    write_page(content_root / "hot.md", "hot\n")
    write_page(content_root / "log.md", "")
    write_page(
        content_root / "entities/storm_anchor.md",
        """---
domain: shattered_sea
type: concept
summary: Anchor in the drowned maw
source_count: 2
status: active
visibility: private
tags:
  - drowned_maw
related: []
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Storm anchor note.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
            "--query-question",
            "Quick answer: storm anchor",
            "--query-fast",
            "--query-log",
            "--query-result-pages",
            "2",
            "--query-escalated",
        ],
    )

    code = wiki_guard.main()
    log_text = (content_root / "log.md").read_text(encoding="utf-8")

    assert code == 0
    assert " QUERY " in log_text
    assert 'query="Quick answer: storm anchor"' in log_text


def test_main_query_prep_qmd_file_errors(tmp_path: Path, monkeypatch, capsys, wiki_guard) -> None:
    write_required_root(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
            "--query-question",
            "Maw",
            "--query-merge-qmd",
            "missing.json",
        ],
    )
    assert wiki_guard.main() == 1
    assert "--query-merge-qmd file not found" in capsys.readouterr().err

    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{oops", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
            "--query-question",
            "Maw",
            "--query-merge-qmd",
            str(bad_json),
        ],
    )
    assert wiki_guard.main() == 1
    assert "failed to read --query-merge-qmd file" in capsys.readouterr().err

    not_array = tmp_path / "not-array.json"
    not_array.write_text('{"rel_path":"wiki/entities/x.md"}', encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
            "--query-question",
            "Maw",
            "--query-merge-qmd",
            str(not_array),
        ],
    )
    assert wiki_guard.main() == 1
    assert "must contain a JSON array" in capsys.readouterr().err


def test_main_query_prep_text_output_and_filed_error(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir(parents=True, exist_ok=True)
    write_page(
        content_root / "index.md",
        """# Index: shattered_sea

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| [[storm_anchor]] | Anchor in the drowned maw | 1 | active | 2026-04-26 |
""",
    )
    write_page(
        content_root / "entities/storm_anchor.md",
        """---
summary: Anchor in the drowned maw
status: active
visibility: private
tags:
  - drowned_maw
---

Storm anchor details.
""",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-prep",
            "--query-question",
            "What is storm anchor?",
            "--query-format",
            "text",
            "--query-output-file",
            ".claude/tmp/query_report.txt",
        ],
    )
    assert wiki_guard.main() == 0
    report_path = tmp_path / ".claude/tmp/query_report.txt"
    assert report_path.exists()
    assert "query prep" in report_path.read_text(encoding="utf-8")

    empty_repo = tmp_path / "empty"
    empty_repo.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(empty_repo),
            "--query-filed",
            "--query-filed-page",
            "content/synthesis/topic.md",
            "--query-filed-from-query",
            "Topic",
        ],
    )
    assert wiki_guard.main() == 1
    assert "could not detect knowledge layout" in capsys.readouterr().err


def test_main_query_log_requires_query_prep(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    write_required_root(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--query-log",
        ],
    )

    with pytest.raises(SystemExit):
        wiki_guard.main()
