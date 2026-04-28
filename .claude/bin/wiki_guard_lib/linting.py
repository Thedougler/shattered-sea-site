from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from .constants import ENTITY_GAP_STOP_TERMS, GAP_NOISE_WORDS, PROPER_NOUN_RE
from .inventory import (
    build_page_inventory,
    classify_dead_link,
    collect_ingestion_dates,
    read_index_entries,
    suggest_related_pages,
)
from .knowledge_layout import detect_knowledge_layout
from .models import (
    ContradictionFinding,
    DeadLinkAggregate,
    DeadLinkFinding,
    EntityGapFinding,
    IndexAuditFinding,
    LintResults,
    OrphanFinding,
    StaleFinding,
)
from .utils import parse_iso_date, strip_frontmatter


def _collect_orphans_and_dead_links(
    pages: dict[str, dict[str, object]],
    page_slugs: set[str],
) -> tuple[list[OrphanFinding], list[DeadLinkFinding]]:
    inbound: dict[str, int] = {slug: 0 for slug in page_slugs}
    dead_map: dict[str, DeadLinkAggregate] = {}

    for source_slug, info in pages.items():
        links = info["links"]
        assert isinstance(links, list)
        for target in links:
            if target in inbound and target != source_slug:
                inbound[target] += 1
            if target in page_slugs:
                continue

            item = dead_map.setdefault(target, DeadLinkAggregate(count=0, sources=set()))
            item.count += 1
            item.sources.add(source_slug)

    orphans: list[OrphanFinding] = []
    for slug in sorted(page_slugs):
        if inbound.get(slug, 0) > 0:
            continue
        page_links = pages[slug]["links"]
        assert isinstance(page_links, list)
        orphans.append(
            OrphanFinding(
                slug=slug,
                inbound_count=0,
                suggested_links_from=suggest_related_pages(page_links, slug),
            )
        )

    dead_links: list[DeadLinkFinding] = []
    for target in sorted(dead_map.keys()):
        item = dead_map[target]
        classification, likely = classify_dead_link(target, page_slugs)
        dead_links.append(
            DeadLinkFinding(
                target=target,
                source_pages=sorted(item.sources),
                count=item.count,
                classification=classification,
                likely_meant=likely,
            )
        )

    return orphans, dead_links


def _collect_stale_and_contradictions(
    pages: dict[str, dict[str, object]],
    page_slugs: set[str],
    ingestion_dates: list[date],
    today: date,
) -> tuple[list[StaleFinding], list[ContradictionFinding]]:
    stale_cutoff = ingestion_dates[-3] if len(ingestion_dates) >= 3 else None
    stale: list[StaleFinding] = []
    contradictions: list[ContradictionFinding] = []

    for slug in sorted(page_slugs):
        frontmatter = pages[slug]["frontmatter"]
        text = pages[slug]["text"]
        assert isinstance(frontmatter, dict)
        assert isinstance(text, str)

        updated_raw = frontmatter.get("updated")
        updated = parse_iso_date(updated_raw if isinstance(updated_raw, str | date) else None)
        source_count_raw = frontmatter.get("source_count")
        source_count = source_count_raw if isinstance(source_count_raw, int) else 0
        status = str(frontmatter.get("status", "")).strip().lower()
        ingestions_since = 0
        if updated is not None:
            ingestions_since = len([d for d in ingestion_dates if d > updated])

        if (
            stale_cutoff is not None
            and updated is not None
            and updated < stale_cutoff
            and source_count == 1
        ):
            stale.append(
                StaleFinding(
                    slug=slug,
                    last_updated=updated.isoformat(),
                    source_count=source_count,
                    ingestions_since_update=ingestions_since,
                    reason="single_source",
                )
            )
        if status == "draft" and updated is not None and (today - updated).days > 30:
            stale.append(
                StaleFinding(
                    slug=slug,
                    last_updated=updated.isoformat(),
                    source_count=source_count,
                    ingestions_since_update=ingestions_since,
                    reason="draft_aged",
                )
            )

        if status == "contradictory":
            conflict = "Contradictions section not found"
            lines = text.splitlines()
            for idx, line in enumerate(lines):
                if line.strip().lower() == "## contradictions":
                    for next_line in lines[idx + 1 :]:
                        value = next_line.strip()
                        if value:
                            conflict = value
                            break
                    break
            open_days = (today - updated).days if updated is not None else 0
            contradictions.append(
                ContradictionFinding(
                    slug=slug,
                    open_since=updated.isoformat() if updated is not None else "unknown",
                    open_days=open_days,
                    conflict=conflict,
                )
            )

    return sorted(stale, key=lambda item: (item.reason, item.slug)), contradictions


