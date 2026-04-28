from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, cast

from .cli_args import apply_agent_presets, create_parser, validate_args
from .ingest_finalize import finalize_ingest, finalize_runner_dir
from .ingest_prep import (
    build_ingest_batch,
    build_ingest_prep,
    build_ingest_runner,
    print_ingest_batch,
    print_ingest_prep,
    print_ingest_runner,
)
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
from .query_prep import (
    append_filed_log,
    append_query_log,
    gather_query_prep,
    print_query_prep,
    render_query_prep_json,
    render_query_prep_text,
)
from .status_audit import (
    gather_wiki_status,
    print_wiki_status,
    render_wiki_status_json,
    render_wiki_status_text,
)
from .synthesis_audit import gather_synthesis_candidates, print_synthesis_report
from .validation import gather_issues, print_report


def _resolve_output_path(repo_root: Path, output_file: str) -> Path:
    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


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
    if args.status_output_file:
        rendered = (
            render_wiki_status_json(
                status_report,
                limit=max(1, args.limit),
                pending_only=args.pending_only,
            )
            if args.status_format == "json"
            else render_wiki_status_text(
                status_report,
                limit=max(1, args.limit),
                pending_only=args.pending_only,
            )
        )
        output_path = _resolve_output_path(repo_root, args.status_output_file)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"status report written to {output_path.relative_to(repo_root)}")
        print(
            "summary: "
            f"new={sum(1 for item in status_report.sources if item.status == 'new')} "
            f"modified={sum(1 for item in status_report.sources if item.status == 'modified')} "
            f"deleted={len(status_report.deleted_sources)} "
            f"recommendation={status_report.recommendation}"
        )
        return 0

    print_wiki_status(
        status_report,
        limit=max(1, args.limit),
        pending_only=args.pending_only,
        output_format=args.status_format,
    )
    return 0


def _run_query(args: argparse.Namespace, repo_root: Path) -> int:
    # Load QMD results from file if provided
    qmd_data: list[dict[str, Any]] | None = None
    if args.query_merge_qmd.strip():
        qmd_path = Path(args.query_merge_qmd)
        if not qmd_path.is_absolute():
            qmd_path = repo_root / qmd_path
        if not qmd_path.exists():
            print(f"error: --query-merge-qmd file not found: {qmd_path}", file=sys.stderr)
            return 1
        try:
            raw = json.loads(qmd_path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                print("error: --query-merge-qmd file must contain a JSON array", file=sys.stderr)
                return 1
            qmd_data = cast(list[dict[str, Any]], raw)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"error: failed to read --query-merge-qmd file: {exc}", file=sys.stderr)
            return 1

    query_result = gather_query_prep(
        repo_root,
        question=args.query_question,
        top_k=max(1, args.query_top_k),
        fast_mode=args.query_fast,
        public_only=args.query_public_only,
        snippet_context=max(0, args.query_snippet_context),
        max_snippets=max(1, args.query_max_snippets),
        qmd_data=qmd_data,
    )
    if args.query_output_file:
        rendered = (
            render_query_prep_json(query_result)
            if args.query_format == "json"
            else render_query_prep_text(query_result)
        )
        output_path = _resolve_output_path(repo_root, args.query_output_file)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"query prep written to {output_path.relative_to(repo_root)}")
        print(
            "summary: "
            f"type={query_result.query_type} "
            f"mode={query_result.mode} "
            f"qmd_merged={'yes' if query_result.qmd_merged else 'no'} "
            f"primary={len(query_result.primary)} "
            f"secondary={len(query_result.secondary)} "
            f"excluded_internal={query_result.excluded_internal_count}"
        )
    else:
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


