---
name: persistent-memory-management
description: Use when establishing session memory patterns, loading context at startup, managing cross-session knowledge, or preventing context loss through checkpoints and summaries
---

# Persistent Memory Management

## Overview

Persistent memory is the operating system layer for Claude Code. It keeps architectural decisions, project context, and proven patterns alive across sessions so you don't restart from scratch. Core principle: **what matters survives between sessions, automatically**.

## When to Use

**Trigger these patterns:**
- Session startup — load memory automatically via hooks
- Long conversations (50+ exchanges) — checkpoint before context compression
- End of work day — synthesize learnings into permanent knowledge
- Context loss risk — safety nets prevent decisions from vanishing
- Cross-project knowledge — share patterns between independent projects

**When NOT to use:**
- Simple one-off tasks (ephemeral state belongs in conversation)
- Conversation context that's already in the chat (don't duplicate)
- Mechanical constraints (use settings.json/hooks instead)

## Core Pattern

### 1. Session Startup — Load Memory Automatically

Every session begins with context injection:

```yaml
# .claude/hooks/session-start.py
- Load MEMORY.md (hot cache of active project state)
- Load CLAUDE.md (agent brain + project rules)
- Load next-session-prompt.md (if present — resume interrupted work)
- Announce loaded context to user
```

**Your move:** Create `next-session-prompt.md` only when suspending work mid-task. Delete it after resuming.

### 2. Memory Structure — Three Tiers

| Tier | File | Purpose | Refresh |
|------|------|---------|---------|
| **Hot** | `.claude/memory/MEMORY.md` | Active decisions, cross-session context (~200 lines max) | Every conversation |
| **Archive** | `.claude/memory/archive/` | Closed projects, deprecated patterns, historical decisions | Manual (never auto-delete) |
| **Knowledge** | `wiki/concepts/` or project-specific `knowledge/` | Permanent reference articles built from daily work | Daily synthesis |

### 3. Checkpoint Before Compression

When approaching context limits:

```
Before context compression happens:
  1. Scan conversation for actionable decisions
  2. Write to MEMORY.md using the memory types (user/feedback/project/reference)
  3. Commit: git add .claude && git commit -m "checkpoint: <summary>"
  4. Announce to user: "Checkpointing before compression"
```

**Safety rule:** Never let compression erase decisions. Checkpointing is non-negotiable before context clears.

For the technical HOW of compression itself—which method to use, artifact tracking, quality probes—see `/llm-wiki:context-compression`.

### 4. Daily Synthesis — `/close-day` Pattern

At end of work:

```
1. Scan today's conversation for patterns
2. Extract:
   - New decisions (add to MEMORY.md)
   - Failures (log to failures.md)
   - Discoveries (file to knowledge/)
   - Next session setup (write next-session-prompt.md if needed)
3. Commit all: git add .claude && git commit -m "close-day: <summary> — YYYY-MM-DD"
```

**Measure:** If tomorrow's Claude doesn't know something today's Claude learned, you failed synthesis.

## File Templates

### MEMORY.md Structure

```markdown
---
last-updated: 2026-04-21
session-count: 42
---

# Memory Index

- [Title](file.md) — one-line hook
- [Another Decision](decision.md) — why it matters

---

## Active Decisions
- Date, decision, reason
- Date, decision, reason
```

Keep under 200 lines. Index everything; full content in separate files.

### Individual Memory Files

```markdown
---
name: {{memory-name}}
description: {{one-line description for search}}
type: {{user | feedback | project | reference}}
---

{{Content. For feedback/project:
- Lead with the rule/fact
- **Why:** reason/motivation
- **How to apply:** when/where it kicks in
}}
```

### next-session-prompt.md

Write ONLY if suspending mid-task:

```markdown
# Session Resume

**Context:** Where we left off
**Blockers:** What's pending
**Next step:** Exactly what to do first
**Files open:** Which files were active
```

Delete after reading.

## Common Mistakes

**Mistake 1: Forgetting to checkpoint before compression**
- Symptom: Decision from morning is gone by afternoon
- Fix: Set a calendar reminder at session start: "Checkpoint before 50 exchanges"
- Prevention: Make checkpointing a reflex—watch for "context compression" in system messages

