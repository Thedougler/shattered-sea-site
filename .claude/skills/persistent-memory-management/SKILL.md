---
name: persistent-memory-management
description: Use when establishing session memory patterns, loading context at startup, managing cross-session knowledge, or preventing context loss through checkpoints and summaries
---

# Persistent Memory Management

## Overview

This vault runs a **two-track memory model**. Understand the difference before touching anything:

| Track | Files | Owner | Purpose |
|-------|-------|-------|---------|
| **Vault memory** | `content/hot.md`, `content/log.md` | wiki_guard.py + ingest ops | Live vault state, audit trail. Written by structured wiki operations. |
| **Agent memory** | `.claude/memory/MEMORY.md`, `.claude/memory/archive/` | Agent (you) | Cross-session decisions, lessons learned, active project context. |
| **Repo memory** | `/memories/repo/*.md` | Agent (you) | Codebase-scoped facts: build commands, tooling quirks, verified practices. |

**Never conflate these tracks.** `content/hot.md` is the vault's own working state — you read it, but `wiki_guard.py --ingest-finalize` writes it. `MEMORY.md` is yours alone.

---

## Session Startup — Boot Sequence

Run this mentally every session before engaging with the user's request:

**Step 1 — Load vault context**
```
read_file: content/index.md       ← master entity catalog; required before any op
read_file: content/hot.md         ← recent vault activity; what changed last session
read_file: .claude/memory/MEMORY.md  ← your cross-session decisions
```

**Step 2 — Check for interrupted work**
```
file_search: .claude/memory/next-session-prompt.md
  → if found: read it, act on it, then delete it
```

**Step 3 — Vault health (run only if issues suspected or first session)**
```
python .claude/bin/wiki_guard.py --status-agent
```

**Step 4 — Resume briefing**
Announce to the user what the vault state is and any pending work from `hot.md`.

---

## Memory Tiers — Detail

### Vault Memory (read-only for agent)

**`content/hot.md`** — ~500-word semantic snapshot of recent vault activity.
- Written by `wiki_guard.py --ingest-finalize` after every ingest
- Updated manually after synthesis or major lint operations
- Read at boot to understand what happened last session
- **Never write to this directly** — always go through `wiki_guard.py`

**`content/log.md`** — Append-only audit trail.
- One line per operation: `[YYYY-MM-DD] OP type — summary`
- Written by `wiki_guard.py --ingest-finalize`
- Read to audit what has been ingested; never edit prior entries

### Agent Memory (you own this)

**`.claude/memory/MEMORY.md`** — Hot cache of active cross-session state.
- Keep under 200 lines
- Index format: `- [Title](file.md) — one-line hook`
- Full content in separate files; MEMORY.md is the index
- Refresh after any decision worth keeping across sessions

**`.claude/memory/archive/`** — Closed decisions, deprecated patterns.
- Move entries here when they're no longer active
- Never delete — archive is permanent reference

### Repo Memory (codebase facts)

**`/memories/repo/*.md`** — Persistent codebase-scoped notes loaded by VS Code Copilot.
- Store: build commands, wiki_guard.py quirks, layout conventions, verified patterns
- Use the `memory` tool (`command: create`) to write new files here
- Examples already in this vault: `wiki_guard_ingest_finalize.md`, `wiki_guard_layout_detection.md`, `wiki_guard_lint_agent_output.md`
- Check these before running wiki_guard.py — quirks and workarounds are documented here

---

## Checkpoint Before Compression

When approaching context limits (50+ exchanges or large ingest batch):

```
1. Scan conversation for actionable decisions
2. Write to .claude/memory/ using memory file types (user/feedback/project/reference)
3. Commit: git add .claude/memory/ && git commit -m "checkpoint: <summary>"
4. Announce to user: "Checkpointing before compression"
```

**Never let compression erase decisions.** Checkpointing is non-negotiable before context clears.

For the technical mechanics of compression — artifact tracking, quality probes — see the `context-compression` skill.

---

## End of Session — `/close-day` Pattern

```
1. Scan conversation for patterns and decisions
2. Extract:
   - New agent decisions → .claude/memory/MEMORY.md
   - Tooling quirks / verified patterns → /memories/repo/<topic>.md
   - Failures / wrong paths → .claude/memory/archive/failures.md
   - Interrupted work → .claude/memory/next-session-prompt.md (only if mid-task)
3. Commit: git add .claude/memory/ && git commit -m "close-day: <summary> — YYYY-MM-DD"
```

**Rule:** If tomorrow's Claude doesn't know something today's Claude discovered, synthesis failed.

---

## Commit Patterns for This Vault

Operations touch different paths. Use the right `git add` scope:

| Operation | Commit command |
|-----------|---------------|
| Wiki ingest (content pages updated) | `git add content/ && git commit -m "ingest: <source>"` |
| Agent memory checkpoint | `git add .claude/memory/ && git commit -m "checkpoint: <summary>"` |
| End of day | `git add .claude/memory/ && git commit -m "close-day: <summary> — YYYY-MM-DD"` |
| Wiki tooling change (wiki_guard.py) | `git add .claude/ && git commit -m "wiki-tools: <summary>"` |
| Mixed (ingest + memory) | `git add content/ .claude/memory/ && git commit -m "ingest+checkpoint: <summary>"` |