def _run_query_filed(args: argparse.Namespace, repo_root: Path) -> int:
    log_path = append_filed_log(
        repo_root,
        page=args.query_filed_page.strip(),
        from_query=args.query_filed_from_query.strip(),
    )
    if log_path is None:
        print("error: could not detect knowledge layout — no log path found", file=sys.stderr)
        return 1
    print(f"filed: {args.query_filed_page} → {log_path.relative_to(repo_root)}")
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

    extension = (
        "json" if args.lint_format == "json" else "md" if args.lint_format == "markdown" else "txt"
    )
    output_path = (
        Path(args.lint_output_file)
        if args.lint_output_file
        else Path(f".claude/tmp/lint_report.{extension}")
    )
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
    typo_count = sum(1 for dl in results.dead_links if dl.classification == "typo_likely")
    stub_count = len(results.dead_links) - typo_count
    print(
        f"orphans={len(results.orphans)} "
        f"dead_links={len(results.dead_links)}(typo={typo_count},stub={stub_count}) "
        f"contradictions={len(results.contradictions)}"
    )
    print(
        f"stale={len(results.stale)} "
        f"index_ghosts={len(results.index.index_ghosts)} "
        f"wiki_ghosts={len(results.index.wiki_ghosts)} "
        f"gaps={len(results.gaps)}"
    )
    wiki_ghost_count = len(results.index.wiki_ghosts)
    if wiki_ghost_count > 0:
        print(
            f"safe_auto_fixable: {wiki_ghost_count} wiki_ghost(s) "
            "→ re-run with --lint-safe-fix to add to index"
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
    if args.ingest_output_file:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_ingest_report(
                statuses,
                limit=max(1, args.limit),
                pending_only=args.pending_only,
                output_format=args.format,
                include_queue=args.ingest_queue,
            )
        output_path = _resolve_output_path(repo_root, args.ingest_output_file)
        output_path.write_text(buffer.getvalue().rstrip() + "\n", encoding="utf-8")
        pending_count = sum(1 for item in statuses if item.status in {"new", "changed"})
        next_pending = next((s.raw_path for s in statuses if s.status in {"new", "changed"}), None)
        print(f"ingest report written to {output_path.relative_to(repo_root)}")
        print(
            f"summary: total={len(statuses)} pending={pending_count} next={next_pending or 'none'}"
        )
    else:
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
    if args.ingest_output_file:
        if args.format == "json":
            rendered = json.dumps(payload, indent=2)
        else:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                print_ingest_prep(payload, args.format)
            rendered = buffer.getvalue().rstrip()
        output_path = _resolve_output_path(repo_root, args.ingest_output_file)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"ingest prep written to {output_path.relative_to(repo_root)}")
        if payload.get("ok") is True:
            print(
                "summary: "
                f"source={payload.get('source_path')} "
                f"status={payload.get('ingest_status')} "
                f"knowledge_root={payload.get('knowledge_root')}"
            )
        else:
            print(f"summary: error={payload.get('error')}")
    else:
        print_ingest_prep(payload, args.format)
    if payload.get("ok") is False:
        return 2
    return 0


def _run_ingest_batch(args: argparse.Namespace, repo_root: Path) -> int:
    payload = build_ingest_batch(
        repo_root,
        limit=max(1, args.limit),
        pending_only=args.pending_only,
    )
    if args.ingest_output_file:
        if args.format == "json":
            rendered = json.dumps(payload, indent=2)
        else:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                print_ingest_batch(payload, args.format)
            rendered = buffer.getvalue().rstrip()
        output_path = _resolve_output_path(repo_root, args.ingest_output_file)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
        summary = summary if isinstance(summary, dict) else {}
        print(f"ingest batch written to {output_path.relative_to(repo_root)}")
        print(
            "summary: "
            f"pending={summary.get('pending_sources')} "
            f"selected={summary.get('selected_sources')} "
            f"next={summary.get('next_source') or 'none'}"
        )
    else:
        print_ingest_batch(payload, args.format)
    return 0


