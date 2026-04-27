from __future__ import annotations

import json
import sys
from pathlib import Path

from wiki_guard_test_utils import write_manifest, write_page


def _write_env(repo_root: Path, content: str) -> None:
    (repo_root / ".env").write_text(content, encoding="utf-8")


def test_gather_wiki_status_classifies_delta_states(tmp_path: Path, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)

    unchanged_path = raw_dir / "unchanged.md"
    modified_path = raw_dir / "modified.md"
    touched_path = raw_dir / "touched.md"
    new_path = raw_dir / "new.md"

    unchanged_path.write_text("same\n", encoding="utf-8")
    modified_path.write_text("current\n", encoding="utf-8")
    touched_path.write_text("still same\n", encoding="utf-8")
    new_path.write_text("brand new\n", encoding="utf-8")

    _write_env(tmp_path, "OBSIDIAN_SOURCES_DIR=raw\n")
    write_manifest(
        tmp_path,
        {
            "raw/unchanged.md": {
                "content_hash": wiki_guard.compute_sha256(unchanged_path),
                "ingested_at": "2026-04-26T00:00:00Z",
                "modified_at": "2999-01-01T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            },
            "raw/modified.md": {
                "content_hash": "sha256:not-a-match",
                "ingested_at": "2026-04-26T00:00:00Z",
                "modified_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            },
            "raw/touched.md": {
                "content_hash": wiki_guard.compute_sha256(touched_path),
                "ingested_at": "2026-04-26T00:00:00Z",
                "modified_at": "2020-01-01T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            },
            "raw/deleted.md": {
                "content_hash": "sha256:deadbeef",
                "ingested_at": "2026-04-26T00:00:00Z",
                "modified_at": "2026-04-26T00:00:00Z",
                "pages_created": [],
                "pages_updated": [],
            },
        },
    )

    report = wiki_guard.gather_wiki_status(tmp_path)
    counts = {state: 0 for state in ["new", "modified", "touched", "unchanged"]}
    for item in report.sources:
        counts[item.status] += 1

    assert counts["unchanged"] == 1
    assert counts["modified"] == 1
    assert counts["touched"] == 1
    assert counts["new"] == 1
    assert report.deleted_sources == ["raw/deleted.md"]
    assert report.recommendation == "append"


def test_gather_wiki_status_reports_visibility_tally(tmp_path: Path, wiki_guard) -> None:
    _write_env(tmp_path, "OBSIDIAN_SOURCES_DIR=raw\n")

    write_page(
        tmp_path / "wiki/entities/public_page.md",
        """---
tags:
  - lore
---
""",
    )
    write_page(
        tmp_path / "wiki/entities/internal_page.md",
        """---
tags:
  - visibility/internal
---
""",
    )
    write_page(
        tmp_path / "wiki/entities/pii_page.md",
        """---
tags:
  - visibility/pii
---
""",
    )

    report = wiki_guard.gather_wiki_status(tmp_path)

    assert report.visibility.public == 1
    assert report.visibility.internal == 1
    assert report.visibility.pii == 1
    assert report.visibility.total_pages == 3


def test_main_status_report_json_output(tmp_path: Path, monkeypatch, capsys, wiki_guard) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "topic.md").write_text("hello\n", encoding="utf-8")
    _write_env(tmp_path, "OBSIDIAN_SOURCES_DIR=raw\n")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wiki_guard.py",
            "--repo-root",
            str(tmp_path),
            "--status-report",
            "--status-format",
            "json",
        ],
    )

    code = wiki_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["delta"]["new"] == 1
    assert payload["recommendation"] == "full_ingest"


def test_gather_wiki_status_reports_claude_project_delta(tmp_path: Path, wiki_guard) -> None:
    history_dir = tmp_path / ".claude-history"
    proj_a = history_dir / "proj_a"
    proj_new = history_dir / "proj_new"

    (proj_a / "memory").mkdir(parents=True)
    (proj_new / "memory").mkdir(parents=True)

    convo_a = proj_a / "session.jsonl"
    memory_a = proj_a / "memory/session.md"
    convo_new = proj_new / "new_session.jsonl"

    convo_a.write_text("{}\n", encoding="utf-8")
    memory_a.write_text("memory\n", encoding="utf-8")
    convo_new.write_text("{}\n", encoding="utf-8")

    _write_env(
        tmp_path,
        "\n".join(
            [
                "OBSIDIAN_SOURCES_DIR=raw",
                "CLAUDE_HISTORY_PATH=.claude-history",
            ]
        )
        + "\n",
    )

    write_manifest(
        tmp_path,
        {
            ".claude-history/proj_a/session.jsonl": {
                "content_hash": wiki_guard.compute_sha256(convo_a),
                "ingested_at": "2026-04-26T00:00:00Z",
                "modified_at": "2999-01-01T00:00:00Z",
                "source_type": "claude_conversation",
                "project": "proj_a",
                "pages_created": [],
                "pages_updated": [],
            },
            ".claude-history/proj_a/memory/session.md": {
                "content_hash": "sha256:not-a-match",
                "ingested_at": "2026-04-26T00:00:00Z",
                "modified_at": "2026-04-26T00:00:00Z",
                "source_type": "claude_memory",
                "project": "proj_a",
                "pages_created": [],
                "pages_updated": [],
            },
        },
    )

    manifest_path = tmp_path / ".manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["projects"] = {
        "proj_a": {
            "source_path": ".claude-history/proj_a",
            "vault_path": "projects/proj_a",
            "last_ingested": "2026-04-26T00:00:00Z",
            "conversations_ingested": 1,
            "conversations_total": 1,
            "memory_files_ingested": 1,
        }
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report = wiki_guard.gather_wiki_status(tmp_path)
    by_project = {item.project: item for item in report.project_deltas}

    assert by_project["proj_a"].updated_memory_files == 1
    assert by_project["proj_a"].is_new_project is False
    assert by_project["proj_new"].new_conversations == 1
    assert by_project["proj_new"].is_new_project is True


