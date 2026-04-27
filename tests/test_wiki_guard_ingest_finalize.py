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


def test_main_ingest_finalize_skips_idempotent_rerun(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw/factions"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source_path = raw_dir / "Golden-Carvers.md"
    source_path.write_text("# Golden Carvers\n", encoding="utf-8")

    _write_content_root(tmp_path)

    payload = {
        "source_path": "raw/factions/Golden-Carvers.md",
        "source_type": "document",
        "content_hash": wiki_guard.compute_sha256(source_path),
        "pages_created": ["content/entities/golden_carvers.md"],
        "pages_updated": ["content/entities/storm_anchor.md"],
        "links_woven": 2,
        "contradictions": [],
        "log_details": [
            "CREATED [[golden_carvers]] — salvage guild faction page",
        ],
        "hot": {
            "recent_activity": "Golden Carvers created.",
            "active_threads": ["- Golden Carvers need follow-up."],
            "key_takeaways": ["- Golden Carvers now exist."],
            "flagged_contradictions": [],
        },
    }

    payload_path = tmp_path / ".claude/tmp/finalize.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

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
    assert wiki_guard.main() == 0
    first_log = (tmp_path / "content/log.md").read_text(encoding="utf-8")

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
    second_log = (tmp_path / "content/log.md").read_text(encoding="utf-8")

    assert code == 0
    assert first_log == second_log
    assert "summary: source=raw/factions/Golden-Carvers.md created=1 updated=1 contradictions=0 skipped=1" in out


def test_main_ingest_finalize_batch_updates_multiple_sources(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw/factions"
    raw_dir.mkdir(parents=True, exist_ok=True)
    first_source = raw_dir / "Golden-Carvers.md"
    second_source = raw_dir / "Storm-Cult.md"
    first_source.write_text("# Golden Carvers\n", encoding="utf-8")
    second_source.write_text("# Storm Cult\n", encoding="utf-8")

    _write_content_root(tmp_path)

    payload_path = tmp_path / ".claude/tmp/finalize_batch.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "source_path": "raw/factions/Golden-Carvers.md",
                        "source_type": "document",
                        "content_hash": wiki_guard.compute_sha256(first_source),
                        "pages_created": ["content/entities/golden_carvers.md"],
                        "pages_updated": [],
                        "links_woven": 1,
                        "contradictions": [],
                        "log_details": ["CREATED [[golden_carvers]] — salvage guild faction page"],
                        "hot": {
                            "recent_activity": "Golden Carvers created.",
                            "active_threads": ["- Golden Carvers need follow-up."],
                            "key_takeaways": ["- Golden Carvers now exist."],
                            "flagged_contradictions": [],
                        },
                    },
                    {
                        "source_path": "raw/factions/Storm-Cult.md",
                        "source_type": "document",
                        "content_hash": wiki_guard.compute_sha256(second_source),
                        "pages_created": ["content/entities/storm_cult.md"],
                        "pages_updated": ["content/entities/storm_anchor.md"],
                        "links_woven": 3,
                        "contradictions": ["[[storm_cult]] — origin story conflicts with prior source"],
                        "log_details": ["CREATED [[storm_cult]] — faction page"],
                        "hot": {
                            "recent_activity": "Storm Cult created and Storm Anchor updated.",
                            "active_threads": ["- Storm Cult origin is disputed."],
                            "key_takeaways": ["- Storm Cult ties into the Maw."],
                            "flagged_contradictions": ["- [[storm_cult]] — origin story conflicts with prior source."],
                        },
                    },
                ]
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
            ".claude/tmp/finalize_batch.json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    manifest = json.loads((tmp_path / ".manifest.json").read_text(encoding="utf-8"))
    log_text = (tmp_path / "content/log.md").read_text(encoding="utf-8")

    assert code == 0
    assert sorted(manifest["sources"].keys()) == [
        "raw/factions/Golden-Carvers.md",
        "raw/factions/Storm-Cult.md",
    ]
    assert manifest["stats"]["total_sources_ingested"] == 2
    assert 'INGEST source="raw/factions/Golden-Carvers.md"' in log_text
    assert 'INGEST source="raw/factions/Storm-Cult.md"' in log_text
    assert "summary: sources=2 applied=2 skipped=0 created=2 updated=1 contradictions=1" in out


