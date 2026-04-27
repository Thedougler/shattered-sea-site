---
name: lint
description: >
  Health-check an LLM-wiki domain for structural and semantic decay. Detects orphan pages,
  dead wiki-links, index gaps, stale pages, unresolved contradictions, and high-frequency
  entity mentions without dedicated pages. Use when the user says "lint the wiki", "check
  the wiki health", "find broken links", "what needs fixing", or on a scheduled basis.
---

# LLM-Wiki Lint Skill

**Critical constraint: Report first. Never silently fix anything. Always show findings and
ask before making any changes.**

## Step 1 — Run the CLI

`wiki_guard --lint-agent` is the primary execution path. It handles layout detection,
template filtering, wikilink normalization, and token-efficient JSON output. Do not manually
traverse the wiki.

| $ARGUMENTS | Command |
|---|---|
| (empty) or `report` | `./.claude/bin/wiki_guard --lint-agent` |
| `<category>` | `./.claude/bin/wiki_guard --lint-agent --lint-category <category>` |
| `fix` | `./.claude/bin/wiki_guard --lint-agent --lint-safe-fix` |

Valid categories: `orphans`, `dead_links`, `index`, `stale`, `contradictions`, `gaps`

Override defaults only when needed:
- Different output path: add `--lint-output-file <path>`
- More gap results: add `--lint-max-gaps 25 --lint-max-gap-pages 5`
- Raw flags without preset: `--lint-report --lint-format json`

**Pre-flight**: Confirm `CLAUDE.md` exists. If not, tell the user to scaffold first.
Layout detection and index reading are handled by the CLI.

**If `wiki_guard` is unavailable or exits with a parse/runtime error**, invoke
`wiki-tooling-fixer` rather than falling back to manual traversal.

## Step 2 — Read the Report

The CLI writes JSON to `.claude/tmp/lint_report.json` and prints a concise summary to stdout.

1. Read the stdout summary.
2. Read only `manual_required` and `safe_auto_fixable` from the JSON — do not load full
   category payloads unless the user asks to drill into a specific category.
3. If template placeholders, malformed escaped wikilinks, or layout mismatches appear in
   the report, treat it as a tooling defect → invoke `wiki-tooling-fixer`.

## Step 3 — Present Findings and Ask

After reading the report, present findings to the user in this format:

```
Found <N> issues across <N> categories.

Safe to auto-fix (structure only, no content changes):
  ✅ Index gaps — add missing index entries for existing wiki files (wiki_ghosts only)

Requires judgment (I'll suggest, you confirm each):
  ⚠️  Orphan pages — suggest link targets
  ⚠️  Typo-likely dead links — suggest correct target

Cannot auto-fix (human arbitration required):
  ❌ Contradictions — requires you to read and decide
  ❌ Stale pages — requires re-ingestion or manual verification

Shall I proceed with safe auto-fixes? [yes / no / show me each one]
```

Only proceed after explicit confirmation.

## Step 4 — After Fixing

Append to `log.md`:

```markdown
## <YYYY-MM-DD HH:MM> — Lint Pass

**Issues found**: <N>
**Auto-fixed**: <N> (orphans: <N>, dead links: <N>, index: <N>)
**Requires human review**: <N> (contradictions: <N>, stale: <N>)
**Entity gaps identified**: <N> (not auto-fixed)
```
