---
name: llm-wiki
description: >
  The foundational knowledge distillation pattern for building and maintaining an AI-powered Obsidian wiki.
  Based on Andrej Karpathy's LLM Wiki architecture. Use this skill whenever the user wants to understand the
  wiki pattern, set up a new knowledge base, or needs guidance on the three-layer architecture (raw sources →
  wiki → schema). Also use when discussing knowledge management strategy, wiki structure decisions, or how
  to organize distilled knowledge. This is the "theory" skill — other skills handle specific operations
  (ingesting, querying, linting).
---

# LLM Wiki — Knowledge Distillation Pattern

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

## Architecture (brief)

- **`raw/`** — Original GM source documents. Read-only. Never touch.
- **`content/`** — LLM-maintained wiki: entity pages organized in category subdirs, interconnected with `[[wikilinks]]`, each with YAML frontmatter.
- **`.claude/`** — Schema layer: skills, rules, bin tools that govern how the wiki operates.

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
| Lint check | `python .claude/bin/wiki_guard.py --lint-agent` |
| Lint + auto-fix safe issues | `python .claude/bin/wiki_guard.py --lint-agent --lint-safe-fix` |
| Query prep | `python .claude/bin/wiki_guard.py --query-agent --query-question "your question"` |
| Synthesis scan | `python .claude/bin/wiki_guard.py --synthesize-report` |

Always prefer `--agent` variants over `--report` variants — they emit machine-readable JSON structured for agent consumption.

## Retrieval Primitives (Claude Code tools)

Use the cheapest tool that answers the question. Escalate only when the cheaper one falls short.

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

## Page Template

```markdown
---
title: Entity Name
category: entities
tags: [npc, pirate, faction_allied]
aliases: [alternate name]
sources: [raw/npcs/entity_name.md]
summary: One or two sentences ≤200 chars — lets other skills preview without opening the page.
provenance:
  extracted: 0.75
  inferred: 0.20
  ambiguous: 0.05
created: 2026-04-27T00:00:00Z
updated: 2026-04-27T00:00:00Z
---

# Entity Name

One-paragraph overview.

## Key Facts

- Direct claim from source.
- Synthesized implication not stated explicitly. ^[inferred]
- Claim two sources disagree on. ^[ambiguous]

## Connections

- [[related_entity]] — relationship description

## Sources

- [[references/source_doc]] — provenance note
```

### Provenance markers

| State | Marker | When |
|-------|--------|------|
| Extracted | *(none — default)* | Paraphrase of what a source says |
| Inferred | `^[inferred]` | LLM synthesis / implication |
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

Load the relevant skill before starting any structured operation:

| Operation | Skill |
|-----------|-------|
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
