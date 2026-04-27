from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, cast

from .inventory import build_page_inventory, read_index_entries
from .models import QueryPrepCandidate, QueryPrepResult

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "do",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}


def _tokenize(value: str) -> list[str]:
    return [token for token in _TOKEN_RE.findall(value.lower()) if token not in _STOPWORDS]


def _normalize_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for item in cast(list[object], values):
        if isinstance(item, str):
            trimmed = item.strip()
            if trimmed:
                out.append(trimmed)
    return out


def _detect_query_type(question: str) -> str:
    lowered = question.lower()
    if any(term in lowered for term in ("compare", "versus", "vs", "difference")):
        return "comparative"
    if any(term in lowered for term in ("contradict", "conflict", "inconsistent")):
        return "contradiction_scan"
    if any(term in lowered for term in ("summarize", "synthesis", "connect", "relationship")):
        return "synthesis"
    if any(term in lowered for term in ("lint", "health", "status", "coverage")):
        return "meta"
    return "factual"


def _extract_snippets(body: str, terms: list[str], *, context: int, max_snippets: int) -> list[str]:
    if not terms:
        return []

    lines = body.splitlines()
    matched_indices: list[int] = []
    lowered_terms = [term.lower() for term in terms]
    for idx, line in enumerate(lines):
        lowered_line = line.lower()
        if any(term in lowered_line for term in lowered_terms):
            matched_indices.append(idx)

    if not matched_indices:
        return []

    snippets: list[str] = []
    used_ranges: list[tuple[int, int]] = []
    for idx in matched_indices:
        start = max(0, idx - context)
        end = min(len(lines), idx + context + 1)

        overlaps = False
        for used_start, used_end in used_ranges:
            if not (end <= used_start or start >= used_end):
                overlaps = True
                break
        if overlaps:
            continue

        chunk = "\n".join(lines[start:end]).strip()
        if chunk:
            snippets.append(chunk)
            used_ranges.append((start, end))

        if len(snippets) >= max_snippets:
            break

    return snippets


def _score_candidate(
    *,
    slug: str,
    question_tokens: list[str],
    summary: str,
    index_summary: str,
    aliases: list[str],
    tags: list[str],
) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    slug_tokens = set(_tokenize(slug.replace("_", " ")))
    shared_slug = [token for token in question_tokens if token in slug_tokens]
    if shared_slug:
        boost = min(14, 8 + len(shared_slug) * 2)
        score += boost
        reasons.append(f"slug:{','.join(sorted(set(shared_slug)))}")

    alias_tokens: set[str] = set()
    for alias in aliases:
        alias_tokens.update(_tokenize(alias))
    shared_aliases = [token for token in question_tokens if token in alias_tokens]
    if shared_aliases:
        boost = min(12, 6 + len(shared_aliases) * 2)
        score += boost
        reasons.append(f"alias:{','.join(sorted(set(shared_aliases)))}")

    tag_tokens: set[str] = set()
    for tag in tags:
        tag_tokens.update(_tokenize(tag.replace("/", " ")))
    shared_tags = [token for token in question_tokens if token in tag_tokens]
    if shared_tags:
        boost = min(8, len(shared_tags) * 2)
        score += boost
        reasons.append(f"tag:{','.join(sorted(set(shared_tags)))}")

    summary_text = f"{summary} {index_summary}".lower()
    shared_summary = [token for token in question_tokens if token in summary_text]
    if shared_summary:
        boost = min(8, len(shared_summary))
        score += boost
        reasons.append(f"summary:{','.join(sorted(set(shared_summary)))}")

    return score, reasons


def _is_blocked_visibility(tags: list[str], public_only: bool) -> bool:
    if not public_only:
        return False
    return any(tag in {"visibility/internal", "visibility/pii"} for tag in tags)


def _build_candidate(
    *,
    slug: str,
    info: dict[str, object],
    index_summary: str,
    question_tokens: list[str],
    fast_mode: bool,
    snippet_context: int,
    max_snippets: int,
) -> QueryPrepCandidate | None:
    frontmatter_value = info.get("frontmatter")
    frontmatter: dict[str, object]
    if isinstance(frontmatter_value, dict):
        frontmatter = cast(dict[str, object], frontmatter_value)
    else:
        frontmatter = {}

    summary_raw = frontmatter.get("summary")
    summary = summary_raw.strip() if isinstance(summary_raw, str) else ""
    aliases = _normalize_list(frontmatter.get("aliases"))
    tags = _normalize_list(frontmatter.get("tags"))

    score, reasons = _score_candidate(
        slug=slug,
        question_tokens=question_tokens,
        summary=summary,
        index_summary=index_summary,
        aliases=aliases,
        tags=tags,
    )
    if score <= 0:
        return None

    status_raw = frontmatter.get("status")
    status = status_raw.strip() if isinstance(status_raw, str) else "unknown"
    visibility_raw = frontmatter.get("visibility")
    visibility = visibility_raw.strip() if isinstance(visibility_raw, str) else "unknown"

    text = info.get("text")
    rel_path = info.get("rel_path")
    links_value = info.get("links")
    if not isinstance(text, str):
        text = ""
    if not isinstance(rel_path, str):
        rel_path = ""
    links: list[str] = []
    if isinstance(links_value, list):
        for target in cast(list[object], links_value):
            if isinstance(target, str):
                links.append(target)

    snippets = []
    if not fast_mode:
        snippets = _extract_snippets(
            text,
            question_tokens,
            context=max(0, snippet_context),
            max_snippets=max(1, max_snippets),
        )

    return QueryPrepCandidate(
        slug=slug,
        rel_path=rel_path,
        score=score,
        match_reasons=reasons,
        summary=summary or index_summary,
        status=status,
        visibility=visibility,
        tags=tags,
        aliases=aliases,
        outbound_links=links,
        snippets=snippets,
    )


