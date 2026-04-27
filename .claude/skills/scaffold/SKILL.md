---
name: scaffold
description: >
  Scaffold a new LLM-wiki domain from scratch. Creates the full tri-layer directory
  structure (raw/, wiki/, .claude/), generates CLAUDE.md, index.md, log.md, hot.md,
  .env, .obsidian/ config, and all modular rule files. Use when a user says "scaffold
  a wiki", "create a new wiki domain", "set up an llm-wiki", "initialize a knowledge
  base for [topic]", or "set up my wiki", "initialize obsidian", "create a new vault".
---

# LLM-Wiki Scaffold Skill

> **Prerequisite:** Load the `llm-wiki` skill before this one. Vault layout, file naming conventions, and CLI reference are defined there.

You are an autonomous librarian and knowledge architect. Your task is to scaffold a new
LLM-wiki domain — a persistent, compounding knowledge base following the Karpathy pattern.

## Input

The user will provide one of:
- A domain name (e.g., "machine_learning", "maritime_law", "dnd_lore")
- A topic description (convert to snake_case for all file/folder names)
- A target path (e.g., "~/wikis/machine_learning" or relative path)
- $ARGUMENTS — parse this for domain name and optional target path

**File naming convention: ALWAYS use snake_case for ALL directories, files, and YAML keys.
Never use kebab-case or spaces. This is mandatory for safe bash traversal.**

## Architecture to Build

Scaffold the following structure at the target path:

```
<domain_root>/
├── .env                          # Environment config (vault path, sources dir, QMD)
├── CLAUDE.md                     # Domain-level schema (primary agent config)
├── raw/                          # IMMUTABLE source archive — agent READ ONLY
│   └── assets/                   # Image attachments (referenced from raw docs)
├── archives/                     # Wiki snapshots for rebuild/restore operations
├── content/                      # Agent-managed synthesized knowledge graph
│   ├── index.md                  # Centralized entity catalog (agent reads this first)
│   ├── log.md                    # Append-only audit trail of all modifications
│   ├── hot.md                    # ~500-word semantic snapshot — updated after every major op
│   ├── concepts/                 # Ideas, theories, mental models
│   ├── entities/                 # People, orgs, tools, projects
│   ├── skills/                   # How-to knowledge, procedures
│   ├── references/               # Summaries of specific sources
│   ├── synthesis/                # Cross-cutting analysis across sources
│   ├── journal/                  # Timestamped observations, session logs
│   └── projects/                 # Per-project scoped knowledge (named subdirs)
├── .obsidian/                    # Obsidian vault recognition and defaults
│   ├── app.json
│   └── appearance.json
└── .claude/
    ├── rules/
    │   ├── ingest_rules.md       # Ingestion workflow — triggered on raw/* paths
    │   ├── wiki_format_rules.md  # Formatting standards — triggered on content/* paths
    │   └── lint_rules.md         # Linting protocol — triggered on index.md or content/*
    ├── memory/
    │   ├── MEMORY.md             # Hot cache of active decisions — read at session start
    │   └── archive/              # Archived decisions and deprecated patterns
    └── plans/                    # Implementation plans created by writing-plans skill
```

## Files to Generate

### 1. CLAUDE.md (domain root)

