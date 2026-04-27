from __future__ import annotations

import argparse
from pathlib import Path

from .ingest_prep import build_ingest_prep, print_ingest_prep
from .ingest_status import (
    gather_ingest_source_status,
    has_pending_ingest_sources,
    print_ingest_report,
)
from .linting import (
    apply_safe_lint_fixes,
    build_lint_summary,
    gather_lint_results,
    render_lint_report_json,
    render_lint_report_text,
)
from .query_prep import append_query_log, gather_query_prep, print_query_prep
from .status_audit import gather_wiki_status, print_wiki_status
from .synthesis_audit import gather_synthesis_candidates, print_synthesis_report
from .validation import gather_issues, print_report


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.lint_safe_fix and not args.lint_report:
        parser.error("--lint-safe-fix requires --lint-report")

    if args.lint_fail_on_manual and not args.lint_report:
        parser.error("--lint-fail-on-manual requires --lint-report")

    if args.lint_output_file and not args.lint_report:
        parser.error("--lint-output-file requires --lint-report")

    if args.lint_max_gaps < 0:
        parser.error("--lint-max-gaps must be >= 0")

    if args.lint_max_gap_pages < 1:
        parser.error("--lint-max-gap-pages must be >= 1")

    if args.query_prep and not args.query_question.strip():
        parser.error("--query-prep requires --query-question")

    if args.query_log and not args.query_prep:
        parser.error("--query-log requires --query-prep")

    if args.query_result_pages < 0:
        parser.error("--query-result-pages must be >= 0")

    if args.status_report and args.ingest_report:
        parser.error("--status-report cannot be combined with --ingest-report")

    if args.synthesize_report and args.query_prep:
        parser.error("--synthesize-report cannot be combined with --query-prep")

    if args.synthesize_report and args.lint_report:
        parser.error("--synthesize-report cannot be combined with --lint-report")

    if args.synthesize_report and args.ingest_report:
        parser.error("--synthesize-report cannot be combined with --ingest-report")

    if args.synthesize_report and args.status_report:
        parser.error("--synthesize-report cannot be combined with --status-report")

    if args.ingest_prep and args.ingest_report:
        parser.error("--ingest-prep cannot be combined with --ingest-report")

    if args.ingest_prep and args.status_report:
        parser.error("--ingest-prep cannot be combined with --status-report")

    if args.ingest_prep and args.lint_report:
        parser.error("--ingest-prep cannot be combined with --lint-report")

    if args.ingest_prep and args.query_prep:
        parser.error("--ingest-prep cannot be combined with --query-prep")

    if args.ingest_prep and args.synthesize_report:
        parser.error("--ingest-prep cannot be combined with --synthesize-report")

    if args.ingest_prep and not args.source.strip():
        parser.error("--ingest-prep requires --source")


def _run_synthesis(args: argparse.Namespace, repo_root: Path) -> int:
    synth_report = gather_synthesis_candidates(
        repo_root,
        top_pair_limit=max(1, args.synthesize_pair_limit),
        top_candidates=max(1, args.synthesize_top_candidates),
        skipped_limit=max(0, args.synthesize_skipped_limit),
        topic_filter=args.synthesize_topic,
    )
    print_synthesis_report(synth_report, args.synthesize_format)
    return 0


def _run_status(args: argparse.Namespace, repo_root: Path) -> int:
    status_report = gather_wiki_status(repo_root)
    print_wiki_status(
        status_report,
        limit=max(1, args.limit),
        pending_only=args.pending_only,
        output_format=args.status_format,
    )
    return 0


def _run_query(args: argparse.Namespace, repo_root: Path) -> int:
    query_result = gather_query_prep(
        repo_root,
        question=args.query_question,
        top_k=max(1, args.query_top_k),
        fast_mode=args.query_fast,
        public_only=args.query_public_only,
        snippet_context=max(0, args.query_snippet_context),
        max_snippets=max(1, args.query_max_snippets),
    )
    print_query_prep(query_result, args.query_format)

    if args.query_log:
        default_result_pages = len(query_result.primary)
        result_pages = args.query_result_pages or default_result_pages
        append_query_log(
            repo_root,
            question=args.query_question,
            result_pages=result_pages,
            mode=query_result.mode,
            escalated=args.query_escalated,
        )
    return 0