def _collect_entity_gaps(
    pages: dict[str, dict[str, object]],
    page_slugs: set[str],
) -> list[EntityGapFinding]:
    slug_tokens = {
        token
        for slug in page_slugs
        for token in slug.split("_")
        if token and token not in {"the", "a", "an"}
    }
    term_pages: dict[str, set[str]] = {}
    for slug, info in pages.items():
        body = strip_frontmatter(str(info["text"]))
        for term in PROPER_NOUN_RE.findall(body):
            if term in ENTITY_GAP_STOP_TERMS:
                continue

            tokens = term.split()
            if not tokens:
                continue
            if len(tokens) == 1 and (tokens[0] in GAP_NOISE_WORDS or len(tokens[0]) <= 2):
                continue
            if all(token in ENTITY_GAP_STOP_TERMS for token in tokens):
                continue
            if all(token in ENTITY_GAP_STOP_TERMS or token in GAP_NOISE_WORDS for token in tokens):
                continue
            normalized_tokens = [token.lower() for token in tokens]
            meaningful_tokens = [
                token for token in normalized_tokens if token not in {"the", "a", "an"}
            ]
            if meaningful_tokens and all(token in slug_tokens for token in meaningful_tokens):
                continue

            normalized = term.replace(" ", "_").lower()
            if normalized in page_slugs:
                continue
            pages_for_term = term_pages.setdefault(term, set())
            pages_for_term.add(slug)

    gaps: list[EntityGapFinding] = []
    for term, seen_pages in term_pages.items():
        mentions = len(seen_pages)
        if mentions < 3:
            continue
        priority = "high" if mentions >= 8 else "medium" if mentions >= 5 else "low"
        gaps.append(
            EntityGapFinding(
                term=term,
                mentions=mentions,
                pages=sorted(seen_pages),
                priority=priority,
            )
        )
    gaps.sort(key=lambda item: (-item.mentions, item.term))
    return gaps