```markdown
# LLM-Wiki: <DOMAIN_NAME>

## Domain Purpose
<One clear sentence describing what this domain covers.>

## Architecture
- `raw/` — Immutable source archive. READ ONLY. Never modify, move, or delete files here.
- `archives/` — Snapshots of the wiki taken before rebuild/restore operations. Never delete.
- `content/` — Agent-managed knowledge graph. Pages live in category subdirectories:
  - `concepts/` — Ideas, theories, mental models
  - `entities/` — People, orgs, tools, projects
  - `skills/` — How-to knowledge, procedures
  - `references/` — Summaries of specific sources
  - `synthesis/` — Cross-cutting analysis built from multiple sources
  - `journal/` — Timestamped observations and session logs
  - `projects/` — Per-project scoped knowledge (one subdir per project)
- `content/index.md` — Master entity catalog. Read this first before any query or ingestion.
- `content/log.md` — Append-only audit trail. Append after every ingestion; never edit prior entries.
- `content/hot.md` — Semantic snapshot of recent activity (~500 words). Update after every major write.
- `.claude/rules/` — Modular rule files loaded contextually by file path.
- `.claude/memory/` — Persistent session memory. Read `MEMORY.md` at every session start.

## Session Memory
At the start of every session, read `.claude/memory/MEMORY.md` before doing anything else.
Before context compression or session end, checkpoint any important decisions to `.claude/memory/`.

## Core Skills
- **Ingest**: `ingest` skill — Process a new document from raw/
- **Query**: `query` skill — Answer a question using the wiki
- **Status**: `wiki-status` skill — What's been ingested, what's pending, wiki health
- **Synthesize**: `wiki-synthesize` skill — Find and fill synthesis gaps across the wiki
- **Lint**: `lint` skill — Health-check for orphans, dead links, contradictions

> Load the `llm-wiki` skill first before any wiki operation. It defines vault layout,
> CLI reference, retrieval primitives, and core principles shared by all wiki skills.

## Absolute Constraints
1. NEVER modify or delete any file in `raw/`. Read access only.
2. ALWAYS read `content/index.md` before any ingestion or query — never traverse blindly.
3. ALWAYS use snake_case for ALL file names, directory names, and YAML keys.
4. ALWAYS write valid YAML frontmatter at the top of every wiki entity page.
5. NEVER flatten a wiki entity page. Each page covers exactly ONE concept.
6. ALWAYS weave bidirectional wiki-links `[[entity_name]]` between related pages.
7. ALWAYS commit after every write — the vault must be in a valid state before responding.

## Settings
- File edits within `content/`, `.claude/memory/` are auto-approved.
- All bash commands outside of `read`, `grep`, `find`, `cat`, and `ls` require confirmation.
- Never run `rm`, `curl`, or any destructive or network command autonomously.
```

### 2. content/index.md

```markdown
# Index: <DOMAIN_NAME>

> Master entity catalog. Read this file first — always — before any ingestion or query.
> One entry per entity. Format: `| [[entity_file]] | one-line summary | source_count | status | updated |`

## Entity Catalog

| Entity | Summary | Sources | Status | Updated |
|--------|---------|---------|--------|---------|
| *(empty — populate via ingestion)* | | | | |

## Notes
- Source count = number of distinct raw documents informing the page
- Status: `draft` → `active` → `verified` → `contradictory` (flag for human review)
- All entity filenames are snake_case with no spaces or hyphens
```

### 3. content/log.md

```markdown
# Audit Log: <DOMAIN_NAME>

> Append-only chronological record of all wiki modifications.
> Format: `## YYYY-MM-DD HH:MM` followed by bulleted action list.
> Never edit or delete prior entries. Only append.

---

## <SCAFFOLD_DATE>

- [<SCAFFOLD_DATE>T00:00:00Z] INIT domain="<DOMAIN_NAME>" vault_path="<VAULT_PATH>" categories=concepts,entities,skills,references,synthesis,journal,projects
- Structure created: raw/, archives/, wiki/, .obsidian/, .claude/rules/, .claude/memory/
- Files initialized: CLAUDE.md, index.md, log.md, hot.md, .env
- No entities ingested yet.
```

### 4. content/hot.md

```markdown
---
title: Hot Cache
updated: <SCAFFOLD_DATE>
---

# Hot Cache

*A ~500-word semantic snapshot of recent activity. Updated after every major write operation.*

## Recent Activity

- [<SCAFFOLD_DATE>] INIT — wiki domain `<DOMAIN_NAME>` created

## Active Threads

*None yet — start ingesting sources to populate.*

## Key Takeaways

*None yet.*

## Flagged Contradictions

