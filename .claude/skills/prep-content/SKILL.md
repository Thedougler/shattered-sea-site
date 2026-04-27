---
name: prep-content
description: >
  Universal skill for ALL D&D/TTRPG content prep using the Brennan Lee Mulligan framework.
  Covers NPCs, monsters, encounters, locations, factions, travel events, session prep, and
  any creative campaign content. Includes PC Gravity alignment, pop culture mashup roleplay
  method, and sandbox narrative mindset. Routes to prep-statblock for Fantasy Statblocks
  plugin YAML. Trigger on any mention of: prep, create, build, write, generate, make, design
  applied to any NPC, creature, place, faction, encounter, item, session, or campaign element.
  Also triggers on: /new-npc, /new-monster, /new-location, /new-faction, /new-encounter,
  /new-shop, /session-prep, /narrate, D&D, TTRPG, DM, GM, campaign, session, worldbuilding.
---

# prep-content

Build volatile situations players can't help but mess with. Never write stories — prep reactive systems and get out of the way.

> **Can run directly or via subagent.** When loaded directly, use `wiki-query` to gather canon context. When loaded by a `creative-dispatch` subagent, all context arrives in the Creative Brief.

---

## Core Philosophy

1. Prep situations, not scenes. Define pressures + timelines, not outcomes.
2. Every element acts on its own logic when players aren't watching.
3. Player characters are the center of mass. Everything else orbits them.
4. If you removed the players entirely and the world wouldn't change — you wrote a plot, not a sandbox.

---

## Universal Rules

These apply to ALL content types. Not repeated per section.

### Relevance Pre-Screen

Before generating anything: **which specific PC's backstory, goal, fear, or active thread does this directly touch?** Name the PC and the connection. If you cannot, do not generate — ask the GM for the PC link first. Content with no PC connection is wasted prep.

**Stakes first.** Lead with what a PC stands to gain or lose before writing lore, personality, or description.

### Interview Protocol

Ask all context questions in a single message. Do not generate until you have answers. If the Creative Brief or user message already answers the questions, skip the interview and generate immediately. Never ask more than one clarifying question if you have enough to produce good output.

### NEVER

- Invent canonical facts — check `wiki/index.md` before naming any entity
- Generate plot — generate pressures, goals, and timelines only
- Skip the PC link — no exceptions
- Pad output — no preamble, no `[!DM]` callouts, no commentary after. Output and stop
- Hook to an NPC the party hasn't met — wire through PC backstory instead
- Give a faction a goal the party can't observe
- Use fantasy name slop (Aerin, Vex, Theron, Kael, Lyra, Draven, Zara), decorative apostrophes, or swapped letters
- Write purple prose, character studies, or thematic analysis in wiki pages — Wiki Voice (see CLAUDE.md)
- Generate `[!DM]` callouts — use `[!read-aloud]`, `[!appearance]`, `[!secret]`, `[!skill-check]`, `[!mechanic]` per `dnd-callouts` skill
- Duplicate an existing entity — search `wiki/index.md` before creating
- Use pre-2024 rules for 5e content

### Reference Loading

Load the reference file **before** generating content that needs it. Do not load references you don't need.

| Reference | Load when | Path |
|---|---|---|
| Naming conventions | Naming any entity | `shared-references/naming-conventions.md` |
| Toy field guide | Writing toy frontmatter fields | `shared-references/toy-field-guide.md` |
| Mercer voice | Writing read-aloud prose | `shared-references/mercer-voice.md` |
| CR tables | Monster stat design | `references/cr-tables.md` |
| Battlefield actions | Solo Boss or Elite monsters | `shared-references/battlefield-actions.md` |
| Pacing heuristics | Session prep thread selection | `references/pacing-heuristics.md` |
| Strong Start types | Session prep | `references/strong-start-types.md` |
| Island template | Session prep | `references/island-template.md` |
| Stat block references | Encounter enemy citations | `references/stat-block-references.md` |
| Named enemies | Encounter with unique named antagonist | `references/named-enemies.md` |
| Universal toys | Campaign setup, Toy Chest, Session Zero, Clocks | `references/universal-toys.md` |

### Vault Filing

Use the appropriate template as the basis for new pages. File to the correct directory by type per CLAUDE.md § Directory Layout. For existing files, use `replace_string_in_file` — never delete and recreate. After writing:

