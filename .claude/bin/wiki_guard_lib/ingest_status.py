from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .models import IngestSourceStatus
from .utils import quote_single

_IGNORED_FILENAMES = {".ds_store", "thumbs.db", "desktop.ini"}


def _should_ignore_raw_source(raw_dir: Path, path: Path) -> bool:
    rel_parts = path.relative_to(raw_dir).parts
    if any(part.startswith(".") for part in rel_parts):
        return True
    return path.name.lower() in _IGNORED_FILENAMES


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def load_manifest_sources(repo_root: Path) -> dict[str, dict[str, object]]:
    manifest_path = repo_root / ".manifest.json"
    if not manifest_path.exists():
        return {}

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(raw, dict):
        return {}

    sources = raw.get("sources")
    if not isinstance(sources, dict):
        return {}

    out: dict[str, dict[str, object]] = {}
    for key, value in sources.items():
        if isinstance(key, str) and isinstance(value, dict):
            out[key] = value
    return out


def gather_ingest_source_status(repo_root: Path) -> list[IngestSourceStatus]:
    raw_dir = repo_root / "raw"
    if not raw_dir.exists():
        return []

    manifest_sources = load_manifest_sources(repo_root)
    statuses: list[IngestSourceStatus] = []

    for path in sorted(p for p in raw_dir.rglob("*") if p.is_file()):
        if _should_ignore_raw_source(raw_dir, path):
            continue
        rel = path.relative_to(repo_root).as_posix()
        content_hash = compute_sha256(path)
        size_bytes = path.stat().st_size
        manifest_entry = manifest_sources.get(rel)

        if manifest_entry is None:
            statuses.append(
                IngestSourceStatus(
                    raw_path=rel,
                    status="new",
                    size_bytes=size_bytes,
                    content_hash=content_hash,
                    ingested_at=None,
                    pages_created=0,
                    pages_updated=0,
                )
            )
            continue

        recorded_hash = manifest_entry.get("content_hash")
        ingested_at = manifest_entry.get("ingested_at")
        pages_created = manifest_entry.get("pages_created")
        pages_updated = manifest_entry.get("pages_updated")
        statuses.append(
            IngestSourceStatus(
                raw_path=rel,
                status="unchanged" if recorded_hash == content_hash else "changed",
                size_bytes=size_bytes,
                content_hash=content_hash,
                ingested_at=ingested_at if isinstance(ingested_at, str) else None,
                pages_created=len(pages_created) if isinstance(pages_created, list) else 0,
                pages_updated=len(pages_updated) if isinstance(pages_updated, list) else 0,
            )
        )

    return statuses


def print_ingest_report(
    statuses: list[IngestSourceStatus],
    *,
    limit: int,
    pending_only: bool,
    output_format: str,
    include_queue: bool,
) -> None:
    pending = sorted(
        (s for s in statuses if s.status in {"new", "changed"}),
        key=lambda s: (s.size_bytes, s.raw_path),
    )
    unchanged = [s for s in statuses if s.status == "unchanged"]

    if output_format == "json":
        display_rows = pending if pending_only else statuses
        rows = [
            {
                "raw_path": s.raw_path,
                "status": s.status,
                "size_bytes": s.size_bytes,
                "ingested_at": s.ingested_at,
                "pages_created": s.pages_created,
                "pages_updated": s.pages_updated,
            }
            for s in display_rows[:limit]
        ]
        payload = {
            "summary": {
                "total_sources": len(statuses),
                "pending_sources": len(pending),
                "unchanged_sources": len(unchanged),
                "next_source": pending[0].raw_path if pending else None,
            },
            "sources": rows,
        }
        if include_queue:
            payload["queue"] = {
                "pending_count": len(pending),
                "sources": [item.raw_path for item in pending],
                "command": build_ingest_queue_command(pending),
            }
        print(json.dumps(payload, indent=2))
        return

    print("wiki_guard ingest report")
    print(f"- total sources: {len(statuses)}")
    print(f"- pending ingest: {len(pending)}")
    print(f"- unchanged: {len(unchanged)}")

    if pending:
        print(f"- next recommended source: {pending[0].raw_path}")
    else:
        print("- next recommended source: none")
        print("all raw sources are unchanged per .manifest.json")
        return

    display_rows = pending if pending_only else statuses
    print("")
    print(f"sources (showing up to {limit}):")
    for item in display_rows[:limit]:
        extra = ""
        if item.status == "changed" and item.ingested_at:
            extra = (
                f"; last_ingested={item.ingested_at}; "
                f"previous_pages={item.pages_created + item.pages_updated}"
            )
        print(f"- {item.raw_path} [{item.status}] ({item.size_bytes} bytes){extra}")

    if include_queue:
        print("")
        print("ingest queue command:")
        print(build_ingest_queue_command(pending))


def build_ingest_queue_command(pending: list[IngestSourceStatus]) -> str:
    if not pending:
        return "# no pending ingest sources"
    commands = [f"/llm-wiki:ingest {quote_single(item.raw_path)}" for item in pending]
    return " && ".join(commands)


def has_pending_ingest_sources(statuses: list[IngestSourceStatus]) -> bool:
    return any(s.status in {"new", "changed"} for s in statuses)