*None yet.*
```

Update `hot.md` after every significant operation by replacing only the sections that changed. Keep it under 500 words. It is a living summary — not a log (that's `log.md`).

### 5. .env (domain root)

Ask the user for each value before writing this file:

1. **Where should the vault live?** → `OBSIDIAN_VAULT_PATH`
   - Default: the path where you are scaffolding right now
   - Must be absolute (expand `~` to full path)

2. **Where are your source documents?** → `OBSIDIAN_SOURCES_DIR`
   - Can be multiple paths, comma-separated
   - Default: leave blank (user can set later)

3. **Want to import Claude conversation history?** → `CLAUDE_HISTORY_PATH`
   - Default: auto-discovers from `~/.claude`
   - Set explicitly if Claude data is elsewhere

4. **Have QMD (semantic search) installed?** → `QMD_WIKI_COLLECTION` / `QMD_PAPERS_COLLECTION`
   - Optional. Enables semantic search in query and source discovery in ingest.
   - Skills fall back to `Grep` automatically when QMD is absent.
   - If unsure, leave blank — can be added later.

```bash
# LLM-Wiki: <DOMAIN_NAME>
# Generated by /llm-wiki:scaffold — edit as needed

OBSIDIAN_VAULT_PATH=<absolute_path>
OBSIDIAN_SOURCES_DIR=
CLAUDE_HISTORY_PATH=