def _run_ingest_runner(args: argparse.Namespace, repo_root: Path) -> int:
    checkpoint_dir = _resolve_output_path(repo_root, args.ingest_checkpoint_dir)
    payload = build_ingest_runner(
        repo_root,
        limit=max(1, args.limit),
        pending_only=args.pending_only,
        checkpoint_dir=checkpoint_dir,
    )
    if args.ingest_output_file:
        if args.format == "json":
            rendered = json.dumps(payload, indent=2)
        else:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                print_ingest_runner(payload, args.format)
            rendered = buffer.getvalue().rstrip()
        output_path = _resolve_output_path(repo_root, args.ingest_output_file)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
        summary = summary if isinstance(summary, dict) else {}
        print(f"ingest runner written to {output_path.relative_to(repo_root)}")
        print(
            "summary: "
            f"pending={summary.get('pending_sources')} "
            f"selected={summary.get('selected_sources')} "
            f"checkpoint_dir={payload.get('checkpoint_dir')}"
        )
    else:
        print_ingest_runner(payload, args.format)
    return 0


def _run_ingest_finalize(args: argparse.Namespace, repo_root: Path) -> int:
    payload_path = Path(args.ingest_finalize_file)
    if not payload_path.is_absolute():
        payload_path = repo_root / payload_path
    result = finalize_ingest(repo_root, payload_path)
    print(
        "ingest finalize updated "
        f"{result['manifest_path']}, {result['log_path']}, {result['hot_path']}"
    )
    if result["mode"] == "single":
        print(
            "summary: "
            f"source={result['source_path']} "
            f"created={result['pages_created']} "
            f"updated={result['pages_updated']} "
            f"contradictions={result['contradictions']} "
            f"skipped={result['sources_skipped']}"
        )
    else:
        print(
            "summary: "
            f"sources={result['sources_processed']} "
            f"applied={result['sources_applied']} "
            f"skipped={result['sources_skipped']} "
            f"created={result['pages_created']} "
            f"updated={result['pages_updated']} "
            f"contradictions={result['contradictions']}"
        )
    return 0


def _run_ingest_runner_finalize(args: argparse.Namespace, repo_root: Path) -> int:
    checkpoint_dir = (
        _resolve_output_path(repo_root, args.ingest_runner_dir)
        if args.ingest_runner_dir
        else repo_root / ".claude/tmp/ingest_runner"
    )
    result = finalize_runner_dir(repo_root, checkpoint_dir)
    if not result.get("ok"):
        print(f"error: {result.get('error')}")
        return 2
    if result.get("files_finalized", 0) == 0:
        message = result.get("message", "no completed stubs")
        files_found = result.get("files_found", 0)
        checkpoint_label = result.get("checkpoint_dir", "?")
        print(
            f"ingest runner-finalize: {message} (checked {files_found} stubs in {checkpoint_label})"
        )
        return 0
    print(
        f"ingest runner-finalize updated "
        f"{result.get('manifest_path')}, {result.get('log_path')}, {result.get('hot_path')}"
    )
    skipped_value = result.get("skipped")
    skipped = skipped_value if isinstance(skipped_value, list) else []
    print(
        "summary: "
        f"stubs_found={result.get('files_found')} "
        f"finalized={result.get('files_finalized')} "
        f"skipped={len(skipped)} "
        f"created={result.get('pages_created')} "
        f"updated={result.get('pages_updated')} "
        f"contradictions={result.get('contradictions')}"
    )
    return 0


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    apply_agent_presets(args)

    repo_root = Path(args.repo_root).resolve()

    validate_args(parser, args)

    dispatch_table: list[tuple[bool, Any]] = [
        (args.synthesize_report, _run_synthesis),
        (args.ingest_prep, _run_ingest_prep),
        (args.ingest_batch, _run_ingest_batch),
        (args.ingest_runner, _run_ingest_runner),
        (args.ingest_runner_finalize, _run_ingest_runner_finalize),
        (args.ingest_finalize, _run_ingest_finalize),
        (args.status_report, _run_status),
        (args.query_prep, _run_query),
        (args.query_filed, _run_query_filed),
        (args.lint_report, _run_lint),
        (args.ingest_report, _run_ingest),
    ]
    for is_enabled, runner in dispatch_table:
        if is_enabled:
            return runner(args, repo_root)

    issues = gather_issues(repo_root)
    print_report(issues)

    has_error = any(i.level == "error" for i in issues)
    has_warn = any(i.level == "warn" for i in issues)
    if has_error or (args.strict and has_warn):
        return 1
    return 0
