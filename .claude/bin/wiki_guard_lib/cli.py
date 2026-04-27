from __future__ import annotations

import argparse
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from .ingest_prep import (
    build_ingest_batch,
    build_ingest_prep,
    build_ingest_runner,
    print_ingest_batch,
    print_ingest_prep,
    print_ingest_runner,
)
from .ingest_finalize import finalize_ingest, finalize_runner_dir
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

    if args.query_output_file and not args.query_prep:
        parser.error("--query-output-file requires --query-prep")

    if args.query_result_pages < 0:
        parser.error("--query-result-pages must be >= 0")

    if args.status_output_file and not args.status_report:
        parser.error("--status-output-file requires --status-report")

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

    if args.ingest_batch and args.ingest_report:
        parser.error("--ingest-batch cannot be combined with --ingest-report")

    if args.ingest_runner and args.ingest_report:
        parser.error("--ingest-runner cannot be combined with --ingest-report")

    if args.ingest_prep and args.status_report:
        parser.error("--ingest-prep cannot be combined with --status-report")

    if args.ingest_batch and args.status_report:
        parser.error("--ingest-batch cannot be combined with --status-report")

    if args.ingest_runner and args.status_report:
        parser.error("--ingest-runner cannot be combined with --status-report")

    if args.ingest_prep and args.lint_report:
        parser.error("--ingest-prep cannot be combined with --lint-report")

    if args.ingest_batch and args.lint_report:
        parser.error("--ingest-batch cannot be combined with --lint-report")

    if args.ingest_runner and args.lint_report:
        parser.error("--ingest-runner cannot be combined with --lint-report")

    if args.ingest_prep and args.query_prep:
        parser.error("--ingest-prep cannot be combined with --query-prep")

    if args.ingest_batch and args.query_prep:
        parser.error("--ingest-batch cannot be combined with --query-prep")

    if args.ingest_runner and args.query_prep:
        parser.error("--ingest-runner cannot be combined with --query-prep")

    if args.ingest_prep and args.synthesize_report:
        parser.error("--ingest-prep cannot be combined with --synthesize-report")

    if args.ingest_batch and args.synthesize_report:
        parser.error("--ingest-batch cannot be combined with --synthesize-report")

    if args.ingest_runner and args.synthesize_report:
        parser.error("--ingest-runner cannot be combined with --synthesize-report")

    if args.ingest_batch and args.ingest_prep:
        parser.error("--ingest-batch cannot be combined with --ingest-prep")

    if args.ingest_runner and args.ingest_prep:
        parser.error("--ingest-runner cannot be combined with --ingest-prep")

    if args.ingest_runner and args.ingest_batch:
        parser.error("--ingest-runner cannot be combined with --ingest-batch")

    if args.ingest_prep and not args.source.strip():
        parser.error("--ingest-prep requires --source")

    if args.ingest_output_file and not (args.ingest_report or args.ingest_prep or args.ingest_batch or args.ingest_runner):
        parser.error("--ingest-output-file requires --ingest-report, --ingest-prep, --ingest-batch, or --ingest-runner")

    if args.ingest_finalize and not args.ingest_finalize_file.strip():
        parser.error("--ingest-finalize requires --ingest-finalize-file")

    if args.ingest_runner_finalize and any([
        args.ingest_prep,
        args.ingest_batch,
        args.ingest_runner,
        args.ingest_report,
        args.ingest_finalize,
        args.status_report,
        args.lint_report,
        args.query_prep,
        args.synthesize_report,
    ]):
        parser.error("--ingest-runner-finalize cannot be combined with other report or prep flags")