# QMD semantic search (optional — skills fall back to grep if unset)
QMD_WIKI_COLLECTION=
QMD_PAPERS_COLLECTION=
```

### 6. .obsidian/app.json

```json
{
  "strictLineBreaks": false,
  "showFrontmatter": false,
  "defaultViewMode": "preview",
  "livePreview": true
}
```

### 7. .obsidian/appearance.json

```json
{
  "baseFontSize": 16
}
```

### 8. .claude/rules/ingest_rules.md

```markdown
---
paths:
  - raw/**
description: Ingestion workflow rules — active when processing files in raw/
---

# Ingestion Protocol

Execute this protocol EXACTLY and in ORDER for every new raw document.

## Phase 1 — Source Parsing
1. Read the raw document in full.
2. Extract all distinct conceptual entities, themes, and verifiable data points.
3. Identify all proper nouns, technical terms, and named concepts.

## Phase 2 — Index Cross-Reference
4. Read `index.md` to identify which entities already have wiki pages.
5. Classify each discovered entity as: `existing` | `novel`.

## Phase 3 — Wiki Updates (Existing Entities)
6. For each `existing` entity:
   a. Open the entity's wiki page.
   b. Merge new insights into the appropriate sections.
   c. Increment `source_count` in YAML frontmatter by 1.
   d. Update the `updated` field to today's date.
   e. Add any new bidirectional wiki-links `[[related_entity]]`.
   f. If new information contradicts existing claims: set `status: contradictory` and add
      a `## Contradictions` section describing the conflict. Do NOT silently overwrite.

## Phase 4 — Wiki Creation (Novel Entities)
7. For each `novel` entity:
   a. Create `content/<category>/<entity_name_in_snake_case>.md` with full YAML frontmatter.
   b. Write a dense, encyclopedic entity page (minimum 3 sections).
   c. Weave bidirectional wiki-links to all related existing entities.
   d. Add the entity to `content/index.md` with a one-line summary.

## Phase 5 — Audit Log
8. Append a timestamped entry to `content/log.md`:
   - Source file processed
   - Entities updated (list)
   - Entities created (list)
   - Contradictions flagged (list, if any)

## YAML Frontmatter Template (copy for every new entity page)
\`\`\`yaml
---
domain: <domain_name>
type: <concept | guide | comparison | process | person | event | tool>
source_count: 1
status: draft
visibility: private
tags:
  - <tag_1>
  - <tag_2>
related:
  - "[[related_entity_1]]"
  - "[[related_entity_2]]"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
\`\`\`
```

### 9. .claude/rules/wiki_format_rules.md

```markdown
---
paths:
  - content/**
description: Formatting standards — active when writing or editing wiki entity pages
---

# Wiki Entity Page Format

Every page in wiki/ must strictly follow this structure.

## Required YAML Frontmatter
Must appear at the very top. All fields required. Use snake_case for all keys and string values.
See `ingest_rules.md` for the full YAML template.

## Field Definitions
- `domain`: snake_case domain name matching the wiki root folder name
- `type`: one of: concept | guide | comparison | process | person | event | tool
- `source_count`: integer — number of distinct raw/ documents informing this page
- `status`: one of: draft | active | verified | contradictory
- `visibility`: one of: private | restricted | public
- `tags`: list of snake_case thematic tags (minimum 2)
- `related`: list of `[[wiki_links]]` to directly connected entity pages
- `created`: ISO date YYYY-MM-DD of initial page creation
- `updated`: ISO date YYYY-MM-DD of most recent modification

## Page Body Structure
Use markdown headings (##, ###) to segment the page into semantic sections.
Headings act as token boundaries for the LLM — keep them precise.

```
## Overview
One dense paragraph defining the entity. No filler.

## Core Concepts / Details
Substantive content. Use sub-headings as needed.

## Relationships
Explicitly name and [[wiki-link]] all related entities and describe the relationship.

## Sources
Bullet list of raw/ filenames that informed this page.

## Contradictions (if applicable — only when status: contradictory)
Describe the specific conflict and which sources contradict each other.
Flag this section clearly for human review.
```

## Linking Rules
- Use `[[entity_file_name]]` (snake_case, no extension) for all internal wiki links.
- Every page must link to at least 2 other pages in wiki/. No orphan pages.
- When creating a link to an entity that doesn't yet have a page, create a stub immediately.

## Naming
- ALL wiki filenames: snake_case, no hyphens, no spaces, .md extension.
- Example: `neural_network_architecture.md`, NOT `neural-network-architecture.md`
```

### 10. .claude/rules/lint_rules.md

```markdown
---
paths:
  - content/**
  - content/index.md
description: Linting rules — active during health-check operations
---

# Linting Protocol

Execute a complete wiki health-check in this order. Report all findings before making any fixes.

## Step 1 — Orphan Detection
- Scan every file in `content/`
- For each file, check if any other page contains `[[<this_entity>]]`
- Flag any page with zero inbound links as an ORPHAN
- Orphans should be linked to the most semantically related existing pages

## Step 2 — Dead Link Detection
- Scan every content page for `[[wiki_links]]`
- Verify each linked filename exists in `content/`
- Flag any link pointing to a non-existent file as a DEAD LINK
- Create stubs for dead links pointing to entities worth having

## Step 3 — Index Audit
- Compare `content/index.md` entries against actual files in `content/`
- Flag: entities in index.md with no corresponding file
- Flag: files with no index.md entry (add missing entries)

## Step 4 — Staleness Detection
- Review `updated` dates across all wiki pages
- Cross-reference with log.md to find pages not updated in the last 3 ingestion cycles
- Flag stale pages for human review or re-ingestion

## Step 5 — Contradiction Scan
- Search for pages where `status: contradictory`
- List all flagged contradictions for human arbitration
- Do NOT resolve contradictions autonomously — surface them only

## Step 6 — Missing Entity Detection
- Scan wiki pages for entity names (capitalized terms, technical terms, proper nouns)
  that are mentioned frequently but do NOT have dedicated pages
- List high-frequency mentions without pages as ENTITY GAPS

## Lint Report Format
```
# Lint Report — <DOMAIN_NAME> — <DATE>

## Orphan Pages (<count>)
- [[entity_name]] — no inbound links

## Dead Links (<count>)
- [[missing_entity]] referenced in [[source_page]]

## Index Gaps (<count>)
- wiki/entity.md not in index.md

## Stale Pages (<count>)
- [[entity_name]] — last updated <date>

## Contradictions (<count>)
- [[entity_name]] — flagged since <date>

## Entity Gaps (<count>)
- "term_name" — mentioned <N> times, no dedicated page
```

After reporting, ask the human which categories to auto-fix before making changes.
```

## Execution Steps

When the scaffold skill is invoked:

1. Parse $ARGUMENTS for domain name and optional path. If no path given, scaffold in the
   current working directory under a folder named `<domain_name>/`.

2. Convert the domain name to snake_case. Reject any input containing spaces or hyphens
   and convert them automatically (alert the user that you did so).

3. **Configure .env** — Before creating any files, ask the user for environment values
   (see section 5 above). Write `.env` into the domain root with their answers. If the
   user wants to skip any field, leave it blank — skills fall back gracefully.

4. Create every directory and file listed in the architecture above, populating templates
   with the actual domain name and today's date substituted for all placeholders.

   Directories to create:
   - `raw/assets/`
   - `archives/`
   - `content/concepts/`, `content/entities/`, `content/skills/`, `content/references/`,
     `content/synthesis/`, `content/journal/`, `content/projects/`
   - `.obsidian/`
   - `.claude/rules/`
   - `.claude/memory/archive/`
   - `.claude/plans/`

   Files to create: `CLAUDE.md`, `content/index.md`, `content/log.md`, `content/hot.md`,
   `.obsidian/app.json`, `.obsidian/appearance.json`, `.claude/rules/ingest_rules.md`,
   `.claude/rules/wiki_format_rules.md`, `.claude/rules/lint_rules.md`

   Create `.claude/memory/MEMORY.md` with this initial content:
   ```markdown
   ---
   last-updated: <SCAFFOLD_DATE>
   session-count: 1
   ---

   # Memory Index

   (empty — populate as you work)
   ```

5. **Recommend Obsidian community plugins** — Tell the user about these (they install
   manually via Settings → Community plugins):
   - **Bases** — Dynamic property-driven tables and dashboards. Core to this wiki's `.base` files.
   - **Obsidian Git** — Auto-backup the vault to a git repo. Strongly recommended.
   - **Graph Analysis** — Enhanced graph view for exploring wiki connections.
   - **Templater** — Useful if the user wants to create pages manually with templates.

6. **Verify setup** — Run a sanity check and report results:
   - [ ] Vault directory exists with all subdirectories
   - [ ] `content/index.md`, `content/log.md`, `content/hot.md`, `CLAUDE.md` exist
   - [ ] `.env` has `OBSIDIAN_VAULT_PATH` set
   - [ ] `.obsidian/` directory exists
   - [ ] `.claude/rules/` has all three rule files
   - [ ] `.claude/memory/MEMORY.md` exists
   - [ ] Source directory (if configured) exists and is readable

7. Print a confirmation summary:
   ```
   ✅ LLM-Wiki scaffolded: <path>/<domain_name>/

   Structure created:
     raw/          ← Drop source documents here. READ ONLY to the agent.
     archives/     ← Wiki snapshots for rebuild/restore. Never delete.
     content/      ← Agent-managed knowledge graph (concepts, entities, skills, ...).
       index.md    ← Master catalog. Agent reads this first.
       log.md      ← Audit trail. Append-only.
       hot.md      ← Semantic snapshot of recent activity. Update after major writes.
     CLAUDE.md     ← Domain schema. Edit to refine agent behavior.
     .env          ← Environment config. Update OBSIDIAN_SOURCES_DIR to add source paths.
     .obsidian/    ← Vault recognised by Obsidian. Open with: File → Open Vault.
     .claude/rules/
       ingest_rules.md
       wiki_format_rules.md
       lint_rules.md
     .claude/memory/
       MEMORY.md     ← Read at every session start.
       archive/      ← Archived decisions (never auto-delete).

   Available skills (load llm-wiki first, then the operation skill):
     llm-wiki      ← LOAD FIRST before any wiki operation
     ingest        ← Process raw documents into the knowledge graph
     query         ← Answer questions using the wiki
     wiki-status   ← Delta report: what's pending, wiki health, graph insights
     wiki-synthesize ← Find co-occurring concepts and create synthesis pages
     lint          ← Health-check for orphans, dead links, contradictions
     obsidian-markdown ← Formatting reference (load when writing wiki pages)
     obsidian-bases    ← Create dynamic .base views
     obsidian-cli      ← Interact with a running Obsidian instance
     obsidian-json-canvas ← Create and edit .canvas visual diagrams
     defuddle          ← Extract clean markdown from a URL for use as a raw source

   Next steps:
     1. Open the vault in Obsidian (File → Open Vault → select this directory)
     2. Install recommended community plugins (Settings → Community plugins)
     3. Drop a source document into raw/
     4. Load the llm-wiki skill, then the ingest skill, then ingest your first document
   ```

8. Do NOT create any content pages during scaffolding. The `content/` folder starts empty
   (except index.md, log.md, hot.md). All entities are created through the ingest workflow.
