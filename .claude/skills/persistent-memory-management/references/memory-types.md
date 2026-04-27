---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
<!-- GENERATED FILE - DO NOT EDIT DIRECTLY. Edit wiki/system/agent-runtime/canon. -->
---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
# Memory Types Reference

## User Memories

**Trigger:** Learn details about the user's role, preferences, responsibilities, or knowledge.

**When to save:**
- User's role or title changes
- Preferences about how you should work
- Knowledge domain or expertise level
- Working style or communication preference

**Structure:**
```markdown
---
name: {{user-aspect}}
description: {{one-line description}}
type: user
---

{{Fact about user}}
```

**Example:**
```markdown
---
name: user-backend-specialist
description: Senior Go engineer, new to React and this project's frontend
type: user
---

User has 10+ years Go experience but this is first React project. Frame frontend
explanations in terms of backend analogues (goroutines → async/await, interfaces →
TypeScript protocols, etc.). User prefers seeing architecture diagrams before diving
into component details.
```

## Feedback Memories

**Trigger:** User corrects an approach OR confirms a non-obvious approach worked.

**When to save:**
- "Don't do X" (correction)
- "Keep doing Y" (validation)
- "This approach failed because Z" (historical context)
- User accepts unusual choice without pushback (implicit validation)

**Structure:**
```markdown
---
name: {{feedback-topic}}
description: {{What was corrected/validated}}
type: feedback
---

**Rule:** {{The behavior to change}}

**Why:** {{Reason — incident, constraint, or strong preference}}

**How to apply:** {{When/where this kicks in; when to make exceptions}}
```

**Example:**
```markdown
---
name: feedback-database-mocks
description: Integration tests must hit real DB, not mocks
type: feedback
---

**Rule:** Never mock the database in integration tests.

**Why:** Last quarter, mocked tests passed but the prod migration failed. The mock
diverged from actual schema, masking a breaking change. Mocking hides real failures.

**How to apply:** Integration tests must use a real database instance (Docker container,
test fixture). Unit tests can mock; integration tests cannot.
```

## Project Memories

**Trigger:** Learn who is doing what, why, or by when. Active goals, blockers, deadlines.

**When to save:**
- Feature deadline or launch date
- Stakeholder ask or priority shift
- Active incident or critical path blocker
- Architecture decision with timeline
- Organizational constraint

**Convert relative dates to absolute:** "Thursday" → "2026-03-05"

**Structure:**
```markdown
---
name: {{project-decision}}
description: {{What decision or state, why it matters}}
type: project
---

**Fact:** {{The decision/state/goal}}

**Why:** {{Motivation — deadline, constraint, stakeholder ask}}

**How to apply:** {{How this shapes priorities/suggestions}}
```

**Example:**
```markdown
---
name: project-mobile-release-freeze
description: Merge freeze begins 2026-03-05 for mobile release cut
type: project
---

**Fact:** All non-critical merges frozen starting 2026-03-05. Mobile team is cutting
release branch; any non-critical PR that lands during freeze risks breaking the build.

**Why:** Mobile release cycle requires stability window. Non-critical merges destabilize
the branch.

**How to apply:** Flag any non-critical PR work scheduled after 2026-03-05 as
post-release. Prioritize critical fixes only.
```

## Reference Memories

**Trigger:** Learn about resources in external systems — where to find information.

**When to save:**
- External service or tool location (Grafana board, Linear project, Slack channel)
- Documentation that changes often
- Third-party system that's the source of truth
- Configuration or credential location

**Structure:**
```markdown
---
name: {{reference-name}}
description: {{What resource, what purpose}}
type: reference
---

**Location:** {{Where to find it}}

**When to check:** {{Context for when this resource is relevant}}

**Value:** {{Why it matters}}
```

**Example:**
```markdown
---
name: reference-oncall-dashboard
description: Grafana dashboard for oncall latency monitoring
type: reference
---

**Location:** grafana.internal/d/api-latency

**When to check:** Before/after any request-path code changes; if paging starts after
your changes, check this first.

**Value:** Oncall watches this board. High latency here triggers pages. It's your
feedback signal that your change broke something.
```

## What NOT to Save

- Code patterns, conventions, architecture (derive from current code)
- Git history or who-changed-what (`git log` is authoritative)
- Debugging solutions or fix recipes (the code is the record)
- Project structure or file paths (read current structure)
- Anything already in CLAUDE.md (no duplication)
- Ephemeral state (conversation context, in-progress work, temp files)
