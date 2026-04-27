from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from .inventory import build_page_inventory
from .knowledge_layout import detect_knowledge_layout


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_payloads(raw_payload: object) -> list[dict[str, object]]:
    if isinstance(raw_payload, list):
        payloads = raw_payload
    elif isinstance(raw_payload, dict):
        entries = raw_payload.get("entries")
        if isinstance(entries, list):
            payloads = entries
        else:
            payloads = [raw_payload]
    else:
        raise ValueError("finalize payload must be a JSON object or list")

    normalized: list[dict[str, object]] = []
    for payload in payloads:
        if not isinstance(payload, dict):
            raise ValueError("finalize payload entries must be JSON objects")
        normalized.append(cast(dict[str, object], payload))
    return normalized


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


def _payload_matches_manifest_entry(entry: object, payload: dict[str, object]) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("content_hash") != payload.get("content_hash"):
        return False
    if entry.get("source_type", "document") != (
        payload.get("source_type") if isinstance(payload.get("source_type"), str) else "document"
    ):
        return False
    if entry.get("project") != (
        payload.get("project") if isinstance(payload.get("project"), str) else None
    ):
        return False
    if _normalize_string_list(entry.get("pages_created")) != _normalize_string_list(payload.get("pages_created")):
        return False
    if _normalize_string_list(entry.get("pages_updated")) != _normalize_string_list(payload.get("pages_updated")):
        return False
    return True


def _load_manifest_entry(repo_root: Path, source_path: str) -> object:
    manifest_path = repo_root / ".manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(manifest, dict):
        return None
    sources = manifest.get("sources")
    if not isinstance(sources, dict):
        return None
    return sources.get(source_path)


def _finalize_single_ingest(repo_root: Path, layout: Any, payload: dict[str, object]) -> dict[str, object]:
    source_path = payload.get("source_path")
    content_hash = payload.get("content_hash")
    if not isinstance(source_path, str) or not source_path.strip():
        raise ValueError("finalize payload requires source_path")
    if not isinstance(content_hash, str) or not content_hash.strip():
        raise ValueError("finalize payload requires content_hash")

    existing_entry = _load_manifest_entry(repo_root, source_path)
    if _payload_matches_manifest_entry(existing_entry, payload):
        return {
            "source_path": source_path,
            "knowledge_root": layout.page_root.relative_to(repo_root).as_posix() if layout.page_root != repo_root else ".",
            "manifest_path": (repo_root / ".manifest.json").relative_to(repo_root).as_posix(),
            "log_path": layout.log_path.relative_to(repo_root).as_posix(),
            "hot_path": layout.hot_path.relative_to(repo_root).as_posix(),
            "pages_created": len(_normalize_string_list(payload.get("pages_created"))),
            "pages_updated": len(_normalize_string_list(payload.get("pages_updated"))),
            "contradictions": len(_normalize_contradictions(payload.get("contradictions"))),
            "applied": False,
        }

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
        "applied": True,
    }


def finalize_runner_dir(repo_root: Path, checkpoint_dir: Path) -> dict[str, object]:
    """Discover completed finalize stubs in checkpoint_dir and process them in one pass.

    A stub is considered complete when it exists on disk and contains a non-empty JSON
    object with a ``source_path`` key.  Empty stubs (not yet written by the agent) and
    stubs that do not match that shape are silently skipped so this command is safe to
    call after each step without waiting for the full batch to finish.
    """
    if not checkpoint_dir.exists():
        return {
            "ok": False,
            "error": f"checkpoint directory not found: {checkpoint_dir}",
            "files_found": 0,
            "files_finalized": 0,
        }

    stub_paths = sorted(checkpoint_dir.glob("*_finalize.json"))
    payloads: list[dict[str, object]] = []
    skipped: list[str] = []
    for stub in stub_paths:
        try:
            raw_text = stub.read_text(encoding="utf-8").strip()
            if not raw_text:
                skipped.append(stub.name)
                continue
            raw = json.loads(raw_text)
            if isinstance(raw, list):
                for entry in raw:
                    if isinstance(entry, dict) and entry.get("source_path"):
                        payloads.append(entry)
            elif isinstance(raw, dict):
                entries = raw.get("entries")
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, dict) and entry.get("source_path"):
                            payloads.append(entry)
                elif raw.get("source_path"):
                    payloads.append(raw)
                else:
                    skipped.append(stub.name)
            else:
                skipped.append(stub.name)
        except (json.JSONDecodeError, OSError):
            skipped.append(stub.name)

    if not payloads:
        return {
            "ok": True,
            "message": "no completed finalize stubs found",
            "checkpoint_dir": checkpoint_dir.relative_to(repo_root).as_posix(),
            "files_found": len(stub_paths),
            "files_finalized": 0,
            "skipped": skipped,
        }

    combined_path = checkpoint_dir / "_combined_finalize.json"
    combined_path.write_text(json.dumps({"entries": payloads}, indent=2) + "\n", encoding="utf-8")
    result = finalize_ingest(repo_root, combined_path)
    result["ok"] = True
    result["checkpoint_dir"] = checkpoint_dir.relative_to(repo_root).as_posix()
    result["files_found"] = len(stub_paths)
    result["files_finalized"] = len(payloads)
    result["skipped"] = skipped
    return result


def finalize_ingest(repo_root: Path, payload_path: Path) -> dict[str, object]:
    payloads = _normalize_payloads(_read_json(payload_path))

    layout = detect_knowledge_layout(repo_root)
    if layout is None:
        raise ValueError("unable to detect knowledge layout")

    results = [_finalize_single_ingest(repo_root, layout, payload) for payload in payloads]
    applied = [result for result in results if result["applied"] is True]

    return {
        "source_path": results[0]["source_path"] if len(results) == 1 else None,
        "source_paths": [result["source_path"] for result in results],
        "mode": "single" if len(results) == 1 else "batch",
        "sources_processed": len(results),
        "sources_applied": len(applied),
        "sources_skipped": len(results) - len(applied),
        "knowledge_root": layout.page_root.relative_to(repo_root).as_posix() if layout.page_root != repo_root else ".",
        "manifest_path": (repo_root / ".manifest.json").relative_to(repo_root).as_posix(),
        "log_path": layout.log_path.relative_to(repo_root).as_posix(),
        "hot_path": layout.hot_path.relative_to(repo_root).as_posix(),
        "pages_created": sum(cast(int, result["pages_created"]) for result in results),
        "pages_updated": sum(cast(int, result["pages_updated"]) for result in results),
        "contradictions": sum(cast(int, result["contradictions"]) for result in results),
    }