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
- A filename relative to raw/ (e.g., `neural_scaling_laws.md`)
- A full path to a file in raw/
- A URL — pass through `/llm-wiki:defuddle` first, then ingest the resulting file
- "all" — process all files in raw/ not yet in the manifest (or changed since last ingest)
- Empty — check manifest, list pending files, ask which to process

## Pre-Flight Checks

Before ingesting anything:

1. Confirm you are inside an LLM-wiki domain root (CLAUDE.md and a valid knowledge index must exist).
   If not found, tell the user to run `/llm-wiki:scaffold` first.

  Set `KNOWLEDGE_ROOT` before proceeding:
  - `content` if `content/index.md` exists
  - otherwise `wiki` if `wiki/index.md` exists
  - otherwise stop and ask the user to scaffold or repair the domain index

2. Confirm the target file exists in raw/. If not, list available files in raw/ and ask.
   If the user provides a URL instead of a file path, use `/llm-wiki:defuddle` to extract
   clean markdown (`defuddle parse <url> --md -o raw/<slug>.md`), then proceed with that file.

3. Check `.manifest.json` at the domain root to determine whether this file needs ingesting:
   - If the manifest doesn't exist yet, proceed (first ingest — create it in Phase 6).
   - If the file is **not** in the manifest, proceed.
   - If the file **is** in the manifest, compute its SHA-256 hash:
     `sha256sum -- "<file>"` (Linux) or `shasum -a 256 -- "<file>"` (macOS).
     Always double-quote the path and use `--` to prevent filenames with special characters
     from being misinterpreted by the shell.
     - If the hash **matches** `content_hash` in the manifest → skip; content is unchanged
       (handles timestamp drift from git checkout, copies, NFS). Tell the user it was skipped.
     - If the hash **differs** → re-ingest; content has genuinely changed since last run.

4. Read `${KNOWLEDGE_ROOT}/index.md` in full. This is mandatory — do NOT proceed without reading it.

## Ingestion Protocol

Execute ALL phases in order. Do not skip any phase.

---

### Phase 1 — Source Analysis

Determine the source format and read accordingly:

**Text sources** (`.md`, `.txt`, web clippings) — read directly.

**PDFs** — use the Read tool with page ranges. For scanned PDFs (slide decks, documents
exported to PDF where pages are images), treat each page as an image source below.

**Image sources** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) — *requires a vision-capable
model*. If your model doesn't support vision, skip image files and tell the user which were
skipped so they can re-run with a vision-capable model. For images, walk the content
methodically:
1. **Transcribe** any visible text verbatim (UI labels, slide bullets, whiteboard
   handwriting, code snippets). This is the only *extracted* content from an image.
2. **Describe structure** — for diagrams, list the nodes and edges. For screenshots, name
   the app or context if recognizable.
3. **Extract concepts** — what is the image *about*? What ideas, entities, or relationships
   does it convey? Most of this is `^[inferred]`.
4. **Note ambiguity** — handwriting you can't read, arrows whose direction is unclear,
   cropped content. Use `^[ambiguous]` and call it out.

Image-derived pages will skew heavily toward `^[inferred]` — that's expected. Don't present
inferred meaning as extracted fact.

---

From the source, extract:

**Entities** — Every distinct concept, person, tool, process, event, or system mentioned.
  Classify each as: `major` (deserves its own wiki page) or `minor` (mention-only).

**Claims** — All verifiable factual assertions. Note the exact location in the source.

**Relationships** — How entities relate to each other (causes, contains, contradicts,
  enables, precedes, etc.).

**Contradictions** — Any claim that appears to conflict with what you know from prior
  ingestions (visible in existing wiki pages).

Output a brief internal analysis before proceeding:
```
Source: <filename>
Source type: <document | image | pdf>
Major entities identified: <list>
Minor entities identified: <list>
Potential contradictions with existing wiki: <list or "none">
```

---