```bash
wiki workflow contradict <slug>    # cross-page contradiction check (run after each page)
wiki workflow validate --fix       # self-heal: YAML + reciprocal wikilink repair
cd /Users/nick/vaults/dnd-wiki && git add wiki/ && git commit -m "new-<type>: <Name>"
wiki workflow log --append "new-<type>: <Name>"
```

`wiki/index.md` is auto-rebuilt by the pre-commit hook. See CLAUDE.md § Vault Tool Strategy, § Editing Rule, § Self-Sealing Writes.

**Toy fields live in YAML frontmatter and in an NPC body `## Toy Chest` table.** Keep both synchronized so Bases stay queryable and at-table scanning stays fast.

**`appearance` frontmatter field** — single-sentence evocative visual. Present on all in-world entity types. No plot, no drama.

---

## PC Gravity

Player characters generate narrative gravity. Every prep element must be wired to a PC's internal tensions.

### Gravity Well Extraction

For each PC, identify from their entity pages:

- **Two Dials** — two core behavioral axes defining their decision-making (e.g., family loyalty / reckless ambition). Must be *internal tensions*, not surface traits.
- **Terminal Node** — single deepest long-term desire. Asymptotic — the PC approaches but never cleanly arrives.
- **Active Friction** — what currently blocks them. This is where you place toys.

### The Gravity Filter

Every entity must pass: **does this pull on at least one PC's dials or terminal node?**

- Yes → include it, note which PC and how
- No → cut it, or retrofit a connection

### Anti-Patterns

| Bad Prep | Why It Fails |
|---|---|
| Content unconnected to PC wells | Players drift past it |
| Hooks requiring players to care about strangers | No internal gravity |
| All pulls in the same direction | Removes meaningful choice |
| Terminal Node treated as solvable | Kills the gravity well |
| Only one dial threatened | Half as interesting as both dials in opposition |

---

## Roleplay Method — Pop Culture Mashup

Every NPC and intelligent monster gets a **Roleplay Concept**: a mashup that loads voice and energy in one line.

**Formula:** `[unexpected animal/archetype/vibe] + [pop culture character/persona]`

Examples: *owl Obi-Wan Kenobi* · *rat grandma Scarface* · *southern golden retriever lawyer* · *burned-out vice principal Voldemort* · *yoga instructor who is also a hitman*

The mashup is the character's **operating system** — not look, not job, not backstory. Every choice flows from it. The two halves must create tension (warm AND territorial, menacing AND exhausted). If a line could belong to any character, rewrite it.

### Voice & Delivery Block

For every performed character, output:
- Speech patterns, vocabulary, verbal tics
- 2–3 actual lines the DM can say at the table
- Physical mannerisms (hands, eye contact, posture)
- Emotional default + what cracks it

### Performance Hooks

2–3 specific DM moves: when to lean into the bit, when to let the crack show, when to surprise. Write these as felt actions, not clinical instructions.

**Skip the mashup** for mindless beasts, constructs with no dialogue, or entities with no speaking role.

---

## Narrative Mindset

Narrative devices are tools for world-building, not plot control. Place loaded guns — players decide when they fire.

**Key devices to layer into prep:**
- **Chekhov's Gun** — seed elements with future weight; don't aim them
- **Foreshadowing** — hint at conditions and threats, not scripted events
- **Ticking Clock** — factions pursue goals on timelines; inaction has visible consequences
- **Reversal** — give NPCs/factions hidden layers that produce genuine surprise when revealed
- **The Iceberg** — build more world than players will see; depth makes the visible tip feel real
- **In Medias Res** — start scenes mid-action, not at the beginning

Apply after generating content: which devices are present? Which are missing? What would make this feel more alive?

---

## § NPC

**Interview (if needed):** Campaign/setting, race/species, role/function, PC link.

**Toy fields (5):** primary_goal, consistent_method, active_problem, performance_hooks, link_of_relevance.

**Name:** Derive from race/culture linguistic root. Load `naming-conventions.md`.

**Lore Sheet:** 2–4 sentences of concrete facts. Not a backstory — a dossier. Each sentence gives the DM something usable. No adjective piles, no dramatic commentary.

**Callouts:**
- `> [!read-aloud]` — 1–2 sentence first impression. Sensory, present tense, Mercer voice.
- `> [!appearance]` — build, colouring, bearing. One signature detail. 1–3 sentences.
- `> [!secret]` — only for genuinely hidden info. Omit if nothing is hidden.