def gather_lint_results(repo_root: Path, *, today: date | None = None) -> LintResults:
    if today is None:
        today = datetime.now().date()

    pages = build_page_inventory(repo_root)
    page_slugs = set(pages.keys())
    index_entries = read_index_entries(repo_root)
    index_slugs = set(index_entries.keys())
    orphans, dead_links = _collect_orphans_and_dead_links(pages, page_slugs)

    empty_summaries = [
        slug
        for slug, summary in index_entries.items()
        if summary == "" or summary.lower().startswith("todo")
    ]
    index = IndexAuditFinding(
        index_ghosts=sorted(index_slugs - page_slugs),
        wiki_ghosts=sorted(page_slugs - index_slugs),
        empty_summaries=sorted(empty_summaries),
    )

    layout = detect_knowledge_layout(repo_root)
    log_path = layout.log_path if layout is not None else (repo_root / "log.md")
    ingestion_dates = (
        collect_ingestion_dates(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    )
    stale, contradictions = _collect_stale_and_contradictions(
        pages,
        page_slugs,
        ingestion_dates,
        today,
    )
    gaps = _collect_entity_gaps(pages, page_slugs)

    return LintResults(
        pages_audited=len(page_slugs),
        index_entries=len(index_entries),
        ingestion_events=len(ingestion_dates),
        orphans=orphans,
        dead_links=dead_links,
        index=index,
        stale=stale,
        contradictions=contradictions,
        gaps=gaps,
    )


def _build_index_row(slug: str, frontmatter: dict[str, object], today: date) -> str:
    summary_raw = frontmatter.get("summary")
    summary = (
        summary_raw.strip()
        if isinstance(summary_raw, str) and summary_raw.strip()
        else "TODO: add summary"
    )
    summary = summary.replace("|", "/")

    source_count = frontmatter.get("source_count")
    source_count_val = str(source_count) if isinstance(source_count, int) else "0"

    status_raw = frontmatter.get("status")
    status_val = (
        status_raw.strip() if isinstance(status_raw, str) and status_raw.strip() else "draft"
    )

    updated_raw = frontmatter.get("updated")
    updated_date = parse_iso_date(updated_raw if isinstance(updated_raw, str | date) else None)
    updated_val = updated_date.isoformat() if updated_date is not None else today.isoformat()

    return f"| [[{slug}]] | {summary} | {source_count_val} | {status_val} | {updated_val} |"


def update_index_with_wiki_ghosts(
    repo_root: Path,
    missing_slugs: list[str],
    pages: dict[str, dict[str, object]],
    *,
    today: date | None = None,
) -> int:
    if not missing_slugs:
        return 0
    if today is None:
        today = datetime.now().date()

    index_path = repo_root / "index.md"
    if not index_path.exists():
        return 0

    lines = index_path.read_text(encoding="utf-8").splitlines()
    existing = read_index_entries(repo_root)
    to_add = [slug for slug in sorted(missing_slugs) if slug not in existing]
    if not to_add:
        return 0

    insert_at = len(lines)
    for idx, line in enumerate(lines):
        if line.startswith("## Notes"):
            insert_at = idx
            break

    new_rows: list[str] = []
    for slug in to_add:
        info = pages.get(slug, {})
        frontmatter = info.get("frontmatter") if isinstance(info, dict) else {}
        if not isinstance(frontmatter, dict):
            frontmatter = {}
        new_rows.append(_build_index_row(slug, frontmatter, today))

    updated_lines = lines[:insert_at] + new_rows + lines[insert_at:]
    index_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return len(new_rows)


def apply_safe_lint_fixes(repo_root: Path, results: LintResults) -> dict[str, int]:
    pages = build_page_inventory(repo_root)
    added_index_entries = update_index_with_wiki_ghosts(
        repo_root,
        results.index.wiki_ghosts,
        pages,
    )
    return {
        "index_entries_added": added_index_entries,
    }


def build_lint_summary(results: LintResults) -> dict[str, int]:  # pragma: no cover
    critical = len(results.orphans) + len(results.dead_links) + len(results.contradictions)
    structural = (
        len(results.index.index_ghosts) + len(results.index.wiki_ghosts) + len(results.stale)
    )
    opportunities = len(results.gaps)
    total_issues = critical + structural + opportunities
    health_denominator = max(1, results.pages_audited)
    health_score = max(
        0, min(100, int(round(100 * (1 - (critical + structural) / health_denominator))))
    )
    return {
        "critical": critical,
        "structural": structural,
        "opportunities": opportunities,
        "total": total_issues,
        "health_score": health_score,
    }


def render_lint_report_text(
    results: LintResults,
    category: str,
    *,
    max_gaps: int = 25,
    max_gap_pages: int = 5,
) -> str:  # pragma: no cover
    summary = build_lint_summary(results)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Lint Report - shattered_sea",
        f"Generated: {generated}",
        f"Pages audited: {results.pages_audited}",
        f"Index entries: {results.index_entries}",
        f"Ingestion events in log: {results.ingestion_events}",
        "",
    ]

    def include(name: str) -> bool:
        return category == "all" or category == name

    if include("orphans"):
        lines.append(f"Orphan Pages ({len(results.orphans)})")
        for orphan in results.orphans:
            suggestions = ", ".join(f"[[{s}]]" for s in orphan.suggested_links_from) or "none"
            lines.append(f"- [[{orphan.slug}]]; suggested links from: {suggestions}")
        lines.append("")

    if include("dead_links"):
        lines.append(f"Dead Links ({len(results.dead_links)})")
        for dead in results.dead_links:
            sources = ", ".join(f"[[{s}]]" for s in dead.source_pages)
            line = (
                f"- [[{dead.target}]] in {sources}; classification={dead.classification}; "
                f"count={dead.count}"
            )
            if dead.likely_meant:
                line += f"; likely meant [[{dead.likely_meant}]]"
            lines.append(line)
        lines.append("")

    if include("index"):
        index_gap_count = (
            len(results.index.index_ghosts)
            + len(results.index.wiki_ghosts)
            + len(results.index.empty_summaries)
        )
        lines.append(f"Index Gaps ({index_gap_count})")
        for slug in results.index.index_ghosts:
            lines.append(f"- INDEX GHOST [[{slug}]]")
        for slug in results.index.wiki_ghosts:
            lines.append(f"- WIKI GHOST [[{slug}]]")
        for slug in results.index.empty_summaries:
            lines.append(f"- EMPTY SUMMARY [[{slug}]]")
        lines.append("")

    if include("stale"):
        lines.append(f"Stale Pages ({len(results.stale)})")
        for stale_item in results.stale:
            lines.append(
                f"- [[{stale_item.slug}]] "
                f"last_updated={stale_item.last_updated} "
                f"source_count={stale_item.source_count} "
                f"ingestions_since={stale_item.ingestions_since_update} "
                f"reason={stale_item.reason}"
            )
        lines.append("")

    if include("contradictions"):
        lines.append(f"Contradictions ({len(results.contradictions)})")
        for contradiction in results.contradictions:
            lines.append(
                f"- [[{contradiction.slug}]] "
                f"open_since={contradiction.open_since} "
                f"({contradiction.open_days} days); "
                f"conflict={contradiction.conflict}"
            )
        lines.append("")

    if include("gaps"):
        gap_limit = max(0, max_gaps)
        page_limit = max(1, max_gap_pages)
        shown = results.gaps[:gap_limit] if gap_limit > 0 else []
        lines.append(f"Entity Gaps ({len(shown)} shown of {len(results.gaps)})")
        for gap in shown:
            pages = ", ".join(f"[[{s}]]" for s in gap.pages[:page_limit])
            lines.append(
                f'- "{gap.term}" mentions={gap.mentions} priority={gap.priority}; pages={pages}'
            )
        lines.append("")

    lines.append("Summary")
    lines.append(f"- Critical: {summary['critical']}")
    lines.append(f"- Structural: {summary['structural']}")
    lines.append(f"- Opportunities: {summary['opportunities']}")
    lines.append(f"- Wiki health score: {summary['health_score']}%")
    lines.append("")
    lines.append("Auto-fix boundary")
    lines.append("- Safe auto-fixable: index wiki-ghost additions only (idempotent)")
    lines.append("- Manual required: orphans, dead-links, contradictions, stale pages,")
    lines.append("  index ghosts, and entity gaps")
    return "\n".join(lines)