def _run_lint(args: argparse.Namespace, repo_root: Path) -> int:
    results = gather_lint_results(repo_root)
    report = (
        render_lint_report_json(
            results,
            args.lint_category,
            max_gaps=args.lint_max_gaps,
            max_gap_pages=args.lint_max_gap_pages,
        )
        if args.lint_format == "json"
        else render_lint_report_text(
            results,
            args.lint_category,
            max_gaps=args.lint_max_gaps,
            max_gap_pages=args.lint_max_gap_pages,
        )
    )

    extension = "json" if args.lint_format == "json" else "md" if args.lint_format == "markdown" else "txt"
    output_path = Path(args.lint_output_file) if args.lint_output_file else Path(f".claude/tmp/lint_report.{extension}")
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")

    summary = build_lint_summary(results)
    print(f"lint report written to {output_path.relative_to(repo_root)}")
    print(
        "summary: "
        f"critical={summary['critical']} "
        f"structural={summary['structural']} "
        f"opportunities={summary['opportunities']} "
        f"health={summary['health_score']}%"
    )

    if args.lint_safe_fix:
        applied = apply_safe_lint_fixes(repo_root, results)
        print("")
        print("safe auto-fixes applied:")
        print(f"- index entries added: {applied['index_entries_added']}")

    if args.lint_fail_on_manual:
        has_manual = any(
            [
                len(results.orphans) > 0,
                len(results.dead_links) > 0,
                len(results.contradictions) > 0,
                len(results.stale) > 0,
                len(results.index.index_ghosts) > 0,
                len(results.gaps) > 0,
            ]
        )
        if has_manual:
            return 3
    return 0


def _run_ingest(args: argparse.Namespace, repo_root: Path) -> int:
    statuses = gather_ingest_source_status(repo_root)
    print_ingest_report(
        statuses,
        limit=max(1, args.limit),
        pending_only=args.pending_only,
        output_format=args.format,
        include_queue=args.ingest_queue,
    )
    if args.fail_on_pending and has_pending_ingest_sources(statuses):
        return 2
    return 0


