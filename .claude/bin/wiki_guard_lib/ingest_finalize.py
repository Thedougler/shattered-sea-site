from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from .inventory import build_page_inventory
from .knowledge_layout import detect_knowledge_layout


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("finalize payload must be a JSON object")
    return cast(dict[str, object], payload)


def _normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            trimmed = item.strip()
            if trimmed:
                out.append(trimmed)
    return out


def _normalize_contradictions(value: object) -> list[str]:
    return _normalize_string_list(value)


def _hot_template() -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    return (
        "---\n"
        "title: Hot Cache\n"
        f"updated: {today}\n"
        "---\n\n"
        "# Hot Cache\n\n"
        "## Recent Activity\n\n"
        "## Active Threads\n\n"
        "## Key Takeaways\n\n"
        "## Flagged Contradictions\n"
    )


def _log_template(repo_root: Path) -> str:
    domain = repo_root.name.replace("-", "_")
    return (
        f"# Audit Log: {domain}\n\n"
        "> Append-only chronological record of all wiki modifications.\n"
        "> Format: `## YYYY-MM-DD HH:MM` followed by bulleted action list.\n"
        "> Never edit or delete prior entries. Only append.\n\n"
        "---\n"
    )


def _split_hot_sections(text: str) -> tuple[dict[str, list[str]], list[str]]:
    headings = {
        "## Recent Activity": "recent_activity",
        "## Active Threads": "active_threads",
        "## Key Takeaways": "key_takeaways",
        "## Flagged Contradictions": "flagged_contradictions",
    }
    sections: dict[str, list[str]] = {value: [] for value in headings.values()}
    preamble: list[str] = []
    current: str | None = None

    for line in text.splitlines():
        heading_key = headings.get(line.strip())
        if heading_key is not None:
            current = heading_key
            continue
        if current is None:
            preamble.append(line)
            continue
        sections[current].append(line)

    return sections, preamble


def _render_hot(preamble: list[str], sections: dict[str, list[str]]) -> str:
    blocks = ["\n".join(preamble).rstrip(), "## Recent Activity", "\n".join(sections["recent_activity"]).strip()]
    blocks.extend([
        "## Active Threads",
        "\n".join(sections["active_threads"]).strip(),
        "## Key Takeaways",
        "\n".join(sections["key_takeaways"]).strip(),
        "## Flagged Contradictions",
        "\n".join(sections["flagged_contradictions"]).strip(),
    ])
    return "\n\n".join(block for block in blocks if block != "").rstrip() + "\n"


def _update_hot(layout_hot_path: Path, payload: dict[str, object]) -> Path:
    hot_data = payload.get("hot") if isinstance(payload.get("hot"), dict) else {}
    hot_payload = cast(dict[str, object], hot_data)

    if layout_hot_path.exists():
        text = layout_hot_path.read_text(encoding="utf-8")
    else:
        layout_hot_path.parent.mkdir(parents=True, exist_ok=True)
        text = _hot_template()

    sections, preamble = _split_hot_sections(text)
    recent_summary = hot_payload.get("recent_activity")
    if isinstance(recent_summary, str) and recent_summary.strip():
        existing_recent = [line for line in sections["recent_activity"] if line.strip()]
        max_items = hot_payload.get("recent_activity_limit")
        limit = max_items if isinstance(max_items, int) and max_items > 0 else 12
        existing_recent.insert(0, f"- [{datetime.now(timezone.utc).date().isoformat()}] INGEST `{payload['source_path']}` — {recent_summary.strip()}")
        sections["recent_activity"] = existing_recent[:limit]

    active_threads = _normalize_string_list(hot_payload.get("active_threads"))
    if active_threads:
        sections["active_threads"] = active_threads

    key_takeaways = _normalize_string_list(hot_payload.get("key_takeaways"))
    if key_takeaways:
        sections["key_takeaways"] = key_takeaways

    contradictions = _normalize_contradictions(hot_payload.get("flagged_contradictions"))
    sections["flagged_contradictions"] = contradictions or ["*None.*"]

    if preamble:
        updated_line = f"updated: {datetime.now(timezone.utc).date().isoformat()}"
        preamble = [updated_line if line.startswith("updated:") else line for line in preamble]

    layout_hot_path.write_text(_render_hot(preamble, sections), encoding="utf-8")
    return layout_hot_path


