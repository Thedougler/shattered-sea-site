from __future__ import annotations

import json
import sys
from pathlib import Path

from wiki_guard_test_utils import write_manifest


def _write_content_index(repo_root: Path) -> None:
    content_dir = repo_root / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "index.md").write_text(
        "\n".join(
            [
                "# Index",
                "",
                "| Entity | Summary | Sources | Status | Updated |",
                "| -------- | --------- | --------- | -------- | --------- |",
                "| [[the_dravosi_crown]] | colonial power | 1 | active | 2026-04-26 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_build_ingest_prep_maps_manifest_and_links(tmp_path: Path, wiki_guard) -> None:
    raw_path = tmp_path / "raw/factions/Golden-Carvers.md"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        "\n".join(
            [
                "# Golden Carvers",
                "",
                "Connected to [[The-Dravosi-Crown]] and [[Unknown-Thing]].",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    _write_content_index(tmp_path)
    write_manifest(
        tmp_path,
        {
            "raw/factions/Golden-Carvers.md": {
                "content_hash": wiki_guard.compute_sha256(raw_path),
                "ingested_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            }
        },
    )

    payload = wiki_guard.build_ingest_prep(tmp_path, "raw/factions/Golden-Carvers.md")

    assert payload["ok"] is True
    assert payload["knowledge_root"] == "content"
    assert payload["ingest_status"] == "unchanged"
    assert payload["suggested_entity_slug"] == "golden_carvers"

    wikilinks = payload["wikilinks"]
    assert isinstance(wikilinks, dict)
    assert wikilinks["existing_entities"] == ["the_dravosi_crown"]
    assert wikilinks["unresolved_entities"] == ["unknown_thing"]


def test_main_ingest_prep_json_output(tmp_path: Path, monkeypatch, capsys, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    source_path = raw_dir / "topic.md"
    source_path.write_text("hello [[The-Dravosi-Crown]]\n", encoding="utf-8")
    _write_content_index(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-prep",
            "--source",
            "raw/topic.md",
            "--format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["source_path"] == "raw/topic.md"
    assert payload["ingest_status"] == "new"
    assert payload["knowledge_root"] == "content"


def test_main_ingest_prep_missing_source_returns_non_zero(
    tmp_path: Path, monkeypatch, wiki_guard
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-prep",
            "--source",
            "raw/missing.md",
        ],
    )

    code = wiki_guard.main()

    assert code == 2


def test_main_ingest_agent_writes_default_json_file(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    source_path = raw_dir / "topic.md"
    source_path.write_text("hello [[The-Dravosi-Crown]]\n", encoding="utf-8")
    _write_content_index(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-agent",
            "--source",
            "raw/topic.md",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / ".claude/tmp/ingest_prep.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert code == 0
    assert report_path.exists()
    assert payload["ok"] is True
    assert payload["source_path"] == "raw/topic.md"
    assert "ingest prep written to .claude/tmp/ingest_prep.json" in out
    assert "summary: source=raw/topic.md" in out


def test_build_ingest_batch_prioritizes_smallest_pending_sources(
    tmp_path: Path, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    large = raw_dir / "large.md"
    small = raw_dir / "small.md"
    unchanged = raw_dir / "unchanged.md"
    large.write_text("x" * 50, encoding="utf-8")
    small.write_text("x" * 5 + " [[The-Dravosi-Crown]]\n", encoding="utf-8")
    unchanged.write_text("same\n", encoding="utf-8")
    _write_content_index(tmp_path)
    write_manifest(
        tmp_path,
        {
            "raw/unchanged.md": {
                "content_hash": wiki_guard.compute_sha256(unchanged),
                "ingested_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            }
        },
    )

    payload = wiki_guard.build_ingest_batch(tmp_path, limit=1, pending_only=True)

    assert payload["knowledge_root"] == "content"
    assert payload["summary"]["pending_sources"] == 2
    assert payload["summary"]["selected_sources"] == 1
    assert payload["summary"]["next_source"] == "raw/small.md"
    assert payload["queue"]["sources"] == ["raw/small.md", "raw/large.md"]
    assert payload["sources"][0]["source_path"] == "raw/small.md"
    assert payload["sources"][0]["wikilinks"]["existing_entities"] == ["the_dravosi_crown"]


def test_main_ingest_batch_agent_writes_default_json_file(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "topic.md").write_text("hello [[The-Dravosi-Crown]]\n", encoding="utf-8")
    _write_content_index(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-batch-agent",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / ".claude/tmp/ingest_batch.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert code == 0
    assert report_path.exists()
    assert payload["summary"]["pending_only"] is True
    assert payload["summary"]["pending_sources"] == 1
    assert payload["sources"][0]["source_path"] == "raw/topic.md"
    assert "ingest batch written to .claude/tmp/ingest_batch.json" in out
    assert "summary: pending=1 selected=1 next=raw/topic.md" in out


def test_build_ingest_runner_writes_checkpoint_files(tmp_path: Path, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "topic.md").write_text("hello [[The-Dravosi-Crown]]\n", encoding="utf-8")
    _write_content_index(tmp_path)

    checkpoint_dir = tmp_path / ".claude/tmp/runner"
    payload = wiki_guard.build_ingest_runner(
        tmp_path,
        limit=5,
        pending_only=True,
        checkpoint_dir=checkpoint_dir,
    )

    assert payload["checkpoint_dir"] == ".claude/tmp/runner"
    assert payload["summary"]["selected_sources"] == 1
    assert payload["steps"][0]["prep_file"] == ".claude/tmp/runner/01_raw_topic.json"
    assert payload["steps"][0]["finalize_file"] == ".claude/tmp/runner/01_raw_topic_finalize.json"
    prep_payload = json.loads(
        (tmp_path / payload["steps"][0]["prep_file"]).read_text(encoding="utf-8")
    )
    assert prep_payload["source_path"] == "raw/topic.md"


def test_main_ingest_runner_agent_writes_manifest_and_checkpoints(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "topic.md").write_text("hello [[The-Dravosi-Crown]]\n", encoding="utf-8")
    _write_content_index(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-runner-agent",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    runner_path = tmp_path / ".claude/tmp/ingest_runner.json"
    payload = json.loads(runner_path.read_text(encoding="utf-8"))

    assert code == 0
    assert runner_path.exists()
    assert payload["summary"]["pending_only"] is True
    assert payload["steps"][0]["prep_file"] == ".claude/tmp/ingest_runner/01_raw_topic.json"
    assert (tmp_path / ".claude/tmp/ingest_runner/01_raw_topic.json").exists()
    assert "ingest runner written to .claude/tmp/ingest_runner.json" in out
    assert "summary: pending=1 selected=1 checkpoint_dir=.claude/tmp/ingest_runner" in out


def test_ingest_prep_helpers_cover_detection_and_source_types(tmp_path: Path, wiki_guard) -> None:
    ingest_prep = sys.modules["wiki_guard_lib.ingest_prep"]

    assert ingest_prep.detect_knowledge_root(tmp_path) is None
    content_dir = tmp_path / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "index.md").write_text("# Index\n", encoding="utf-8")
    assert ingest_prep.detect_knowledge_root(tmp_path) == content_dir

    assert ingest_prep._source_type_for(tmp_path / "note.md") == "document"
    assert ingest_prep._source_type_for(tmp_path / "paper.pdf") == "pdf"
    assert ingest_prep._source_type_for(tmp_path / "map.png") == "image"
    assert ingest_prep._source_type_for(tmp_path / "archive.bin") == "binary"
    assert ingest_prep._normalize_target("Lore/Storm Anchor.md") == "storm_anchor"


def test_build_ingest_runner_skips_non_dict_sources(tmp_path: Path, wiki_guard) -> None:
    ingest_prep = sys.modules["wiki_guard_lib.ingest_prep"]

    def _fake_batch(*_args, **_kwargs):
        return {
            "knowledge_root": "content",
            "selection_policy": "smallest_pending_first",
            "summary": {"selected_sources": 1},
            "queue": {},
            "sources": [{"source_path": "raw/topic.md"}, "ignore-me"],
        }

    checkpoint_dir = tmp_path / ".claude/tmp/runner"
    original = ingest_prep.build_ingest_batch
    setattr(ingest_prep, "build_ingest_batch", _fake_batch)
    try:
        payload = ingest_prep.build_ingest_runner(
            tmp_path,
            limit=2,
            pending_only=True,
            checkpoint_dir=checkpoint_dir,
        )
    finally:
        setattr(ingest_prep, "build_ingest_batch", original)

    assert len(payload["steps"]) == 1
    assert payload["steps"][0]["source_path"] == "raw/topic.md"


def test_print_ingest_helpers_cover_text_and_json(capsys, wiki_guard) -> None:
    wiki_guard.print_ingest_prep({"ok": False, "error": "boom"}, "text")
    assert "- error: boom" in capsys.readouterr().out

    prep_payload = {
        "ok": True,
        "source_path": "raw/topic.md",
        "knowledge_root": "content",
        "source_type": "document",
        "ingest_status": "new",
        "size_bytes": 12,
        "content_hash": "sha256:abc",
        "suggested_entity_slug": "topic",
        "wikilinks": {
            "total_unique": 2,
            "existing_entities": ["alpha"],
            "unresolved_entities": ["beta"],
        },
    }
    wiki_guard.print_ingest_prep(prep_payload, "text")
    out = capsys.readouterr().out
    assert "existing entities from index" in out
    assert "unresolved entities" in out

    wiki_guard.print_ingest_batch(
        {
            "knowledge_root": "content",
            "summary": {
                "total_sources": 3,
                "pending_sources": 2,
                "selected_sources": 1,
                "next_source": "raw/topic.md",
            },
            "sources": [
                {
                    "source_path": "raw/topic.md",
                    "ingest_status": "new",
                    "size_bytes": 12,
                    "suggested_entity_slug": "topic",
                },
                7,
            ],
            "queue": {"command": "wiki_guard --ingest-report"},
        },
        "text",
    )
    batch_out = capsys.readouterr().out
    assert "selected sources:" in batch_out
    assert "ingest queue command:" in batch_out

    wiki_guard.print_ingest_runner(
        {
            "knowledge_root": "content",
            "checkpoint_dir": ".claude/tmp/runner",
            "summary": {"pending_sources": 2, "selected_sources": 1, "next_source": "raw/topic.md"},
            "steps": [
                {
                    "step": 1,
                    "source_path": "raw/topic.md",
                    "prep_file": ".claude/tmp/runner/01_raw_topic.json",
                    "finalize_file": ".claude/tmp/runner/01_raw_topic_finalize.json",
                },
                "skip",
            ],
        },
        "text",
    )
    runner_out = capsys.readouterr().out
    assert "steps:" in runner_out
    assert "prep=.claude/tmp/runner/01_raw_topic.json" in runner_out

    wiki_guard.print_ingest_batch({"ok": True}, "json")
    assert "ok" in capsys.readouterr().out
