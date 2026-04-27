---
name: llm-wiki
description: >
  LOAD FIRST — before any wiki operation. This skill defines the vault layout, CLI quick-reference,
  file naming conventions (snake_case), retrieval primitives (which Claude Code tool at each cost
  tier), and core principles shared by all wiki skills. Load this skill before running ingest, query,
  lint, wiki-status, wiki-synthesize, obsidian-cli, or any other operation inside the wiki — even
  when the user does not mention it explicitly. Also use when the user wants to understand the wiki
  pattern, set up a new knowledge base, or discuss knowledge management strategy.
---

# LLM Wiki — Vault Reference

You are maintaining a persistent, compounding knowledge base. The wiki is a **compiled artifact** — knowledge is distilled once and kept current, not re-derived on every query.

## This Vault at a Glance

| Fact | Value |
|------|-------|
| Content root | `content/` (not `wiki/`) |
| Filename convention | `snake_case.md` |
| Index | `content/index.md` — read first, always |
| Hot cache | `content/hot.md` — session state |
| Sources (immutable) | `raw/` — never modify |
| CLI tool | `python .claude/bin/wiki_guard.py [--flag]` |

**Layout guard:** `wiki_guard.py` auto-detects `content/` vs `wiki/` layout. All commands route index/log/hot writes to the correct path — never hardcode `wiki/`.

## Vault Structure

```
content/
├── index.md          ← master entity catalog (read first before any op)
├── hot.md            ← session state / recent activity snapshot
├── log.md            ← append-only operation audit trail
├── concepts/         ← ideas, mechanics, theories
├── entities/         ← NPCs, factions, items, ships, spells, locations
├── references/       ← summaries of specific source documents
├── synthesis/        ← cross-cutting analysis across multiple sources
├── journal/          ← timestamped session logs and observations
└── projects/         ← per-project scoped knowledge (one subdir per project)
raw/                  ← immutable source material (READ ONLY)
```

**File naming:** Always `snake_case.md`. No spaces, no kebab-case.

## wiki_guard.py — CLI Quick Reference

All structured wiki operations go through the CLI. Run from the repo root.

| Task | Command |
|------|---------|
| Ingest status (what's pending) | `python .claude/bin/wiki_guard.py --status-agent` |
| Ingest preflight for one source | `python .claude/bin/wiki_guard.py --ingest-agent --source raw/path/to/file.md` |
| Finalize a completed ingest | `python .claude/bin/wiki_guard.py --ingest-finalize --ingest-finalize-file <payload.json>` |
| Batch ingest queue | `python .claude/bin/wiki_guard.py --ingest-batch-agent` |
| Runner (ordered batch with checkpoints) | `python .claude/bin/wiki_guard.py --ingest-runner-agent` |
| Runner finalize (all pending stubs) | `python .claude/bin/wiki_guard.py --ingest-runner-finalize-agent` |
| Lint check | `python .claude/bin/wiki_guard.py --lint-agent` |
| Lint + auto-fix safe issues | `python .claude/bin/wiki_guard.py --lint-agent --lint-safe-fix` |
| Query prep | `python .claude/bin/wiki_guard.py --query-agent --query-question "your question"` |
| Synthesis scan | `python .claude/bin/wiki_guard.py --synthesize-report` |

Always prefer `--agent` variants over `--report` variants — they emit machine-readable JSON structured for agent consumption.

## Retrieval Primitives (Claude Code tools)

Use the cheapest tool that answers the question. Escalate only when needed.

| Need | Claude Code Tool | Cost |
|------|-----------------|------|
| Does a page exist? Is it in the index? | `read_file` → `content/index.md` | **Cheapest** |
| Find pages matching a concept/keyword | `grep_search` with `includePattern: "content/**"` | **Cheap** |
| Preview a page (title, tags, summary) | `read_file` frontmatter lines only (startLine/endLine) | **Cheap** |
| Locate a specific claim inside a page | `grep_search` with term scoped to file path | **Medium** |
| Find files by name pattern | `file_search` with glob | **Medium** |
| Semantic / conceptual search across vault | `semantic_search` | **Medium** |
| Full page content | `read_file` entire file | **Expensive** — last resort |
| Wikilink graph / backlinks | `grep_search` for `\[\[entity_name\]\]` in `content/**` | Case-by-case |

**Parallel reads are free:** when gathering context from multiple independent pages, call `read_file` on all of them in the same tool turn rather than serializing.

**The rule:** if `summary:` frontmatter fields answer the question, skip the page body. A 500-line page opened to read 15 lines wastes 485 lines of context.

## Provenance Markers

Apply these inline on every wiki page body. The `ingest` skill owns the full page template — these markers apply to all content-writing operations.

| State | Marker | When |
|-------|--------|------|
| Extracted | *(none — default)* | Paraphrase of what a source says |
| Inferred | `^[inferred]` | LLM synthesis / implication not stated in source |
| Ambiguous | `^[ambiguous]` | Sources conflict or source is unclear |

## Core Principles

1. **Compile, don't retrieve.** Ingest updates every relevant page, not just the source summary.
2. **Compound over time.** Merge new info into existing pages; don't create duplicates.
3. **Mark inferences.** Unmarked = extracted. `^[inferred]` and `^[ambiguous]` keep the wiki trustworthy.
4. **Always check index first.** Read `content/index.md` before creating any page — duplicates silently diverge.
5. **One file at a time to completion.** Read → write → verify → move on. Don't batch-plan writes across files.
6. **Never modify `raw/`.** It is the immutable source of truth.
7. **Commit after every write.** The vault must be in a valid, committed state before responding.

## Skill Reference

Load the relevant skill before starting any structured operation. This skill (`llm-wiki`) is always the first to load.

| Operation | Next skill to load |
|-----------|-------------------|
| Ingest a source doc | `ingest` |
| Answer a question | `query` |
| Health check | `lint` |
| Wiki status / delta | `wiki-status` |
| Find synthesis gaps | `wiki-synthesize` |
| Write wiki pages | `obsidian-markdown` |
| Create base views | `obsidian-bases` |
| Create canvas files | `obsidian-json-canvas` |
| Obsidian CLI ops | `obsidian-cli` |
| Session continuity | `persistent-memory-management` |
| Long ingest sessions | `context-compression` |
| Complex multi-step ops | `writing-plans` → `executing-plans` |
| Debug vault errors | `systematic-debugging` |
| Claim something is done | `verification-before-completion` |