**Sections:** Toy Chest → columns block (Appearance / Voice & Delivery / Lore Sheet) → Connections → Stat Block (optional) → Session Events.

**Toy Chest in body is required.** Render the five toy fields as a markdown table under `## Toy Chest`, even though the same values also live in frontmatter.

**Consistent Method = a gimmick, not a personality.** If the DM can't do it at the table in 5 seconds, rewrite it.

**Roleplay Concept is mandatory.** Always generate the mashup + Voice & Delivery block (see § Roleplay Method above). Insert as the first line of the character, above everything else.

**Columns block is canonical for NPC pages.** Use a `columns` codeblock with a stable `id`, and split presentation so visual/performance data is quickly skimmable during play.

**File to:** the appropriate entity directory per CLAUDE.md § Directory Layout

---

## § Monster

### The Four Laws

1. **One signature moment.** One thing no other monster does — what players describe after the session.
2. **Mechanics tell the story.** Every ability deducible from flavour. Can't explain it in one lore sentence? Cut it.
3. **Players are protagonists.** Design monsters that react to player choices.
4. **Complexity in decisions, not procedures.** Simple to run, rich to fight.

**Interview (if needed):** CR (or party level), role, one-sentence concept, culture/origin, environment, legendary?, lair?, party hook.

**Name:** Derive from cultural/geographic origin. Load `naming-conventions.md`.

### Roles & Stat Arrays

| Role | Priority Stats | Notes |
|---|---|---|
| Solo Boss | STR + CON primary | High across board; legendary actions, lair actions, multi-phase |
| Elite | High single-round damage | Crowd control, 1 legendary action set |
| Standard | Efficient multiattack | One interesting ability, clear weakness |
| Minion | Low HP, pack tactics | Single attack |
| Skirmisher | High speed, medium stats | Bonus action mobility |
| Controller | INT or WIS 18+ | Save DC is the weapon; lower AC acceptable |

### Ability Hierarchy

Build in order. Stop when you have enough.

1. **Tier 1 — Core Identity:** Multiattack (CR 2+) + the Signature Ability (one recharge/limited/save-or-suffer)
2. **Tier 2 — Combat Texture (1–2):** Passive trait, reaction, or bonus action that changes fight dynamics
3. **Tier 3 — Flavour (0–1):** Minor mechanical weight only. Skip if Tiers 1–2 aren't solid.

**Max 3 unique named abilities on a non-boss.** No save-or-die without repeat save and damage on success.

### CR Calculation

1. Defensive CR — effective HP in CR table (×1.5 for common resistance; ×2 for immunity to common type or B/P/S nonmagical)
2. Offensive CR — average damage per round across 3 rounds (÷3 for recharge 5–6; ÷2 for recharge 4–6)
3. Final CR = average of defensive and offensive CR
4. Adjust: +1 per 3 legendary actions; +1 for lair actions

Load `references/cr-tables.md` for full stat table, HP formulas, and damage expressions.

### Solo Boss — Legendary Suite

**Legendary Actions (3):** fast/reactive + pressure (terrain, minion, reveal) + 2-cost powerful.
**Lair Actions (3):** environmental + repositioning + dramatic.
**Legendary Resistance (3/Day):** include on any boss trivially ended by a single failed save.

### Multi-Phase

Max 2 phases (3 for campaign climax). Trigger at 50% HP. Phase 2 must feel *different* — new threat vector, not just stronger. Transition: describe dramatic change, list what stats change, initiative order not interrupted.

### Telegraphing