def render_lint_report_json(
    results: LintResults,
    category: str,
    *,
    max_gaps: int = 25,
    max_gap_pages: int = 5,
) -> str:  # pragma: no cover
    summary = build_lint_summary(results)

    def include(name: str) -> bool:
        return category == "all" or category == name

    has_safe_fixes = bool(results.index.wiki_ghosts)
    has_manual = bool(
        results.orphans
        or results.dead_links
        or results.contradictions
        or results.stale
        or results.index.index_ghosts
    )
    if not has_safe_fixes and not has_manual:
        next_action = "clean"
    elif has_safe_fixes and not has_manual:
        next_action = "safe_fix_available"
    else:
        next_action = "manual_review_required"

    typo_count = sum(1 for dl in results.dead_links if dl.classification == "typo_likely")
    category_counts: dict[str, int] = {
        "orphans": len(results.orphans),
        "dead_links": len(results.dead_links),
        "dead_links_typo_likely": typo_count,
        "dead_links_stub_worthy": len(results.dead_links) - typo_count,
        "contradictions": len(results.contradictions),
        "stale": len(results.stale),
        "index_ghosts": len(results.index.index_ghosts),
        "wiki_ghosts": len(results.index.wiki_ghosts),
        "empty_summaries": len(results.index.empty_summaries),
        "gaps": len(results.gaps),
    }

    payload: dict[str, object] = {
        "summary": {
            "pages_audited": results.pages_audited,
            "index_entries": results.index_entries,
            "ingestion_events": results.ingestion_events,
            **summary,
        },
        "next_action": next_action,
        "category_counts": category_counts,
        "manual_required": {
            "orphans": [item.slug for item in results.orphans],
            "dead_links": [
                {
                    "target": item.target,
                    "classification": item.classification,
                    "likely_meant": item.likely_meant,
                }
                for item in results.dead_links
            ],
            "contradictions": [item.slug for item in results.contradictions],
            "stale": [item.slug for item in results.stale],
            "index_ghosts": results.index.index_ghosts,
            "entity_gaps": [item.term for item in results.gaps],
        },
        "safe_auto_fixable": {
            "index_wiki_ghosts": results.index.wiki_ghosts,
        },
    }

    if include("orphans"):
        payload["orphans"] = [
            {
                "slug": item.slug,
                "inbound_count": item.inbound_count,
                "suggested_links_from": item.suggested_links_from,
            }
            for item in results.orphans
        ]
    if include("dead_links"):
        payload["dead_links"] = [
            {
                "target": item.target,
                "source_pages": item.source_pages,
                "count": item.count,
                "classification": item.classification,
                "likely_meant": item.likely_meant,
            }
            for item in results.dead_links
        ]
    if include("index"):
        payload["index"] = {
            "index_ghosts": results.index.index_ghosts,
            "wiki_ghosts": results.index.wiki_ghosts,
            "empty_summaries": results.index.empty_summaries,
        }
    if include("stale"):
        payload["stale"] = [
            {
                "slug": item.slug,
                "last_updated": item.last_updated,
                "source_count": item.source_count,
                "ingestions_since_update": item.ingestions_since_update,
                "reason": item.reason,
            }
            for item in results.stale
        ]
    if include("contradictions"):
        payload["contradictions"] = [
            {
                "slug": item.slug,
                "open_since": item.open_since,
                "open_days": item.open_days,
                "conflict": item.conflict,
            }
            for item in results.contradictions
        ]
    if include("gaps"):
        gap_limit = max(0, max_gaps)
        page_limit = max(1, max_gap_pages)
        shown = results.gaps[:gap_limit] if gap_limit > 0 else []
        payload["gaps"] = [
            {
                "term": item.term,
                "mentions": item.mentions,
                "pages": item.pages[:page_limit],
                "priority": item.priority,
            }
            for item in shown
        ]
        payload["gaps_meta"] = {
            "returned": len(shown),
            "total": len(results.gaps),
            "truncated": len(shown) < len(results.gaps),
            "max_pages_per_gap": page_limit,
        }

    return json.dumps(payload, indent=2)


def print_lint_report(
    results: LintResults,
    *,
    category: str,
    output_format: str,
    max_gaps: int = 25,
    max_gap_pages: int = 5,
) -> str:  # pragma: no cover
    if output_format in {"text", "markdown"}:
        report = render_lint_report_text(
            results,
            category,
            max_gaps=max_gaps,
            max_gap_pages=max_gap_pages,
        )
        print(report)
        return report
    report = render_lint_report_json(
        results,
        category,
        max_gaps=max_gaps,
        max_gap_pages=max_gap_pages,
    )
    print(report)
    return report