**Mistake 2: MEMORY.md grows too large**
- Symptom: Too much detail in the hot cache
- Fix: Archive old entries to `archive/` directory with date
- Prevention: Monthly review—if a memory wasn't referenced this month, move it

**Mistake 3: Duplicating information between MEMORY.md and CLAUDE.md**
- Symptom: Same decision documented twice
- Fix: CLAUDE.md = permanent rules; MEMORY.md = session-specific state
- Prevention: Search both before writing; if it's timeless, it goes in CLAUDE.md

**Mistake 4: Writing next-session-prompt.md for every task**
- Symptom: File never gets deleted; accumulates obsolete context
- Fix: Use it ONLY for interrupted work; delete immediately after resuming
- Prevention: Delete in first line of next session: "Resuming from last session—deleting next-session-prompt.md"

**Mistake 5: Synthesis without structure**
- Symptom: Daily summary is prose narrative, not actionable records
- Fix: Always produce: decisions (MEMORY.md), patterns (knowledge/), failures (archive/)
- Prevention: Use `/close-day` checklist—don't skip steps

## Quick Reference

### Session Startup Checklist
- [ ] MEMORY.md loaded (check context section)
- [ ] CLAUDE.md loaded
- [ ] next-session-prompt.md present? (resume + delete)
- [ ] Announce: "Memory loaded — ready to resume"

### Before Context Compression
- [ ] Scan conversation for decisions
- [ ] Write to `.claude/memory/` with proper type
- [ ] Commit before clearing
- [ ] Announce to user

### End of Day
- [ ] Extract decisions → MEMORY.md
- [ ] Extract patterns → knowledge/ or wiki/
- [ ] Log failures → archive/
- [ ] Write next-session-prompt.md (only if interrupted)
- [ ] Commit: `close-day: <summary> — YYYY-MM-DD`

### Memory File Types

| Type | Use For | Structure |
|------|---------|-----------|
| **user** | Role, preferences, knowledge | Lead with fact, **Why:** context |
| **feedback** | Corrections & validations | Rule/fact, **Why:** reason, **How to apply:** when |
| **project** | Active goals, deadlines, context | Fact, **Why:** motivation, **How to apply:** influence |
| **reference** | External resource pointers | Resource, **When:** context, **Value:** why it matters |

## Anti-Rationalization Guards

**Checkpointing is not optional.** If you think "I'll just remember this," you won't. If you think "It's a small decision," it still matters tomorrow. Checkpoint everything before context clears.

**Synthesis is not deferrable.** If you say "I'll write the summary later," it won't happen. End-of-session synthesis happens immediately, always.

**next-session-prompt.md must be deleted.** Write it only for interrupted work. Delete immediately after resuming. Don't let it accumulate.

## Setting It Up

1. **Create directory structure:**
   ```
   .claude/
     memory/
       MEMORY.md
       archive/
     hooks/
       session-start.py
       context-checkpoint.py
   ```

2. **Create `.claude/hooks/session-start.py`:**
   ```python
   #!/usr/bin/env python3
   import sys, os

   memory_file = ".claude/memory/MEMORY.md"
   claude_file = "CLAUDE.md"
   next_session = ".claude/memory/next-session-prompt.md"

   print("=== Memory Loaded ===")
   if os.path.exists(memory_file):
       with open(memory_file) as f:
           print(f.read()[:500] + "...\n")

   if os.path.exists(claude_file):
       print(f"✓ CLAUDE.md loaded")

   if os.path.exists(next_session):
       print(f"⚠ next-session-prompt.md found — resuming interrupted work")
       with open(next_session) as f:
           print(f.read())
   ```

3. **Register in the plugin's hooks.json:**
   ```json
   {
     "event": "UserPromptSubmit",
     "command": "python .claude/hooks/session-start.py 2>/dev/null || true"
   }
   ```

4. **Create initial MEMORY.md:**
   ```markdown
   ---
   last-updated: 2026-04-21
   session-count: 1
   ---

   # Memory Index

   (empty on first session)
   ```

5. **Commit:**
   ```
   git add .claude/ && git commit -m "boot: persistent memory system initialized"
   ```
