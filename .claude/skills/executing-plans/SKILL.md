---
name: executing-plans
description: Use when you have a written implementation plan to execute step by step — loads plan, reviews critically, executes all tasks with verification, commits when complete
---

# Executing Plans

> Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT License) — modified for LLM Wiki vault operations.

## Overview

Load plan, review critically, execute all tasks, verify each step, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Load and Review Plan

1. Read the plan file from `.claude/plans/`
2. Review critically — identify any questions or concerns
3. If concerns: Raise them with the user before starting
4. If no concerns: Proceed to execution

### Step 2: Execute Tasks

For each task in the plan:

1. **Mark as in-progress** (via todo tracking)
2. **Follow each step exactly** — the plan has bite-sized steps for a reason
3. **Run verifications as specified** — do NOT skip verification steps
4. **Use `verification-before-completion`** — evidence before claiming step is done
5. **Mark as completed** — only after verification passes
6. **Commit as specified** — follow the plan's commit instructions

### Step 3: Final Verification

After all tasks complete:

1. Run `/llm-wiki:lint` — must be clean
2. `git status` — must be clean
3. `git log --oneline -3` — verify commits look correct
4. Report to user: tasks completed, issues found, final state

## When to Stop and Ask

**STOP executing immediately when:**
- Hit a blocker (page doesn't exist, validation fails unexpectedly)
- Plan has gaps — step says "create page" but doesn't show content
- Verification fails and you don't understand why
- Two tasks conflict (both want to edit the same section)

**Ask for clarification rather than guessing.** Don't force through blockers.

## When to Use Parallel Agents

If the plan has 3+ independent tasks (different pages, no shared state), consider using `dispatching-parallel-agents` to execute them concurrently. Check the plan's task dependencies first — only parallelize truly independent work.

## Key Rules

- **Follow plan steps exactly** — don't improvise or "improve"
- **Don't skip verifications** — they're there for a reason
- **Stop when blocked** — don't guess
- **One task at a time** — mark in-progress, complete, then next
- **Commit as instructed** — follow the plan's commit messages and grouping
