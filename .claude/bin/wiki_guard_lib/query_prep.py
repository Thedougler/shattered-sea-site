from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import field as dataclass_field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from .inventory import build_page_inventory, read_index_entries
from .knowledge_layout import detect_knowledge_layout
from .models import QueryPrepCandidate, QueryPrepResult
from .utils import strip_frontmatter

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


def _normalize_source_count(value: object) -> int:
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed.isdigit():
            return int(trimmed)
    return 0


def _normalize_source_refs(values: object) -> list[str]:
    refs = _normalize_list(values)
    return refs[:8]


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

    lines = strip_frontmatter(body).splitlines()
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

    source_count = _normalize_source_count(frontmatter.get("source_count"))
    source_refs = _normalize_source_refs(frontmatter.get("sources"))

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
        source_count=source_count,
        source_refs=source_refs,
        status=status,
        visibility=visibility,
        tags=tags,
        aliases=aliases,
        outbound_links=links,
        snippets=snippets,
    )


def _compute_read_strategy(candidate: QueryPrepCandidate) -> str:
    """Recommend the cheapest read primitive that can answer a query for this page.

    summary_only — summary field is rich (≥60 chars) and no keyword snippets were found;
                   the summary alone should be sufficient for shallow/factual queries.
    grep         — keyword snippets were extracted; grep around those terms for context.
    full_read    — no snippets and summary is thin (<60 chars), or QMD score is high
                   but wiki_guard score is low (semantic match without keyword overlap).
    """
    has_snippets = bool(candidate.snippets) or bool(candidate.qmd_snippets)
    rich_summary = len(candidate.summary) >= 60
    # QMD found it semantically but no keyword overlap → likely needs full read
    qmd_only = candidate.qmd_score > 0.6 and candidate.score < 4
    if has_snippets:
        return "grep"
    if rich_summary and not qmd_only:
        return "summary_only"
    return "full_read"


def _slug_from_rel_path(rel_path: str) -> str:
    """Derive a slug from a relative path like 'content/entities/foo_bar.md' → 'foo_bar'."""
    stem = Path(rel_path).stem
    return stem.lower().replace("-", "_")


def merge_qmd_results(
    candidates: list[QueryPrepCandidate],
    qmd_data: list[dict[str, Any]],
    *,
    inventory: dict[str, Any],
    index_entries: dict[str, str],
    question_tokens: list[str],
) -> list[QueryPrepCandidate]:
    """Merge QMD semantic search results into the wiki_guard candidate list.

    qmd_data entries: {"rel_path": str, "score": float (0.0–1.0), "snippet": str (optional)}

    For existing candidates: boost score by int(qmd_score * 15), attach qmd_snippet.
    For new candidates (in QMD but not wiki_guard): add with score = int(qmd_score * 10),
    reason="qmd_semantic", sourcing metadata from inventory if available.
    """
    by_slug: dict[str, QueryPrepCandidate] = {c.slug: c for c in candidates}
    existing_paths: dict[str, str] = {c.rel_path: c.slug for c in candidates}

    for entry in qmd_data:
        rel_path = entry.get("rel_path", "")
        if not rel_path:
            continue
        raw_score = entry.get("score", 0.0)
        try:
            qmd_score = max(0.0, min(1.0, float(raw_score)))
        except (TypeError, ValueError):
            qmd_score = 0.0
        qmd_snippet: str = entry.get("snippet", "")

        # Match by rel_path first, then by derived slug
        slug = existing_paths.get(rel_path) or _slug_from_rel_path(rel_path)

        if slug in by_slug:
            c = by_slug[slug]
            boost = int(qmd_score * 15)
            c.score += boost
            c.qmd_score = qmd_score
            if qmd_snippet and qmd_snippet not in c.qmd_snippets:
                c.qmd_snippets.append(qmd_snippet)
            if "qmd_semantic" not in c.match_reasons:
                c.match_reasons.append(f"qmd:{qmd_score:.2f}")
        else:
            # New candidate from QMD not found by keyword scoring
            info = inventory.get(slug, {})
            frontmatter: dict[str, object] = {}
            fm_value = info.get("frontmatter")
            if isinstance(fm_value, dict):
                frontmatter = cast(dict[str, object], fm_value)

            summary_raw = frontmatter.get("summary")
            summary = summary_raw.strip() if isinstance(summary_raw, str) else ""
            tags = _normalize_list(frontmatter.get("tags"))
            aliases = _normalize_list(frontmatter.get("aliases"))
            source_count = _normalize_source_count(frontmatter.get("source_count"))
            source_refs = _normalize_source_refs(frontmatter.get("sources"))
            status_raw = frontmatter.get("status")
            status = status_raw.strip() if isinstance(status_raw, str) else "unknown"
            visibility_raw = frontmatter.get("visibility")
            visibility = visibility_raw.strip() if isinstance(visibility_raw, str) else "unknown"
            links_value = info.get("links")
            links: list[str] = []
            if isinstance(links_value, list):
                for t in cast(list[object], links_value):
                    if isinstance(t, str):
                        links.append(t)

            new_candidate = QueryPrepCandidate(
                slug=slug,
                rel_path=rel_path,
                score=int(qmd_score * 10),
                match_reasons=[f"qmd:{qmd_score:.2f}"],
                summary=summary or index_entries.get(slug, ""),
                source_count=source_count,
                source_refs=source_refs,
                status=status,
                visibility=visibility,
                tags=tags,
                aliases=aliases,
                outbound_links=links,
                snippets=[],
                qmd_score=qmd_score,
                qmd_snippets=[qmd_snippet] if qmd_snippet else [],
            )
            by_slug[slug] = new_candidate

    merged = sorted(by_slug.values(), key=lambda c: (-c.score, c.slug))
    return merged


