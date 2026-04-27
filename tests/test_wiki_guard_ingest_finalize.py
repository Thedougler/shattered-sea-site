from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from wiki_guard_test_utils import write_page


def _write_content_root(repo_root: Path) -> None:
    content_root = repo_root / "content"
    content_root.mkdir(parents=True, exist_ok=True)
    (content_root / "index.md").write_text(
        "\n".join(
            [
                "# Index",
                "",
                "| Entity | Summary | Sources | Status | Updated |",
                "| -------- | --------- | --------- | -------- | --------- |",
                "| [[storm_anchor]] | anchor in the maw | 1 | active | 2026-04-26 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_page(
        content_root / "hot.md",
        "\n".join(
            [
                "---",
                "title: Hot Cache",
                "updated: 2026-04-26",
                "---",
                "",
                "# Hot Cache",
                "",
                "## Recent Activity",
                "",
                "- [2026-04-26] INGEST `raw/old.md` — older activity.",
                "",
                "## Active Threads",
                "",
                "- Old thread",
                "",
                "## Key Takeaways",
                "",
                "- Old takeaway",
                "",
                "## Flagged Contradictions",
                "",
                "*None.*",
            ]
        )
        + "\n",
    )
    write_page(content_root / "log.md", "# Audit Log: shattered_sea\n\n---\n")


def test_main_ingest_finalize_updates_content_bookkeeping(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw/factions"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source_path = raw_dir / "Golden-Carvers.md"
    source_path.write_text("# Golden Carvers\n", encoding="utf-8")

    _write_content_root(tmp_path)
    write_page(
        tmp_path / "content/entities/golden_carvers.md",
        """---
domain: shattered_sea
type: entity
summary: A faction.
source_count: 1
status: draft
visibility: private
tags:
  - faction
related:
  - \"[[storm_anchor]]\"
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
created: 2026-04-27
updated: 2026-04-27
---

## Overview

Golden Carvers.
""",
    )
    write_page(
        tmp_path / "content/entities/storm_anchor.md",
        """---
domain: shattered_sea
type: concept
summary: Anchor in the maw.
source_count: 1
status: active
visibility: private
tags:
  - drowned_maw
related: []
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
created: 2026-04-26
updated: 2026-04-26
---

## Overview

Storm anchor.
""",
    )

    payload_path = tmp_path / ".claude/tmp/finalize.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(
        json.dumps(
            {
                "source_path": "raw/factions/Golden-Carvers.md",
                "source_type": "document",
                "content_hash": wiki_guard.compute_sha256(source_path),
                "pages_created": ["content/entities/golden_carvers.md"],
                "pages_updated": ["content/entities/storm_anchor.md"],
                "links_woven": 4,
                "contradictions": ["[[golden_carvers]] — founding date conflicts with prior source"],
                "log_details": [
                    "CREATED [[golden_carvers]] — salvage guild faction page",
                    "UPDATED [[storm_anchor]] — linked Golden Carvers involvement",
                ],
                "hot": {
                    "recent_activity": "Golden Carvers created and Storm Anchor updated.",
                    "active_threads": [
                        "- Golden Carvers now tied to salvage politics.",
                        "- Storm Anchor remains central to the drowned maw.",
                    ],
                    "key_takeaways": [
                        "- Golden Carvers connect faction politics to Maw salvage.",
                    ],
                    "flagged_contradictions": [
                        "- [[golden_carvers]] — founding date conflicts with prior source.",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-finalize",
            "--ingest-finalize-file",
            ".claude/tmp/finalize.json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out

    manifest = json.loads((tmp_path / ".manifest.json").read_text(encoding="utf-8"))
    log_text = (tmp_path / "content/log.md").read_text(encoding="utf-8")
    hot_text = (tmp_path / "content/hot.md").read_text(encoding="utf-8")

    assert code == 0
    assert manifest["sources"]["raw/factions/Golden-Carvers.md"]["pages_created"] == [
        "content/entities/golden_carvers.md"
    ]
    assert manifest["stats"]["total_sources_ingested"] == 1
    assert manifest["stats"]["total_pages"] == 2
    assert 'INGEST source="raw/factions/Golden-Carvers.md"' in log_text
    assert "CREATED [[golden_carvers]]" in log_text
    assert "Golden Carvers created and Storm Anchor updated." in hot_text
    assert "[[golden_carvers]] — founding date conflicts with prior source." in hot_text
    assert "ingest finalize updated .manifest.json, content/log.md, content/hot.md" in out
    assert "summary: source=raw/factions/Golden-Carvers.md created=1 updated=1 contradictions=1" in out


def test_main_ingest_finalize_requires_payload_file(tmp_path: Path, monkeypatch, wiki_guard) -> None:
    _write_content_root(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-finalize",
        ],
    )

    with pytest.raises(SystemExit):
        wiki_guard.main()