Never use `git add .` — it risks committing build artifacts or raw/ accidentally.

---

## File Templates

### MEMORY.md

```markdown
---
last-updated: YYYY-MM-DD
session-count: N
---

# Memory Index

- [Decision Title](decision.md) — one-line hook
- [Another Decision](another.md) — why it matters

---

## Active Decisions
- YYYY-MM-DD: <decision> — <reason>
```

Keep under 200 lines. Move inactive entries to `archive/`.

### Individual Memory Files

```markdown
---
name: <memory-name>
description: <one-line description for search>
type: <user | feedback | project | reference>
---

<Lead with the rule or fact.>
**Why:** <reason/motivation>
**How to apply:** <when/where it kicks in>
```

### next-session-prompt.md

Write ONLY when suspending mid-task:

```markdown
# Session Resume

**Context:** Where we left off
**Blockers:** What's pending
**Next step:** Exactly what to do first
**Active files:** Which pages were being modified
```

Delete immediately after reading at next session start.

---

## Common Mistakes

**Mistake 1: Writing to `content/hot.md` directly**
- Symptom: Hot cache diverges from actual vault state; `wiki_guard.py` overwrites your edits
- Fix: Never write `content/hot.md` manually. Let `--ingest-finalize` handle it.

**Mistake 2: Skipping `content/index.md` at boot**
- Symptom: Creating duplicate pages, broken wikilinks, index drift
- Fix: Always read `content/index.md` as the first action of any wiki operation

**Mistake 3: Forgetting to checkpoint before context compression**
- Symptom: Decision from morning is gone by afternoon
- Fix: Watch for "context compression" in system messages; checkpoint immediately

**Mistake 4: MEMORY.md grows too large**
- Symptom: Index too dense to scan; hot cache loses its speed advantage
- Fix: Archive old entries to `.claude/memory/archive/` with date
- Prevention: Monthly review — if a memory wasn't referenced this month, archive it

**Mistake 5: Confusing agent memory with repo memory**
- Symptom: Tooling quirks written to MEMORY.md instead of `/memories/repo/`; lost when switching workspaces
- Fix: Codebase-scoped facts go to `/memories/repo/`; personal/session decisions go to `.claude/memory/`

**Mistake 6: Using `git add .` for commits**
- Symptom: Build artifacts, raw/ files, or temp files get committed
- Fix: Always scope `git add` to the changed path (see commit patterns table above)

---

## Hooks — What's Active in This Vault

Current `.claude/hooks/hooks.json`:

| Event | Trigger | Action |
|-------|---------|--------|
| `PostToolUse` (Write) | File path contains `/raw/` | Remind: run `--ingest-agent` to process new source |
| `PostToolUse` (Bash) | Command includes `cp`/`mv` and output includes `raw/` | Remind: run `--ingest-agent` |
| `Stop` | Session ending | Remind: checkpoint to `.claude/memory/` if decisions made |

There is no automatic session-start hook. Boot sequence is manual (run by you on every session).

---

## Quick Reference Checklists

### Session Startup
- [ ] Read `content/index.md`
- [ ] Read `content/hot.md`
- [ ] Read `.claude/memory/MEMORY.md`
- [ ] Check for `next-session-prompt.md` — read + delete if present
- [ ] Announce vault state to user

### Before Context Compression
- [ ] Scan conversation for decisions
- [ ] Write new entries to `.claude/memory/`
- [ ] Commit: `git add .claude/memory/ && git commit -m "checkpoint: <summary>"`
- [ ] Announce to user

### End of Session
- [ ] Extract decisions → `.claude/memory/MEMORY.md`
- [ ] Extract tooling facts → `/memories/repo/<topic>.md`
- [ ] Log failures → `.claude/memory/archive/failures.md`
- [ ] Write `next-session-prompt.md` (only if mid-task)
- [ ] Commit: `git add .claude/memory/ && git commit -m "close-day: <summary> — YYYY-MM-DD"`

### Memory File Type Guide

| Type | Use For | Lead with |
|------|---------|-----------|
| **user** | Role, preferences, knowledge | Fact → **Why:** context |
| **feedback** | Corrections & validations | Rule → **Why:** reason → **How to apply:** when |
| **project** | Active goals, deadlines, context | Fact → **Why:** motivation → **How to apply:** influence |
| **reference** | External resource pointers | Resource → **When:** context → **Value:** why it matters |

---

## Anti-Rationalization Guards

**Checkpointing is not optional.** If you think "I'll just remember this," you won't.

**Synthesis is not deferrable.** End-of-session synthesis happens immediately, always.

**`next-session-prompt.md` must be deleted.** Write it only for interrupted work. Delete in the first action of the next session.

**`content/hot.md` is vault-owned.** Reading it is free; writing it is prohibited outside of `wiki_guard.py --ingest-finalize`.