def gather_query_prep(
    repo_root: Path,
    *,
    question: str,
    top_k: int = 5,
    fast_mode: bool = False,
    public_only: bool = False,
    snippet_context: int = 2,
    max_snippets: int = 2,
    qmd_data: list[dict[str, Any]] | None = None,
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

    # Merge QMD semantic results if provided, then re-slice primary/secondary
    qmd_merged = False
    if qmd_data:
        all_merged = merge_qmd_results(
            ranked,
            qmd_data,
            inventory=pages,
            index_entries=index_entries,
            question_tokens=question_tokens,
        )
        primary = all_merged[:capped_top_k]
        primary_slugs = {c.slug for c in primary}
        # Rebuild secondary from merged list
        secondary_counts2: Counter[str] = Counter()
        by_slug2 = {c.slug: c for c in all_merged}
        for candidate in primary:
            for target in candidate.outbound_links:
                if target in primary_slugs:
                    continue
                if target in by_slug2:
                    secondary_counts2[target] += 1
        secondary_ranked2 = sorted(
            secondary_counts2.items(),
            key=lambda entry: (-entry[1], -by_slug2[entry[0]].score, entry[0]),
        )
        secondary = [by_slug2[s] for s, _ in secondary_ranked2[:capped_top_k]]
        qmd_merged = True

    # Compute per-candidate read strategy
    for candidate in primary:
        candidate.read_strategy = _compute_read_strategy(candidate)
    for candidate in secondary:
        candidate.read_strategy = _compute_read_strategy(candidate)

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
        qmd_merged=qmd_merged,
    )


def _candidate_to_dict(candidate: QueryPrepCandidate) -> dict[str, Any]:
    return {
        "slug": candidate.slug,
        "rel_path": candidate.rel_path,
        "score": candidate.score,
        "match_reasons": candidate.match_reasons,
        "summary": candidate.summary,
        "source_count": candidate.source_count,
        "source_refs": candidate.source_refs,
        "status": candidate.status,
        "visibility": candidate.visibility,
        "tags": candidate.tags,
        "aliases": candidate.aliases,
        "outbound_links": candidate.outbound_links,
        "snippets": candidate.snippets,
        "qmd_score": candidate.qmd_score,
        "qmd_snippets": candidate.qmd_snippets,
        "read_strategy": candidate.read_strategy,
    }


