---
name: ingest
description: >
  Run the LLM-wiki ingestion pipeline on source documents. Parses the source,
  cross-references the index, updates or creates wiki entity pages, weaves bidirectional
  links, updates the manifest and audit log. Use when the user says "ingest [file]",
  "process [document]", "add this to the wiki", or drops a new file into raw/.
  Also handles image sources (screenshots, diagrams, slides) when running a
  vision-capable model.
---

# LLM-Wiki Ingest Skill

You are a deep agent executing a structured ingestion pipeline. You do NOT summarize
documents — you synthesize them into a persistent, interlinked knowledge graph.

## Input

$ARGUMENTS — one of:
- A filename relative to `raw/` (e.g., `neural_scaling_laws.md`)
- A full path to a file in `raw/`
- A URL — run defuddle first (`defuddle parse <url> --md -o raw/<slug>.md`), then ingest
- `"all"` — process all pending files (new or changed since last ingest)
- Empty — list pending files and ask which to process

## Setup: Tool Commands & KNOWLEDGE_ROOT

Run the appropriate command first. Read the output JSON before doing anything else.

**Single file:**
```bash
./.claude/bin/wiki_guard --ingest-agent --source raw/<file>.md
# → .claude/tmp/ingest_prep.json
# Contains: KNOWLEDGE_ROOT, hash status (new/changed/unchanged), existing + unresolved wikilinks
```
If `status == unchanged`: skip and tell the user. If `new` or `changed`: proceed.

**Batch / "all" (preferred — materializes checkpoints):**
```bash
./.claude/bin/wiki_guard --ingest-runner-agent
# → .claude/tmp/ingest_runner.json + .claude/tmp/ingest_runner/<source>.json per step
# Process steps[] in order. Read each step's prep_file directly.
# After finishing a source, write finalize payload to that step's finalize_file.
```

**Pending queue only (no prep checkpoints):**
```bash
./.claude/bin/wiki_guard --ingest-batch-agent
# → .claude/tmp/ingest_batch.json  (queue + per-source preflight packets, cap 5)
```

**KNOWLEDGE_ROOT** is set from tool output: `content/` if `content/index.md` exists, else `wiki/`. If neither exists, stop — tell user to run `/llm-wiki:scaffold`.

**Read `${KNOWLEDGE_ROOT}/index.md` in full before Phase 2.** You can parallelize this read with the source file read in Phase 1.

## Ingestion Protocol

Execute ALL phases in order. Do not skip any phase.

---

### Phase 1 — Source Analysis

**Read the source file.** (You can parallelize this with reading `${KNOWLEDGE_ROOT}/index.md`.)

Format-specific handling:
- **Text** (`.md`, `.txt`, web clippings) — read directly
- **PDF** — use Read tool with page ranges; if scanned/image-based, treat as image source
- **Images** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) — *vision-capable model required*; transcribe visible text verbatim, describe structure (nodes/edges), extract concepts as `^[inferred]`, flag unreadable content as `^[ambiguous]`. Image pages will skew heavily `^[inferred]` — expected. If model can't handle vision, skip and tell user.

Extract from the source:
- **Entities** — major (deserves own page) vs. minor (mention-only)
- **Claims** — verifiable factual assertions
- **Relationships** — how entities relate (causes, contains, contradicts, enables, precedes)
- **Contradictions** — conflicts with existing wiki pages

Output internal analysis before continuing:
```
Source: <filename>
Source type: <document | image | pdf>
Major entities: <list>
Minor entities: <list>
Contradictions with wiki: <list or "none">
```

Seed this from `wikilinks.existing_entities` and `wikilinks.unresolved_entities` in the prep JSON. For runner workflow, process `steps[]` in order, read each `prep_file` directly, write finalize payload to that step's `finalize_file` when done.

---

### Phase 1b — QMD Corpus Check (optional)

**GUARD: Skip if `QMD_PAPERS_COLLECTION` is unset in `.env`.**

```
mcp__qmd__query: collection=<QMD_PAPERS_COLLECTION>
  - vec search: topic/thesis of this source
  - lex search: key terms, author names, method names
```

