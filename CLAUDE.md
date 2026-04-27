# LLM-Wiki: shattered_sea

## Domain Purpose

A persistent, compounding knowledge base for the Shattered Sea campaign — lore, factions, entities, locations, and emergent story threads.

## Architecture

- `raw/` — Immutable source archive. READ ONLY. Never modify, move, or delete files here. Drop all source documents here before ingesting.
- `archives/` — Snapshots of the wiki taken before rebuild/restore operations. Never delete.
- `content/` — Agent-managed knowledge graph. Pages live in category subdirectories:
  - `concepts/` — Ideas, theories, mental models
  - `entities/` — People, orgs, tools, projects
  - `skills/` — How-to knowledge, procedures
  - `references/` — Summaries of specific sources
  - `synthesis/` — Cross-cutting analysis built from multiple sources
  - `journal/` — Timestamped observations and session logs
  - `projects/` — Per-project scoped knowledge (one subdir per project)
- `index.md` — Master entity catalog. Read this first before any query or ingestion.
- `log.md` — Append-only audit trail. Append after every ingestion; never edit prior entries.
- `hot.md` — Semantic snapshot of recent activity (~500 words). Update after every major write.
- `.claude/rules/` — Modular rule files loaded contextually by file path.
- `.claude/memory/` — Persistent session memory. Read `MEMORY.md` at every session start.

## Session Memory

At the start of every session, read `.claude/memory/MEMORY.md` before doing anything else.
Before context compression or session end, checkpoint any important decisions to `.claude/memory/`
using the memory file types (user / feedback / project / reference). Use
`/llm-wiki:persistent-memory-management` for the full protocol.

## Core Commands

- **Ingest**: `/llm-wiki:ingest [filename]` — Process a new document from raw/
- **Query**: `/llm-wiki:query [question]` — Answer a question using the wiki
- **Status**: `/llm-wiki:wiki-status` — See what's been ingested, what's pending, wiki health
- **Update**: `/llm-wiki:wiki-update` — Sync current project's knowledge into the wiki
- **Synthesize**: `/llm-wiki:wiki-synthesize` — Find and fill synthesis gaps across the wiki
- **Lint**: `/llm-wiki:lint` — Health-check for orphans, dead links, contradictions
- **Rebuild**: `/llm-wiki:wiki-rebuild` — Archive and rebuild from scratch, or restore

## Obsidian Tools

These trigger automatically when the relevant context arises — no need to call them manually.
- **`/llm-wiki:obsidian-markdown`** — Use when writing or editing any wiki page. Covers wikilinks, callouts, embeds, properties, and Obsidian-specific formatting rules.
- **`/llm-wiki:obsidian-bases`** — Use when creating index, dashboard, or aggregation pages. Creates `.base` files for dynamic, frontmatter-driven views instead of static tables.
- **`/llm-wiki:obsidian-cli`** — Use when interacting with a running Obsidian instance: reading, creating, appending, renaming, or searching notes via the `obsidian` CLI.
- **`/llm-wiki:obsidian-automation`** — Use for multi-step vault operations: batch note creation, bulk property updates, post-ingest cleanup sequences.
- **`/llm-wiki:obsidian-json-canvas`** — Use when creating or editing `.canvas` files: mind maps, flowcharts, and relationship diagrams embedded in synthesis pages.

## Meta-Capabilities

Use these when you hit a gap in what the plugin can do.
- **`/llm-wiki:persistent-memory-management`** — Session continuity across context resets. Checkpointing, daily synthesis, and memory structure. Use at session start, before context compression, and end of day.
- **`/llm-wiki:writing-plans`** — Write a comprehensive implementation plan before executing complex or multi-step vault operations. Plans are saved to `.claude/plans/`.
- **`/llm-wiki:executing-plans`** — Execute a written plan task-by-task with verification at every step.
- **`/llm-wiki:systematic-debugging`** — Root-cause-first debugging protocol for any vault error, broken link, or validation failure.
- **`/llm-wiki:verification-before-completion`** — Gate function: run verification commands and read output before claiming any operation is complete.
- **`/llm-wiki:context-fundamentals`** — Context engineering principles: attention budget, token positioning, progressive loading. Use when designing agent systems or optimizing how information is structured in context.
- **`/llm-wiki:context-compression`** — Compression strategies for long-running wiki sessions. Use when sessions span large ingestion batches or approach context limits.
- **`/llm-wiki:find-skills`** — Search the open agent skills ecosystem (`skills.sh`) for an existing skill when you need a capability this plugin doesn't cover. Check here before building anything from scratch.
- **`/llm-wiki:skill-creator`** — Create and iteratively improve a new skill when `find-skills` turns up nothing. The full creation loop: draft → test → eval → refine.

## Absolute Constraints

1. NEVER modify or delete any file in `raw/`. Read access only.
2. ALWAYS read `index.md` before any ingestion or query — never traverse blindly.
3. ALWAYS use snake_case for ALL file names, directory names, and YAML keys.
4. ALWAYS write valid YAML frontmatter at the top of every wiki entity page.
5. ALWAYS append to `log.md` after every ingestion — never skip this step.
6. NEVER flatten a wiki entity page. Each page covers exactly ONE concept.
7. ALWAYS weave bidirectional wiki-links `[[entity_name]]` between related pages.
8. Always commit your changes to git with a concise, clear message.

## Settings

- File edits within `content/`, `index.md`, `log.md`, and `hot.md` are auto-approved.
- All bash commands outside of `read`, `grep`, `find`, `cat`, and `ls` require confirmation.
- Never run `rm`, `curl`, or any destructive or network command autonomously.