# ---------------------------------------------------------------------------
# Runner finalize tests
# ---------------------------------------------------------------------------

def _make_finalize_stub(checkpoint_dir: Path, name: str, source_path: str, content_hash: str) -> Path:
    stub_path = checkpoint_dir / name
    stub_path.write_text(
        json.dumps(
            {
                "source_path": source_path,
                "source_type": "document",
                "content_hash": content_hash,
                "pages_created": [f"content/entities/{Path(source_path).stem.lower()}.md"],
                "pages_updated": [],
                "links_woven": 1,
                "contradictions": [],
                "log_details": [f"CREATED [[{Path(source_path).stem.lower()}]] — entity"],
                "hot": {
                    "recent_activity": f"Ingested {source_path}.",
                    "active_threads": [],
                    "key_takeaways": [],
                    "flagged_contradictions": [],
                },
            }
        ),
        encoding="utf-8",
    )
    return stub_path


def test_finalize_runner_dir_processes_completed_stubs(tmp_path: Path, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    src_a = raw_dir / "Alpha.md"
    src_a.write_text("# Alpha\n", encoding="utf-8")
    src_b = raw_dir / "Beta.md"
    src_b.write_text("# Beta\n", encoding="utf-8")

    _write_content_root(tmp_path)
    checkpoint_dir = tmp_path / ".claude/tmp/ingest_runner"
    checkpoint_dir.mkdir(parents=True)

    # One completed stub, one empty (agent hasn't written it yet)
    _make_finalize_stub(checkpoint_dir, "01_alpha_finalize.json", "raw/Alpha.md", wiki_guard.compute_sha256(src_a))
    (checkpoint_dir / "02_beta_finalize.json").write_text("", encoding="utf-8")

    result = wiki_guard.finalize_runner_dir(tmp_path, checkpoint_dir)

    assert result["ok"] is True
    assert result["files_found"] == 2
    assert result["files_finalized"] == 1
    assert "02_beta_finalize.json" in result["skipped"]

    manifest = json.loads((tmp_path / ".manifest.json").read_text())
    assert "raw/Alpha.md" in manifest["sources"]
    assert "raw/Beta.md" not in manifest["sources"]


def test_finalize_runner_dir_no_stubs_returns_ok(tmp_path: Path, wiki_guard) -> None:
    _write_content_root(tmp_path)
    checkpoint_dir = tmp_path / ".claude/tmp/ingest_runner"
    checkpoint_dir.mkdir(parents=True)

    result = wiki_guard.finalize_runner_dir(tmp_path, checkpoint_dir)

    assert result["ok"] is True
    assert result["files_finalized"] == 0
    assert result["files_found"] == 0


def test_finalize_runner_dir_missing_dir_returns_error(tmp_path: Path, wiki_guard) -> None:
    _write_content_root(tmp_path)
    checkpoint_dir = tmp_path / ".claude/tmp/does_not_exist"

    result = wiki_guard.finalize_runner_dir(tmp_path, checkpoint_dir)

    assert result["ok"] is False
    assert "not found" in result["error"]


def test_main_ingest_runner_finalize_agent_preset(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    src_a = raw_dir / "Alpha.md"
    src_a.write_text("# Alpha\n", encoding="utf-8")

    _write_content_root(tmp_path)
    checkpoint_dir = tmp_path / ".claude/tmp/ingest_runner"
    checkpoint_dir.mkdir(parents=True)
    _make_finalize_stub(checkpoint_dir, "01_alpha_finalize.json", "raw/Alpha.md", wiki_guard.compute_sha256(src_a))

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-runner-finalize-agent",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out

    assert code == 0
    assert "stubs_found=1" in out
    assert "finalized=1" in out