### Phase 1b — QMD Source Discovery (optional)

**GUARD: If `QMD_PAPERS_COLLECTION` is empty or unset in `.env`, skip this entire step.**

When `QMD_PAPERS_COLLECTION` is set, before writing any pages check whether related papers
are already indexed that could enrich or contradict what you're about to write:

```
mcp__qmd__query:
  collection: <QMD_PAPERS_COLLECTION>
  intent: <what this source is about>
  searches:
    - type: vec    # semantic — finds related work even with different vocabulary
      query: <topic or thesis of the source>
    - type: lex    # keyword — finds papers citing the same methods, tools, or authors
      query: <key terms, author names, method names from the source>
```

Use the returned snippets to:
- **Surface related papers** to add as cross-references in wiki pages
- **Identify recurring themes** across the corpus — 3+ papers on the same concept means
  that concept almost certainly warrants its own global `concepts/` page
- **Find contradictions** between this source and indexed papers — flag with `^[ambiguous]`
- **Avoid duplicate pages** — if the corpus already covers this concept heavily, merge
  rather than create

---

### Phase 2 — Index Cross-Reference

**Project scope** — Before classifying entities, determine where knowledge belongs:
- **Project-specific** (a debugging technique that only applies to one codebase, a
  project-specific architecture decision) → `${KNOWLEDGE_ROOT}/projects/<project-name>/<category>/`
  Also create or update the project overview at `${KNOWLEDGE_ROOT}/projects/<name>/<name>.md` (must be
  named after the project — never `_project.md`, as Obsidian uses filenames as graph node
  labels so every project would appear as `_project` in the graph).
- **General** (a concept like "React Server Components", a widely applicable skill, a
  person) → global category directory (for example, `${KNOWLEDGE_ROOT}/concepts/`, `${KNOWLEDGE_ROOT}/entities/`, `${KNOWLEDGE_ROOT}/skills/`)
- Cross-reference: project pages should `[[wikilink]]` to global pages and vice versa.

Using `${KNOWLEDGE_ROOT}/index.md` (already read in pre-flight):

- Classify every major entity as `existing` (has a wiki page) or `novel` (no wiki page yet).
- Identify the top 5 most relevant existing pages that will need updates or new links.

---

### Phase 3 — Update Existing Entity Pages

For each `existing` major entity:

1. Open its existing knowledge page.
2. Determine what new information the source adds vs. what is already captured.
3. Merge new insights into the appropriate section. Do NOT rewrite existing content —
   append and integrate only.
4. Increment `source_count` by exactly 1 in YAML frontmatter.
5. Update the `updated` field to today's date.
6. If the page is currently `draft`, upgrade to `active` if source_count reaches 2+.
7. If the source contradicts existing claims:
   - Set `status: contradictory` in YAML.
   - Add or update a `## Contradictions` section documenting the specific conflict,
     which source makes which claim, and that human arbitration is required.
   - Do NOT silently overwrite or "resolve" the contradiction.
8. Add `[[wiki_links]]` to any related entities now mentioned in this page.

---

### Phase 4 — Create Novel Entity Pages

For each `novel` major entity (those not yet in the wiki):

Format all page content following Obsidian Flavored Markdown conventions (`obsidian-markdown`
skill): use `[[wikilinks]]` for internal links, callouts for DM/secret/mechanic content,
and valid YAML properties (flat, snake_case keys, dates as `YYYY-MM-DD`, wikilinks quoted).

1. Choose the correct category directory and create
  `${KNOWLEDGE_ROOT}/<category>/<entity_name_in_snake_case>.md`

