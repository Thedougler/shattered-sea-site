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

You are a deep research agent operating against a persistent knowledge graph. You do NOT
guess, recall from training, or hallucinate. Every claim in your answer traces back to a
wiki page, which itself traces back to raw source documents.

## Input

$ARGUMENTS — the user's question or query. Examples:
- "What is the relationship between X and Y?"
- "Compare A and B"
- "Summarize everything the wiki says about Z"
- "What contradictions exist around topic W?"
- "What are the highest source_count pages in this domain?"

## Pre-Flight

1. Confirm CLAUDE.md and index.md exist. If not, tell user to run `/llm-wiki:scaffold`.
2. If the wiki appears empty (no rows in index.md catalog), inform user to ingest sources first.
3. If `hot.md` exists at the wiki root, read it before index.md. It contains a ~500-word semantic
   snapshot of recent activity — if the question is about something ingested recently, hot.md may
   answer it without opening index.md at all. Skip to Phase 4 synthesis if it does.

---

## Visibility Filter (optional)

By default all pages are returned regardless of visibility tags.

If the query includes **"public only"**, **"user-facing"**, **"no internal content"**, **"as a user would see it"**, or **"exclude internal"**, activate **filtered mode**:

- Build a blocked tag set: `{visibility/internal, visibility/pii}`
- In Phase 2, skip any candidate whose frontmatter tags contain a blocked tag
- In Phases 3–4, do not read or cite any blocked page
- Synthesize from allowed pages only — do not mention that excluded pages exist
- Note the filter in the log entry: `mode=filtered`

Pages with no `visibility/` tag, or tagged `visibility/public`, are always included.

---

## Query Protocol

### Phase 1 — Intent Parsing

Parse the question to determine:
- **Query type**: factual | comparative | synthesis | contradiction_scan | meta (wiki health)
- **Entities involved**: which named concepts from the query are likely to have wiki pages
- **Depth needed**: shallow (1-2 pages) | medium (3-5 pages) | deep (5+ pages)
- **Mode**: index-only (triggered by "quick answer", "just scan", "don't read the pages",
  "fast lookup") | normal

---

### Phase 2 — Index-Driven Navigation

Read index.md. Build a candidate set *without opening any page bodies*:

1. Use index.md as the first filter — it lists every page with a one-line description and tags.
2. Use `Grep` to scan page **frontmatter only** for title, tag, alias, and summary matches.
   The pattern `^(title|tags|aliases|summary):` scoped to vault `.md` files is far cheaper
   than a content grep.
3. Rank candidates by: exact title/alias match → tag match → summary contains query term →
   index.md entry contains query term. Collect the top 5–10.
4. Identify second-order entities — pages linked FROM primary candidates that provide context.
5. Do NOT load pages you won't use — preserve context budget.

Report your navigation plan:
```
Query: "<question>"
Type: <factual | comparative | synthesis | contradiction_scan | meta>
Mode: <normal | index-only | filtered>
Primary pages: [[entity_1]], [[entity_2]]
Secondary pages: [[entity_3]] (linked from [[entity_1]])
Estimated depth: <shallow | medium | deep>
```

**Index-only fast path**: If mode is index-only, stop here. Answer from `summary:` fields,
titles, and index.md descriptions only. Label the answer clearly at the top:
> *(index-only answer — page bodies not read; facts are from page summaries and may miss nuance)*

Then skip to Phase 4.

---

### Phase 2b — QMD Semantic Pass (optional)

**GUARD: If `QMD_WIKI_COLLECTION` is empty or unset in `.env`, skip this entire step.**

If `QMD_WIKI_COLLECTION` is set and the index pass didn't produce clear candidates — or the
question requires semantic/concept matching rather than exact terms — run a QMD search before
reaching for per-file `Grep`:

```
mcp__qmd__query:
  collection: <QMD_WIKI_COLLECTION>
  intent: <the user's question>
  searches:
    - type: lex    # keyword match — good for exact names, file paths, error codes
      query: <key terms>
    - type: vec    # semantic match — good for concepts, patterns, analogies
      query: <question rephrased as a description>
```

If `QMD_PAPERS_COLLECTION` is also set and the question may have source material in `raw/`,
run a parallel search against the papers collection and cite raw sources separately.

QMD snippets act as pre-read section summaries. If they answer the question fully, skip Phase 3
and go straight to Phase 4. Otherwise use the ranked file list to guide Phase 3.

---

### Phase 3 — Entity Page Reading

Reading the vault is the dominant token cost of every query. Use the cheapest primitive
that can answer the question and escalate only when the cheaper one is insufficient:

| Need | Primitive | Cost |
|---|---|---|
| Does a page exist? What category/tags? | `index.md` already read in Phase 2 | Cheapest |
| 1–2 sentence preview | Read the `summary:` field from frontmatter only | Cheap |
| A specific claim or section | `Grep -A <n> -B <n> "<term>" <file>` — matching lines + context | Medium |
| Whole page content | `Read <file>` | Expensive — last resort |
| Relationships across pages | `Grep "\[\[.*?\]\]"` across wiki/ or walk wikilinks from a known page | Case-by-case |

**The rule:** if you can answer from `summary:` fields alone, don't read page bodies.
If a grepped section gives you the claim, don't read the whole page.
A 500-line page opened to read 15 lines is 485 lines of wasted tokens.

