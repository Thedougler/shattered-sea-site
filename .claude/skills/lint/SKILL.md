---
description: >
  Health-check an LLM-wiki domain for structural and semantic decay. Detects orphan pages,
  dead wiki-links, index gaps, stale pages, unresolved contradictions, and high-frequency
  entity mentions without dedicated pages. Use when the user says "lint the wiki", "check
  the wiki health", "find broken links", "what needs fixing", or on a scheduled basis.
---

# LLM-Wiki Lint Skill

You are an autonomous wiki auditor executing a systematic health-check. Your role is to
surface structural and semantic problems — not to silently fix them. Always report first,
then ask which categories to auto-fix before making any changes.

## Input

$ARGUMENTS — one of:
- Empty — run a full lint pass across all 6 checks
- A category name — run only that check: `orphans`, `dead_links`, `index`, `stale`, `contradictions`, `gaps`
- `fix` — run full lint then auto-fix all safe issues (orphans, dead links, index gaps)
- `report` — run full lint but produce only a report, do not fix anything

## Pre-Flight

1. Confirm CLAUDE.md and index.md exist. If not, tell user to scaffold first.
2. Read index.md in full — this is your map.
3. Get the full file list in wiki/ using directory traversal.

---

## Lint Checks

Run each check completely before moving to the next.

---

### Check 1 — Orphan Pages

**Goal**: Every wiki page must have at least one inbound link from another wiki page.

Process:
1. List every .md file in wiki/.
2. For each file `X.md`, search all OTHER wiki pages for `[[X]]` (case-insensitive,
   handle snake_case variants).
3. If no other page links to X, it is an ORPHAN.
4. Record: filename, topic, and 2-3 candidate pages that should logically link to it.

Output format:
```
ORPHAN: [[entity_name]]
  Topic: <one-line description from index.md>
  Suggested links from: [[candidate_1]], [[candidate_2]]
```

---

### Check 2 — Dead Link Detection

**Goal**: Every `[[wiki_link]]` must point to an existing .md file in wiki/.

Process:
1. Scan every wiki page for all occurrences of `[[...]]` patterns.
2. For each link, check whether `wiki/<link_target>.md` exists.
3. If not, it is a DEAD LINK.
4. Record: the dead link, the page it appears in, and how many times it appears.
5. Classify dead links as: `stub_worthy` (entity deserves a page) or `typo_likely`
   (looks like a misspelling of an existing entity).

Output format:
```
DEAD LINK: [[missing_entity]]
  Found in: [[source_page_1]], [[source_page_2]]
  Classification: stub_worthy | typo_likely
  If typo, likely meant: [[similar_existing_entity]]
```

---

### Check 3 — Index Audit

**Goal**: index.md and wiki/ are perfectly synchronized.

Process:
1. Extract all entity names from index.md's entity catalog.
2. List all .md files in wiki/.
3. Find:
   - **Index ghost**: entry in index.md with no corresponding wiki/*.md file
   - **Wiki ghost**: wiki/*.md file with no corresponding index.md entry
4. Also check that each index entry's one-line summary is not empty or stale.

Output format:
```
INDEX GHOST: [[entity_name]] — in index.md but no wiki file
WIKI GHOST: [[entity_name]] — has wiki file but not in index.md
EMPTY SUMMARY: [[entity_name]] — index entry has no summary
```

---

### Check 4 — Staleness Detection

**Goal**: Identify pages that may contain outdated information.

Process:
1. Read the `updated` date from the YAML frontmatter of every wiki page.
2. Count total ingestion events in log.md.
3. Flag any page whose `updated` date predates the last 3 ingestion events AND has
   `source_count: 1` (single-source pages are most likely to become stale).
4. Also flag any page with `status: draft` that has not been updated in over 30 days.

Output format:
```
STALE: [[entity_name]]
  Last updated: <date>
  Source count: <N>
  Ingestions since update: <N>
  Reason: single_source | draft_aged
```

---

### Check 5 — Contradiction Scan

**Goal**: Surface all unresolved contradictions for human arbitration.

Process:
1. Scan every wiki page's YAML frontmatter for `status: contradictory`.
2. For each flagged page, read the `## Contradictions` section.
3. List the contradiction, the conflicting sources, and how long it has been unresolved
   (compare `updated` date to today).

Output format:
```
CONTRADICTION: [[entity_name]]
  Open since: <date> (<N> days)
  Conflict: <brief description of the disagreement>
  Sources in conflict: raw/<file_a> vs raw/<file_b>
  Action required: Human arbitration needed before status can be cleared
```

---

### Check 6 — Entity Gap Detection

**Goal**: Find high-frequency mentions of concepts that lack dedicated wiki pages.

Process:
1. Scan all wiki pages for capitalized terms, technical terms, and proper nouns
   that appear 3 or more times across the corpus.
2. Filter out terms that already have wiki pages.
3. Rank by frequency — highest frequency gaps are highest priority.
4. These are candidate entities that should be ingested or synthesized into new pages.

Output format:
```
ENTITY GAP: "<term>"
  Mentions: <N> across <N> pages
  Mentioned in: [[page_1]], [[page_2]], [[page_3]]
  Priority: high | medium | low
```

---

## Lint Report

After all checks, output a structured report:

```markdown
# Lint Report — <DOMAIN_NAME>
Generated: <YYYY-MM-DD HH:MM>
Pages audited: <N>
Index entries: <N>
Ingestion events in log: <N>

---

## 🔴 Critical Issues

### Orphan Pages (<N>)
[list]

### Dead Links (<N>)
[list]

### Contradictions (<N>)
[list]

---

## 🟡 Structural Issues

### Index Gaps (<N>)
[list]

### Stale Pages (<N>)
[list]

---

## 🔵 Growth Opportunities

### Entity Gaps — high priority (<N>)
[list top 10]

---

## Summary
- Critical: <N> issues
- Structural: <N> issues
- Opportunities: <N> gaps

Wiki health score: <calculate as % of pages without any issues>
```

---

## Auto-Fix Protocol

After reporting, ask:
```
Found <N> issues across <N> categories.

Safe to auto-fix (no content changes, structure only):
  ✅ Index gaps — add missing index entries from existing wiki files
  ✅ Wiki ghost additions — add stubs for stub_worthy dead links

Requires judgment (ask before each):
  ⚠️  Orphan pages — I'll suggest link targets, you confirm each
  ⚠️  Typo-likely dead links — I'll suggest the correct target, you confirm

Cannot auto-fix (human arbitration required):
  ❌ Contradictions — requires you to read and decide
  ❌ Stale pages — requires re-ingestion or manual verification

Shall I proceed with the safe auto-fixes? [yes / no / show me each one]
```

Only proceed with fixes after explicit user confirmation.

## After Fixing

Append a lint report entry to log.md:

```markdown
## <YYYY-MM-DD HH:MM> — Lint Pass

**Issues found**: <N>
**Auto-fixed**: <N>
  - Orphans resolved: <N>
  - Dead links resolved: <N>
  - Index synced: <N>
**Requires human review**: <N>
  - Contradictions: <N>
  - Stale pages: <N>
**Entity gaps identified**: <N> (not auto-fixed)
```
