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
