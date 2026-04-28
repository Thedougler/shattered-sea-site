from __future__ import annotations

import argparse


def _apply_lint_agent_preset(args: argparse.Namespace) -> None:
    if args.lint_agent:
        args.lint_report = True
        if args.lint_format == "text":
            args.lint_format = "json"
        if args.lint_max_gaps == 25:
            args.lint_max_gaps = 10
        if args.lint_max_gap_pages == 5:
            args.lint_max_gap_pages = 3


def _apply_status_agent_preset(args: argparse.Namespace) -> None:
    if args.status_agent:
        args.status_report = True
        if args.status_format == "text":
            args.status_format = "json"
        if not args.status_output_file:
            args.status_output_file = ".claude/tmp/status_report.json"


def _apply_query_agent_preset(args: argparse.Namespace) -> None:
    if args.query_agent:
        args.query_prep = True
        if args.query_format == "text":
            args.query_format = "json"
        if not args.query_output_file:
            args.query_output_file = ".claude/tmp/query_prep.json"


def _apply_ingest_agent_preset(args: argparse.Namespace) -> None:
    if args.ingest_agent:
        args.ingest_prep = True
        if args.format == "text":
            args.format = "json"
        if not args.ingest_output_file:
            args.ingest_output_file = ".claude/tmp/ingest_prep.json"


def _apply_ingest_batch_agent_preset(args: argparse.Namespace) -> None:
    if args.ingest_batch_agent:
        args.ingest_batch = True
        args.pending_only = True
        if args.format == "text":
            args.format = "json"
        if args.limit == 10:
            args.limit = 5
        if not args.ingest_output_file:
            args.ingest_output_file = ".claude/tmp/ingest_batch.json"


def _apply_ingest_runner_agent_preset(args: argparse.Namespace) -> None:
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


def _apply_ingest_runner_finalize_agent_preset(args: argparse.Namespace) -> None:
    if args.ingest_runner_finalize_agent:
        args.ingest_runner_finalize = True
        if not args.ingest_runner_dir:
            args.ingest_runner_dir = ".claude/tmp/ingest_runner"


