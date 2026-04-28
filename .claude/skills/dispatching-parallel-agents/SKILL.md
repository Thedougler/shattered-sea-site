---
name: dispatching-parallel-agents
description: Use when facing 2+ independent wiki tasks that can be worked on without shared state or sequential dependencies — batch page updates, parallel queries, independent frontmatter repairs across subsystems
---

# Dispatching Parallel Agents

> Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT License) — modified for LLM Wiki vault operations.

## Overview

You delegate tasks to specialized subagents with isolated context. By precisely crafting their instructions, you ensure they stay focused and succeed. They should never inherit your full session context — construct exactly what they need.

**Core principle:** Dispatch one agent per independent problem domain. Let them work concurrently.

**Critical constraint:** Each dispatched agent must still process its assigned files **one at a time to completion** — read, understand, write, verify each file before moving to the next. Parallel dispatch is about giving independent domains to different agents, not about batch-writing within a single agent. See CLAUDE.md § Vault Integrity.

## When to Use

**Use when:**
- 3+ pages need independent updates (different entities, different subsystems)
- Multiple health check issues in unrelated vault areas
- Batch NPC/location/item creation (each page independent)
- Multiple `/query` operations on unrelated topics
- Frontmatter repairs across different entity types

**Don't use when:**
- Updates are related (fixing one might fix others — e.g., reciprocal wikilinks)
- Need to understand full vault state before acting
- Agents would edit the same files (e.g., both updating `content/index.md`)
- Operations must be sequential (ingest → lint → commit)

## The Pattern

### 1. Identify Independent Domains

Group tasks by what's independent:
- NPC pages: Active Problem updates for 3 different NPCs
- Location pages: New wikilinks for 2 locations
- Frontmatter: Fix `source_count` on 4 entity pages

Each domain is independent — updating one NPC doesn't affect another.

### 2. Create Focused Agent Tasks

Each agent gets:
- **Specific scope:** One page, one subsystem, or one entity type
- **Clear goal:** What to create, update, or fix
- **Constraints:** Don't modify other pages, check index before creating
- **Context:** Relevant template, existing page content, canon references
- **Expected output:** Summary of what was created/changed

### 3. Dispatch in Parallel

```
Agent 1 → Update Active Problem for Captain Draven
Agent 2 → Update Active Problem for Mariselle
Agent 3 → Create new location page for The Coral Spire
```

### 4. Review and Integrate

When agents return:
- Read each summary
- Verify no conflicting changes (e.g., contradictory wikilinks)
- Run `python .claude/bin/wiki_guard.py --lint-agent` on all changed pages
- Verify `content/index.md` is consistent
- Git commit all changes together: `git add content/ && git commit -m "update: <summary>"`

## Agent Prompt Structure

Good agent prompts are:
1. **Focused** — one clear problem domain
2. **Self-contained** — all context needed to understand the task
3. **Specific about output** — what should the agent return?

### Example: Batch NPC Update

```markdown
Update the active_problem frontmatter field for Captain Draven.

Current page content:
[paste current page]

New active_problem: "The Tessarine Concordat is pressuring him to reveal
the smuggling routes he used during the war."

Your task:
1. Read the current page
2. Replace the active_problem in frontmatter
3. Update the `updated` frontmatter field to today's date
4. Do NOT modify any other fields or content
5. Do NOT create new wikilinks to pages that don't exist

Return: The exact text replacement (oldString → newString)
```

### Example: Batch Page Creation

```markdown
Create a new deity page for Procan using the deity template.

Template structure:
[paste the deity template]

Facts from canon:
- Domain: Seas, Sea Life, Salt
- Alignment: Chaotic Neutral
- Mentioned in: Session 3 source

Vault index for wikilink validation (check ONLY against these slugs):
[paste relevant lines from content/index.md]

Your task:
1. Follow the template exactly
2. Use frontmatter: type: deity, campaign: "shattered-sea"
3. Create wikilinks ONLY to slugs present in the index excerpt above
4. Do NOT invent lore not in the provided facts

Return: Complete page content ready to write to vault
```

## Common Mistakes

**❌ Too broad:** "Update all NPCs" — agent gets lost
**✅ Specific:** "Update Captain Draven's Active Problem" — focused scope

**❌ No context:** "Fix the wikilinks" — agent doesn't know which
**✅ Context:** Paste the page content and the validation error

**❌ No constraints:** Agent might restructure the entire page
**✅ Constraints:** "Do NOT modify other fields", "ONLY update Active Problem"

**❌ Shared state:** Two agents both updating `content/index.md`
**✅ Independent:** Each agent updates a different entity page; YOU update index after

**❌ Fabricated index:** "Link to related pages you think exist"
**✅ Grounded index:** Paste the relevant section of `content/index.md` so agents only link to real slugs

## Verification After Integration

After all agents return:
1. **Review each result** — does it match the task?
2. **Check for conflicts** — did any agent touch shared state?
3. **Run lint** — `python .claude/bin/wiki_guard.py --lint-agent`
4. **Verify wikilinks** — no broken links introduced
5. **Update index** — add any new pages to `content/index.md`
6. **Commit** — `git add content/ && git commit -m "update: <summary of parallel changes>"`

## Key Rule

**Never let parallel agents edit the same file.** If two tasks need to modify `content/index.md`, YOU do the index update after both agents return. Agents only touch their assigned pages.

---

## Tooling Friction → `wiki-tooling-fixer` Agent

Any time you hit friction with the wiki tooling during a session — before retrying with a
guess or working around the issue — dispatch the `wiki-tooling-fixer` subagent. It runs
independently of wiki content work and can be dispatched in parallel with content agents.

### Trigger conditions

Dispatch `wiki-tooling-fixer` when any of these occur:

- A `wiki_guard.py` command exits with an error or unexpected output
- A CLI flag or subcommand you expected doesn't exist (`error: unrecognized arguments`)
- A command works but produces wrong results (wrong files, wrong counts, missing output)
- You had to retry an action because the first attempt used a wrong command form
- Documentation in a rule or skill led you to run a command that didn't work
- A tool assumption (e.g., a flag name, a default behavior) turned out to be wrong

### What to pass

```markdown
**Friction description:** [what failed and what you expected instead]
**Exact command tried:** python .claude/bin/wiki_guard.py --lint-agent
**Exact output/error:** [full error message or wrong output]
**Context:** [which skill or operation was running — e.g., "post-ingest lint step"]
**Files involved:** [optional — e.g., ".claude/bin/wiki_guard_lib/linting.py"]
```

### Integration rules

- `wiki-tooling-fixer` never touches wiki content pages, `content/index.md`, or `content/hot.md`
- It commits its own fix before returning — its changes are self-contained
- You do not need to re-validate or re-commit after it returns
- If it finds the command was correct but used wrong, it returns the correct form — apply it
  and continue without any file changes
- Safe to dispatch in parallel with content agents IF the friction is in a different subsystem
  than what the content agent is writing to
