---
name: context-compression
description: Use when managing long-running agent sessions, preserving critical information as context fills, or optimizing tokens-per-task completion rate
---

# Context Compression for Agent Sessions

## Overview

Context compression optimizes for **tokens-per-task** (total tokens to completion), not tokens-per-request. Aggressive compression that loses critical information triggers expensive re-fetching—negating savings. The goal is strategic reduction without losing the information needed to continue effectively.

**Core principle:** Compression is a trade-off between context size, output quality, and re-fetch cost. Different methods suit different session types.

## When to Use

**Triggers:**
- Long-running sessions (5+ turns with accumulating context)
- Agents hitting context limits mid-task
- Need to preserve artifact tracking (which files changed?)
- Session has clear phases (research → planning → execution)
- Debugging sessions where compression history matters

**When NOT to use:**
- Short single-phase tasks (just context-window management)
- One-off queries (no compression needed)
- Tasks requiring full interpretability of intermediate steps

## Three Production Compression Methods

### 1. Anchored Iterative Summarization (Recommended)

**Best for:** Long sessions where file tracking and decision history matter
**Token savings:** 70-80% compression ratio
**Quality score:** 4.65/5.0

Maintains a persistent summary with fixed sections. On compression:
1. Identify newly-truncated content (messages falling off context window)
2. Summarize *only that new content*
3. Merge into existing summary sections
4. Drop the truncated messages

**Structure:** Use these mandatory sections:
- **Session Intent** — Original goal, constraints, success criteria
- **Files Modified** — Absolute paths, specific identifiers (function names, error codes)
- **Decisions Made** — Why X was chosen over Y, dependencies
- **Current State** — System status, incomplete tasks, open questions
- **Next Steps** — What happens on resume

```markdown
## Session Summary

**Session Intent:** Ingest three raw sources on transformer architecture into the wiki.

**Files Modified:**
- `wiki/concepts/transformer_architecture.md` — Created, source_count: 1
- `wiki/entities/andrej_karpathy.md` — Updated, source_count: 3
- `index.md` — 2 new rows added

**Decisions Made:**
- Merged attention_mechanism into transformer_architecture (not a separate page — too tightly coupled)
- Flagged scaling_laws as contradictory — two sources disagree on parameter counts

**Current State:**
- 2 of 3 sources ingested
- 1 contradiction flagged awaiting human arbitration
- Link weaving complete for ingested pages

**Next Steps:**
- Ingest raw/scaling_laws_survey.md
- Resolve contradiction in [[scaling_laws]]
```

**Gotchas:**
- Artifact tracking scores only 2.2-2.5/5.0 even with structured sections. Supplement with separate artifact indexing if file tracking is critical.
- Sections must be explicit checklist items; omissions become visible rather than silent.

### 2. Opaque Compression

**Best for:** Short sessions prioritizing maximum token savings
**Token savings:** 95-99% compression ratio
**Quality score:** 2.1/5.0

Compress the entire session to a single dense summary. Sacrifices interpretability—you cannot verify what was preserved without evaluation probes.

**When to use:**
- Tokens are severely constrained
- Output quality is less critical than throughput
- Debugging not required

**When NOT to use:**
- Artifact tracking matters
- Debugging or troubleshooting needed
- Decision rationale must be preserved

**Implementation:** Feed the full conversation to Claude with:
> "Compress this session to the absolute minimum needed to continue. Target 99% compression. Preserve: original goal, final decisions, current state, what's next."

Then use only the result. Never revert to full history.

### 3. Regenerative Full Summary

**Best for:** Sessions with clear phase boundaries (research → planning → execution)
**Token savings:** 80-85% compression ratio
**Quality score:** 4.2/5.0

Generate a complete, detailed summary at phase transitions. Weakness: cumulative detail loss across repeated cycles.

**When to use:**
- Readability of summary matters
- Sessions have natural phase breaks
- Re-fetching is cheap

**When NOT to use:**
- Sessions are continuous (no clear boundaries)
- Many compression cycles planned
- Artifact preservation is critical

## Critical Implementation Pattern: Artifact Trail

**Problem:** File tracking scores only 2.2-2.5/5.0 across all methods. Compressed summaries lose specificity.

**Solution:** Implement separate artifact indexing parallel to compression:

```markdown
## Artifact Index (separate from summary)

| File | Created | Modified | Current State |
|------|---------|----------|----------------|
| `wiki/concepts/transformer_architecture.md` | Turn 3 | Turn 18 | source_count: 2, status: active |
| `wiki/entities/andrej_karpathy.md` | Turn 1 | Turn 5 | source_count: 3, status: verified |
| `index.md` | — | Turn 23 | 2 new rows added |
```

Keep this index outside the summarization—it's your ground truth for "what changed."

## Compression Triggers

### Default Strategy: Sliding Window

Trigger compression at 70-80% context utilization:

```
Keep: [Last 15 turns] + [Compressed earlier history]
```

Simple, predictable, works for most sessions.

### Task-Boundary Triggers

Better when sessions have natural phases:

```
Research Phase  → [Compress to structured analysis]
Planning Phase  → [Compress to implementation spec]
Execution Phase → [Keep focused context]
```

Research shows this reduces re-fetch cost by 40%.

## Compression Quality Evaluation

**Don't trust metrics.** Evaluate with targeted probes after compression:

### Probe 1: Technical Accuracy
Ask the agent to recall specific details:
- Which wiki pages were created or modified?
- What source_count values were set?
- What contradictions were flagged?

**Pass threshold:** 90%+ accuracy on specific identifiers

### Probe 2: Artifact Tracking
- List all files touched in this session
- State current status of each

**Pass threshold:** 100% file list accuracy

### Probe 3: Continuation Logic
- What's the next step?
- What decisions led here?

**Pass threshold:** Sufficient to resume without re-reading original context

### Probe 4: Decision Rationale
- Why was X chosen over Y?
- What constraint made that decision necessary?

**Pass threshold:** Matches original decision log

## Three-Phase Workflow for Large Ingestion Sessions

For ingesting large raw sources (full books, long transcripts, large PDF batches):

### Phase 1: Source Analysis (Compress Aggressively)
- Goal: Understand the source
- Load: Raw document sections, index.md
- Compress to: 2,000-word structured analysis
  - Major entities identified
  - Relationships discovered
  - Potential contradictions with existing wiki

### Phase 2: Planning (Keep Spec Dense)
- Goal: Decide what pages to create/update
- Load: Analysis summary, relevant existing wiki pages
- Compress to: ~2,000 words (ingestion blueprint)
  - Pages to create (with draft frontmatter)
  - Pages to update (with specific changes)
  - Link weaving plan

### Phase 3: Execution (Focused Context)
- Goal: Write the pages
- Load: Current page being written, spec section
- Compression: Minimal—keep full context for active files

## Critical Trade-offs

**Anchored vs. Aggressive:**
- Anchored retains 0.7% more information
- Anchored scores 0.35 quality points higher
- Anchored adds 2-3 minutes per compression cycle
- **Use anchored when:** Re-fetching has costs (reading wiki pages, re-parsing raw sources)
- **Use aggressive when:** Pure context constraint (approaching hard limit)

## Gotchas & Failure Modes

| Gotcha | Symptom | Prevention |
|--------|---------|-----------|
| **Compression loss compounds** | Three 95% compressions = 0.0125% original | Use 70-80% ratio per cycle, limit cycles |
| **Page content hallucinated** | "Updated" page content appears after compression | Never trust compressed page content; re-read from disk |
| **Early constraints forgotten** | Agent violates rules from turn 1 | Preserve original constraints separately |
| **Index goes stale** | index.md out of sync after compression | Update artifact index *before* compressing |
| **Summaries lose nuance** | "Updated page" hides that update was partial | Include decision context, not just outcomes |

## Compression Checklist

- [ ] Compression method chosen (anchored/opaque/regenerative)
- [ ] Trigger point defined (70-80% utilization or task boundary)
- [ ] Mandatory sections included if using anchored method
- [ ] Artifact index maintained separately
- [ ] Quality probes defined (technical accuracy, continuation logic)
- [ ] Compression ratio documented (expect 70-85%)
- [ ] index.md and log.md state captured before compressing

## References

- `/llm-wiki:context-fundamentals` — Position strategy, token allocation
- `/llm-wiki:persistent-memory-management` — Cross-session checkpointing and memory files