2. Write the complete YAML frontmatter block:

   **`summary:`** — Write 1–2 sentences, ≤200 chars. This is what the query skill reads in
   its index pass — a missing or stale summary forces expensive full-page reads on every
   query touching this page. When updating an existing page whose meaning has shifted,
   rewrite the summary to match the new content, not just the old scope.

   **`tags:`** — Use snake_case thematic tags. Minimum 2. Maximum 5. `visibility/` tags
   (see below) are system tags and do NOT count toward this limit.

   **Visibility tags** (optional, add only when clearly warranted):
   - `visibility/internal` — architecture internals, credentials patterns, team-only context
   - `visibility/pii` — content referencing personal data, user records, or sensitive identifiers
   - No tag (default) — anything safe to surface in user-facing query answers

   When in doubt, omit. Untagged pages are treated as public. Never add a visibility tag
   just because a topic sounds technical.

```yaml
---
domain: <current_domain>
type: <concept | guide | comparison | process | person | event | tool>
summary: <one or two sentences, ≤200 chars>
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
  extracted: 0.0   # rough fraction of sentences with no marker (direct paraphrase)
  inferred: 0.0    # fraction marked ^[inferred] (synthesized connections)
  ambiguous: 0.0   # fraction marked ^[ambiguous] (sources disagree or unclear)
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
```

3. Write the page body following this structure. Apply provenance markers inline to every
   claim that is not a direct paraphrase of the source. For `synthesis` type pages, the
   prose is meant to be read as an essay — apply `/llm-wiki:humanize-writing` principles
   (earned specificity, no hollow openers, say the thing directly). For all other types
   (concept, entity, skill, reference), encyclopedic density is correct; ignore humanize-writing.
   - No marker (default) — extracted directly from the source
   - `^[inferred]` — an LLM-synthesized connection, generalization, or implication the source doesn't state directly
   - `^[ambiguous]` — sources disagree, or the source itself is unclear

```markdown
## Overview
[Dense, encyclopedic 1-2 paragraph definition. No filler. Maximum information density.]
[Example provenance markers:]
[- Transformers parallelize across positions, unlike RNNs.]
[- This is why they scale better on modern hardware. ^[inferred]]
[- The model was trained on roughly 13T tokens. ^[ambiguous]]

## [Most relevant section for this entity type]
[Substantive content organized under meaningful headings.]

## Relationships
[Explicitly describe and [[wiki-link]] all connected entities.]
[Every major entity mentioned here that has a wiki page gets a wiki-link.]

## Sources
- `raw/<source_filename>` — <one-line description of what this source contributed>
```

After writing the body, update the `provenance:` frontmatter fields with rough fractions
reflecting the actual mix of extracted / inferred / ambiguous content on the page.

4. Add a new row to `${KNOWLEDGE_ROOT}/index.md`:
```
| [[entity_snake_case]] | <one-line summary — precise, dense, no fluff> | 1 | draft | <date> |
```

  If this domain uses a `.base` dashboard (e.g., `${KNOWLEDGE_ROOT}/meta/dashboard.base`), the new entity
   will appear automatically — no manual update needed. See `obsidian-bases` skill if a
   dashboard doesn't yet exist and one would add value.

5. Go back to the most related existing pages and add a `[[link]]` to this new page
   so no new page is born as an orphan.

---

### Phase 5 — Link Weaving Pass

After all entity pages are written or updated:

1. Scan the current ingestion's entity list.
2. For every pair of entities that have a meaningful relationship, ensure both pages
   reference each other via `[[wiki_links]]`.
3. Check that no newly created page is an orphan (zero inbound links from other pages).
   If it is, add a link from the most semantically relevant existing page.

---

### Phase 6 — Record Keeping

**`${KNOWLEDGE_ROOT}/log.md`** — Append (NEVER edit prior entries). Machine-parseable one-line format:

```markdown
- [<YYYY-MM-DDThh:mm:ssZ>] INGEST source="raw/<filename>" pages_updated=<N> pages_created=<N> contradictions=<N> links_woven=<N> source_type=<document|image|pdf>
```

Follow with a human-readable detail block for contradictions or notable changes:

```markdown
- [<YYYY-MM-DDThh:mm:ssZ>] INGEST source="raw/<filename>" pages_updated=2 pages_created=1 contradictions=1 links_woven=4 source_type=document
  - UPDATED [[entity_1]] — <what changed>
  - UPDATED [[entity_2]] — <what changed>
  - CREATED [[new_entity_1]] — <one-line description>
  - CONTRADICTION [[entity_name]] — <brief description of conflict>
```

**`.manifest.json`** — Add or update the entry for this source file. Create the file with
`version: 1` if it doesn't exist yet:

```json
{
  "version": 1,
  "stats": {
    "total_sources_ingested": <N>,
    "total_pages": <N>
  },
  "sources": {
    "raw/<filename>": {
      "ingested_at": "<ISO8601>",
      "size_bytes": <N>,
      "modified_at": "<ISO8601>",
      "content_hash": "sha256:<64-char-hex>",
      "source_type": "document",
      "project": "<project-name or null>",
      "pages_created": ["${KNOWLEDGE_ROOT}/path/to/page.md"],
      "pages_updated": ["${KNOWLEDGE_ROOT}/path/to/page.md"]
    }
  }
}
```

`content_hash` is the SHA-256 computed in Pre-Flight step 3. It's the primary skip signal
on subsequent runs — always write it. Update `stats` counters to reflect the current totals.

---

### Phase 7 — Hot Cache Update

If `${KNOWLEDGE_ROOT}/hot.md` doesn't exist, create it from this template before updating:

```markdown
---
title: Hot Cache
updated: <TODAY>
---

## Recent Activity

## Active Threads

## Key Takeaways

## Flagged Contradictions
```

Update `${KNOWLEDGE_ROOT}/hot.md` to reflect this ingestion. Overwrite the entire file (it is not
append-only like `${KNOWLEDGE_ROOT}/log.md`). Keep it under 500 words total:

- **Recent Activity**: prepend a new bullet; keep only the last 3 operations
- **Active Threads**: add or update threads for entities with open contradictions or
  `status: draft` pages that need follow-up
- **Key Takeaways**: update with the most significant new knowledge this source added (1-3 bullets)
- **Flagged Contradictions**: add any new contradictions; remove any that have been resolved
- Update the `updated:` frontmatter timestamp

Write the **conceptual change**, not a file list. Example: *"Ingested Fowler's microservices
article — 3 new concept pages on service decomposition, API gateway, bounded contexts."*
A future agent scanning `${KNOWLEDGE_ROOT}/hot.md` needs to understand *what shifted in the knowledge base*,
not which files were written.

---

### Phase 8 — Ingestion Summary

Print a final summary to the user:

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

## Edge Cases

**If the source is very long** (e.g., a full book or large PDF transcript):
- Process it in conceptual chunks — complete all 6 phases per chunk before moving to the next.
- Write intermediate progress to `${KNOWLEDGE_ROOT}/log.md` so state survives context compaction.
- For structured approaches to managing context across a large multi-chunk ingestion session, see `/llm-wiki:context-compression` (Three-Phase Workflow for Large Ingestion Sessions).

**If `${KNOWLEDGE_ROOT}/index.md` is empty** (first ingestion):
- Proceed without cross-reference. All entities are novel.
- After ingestion, the wiki has its first nodes — subsequent ingestions will link against them.

**If a file in raw/ is an image** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`):
- Follow the multimodal branch in Phase 1. Requires a vision-capable model.
- If the model doesn't support vision, note it in `${KNOWLEDGE_ROOT}/log.md` and inform the user.
- Image pages are expected to have high `^[inferred]` fractions — this is correct behaviour.

**If a file in raw/ is a non-parseable binary** (video, archive, etc.):
- Note this in `${KNOWLEDGE_ROOT}/log.md` and inform the user. Do not attempt to ingest binary files.

**Never hallucinate sources.** Only claim information comes from a source if you actually
read it in the raw document during this session. Do not draw on training data to "fill in"
entity pages — only what the source explicitly states.

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