def _run_ingest_prep(args: argparse.Namespace, repo_root: Path) -> int:
    payload = build_ingest_prep(repo_root, args.source)
    print_ingest_prep(payload, args.format)
    if payload.get("ok") is False:
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate llm-wiki structure and links")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: current directory)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    parser.add_argument(
        "--ingest-report",
        action="store_true",
        help="Show manifest-backed ingest status for files in raw/",
    )
    parser.add_argument(
        "--ingest-prep",
        action="store_true",
        help="Build a source-specific ingest preflight packet for agent execution",
    )
    parser.add_argument(
        "--status-report",
        action="store_true",
        help="Show skill-aligned wiki status/delta across sources and manifest",
    )
    parser.add_argument(
        "--pending-only",
        action="store_true",
        help="With --ingest-report, only include pending (new/changed) sources",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="With --ingest-report, max number of sources to print (default: 10)",
    )
    parser.add_argument(
        "--source",
        default="",
        help="With --ingest-prep, source path relative to repo root (for example raw/factions/Foo.md)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="With --ingest-report, output format (default: text)",
    )
    parser.add_argument(
        "--status-format",
        choices=("text", "json"),
        default="text",
        help="With --status-report, output format (default: text)",
    )
    parser.add_argument(
        "--ingest-queue",
        action="store_true",
        help="With --ingest-report, include one-command queue for all pending sources",
    )
    parser.add_argument(
        "--fail-on-pending",
        action="store_true",
        help="With --ingest-report, exit non-zero when pending sources exist",
    )
    parser.add_argument(
        "--lint-report",
        action="store_true",
        help="Run category-aware lint audit aligned to LLM-wiki lint workflow",
    )
    parser.add_argument(
        "--lint-category",
        choices=("all", "orphans", "dead_links", "index", "stale", "contradictions", "gaps"),
        default="all",
        help="With --lint-report, limit output to a single lint category (default: all)",
    )
    parser.add_argument(
        "--lint-format",
        choices=("text", "markdown", "json"),
        default="text",
        help="With --lint-report, output format (default: text)",
    )
    parser.add_argument(
        "--lint-safe-fix",
        action="store_true",
        help="With --lint-report, apply only safe idempotent fixes (index wiki-ghost additions)",
    )
    parser.add_argument(
        "--lint-fail-on-manual",
        action="store_true",
        help="With --lint-report, return non-zero when manual-fix categories are present",
    )
    parser.add_argument(
        "--lint-max-gaps",
        type=int,
        default=25,
        help="With --lint-report, max entity gaps to emit in report output (default: 25)",
    )
    parser.add_argument(
        "--lint-max-gap-pages",
        type=int,
        default=5,
        help="With --lint-report, max source pages listed per entity gap (default: 5)",
    )
    parser.add_argument(
        "--lint-output-file",
        default="",
        help=(
            "With --lint-report, write report to this path; defaults to .claude/tmp/lint_report.<format>"
        ),
    )
    parser.add_argument(
        "--query-prep",
        action="store_true",
        help="Build query candidate pages/snippets so Claude can synthesize without broad scans",
    )
    parser.add_argument(
        "--query-question",
        default="",
        help="With --query-prep, user question to rank candidate pages",
    )
    parser.add_argument(
        "--query-top-k",
        type=int,
        default=5,
        help="With --query-prep, number of primary and secondary candidates to return",
    )
    parser.add_argument(
        "--query-fast",
        action="store_true",
        help="With --query-prep, skip snippet extraction and use index/frontmatter signals only",
    )
    parser.add_argument(
        "--query-public-only",
        action="store_true",
        help="With --query-prep, exclude pages tagged visibility/internal or visibility/pii",
    )
    parser.add_argument(
        "--query-format",
        choices=("text", "json"),
        default="text",
        help="With --query-prep, output format (default: text)",
    )
    parser.add_argument(
        "--query-snippet-context",
        type=int,
        default=2,
        help="With --query-prep, context lines around matching lines when generating snippets",
    )
    parser.add_argument(
        "--query-max-snippets",
        type=int,
        default=2,
        help="With --query-prep, max snippets emitted per primary page",
    )
    parser.add_argument(
        "--query-log",
        action="store_true",
        help="With --query-prep, append a QUERY operation line to the knowledge log",
    )
    parser.add_argument(
        "--query-result-pages",
        type=int,
        default=0,
        help=(
            "With --query-log, override result_pages in the log line; "
            "default uses number of primary pages"
        ),
    )
    parser.add_argument(
        "--query-escalated",
        action="store_true",
        help="With --query-log, mark escalated=true for broad-vault fallback runs",
    )
    parser.add_argument(
        "--synthesize-report",
        action="store_true",
        help=(
            "Build ranked synthesis candidates from wiki co-occurrence "
            "and existing synthesis coverage"
        ),
    )
    parser.add_argument(
        "--synthesize-format",
        choices=("text", "json"),
        default="text",
        help="With --synthesize-report, output format (default: text)",
    )
    parser.add_argument(
        "--synthesize-topic",
        default="",
        help="With --synthesize-report, optional topic filter to narrow candidate pairs",
    )
    parser.add_argument(
        "--synthesize-pair-limit",
        type=int,
        default=30,
        help="With --synthesize-report, max co-occurring pairs to evaluate before scoring",
    )
    parser.add_argument(
        "--synthesize-top-candidates",
        type=int,
        default=5,
        help="With --synthesize-report, number of top synthesis candidates to show",
    )
    parser.add_argument(
        "--synthesize-skipped-limit",
        type=int,
        default=10,
        help="With --synthesize-report, number of additional high-score pairs to list as skipped",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    _validate_args(parser, args)

    if args.synthesize_report:
        return _run_synthesis(args, repo_root)

    if args.ingest_prep:
        return _run_ingest_prep(args, repo_root)

    if args.status_report:
        return _run_status(args, repo_root)

    if args.query_prep:
        return _run_query(args, repo_root)

    if args.lint_report:
        return _run_lint(args, repo_root)

    if args.ingest_report:
        return _run_ingest(args, repo_root)

    issues = gather_issues(repo_root)
    print_report(issues)

    has_error = any(i.level == "error" for i in issues)
    has_warn = any(i.level == "warn" for i in issues)
    if has_error or (args.strict and has_warn):
        return 1
    return 0
