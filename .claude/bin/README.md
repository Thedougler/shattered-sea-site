# Claude Tooling Bin

This directory contains repo-local tooling optimized for Claude Code and llm-wiki maintenance.

## Quick Start

1. Bootstrap the Python environment:

   ```bash
   ./.claude/bin/bootstrap_python_env
   ```

2. Run wiki validation:

   ```bash
   ./.claude/bin/wiki_guard
   ```

## Tools

- `bootstrap_python_env`:
  Creates `.claude/.venv` using `uv` when available (fallback to `python3 -m venv`), then installs `.claude/python/requirements.txt`.
- `venv_python`:
  Runs Python from `.claude/.venv` without manual activation.
- `venv_pip`:
  Runs `pip` in `.claude/.venv`.
- `wiki_guard.py`:
  Compatibility CLI shim that exposes `wiki_guard_lib.core` as a stable entrypoint.
- `wiki_guard`:
  Wrapper around `wiki_guard.py` via `venv_python`.
- `wiki_guard_lib/`:
  Importable module that contains lint, ingest-status, and validation logic used by both CLI and tests.

Current module map:

- `wiki_guard_lib/synthesis_audit.py`: co-occurrence ranking and synthesis-gap candidate discovery.

## Python Tooling Pattern (for Claude + human maintainers)

Use this structure for all future tooling under `.claude/bin/`:

- Keep shell wrappers stable and tiny.
- Keep Python CLI files thin (argument parsing and command routing only).
- Put reusable logic in importable modules (example: `wiki_guard_lib/core.py`).
- Write tests against module functions, not shell wrappers.
- Preserve backward compatibility at entrypoints whenever refactoring internals.

Recommended extension flow:

1. Add pure helper functions first (deterministic, typed, no side effects).
2. Add data models (`@dataclass`) for new report shapes.
3. Add/expand tests for new behavior before wiring CLI options.
4. Add CLI flags in `main()` only after helper behavior is verified.
5. Update docs + examples in this file as part of the same change.

Claude Code iteration workflow for tooling changes:

1. Use `/llm-wiki:writing-plans` before multi-step refactors.
2. Use `/llm-wiki:systematic-debugging` when behavior diverges from expectations.
3. Use `/llm-wiki:verification-before-completion` before declaring success.
4. Keep changes small and reversible; avoid combining refactor + feature + format-only edits.

Testing standards:

- Test library functions directly.
- Cover command-line routing via `main()` tests by monkeypatching `sys.argv`.
- Include regression tests for malformed input and invalid YAML.
- Keep coverage gate at 90% or higher for tooling modules.

Refactor safety rules:

- Preserve command compatibility for existing wrappers and flags.
- Refactor internals before adding new behavior when complexity rises.
- Avoid mixed commits that combine broad refactor and unrelated features.
- If a refactor changes user-visible output, update tests and docs in the same change.

Extension checklist:

1. Add or update dataclasses in the module.
2. Add helper functions with typed signatures.
3. Add tests for helper behavior.
4. Wire CLI arguments in `main()`.
5. Add documentation examples to this README.
6. Run tests and verify coverage.

## Ingest Preflight Utility

Use `wiki_guard` to decide what to ingest next from `raw/` based on `.manifest.json` hashes.

```bash
./.claude/bin/wiki_guard --ingest-report
```

Useful options:

```bash
# Show only sources that need ingest (new or changed)
./.claude/bin/wiki_guard --ingest-report --pending-only

# Machine-readable output for agent workflows
./.claude/bin/wiki_guard --ingest-report --format json

# Limit number of displayed rows
./.claude/bin/wiki_guard --ingest-report --pending-only --limit 5

# Emit a one-command ordered ingest queue for all pending sources
./.claude/bin/wiki_guard --ingest-report --pending-only --ingest-queue

# Exit non-zero if pending sources exist (automation/CI gate)
./.claude/bin/wiki_guard --ingest-report --pending-only --fail-on-pending
```

Report behavior:

- Computes current SHA-256 for all files under `raw/`
- Compares against `.manifest.json` `content_hash`
- Classifies each source as `new`, `changed`, or `unchanged`
- Recommends next source by smallest pending file (fastest ingest-first)
- Optionally emits a one-command queue to ingest all pending sources in order
- Can act as a strict gate with `--fail-on-pending` (exit code 2 when pending exists)

## Wiki Status Utility

Use `wiki_guard` status mode for a skill-aligned status/delta audit across current sources and
`.manifest.json`.

```bash
# Agent preset: JSON report on disk + concise stdout summary
./.claude/bin/wiki_guard --status-agent

# Human-readable status report
./.claude/bin/wiki_guard --status-report

# JSON output for agent workflows
./.claude/bin/wiki_guard --status-report --status-format json

# Show only pending (new/modified) sources
./.claude/bin/wiki_guard --status-report --pending-only
```

Agent-oriented defaults for `--status-agent`:

- Implies `--status-report`
- Defaults `--status-format` to `json`
- Writes report to `.claude/tmp/status_report.json`
- Prints a concise stdout summary with `new`, `modified`, `deleted`, and `recommendation`
- Preserves explicit overrides when you pass them

Status behavior:

- Reads `.env` for `OBSIDIAN_SOURCES_DIR` and `CLAUDE_HISTORY_PATH`
- Scans configured sources and Claude history files
- Compares current files to `.manifest.json`
- Classifies each source as `new`, `modified`, `touched`, `unchanged`, or `deleted`
- Computes visibility tally from wiki frontmatter tags (`visibility/internal`, `visibility/pii`)
- Emits deterministic recommendation (`append`, `rebuild`, `lint_first`, `full_ingest`, `no_action`)

Separation of duties:

- Tooling should perform deterministic inventory/delta computation and emit compact machine output
- Claude should use tool output for synthesis, tradeoff framing, and user-facing decisions

## Wiki Synthesis Utility

Use synthesis mode to offload co-occurrence discovery and ranking so Claude can focus on writing
high-quality synthesis pages.

```bash
# Human-readable candidate report
./.claude/bin/wiki_guard --synthesize-report

# JSON output for agent workflows
./.claude/bin/wiki_guard --synthesize-report --synthesize-format json

# Topic-focused ranking
./.claude/bin/wiki_guard --synthesize-report --synthesize-topic "drowned maw"
```

Useful options:

```bash
# Control breadth of co-occurrence scanning
./.claude/bin/wiki_guard --synthesize-report --synthesize-pair-limit 40

# Control top and skipped candidate counts
./.claude/bin/wiki_guard --synthesize-report --synthesize-top-candidates 5 --synthesize-skipped-limit 10
```

Synthesis behavior:

- Scans non-special wiki pages for outgoing wikilinks
- Builds pairwise co-occurrence counts based on shared source pages
- Detects pairs already covered by existing `synthesis/` pages
- Scores candidates with deterministic signals (co-occurrence, cross-domain, shared tags, hub, contradiction)
- Emits top candidates plus high-value skipped pairs for next run planning

Separation of duties:

- Tooling should discover and rank synthesis opportunities deterministically
- Claude should draft synthesis narratives, trade-offs, and open questions

## Lint Workflow Utility

Use `wiki_guard` lint mode to run the LLM-wiki lint skill checks with explicit workflow boundaries.

```bash
# Agent preset: JSON report on disk + concise stdout + capped gap payloads
./.claude/bin/wiki_guard --lint-agent

# Full lint report (report-first workflow)
./.claude/bin/wiki_guard --lint-report

# Category-only report (orphans, dead_links, index, stale, contradictions, gaps)
./.claude/bin/wiki_guard --lint-report --lint-category index

# Machine-readable report for Claude Code automation
./.claude/bin/wiki_guard --lint-report --lint-format json

# Apply only safe, idempotent auto-fixes
./.claude/bin/wiki_guard --lint-report --lint-safe-fix

# Return non-zero if manual work is still required
./.claude/bin/wiki_guard --lint-report --lint-fail-on-manual
```

Agent-oriented defaults for `--lint-agent`:

- Implies `--lint-report`
- Defaults `--lint-format` to `json`
- Writes report to `.claude/tmp/lint_report.json`
- Caps gap payloads to `--lint-max-gaps 10 --lint-max-gap-pages 3`
- Preserves explicit overrides when you pass them

