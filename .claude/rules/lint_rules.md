---
paths:
  - wiki/**
  - index.md
description: Linting rules — active during health-check operations
---

# Linting Protocol

Execute a complete wiki health-check in this order. Report all findings before making any fixes.

## Step 1 — YAML Frontmatter Validation

For every file in wiki/, verify:

- ✅ All required fields present: `type`, `title`, `campaign`, `created`, `updated`, `status`, `tags`, `sources`, `related`
- ✅ `status` is one of: `draft | active | verified | contradictory`
- ✅ `type` is one of: `concept | entity | location | npc | faction | item | encounter | other`
- ✅ `created` and `updated` are valid ISO dates (`YYYY-MM-DD`)
- ✅ `tags` is a list with minimum 2 items, all kebab-case
- ✅ `sources` is a list of quoted wikilinks (`"[[Page]]"`)
- ✅ `related` is a list of quoted wikilinks (`"[[Page]]"`)
- ✅ `reveal_status` (if present) is one of: `unrevealed | foreshadowed | revealed`

Flag violations for manual review or auto-fix.

---

## Step 2 — Bases-Ready Property Consistency

For base queries to work correctly, frontmatter properties must be consistently typed and valued:

- ✅ `status` values are normalized (all lowercase, consistent spelling)
- ✅ `type` values match across similar entities
- ✅ Dates are always ISO format (`YYYY-MM-DD`), never mixed with natural language
- ✅ Lists don't contain empty strings or whitespace
- ✅ Wikilinks in YAML are quoted and properly formatted

Flag inconsistent enum values that would break base filters or sorts.

---

## Step 3 — Orphan Detection

- Scan every file in wiki/
- For each file, check if any other wiki page contains `[[<this-entity>]]`
- Flag any page with zero inbound links as an ORPHAN
- Orphans should be linked to the most semantically related existing pages

---

## Step 4 — Dead Link Detection

- Scan every wiki page for `[[wiki-links]]` (including reciprocals)
- Verify each linked filename exists in wiki/
- Check that linked filenames match kebab-case convention
- Flag any link pointing to a non-existent file as a DEAD LINK
- Create stubs for dead links pointing to entities worth having

---

## Step 5 — Index Audit

- Read `wiki/index.md`
- Compare entries against actual files in wiki/
- Flag: entities in index.md with no corresponding .md file
- Flag: wiki files with no entry in index.md (add missing entries)
- Verify index entries use kebab-case slugs matching actual filenames

---

## Step 6 — Reciprocal Link Validation

- For every outbound `[[link]]` in the body of Page A, check if Page B contains a reciprocal link back to Page A
- Reciprocals live in the `## Relationships` section
- Flag missing reciprocals (except for plot-protected entities)
- Check plot protection rule: never create reciprocals FROM unrevealed/foreshadowed entities TO revealed entities

---

## Step 7 — Staleness Detection

- Review `updated` dates across all wiki pages
- Identify pages not updated in the last 90 days
- Cross-reference with git log to understand ingest patterns
- Flag stale pages for human review or re-ingestion

---

## Step 8 — Contradiction Scan

- Search for pages where `status: contradictory`
- List all flagged contradictions for human arbitration
- Do NOT resolve contradictions autonomously — surface them only
- Verify `## Contradictions` section exists and describes the conflict clearly

---

## Step 9 — Missing Entity Detection

- Scan all wiki page bodies for entity names (capitalized terms, proper nouns, technical terms)
  that are mentioned frequently but do NOT have dedicated pages
- List high-frequency mentions without pages as ENTITY GAPS
- Threshold: entities mentioned 3+ times across different pages

---

## Step 10 — Wikilink Format Validation

- All wikilinks use kebab-case: `[[Entity-Name]]` not `[[entity_name]]` or `[[EntityName]]`
- Wikilinks in YAML are quoted: `sources: - "[[Entity]]"` ✅
- No bare wikilinks in YAML: `related: - [[Entity]]` ❌
- No markdown links for internal references: `[text](wiki/entity.md)` ❌

---

## Lint Report Format

```
# Lint Report — shattered_sea — <DATE>

## YAML Violations (<count>)
- wiki/entity.md — missing field: sources
- wiki/entity.md — invalid status: "pending"

## Bases-Ready Violations (<count>)
- status field inconsistent: "Active" vs "active"
- type field varies: "npc" vs "person"

## Orphan Pages (<count>)
- [[Entity-Name]] — no inbound links

## Dead Links (<count>)
- [[Missing-Entity]] referenced in [[Source-Page]]
- [[entity_name]] (wrong case/format) in [[Source-Page]]

## Index Gaps (<count>)
- wiki/entity.md not in index.md
- index.md entry has no file: [[Missing-Page]]

## Missing Reciprocals (<count>)
- [[Entity-A]] links to [[Entity-B]], but Entity-B has no reciprocal link back

## Stale Pages (<count>)
- [[Entity-Name]] — last updated 2026-01-10 (107 days ago)

## Contradictions (<count>)
- [[Entity-Name]] — status: contradictory since 2026-03-01

## Entity Gaps (<count>)
- "term_name" — mentioned 5 times, no dedicated page

## Format Issues (<count>)
- wiki/entity.md — wikilinks use snake_case: [[wrong_format]]
- wiki/entity.md — unquoted wikilinks in YAML frontmatter
```

---

## Auto-Fix Protocol

After reporting all findings, ask the human which categories to auto-fix:

**Safe to auto-fix:**
- ✅ YAML field additions (missing required fields → add with safe defaults)
- ✅ Enum normalization (status: "Active" → "active")
- ✅ Wikilink case fixes (entity_name → Entity-Name)
- ✅ Reciprocal link creation (add missing backlinks)
- ✅ Index sync (add missing entries, remove orphaned entries)

**Require human review:**
- ⚠️ Stale pages (determine if still relevant)
- ⚠️ Contradictions (only GM can rule)
- ⚠️ Entity gaps (determine if entities should exist)
- ⚠️ Orphans (decide on meaningful connections)

---

## Bases Validation

For vault sections using Obsidian Bases (`.base` files):

- ✅ All entities used in base queries have consistent property values
- ✅ `status` enum is normalized for sorting/filtering
- ✅ `type` is present on all entities in the base's scope
- ✅ Dates are ISO format for correct base sorting
- ✅ Lists in frontmatter don't have trailing whitespace (breaks query matching)

Invalid bases properties will cause bases to display incomplete data or fail to render views.
