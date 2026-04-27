---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing — before committing, reporting to the user, or moving to the next operation. Requires running verification commands and confirming output before making any success claims. Evidence before assertions, always.
---

# Verification Before Completion

> Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT License) — modified for LLM Wiki vault operations.

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Wiki Verification Commands

| Claim | Verification Command | Not Sufficient |
|-------|---------------------|----------------|
| Pages created correctly | Read each page back | "Created successfully" without reading back |
| Frontmatter valid | Read page back, confirm all required fields present | "YAML looks correct" by eyeballing |
| Git commit clean | `git status` + `git log --oneline -1` | "Committed" without checking |
| Wikilinks work | `grep -r "\[\[<target>\]\]" wiki/` + confirm target file exists | "Added wikilinks" without verifying targets exist |
| Index updated | Read `index.md`, confirm entry present | "Updated index" without reading it |
| No broken links | `/llm-wiki:lint dead_links` — 0 errors | Partial check, spot-checked one page |
| Vault accessible | `obsidian eval code="app.vault.getFiles().length"` | Assuming Obsidian is running |
| Ingest complete | Read each created/updated page + verify source_count incremented | "Ingest done" without verifying pages |
| Lint clean | `/llm-wiki:lint` → read full output → 0 issues | "Ran lint" without reading output |

## Red Flags — STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit without running `git status` first
- Trusting a subagent's success report without independent verification
- Relying on partial verification (checked 1 of 5 pages)
- Thinking "just this once"
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "I checked the first page" | Check ALL pages |
| "Batch-planned all writes, executing now" | Process one file at a time — read, write, verify each before moving to the next |
| "Lint will catch it" | Run lint NOW, don't defer |
| "I'll verify in the next operation" | Verify NOW, not later |
| "Different words so rule doesn't apply" | Spirit over letter |

## Wiki-Specific Patterns

**Page creation:**
```
✅ Create page → read page back → verify frontmatter + content → "Page created with correct frontmatter"
❌ "Page created successfully"
```

**Ingest operation:**
```
✅ Run ingest → read each new page → verify index updated → /llm-wiki:lint → git status clean → "Ingest complete: 3 pages created, 0 lint errors"
❌ "Ingest complete" (without reading pages back)
```

**Link weaving:**
```
✅ Add wikilinks → grep for [[target]] in modified pages → confirm target files exist → "Links woven: [[entity-a]] ↔ [[entity-b]] both verified"
❌ "Links added" (without confirming targets exist)
```

**Lint / health check:**
```
✅ /llm-wiki:lint → read output → count issues → "Health check: 2 warnings, 0 errors"
❌ "Lint passed" (without reading output)
```

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- Committing to git
- Reporting operation results to the user
- Moving to the next wiki operation

**Rule applies to:**
- Exact phrases, paraphrases, synonyms
- Implications of success
- ANY communication suggesting completion or correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
