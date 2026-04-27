from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path

from .constants import WIKILINK_RE
from .models import SynthesisCandidate, SynthesisReport
from .utils import parse_frontmatter

_SPECIAL_FILENAMES = {"index.md", "log.md", "hot.md", "_insights.md"}
_SKIP_PARTS = {"_meta", "_archives", "_raw", "raw"}


@dataclass
class _PageInfo:
    slug: str
    rel_path: str
    category: str
    tags: set[str]
    summary: str
    status: str
    links: set[str]
    is_synthesis: bool


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


def _resolve_vault_root(repo_root: Path) -> Path:
    env_map = _load_env_map(repo_root)
    raw = env_map.get("OBSIDIAN_VAULT_PATH")
    if not raw:
        return repo_root
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate
    return (repo_root / candidate).resolve()


def _iter_markdown_pages(vault_root: Path) -> list[Path]:
    pages: list[Path] = []
    for path in sorted(vault_root.rglob("*.md")):
        rel = path.relative_to(vault_root)
        if path.name in _SPECIAL_FILENAMES:
            continue
        if any(part in _SKIP_PARTS for part in rel.parts):
            continue
        pages.append(path)
    return pages


def _extract_links(text: str) -> set[str]:
    out: set[str] = set()
    for match in WIKILINK_RE.findall(text):
        slug = match.split("/")[-1].strip()
        if slug:
            out.add(slug)
    return out


def _collect_pages(vault_root: Path) -> dict[str, _PageInfo]:
    pages: dict[str, _PageInfo] = {}
    for path in _iter_markdown_pages(vault_root):
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text) or {}
        rel = path.relative_to(vault_root).as_posix()
        rel_parts = rel.split("/")
        category = str(frontmatter.get("category", rel_parts[0] if len(rel_parts) > 1 else "root"))
        tags_value = frontmatter.get("tags")
        tags = {str(item) for item in tags_value} if isinstance(tags_value, list) else set()

        is_synthesis = (
            rel.startswith("wiki/synthesis/")
            or rel.startswith("synthesis/")
            or category == "synthesis"
        )
        pages[path.stem] = _PageInfo(
            slug=path.stem,
            rel_path=rel,
            category=category,
            tags=tags,
            summary=str(frontmatter.get("summary", "")),
            status=str(frontmatter.get("status", "")),
            links=_extract_links(text),
            is_synthesis=is_synthesis,
        )
    return pages


def _hub_slugs(vault_root: Path) -> set[str]:
    insights_path = vault_root / "_insights.md"
    if not insights_path.exists():
        return set()
    return _extract_links(insights_path.read_text(encoding="utf-8"))


def _covered_pairs(pages: dict[str, _PageInfo], target_slugs: set[str]) -> set[tuple[str, str]]:
    covered: set[tuple[str, str]] = set()
    for page in pages.values():
        if not page.is_synthesis:
            continue
        linked_targets = sorted(slug for slug in page.links if slug in target_slugs)
        for left, right in combinations(linked_targets, 2):
            covered.add((left, right))
    return covered


def _topic_match(candidate: SynthesisCandidate, pages: dict[str, _PageInfo], topic: str) -> bool:
    if not topic.strip():
        return True
    tokens = [token.lower() for token in topic.split() if token.strip()]
    if not tokens:
        return True

    left_page = pages[candidate.left_slug]
    right_page = pages[candidate.right_slug]
    haystack = " ".join(
        [
            candidate.title,
            left_page.summary,
            right_page.summary,
            " ".join(left_page.tags),
            " ".join(right_page.tags),
            left_page.rel_path,
            right_page.rel_path,
        ]
    ).lower()
    return any(token in haystack for token in tokens)


def _score_pair(
    left: _PageInfo,
    right: _PageInfo,
    shared_by_pages: list[_PageInfo],
    hubs: set[str],
) -> SynthesisCandidate:
    cooccur = len(shared_by_pages)
    score = 0
    if cooccur >= 5:
        score += 3
    elif cooccur >= 3:
        score += 2
    elif cooccur >= 1:
        score += 1

    cross_domain = left.category != right.category
    if cross_domain:
        score += 2

    shared_tags = sorted(left.tags.intersection(right.tags))
    if shared_tags and cross_domain:
        score += 1

    hub_involved = left.slug in hubs or right.slug in hubs
    if hub_involved:
        score += 1

    contradiction_signal = any(
        page.status == "contradictory" or "contradictions" in page.rel_path.lower()
        for page in shared_by_pages
    )
    if contradiction_signal:
        score += 2

    return SynthesisCandidate(
        left_slug=left.slug,
        right_slug=right.slug,
        title=f"{left.slug} × {right.slug}",
        score=score,
        cooccurrence_count=cooccur,
        shared_by_pages=[page.rel_path for page in shared_by_pages],
        cross_domain=cross_domain,
        shared_tags=shared_tags,
        hub_involved=hub_involved,
        contradiction_signal=contradiction_signal,
    )


