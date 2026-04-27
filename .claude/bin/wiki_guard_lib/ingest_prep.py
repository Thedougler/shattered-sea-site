from __future__ import annotations

import json
from pathlib import Path

from .constants import INDEX_ROW_RE, WIKILINK_RE
from .ingest_status import compute_sha256, load_manifest_sources
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