Responsibility split:

- Safe automatic fixes (idempotent):
  - Add missing index rows for wiki files that exist but are absent from `index.md` (`wiki_ghosts`)
- Manual fixes only (reported, never auto-applied):
  - Orphans
  - Dead links
  - Contradictions
  - Stale pages
  - Index ghosts
  - Entity gaps

## Query Workflow Utility

Use `wiki_guard` query mode to offload retrieval prep work that is expensive in agent context windows.

```bash
# Agent preset: JSON report on disk + concise stdout summary
./.claude/bin/wiki_guard --query-agent --query-question "What is the relationship between the maw and leviathan?"

# Build a ranked candidate set for a user question
./.claude/bin/wiki_guard --query-prep --query-question "What is the relationship between the maw and leviathan?"

# JSON output for Claude Code automation
./.claude/bin/wiki_guard --query-prep --query-question "Compare Dravosi Crown and Sentinels" --query-format json

# Fast index/frontmatter-only path (skip snippet extraction)
./.claude/bin/wiki_guard --query-prep --query-question "Quick answer: Umberlee" --query-fast

# Public-facing filter (exclude internal and pii-tagged pages)
./.claude/bin/wiki_guard --query-prep --query-question "User-facing summary of the maw" --query-public-only

# Append Phase-5 query audit log entry automatically
./.claude/bin/wiki_guard --query-prep --query-question "What is the relationship between the maw and leviathan?" --query-log

# Mark broad-grep escalation and override result_pages when needed
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-log --query-result-pages 6 --query-escalated
```

Useful options:

```bash
# Control candidate breadth
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-top-k 8

# Tune snippet extraction from candidate pages
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-snippet-context 3 --query-max-snippets 3
```

Agent-oriented defaults for `--query-agent`:

- Implies `--query-prep`
- Defaults `--query-format` to `json`
- Writes report to `.claude/tmp/query_prep.json`
- Prints a concise stdout summary with query type, mode, and candidate counts
- Preserves explicit overrides when you pass them

Separation of duties:

- `wiki_guard --query-prep` should do deterministic, token-expensive prep work:
  - index/frontmatter scanning
  - candidate ranking
  - secondary link expansion
  - targeted snippet extraction (frontmatter stripped)
  - source metadata extraction (`source_count`, `source_refs`)
  - optional query audit log append (`--query-log`)
- Claude Code should do synthesis work:
  - answer composition
  - caveat framing
  - contradiction handling
  - deciding whether to file back a synthesis page

## Strict Mode

Run with warnings treated as failures:

```bash
./.claude/bin/wiki_guard --strict
```

## Pyright LSP Integration

This repository enables the official Claude plugin `pyright-lsp@claude-plugins-official` in [../settings.json](../settings.json).

The plugin requires the `pyright` binary in your PATH. Install with:

```bash
npm install -g pyright
```

Verify installation:

```bash
pyright --version
pyright-langserver --help
```

## Quality Gates

This repository uses `pre-commit` as the Git quality gate runner.

Installed checks:

- `markdownlint` for markdown style in `wiki/**/*.md` and `.claude/bin/*.md`
- `ruff` + `ruff-format` for Python lint/format in `.claude/bin/*.py`
- Ruff complexity checks (cyclomatic complexity and branch/statement/argument thresholds)
- `mypy` for Python typing in `.claude/bin/*.py`
- `pylint` design checks for oversized files/functions and related maintainability limits
- `pytest` for regression tests in `tests/`, with coverage gate on `wiki_guard.py`

Install and run:

```bash
./.claude/bin/bootstrap_python_env
./.claude/bin/venv_python -m pre_commit install
./.claude/bin/venv_python -m pre_commit run --all-files
```

Target a specific file:

```bash
./.claude/bin/venv_python -m pre_commit run --files .claude/bin/wiki_guard.py
```

Run tests directly:

```bash
./.claude/bin/venv_python -m pytest
```

Coverage is enforced by pytest args in `pyproject.toml` via:

- `--cov=wiki_guard`
- `--cov=wiki_guard_lib`
- `--cov-fail-under=90`