def test_status_audit_helpers_cover_edge_cases(tmp_path: Path, wiki_guard) -> None:
    import wiki_guard_lib.status_audit as status_audit

    assert status_audit._split_multi_path(None) == []
    assert status_audit._split_multi_path("a:b,c\nd") == ["a", "b", "c", "d"]
    assert status_audit._load_env_map(tmp_path) == {}

    _write_env(
        tmp_path,
        "\n".join(["# comment", "FOO=bar", " BAD = value ", "NOT_A_PAIR"]) + "\n",
    )
    env_map = status_audit._load_env_map(tmp_path)
    assert env_map["FOO"] == "bar"
    assert env_map["BAD"] == "value"

    manifest_path = tmp_path / ".manifest.json"
    manifest_path.write_text("{not-json", encoding="utf-8")
    assert status_audit._load_manifest(tmp_path) == {}

    manifest_path.write_text(json.dumps(["bad"]), encoding="utf-8")
    assert status_audit._load_manifest(tmp_path) == {}

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / "file.md").write_text("x\n", encoding="utf-8")
    (raw_dir / "binary.png").write_bytes(b"\x89PNG\r\n")
    doc_rows = status_audit._scan_documents(tmp_path, {})
    assert len(doc_rows) == 1
    assert doc_rows[0]["source_type"] == "document"

    assert status_audit._scan_claude_history(tmp_path, {}) == ([], {})
    assert status_audit._scan_claude_history(tmp_path, {"CLAUDE_HISTORY_PATH": "missing"}) == ([], {})

    other_file = tmp_path / "notes.txt"
    other_file.write_text("note\n", encoding="utf-8")
    extras = status_audit._scan_extra_manifest_sources(
        tmp_path,
        {
            "notes.txt": {"project": 7},
            "raw/file.md": {"source_type": "document"},
        },
        existing_keys={doc_rows[0]["source_path"]},
    )
    assert len(extras) == 1
    assert extras[0]["source_type"] == "external"
    assert extras[0]["project"] is None

    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()
    pages, cats, visibility = status_audit._count_wiki_pages_and_visibility(empty_repo)
    assert pages == 0
    assert cats == 0
    assert visibility.total_pages == 0

    snapshot = {"content_hash": "sha256:a", "modified_epoch": 1000.0}
    assert status_audit._classify_status(snapshot, None) == "new"
    assert status_audit._classify_status(snapshot, {"content_hash": "sha256:b"}) == "modified"
    assert (
        status_audit._classify_status(
            snapshot,
            {"content_hash": "sha256:a", "modified_at": "1970-01-01T00:00:00Z"},
        )
        == "touched"
    )
    assert (
        status_audit._classify_status(
            snapshot,
            {"content_hash": "sha256:a", "modified_at": "2999-01-01T00:00:00Z"},
        )
        == "unchanged"
    )
    assert (
        status_audit._classify_status(
            snapshot,
            {"modified_at": "1970-01-01T00:00:00Z"},
        )
        == "modified"
    )

    assert status_audit._recommend_action(10, 2, 0, False) == "full_ingest"
    assert status_audit._recommend_action(0, 0, 0, True) == "no_action"
    assert status_audit._recommend_action(10, 1, 5, True) == "lint_first"
    assert status_audit._recommend_action(10, 6, 0, True) == "rebuild"
    assert status_audit._recommend_action(10, 1, 0, True) == "append"


def test_status_render_and_print_helpers(capsys, wiki_guard) -> None:
    report = wiki_guard.WikiStatusReport(
        total_wiki_pages=2,
        wiki_categories=1,
        visibility=wiki_guard.VisibilityTally(public=2, internal=0, pii=0, total_pages=2),
        total_sources_ingested=3,
        projects_tracked=1,
        last_ingest=None,
        sources=[
            wiki_guard.StatusSourceRecord(
                source_path="raw/a.md",
                status="new",
                source_type="document",
                size_bytes=10,
                modified_at="2026-04-26T00:00:00Z",
                last_ingested=None,
                last_modified=None,
                project=None,
            )
        ],
        deleted_sources=[],
        project_deltas=[],
        recommendation="append",
    )

    text = wiki_guard.render_wiki_status_text(report, limit=10, pending_only=False)
    assert "wiki_guard status report" in text
    assert "page visibility" not in text

    payload = json.loads(wiki_guard.render_wiki_status_json(report, limit=10, pending_only=False))
    assert payload["delta"]["new"] == 1

    wiki_guard.print_wiki_status(report, limit=10, pending_only=True, output_format="text")
    out_text = capsys.readouterr().out
    assert "sources (showing up to 10)" in out_text

    wiki_guard.print_wiki_status(report, limit=10, pending_only=True, output_format="json")
    out_json = capsys.readouterr().out
    assert '"recommendation": "append"' in out_json
