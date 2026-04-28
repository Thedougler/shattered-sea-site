from __future__ import annotations

import json
import sys
from pathlib import Path

from wiki_guard_test_utils import write_manifest


def test_gather_ingest_source_status_classifies_sources(tmp_path: Path, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    unchanged_path = raw_dir / "unchanged.md"
    changed_path = raw_dir / "changed.md"
    new_path = raw_dir / "new.md"

    unchanged_path.write_text("same\n", encoding="utf-8")
    changed_path.write_text("current\n", encoding="utf-8")
    new_path.write_text("brand new\n", encoding="utf-8")

    write_manifest(
        tmp_path,
        {
            "raw/unchanged.md": {
                "content_hash": wiki_guard.compute_sha256(unchanged_path),
                "ingested_at": "2026-04-26T00:00:00Z",
                "pages_created": ["wiki/entities/a.md"],
                "pages_updated": [],
            },
            "raw/changed.md": {
                "content_hash": "sha256:not-a-match",
                "ingested_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": ["wiki/entities/b.md", "wiki/entities/c.md"],
            },
        },
    )

    statuses = wiki_guard.gather_ingest_source_status(tmp_path)
    by_path = {item.raw_path: item for item in statuses}

    assert by_path["raw/unchanged.md"].status == "unchanged"
    assert by_path["raw/changed.md"].status == "changed"
    assert by_path["raw/new.md"].status == "new"
    assert by_path["raw/changed.md"].pages_updated == 2


def test_main_ingest_report_json_output(tmp_path: Path, monkeypatch, capsys, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    source_path = raw_dir / "topic.md"
    source_path.write_text("hello\n", encoding="utf-8")
    write_manifest(
        tmp_path,
        {
            "raw/topic.md": {
                "content_hash": wiki_guard.compute_sha256(source_path),
                "ingested_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            }
        },
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-report",
            "--format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["summary"]["total_sources"] == 1
    assert payload["summary"]["pending_sources"] == 0
    assert payload["summary"]["next_source"] is None


def test_print_ingest_report_pending_only_text(capsys, wiki_guard) -> None:
    statuses = [
        wiki_guard.IngestSourceStatus(
            raw_path="raw/a.md",
            status="unchanged",
            size_bytes=300,
            content_hash="sha256:a",
            ingested_at="2026-04-26T00:00:00Z",
            pages_created=1,
            pages_updated=0,
        ),
        wiki_guard.IngestSourceStatus(
            raw_path="raw/b.md",
            status="new",
            size_bytes=100,
            content_hash="sha256:b",
            ingested_at=None,
            pages_created=0,
            pages_updated=0,
        ),
    ]

    wiki_guard.print_ingest_report(
        statuses,
        limit=5,
        pending_only=True,
        output_format="text",
        include_queue=False,
    )
    out = capsys.readouterr().out

    assert "next recommended source: raw/b.md" in out
    assert "raw/b.md [new]" in out
    assert "raw/a.md [unchanged]" not in out


def test_build_ingest_queue_command_orders_by_pending_list(wiki_guard) -> None:
    pending = [
        wiki_guard.IngestSourceStatus(
            raw_path="raw/species/Human.md",
            status="new",
            size_bytes=100,
            content_hash="sha256:a",
            ingested_at=None,
            pages_created=0,
            pages_updated=0,
        ),
        wiki_guard.IngestSourceStatus(
            raw_path="raw/species/Tabaxi.md",
            status="changed",
            size_bytes=200,
            content_hash="sha256:b",
            ingested_at="2026-04-26T00:00:00Z",
            pages_created=1,
            pages_updated=1,
        ),
    ]

    command = wiki_guard.build_ingest_queue_command(pending)

    assert command == (
        "/llm-wiki:ingest 'raw/species/Human.md' && /llm-wiki:ingest 'raw/species/Tabaxi.md'"
    )


def test_main_ingest_report_json_with_queue(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    pending_path = raw_dir / "pending.md"
    pending_path.write_text("hello\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-report",
            "--pending-only",
            "--ingest-queue",
            "--format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["queue"]["pending_count"] == 1
    assert payload["queue"]["sources"] == ["raw/pending.md"]
    assert payload["queue"]["command"] == "/llm-wiki:ingest 'raw/pending.md'"


def test_print_ingest_report_includes_text_queue(capsys, wiki_guard) -> None:
    statuses = [
        wiki_guard.IngestSourceStatus(
            raw_path="raw/new.md",
            status="new",
            size_bytes=1,
            content_hash="sha256:a",
            ingested_at=None,
            pages_created=0,
            pages_updated=0,
        )
    ]

    wiki_guard.print_ingest_report(
        statuses,
        limit=10,
        pending_only=True,
        output_format="text",
        include_queue=True,
    )
    out = capsys.readouterr().out

    assert "ingest queue command:" in out
    assert "/llm-wiki:ingest 'raw/new.md'" in out


def test_has_pending_ingest_sources_detects_new_or_changed(wiki_guard) -> None:
    statuses = [
        wiki_guard.IngestSourceStatus(
            raw_path="raw/a.md",
            status="unchanged",
            size_bytes=1,
            content_hash="sha256:a",
            ingested_at="2026-04-26T00:00:00Z",
            pages_created=0,
            pages_updated=0,
        ),
        wiki_guard.IngestSourceStatus(
            raw_path="raw/b.md",
            status="changed",
            size_bytes=2,
            content_hash="sha256:b",
            ingested_at="2026-04-26T00:00:00Z",
            pages_created=0,
            pages_updated=0,
        ),
    ]

    assert wiki_guard.has_pending_ingest_sources(statuses) is True


def test_main_ingest_report_fail_on_pending_returns_non_zero(
    tmp_path: Path, monkeypatch, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "pending.md").write_text("hello\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-report",
            "--fail-on-pending",
        ],
    )

    code = wiki_guard.main()

    assert code == 2


def test_main_ingest_report_fail_on_pending_returns_zero_when_clean(
    tmp_path: Path, monkeypatch, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    source_path = raw_dir / "clean.md"
    source_path.write_text("hello\n", encoding="utf-8")
    write_manifest(
        tmp_path,
        {
            "raw/clean.md": {
                "content_hash": wiki_guard.compute_sha256(source_path),
                "ingested_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            }
        },
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-report",
            "--fail-on-pending",
        ],
    )

    code = wiki_guard.main()

    assert code == 0


def test_main_ingest_report_writes_output_file(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "pending.md").write_text("hello\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-report",
            "--pending-only",
            "--format",
            "json",
            "--ingest-output-file",
            ".claude/tmp/ingest_report.json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    report_path = tmp_path / ".claude/tmp/ingest_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert code == 0
    assert report_path.exists()
    assert payload["summary"]["pending_sources"] == 1
    assert payload["summary"]["next_source"] == "raw/pending.md"
    assert "ingest report written to .claude/tmp/ingest_report.json" in out
    assert "summary: total=1 pending=1" in out


def test_gather_ingest_source_status_ignores_hidden_and_system_files(
    tmp_path: Path, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "valid.md").write_text("ok\n", encoding="utf-8")
    (raw_dir / ".DS_Store").write_text("ignored\n", encoding="utf-8")
    (raw_dir / "Thumbs.db").write_text("ignored\n", encoding="utf-8")
    hidden_dir = raw_dir / ".cache"
    hidden_dir.mkdir(parents=True)
    (hidden_dir / "x.md").write_text("ignored\n", encoding="utf-8")

    statuses = wiki_guard.gather_ingest_source_status(tmp_path)
    paths = [item.raw_path for item in statuses]

    assert paths == ["raw/valid.md"]


def test_main_ingest_report_queue_excludes_hidden_files(
    tmp_path: Path, monkeypatch, capsys, wiki_guard
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "visible.md").write_text("ok\n", encoding="utf-8")
    (raw_dir / ".DS_Store").write_text("ignored\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--ingest-report",
            "--pending-only",
            "--ingest-queue",
            "--format",
            "json",
        ],
    )

    code = wiki_guard.main()
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["queue"]["sources"] == ["raw/visible.md"]
    assert payload["queue"]["command"] == "/llm-wiki:ingest 'raw/visible.md'"
