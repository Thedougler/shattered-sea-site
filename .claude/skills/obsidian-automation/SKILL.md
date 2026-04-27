---
name: obsidian-automation
description: >
  Automate multi-step Obsidian vault operations: batch note creation, bulk property updates,
  template application, linking workflows, and vault maintenance sequences using the obsidian
  CLI. Use when the user asks to automate note creation, batch-update properties across many
  pages, apply templates in bulk, or run any multi-step operation that would be tedious
  one note at a time. Reference alongside obsidian-cli for syntax.
---

# Obsidian Automation

Automate multi-step vault operations using the `obsidian` CLI. This skill covers patterns for
bulk note creation, property updates, linking workflows, and vault maintenance sequences.

For single-note CLI syntax, see `obsidian-cli`. For page formatting, see `obsidian-markdown`.
For dynamic views over frontmatter, see `obsidian-bases`.

---

## When to Use This Skill

- Creating multiple related stub pages in one operation
- Updating a frontmatter property across many notes (e.g., promoting all `draft` pages to `active`)
- Applying a template to a batch of existing notes
- Running a multi-step linking or tagging workflow
- Automating post-ingest cleanup sequences

---

## Automation Patterns

### Batch Stub Creation

Pre-create stub pages for a list of entities before bulk ingestion. Prevents dead links during
the ingest phase.

```bash
for name in "entity_one" "entity_two" "entity_three"; do
  obsidian create name="$name" folder="wiki" silent
done
```

### Bulk Property Updates

Update a frontmatter property across every note matching a condition.

```bash
# Promote all single-source draft pages to active
obsidian search query="path:wiki/ status:draft" | while read -r file; do
  obsidian property:set name="status" value="active" file="$file" silent
done
```

### Append Backlinks

After creating a new entity page, add a wikilink to it from each of its related pages.

```bash
obsidian append file="related_entity" content="\n- [[new_entity]]" silent
```

### Post-Ingest Cleanup Sequence

Run after `/llm-wiki:ingest` to verify structural integrity before closing the session:

1. Check for stubs that weren't filled during ingestion:
   ```bash
   obsidian search query="path:wiki/ tag:stub"
   ```
2. Verify the new entity appears in the index:
   ```bash
   obsidian read file="index"
   ```
3. Confirm no orphans were introduced — run `/llm-wiki:lint orphans` for a targeted scan.

---

## Note Templates

Use these templates when creating wiki pages programmatically.

### Entity Stub

For pre-creating a page before its source is ingested. Ingest will fill in the body.

```markdown
---
domain: <domain>
type: concept
source_count: 0
status: draft
visibility: private
tags:
  - stub
related: []
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

## Overview
*(Stub — pending ingestion)*

## Relationships

## Sources
```

### Wiki Dashboard Page

A meta page that embeds a `.base` dynamic view. Keeps overview pages DRY.

```markdown
---
type: meta
domain: <domain>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Domain> Dashboard

![[dashboard.base]]
```

---

## Graph Maintenance

### Find orphan pages

```bash
# Check inbound links for a specific page
obsidian backlinks file="entity_name"
```

### Find pages missing required frontmatter

```bash
# Pages without a status property
obsidian search query="path:wiki/ -status:active -status:draft -status:verified -status:contradictory"
```

### Rename or move a page

```bash
obsidian rename file="old_name" name="new_name"
```

After renaming, run `/llm-wiki:lint dead_links` — obsidian CLI updates wikilinks in the vault
automatically when renaming via the `rename` command if the vault has "Automatically update
internal links" enabled. Verify with a lint pass regardless.

---

## Integration Points

| Skill | When to use alongside this one |
|---|---|
| `obsidian-cli` | All automation commands use the `obsidian` CLI — refer to that skill for full syntax |
| `obsidian-bases` | For dynamic dashboards and filtered views, create `.base` files rather than static tables |
| `obsidian-markdown` | All generated note content must follow Obsidian Flavored Markdown conventions |
| `ingest` | Use stub-creation patterns here to pre-create pages before bulk ingestion |
| `lint` | Automation can batch-fix structural issues surfaced by lint (orphans, dead links, index gaps) |