def render_query_prep_json(result: QueryPrepResult) -> str:
    payload: dict[str, Any] = {
        "question": result.question,
        "query_type": result.query_type,
        "mode": result.mode,
        "filtered": result.filtered,
        "top_k": result.top_k,
        "qmd_merged": result.qmd_merged,
        "excluded_internal_count": result.excluded_internal_count,
        "primary": [
            _candidate_to_dict(candidate)
            for candidate in result.primary
        ],
        "secondary": [
            _candidate_to_dict(candidate)
            for candidate in result.secondary
        ],
    }
    return json.dumps(payload, indent=2)


def render_query_prep_text(result: QueryPrepResult) -> str:
    qmd_flag = " qmd_merged=yes" if result.qmd_merged else ""
    lines = [
        "query prep",
        f"- query: {result.question}",
        f"- type: {result.query_type}",
        f"- mode: {result.mode}{qmd_flag}",
        f"- filtered: {'yes' if result.filtered else 'no'}",
        f"- excluded internal pages: {result.excluded_internal_count}",
        "",
        f"primary pages ({len(result.primary)}):",
    ]

    for item in result.primary:
        reasons = ", ".join(item.match_reasons) if item.match_reasons else "none"
        lines.append(
            f"- [[{item.slug}]] score={item.score} read={item.read_strategy} "
            f"status={item.status} via={reasons}"
        )
        if item.summary:
            lines.append(f"  summary: {item.summary}")
        if item.source_count > 0:
            lines.append(f"  source_count: {item.source_count}")
        if item.source_refs:
            lines.append(f"  sources: {', '.join(item.source_refs)}")
        for snippet in item.snippets:
            lines.append("  snippet:")
            for snippet_line in snippet.splitlines():
                lines.append(f"    {snippet_line}")
        for snippet in item.qmd_snippets:
            lines.append("  qmd_snippet:")
            for snippet_line in snippet.splitlines():
                lines.append(f"    {snippet_line}")

    lines.append("")
    lines.append(f"secondary pages ({len(result.secondary)}):")
    for item in result.secondary:
        lines.append(f"- [[{item.slug}]] score={item.score} read={item.read_strategy}")

    lines.append("")
    lines.append("suggested read order:")
    for item in result.primary:
        lines.append(f"- {item.rel_path}  # read={item.read_strategy}")

    return "\n".join(lines)


def print_query_prep(result: QueryPrepResult, output_format: str) -> None:
    if output_format == "json":
        print(render_query_prep_json(result))
        return
    print(render_query_prep_text(result))


def normalize_query_log_mode(mode: str) -> str:
    if mode.startswith("filtered"):
        return "filtered"
    if mode == "index_only":
        return "index_only"
    return "normal"


def append_query_log(
    repo_root: Path,
    *,
    question: str,
    result_pages: int,
    mode: str,
    escalated: bool,
) -> Path | None:
    layout = detect_knowledge_layout(repo_root)
    if layout is None:
        return None

    log_path = layout.log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    normalized_mode = normalize_query_log_mode(mode)
    escaped_question = question.replace('"', "\\\"")
    line = (
        f'- [{timestamp}] QUERY query="{escaped_question}" '
        f"result_pages={max(0, result_pages)} mode={normalized_mode} "
        f"escalated={'true' if escalated else 'false'}"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return log_path


def append_filed_log(
    repo_root: Path,
    *,
    page: str,
    from_query: str,
) -> Path | None:
    """Append a FILED entry to the knowledge log for a synthesis page written back to the wiki."""
    layout = detect_knowledge_layout(repo_root)
    if layout is None:
        return None

    log_path = layout.log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    escaped_page = page.replace('"', "\\\"")
    escaped_query = from_query.replace('"', "\\\"")
    line = f'- [{timestamp}] FILED page="{escaped_page}" from_query="{escaped_query}"'
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return log_path
