---
name: context-fundamentals
description: Use when designing agent systems, optimizing context windows, or architecting how information is loaded and positioned for LLM attention
---

# Context Engineering Fundamentals

## Overview

Context engineering treats the LLM's attention budget as a **finite, precious resource**—not a storage bin. Every token competes for model focus. The engineering challenge is not "what can fit" but "what maximizes utility per token."

**Core principle:** Effective capacity is 60-70% of advertised window size. The U-shaped attention curve means the beginning and end of context receive disproportionate focus. Position information strategically.

## When to Use

**Triggers:**
- Designing system prompts or context structures
- Optimizing token allocation across tools, history, and documents
- Troubleshooting agent performance (lost constraints, missed context)
- Building agent pipelines where context needs to scale
- Evaluating whether nominal window size equals usable capacity

**When NOT to use:**
- Simple, single-shot queries (use native Claude)
- Tasks with minimal context needs
- Prototyping with small datasets (scale later)

## Four Operating Principles

### 1. Prioritize Signal Over Completeness

**Not:** "Include everything that could matter"
**Instead:** "What would the model fail without?"

Completeness is the enemy of clarity. Every irrelevant token competes with critical information.

### 2. Place Critical Constraints at Attention Peaks

The U-shaped attention curve means:
- **Beginning:** Highest attention—put system constraints, critical rules
- **Middle:** Degraded attention—documents, tool definitions, history
- **End:** High attention again—current task, immediate context, user request

Constraints buried in the middle get ignored.

### 3. Load Content Progressively

**Not:** "Load all knowledge at startup"
**Instead:** "Load just-in-time as tasks reveal what's needed"

Upfront loading bloats context. Use:
- Tool calls to retrieve documents on-demand
- Conditional context based on task type
- Lazy loading for rare edge cases

The wiki's retrieval primitives table in `/llm-wiki:llm-wiki` is a concrete implementation of this principle—escalate from index.md → summary fields → grep → full page read, not the other way around.

### 4. Continuously Refine Context as Tasks Evolve

Context that's optimal for planning is inefficient for execution. Update system prompts, compress intermediate results, and adjust tool definitions as tasks progress.

## Practical Architecture

### System Prompt Organization

Structure in this order:
1. **Identity + Core Constraints** (non-negotiable rules)
2. **Task Description** (what the agent does)
3. **Key Definitions** (terminology, concepts)
4. **Interaction Style** (voice, tone, format)
5. **Tool Usage Patterns** (when/how to use available tools)

Keep under 2,000 tokens. Treat as constants, not narrative.

### Tool Definition Efficiency

**Gotcha:** Tool schemas serialize with padding. A 100-line schema can consume 300 tokens after JSON serialization.

**Fix:**
- Use concise descriptions (1-2 sentences max)
- Parameter examples beat prose explanations
- Remove unused parameters
- Group related tools into categories to reduce schema duplication

### Document Retrieval Strategy

For large document sets:
- Load metadata + summaries upfront (structured, scannable)
- Retrieve full documents only when selected
- Compress retrieved content to critical sections
- Use semantic search, not exhaustive retrieval

### Message History Management

Long-running agents accumulate history bloat. Solutions:
- **Sliding window:** Keep last N turns + compress older turns
- **Summarization:** Periodically collapse history into structured summaries
- **Sampling:** Preserve early constraint-setting turns, sample middle history
- **Invalidation:** Mark outdated decisions rather than deleting (for reasoning chains)

For the specific compression methods (anchored iterative, opaque, regenerative) and quality probes, see `/llm-wiki:context-compression`.

### Tool Output Compression

Tool outputs consume 30-50% of agentic context. Compress immediately:
- Extract structured results; discard explanatory prose
- Summarize logs to error signatures only
- Keep file paths, function names, error codes; drop stack traces
- For search results: title + rank only, fetch full results on demand

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| **Token counting errors** | Context fits in math but fails in practice | Use Claude's token counter; assume 25-30% overhead for serialization |
| **Critical constraints in system prompt tail** | Agent ignores rules stated late | Move constraints to beginning; repeat at context end |
| **Tool schema bloat** | Context exhausted before reaching task | Audit schemas; remove padding; use parameter examples |
| **All-upfront loading** | Context full before agent starts work | Switch to progressive/just-in-time loading |
| **No artifact tracking** | Agent loses which files were modified | Add explicit "Files Modified" section to summaries |
| **Opaque compression** | Can't debug what was lost | Use anchored summarization with explicit sections |
| **Ignoring position bias** | Middle context gets skipped | Test with varied position; move critical info to peaks |

## Context Audit Checklist

Before deploying an agent:

- [ ] System prompt is under 2,000 tokens
- [ ] Critical constraints appear in first 200 and last 200 tokens
- [ ] Tool schemas are minimal (< 50 tokens each)
- [ ] Message history has a compression strategy
- [ ] Tool outputs are compressed immediately
- [ ] Effective window capacity estimated at 60-70% of nominal
- [ ] Document retrieval is on-demand, not upfront
- [ ] Position bias tested (constraints moved to verify impact)

## References

- `/llm-wiki:context-compression` — Compression methods for long-running wiki sessions: anchored iterative, opaque, regenerative, with artifact tracking and quality probes
- `/llm-wiki:persistent-memory-management` — Cross-session knowledge and checkpointing before context clears