def _apply_agent_presets(args: argparse.Namespace) -> None:
    if args.lint_agent:
        args.lint_report = True
        if args.lint_format == "text":
            args.lint_format = "json"
        if args.lint_max_gaps == 25:
            args.lint_max_gaps = 10
        if args.lint_max_gap_pages == 5:
            args.lint_max_gap_pages = 3

    if args.status_agent:
        args.status_report = True
        if args.status_format == "text":
            args.status_format = "json"
        if not args.status_output_file:
            args.status_output_file = ".claude/tmp/status_report.json"

    if args.query_agent:
        args.query_prep = True
        if args.query_format == "text":
            args.query_format = "json"
        if not args.query_output_file:
            args.query_output_file = ".claude/tmp/query_prep.json"

    if args.ingest_agent:
        args.ingest_prep = True
        if args.format == "text":
            args.format = "json"
        if not args.ingest_output_file:
            args.ingest_output_file = ".claude/tmp/ingest_prep.json"

    if args.ingest_batch_agent:
        args.ingest_batch = True
        args.pending_only = True
        if args.format == "text":
            args.format = "json"
        if args.limit == 10:
            args.limit = 5
        if not args.ingest_output_file:
            args.ingest_output_file = ".claude/tmp/ingest_batch.json"

    if args.ingest_runner_agent:
        args.ingest_runner = True
        args.pending_only = True
        if args.format == "text":
            args.format = "json"
        if args.limit == 10:
            args.limit = 5
        if not args.ingest_output_file:
            args.ingest_output_file = ".claude/tmp/ingest_runner.json"
        if not args.ingest_checkpoint_dir:
            args.ingest_checkpoint_dir = ".claude/tmp/ingest_runner"

    if args.ingest_runner_finalize_agent:
        args.ingest_runner_finalize = True
        if not args.ingest_runner_dir:
            args.ingest_runner_dir = ".claude/tmp/ingest_runner"


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
    query_result = gather_query_prep(
        repo_root,
        question=args.query_question,
        top_k=max(1, args.query_top_k),
        fast_mode=args.query_fast,
        public_only=args.query_public_only,
        snippet_context=max(0, args.query_snippet_context),
        max_snippets=max(1, args.query_max_snippets),
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
        print(f"safe_auto_fixable: {wiki_ghost_count} wiki_ghost(s) → re-run with --lint-safe-fix to add to index")

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
        print(f"ingest report written to {output_path.relative_to(repo_root)}")
        print(
            "summary: "
            f"total={len(statuses)} "
            f"pending={pending_count} "
            f"next={(next((s.raw_path for s in statuses if s.status in {'new', 'changed'}), None) or 'none')}"
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
    print(f"ingest finalize updated {result['manifest_path']}, {result['log_path']}, {result['hot_path']}")
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
    checkpoint_dir = _resolve_output_path(repo_root, args.ingest_runner_dir) if args.ingest_runner_dir else repo_root / ".claude/tmp/ingest_runner"
    result = finalize_runner_dir(repo_root, checkpoint_dir)
    if not result.get("ok"):
        print(f"error: {result.get('error')}")
        return 2
    if result.get("files_finalized", 0) == 0:
        print(f"ingest runner-finalize: {result.get('message', 'no completed stubs')} (checked {result.get('files_found', 0)} stubs in {result.get('checkpoint_dir', '?')})")
        return 0
    print(
        f"ingest runner-finalize updated "
        f"{result.get('manifest_path')}, {result.get('log_path')}, {result.get('hot_path')}"
    )
    print(
        "summary: "
        f"stubs_found={result.get('files_found')} "
        f"finalized={result.get('files_finalized')} "
        f"skipped={len(result.get('skipped', []))} "
        f"created={result.get('pages_created')} "
        f"updated={result.get('pages_updated')} "
        f"contradictions={result.get('contradictions')}"
    )
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
        "--ingest-finalize",
        action="store_true",
        help="Apply manifest/log/hot bookkeeping for a completed ingest from a JSON payload",
    )
    parser.add_argument(
        "--ingest-agent",
        action="store_true",
        help=(
            "Agent preset for ingest preflight: implies --ingest-prep, defaults to JSON output, "
            "and writes the prep packet to .claude/tmp/ingest_prep.json"
        ),
    )
    parser.add_argument(
        "--ingest-batch",
        action="store_true",
        help="Build a compact multi-source ingest packet for the selected raw/ queue",
    )
    parser.add_argument(
        "--ingest-batch-agent",
        action="store_true",
        help=(
            "Agent preset for batch ingest preflight: implies --ingest-batch, defaults to JSON output, "
            "sets --pending-only, caps selection to 5, and writes .claude/tmp/ingest_batch.json"
        ),
    )
    parser.add_argument(
        "--ingest-runner",
        action="store_true",
        help="Build a sequential ingest runner packet plus per-source prep checkpoints",
    )
    parser.add_argument(
        "--ingest-runner-agent",
        action="store_true",
        help=(
            "Agent preset for ingest runner mode: implies --ingest-runner, defaults to JSON output, "
            "sets --pending-only, caps selection to 5, writes .claude/tmp/ingest_runner.json, "
            "and materializes prep checkpoints under .claude/tmp/ingest_runner/"
        ),
    )
    parser.add_argument(
        "--ingest-runner-finalize",
        action="store_true",
        help=(
            "Discover completed finalize stubs in --ingest-runner-dir and submit them in one pass; "
            "safe to call after each step or at the end of a batch run"
        ),
    )
    parser.add_argument(
        "--ingest-runner-finalize-agent",
        action="store_true",
        help=(
            "Agent preset for runner finalize: implies --ingest-runner-finalize and defaults "
            "--ingest-runner-dir to .claude/tmp/ingest_runner"
        ),
    )
    parser.add_argument(
        "--ingest-runner-dir",
        default="",
        help="With --ingest-runner-finalize, path to the runner checkpoint directory (default: .claude/tmp/ingest_runner)",
    )
    parser.add_argument(
        "--status-report",
        action="store_true",
        help="Show skill-aligned wiki status/delta across sources and manifest",
    )
    parser.add_argument(
        "--status-agent",
        action="store_true",
        help=(
            "Agent preset for status workflow: implies --status-report, defaults to JSON output, "
            "and writes the report to .claude/tmp/status_report.json"
        ),
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
        "--ingest-output-file",
        default="",
        help=(
            "With --ingest-report, --ingest-prep, or --ingest-batch, write output to this path instead of stdout; "
            "commonly used by ingest agent presets"
        ),
    )
    parser.add_argument(
        "--ingest-checkpoint-dir",
        default="",
        help="With --ingest-runner, directory where per-source prep/finalize checkpoint paths are staged",
    )
    parser.add_argument(
        "--ingest-finalize-file",
        default="",
        help="With --ingest-finalize, JSON payload describing manifest/log/hot updates to apply",
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
        "--status-output-file",
        default="",
        help=(
            "With --status-report, write report to this path instead of stdout; "
            "commonly used by --status-agent"
        ),
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
        "--lint-agent",
        action="store_true",
        help=(
            "Agent preset for lint workflow: implies --lint-report, defaults to JSON output, "
            "and caps entity-gap payloads for token efficiency"
        ),
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
        "--query-agent",
        action="store_true",
        help=(
            "Agent preset for query workflow: implies --query-prep, defaults to JSON output, "
            "and writes the report to .claude/tmp/query_prep.json"
        ),
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
        "--query-output-file",
        default="",
        help=(
            "With --query-prep, write report to this path instead of stdout; "
            "commonly used by --query-agent"
        ),
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
    _apply_agent_presets(args)

    repo_root = Path(args.repo_root).resolve()

    _validate_args(parser, args)

    if args.synthesize_report:
        return _run_synthesis(args, repo_root)

    if args.ingest_prep:
        return _run_ingest_prep(args, repo_root)

    if args.ingest_batch:
        return _run_ingest_batch(args, repo_root)

    if args.ingest_runner:
        return _run_ingest_runner(args, repo_root)

    if args.ingest_runner_finalize:
        return _run_ingest_runner_finalize(args, repo_root)

    if args.ingest_finalize:
        return _run_ingest_finalize(args, repo_root)

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
