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
4. Read `wiki/index.md` to identify which entities already have wiki pages.
5. Classify each discovered entity as: `existing` | `novel`.

## Phase 3 — Wiki Updates (Existing Entities)
6. For each `existing` entity:
   a. Open the entity's wiki page.
   b. Merge new insights into the appropriate sections.
   c. Update the `updated` field to today's date (YYYY-MM-DD).
   d. Add the source file to the `sources` list in frontmatter (as `"[[Source-Slug]]"`).
   e. Add any new bidirectional wiki-links `[[related-entity]]` and reciprocal links.
   f. If new information contradicts existing claims: set `status: contradictory` and add
      a `## Contradictions` section describing the conflict. Do NOT silently overwrite.

## Phase 4 — Wiki Creation (Novel Entities)
7. For each `novel` entity:
   a. Create `wiki/<entity-name-kebab-case>.md` with full YAML frontmatter.
   b. Write a dense, encyclopedic entity page (minimum 3 sections).
   c. Weave bidirectional wiki-links to all related existing entities.
   d. Add the entity to `wiki/index.md` with a one-line summary.

## Phase 5 — Commit & Hot Update
8. Run `wiki-tools validate` to catch YAML/link errors before commit.
9. Self-heal: fix broken wikilinks, reciprocate links, add to index.
10. Commit changes: `git add wiki/ && git commit -m "ingest: [source file name]"`
11. Update `wiki/hot.md` with new entity counts and active threads.

---

## YAML Frontmatter Template

Use this template for every new entity page. All fields are required.

```yaml
---
type: entity
title: "Display Name"
campaign: shattered-sea
created: 2026-04-08
updated: 2026-04-08
tags:
  - tag-name
  - another-tag
status: draft
sources:
  - "[[Source-Slug]]"
related:
  - "[[Related-Entity-1]]"
  - "[[Related-Entity-2]]"
---
```

### Field Definitions

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | enum | ✅ | `concept`, `entity`, `location`, `npc`, `faction`, `item`, `encounter`, `other` |
| `title` | string | ✅ | Display name (can differ from filename) |
| `campaign` | string | ✅ | Campaign slug, e.g., `shattered-sea` |
| `created` | date | ✅ | ISO `YYYY-MM-DD` |
| `updated` | date | ✅ | ISO `YYYY-MM-DD` — update on every merge |
| `tags` | list | ✅ | kebab-case, minimum 2 tags |
| `status` | enum | ✅ | `draft`, `active`, `verified`, `contradictory` |
| `sources` | list | ✅ | `"[[Source]]"` wikilinks (quoted), minimum 1 |
| `related` | list | ✅ | `"[[Entity]]"` wikilinks (quoted), minimum 2 |
| `reveal_status` | enum | ❌ | `unrevealed`, `foreshadowed`, `revealed` (optional plot protection) |

### YAML Best Practices

- Wikilinks must be quoted: `sources: - "[[Page]]"` ✅
- Dates only as `YYYY-MM-DD`; never use timestamps
- List format only: use `-`, never inline `[a, b, c]`
- Kebab-case for file slugs, matching the filename exactly (case-sensitive)

---

## Reconciliation Rules

When merging new source material into an existing entity page:

- **Update `updated` field** to today's date
- **Add source to `sources` list** (avoid duplicates)
- **Merge new details into existing sections** (don't add duplicate sections)
- **Add new `related` links** only if the connection is significant
- **Flag contradictions immediately** — do not resolve autonomously; set `status: contradictory` and document in `## Contradictions` section

---

## Index Management

The `wiki/index.md` file is the canonical authority:

- One entry per entity: `- [[Entity-Name]] — one-line description`
- Check before creating any page (duplicate authorities silently diverge)
- Regenerate with `wiki-tools index --write` after bulk changes
- Never delete entries (archive instead)
