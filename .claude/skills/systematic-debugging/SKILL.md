---
name: systematic-debugging
description: Use when encountering any bug, error, or unexpected behavior in wiki operations, git hooks, validation failures, broken wikilinks, frontmatter errors, or vault inconsistencies — before proposing fixes.
---

# Systematic Debugging

> Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT License) — modified for LLM Wiki vault operations.

## Overview

Random fixes waste time and create new problems. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue in the vault ecosystem:
- `/llm-wiki:lint` failures
- Git hook errors (pre-commit, post-commit)
- YAML frontmatter parse errors
- Broken or orphaned wikilinks
- Index inconsistencies
- Obsidian CLI errors
- Ingestion failures (pages not created, source_count wrong)

**Use this ESPECIALLY when:**
- Under time pressure (mid-session, user waiting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - Run `/llm-wiki:lint` — does it show the issue?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - `git log --oneline -5` — what changed recently?
   - `git diff` — any uncommitted changes?
   - Did a recent ingest or edit introduce the issue?

4. **Gather Evidence in Multi-Component Systems**

   The wiki has multiple layers. Trace data flow through:

   ```
   raw/ sources → ingest skill → wiki/ pages → index.md → Obsidian vault
   ```

   For EACH component boundary:
   - Does the file exist on disk? (`find wiki/ -name "*.md" | grep <slug>`)
   - Does the page have valid frontmatter? (Read the file, check YAML block)
   - Is git tracking it? (`git status`)

5. **Trace Data Flow**
   - Where does the bad value originate?
   - Trace backward: broken wikilink → which page? → which ingest created it? → which source?
   - Fix at source, not at symptom
   ```bash
   obsidian backlinks file="<slug>"              # inspect inbound links for a page
   obsidian search query="[[<slug>]]"            # find all pages linking to this slug
   grep -r "\[\[<slug>\]\]" wiki/               # find wikilink references across vault
   ```

### Phase 2: Pattern Analysis

1. **Find Working Examples**
   - Locate similar working pages in the vault
   - Compare frontmatter structure, wikilink syntax
   ```bash
   obsidian search query="type:<entity-type>" limit=5   # find similar pages
   obsidian read file="<working-page-slug>"              # compare frontmatter + structure
   ```

2. **Compare Against References**
   - Check the ingest skill's YAML template for correct structure
   - Read `index.md` for expected entries
   - Read the relevant skill for expected behavior

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small

### Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis**
   - "I think X is the root cause because Y"
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T stack more fixes on top

### Phase 4: Implementation

1. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements

2. **Verify Fix**
   - Run `/llm-wiki:lint` — clean?
   - `git status` clean after commit?
   - Run the operation that originally failed

3. **If Fix Doesn't Work**
   - STOP and count: How many fixes have you tried?
   - If < 3: Return to Phase 1 with new information
   - **If ≥ 3: STOP and escalate to the user**

4. **If 3+ Fixes Failed: Question Architecture**
   - Is the approach fundamentally sound?
   - Should we restructure rather than patch?
   - **Alert the user before attempting more fixes**

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Fix multiple things, run lint"
- "Skip verification, I'll check later"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**

**ALL of these mean: STOP. Return to Phase 1.**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too |
| "Emergency, user is waiting" | Systematic debugging is FASTER than thrashing |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause |
| "One more fix attempt" (after 2+ failures) | 3+ failures = structural problem. Escalate. |

## Supporting Techniques

### Root-Cause Tracing

Trace bugs backward through the system to find the original trigger:
1. Start at the error (broken wikilink, bad YAML, missing index entry)
2. What created this? (which ingest, which manual edit)
3. What fed that operation? (which source, which raw file)
4. Keep tracing until you find the source
5. Fix at source, not at symptom

### Defense in Depth

After finding root cause, add validation at every layer:
- **Entry point:** `/llm-wiki:lint` catches it on next run
- **Operation level:** The skill that runs this operation checks for it
- **Git hook:** Pre-commit catches it before it's committed

### Condition-Based Waiting

Replace assumptions with checks:
- Don't assume tools are up — run `obsidian eval code="app.vault.getFiles().length"`
- Don't assume a page exists — read it
- Don't assume git is clean — run `git status`
- Don't assume index is current — read `index.md`

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Single fix, verify | Issue resolved, lint clean |