Read each identified page in order of relevance (primary first, secondary after),
using the cheapest primitive at each step.

As you read:
- Extract the specific claims relevant to the query
- Note the source_count (epistemic weight) of each page
- Note the status — if `contradictory`, surface that in your answer
- Note provenance markers: `^[inferred]` claims are synthesized, `^[ambiguous]` claims are contested
- Track which raw/ sources support each claim (from the ## Sources section)
- **Track the retrieval tier** that answered each claim: `summary` / `grep` / `full-read` — include
  this in the Sources section so the user can gauge confidence

Do NOT read pages that are not relevant. Breadth costs tokens — be surgical.

**Escalation disclosure**: If the section grep and full reads still don't answer the question and
you fall back to a broad content grep across the entire vault, tell the user:
> *(broad vault grep — this is the expensive path; answer confidence may be lower)*

---

### Phase 4 — Synthesis

Construct the answer using ONLY information found in the wiki pages you read.

Write the Answer section as human prose — it is meant to be read, not scanned. Apply
`/llm-wiki:humanize-writing` principles: earned specificity over vague adjectives, no
hollow openers, say the thing directly without wind-up phrases, mix sentence lengths.
Wiki entity names and technical terms are exempt from slop-word rules.

**Answer format**:
```markdown
## Answer

[Your synthesized answer. Write with information density. No filler phrases.
If comparing entities, use a table. If summarizing, use structured headings.
Every significant claim should be traceable to a specific page.]

## Sources (from wiki)
- [[entity_page_1]] (source_count: N, status: active, via: summary) — contributed: <what it added>
- [[entity_page_2]] (source_count: N, status: verified, via: grep) — contributed: <what it added>
- [[entity_page_3]] (source_count: N, status: draft, via: full-read) — contributed: <what it added>

## Caveats
[If any pages are status: draft or status: contradictory, note this clearly.
If the query asks about something not yet in the wiki, say so explicitly —
do NOT fill gaps with training data. Instead, recommend ingesting a source.]
```

**Critical rule**: If the wiki does not contain enough information to answer the question
confidently, say so. Tell the user what source they could add to raw/ to fill the gap.
Do NOT draw on pre-training knowledge to supplement the wiki. The wiki's epistemic
boundaries are the answer's epistemic boundaries.

---

### Phase 5 — Query Logging

Append to `log.md` after every query (including index-only and filtered modes):

```
- [<YYYY-MM-DDThh:mm:ssZ>] QUERY query="<the user's question>" result_pages=<N> mode=<normal|index_only|filtered> escalated=<true|false>
```

`escalated=true` means the broad vault grep fallback was triggered. This log entry keeps
`log.md` as a complete audit trail of all wiki operations, not just ingestions.

---

### Phase 6 — Generative Filing (The Compounding Step)

After answering, evaluate whether this synthesis is valuable enough to persist:

**File back if the answer is**:
- A non-trivial comparison between 2+ entities not previously captured
- A synthesis that reveals a previously undocumented relationship
- An answer that took 4+ wiki pages to construct (it's a new hub node)
- Something the user will likely ask again

**Do NOT file back if**:
- It's a simple lookup of a single page's content (no synthesis value)
- It's a meta-query about the wiki structure itself
- The user explicitly says not to

**If filing back**, ask first:
```
This answer synthesizes a new connection between [[entity_1]] and [[entity_2]]
that isn't captured anywhere in the wiki yet.

File this synthesis as a new wiki page?
  Suggested name: <proposed_snake_case_filename>
  Suggested type: comparison | synthesis | guide
[yes / no / edit name]
```

If confirmed, create the new entity page with:
```yaml
---
domain: <current_domain>
type: synthesis
source_count: <N>  # number of wiki pages this synthesized from
status: active
visibility: private
tags:
  - <tags>
related:
  - "[[all source pages used in synthesis]]"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
```

Page body should document:
- The question that generated this synthesis (as context)
- The synthesized answer with all wiki-links intact
- A `## Synthesis Method` section noting which pages were combined and why

Add to index.md. The Phase 5 log entry will record this query; also append a second line noting the new page created:
```
- [<TIMESTAMP>] FILED page="wiki/<synthesis_filename>.md" from_query="<question>"
```

---

## Special Query Modes

### Comparative Query (`compare X and Y`)
- Build a structured comparison table as the primary output format
- Use the entity page attributes (source_count, status, tags) as comparison axes
- If one entity has significantly more sources than the other, note the asymmetry

### Contradiction Query (`what contradictions exist`)
- Run a targeted scan for all pages with `status: contradictory`
- Present each contradiction clearly: what the conflict is, which sources disagree
- Do NOT attempt to resolve contradictions — present them for human arbitration

### Meta Query (`what's the wiki's coverage of X topic`)
- Scan index.md for all pages tagged with or related to X
- Report coverage: number of pages, total source_count across those pages, any gaps
- Identify which aspects of X are well-covered vs. under-documented

### Deep Synthesis (`synthesize everything about X`)
- Load ALL pages related to X (primary, secondary, and tertiary)
- Build a comprehensive synthesis document
- This ALWAYS triggers the generative filing offer — deep syntheses are always worth filing
- If the synthesis reveals a complex web of relationships, offer to create a companion
  `.canvas` file alongside the synthesis page to visualize the entity graph spatially.
  Use `/llm-wiki:obsidian-json-canvas` for the canvas structure.