Include at least one: environmental traces, social NPC reaction, or mechanical preview (previous victim showing the signature ability's effect).

### Lore & Toy

- **Lore:** 2–3 sentences. What it is, what drives it, what makes it strange.
- **Toy fields (5):** Same as NPC — primary_goal, consistent_method, active_problem, performance_hooks, link_of_relevance.
- **Roleplay Concept:** mandatory for intelligent monsters. Skip for mindless beasts/constructs.

### Output

- Monster page with inline statblock — filed per CLAUDE.md § Directory Layout
- Use `prep-statblock` formatting rules for the embedded `statblock` codeblock
- Default to a single-note monster entry (frontmatter + H1 + inline statblock)

---

## § Encounter

### The 10-Field Toy

| Field | Content |
|---|---|
| **Primary Goal** | Thematic, not tactical — what this encounter proves |
| **Consistent Method** | Opposition behaviour and tactics — no editorializing after em dashes |
| **Active Problem** | Situation already in motion before party arrives — not enemy intent |
| **Performance Hooks** | One vibe reference + one tic for lead antagonist |
| **Link of Relevance** | Which PC's backstory/fear/goal — required |
| **Terrain Shift** | One specific, timed change mid-encounter |
| **Challenge Calibration** | Enemy count, stat block citations, action economy vs party (3–4 lines) |
| **Pressure Valve** | Targets party weakness — tension without unfairness |
| **Advantage Window** | Plays to party strength — lets them feel powerful if found |
| **Drama Suite** | DC table (10/15/20), Shenanigan offers, Box of Doom flags |

First 6 fields go in frontmatter when filing. Last 4 stay in page body.

### Encounter Type Router

1. **Social primary?** → Drama Suite is primary. Pressure Valve = social leverage. Challenge Calibration optional.
2. **Skill challenge (no initiative)?** → Replace Challenge Calibration with Skill Track: 3–5 skills, DC tiers, failure consequences.
3. **Ambush/chase?** → Terrain Shift fires round 1. Advantage Window = escape or reversal.
4. **Otherwise → standard combat.** Challenge Calibration + Pressure Valve + Advantage Window are primary.

### Scaling

| Level | Target Tone |
|---|---|
| 1–4 | Danger is real. Terrain Shift is a lifeline. |
| 5–8 | Party has power. Target action economy and concentration. |
| 9–12 | Moving parts. Multiple objectives. Non-combat solutions viable. |
| 13–16 | Consequences beyond the room. |
| 17–20 | Threaten things they love, not their HP. |

**File to:** the appropriate concepts directory per CLAUDE.md § Directory Layout

---

## § Location

**Interview (if needed):** Campaign context, PC connection, location type, cultural root.

**Name:** Derive from who built/inhabits the place. Load `naming-conventions.md`.

### Toy Fields (4)

| Field | Content |
|---|---|
| **verb** | What this location *does* — its active principle, even when untouched |
| **unstable_condition** | What's about to break, shift, or boil over |
| **consequence** | What happens if no one intervenes |
| **link_of_relevance** | Which PC's thread connects here |

### Read-Aloud

3–5 sentences, Mercer voice. Second-person present tense. Slow zoom: atmosphere → specific detail → trailing hook. Minimum three senses. No em dashes. End on something unresolved. Load `mercer-voice.md`.

Full Mercer for first impressions. Mercer-lite (2–3 sentences) for revisits or minor spaces.

### Key Rules

- Every room was built for a purpose — traces remain. No "empty" rooms.
- NPCs are `[[wikilinks]]` to existing pages — don't describe inline.
- Notable sub-locations get their own read-aloud + mini verb/condition/link.
- Don't describe a location by its history first — PCs experience places through senses.

**Sections:** Overview (read-aloud) → Lore (2–4 sentences) → Notable Locations → Known Inhabitants → Connections.

**File to:** the appropriate entity directory per CLAUDE.md § Directory Layout

---

## § Faction

**Interview (if needed):** Setting/tone, faction concept, PC hook.

**Name:** Culturally earned — proper noun group, title/role, corrupted historical, or geographic anchor. Load `naming-conventions.md`.

### Toy Fields (6)

Same as NPC fields plus **off_screen_action** — what the faction does when the party isn't watching. This is the sandbox engine: it makes the world move between sessions.

| Field | Content |
|---|---|
| **primary_goal** | What they always want |
| **consistent_method** | How they pursue it |
| **active_problem** | What's going wrong |
| **off_screen_action** | What they do when the party isn't watching |
| **performance_hooks** | How members are recognized — visual identity, vibe |
| **link_of_relevance** | Which PC is entangled |

**No org charts.** One crisp table for Structure if needed — key nodes, not political hierarchy. No council/political procedural content unless GM explicitly asks.

**Sections:** Lore (2–5 sentences, what holds them together, what they hide) → Structure → Connections.

**File to:** the appropriate entity directory per CLAUDE.md § Directory Layout

---

## § Ship

Use ships as mobile locations plus strategic assets. They are not just transport; they are pressure engines.

**Interview (if needed):** Tier/class, current status (active/impounded/destroyed), location, captain or owning faction, party relevance.

**Core frontmatter fields:** `tier`, `ship_class`, `current_location`, `status`, plus `captain` and/or `home_port` when applicable.

### Required Body Pattern

- `> [!read-aloud]` opening (1–3 sentences, visual and practical)
- `columns` block
  - Left column: Current State, Overview, and one state-specific section (`History`, `The Wreck`, or `Current Notes`)
  - Right column: `## Stat Block` markdown table with ship mechanics
- `## Layout` with deck-by-deck subsections when explorable
- State-specific logistics sections as needed: `Bastion Notes`, `Acquisition`, `Crew`
- `## Session Events`
- `## Connections`

### State Router

1. **Active ship** → emphasize crew readiness, route role, and bastion upgrade paths.
2. **Impounded / for-sale ship** → emphasize legal release cost, condition, and hidden leverage.
3. **Destroyed / wreck ship** → emphasize wreck location, losses, recoverables, and aftermath.

### Ship Stat Block Table (minimum fields)

`Type`, `Tier`, `Status`, `Hull Points`, `Hull AC`, `Condition`, `Speed`, `Maneuverability`, `Profile`, `Crew (min/full/max)`, `Cargo`, `Gun Mounts`, `Weapons`, `Upkeep`.

If a value is unknown, use a clear placeholder (`Unknown`), not omission.

**File to:** the appropriate entity directory per CLAUDE.md § Directory Layout

---

## § Condition

Condition pages are mechanical references, not narrative entities.

**Interview (if needed):** Ruleset version, exact condition name, whether this is strict SRD mirror or campaign-adjusted wording.

### Frontmatter Minimum

Use:
- `type: entity`
- `subtype: condition`
- `status: active`
- `tags: [rule, condition]`
- `sources`, `source_count`, `confidence_level`

### Body Pattern

- H1 with condition name
- `## Rule Text`
- Lead sentence: `While you have the <Condition> condition, you experience the following effects.`
- Effect lines in this format: `***Header.*** Rule sentence.`
- Optional `## Context` section for table-specific clarifications

### Rule Fidelity

- For canonical conditions, preserve mechanical intent and key thresholds exactly.
- Keep wording compact and scan-friendly; avoid lore language.
- One condition per page.

**File to:** the appropriate entity directory per CLAUDE.md § Directory Layout

---

## § Class

Class pages are reference condensations of published mechanics, not narrative world entities.

**Interview (if needed):** Rules edition/source, class name, and whether to emphasize resource progression text or spell-slot table detail.

### Frontmatter Minimum

Use:
- `type: concept`
- `subtype: class`
- `status: active`
- `tags` including `reference`, `class`, and class identifier
- `sources`, `source_count`, `confidence_level`
- `cssclasses: [wiki-reference]`

### Body Pattern

- H1 with class name
- Italic source line: `*Class — Source*`
- One-line mechanical profile using bold labels (Primary Ability, Hit Die, Saves, Armor, Weapons, Spellcasting)
- Horizontal rule
- Class-specific progression section:
  - text progression (for example class resource dice), or
  - `Spell Slots by Level` table
- `## Core Features` level table
- `## Subclasses`
- `## Connections`

### Rule Fidelity

- Keep mechanical thresholds and progression breakpoints exact to source.
- Keep wording compact and table-first; avoid narrative prose.
- One class per page.

**File to:** the appropriate concepts/reference directory per CLAUDE.md § Directory Layout

---

## § Rule

Rule pages are reference digests for mechanics and campaign implementation notes.

**Interview (if needed):** Source book/version, rule scope, and whether this page is strict summary or includes campaign adaptation.

### Frontmatter Minimum

Use:
- `type: concept`
- `subtype: rule`
- `status: active`
- `tags` including `rule` and `reference`
- `sources`, `source_count`, `confidence_level`

### Body Pattern

- H1 with rule name
- `## Rule Text` as primary section
- `###` subsections for components/mechanics
- Markdown tables for enumerations and progression where useful
- Optional `## Context` for campaign-specific adaptation notes
- `## Connections` to related rules/entities

### Rule Fidelity

- Preserve mechanical intent and thresholds from source.
- Prefer concise, implementation-first wording over lore prose.
- One rule system/topic per page; split oversized pages by subsystem when needed.

**File to:** the appropriate concepts/reference directory per CLAUDE.md § Directory Layout

---

## § Travel

Travel is drama, not logistics. Every event is a toy — a situation already in motion.

### Event Types (Pointy Hat TES)

| Color | Type | Focus |
|---|---|---|
| 🔴 Red | Combat | Fight with narrative stakes |
| 🔵 Blue | Roleplay | NPC, faction, moral dilemma |
| 🟡 Yellow | Exploration | Terrain hazard, wonder, skill challenge |

**Combos:** 🟣 Purple (RP+Combat) · 🟢 Green (Explore+RP) · 🟠 Orange (Combat+Explore) · ⚪ White (all three).

### Distance → Event Count

| Distance | Events | Notes |
|---|---|---|
| Close | 1 | +1 if dramatically loaded |
| Far | 2 | 3 for campaign centrepiece |
| Very Far | 3–4 | 5 for epic voyage |

### Composition Rules

- Never stack same type twice in a row
- At least one non-combat event per journey
- At least one event per journey must connect to an active PC thread — every event should
- Leave loose ends — events that resolve completely are wasted prep
- No event should star NPCs the party has never met doing things to NPCs they've never met

### Event Toy Format

Each event uses the encounter toy fields (Primary Goal, Consistent Method, Active Problem, Performance Hooks, Link of Relevance, Terrain Shift) plus a **Drama Suite** with applicable sub-elements: DC Tiers (10/15/20), Shenanigan offers, Box of Doom flags, stat block citations.

### Vault Handoff

Most travel events are ephemeral. Escalate to a wiki page only when the event introduces a recurring named entity or changes wiki state. Default: do not escalate.

**Travel method shapes the palette:** Ship (rival vessels, weather, sea creatures, crew problems) · Overland (road encounters, terrain, settlements) · Aerial (weather, predators, altitude) · Planar (reality warps, native denizens).

---

## § Session Prep

Orchestrate a table-ready session from wiki state. This section adds thread selection, session shaping, island design, pacing, and sub-skill orchestration on top of the universal rules above.

**Output:** filed as a reference page per CLAUDE.md § Directory Layout

### Protocol

**1. Orient** — Read `wiki/hot.md`. Determine session number. If threads are sparse, lean on unsurfaced PC backstory or introduce a faction off-screen action.

**2. Select Threads** — Load `references/pacing-heuristics.md`. Pick 3–4 threads from hot.md that could naturally surface. Leave at least 1 active thread untouched.

**3. Strong Start** — Load `references/strong-start-types.md`. First 30 seconds: party is mid-action. Situation already in motion, immediate decision required, rooted in hot cache. First line is read-aloud (Mercer voice). If last session ended dramatically, the Strong Start must acknowledge it.

**4. Narrative Islands** — Load `references/island-template.md`. For each island:
- Pick core entity, read their wiki page and toy fields
- State dramatic question in one sentence — if you can't, it's an errand, not an island
- Write default outcome (what happens if party never shows — proves stakes)
- Write DM brief (2–3 sentences), read-aloud opening (2–4 sentences), behavioral fallbacks

**Island composition:**
- 3 mandatory + 1 optional (4+1 for long sessions)
- Vary registers: social, exploratory, combat, revelation — never repeat back-to-back
- Max 1 major revelation per session
- The optional island must be genuinely cuttable
- Don't put a major revelation and major combat in the same island
- At least 1 island connects to a PC who hasn't had spotlight recently

**5. Sub-Skill Routing** — Generate new content inline as needed. NPCs get the full mashup + Voice & Delivery. Encounters use the 10-field toy. Travel events use TES typing. Embed sub-content in the island — don't create separate sections.

**6. Write & Index** — Use the session prep template for frontmatter. Structure: Strong Start → Narrative Islands → Travel Events (if applicable) → Faction Off-Screen Actions → Loose Ends. Add to `wiki/index.md`. No commit — prep is not canonical until played.

### Quality Gates

- [ ] Strong Start connects to an open thread and acknowledges last session's dramatic ending
- [ ] Every island has: dramatic question, default outcome, entity with toy fields
- [ ] At least one island is `[OPTIONAL]` and genuinely cuttable
- [ ] Registers vary — no adjacent islands share register; max 1 major revelation
- [ ] At least 1 island targets a spotlight-neglected PC
- [ ] Read-aloud is Mercer-voice
- [ ] No invented canonical facts
- [ ] Off-screen actions describe observable evidence
