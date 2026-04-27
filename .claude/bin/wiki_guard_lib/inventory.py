from __future__ import annotations

from datetime import date
from pathlib import Path

from .constants import INDEX_ROW_RE, INGEST_TIMESTAMP_RE, WIKILINK_RE
from .knowledge_layout import detect_knowledge_layout
from .utils import levenshtein_distance, parse_frontmatter, parse_iso_date


def _is_template_page(path: Path, page_root: Path) -> bool:
    parts = path.relative_to(page_root).parts
    return any(part in {"templates", "_templates"} for part in parts)


def _normalize_wikilink_target(target: str) -> str:
    normalized = target.strip()
    if normalized.endswith("\\"):
        normalized = normalized[:-1]
    return normalized


def read_index_entries(repo_root: Path) -> dict[str, str]:
    layout = detect_knowledge_layout(repo_root)
    if layout is None or not layout.index_path.exists():
        return {}

    entries: dict[str, str] = {}
    for line in layout.index_path.read_text(encoding="utf-8").splitlines():
        match = INDEX_ROW_RE.match(line)
        if not match:
            continue
        slug = match.group(1)
        summary = match.group(2).strip()
        entries[slug] = summary
    return entries


def build_page_inventory(repo_root: Path) -> dict[str, dict[str, object]]:
    layout = detect_knowledge_layout(repo_root)
    pages: dict[str, dict[str, object]] = {}
    if layout is None or not layout.page_root.exists():
        return pages

    root_special_files = {"index.md", "hot.md", "log.md"}

    for path in sorted(layout.page_root.rglob("*.md")):
        if path.parent == layout.page_root and path.name in root_special_files:
            continue
        if _is_template_page(path, layout.page_root):
            continue

        slug = path.stem
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text) or {}
        links: list[str] = []
        for link in WIKILINK_RE.findall(text):
            target = _normalize_wikilink_target(link.split("/")[-1])
            if target:
                links.append(target)

        pages[slug] = {
            "path": path,
            "rel_path": path.relative_to(repo_root).as_posix(),
            "text": text,
            "frontmatter": frontmatter,
            "links": links,
        }
    return pages


def classify_dead_link(target: str, known_slugs: set[str]) -> tuple[str, str | None]:
    best: tuple[int, str] | None = None
    for slug in known_slugs:
        dist = levenshtein_distance(target, slug)
        if best is None or dist < best[0]:
            best = (dist, slug)
    if best is not None and best[0] <= 2:
        return ("typo_likely", best[1])
    return ("stub_worthy", None)


def collect_ingestion_dates(log_text: str) -> list[date]:
    dates: list[date] = []
    for line in log_text.splitlines():
        if "INGEST" not in line:
            continue
        match = INGEST_TIMESTAMP_RE.search(line)
        if not match:
            continue
        parsed = parse_iso_date(match.group(1))
        if parsed is not None:
            dates.append(parsed)
    return sorted(dates)


def suggest_related_pages(links: list[str], current_slug: str, limit: int = 3) -> list[str]:
    out: list[str] = []
    for slug in links:
        if slug == current_slug or slug in out:
            continue
        out.append(slug)
        if len(out) >= limit:
            break
    return out