def _append_log(log_path: Path, payload: dict[str, object]) -> Path:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        current = log_path.read_text(encoding="utf-8").rstrip()
    else:
        current = _log_template(log_path.parent.parent if log_path.parent.name in {"content", "wiki"} else log_path.parent).rstrip()

    timestamp = _utc_now_iso()
    pages_created = _normalize_string_list(payload.get("pages_created"))
    pages_updated = _normalize_string_list(payload.get("pages_updated"))
    contradictions = _normalize_contradictions(payload.get("contradictions"))
    source_type = payload.get("source_type") if isinstance(payload.get("source_type"), str) else "document"
    links_woven = payload.get("links_woven")
    links_woven_value = str(links_woven).strip() if links_woven is not None else "0"
    lines = [
        (
            f'- [{timestamp}] INGEST source="{payload["source_path"]}" '
            f"pages_updated={len(pages_updated)} pages_created={len(pages_created)} "
            f"contradictions={len(contradictions)} links_woven={links_woven_value} source_type={source_type}"
        )
    ]
    for detail in _normalize_string_list(payload.get("log_details")):
        lines.append(f"  - {detail}")

    new_block = "\n".join(lines)
    if current:
        rendered = current + "\n\n---\n\n" + new_block + "\n"
    else:
        rendered = new_block + "\n"
    log_path.write_text(rendered, encoding="utf-8")
    return log_path


def _update_manifest(repo_root: Path, layout_page_root: Path, payload: dict[str, object]) -> Path:
    manifest_path = repo_root / ".manifest.json"
    if manifest_path.exists():
        try:
            manifest_raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest_raw = {}
    else:
        manifest_raw = {}

    manifest = manifest_raw if isinstance(manifest_raw, dict) else {}
    sources = manifest.get("sources") if isinstance(manifest.get("sources"), dict) else {}
    sources = cast(dict[str, object], sources)

    raw_path = repo_root / str(payload["source_path"])
    stat = raw_path.stat()
    entry = {
        "ingested_at": _utc_now_iso(),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "content_hash": payload["content_hash"],
        "source_type": payload.get("source_type") if isinstance(payload.get("source_type"), str) else "document",
        "project": payload.get("project") if isinstance(payload.get("project"), str) else None,
        "pages_created": _normalize_string_list(payload.get("pages_created")),
        "pages_updated": _normalize_string_list(payload.get("pages_updated")),
    }
    sources[str(payload["source_path"])] = entry
    manifest["version"] = 1
    manifest["sources"] = sources
    manifest["stats"] = {
        "total_sources_ingested": len(sources),
        "total_pages": len(build_page_inventory(repo_root)),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def finalize_ingest(repo_root: Path, payload_path: Path) -> dict[str, object]:
    payload = _read_json(payload_path)
    source_path = payload.get("source_path")
    content_hash = payload.get("content_hash")
    if not isinstance(source_path, str) or not source_path.strip():
        raise ValueError("finalize payload requires source_path")
    if not isinstance(content_hash, str) or not content_hash.strip():
        raise ValueError("finalize payload requires content_hash")

    layout = detect_knowledge_layout(repo_root)
    if layout is None:
        raise ValueError("unable to detect knowledge layout")

    manifest_path = _update_manifest(repo_root, layout.page_root, payload)
    log_path = _append_log(layout.log_path, payload)
    hot_path = _update_hot(layout.hot_path, payload)

    return {
        "source_path": source_path,
        "knowledge_root": layout.page_root.relative_to(repo_root).as_posix() if layout.page_root != repo_root else ".",
        "manifest_path": manifest_path.relative_to(repo_root).as_posix(),
        "log_path": log_path.relative_to(repo_root).as_posix(),
        "hot_path": hot_path.relative_to(repo_root).as_posix(),
        "pages_created": len(_normalize_string_list(payload.get("pages_created"))),
        "pages_updated": len(_normalize_string_list(payload.get("pages_updated"))),
        "contradictions": len(_normalize_contradictions(payload.get("contradictions"))),
    }