def gather_query_prep(
    repo_root: Path,
    *,
    question: str,
    top_k: int = 5,
    fast_mode: bool = False,
    public_only: bool = False,
    snippet_context: int = 2,
    max_snippets: int = 2,
) -> QueryPrepResult:
    pages = build_page_inventory(repo_root)
    index_entries = read_index_entries(repo_root)
    question_tokens = _tokenize(question)
    query_type = _detect_query_type(question)

    ranked: list[QueryPrepCandidate] = []
    excluded_internal_count = 0
    capped_top_k = max(1, top_k)

    for slug, info in pages.items():
        frontmatter_value = info.get("frontmatter")
        frontmatter: dict[str, object]
        if isinstance(frontmatter_value, dict):
            frontmatter = cast(dict[str, object], frontmatter_value)
        else:
            frontmatter = {}
        tags = _normalize_list(frontmatter.get("tags"))
        if _is_blocked_visibility(tags, public_only):
            excluded_internal_count += 1
            continue

        candidate = _build_candidate(
            slug=slug,
            info=info,
            index_summary=index_entries.get(slug, ""),
            question_tokens=question_tokens,
            fast_mode=fast_mode,
            snippet_context=snippet_context,
            max_snippets=max_snippets,
        )
        if candidate is not None:
            ranked.append(candidate)

    ranked.sort(key=lambda item: (-item.score, item.slug))
    primary = ranked[:capped_top_k]
    primary_slugs = {item.slug for item in primary}

    secondary_counts: Counter[str] = Counter()
    by_slug = {item.slug: item for item in ranked}
    for candidate in primary:
        for target in candidate.outbound_links:
            if target in primary_slugs:
                continue
            if target in by_slug:
                secondary_counts[target] += 1

    secondary_ranked = sorted(
        secondary_counts.items(),
        key=lambda entry: (-entry[1], -by_slug[entry[0]].score, entry[0]),
    )
    secondary = [by_slug[slug] for slug, _ in secondary_ranked[:capped_top_k]]

    mode = "index_only" if fast_mode else "normal"
    if public_only:
        mode = "filtered" if mode == "normal" else "filtered_index_only"

    return QueryPrepResult(
        question=question,
        query_type=query_type,
        mode=mode,
        filtered=public_only,
        top_k=capped_top_k,
        primary=primary,
        secondary=secondary,
        excluded_internal_count=excluded_internal_count,
    )


def render_query_prep_json(result: QueryPrepResult) -> str:
    payload: dict[str, Any] = {
        "question": result.question,
        "query_type": result.query_type,
        "mode": result.mode,
        "filtered": result.filtered,
        "top_k": result.top_k,
        "excluded_internal_count": result.excluded_internal_count,
        "primary": [
            {
                "slug": candidate.slug,
                "rel_path": candidate.rel_path,
                "score": candidate.score,
                "match_reasons": candidate.match_reasons,
                "summary": candidate.summary,
                "status": candidate.status,
                "visibility": candidate.visibility,
                "tags": candidate.tags,
                "aliases": candidate.aliases,
                "outbound_links": candidate.outbound_links,
                "snippets": candidate.snippets,
            }
            for candidate in result.primary
        ],
        "secondary": [
            {
                "slug": candidate.slug,
                "rel_path": candidate.rel_path,
                "score": candidate.score,
                "match_reasons": candidate.match_reasons,
                "summary": candidate.summary,
                "status": candidate.status,
                "visibility": candidate.visibility,
                "tags": candidate.tags,
                "aliases": candidate.aliases,
                "outbound_links": candidate.outbound_links,
                "snippets": candidate.snippets,
            }
            for candidate in result.secondary
        ],
    }
    return json.dumps(payload, indent=2)


def render_query_prep_text(result: QueryPrepResult) -> str:
    lines = [
        "query prep",
        f"- query: {result.question}",
        f"- type: {result.query_type}",
        f"- mode: {result.mode}",
        f"- filtered: {'yes' if result.filtered else 'no'}",
        f"- excluded internal pages: {result.excluded_internal_count}",
        "",
        f"primary pages ({len(result.primary)}):",
    ]

    for item in result.primary:
        reasons = ", ".join(item.match_reasons) if item.match_reasons else "none"
        lines.append(
            f"- [[{item.slug}]] score={item.score} status={item.status} "
            f"visibility={item.visibility} via={reasons}"
        )
        if item.summary:
            lines.append(f"  summary: {item.summary}")
        for snippet in item.snippets:
            lines.append("  snippet:")
            for snippet_line in snippet.splitlines():
                lines.append(f"    {snippet_line}")

    lines.append("")
    lines.append(f"secondary pages ({len(result.secondary)}):")
    for item in result.secondary:
        lines.append(f"- [[{item.slug}]] score={item.score}")

    lines.append("")
    lines.append("suggested read order:")
    for item in result.primary:
        lines.append(f"- {item.rel_path}")

    return "\n".join(lines)


def print_query_prep(result: QueryPrepResult, output_format: str) -> None:
    if output_format == "json":
        print(render_query_prep_json(result))
        return
    print(render_query_prep_text(result))
