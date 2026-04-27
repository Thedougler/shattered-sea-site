---
name: writing-plans
description: Use when you have an approved design or complex multi-step vault operation to plan — before starting implementation. Breaks work into bite-sized tasks with exact paths and verification steps.
---

# Writing Plans

> Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT License) — modified for LLM Wiki vault operations.

## Overview

Write comprehensive implementation plans assuming the next agent has zero vault context. Document everything: which files to touch, exact content, how to verify. Bite-sized tasks. Frequent commits.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `.claude/plans/YYYY-MM-DD-<feature-name>.md`

## Scope Check

If the design covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking into separate plans — one per subsystem. Each plan should produce a working, verifiable vault state on its own.

## File Mapping

Before defining tasks, map out which files will be created or modified:

- Design units with clear boundaries (one page = one responsibility)
- Follow existing vault conventions and directory routing
- In existing vault structure, follow established patterns — don't restructure unilaterally

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Create the page" — step
- "Verify page exists" — step
- "Update wiki/index.md with new slug" — step
- "Run /llm-wiki:lint" — step
- "Git commit" — step

## Plan Document Header

```markdown
# [Feature Name] Implementation Plan

> **For execution:** Use `executing-plans` skill to implement task-by-task.

**Goal:** [One sentence describing what this builds]
**Approach:** [2-3 sentences about approach]
**Affected Files:** [Key wiki paths]

---
```

## Task Structure

````markdown
### Task N: [Description]

**Files:**
- Create: `wiki/entities/new-entity.md`
- Modify: `index.md`
- Verify: `/llm-wiki:lint`

- [ ] **Step 1: Create page**

Create `wiki/entities/new-entity.md` with content:
```markdown
---
type: entity
summary: One-line summary here
...frontmatter...
---
# New Entity
...page content...
```

- [ ] **Step 2: Verify page exists**

Read the newly created `wiki/entities/new-entity.md`
Expected: Page content matches what was written

- [ ] **Step 3: Update index**

Add to `index.md`:
```
| [[new-entity]] | one-line summary | 1 | draft | YYYY-MM-DD |
```

- [ ] **Step 4: Validate**

Run: `/llm-wiki:lint`
Expected: 0 errors

- [ ] **Step 5: Commit**

```bash
git add wiki/ index.md && git commit -m "feat: add new entity page"
```
````

## No Placeholders

Every step must contain actual content. These are **plan failures** — never write:
- "TBD", "TODO", "implement later"
- "Add appropriate frontmatter" (show the actual YAML)
- "Create wikilinks as needed" (list the exact links)
- "Similar to Task N" (repeat the content)
- Steps that describe what to do without showing how

## Verification Steps

Every task MUST include verification. Wiki-specific verification commands:

| Operation | Verification |
|-----------|-------------|
| Create page | Read the page back |
| Update frontmatter | Read page back, check fields |
| Add wikilinks | Confirm link targets exist in vault |
| Update index | Read `index.md` — confirm entry present |
| Git commit | `git status` — verify clean |
| Batch operation | `/llm-wiki:lint` — 0 errors |

## Self-Review

After writing the plan:

1. **Design coverage:** Can you point to a task for each requirement? List any gaps.
2. **Placeholder scan:** Search for "TBD", "TODO", vague instructions. Fix them.
3. **Path consistency:** Do file paths in later tasks match what earlier tasks created?
4. **Wikilink validity:** Do any tasks create wikilinks to pages that won't exist yet? Reorder if needed.

Fix issues inline. No need to re-review.

## Execution Handoff

After saving the plan:

> "Plan complete and saved to `.claude/plans/<filename>.md`. Ready to execute with `executing-plans` skill, or would you like to review first?"

**If approved:** Use `executing-plans` skill to implement task-by-task.
**If revisions needed:** Revise plan inline and re-offer.
