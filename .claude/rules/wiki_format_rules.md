---
paths:
  - wiki/**
description: Formatting standards — active when writing or editing wiki entity pages
---

# Wiki Entity Page Format

Every page in wiki/ must strictly follow this structure. This rule set aligns with Obsidian Markdown
and Obsidian Bases best practices for maximum queryability and reusability.

---

## File Naming

**ALL wiki filenames use kebab-case (hyphen-separated), no spaces or underscores, .md extension.**

- ✅ Correct: `Beaumont-Sel.md`, `Fisks-Fleet.md`, `Iron-Coast.md`
- ❌ Incorrect: `beaumont_sel.md`, `BeaumontSel.md`, `beaumont sel.md`

Wikilinks match filenames exactly (case-sensitive on some systems). Use `[[Beaumont-Sel]]` to link.

---

## Required YAML Frontmatter

Must appear at the very top of every page. All fields required. Use kebab-case for keys.
Wikilinks in YAML must be quoted (`"[[Page]]"`). Dates use ISO format `YYYY-MM-DD`.

```yaml
---
type: entity
title: "Display Name"
campaign: shattered-sea
created: 2026-04-08
updated: 2026-04-26
tags:
  - tag-name
  - another-tag
status: active
sources:
  - "[[Source-Page]]"
related:
  - "[[Related-Entity]]"
---
```

### Field Reference

| Field | Type | Required | Values | Notes |
|-------|------|----------|--------|-------|
| `type` | enum | ✅ | `concept`, `entity`, `location`, `npc`, `faction`, `item`, `encounter`, `other` | Determines directory category |
| `title` | string | ✅ | Any | Display name in Properties panel |
| `campaign` | string | ✅ | `shattered-sea` (or other campaign slug) | Filters for campaign-scoped bases |
| `created` | date | ✅ | `YYYY-MM-DD` | Page creation date |
| `updated` | date | ✅ | `YYYY-MM-DD` | Last modification date |
| `status` | enum | ✅ | `draft`, `active`, `verified`, `contradictory` | Queryable in bases; gates content generation |
| `tags` | list | ✅ | kebab-case strings, minimum 2 | Thematic tags for search and filtering |
| `sources` | list | ✅ | `"[[Page]]"` wikilinks (quoted) | Which raw/ or wiki/ pages informed this entity |
| `related` | list | ✅ | `"[[Page]]"` wikilinks (quoted) | Directly connected entities (reciprocal) |
| `reveal_status` | enum | ❌ | `unrevealed`, `foreshadowed`, `revealed` | Plot protection; gates what content is readable |

**YAML rules:**
- Flat only. Never nest objects — use list format for multiple values.
- Wikilinks must be quoted in YAML: `sources: - "[[Page]]"` ✅ | `sources: - [[Page]]` ❌
- Dates as `YYYY-MM-DD` only; never use ISO 8601 timestamps like `2026-04-08T00:00:00Z`
- Lists always use `-` format, never inline `[item1, item2]`

### Monster Page Exception

Monster entries use a dedicated schema instead of the generic entity schema above. Match the inline,
single-note pattern used by the canonical examples in `raw/monsters/`.

```yaml
---
type: entity
subtype: monster
cr: 10
creature_type: aberration
environment: underdark, underwater
str: 21
dex: 9
con: 15
int: 18
wis: 15
cha: 18
status: bestiary
confidence_level: high
sources: XMM
page: 12
tags:
  - creature
  - aberration
  - xmm
created: '2026-04-26'
updated: '2026-04-26'
cssclasses:
  - wiki-monster
statblock: inline
source_count: 1
---
```

### Monster Field Reference

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | string | ✅ | Always `entity` |
| `subtype` | string | ✅ | Always `monster` |
| `cr` | number or string | ✅ | Use the display CR form shown in the source, e.g. `15` or `1/2` |
| `creature_type` | string | ✅ | Canonical 5e creature type, lowercase |
| `environment` | string | ✅ | Comma-separated habitats from source; leave blank if unspecified |
| `str` | integer | ✅ | Ability score |
| `dex` | integer | ✅ | Ability score |
| `con` | integer | ✅ | Ability score |
| `int` | integer | ✅ | Ability score |
| `wis` | integer | ✅ | Ability score |
| `cha` | integer | ✅ | Ability score |
| `status` | string | ✅ | Always `bestiary` for published monster entries |
| `confidence_level` | string | ✅ | Usually `high` when transcribed directly from source |
| `sources` | string | ✅ | Source-book code, not a wikilink list |
| `page` | integer | ✅ | Printed page number from the source |
| `tags` | list | ✅ | Always include `creature`, the creature type, and the lowercased source code |
| `created` | string | ✅ | Quote the date exactly as `'YYYY-MM-DD'` |
| `updated` | string | ✅ | Quote the date exactly as `'YYYY-MM-DD'` |
| `cssclasses` | list | ✅ | Include `wiki-monster` |
| `statblock` | string | ✅ | Always `inline` |
| `source_count` | integer | ✅ | Count of distinct source books represented in the note |

### Monster YAML Rules

- Keep monster YAML flat and mechanical. Do not add `title`, `campaign`, `related`, or `reveal_status` unless a downstream workflow explicitly requires them.
- Use lowercase snake_case YAML keys for monster metadata such as `creature_type`, `confidence_level`, and `source_count`.
- Keep ability scores duplicated in frontmatter and in the statblock `stats` array. Frontmatter supports querying; the codeblock supports rendering.
- Use a plain source code in `sources` such as `XPHB`, `XMM`, `MCV1SC`, or `GGR`, not a wikilink.
- Keep `environment:` present even when empty so the schema stays consistent across entries.

### NPC Page Exception

NPC entries use an extended profile schema and a performable page body. Match the pattern used by the
canonical examples in `raw/npcs/`.

```yaml
---
type: entity
subtype: npc
status: active
created: '2026-04-26'
updated: '2026-04-26'
tags:
  - npc
  - faction-tag
  - location-tag
sources:
  - Homebrew
source_count: 1
confidence_level: medium
appearance: One-sentence visual first impression.
campaign: shattered-sea
player_gravity: 3
gravity_sources:
  Player-Name: 3
active_problem: Current actionable pressure.
primary_goal: What this NPC wants right now.
consistent_method: Repeatable table behavior pattern.
performance_hooks: 1-3 memorable DM cues.
link_of_relevance: "[[PC-Or-Anchor]] — why this NPC matters in play."
faction: "[[Faction-Name]]"
location: "[[Location-Name]]"
species: Species-or-wikilink
role: in-world role title
disposition: friendly
roleplay_prompt: Pop-culture mashup performance seed.
portrait: raw/assets/portraits/NPC-Name.webp
banner: raw/assets/banners/NPC-Name.webp
cssclasses:
  - wiki-npc
---
```

### NPC Field Reference

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | string | ✅ | Always `entity` |
| `subtype` | string | ✅ | Always `npc` |
| `status` | string | ✅ | Use campaign-facing states such as `unmet`, `active`, `retired`, `dead` |
| `created` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `updated` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `tags` | list | ✅ | Include `npc` plus origin/faction/location identity tags |
| `sources` | list | ✅ | May use plain source labels (for example `Homebrew`) or wikilinks |
| `source_count` | integer | ✅ | Count of distinct source items |
| `confidence_level` | string | ✅ | `low`, `medium`, or `high` |
| `appearance` | string | ✅ | One sentence, visual and table-usable |
| `campaign` | string | ✅ | Usually `shattered-sea` |
| `player_gravity` | number | ✅ | Aggregate pull across current PCs |
| `gravity_sources` | mapping | ✅ | Per-PC gravity weights |
| `active_problem` | string | ✅ | Immediate conflict currently in motion |
| `primary_goal` | string | ✅ | What the NPC is trying to achieve now |
| `consistent_method` | string | ✅ | Repeatable behavior gimmick the GM can perform quickly |
| `performance_hooks` | string | ✅ | Distinct performance cues for voice/behavior |
| `link_of_relevance` | string | ✅ | Linked anchor to a PC or key campaign thread |
| `faction` | string | ✅ | Primary faction wikilink |
| `location` | string | ✅ | Current operating location wikilink |
| `species` | string | ✅ | Species label or species wikilink |
| `role` | string | ✅ | Functional role in the world |
| `disposition` | string | ✅ | Table-ready stance: `friendly`, `neutral`, `hostile`, etc. |
| `roleplay_prompt` | string | ✅ | Fast roleplay seed in one line |
| `portrait` | string | ❌ | Raw asset path when art exists |
| `banner` | string | ❌ | Raw asset path when art exists |
| `cssclasses` | list | ✅ | Include `wiki-npc` |
| `public` | boolean | ❌ | Visibility flag for player-facing views |
| `reveal_status` | enum | ❌ | `unrevealed`, `foreshadowed`, `revealed` |

### NPC YAML Rules

- Keep toy fields in frontmatter for queryability: `active_problem`, `primary_goal`, `consistent_method`, `performance_hooks`, `link_of_relevance`.
- Keep `gravity_sources` as a YAML mapping keyed by PC name.
- Use quoted wikilinks for identity anchors in scalar fields such as `faction`, `location`, and `link_of_relevance`.
- Keep `appearance` concise and visual; no hidden lore or plot twists in that field.
- Keep `roleplay_prompt` short and performable (for example, `Owl Obi-Wan Kenobi`).

### Ship Page Exception

Ship entries use an operational profile schema and a deck-usable body layout. Match the pattern used by
canonical examples in `raw/ships/`.

```yaml
---
type: entity
subtype: ship
status: active
created: '2026-04-26'
updated: '2026-04-26'
tags:
  - ship
  - tier-1
  - role-tag
sources:
  - Homebrew
source_count: 1
confidence_level: medium
campaign: shattered-sea
tier: 1
ship_class: sloop
home_port: "[[Port-Tidefall]]"
captain: "[[Captain-Name]]"
current_location: Current dock, route, or wreck position
banner: raw/assets/banners/Ship-Name.webp
cssclasses:
  - wiki-ship
---
```

### Ship Field Reference

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | string | ✅ | Always `entity` |
| `subtype` | string | ✅ | Always `ship` |
| `status` | string | ✅ | Use vessel lifecycle states such as `active`, `unmet`, `impounded`, `destroyed` |
| `created` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `updated` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `tags` | list | ✅ | Include `ship` and vessel identity tags (tier, condition, fleet, role) |
| `sources` | list | ✅ | Usually `Homebrew` or source wikilinks |
| `source_count` | integer | ✅ | Count of distinct source items |
| `confidence_level` | string | ✅ | `low`, `medium`, or `high` |
| `campaign` | string | ✅ | Usually `shattered-sea` |
| `tier` | number | ✅ | Ship mechanical tier |
| `ship_class` | string | ✅ | Hull and rig class description |
| `current_location` | string | ✅ | Present-day dock, route, region, or wreck position |
| `captain` | string | ❌ | Wikilink to current or final captain |
| `home_port` | string | ❌ | Wikilink to regular port base |
| `player_gravity` | number | ❌ | Aggregate pull across PCs |
| `gravity_sources` | mapping | ❌ | Per-PC gravity values |
| `banner` | string | ❌ | Raw asset path when art exists |
| `cssclasses` | list | ✅ | Include `wiki-ship` |

### Ship YAML Rules

- Prefer operational facts over prose in frontmatter: classification, status, tier, location, captain/home port.
- Keep `current_location` explicit enough for encounter staging (dock, impound, region edge, wreck shelf).
- Use quoted wikilinks for captain and port identity anchors where applicable.
- Use tags to encode mechanical and narrative affordances (`tier-1`, `impounded`, `wreck`, `fleet`, etc.).
- Keep status and section content synchronized (for example, an `impounded` ship should have Acquisition or release notes).

### Condition Page Exception

Condition entries use a compact rules schema optimized for quick in-session lookup. Match the pattern used by
canonical examples in `raw/conditions/`.

```yaml
---
type: entity
subtype: condition
status: active
created: '2026-04-26'
updated: '2026-04-26'
tags:
  - rule
  - condition
sources:
  - raw/ingested/Condition-Name.md
source_count: 1
confidence_level: medium
---
```

### Condition Field Reference

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | string | ✅ | Always `entity` |
| `subtype` | string | ✅ | Always `condition` |
| `status` | string | ✅ | Usually `active` |
| `created` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `updated` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `tags` | list | ✅ | Include both `rule` and `condition` |
| `sources` | list | ✅ | Usually one raw ingest source path |
| `source_count` | integer | ✅ | Distinct source count |
| `confidence_level` | string | ✅ | `low`, `medium`, or `high` |

### Condition YAML Rules

- Keep condition frontmatter minimal and mechanical.
- Use source path entries in `sources` when transcribing direct rules text.
- Avoid narrative identity fields (`faction`, `location`, `appearance`, etc.) on condition pages.
- Keep one note per condition name.

### Class Page Exception

Class entries are reference concepts, not in-world entities. Match the pattern used by canonical
examples in `raw/class/`.

```yaml
---
type: concept
subtype: class
status: active
created: '2026-04-26'
updated: '2026-04-26'
tags:
  - reference
  - class
  - class-name
  - 2024-phb
sources:
  - Player's Handbook (2024)
source_count: 1
confidence_level: medium
cssclasses:
  - wiki-reference
---
```

### Class Field Reference

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | string | ✅ | Always `concept` for class references |
| `subtype` | string | ✅ | Always `class` |
| `status` | string | ✅ | Usually `active` |
| `created` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `updated` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `tags` | list | ✅ | Include `reference`, `class`, class slug tag, and source-era tag |
| `sources` | list | ✅ | Source-book attribution, usually `Player's Handbook (2024)` |
| `source_count` | integer | ✅ | Distinct source count |
| `confidence_level` | string | ✅ | `low`, `medium`, or `high` |
| `cssclasses` | list | ✅ | Include `wiki-reference` |

### Class YAML Rules

- Keep class pages under `type: concept` with `subtype: class`.
- Keep source metadata explicit in frontmatter (`sources`, `source_count`).
- Use class-specific tags for queryability (for example `bard`, `ranger`).
- Do not add narrative toy fields (`active_problem`, `faction`, etc.) to class reference pages.

### Rule Page Exception

Rules entries are reference concepts that summarize mechanics and campaign adaptations. Match the pattern
used by canonical examples in `raw/rules/`.

```yaml
---
type: concept
subtype: rule
status: active
created: '2026-04-26'
updated: '2026-04-26'
tags:
  - rule
  - reference
  - source-tag
sources:
  - Source Book (Year)
source_count: 1
confidence_level: medium
---
```

### Rule Field Reference

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | string | ✅ | Always `concept` for rules references |
| `subtype` | string | ✅ | Always `rule` |
| `status` | string | ✅ | Usually `active` |
| `created` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `updated` | string or date | ✅ | Use `YYYY-MM-DD`; quoting is acceptable |
| `tags` | list | ✅ | Include `rule`, `reference`, and source/domain tags |
| `sources` | list | ✅ | Rulebook and adaptation sources |
| `source_count` | integer | ✅ | Distinct source count |
| `confidence_level` | string | ✅ | `low`, `medium`, or `high` |

### Rule YAML Rules

- Keep rules pages under `type: concept` with `subtype: rule`.
- Include every significant source in `sources` and keep `source_count` accurate.
- Use tags to signal source era and subsystem scope (for example `phb-2024`, `dmg-2024`, `bastion`).
- Keep frontmatter mechanical and bibliographic; do not include narrative entity fields.

---

## Page Body Structure

Use markdown headings (##, ###) to segment into semantic sections. Headings act as token
boundaries for the LLM — keep them concise and descriptive.

```markdown
## Overview
One dense paragraph defining the entity. No filler. State its role, nature, or significance.

## Details / Lore / Mechanics
Substantive content using sub-headings as needed (###). This is the main body.

## Relationships
Explicitly describe connections to other entities. Use `[[wiki-links]]` for bidirectional
references. Format: "[[Entity]] — brief relationship description."

## Sources
Bullet list of raw/ filenames that informed this page.

## Contradictions
Only if `status: contradictory`. Describe the specific conflict, which sources disagree,
and what ruling is needed from the GM.
```

---

## Wikilinks & Reciprocals

- **Syntax:** `[[Entity-Name]]` (matches filename exactly, case-sensitive, no extension)
- **Reciprocal rule:** If Page A links to Page B, Page B should link back to Page A (in Relationships section)
- **Every page must have ≥2 inbound links.** No orphans allowed.
- **Dead links:** If you link to a non-existent page, create a stub immediately with minimal frontmatter

---

## Content Patterns (DRY)

To avoid duplication, use the appropriate pattern for each use case:

### When to use each pattern

| Pattern | Syntax | Use when |
|---------|--------|----------|
| **Base embed** | `![[tracker.base]]` or `![[tracker.base#View Name]]` | Displaying a dynamic list, roster, or table of entities. Queries live frontmatter — updates automatically. |
| **Section embed** | `![[Entity-Name#Heading]]` | Pulling a specific section from another page inline; avoids copy-paste. |
| **Full embed** | `![[Entity-Name]]` | Embedding an entire page inline (rare — usually imprecise). |
| **Wikilink** | `[[Entity-Name]]` | Cross-referencing where reader clicks through to full page. |
| **Canvas embed** | `![[diagram.canvas]]` | Visual layout (mind map, flowchart, relationship diagram). |
| **Static text** | Plain markdown | Content unique to this page, not derivable from other entities' frontmatter. |

### Anti-patterns to avoid

❌ Static tables listing entity status — replace with base embeds (queryable, auto-updating)
❌ Paragraph descriptions of Entity B on Entity A's page — use section embed or one-sentence link
❌ Hand-maintained rosters or inventories — replace with bases
❌ Manual "Last Updated" dates — let file metadata handle this

---

## Callouts (D&D Wiki System)

Callouts render as styled alert boxes. Reference `obsidian-markdown` skill for full callout syntax.

### Play callouts (at-table use)

| Type | Use for |
|------|---------|
| `read-aloud` | GM performance text — arrivals, reveals, atmosphere |
| `appearance` | Physical description — what the party sees on first look |
| `secret` | Hidden info the party hasn't discovered |
| `skill-check` | Actionable DC: `**Skill DC N** — outcome on success/fail` |
| `mechanic` | Rules, conditions, phase triggers |

### Meta callouts (wiki maintenance)

| Type | Use for |
|------|---------|
| `contradiction` | Conflicting facts — requires GM ruling |

---

## Embedding & Bases

### Obsidian Bases (Canonical Infrastructure)

Bases are the primary query layer for wiki data. Every property in frontmatter becomes a filterable,
sortable column. Design properties for queryability:

- **Use consistent enum values** — status should always be `draft | active | verified | contradictory`
- **Use queryable property names** — avoid abbreviations (e.g., `last_seen` not `ls`)
- **Dates as ISO `YYYY-MM-DD`** — bases sorts them correctly
- **Avoid free-text fields** — prefer enums and lists
- **Link counts matter** — `sources` list length is often a quality signal

Bases are embedded with `![[MyBase.base]]` or `![[MyBase.base#View Name]]` for specific views.

---

## Linking & Reciprocals

**Golden rule:** Every outbound `[[link]]` should have a reciprocal inbound link on the target page.

Self-heal automates this, except:
- Plot-protected entities (`reveal_status: unrevealed | foreshadowed`) never create reciprocals to revealed entities
- This prevents leaking hidden info via the graph

---

## Monster Body Structure

Monster pages are intentionally minimal. Follow this order exactly:

```markdown
# Monster Name

```statblock
layout: Basic 5e Layout
name: "Monster Name"
size: Medium
type: beast
alignment: Unaligned
ac: 12
hp: 19
hit_dice: 3d8 + 6
speed: "30 ft., Climb 30 ft."
stats: [16, 14, 14, 6, 12, 7]
skillsaves:
  - athletics: 5
  - perception: 3
senses: "Passive Perception 13"
languages: "—"
cr: "1/2"
actions:
  - name: "Multiattack"
    desc: "The creature makes two attacks."
```
```

### Monster Statblock Rules

- The page title is a single H1 matching the statblock `name:` exactly.
- The first body element after the H1 is the `statblock` codeblock. Do not insert overview prose ahead of it.
- Always use `layout: Basic 5e Layout` unless the vault defines a different exact layout name.
- Quote display strings in the codeblock when they contain punctuation, fractions, em dashes, ranges, or comma-separated values.
- Always include the required core fields in this order: `layout`, `name`, `size`, `type`, `alignment`, `ac`, `hp`, `hit_dice`, `speed`, `stats`, optional defenses/saves/skills, `senses`, `languages`, `cr`.
- Add optional sections only when the creature has them in source material: `traits`, `actions`, `bonus_actions`, `reactions`, `legendary_actions`, `spells`.
- Preserve section names exactly. Use `legendary_actions`, not ad hoc headings or prose labels.
- Within list sections, every entry uses `name` plus `desc` only.
- If a monster has no languages, render `languages: "—"`.
- Use one note per monster. The vault default is an inline bestiary note, not a split lore note plus separate statblock file.

### Monster Section Patterns From Canonical Examples

- Baseline brute or beast: follow the `Ape` shape with only `skillsaves` and `actions`.
- Trait-heavy elite: follow the `Asteroid Spider` shape with `saves`, `skillsaves`, `traits`, `actions`, and `bonus_actions`.
- Legendary creature: follow the `Aboleth` shape with `traits`, `actions`, and `legendary_actions`.
- Legendary spellcaster: follow the `Niv-Mizzet` shape with defenses, `traits`, `actions`, `legendary_actions`, and `spells`.

---

## NPC Body Structure

NPC pages are performance-oriented reference sheets. Follow this order:

```markdown
# NPC Name

> [!read-aloud]
> 1-3 sentences of immediate table-facing introduction.

## Toy Chest

| Active Problem | Primary Goal | Consistent Method | Performance Hooks | Link of Relevance |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

```columns
id: unique-columns-id
===
<figure class="npc-portrait"><img src="relative/path.webp" alt="NPC Name" /></figure>

## Appearance
Short visual read.

## Voice & Delivery
- Performable bullet cues.

===
## Lore Sheet
Concrete, actionable lore blocks.
```

## Connections
- [[Linked-Entity]] — relationship note

## Stat Block
Optional, only if the NPC has mechanics here.

## Session Events
Log campaign-facing changes over time.
```

### NPC Body Rules

- Start with H1 and a `read-aloud` callout. Make it table-usable, not encyclopedic.
- Include the `## Toy Chest` table in the body and keep it aligned with the five toy fields in frontmatter.
- Use a `columns` block for high-signal presentation: portrait/voice on one side, lore or mechanics on the other.
- Include `## Connections` with linked anchors to factions, places, and key NPCs.
- Keep `## Session Events` even when empty (`None yet.`) so updates have a stable home.
- Treat `## Stat Block` as optional: include a full `statblock` codeblock only when this NPC needs combat mechanics in this note.

### NPC Variant Patterns From Canonical Examples

- Social/support NPC (`Félix Aho`): no statblock, strong voice/performance content, dense connection graph.
- Command NPC with mechanics (`Simone Tabarnack`): full Toy Chest plus integrated statblock and tactical unit notes.
- Mentor NPC (`Master Kyzil`): strong read-aloud and voice patterning, optional statblock placeholder, pilgrimage/event hooks.

---

## Ship Body Structure

Ship pages are tactical logistics references. Follow this order:

```markdown
# Ship Name

> [!read-aloud]
> 1-3 sentence visual pass from dock or deck level.

```columns
id: stable-columns-id
===
## Current State
Present operating condition.

## Overview
Hull profile, role, and readiness.

## History / Wreck / Current Notes
State-dependent narrative section.

===
## Stat Block
| | |
| --- | --- |
| **Type** | ... |
| **Tier** | ... |
| **Status** | ... |
| **Hull Points** | ... |
| **Hull AC** | ... |
| **Crew (min/full/max)** | ... |
| **Cargo** | ... |
| **Gun Mounts** | ... |
| **Weapons** | ... |
| **Upkeep** | ... |
```

## Layout
Deck-by-deck walkable structure.

## Bastion Notes / Acquisition / Crew
Include whichever are relevant to the ship's current state.

## Session Events
Chronological interaction log.

## Connections
- [[Linked-Entity]] — relationship note
```

### Ship Body Rules

- Start with H1 and a `read-aloud` callout using lowercase callout key (`read-aloud`).
- Use a two-column block with narrative state on one side and mechanical stat table on the other.
- Keep `## Stat Block` as a markdown table, not a prose paragraph.
- Include `## Layout` with deck-by-deck subsections when the vessel is explorable.
- Add state-appropriate logistics sections:
  - Operational ships: `Crew`, `Bastion Notes`
  - Impounded ships: `Acquisition`, legal release details
  - Destroyed ships: `The Wreck`, `Aftermath`
- Keep `## Session Events` even when empty.

### Ship Variant Patterns From Canonical Examples

- Destroyed flagship (`Red Lady`): rich wreck narrative, fleet context, soul or cargo consequences.
- Impounded acquisition target (`Lasting Insult`): purchase/legal release details, condition notes, hidden opportunities.

---

## Condition Body Structure

Condition pages are rules references first. Follow this order:

```markdown
# Condition Name

## Rule Text

While you have the Condition Name condition, you experience the following effects.

***Effect Header.*** Rule sentence.
***Effect Header.*** Rule sentence.

## Context

Optional brief implementation or campaign context note.
```

### Condition Body Rules

- Start with H1 named exactly after the condition.
- Use `## Rule Text` as canonical section heading for normalized condition pages.
- Lead Rule Text with the framing sentence `While you have the <Condition> condition, you experience the following effects.` unless the source format requires a different lead.
- Encode each effect as `***Header.***` followed by one concise rule sentence.
- Use `## Context` only when a clarification note is useful at your table. Omit for pure SRD mirrors.
- Keep prose terse and deterministic; no flavor text.

### Condition Variant Patterns From Canonical Examples

- Minimal mirror (`Blinded`): direct heading + effect bullets, no Context section.
- Normalized reference (`Grappled`, `Exhaustion`): `Rule Text` section plus optional `Context` section.

---

## Class Body Structure

Class pages are rules digests for fast table reference. Follow this order:

```markdown
# Class Name

*Class — Source Book (Year)*

**Primary Ability:** ... · **Hit Die:** ... · **Saves:** ... · **Armor:** ... · **Weapons:** ... · **Spellcasting:** ...

---

## Class Resource or Spell Slots
Key progression summary (text or table).

## Core Features
| Level | Feature |
| --- | --- |
| ... | ... |

## Subclasses
Subclass list with source scope.

## Connections
- [[Related-Page]] — relationship note
```

### Class Body Rules

- Start with H1 class name and an italic source line (`*Class — ...*`).
- Include a one-line mechanical profile using bold labels and middle-dot separators.
- Place a horizontal rule before major section breakdown.
- Use either a text progression section (for example class dice scaling) or a slot table section based on class needs.
- Keep `## Core Features` as a level-to-feature markdown table.
- Include `## Subclasses` and restrict to the source/version scope named at top.
- Include `## Connections` with at least one relevant link.

### Class Variant Patterns From Canonical Examples

- Bard-style: class resource progression section (`Bardic Inspiration Die`) plus concise spell-slot summary text.
- Ranger-style: explicit `Spell Slots by Level` table plus martial/ranger feature progression table.

---

## Rule Body Structure

Rules pages are concise mechanical references with optional campaign context.

```markdown
# Rule Name

## Rule Text

Plain-language mechanical summary.

### Subsection
Focused breakdown of one rule component.

| Table Header | Value |
| --- | --- |
| ... | ... |

## Context

Optional adaptation or interpretation notes for this campaign.

## Connections

- [[Related-Rule-Or-Entity]] — relationship note
```

### Rule Body Rules

- Start with H1 rule name.
- Use `## Rule Text` as canonical heading for the primary mechanics digest.
- Use short `###` subsections to segment complex systems.
- Prefer markdown tables for enumerations (categories, progression, facility lists, event tables).
- Include `## Context` when adaptation guidance or edition framing helps play.
- Include `## Connections` to adjacent rule notes or impacted entities.
- Keep prose deterministic and implementation-focused; avoid flavor-heavy narration.

### Rule Variant Patterns From Canonical Examples

- System-heavy rules (`Bastions`): multiple subsection tables plus campaign adaptation context.
- Category overview rules (`Feats`): definitions and grouped lists with minimal tabular depth.
- Core framework rules (`Species`): concise rule definitions with short context and targeted links.

---

## What NOT to Do

❌ Use `[link text](path/to/note.md)` for internal links — use `[[Note-Name]]` instead
❌ Write `tags: [a, b, c]` inline in YAML — use list format
❌ Use ISO timestamps in frontmatter — stick to `YYYY-MM-DD`
❌ Use `#` headings inside callout bodies — they don't render
❌ Link to pages that shouldn't exist as entities — create stubs instead
❌ Leave pages with fewer than 2 inbound links — lint will flag as orphans
❌ Use `snake_case` for filenames — always use `kebab-case`
