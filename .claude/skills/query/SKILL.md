---
name: query
description: >
  Answer a question using the LLM-wiki knowledge graph. Reads index.md to navigate,
  identifies and reads relevant entity pages, synthesizes a cited answer, and optionally
  files the synthesis back into the wiki as a new compounding entity page. Use when the
  user asks a question about topics the wiki covers, says "query the wiki", "what does
  the wiki say about X", or asks for a synthesis or comparison of wiki topics.
  Supports an index-only fast mode triggered by "quick answer", "just scan",
  "don't read the pages", or "fast lookup" — returns answers from page summaries and
  frontmatter without reading page bodies. Supports a visibility filter triggered by
  "public only", "user-facing", or "exclude internal" — restricts results to
  non-internal pages only.
---

# LLM-Wiki Query Skill

> **Prerequisite:** Load the `llm-wiki` skill before this one. Vault layout, CLI path, file naming, retrieval primitives, and core principles are defined there — not repeated here.

Every claim traces back to a wiki page, which traces back to a raw source. Do not supplement
with training knowledge. If the wiki can't answer, say so and recommend a source to ingest.

---

## Pre-Flight

1. Check `content/hot.md` first — if it already answers the question, skip to Synthesis.
2. **Index-only mode** (triggered by "quick answer", "just scan", "don't read the pages", "fast lookup"):
   answer from `summary:` fields and `index.md` descriptions only, skip to Synthesis, label the answer:
   > *(index-only — facts from page summaries; may miss nuance)*
3. **Filtered mode** (triggered by "public only", "user-facing", "exclude internal"):
   skip any page tagged `visibility/internal` or `visibility/pii`; don't mention excluded pages exist.

---

## Step 1 — Parallel Candidate Discovery

Run both searches simultaneously (they're fast and complementary):

**A. Structural search** (index + frontmatter ranking):
```bash
python .claude/bin/wiki_guard.py --query-agent --query-question "<question>"
# reads stdout summary; then reads .claude/tmp/query_prep.json for the ranked file list
# add --query-fast for index-only mode; --query-public-only for filtered mode
# add --query-top-k 8 if the initial candidate set is too narrow
```

**B. QMD semantic search** (always run — both collections are live):
```
mcp__qmd__query:
  collection: shattered_sea_wiki         # keyword + semantic over wiki pages
  intent: <the user's question>
  searches:
    - type: lex    # exact names, proper nouns, file paths
      query: <key terms from question>
    - type: vec    # concepts, relationships, themes
      query: <question rephrased as a descriptive statement>

mcp__qmd__query:                         # parallel: check raw/ sources too
  collection: papers
  intent: <the user's question>
  searches:
    - type: lex
      query: <key terms>
    - type: vec
      query: <question rephrased>
```

**Merge results** — write QMD output to `.claude/tmp/qmd_results.json` as a list of
`{"rel_path": str, "score": float, "snippet": str}` objects, then rerun wiki_guard with the
merge flag. This produces a single unified ranked payload:
```bash
python .claude/bin/wiki_guard.py --query-agent --query-question "<question>" \
  --query-merge-qmd .claude/tmp/qmd_results.json
```
The updated `query_prep.json` has `qmd_merged: true`, boosted scores, `qmd_snippets` per page,
and a `read_strategy` per candidate (`summary_only` / `grep` / `full_read`).

If QMD snippets already fully answer the question, skip Step 2 entirely and go straight to Synthesis.

**Fallback** (if `wiki_guard` unavailable): use `grep_search` on frontmatter fields `^(title|tags|aliases|summary):` scoped to `content/**`. Rank: exact title/alias → tag match → summary contains term → index.md entry contains term.

---

## Step 2 — Entity Page Reading

Follow the retrieval primitives from `llm-wiki`. For query specifically:
- Read primary candidates first; read secondaries (pages linked from primaries) only if needed.
- Prefer `read_file` with startLine/endLine on frontmatter before reading the full body.
- Read multiple independent candidates in parallel in the same tool turn.

As you read, note per-page:
- `source_count` — epistemic weight
- `status` — surface `contradictory` in the answer
- `^[inferred]` / `^[ambiguous]` provenance markers
- Retrieval tier used: `summary` / `grep` / `full-read` (report this in Sources)

If broad vault grep is the only remaining option, tell the user:
> *(broad vault grep — expensive path; confidence may be lower)*

---

## Synthesis

Write as dense human prose — no hollow openers, no filler, mix sentence lengths. Apply
`/llm-wiki:humanize-writing` principles. Use tables for comparisons, headings for summaries.

```markdown
## Answer

[Synthesized answer. Every significant claim traceable to a page.]

## Sources (from wiki)
- [[page]] (source_count: N, status: active, via: summary) — contributed: <what it added>
- [[page]] (source_count: N, status: draft, via: grep) — contributed: <what it added>

## Caveats
[Note any draft/contradictory pages. If the wiki lacks coverage, say so and name the raw/ source to ingest.]
```

---

## Step 3 — Log + Optionally File

**Log** (always):
```bash
python .claude/bin/wiki_guard.py --query-agent --query-question "<question>" --query-log
# add --query-result-pages <N> or --query-escalated as needed
```

Log line written: `- [<ISO8601>] QUERY query="..." result_pages=N mode=<normal|index_only|filtered> escalated=<true|false>`

**File back** (offer if any of these are true):
- Non-trivial comparison or relationship between 2+ entities not yet captured
- Answer required 4+ pages to construct (it's a new hub node)
- Something the user will likely ask again

Skip filing for: single-page lookups, meta-queries about wiki structure, or if user says not to.

If filing, ask first:
```
This synthesizes [[entity_1]] × [[entity_2]] — not captured anywhere yet.
File as a new synthesis page?  Suggested: <snake_case_name> (type: synthesis)
[yes / no / edit name]
```

New synthesis page frontmatter:
```yaml
---
domain: <domain>
type: synthesis
source_count: <N>
status: active
visibility: private
tags: [<tags>]
related: ["[[source pages]]"]
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
```

Body: the question as context, the full synthesized answer with wikilinks, and a `## Synthesis Method`
section naming which pages were combined and why. Add to `index.md`.

Then log the filing:
```bash
python .claude/bin/wiki_guard.py --query-filed \
  --query-filed-page "content/synthesis/<name>.md" \
  --query-filed-from-query "<question>"
```

This writes: `- [<TIMESTAMP>] FILED page="content/synthesis/<name>.md" from_query="<question>"`

---

## Special Modes

| Mode | Trigger phrase | Behavior |
|---|---|---|
| **Comparative** | "compare X and Y" | Structured table; note source_count asymmetry |
| **Contradiction scan** | "what contradictions exist" | Scan for `status: contradictory`; present conflicts, don't resolve |
| **Coverage meta** | "what's the coverage of X" | Count pages + source_count; identify gaps |
| **Deep synthesis** | "synthesize everything about X" | Load all primary + secondary + tertiary pages; always offer to file; offer `.canvas` companion via `/llm-wiki:obsidian-json-canvas` if the relationship graph is complex |
