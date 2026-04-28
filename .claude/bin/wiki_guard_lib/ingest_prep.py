from __future__ import annotations

import json
from pathlib import Path

from .constants import INDEX_ROW_RE, WIKILINK_RE
from .ingest_status import (
    build_ingest_queue_command,
    compute_sha256,
    gather_ingest_source_status,
    load_manifest_sources,
)
from .knowledge_layout import detect_knowledge_layout

_DOCUMENT_EXTENSIONS = {".md", ".txt", ".rst"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def detect_knowledge_root(repo_root: Path) -> Path | None:
    layout = detect_knowledge_layout(repo_root)
    if layout is None:
        return None
    return layout.page_root


def _source_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in _DOCUMENT_EXTENSIONS:
        return "document"
    if suffix == ".pdf":
        return "pdf"
    if suffix in _IMAGE_EXTENSIONS:
        return "image"
    return "binary"


def _normalize_target(target: str) -> str:
    slug = target.split("/")[-1].strip()
    if slug.endswith(".md"):
        slug = slug[:-3]
    return slug.replace("-", "_").replace(" ", "_").lower()


def _load_index_slugs(index_path: Path) -> set[str]:
    slugs: set[str] = set()
    for line in index_path.read_text(encoding="utf-8").splitlines():
        match = INDEX_ROW_RE.match(line)
        if not match:
            continue
        slugs.add(match.group(1))
    return slugs


def build_ingest_prep(repo_root: Path, source_path: str) -> dict[str, object]:
    source_rel = source_path.strip()
    raw_path = (repo_root / source_rel).resolve()
    if not raw_path.exists() or not raw_path.is_file():
        return {
            "ok": False,
            "error": f"source file not found: {source_rel}",
            "source_path": source_rel,
        }

    manifest_sources = load_manifest_sources(repo_root)
    manifest_entry = manifest_sources.get(source_rel)
    content_hash = compute_sha256(raw_path)
    manifest_hash = manifest_entry.get("content_hash") if isinstance(manifest_entry, dict) else None

    if manifest_entry is None:
        ingest_status = "new"
    elif manifest_hash == content_hash:
        ingest_status = "unchanged"
    else:
        ingest_status = "changed"

    source_text = ""
    if _source_type_for(raw_path) == "document":
        source_text = raw_path.read_text(encoding="utf-8")

    targets = {
        _normalize_target(link)
        for link in WIKILINK_RE.findall(source_text)
        if _normalize_target(link)
    }

    layout = detect_knowledge_layout(repo_root)
    knowledge_root = layout.page_root if layout is not None else None
    index_slugs: set[str] = set()
    knowledge_root_rel = None
    if layout is not None:
        knowledge_root = layout.page_root
        knowledge_root_rel = knowledge_root.relative_to(repo_root).as_posix() if knowledge_root != repo_root else "."
        index_path = layout.index_path
        if index_path.exists():
            index_slugs = _load_index_slugs(index_path)

    existing_links = sorted(link for link in targets if link in index_slugs)
    unresolved_links = sorted(link for link in targets if link not in index_slugs)
    suggested_slug = _normalize_target(raw_path.stem)

    return {
        "ok": True,
        "source_path": source_rel,
        "knowledge_root": knowledge_root_rel,
        "source_type": _source_type_for(raw_path),
        "size_bytes": raw_path.stat().st_size,
        "content_hash": content_hash,
        "ingest_status": ingest_status,
        "last_ingested": manifest_entry.get("ingested_at") if isinstance(manifest_entry, dict) else None,
        "suggested_entity_slug": suggested_slug,
        "wikilinks": {
            "total_unique": len(targets),
            "existing_entities": existing_links,
            "unresolved_entities": unresolved_links,
        },
    }


def build_ingest_batch(
    repo_root: Path,
    *,
    limit: int,
    pending_only: bool,
) -> dict[str, object]:
    statuses = gather_ingest_source_status(repo_root)
    pending = sorted(
        (item for item in statuses if item.status in {"new", "changed"}),
        key=lambda item: (item.size_bytes, item.raw_path),
    )
    selected_statuses = pending if pending_only else statuses
    selected_statuses = selected_statuses[:limit]

    layout = detect_knowledge_layout(repo_root)
    knowledge_root = None
    if layout is not None:
        knowledge_root = layout.page_root.relative_to(repo_root).as_posix() if layout.page_root != repo_root else "."

    return {
        "ok": True,
        "knowledge_root": knowledge_root,
        "selection_policy": "smallest_pending_first",
        "summary": {
            "total_sources": len(statuses),
            "pending_sources": len(pending),
            "selected_sources": len(selected_statuses),
            "pending_only": pending_only,
            "next_source": pending[0].raw_path if pending else None,
        },
        "sources": [build_ingest_prep(repo_root, item.raw_path) for item in selected_statuses],
        "queue": {
            "pending_count": len(pending),
            "sources": [item.raw_path for item in pending],
            "command": build_ingest_queue_command(pending),
        },
    }


def _checkpoint_slug(source_path: str) -> str:
    parts = source_path.split("/")
    stem = Path(parts[-1]).stem
    parent = parts[-2] if len(parts) > 1 else "raw"
    return _normalize_target(f"{parent}_{stem}")


def build_ingest_runner(
    repo_root: Path,
    *,
    limit: int,
    pending_only: bool,
    checkpoint_dir: Path,
) -> dict[str, object]:
    batch = build_ingest_batch(repo_root, limit=limit, pending_only=pending_only)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    steps: list[dict[str, object]] = []
    for index, item in enumerate(batch["sources"], start=1):
        if not isinstance(item, dict):
            continue
        source_path = str(item["source_path"])
        checkpoint_name = f"{index:02d}_{_checkpoint_slug(source_path)}.json"
        checkpoint_path = checkpoint_dir / checkpoint_name
        checkpoint_path.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
        finalize_stub = checkpoint_dir / f"{index:02d}_{_checkpoint_slug(source_path)}_finalize.json"
        steps.append(
            {
                "step": index,
                "source_path": source_path,
                "prep_file": checkpoint_path.relative_to(repo_root).as_posix(),
                "finalize_file": finalize_stub.relative_to(repo_root).as_posix(),
                "ingest_status": item.get("ingest_status"),
                "suggested_entity_slug": item.get("suggested_entity_slug"),
                "status": "ready",
            }
        )

    runner_payload = {
        "ok": True,
        "knowledge_root": batch.get("knowledge_root"),
        "selection_policy": batch.get("selection_policy"),
        "summary": batch.get("summary"),
        "queue": batch.get("queue"),
        "checkpoint_dir": checkpoint_dir.relative_to(repo_root).as_posix(),
        "steps": steps,
        "instructions": [
            "Read steps in order and consume each prep_file directly instead of calling --ingest-agent again.",
            "After completing a source, write its finalize payload to the paired finalize_file path.",
            "When all steps are done, run: wiki_guard --ingest-runner-finalize to process all completed stubs in one pass.",
            "You may also run --ingest-runner-finalize after each step for incremental bookkeeping.",
        ],
    }
    return runner_payload


def print_ingest_prep(payload: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
        return

    if not payload.get("ok"):
        print("wiki_guard ingest prep")
        print(f"- error: {payload.get('error')}")
        return

    wikilinks = payload.get("wikilinks")
    existing: list[str] = []
    unresolved: list[str] = []
    total_unique = 0
    if isinstance(wikilinks, dict):
        raw_existing = wikilinks.get("existing_entities")
        raw_unresolved = wikilinks.get("unresolved_entities")
        if isinstance(raw_existing, list):
            existing = [str(item) for item in raw_existing]
        if isinstance(raw_unresolved, list):
            unresolved = [str(item) for item in raw_unresolved]
        raw_total = wikilinks.get("total_unique")
        if isinstance(raw_total, int):
            total_unique = raw_total

    print("wiki_guard ingest prep")
    print(f"- source: {payload.get('source_path')}")
    print(f"- knowledge_root: {payload.get('knowledge_root')}")
    print(f"- source_type: {payload.get('source_type')}")
    print(f"- ingest_status: {payload.get('ingest_status')}")
    print(f"- size_bytes: {payload.get('size_bytes')}")
    print(f"- content_hash: {payload.get('content_hash')}")
    print(f"- suggested_entity_slug: {payload.get('suggested_entity_slug')}")
    print(f"- unique_wikilinks: {total_unique}")

    if existing:
        print("\nexisting entities from index:")
        for slug in existing:
            print(f"- {slug}")

    if unresolved:
        print("\nunresolved entities (likely create-or-map):")
        for slug in unresolved:
            print(f"- {slug}")


def print_ingest_batch(payload: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
        return

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    summary = summary if isinstance(summary, dict) else {}
    sources = payload.get("sources") if isinstance(payload.get("sources"), list) else []
    queue = payload.get("queue") if isinstance(payload.get("queue"), dict) else {}
    queue = queue if isinstance(queue, dict) else {}

    print("wiki_guard ingest batch")
    print(f"- knowledge_root: {payload.get('knowledge_root')}")
    print(f"- total_sources: {summary.get('total_sources')}")
    print(f"- pending_sources: {summary.get('pending_sources')}")
    print(f"- selected_sources: {summary.get('selected_sources')}")
    print(f"- next_source: {summary.get('next_source')}")

    if sources:
        print("\nselected sources:")
        for item in sources:
            if not isinstance(item, dict):
                continue
            print(
                f"- {item.get('source_path')} [{item.get('ingest_status')}] "
                f"{item.get('size_bytes')} bytes -> {item.get('suggested_entity_slug')}"
            )

    print("\ningest queue command:")
    print(queue.get("command", "# no pending ingest sources"))


def print_ingest_runner(payload: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
        return

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    summary = summary if isinstance(summary, dict) else {}
    steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []

    print("wiki_guard ingest runner")
    print(f"- knowledge_root: {payload.get('knowledge_root')}")
    print(f"- checkpoint_dir: {payload.get('checkpoint_dir')}")
    print(f"- pending_sources: {summary.get('pending_sources')}")
    print(f"- selected_sources: {summary.get('selected_sources')}")
    print(f"- next_source: {summary.get('next_source')}")

    if steps:
        print("\nsteps:")
        for item in steps:
            if not isinstance(item, dict):
                continue
            print(
                f"- step {item.get('step')}: {item.get('source_path')} -> "
                f"prep={item.get('prep_file')} finalize={item.get('finalize_file')}"
            )