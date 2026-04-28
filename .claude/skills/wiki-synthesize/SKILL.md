---
name: wiki-synthesize
description: >
  Systematically discover synthesis opportunities across the Obsidian wiki — pairs or clusters of
  concepts that co-occur frequently across pages but have no synthesis page connecting them. Creates
  new synthesis/ pages that draw explicit cross-cutting conclusions. Use when the user says "synthesize
  my wiki", "find connections", "what concepts keep coming up together", "/wiki-synthesize", or after
  a large ingest when the vault has grown significantly.
---

# Wiki Synthesize — First-Class Synthesis Discovery

> **Prerequisite:** Load the `llm-wiki` skill first. It establishes `KNOWLEDGE_ROOT` (`content/`), vault layout, and retrieval primitives. Do not proceed without it.

You are scanning the wiki for concepts that co-occur across many pages but have no dedicated synthesis page connecting them. Your job is to surface these gaps and fill the most valuable ones with cross-cutting synthesis pages.

`content/index.md` and `content/hot.md` are already in context from `llm-wiki`. Review `hot.md` **Recent Activity** and **Active Threads** — they may already point to synthesis opportunities before you run the scan.

## Step 1: Get Synthesis Candidates

Run the wiki_guard synthesis scanner. It scans all `content/` pages (skipping index/log/hot/archives), builds the co-occurrence matrix, filters already-synthesized pairs, scores and ranks candidates — all in one shot:

```
python .claude/bin/wiki_guard.py --synthesize-report --synthesize-format json
```

Optional flags:
- `--synthesize-topic "..."` — filter candidates to a domain (e.g. `"religion"` or `"factions"`)
- `--synthesize-pair-limit N` — pairs to scan (default 100; increase for broader coverage)
- `--synthesize-top-candidates N` — how many top candidates to return (default 5)
- `--synthesize-skipped-limit N` — how many skipped candidates to include in output

The JSON payload contains:
- `overview` — pages scanned, pairs evaluated, covered pairs filtered
- `top_candidates` — ranked list with `score`, `cooccurrence_count`, `shared_by_pages`, `cross_domain`, `contradiction_signal`
- `skipped_candidates` — next-best pairs not in the top set

If wiki_guard fails or returns empty candidates, invoke the `wiki-tooling-fixer` agent rather than attempting a manual co-occurrence scan.

Review `top_candidates`. Each entry has `shared_by_pages` — use `read_file` on those source pages (batched in parallel) to gather context before drafting.

## Step 2: Draft Synthesis Pages

For each top candidate, create a page in `content/synthesis/` using this template:

```markdown
---
title: <Concept A> × <Concept B>
category: synthesis
tags: [<shared tags>, <domain tags>]
sources: [<all pages that link to both>]
created: TIMESTAMP
updated: TIMESTAMP
summary: "Cross-cutting synthesis of how <A> and <B> interact, with implications for <domain>."
provenance:
  extracted: 0.2
  inferred: 0.7
  ambiguous: 0.1
---

# <Concept A> × <Concept B>

## The Connection

*What makes these two concepts worth synthesizing together — the non-obvious relationship that pages about each individually don't capture.*

## Where They Co-occur

*The pages and contexts where both appear. What situations bring them together.*

## Cross-cutting Insight

*The conclusion that only becomes visible when you look at both together. This is the point of the page — the thing you couldn't see from either concept page alone.*

## Tensions and Trade-offs

*Where the two concepts pull in opposite directions. Unresolved contradictions. Cases where applying one undermines the other.*

## Open Questions

*What this synthesis surfaces that the wiki doesn't yet have an answer for. Good candidates for future research.*

## Related

- [[<Concept A>]]
- [[<Concept B>]]
- [[<other related pages>]]
```

**Synthesis pages are mostly `^[inferred]`.** You are drawing connections across sources — that's synthesis by definition. Apply `^[inferred]` to cross-cutting conclusions and `^[ambiguous]` where sources disagree.

**The title format is `A × B`** — this signals to readers that it's a synthesis page, not a page about either concept alone.

## Step 3: Back-link from Source Pages

For each synthesis page you created, add a link to it from the two (or more) concept pages it synthesizes. In the concept page, add to its `## Related` section:

```markdown
- [[Concept A × Concept B]] — synthesis
```

If the concept page has no `## Related` section, add one at the bottom.

## Step 4: Report Skipped Candidates

The `skipped_candidates` array from the Step 1 JSON payload is your ready-made list. Surface it directly in your output — no manual enumeration needed. Format for the user:

```
Skipped (consider next time):
- [[the_drowned_maw]] × [[umberlee]] — co-occurs in 13 pages
- [[fisks_fleet]] × [[pearl_of_souls]] — co-occurs in 11 pages, shared tags: central_conflict
...
```

## Step 5: Update Special Files

**`content/index.md`** — Add entries for all new synthesis pages.

**`content/log.md`** — Append:
```
- [TIMESTAMP] WIKI_SYNTHESIZE pages_scanned=N synthesis_created=M candidates_skipped=K
```

**`content/hot.md`** — Update **Recent Activity** with what was synthesized — e.g. "Synthesized 5 cross-cutting pages: [[A × B]], [[C × D]], …". Update **Active Threads** with any open questions the synthesis surfaced. Update `updated` timestamp. If `content/hot.md` is missing, create it using the template from the `ingest` skill.

## Quality Checklist

- [ ] Every synthesis page has a `summary:` field (≤200 chars)
- [ ] Every synthesis page links back to its source concepts
- [ ] Source concept pages link forward to the synthesis page
- [ ] No synthesis page just restates what's already on the source pages — it must add a cross-cutting insight
- [ ] `content/index.md` and `content/log.md` updated
- [ ] `content/hot.md` updated

## Tips

- **A synthesis page that only summarizes its sources is useless.** The value is the connection — the thing neither source page says explicitly.
- **Don't synthesize for synthesis's sake.** If two concepts just happen to appear together a lot without a real conceptual link, skip them.
- **Three-way syntheses are powerful but rare.** Only create them when three concepts form a genuine triangle of mutual influence — not just because all three appear in the same project page.
- **Check `content/hot.md` first.** The **wiki-status** skill (insights mode) may have already flagged synthesis candidates in **Active Threads** — review those before running the co-occurrence scan from scratch.
