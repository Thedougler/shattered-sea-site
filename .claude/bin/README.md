# Claude Tooling Bin

Repo-local tooling for Claude Code workflows.

## Quick Start

```bash
./.claude/bin/bootstrap_python_env
./.claude/bin/wiki_guard --help
```

## What Is Here

- `bootstrap_python_env`: creates `.claude/.venv` and installs `.claude/python/requirements.txt`
- `venv_python`: runs Python from `.claude/.venv`
- `venv_pip`: runs pip in `.claude/.venv`
- `wiki_guard`: primary CLI for wiki validation, ingest, status, lint, query prep, and synthesis
- `wiki_guard.py`: compatibility shim for the module CLI
- `wiki_guard_lib/`: implementation modules

## Agent Presets (Recommended)

Use these first in Claude Code. They default to JSON and write outputs to `.claude/tmp/`.

| Preset | Implies | Output file | Notes |
|---|---|---|---|
| `--status-agent` | `--status-report` | `.claude/tmp/status_report.json` | source delta + recommendation |
| `--lint-agent` | `--lint-report` | `.claude/tmp/lint_report.json` | caps gap payloads (`10` gaps, `3` pages each) |
| `--query-agent` | `--query-prep` | `.claude/tmp/query_prep.json` | ranked candidates/snippets for synthesis |
| `--ingest-agent` | `--ingest-prep` | `.claude/tmp/ingest_prep.json` | single-source ingest prep |
| `--ingest-batch-agent` | `--ingest-batch` | `.claude/tmp/ingest_batch.json` | pending-only, limit defaults to `5` |
| `--ingest-runner-agent` | `--ingest-runner` | `.claude/tmp/ingest_runner.json` | pending-only, limit defaults to `5`, writes checkpoints to `.claude/tmp/ingest_runner/` |
| `--ingest-runner-finalize-agent` | `--ingest-runner-finalize` | n/a | finalizes completed runner stubs in `.claude/tmp/ingest_runner/` |

## High-Value Workflows

### 1) Status first

```bash
./.claude/bin/wiki_guard --status-agent
```

### 2) Lint before large edits

```bash
./.claude/bin/wiki_guard --lint-agent
# optional safe auto-fix
./.claude/bin/wiki_guard --lint-report --lint-safe-fix
```

### 3) Query prep for answering questions

```bash
./.claude/bin/wiki_guard --query-agent --query-question "How are the maw and leviathan related?"
```

Useful query flags:

```bash
# fast path: no snippets
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-fast

# hide internal/pii pages
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-public-only

# merge semantic search results from JSON [{rel_path, score, snippet?}]
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-merge-qmd .claude/tmp/qmd.json

# append QUERY audit line
./.claude/bin/wiki_guard --query-prep --query-question "..." --query-log

# mark a filed synthesis page (no --query-prep required)
./.claude/bin/wiki_guard --query-filed \
  --query-filed-page wiki/synthesis/example.md \
  --query-filed-from-query "How are the maw and leviathan related?"
```

### 4) Ingest queue and prep

```bash
# inspect pending ingest work
./.claude/bin/wiki_guard --ingest-report --pending-only --ingest-queue

# prep one source
./.claude/bin/wiki_guard --ingest-agent --source raw/factions/Foo.md

# prep next batch (compact)
./.claude/bin/wiki_guard --ingest-batch-agent

# build sequential runner + checkpoint files
./.claude/bin/wiki_guard --ingest-runner-agent

# finalize completed runner stubs
./.claude/bin/wiki_guard --ingest-runner-finalize-agent
```

### 5) Synthesis opportunity discovery

```bash
./.claude/bin/wiki_guard --synthesize-report --synthesize-format json
```

## Finalize Ingest Bookkeeping

Use this when ingest content is complete and you need manifest/log/hot updates.

```bash
./.claude/bin/wiki_guard --ingest-finalize --ingest-finalize-file .claude/tmp/finalize_payload.json
```

## Exit Codes You Should Rely On

- `0`: success
- `1`: validation/runtime error
- `2`: pending/ingest-prep/finalize conditions (for example `--fail-on-pending` or invalid ingest payload state)
- `3`: lint manual-fix categories present when `--lint-fail-on-manual` is set

## Common Constraints

- `--ingest-prep` requires `--source`
- `--query-prep` requires `--query-question`
- `--query-log` requires `--query-prep`
- `--query-merge-qmd` requires `--query-prep`
- `--ingest-finalize` requires `--ingest-finalize-file`
- `--ingest-runner-finalize` cannot be combined with other report/prep modes

## Development and Quality Gates

```bash
./.claude/bin/venv_python -m pre_commit install
./.claude/bin/venv_python -m pre_commit run --all-files
./.claude/bin/venv_python -m pytest
```

Current gates include markdownlint, ruff, mypy, pylint, and pytest with coverage checks.
