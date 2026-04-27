from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import (
    ProjectDelta,
    StatusSourceRecord,
    VisibilityTally,
    WikiStatusReport,
)
from .utils import parse_frontmatter

_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".csv",
    ".tsv",
    ".toml",
    ".ini",
}


def _is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in _TEXT_EXTENSIONS or path.suffix == ""


def _to_iso_utc(epoch_seconds: float) -> str:
    dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _parse_iso_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_env_map(repo_root: Path) -> dict[str, str]:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return {}

    out: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out


def _resolve_path(repo_root: Path, raw_value: str) -> Path:
    candidate = Path(raw_value).expanduser()
    if candidate.is_absolute():
        return candidate
    return (repo_root / candidate).resolve()


def _split_multi_path(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    normalized = raw_value.replace("\n", ",").replace(":", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _load_manifest(repo_root: Path) -> dict[str, object]:
    manifest_path = repo_root / ".manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _manifest_sources(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, dict):
        return {}
    out: dict[str, dict[str, object]] = {}
    for key, value in raw_sources.items():
        if isinstance(key, str) and isinstance(value, dict):
            out[key] = value
    return out


def _manifest_projects(payload: dict[str, object]) -> set[str]:
    raw_projects = payload.get("projects")
    if not isinstance(raw_projects, dict):
        return set()
    return {
        key
        for key, value in raw_projects.items()
        if isinstance(key, str) and isinstance(value, dict)
    }


def _scan_source_files(
    base_dir: Path, source_type: str, project: str | None = None
) -> list[dict[str, object]]:
    if not base_dir.exists():
        return []

    rows: list[dict[str, object]] = []
    for path in sorted(item for item in base_dir.rglob("*") if item.is_file()):
        if not _is_text_candidate(path):
            continue
        stat = path.stat()
        rows.append(
            {
                "path": path,
                "source_path": path.as_posix(),
                "source_type": source_type,
                "project": project,
                "size_bytes": stat.st_size,
                "modified_epoch": stat.st_mtime,
                "modified_at": _to_iso_utc(stat.st_mtime),
            }
        )
    return rows


def _scan_documents(repo_root: Path, env_map: dict[str, str]) -> list[dict[str, object]]:
    raw_dirs = _split_multi_path(env_map.get("OBSIDIAN_SOURCES_DIR"))
    if not raw_dirs:
        raw_dirs = ["raw"]

    rows: list[dict[str, object]] = []
    for raw_dir in raw_dirs:
        source_dir = _resolve_path(repo_root, raw_dir)
        rows.extend(_scan_source_files(source_dir, source_type="document"))
    return rows


def _scan_claude_history(
    repo_root: Path, env_map: dict[str, str]
) -> tuple[list[dict[str, object]], dict[str, tuple[int, int]]]:
    raw_history = env_map.get("CLAUDE_HISTORY_PATH")
    if not raw_history:
        return ([], {})

    history_dir = _resolve_path(repo_root, raw_history)
    if not history_dir.exists():
        return ([], {})

    rows: list[dict[str, object]] = []
    per_project: dict[str, tuple[int, int]] = {}

    for project_dir in sorted(item for item in history_dir.iterdir() if item.is_dir()):
        project_name = project_dir.name
        conversations = sorted(project_dir.glob("*.jsonl"))
        memory_files = sorted((project_dir / "memory").glob("*.md"))
        per_project[project_name] = (len(conversations), len(memory_files))

        for file_path in conversations:
            stat = file_path.stat()
            rows.append(
                {
                    "path": file_path,
                    "source_path": file_path.as_posix(),
                    "source_type": "claude_conversation",
                    "project": project_name,
                    "size_bytes": stat.st_size,
                    "modified_epoch": stat.st_mtime,
                    "modified_at": _to_iso_utc(stat.st_mtime),
                }
            )

        for file_path in memory_files:
            stat = file_path.stat()
            rows.append(
                {
                    "path": file_path,
                    "source_path": file_path.as_posix(),
                    "source_type": "claude_memory",
                    "project": project_name,
                    "size_bytes": stat.st_size,
                    "modified_epoch": stat.st_mtime,
                    "modified_at": _to_iso_utc(stat.st_mtime),
                }
            )

    return (rows, per_project)


def _scan_extra_manifest_sources(
    repo_root: Path,
    manifest_sources: dict[str, dict[str, object]],
    existing_keys: set[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source_key, manifest_entry in manifest_sources.items():
        resolved = _resolve_path(repo_root, source_key)
        canonical = resolved.as_posix()
        if canonical in existing_keys or not resolved.exists() or not resolved.is_file():
            continue

        stat = resolved.stat()
        rows.append(
            {
                "path": resolved,
                "source_path": canonical,
                "source_type": str(manifest_entry.get("source_type", "external")),
                "project": manifest_entry.get("project")
                if isinstance(manifest_entry.get("project"), str)
                else None,
                "size_bytes": stat.st_size,
                "modified_epoch": stat.st_mtime,
                "modified_at": _to_iso_utc(stat.st_mtime),
            }
        )
    return rows


def _count_wiki_pages_and_visibility(repo_root: Path) -> tuple[int, int, VisibilityTally]:
    wiki_dir = repo_root / "wiki"
    if not wiki_dir.exists():
        return (0, 0, VisibilityTally(public=0, internal=0, pii=0, total_pages=0))

    total_pages = 0
    categories: set[str] = set()
    public = 0
    internal = 0
    pii = 0

    for path in sorted(wiki_dir.rglob("*.md")):
        total_pages += 1
        rel_parts = path.relative_to(wiki_dir).parts
        if rel_parts:
            categories.add(rel_parts[0])

        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8")) or {}
        tags = frontmatter.get("tags")
        tag_values = [str(item) for item in tags] if isinstance(tags, list) else []
        if "visibility/internal" in tag_values:
            internal += 1
        elif "visibility/pii" in tag_values:
            pii += 1
        else:
            public += 1

    return (
        total_pages,
        len(categories),
        VisibilityTally(public=public, internal=internal, pii=pii, total_pages=total_pages),
    )


def _classify_status(
    snapshot: dict[str, object],
    manifest_entry: dict[str, object] | None,
) -> str:
    if manifest_entry is None:
        return "new"

    current_hash = snapshot.get("content_hash")
    recorded_hash = manifest_entry.get("content_hash")

    if isinstance(recorded_hash, str):
        if recorded_hash != current_hash:
            return "modified"
        current_epoch = snapshot.get("modified_epoch")
        manifest_modified = _parse_iso_datetime(manifest_entry.get("modified_at"))
        if isinstance(current_epoch, float) and manifest_modified is not None:
            if current_epoch > manifest_modified.timestamp():
                return "touched"
        return "unchanged"

    current_epoch = snapshot.get("modified_epoch")
    manifest_modified = _parse_iso_datetime(manifest_entry.get("modified_at"))
    if isinstance(current_epoch, float) and manifest_modified is not None:
        if current_epoch > manifest_modified.timestamp():
            return "modified"
    return "unchanged"


def _recommend_action(
    total_sources: int,
    pending_sources: int,
    deleted_sources: int,
    has_manifest: bool,
) -> str:
    if not has_manifest and total_sources > 0:
        return "full_ingest"
    if total_sources == 0:
        return "no_action"

    if deleted_sources >= max(5, total_sources // 3):
        return "lint_first"

    ratio = pending_sources / total_sources
    if ratio > 0.5:
        return "rebuild"
    if ratio < 0.2:
        return "append"
    return "append"


def _manifest_value(manifest_entry: dict[str, object] | None, key: str) -> str | None:
    if not isinstance(manifest_entry, dict):
        return None
    value = manifest_entry.get(key)
    return value if isinstance(value, str) else None


def _build_status_rows(
    repo_root: Path,
    combined_with_hash: list[dict[str, object]],
    manifest_sources: dict[str, dict[str, object]],
) -> tuple[list[StatusSourceRecord], set[str]]:
    status_rows: list[StatusSourceRecord] = []
    seen_manifest_keys: set[str] = set()

    for snapshot in sorted(
        combined_with_hash,
        key=lambda item: (str(item["source_path"]), str(item["source_type"])),
    ):
        source_path = str(snapshot["source_path"])
        manifest_entry = manifest_sources.get(source_path)
        if manifest_entry is None:
            rel_from_root = _relative_from_root(repo_root, Path(source_path))
            if rel_from_root in manifest_sources:
                manifest_entry = manifest_sources[rel_from_root]
                seen_manifest_keys.add(rel_from_root)
        else:
            seen_manifest_keys.add(source_path)

        if manifest_entry is not None and source_path in manifest_sources:
            seen_manifest_keys.add(source_path)

        size_value = snapshot.get("size_bytes")
        if isinstance(size_value, int):
            size_bytes = size_value
        elif isinstance(size_value, float | str):
            size_bytes = int(size_value)
        else:
            size_bytes = 0
        project_value = snapshot.get("project")
        project = project_value if isinstance(project_value, str) else None

        status_rows.append(
            StatusSourceRecord(
                source_path=source_path,
                status=_classify_status(snapshot, manifest_entry),
                source_type=str(snapshot["source_type"]),
                size_bytes=size_bytes,
                modified_at=str(snapshot["modified_at"]),
                last_ingested=_manifest_value(manifest_entry, "ingested_at"),
                last_modified=_manifest_value(manifest_entry, "modified_at"),
                project=project,
            )
        )

    return (status_rows, seen_manifest_keys)


def _build_project_deltas(
    history_projects: dict[str, tuple[int, int]],
    manifest_projects: set[str],
    status_rows: list[StatusSourceRecord],
) -> list[ProjectDelta]:
    project_delta_map: dict[str, ProjectDelta] = {}

    for project_name, counts in history_projects.items():
        conversations_total, memory_files_total = counts
        project_delta_map[project_name] = ProjectDelta(
            project=project_name,
            conversations_total=conversations_total,
            memory_files_total=memory_files_total,
            new_conversations=0,
            updated_memory_files=0,
            is_new_project=project_name not in manifest_projects,
        )

    for status_row in status_rows:
        if not status_row.project:
            continue

        if status_row.project not in project_delta_map:
            project_delta_map[status_row.project] = ProjectDelta(
                project=status_row.project,
                conversations_total=0,
                memory_files_total=0,
                new_conversations=0,
                updated_memory_files=0,
                is_new_project=status_row.project not in manifest_projects,
            )

        project_delta = project_delta_map[status_row.project]
        if status_row.source_type == "claude_conversation" and status_row.status == "new":
            project_delta.new_conversations += 1
        if status_row.source_type == "claude_memory" and status_row.status in {"new", "modified"}:
            project_delta.updated_memory_files += 1

    return sorted(project_delta_map.values(), key=lambda item: item.project)


def gather_wiki_status(repo_root: Path) -> WikiStatusReport:
    env_map = _load_env_map(repo_root)
    manifest_payload = _load_manifest(repo_root)
    manifest_sources = _manifest_sources(manifest_payload)
    manifest_projects = _manifest_projects(manifest_payload)

    doc_sources = _scan_documents(repo_root, env_map)
    history_sources, history_projects = _scan_claude_history(repo_root, env_map)
    combined = doc_sources + history_sources

    existing_keys = {str(item["source_path"]) for item in combined}
    combined.extend(_scan_extra_manifest_sources(repo_root, manifest_sources, existing_keys))

    combined_with_hash: list[dict[str, object]] = []
    for source_row in combined:
        row_with_hash = dict(source_row)
        path_obj = row_with_hash["path"]
        assert isinstance(path_obj, Path)
        row_with_hash["content_hash"] = _compute_sha256(path_obj)
        combined_with_hash.append(row_with_hash)

    status_rows, seen_manifest_keys = _build_status_rows(
        repo_root,
        combined_with_hash,
        manifest_sources,
    )

    deleted_sources = sorted(
        key
        for key in manifest_sources.keys()
        if key not in seen_manifest_keys and not _path_exists(repo_root, key)
    )

    project_deltas = _build_project_deltas(
        history_projects,
        manifest_projects,
        status_rows,
    )

    total_wiki_pages, wiki_categories, visibility = _count_wiki_pages_and_visibility(repo_root)
    stats = manifest_payload.get("stats")
    total_sources_ingested = 0
    if isinstance(stats, dict):
        count = stats.get("total_sources_ingested")
        if isinstance(count, int):
            total_sources_ingested = count
    if total_sources_ingested == 0:
        total_sources_ingested = len(manifest_sources)

    projects_tracked = len(manifest_projects)
    last_ingest = _find_last_ingest(manifest_sources)

    pending_sources = sum(1 for row in status_rows if row.status in {"new", "modified"})
    recommendation = _recommend_action(
        total_sources=len(status_rows),
        pending_sources=pending_sources,
        deleted_sources=len(deleted_sources),
        has_manifest=bool(manifest_sources),
    )

    return WikiStatusReport(
        total_wiki_pages=total_wiki_pages,
        wiki_categories=wiki_categories,
        visibility=visibility,
        total_sources_ingested=total_sources_ingested,
        projects_tracked=projects_tracked,
        last_ingest=last_ingest,
        sources=status_rows,
        deleted_sources=deleted_sources,
        project_deltas=project_deltas,
        recommendation=recommendation,
    )


def _find_last_ingest(manifest_sources: dict[str, dict[str, object]]) -> str | None:
    values: list[str] = []
    for value in manifest_sources.values():
        ingested_at = value.get("ingested_at")
        if isinstance(ingested_at, str):
            values.append(ingested_at)
    return max(values) if values else None


def _relative_from_root(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _path_exists(repo_root: Path, source_key: str) -> bool:
    return _resolve_path(repo_root, source_key).exists()


def _compute_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def render_wiki_status_json(report: WikiStatusReport, limit: int, pending_only: bool) -> str:
    rows = report.sources
    if pending_only:
        rows = [item for item in rows if item.status in {"new", "modified"}]

    payload = {
        "overview": {
            "total_wiki_pages": report.total_wiki_pages,
            "wiki_categories": report.wiki_categories,
            "visibility": asdict(report.visibility),
            "total_sources_ingested": report.total_sources_ingested,
            "projects_tracked": report.projects_tracked,
            "last_ingest": report.last_ingest,
        },
        "delta": {
            "new": sum(1 for item in report.sources if item.status == "new"),
            "modified": sum(1 for item in report.sources if item.status == "modified"),
            "touched": sum(1 for item in report.sources if item.status == "touched"),
            "unchanged": sum(1 for item in report.sources if item.status == "unchanged"),
            "deleted": len(report.deleted_sources),
        },
        "recommendation": report.recommendation,
        "sources": [asdict(item) for item in rows[:limit]],
        "deleted_sources": report.deleted_sources,
        "projects": [asdict(item) for item in report.project_deltas],
    }
    return json.dumps(payload, indent=2)


def render_wiki_status_text(report: WikiStatusReport, limit: int, pending_only: bool) -> str:
    rows = report.sources
    if pending_only:
        rows = [item for item in rows if item.status in {"new", "modified"}]

    counts = {
        "new": sum(1 for item in report.sources if item.status == "new"),
        "modified": sum(1 for item in report.sources if item.status == "modified"),
        "touched": sum(1 for item in report.sources if item.status == "touched"),
        "unchanged": sum(1 for item in report.sources if item.status == "unchanged"),
        "deleted": len(report.deleted_sources),
    }

    lines: list[str] = ["wiki_guard status report", "", "overview"]
    lines.append(
        f"- total wiki pages: {report.total_wiki_pages} across {report.wiki_categories} categories"
    )

    if report.visibility.internal > 0 or report.visibility.pii > 0:
        lines.append(
            "- page visibility: "
            f"{report.visibility.public} public · "
            f"{report.visibility.internal} internal · "
            f"{report.visibility.pii} pii"
        )

    lines.append(f"- total sources ingested: {report.total_sources_ingested}")
    lines.append(f"- projects tracked: {report.projects_tracked}")
    lines.append(f"- last ingest: {report.last_ingest or 'none'}")
    lines.append("")
    lines.append("delta")
    lines.append(f"- new sources: {counts['new']}")
    lines.append(f"- modified sources: {counts['modified']}")
    lines.append(f"- touched sources: {counts['touched']}")
    lines.append(f"- unchanged sources: {counts['unchanged']}")
    lines.append(f"- deleted sources: {counts['deleted']}")
    lines.append("")
    lines.append(f"recommendation: {report.recommendation}")
    lines.append("")
    lines.append(f"sources (showing up to {limit})")

    for source_item in rows[:limit]:
        lines.append(
            "- "
            f"{source_item.source_path} [{source_item.status}] "
            f"({source_item.source_type}, {source_item.size_bytes} bytes)"
        )

    if report.project_deltas:
        lines.append("")
        lines.append("project deltas")
        for project_item in report.project_deltas:
            lines.append(
                "- "
                f"{project_item.project}: "
                f"conversations={project_item.conversations_total}, "
                f"memory={project_item.memory_files_total}, "
                f"new_conversations={project_item.new_conversations}, "
                f"updated_memory={project_item.updated_memory_files}, "
                f"new_project={str(project_item.is_new_project).lower()}"
            )

    return "\n".join(lines)


def print_wiki_status(
    report: WikiStatusReport, *, limit: int, pending_only: bool, output_format: str
) -> None:
    if output_format == "json":
        print(render_wiki_status_json(report, limit=limit, pending_only=pending_only))
        return
    print(render_wiki_status_text(report, limit=limit, pending_only=pending_only))