Use results to: add cross-refs, create `concepts/` pages for themes with 3+ hits, flag conflicts as `^[ambiguous]`, merge instead of creating duplicate pages.

---

### Phase 2 — Index Cross-Reference

Using `${KNOWLEDGE_ROOT}/index.md` (already read in setup):

- Classify every major entity as `existing` (has a wiki page) or `novel` (no page yet).
- Identify the top 5 most relevant existing pages that will need updates or new links.
- Use `suggested_entity_slug` from the prep JSON as first candidate; verify in index.

**Project scope decision:**
- Entity only relevant to one specific project → `${KNOWLEDGE_ROOT}/projects/<name>/<category>/` + update/create `${KNOWLEDGE_ROOT}/projects/<name>/<name>.md`
- General knowledge → global category directory (`concepts/`, `entities/`, `skills/`, etc.)
- Project pages `[[wikilink]]` to global pages and vice versa.

---

### Phase 3 — Update Existing Entity Pages

For each `existing` major entity:

1. Read the entity's current page.
2. Merge new insights — append and integrate only; do NOT rewrite existing content.
3. Increment `source_count` by 1 in frontmatter.
4. Update `updated` to today's date.
5. If `status: draft` and `source_count` reaches 2+, upgrade to `active`.
6. If source contradicts existing claims: set `status: contradictory`, add `## Contradictions` section documenting which source claims what, note human arbitration required. Do NOT silently overwrite.
7. Add `[[wikilinks]]` to related entities now mentioned.

---

### Phase 4 — Create Novel Entity Pages

For each `novel` major entity:

1. Create `${KNOWLEDGE_ROOT}/<category>/<entity_name_in_snake_case>.md`

2. Write YAML frontmatter:

```yaml
---
domain: <current_domain>
type: <concept | guide | comparison | process | person | event | tool>
summary: <1-2 sentences, ≤200 chars — used by query skill; missing = expensive full-page reads>
source_count: 1
status: draft
visibility: private
tags:
  - <tag_1>
  - <tag_2>
related:
  - "[[related_entity_1]]"
  - "[[related_entity_2]]"
provenance:
  extracted: 0.0
  inferred: 0.0
  ambiguous: 0.0
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
```

Tag rules: snake_case, min 2, max 5. `visibility/` tags are system tags and don't count.
Visibility tags: `visibility/internal` (architecture/credentials), `visibility/pii` (personal data). Omit unless clearly warranted — no tag = public.

3. Write page body:

```markdown
## Overview
[Dense encyclopedic 1–2 paragraphs. No filler. Maximum information density.]
[Provenance markers: none=extracted, ^[inferred]=LLM synthesis, ^[ambiguous]=contested]

## [Most relevant section for this entity type]

## Relationships
[Describe and [[wiki-link]] all connected entities with a wiki page.]

## Sources
- `raw/<source_filename>` — <one-line contribution summary>
```

For `synthesis` type pages, write as an essay (apply humanize-writing principles). All other types: encyclopedic density is correct.

After writing body: update `provenance:` fractions to reflect actual mix (should sum to ~1.0).

4. Add to `${KNOWLEDGE_ROOT}/index.md`:
```
| [[entity_snake_case]] | <precise, dense one-line summary> | 1 | draft | <date> |
```

5. Add a `[[link]]` to this new page from at least one existing related page — no orphans.

---

### Phase 5 — Link Weaving Pass

1. For every entity pair with a meaningful relationship, ensure both pages reference each other via `[[wikilinks]]`.
2. Verify no new page has zero inbound links. If orphaned, add a link from the most semantically relevant existing page.

---

### Phase 6 — Finalize (Record Keeping)

Write `.claude/tmp/ingest_finalize.json` then run:

```bash
./.claude/bin/wiki_guard --ingest-finalize --ingest-finalize-file .claude/tmp/ingest_finalize.json
```

Updates `.manifest.json`, `log.md`, and `hot.md` in one layout-aware pass. Idempotent — safe to retry. Accepts a single payload, `{ "entries": [] }`, or a bare array for batch finalization.