def gather_synthesis_candidates(
    repo_root: Path,
    *,
    top_pair_limit: int,
    top_candidates: int,
    skipped_limit: int,
    topic_filter: str | None = None,
) -> SynthesisReport:
    vault_root = _resolve_vault_root(repo_root)
    pages = _collect_pages(vault_root)

    target_slugs = {slug for slug, page in pages.items() if not page.is_synthesis}
    hubs = _hub_slugs(vault_root)

    pair_to_sources: dict[tuple[str, str], list[_PageInfo]] = defaultdict(list)
    scanned_sources = 0
    for source_page in pages.values():
        if source_page.is_synthesis:
            continue
        linked_targets = sorted(slug for slug in source_page.links if slug in target_slugs)
        if len(linked_targets) < 2:
            continue
        scanned_sources += 1
        for left, right in combinations(linked_targets, 2):
            pair_to_sources[(left, right)].append(source_page)

    pair_rows = sorted(
        pair_to_sources.items(),
        key=lambda item: (-len(item[1]), item[0][0], item[0][1]),
    )[: max(1, top_pair_limit)]

    covered_pairs = _covered_pairs(pages, target_slugs)

    candidates: list[SynthesisCandidate] = []
    for (left_slug, right_slug), source_pages in pair_rows:
        if (left_slug, right_slug) in covered_pairs:
            continue
        left_page = pages.get(left_slug)
        right_page = pages.get(right_slug)
        if left_page is None or right_page is None:
            continue

        candidate = _score_pair(left_page, right_page, source_pages, hubs)
        if topic_filter and not _topic_match(candidate, pages, topic_filter):
            continue
        candidates.append(candidate)

    ranked = sorted(
        candidates,
        key=lambda item: (
            -item.score,
            -item.cooccurrence_count,
            item.left_slug,
            item.right_slug,
        ),
    )

    top_n = max(1, top_candidates)
    skipped_n = max(0, skipped_limit)

    return SynthesisReport(
        pages_scanned=scanned_sources,
        candidate_pairs_scanned=len(pair_rows),
        covered_pairs=len(covered_pairs),
        topic_filter=topic_filter if topic_filter and topic_filter.strip() else None,
        top_candidates=ranked[:top_n],
        skipped_candidates=ranked[top_n : top_n + skipped_n],
    )


def render_synthesis_report_json(report: SynthesisReport) -> str:
    payload = {
        "overview": {
            "pages_scanned": report.pages_scanned,
            "candidate_pairs_scanned": report.candidate_pairs_scanned,
            "covered_pairs": report.covered_pairs,
            "topic_filter": report.topic_filter,
        },
        "top_candidates": [asdict(item) for item in report.top_candidates],
        "skipped_candidates": [asdict(item) for item in report.skipped_candidates],
    }
    return json.dumps(payload, indent=2)


def render_synthesis_report_text(report: SynthesisReport) -> str:
    lines = [
        "wiki_guard synthesis report",
        "",
        "overview",
        f"- pages scanned: {report.pages_scanned}",
        f"- candidate pairs scanned: {report.candidate_pairs_scanned}",
        f"- covered by existing synthesis: {report.covered_pairs}",
    ]
    if report.topic_filter:
        lines.append(f"- topic filter: {report.topic_filter}")

    lines.extend(["", "top candidates"])
    if not report.top_candidates:
        lines.append("- none")
    for item in report.top_candidates:
        lines.append(
            "- "
            f"[[{item.left_slug}]] × [[{item.right_slug}]]: "
            f"score={item.score}, cooccurs={item.cooccurrence_count}, "
            f"cross_domain={str(item.cross_domain).lower()}, "
            f"hub={str(item.hub_involved).lower()}, "
            f"contradiction={str(item.contradiction_signal).lower()}"
        )

    lines.extend(["", "skipped (consider next time)"])
    if not report.skipped_candidates:
        lines.append("- none")
    for item in report.skipped_candidates:
        lines.append(
            "- "
            f"[[{item.left_slug}]] × [[{item.right_slug}]]: "
            f"score={item.score}, cooccurs={item.cooccurrence_count}"
        )

    return "\n".join(lines)


def print_synthesis_report(report: SynthesisReport, output_format: str) -> None:
    if output_format == "json":
        print(render_synthesis_report_json(report))
        return
    print(render_synthesis_report_text(report))