def apply_agent_presets(args: argparse.Namespace) -> None:
    _apply_lint_agent_preset(args)
    _apply_status_agent_preset(args)
    _apply_query_agent_preset(args)
    _apply_ingest_agent_preset(args)
    _apply_ingest_batch_agent_preset(args)
    _apply_ingest_runner_agent_preset(args)
    _apply_ingest_runner_finalize_agent_preset(args)


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    direct_rules = [
        (args.lint_safe_fix and not args.lint_report, "--lint-safe-fix requires --lint-report"),
        (
            args.lint_fail_on_manual and not args.lint_report,
            "--lint-fail-on-manual requires --lint-report",
        ),
        (
            bool(args.lint_output_file) and not args.lint_report,
            "--lint-output-file requires --lint-report",
        ),
        (args.lint_max_gaps < 0, "--lint-max-gaps must be >= 0"),
        (args.lint_max_gap_pages < 1, "--lint-max-gap-pages must be >= 1"),
        (
            args.query_prep and not args.query_question.strip(),
            "--query-prep requires --query-question",
        ),
        (args.query_log and not args.query_prep, "--query-log requires --query-prep"),
        (
            bool(args.query_output_file) and not args.query_prep,
            "--query-output-file requires --query-prep",
        ),
        (args.query_result_pages < 0, "--query-result-pages must be >= 0"),
        (
            bool(args.query_merge_qmd) and not args.query_prep,
            "--query-merge-qmd requires --query-prep",
        ),
        (
            bool(args.status_output_file) and not args.status_report,
            "--status-output-file requires --status-report",
        ),
        (args.ingest_prep and not args.source.strip(), "--ingest-prep requires --source"),
        (
            bool(args.ingest_output_file)
            and not (
                args.ingest_report or args.ingest_prep or args.ingest_batch or args.ingest_runner
            ),
            (
                "--ingest-output-file requires --ingest-report, --ingest-prep, "
                "--ingest-batch, or --ingest-runner"
            ),
        ),
        (
            args.ingest_finalize and not args.ingest_finalize_file.strip(),
            "--ingest-finalize requires --ingest-finalize-file",
        ),
    ]
    for condition, message in direct_rules:
        if condition:
            parser.error(message)

    if args.query_filed:
        if not args.query_filed_page.strip():
            parser.error("--query-filed requires --query-filed-page")
        if not args.query_filed_from_query.strip():
            parser.error("--query-filed requires --query-filed-from-query")

    conflict_pairs = [
        ("status_report", "ingest_report", "--status-report", "--ingest-report"),
        ("synthesize_report", "query_prep", "--synthesize-report", "--query-prep"),
        ("synthesize_report", "lint_report", "--synthesize-report", "--lint-report"),
        ("synthesize_report", "ingest_report", "--synthesize-report", "--ingest-report"),
        ("synthesize_report", "status_report", "--synthesize-report", "--status-report"),
        ("ingest_batch", "ingest_prep", "--ingest-batch", "--ingest-prep"),
        ("ingest_runner", "ingest_prep", "--ingest-runner", "--ingest-prep"),
        ("ingest_runner", "ingest_batch", "--ingest-runner", "--ingest-batch"),
    ]
    for ingest_mode, mode_label in (
        ("ingest_prep", "--ingest-prep"),
        ("ingest_batch", "--ingest-batch"),
        ("ingest_runner", "--ingest-runner"),
    ):
        conflict_pairs.extend(
            [
                (ingest_mode, "ingest_report", mode_label, "--ingest-report"),
                (ingest_mode, "status_report", mode_label, "--status-report"),
                (ingest_mode, "lint_report", mode_label, "--lint-report"),
                (ingest_mode, "query_prep", mode_label, "--query-prep"),
                (ingest_mode, "synthesize_report", mode_label, "--synthesize-report"),
            ]
        )
    for left_attr, right_attr, left_label, right_label in conflict_pairs:
        if getattr(args, left_attr) and getattr(args, right_attr):
            parser.error(f"{left_label} cannot be combined with {right_label}")

    if args.ingest_runner_finalize:
        other_modes = [
            args.ingest_prep,
            args.ingest_batch,
            args.ingest_runner,
            args.ingest_report,
            args.ingest_finalize,
            args.status_report,
            args.lint_report,
            args.query_prep,
            args.synthesize_report,
        ]
        if any(other_modes):
            parser.error(
                "--ingest-runner-finalize cannot be combined with other report or prep flags"
            )


def create_parser() -> argparse.ArgumentParser:
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
            "Agent preset for batch ingest preflight: implies --ingest-batch, "
            "defaults to JSON output, "
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
            "Agent preset for ingest runner mode: implies --ingest-runner, "
            "defaults to JSON output, "
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
        help=(
            "With --ingest-runner-finalize, path to the runner checkpoint directory "
            "(default: .claude/tmp/ingest_runner)"
        ),
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
        help=(
            "With --ingest-prep, source path relative to repo root "
            "(for example raw/factions/Foo.md)"
        ),
    )
    parser.add_argument(
        "--ingest-output-file",
        default="",
        help=(
            "With --ingest-report, --ingest-prep, or --ingest-batch, write output to this path "
            "instead of stdout; commonly used by ingest agent presets"
        ),
    )
    parser.add_argument(
        "--ingest-checkpoint-dir",
        default="",
        help=(
            "With --ingest-runner, directory where per-source prep/finalize "
            "checkpoint paths are staged"
        ),
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
            "With --lint-report, write report to this path; "
            "defaults to .claude/tmp/lint_report.<format>"
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
        "--query-merge-qmd",
        default="",
        metavar="JSON_FILE",
        help=(
            "With --query-prep, path to a JSON file containing QMD semantic search results "
            "(list of {rel_path, score, snippet?} objects). Results are merged into the "
            "candidate ranking: existing candidates get a score boost, new candidates are added. "
            "Sets qmd_merged=true in the output."
        ),
    )
    parser.add_argument(
        "--query-filed",
        action="store_true",
        help=(
            "Append a FILED log entry for a synthesis page written back to the wiki. "
            "Requires --query-filed-page and --query-filed-from-query. "
            "Does not require --query-prep."
        ),
    )
    parser.add_argument(
        "--query-filed-page",
        default="",
        help="With --query-filed, the relative path of the synthesis page that was filed.",
    )
    parser.add_argument(
        "--query-filed-from-query",
        default="",
        help="With --query-filed, the original query that generated the synthesis.",
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
    return parser