**Payload:**
```json
{
  "source_path": "raw/<filename>",
  "source_type": "document",
  "content_hash": "sha256:<64-char-hex>",
  "project": null,
  "pages_created": ["content/path/to/page.md"],
  "pages_updated": ["content/path/to/page.md"],
  "links_woven": 4,
  "contradictions": ["[[entity]] — brief conflict summary"],
  "log_details": [
    "UPDATED [[entity_1]] — <what changed>",
    "CREATED [[entity_2]] — <one-line description>"
  ],
  "hot": {
    "recent_activity": "Conceptual summary of what shifted in the knowledge base — not a file list.",
    "active_threads": ["- Thread bullet"],
    "key_takeaways": ["- Key takeaway bullet"],
    "flagged_contradictions": ["- [[entity]] — conflict summary"]
  }
}
```

**Manual fallback** (only if `wiki_guard` unavailable):
- Append to `${KNOWLEDGE_ROOT}/log.md`: `- [<ISO8601>] INGEST source="raw/<filename>" pages_updated=<N> pages_created=<N> contradictions=<N> links_woven=<N> source_type=<document|image|pdf>` followed by detail lines.
- Update `.manifest.json` entry with `content_hash`, `ingested_at`, `pages_created`, `pages_updated`.
- Overwrite `${KNOWLEDGE_ROOT}/hot.md` (≤500 words): prepend to Recent Activity, update Active Threads, Key Takeaways, Flagged Contradictions.

---

### Phase 7 — Ingestion Summary

```
✅ Ingestion complete: raw/<filename>

  Updated:  <N> existing pages
  Created:  <N> new entity pages
  Orphans:  0 (all pages linked)
  Flags:    <N> contradictions requiring human review (or "none")

  New entities:
    → [[entity_1]]
    → [[entity_2]]

  Review these flagged contradictions:
    → [[entity_name]]: <brief description>
```

## Tooling Friction Protocol

If `wiki_guard` produces unexpected output, errors, or wrong layout resolution — **stop and invoke `wiki-tooling-fixer` subagent** before any manual workaround. Do not paper over tooling defects inside content changes. Provide: exact command, stdout/stderr, expected vs. actual behavior, source file for reproduction. After fix, rerun the command and verify before resuming.

## Edge Cases

- **Very long source** — process in conceptual chunks; complete all phases per chunk before starting the next; write intermediate progress to `log.md` so state survives context compaction. See `/llm-wiki:context-compression` for large session management.
- **Empty `${KNOWLEDGE_ROOT}/index.md`** (first ingest) — all entities are novel; proceed without cross-reference.
- **Image file** — requires vision-capable model; high `^[inferred]` fraction is expected and correct. If model lacks vision, log in `log.md` and tell user.
- **Non-parseable binary** (video, archive) — log in `log.md` and inform user; do not attempt ingest.
- **Never hallucinate sources.** Only attribute claims to a source if you read them in the raw document this session. Do not fill pages from training data.

## Quality Checklist

After completing all phases, verify before reporting done:

- [ ] Every new page has `domain`, `type`, `summary`, `source_count`, `status`, `tags`, `related`, `provenance`, `created`, `updated` in frontmatter
- [ ] `summary:` is present and ≤200 chars on every new and updated page
- [ ] `provenance:` block is present and fractions sum to ~1.0 on every new and updated page
- [ ] Every new page has at least 2 `[[wikilinks]]` to existing pages
- [ ] No orphaned new pages (at least one existing page links back)
- [ ] `${KNOWLEDGE_ROOT}/index.md` has a row for every new page
- [ ] `${KNOWLEDGE_ROOT}/log.md` has the ingest entry with correct counters
- [ ] `.manifest.json` has the entry for this source with `content_hash`
- [ ] `${KNOWLEDGE_ROOT}/hot.md` has been updated with a conceptual description of what changed
- [ ] Inferred claims marked `^[inferred]`, contested claims marked `^[ambiguous]`
- [ ] Visibility tags applied only where clearly warranted (default: no tag)
