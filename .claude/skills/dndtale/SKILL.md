---
name: dndtale
description: "Campaign scaffolding for this vault. Use whenever the user wants to start, plan, build, organize, or reshape a D&D campaign — even if they just say 'I want to run a pirate campaign' or 'let's plan season 2' or 'set up a sandbox'. This skill turns rough ideas, existing notes, or a bare premise into a complete vault-ready campaign structure with hub pages, typed subfolders, season/chapter planning, and navigation files. It wires into blm-prep-style for prep philosophy, wiki-query for existing campaign context, run-sandbox for player gravity, and prep-content for detailed NPC/faction/location generation. Trigger on: campaign creation, campaign scaffolding, season planning, chapter planning, sandbox design, campaign hub setup, campaign reorganization, 'build me a campaign', 'I want to run a...', 'let's set up...', or any request to organize or expand a D&D campaign in the wiki."
---

# Dndtale

Dndtale is the campaign scaffolding skill for this vault. Its job is to build and maintain a complete campaign structure that fits the existing wiki layout, then route detailed prep through the correct downstream skills.

It does not replace the Brennan Lee Mulligan prep framework or the vault's detailed prep engine. It provides the campaign shell those workflows live inside.

---

## Skill Responsibilities

This skill owns the scaffolding layer — campaign folder shape, hub pages, organizing documents, season/chapter breakdowns, file placement, and cross-file consistency. It delegates everything else.

When responsibilities overlap, resolve in this order:

| Step | Skill | Responsibility |
|---|---|---|
| 1 | `wiki-query` | Retrieve existing campaign context from the vault |
| 2 | `run-sandbox` | Load gravity — what does the party currently care about? |
| 3 | `blm-prep-style` | Prep philosophy: reactive systems, toys, strong starts |
| 4 | `prep-content` | Generate detailed NPCs, factions, locations, encounters |
| 5 | `dndtale` | Decide where content lives and how the campaign is organized |

---

## Use This Skill For

- Creating a new campaign in `wiki/dnd/campaigns/`
- Scaffolding a full standard-style campaign
- Scaffolding a full sandbox-style campaign
- Reorganizing an existing campaign so it fits the vault structure
- Building season, chapter, and hub documents around an existing D&D premise
- Expanding a rough campaign idea into a complete vault-ready campaign shell
- Refitting campaign files so future NPC, faction, encounter, and location work can be delegated cleanly

Do not use this skill for one-off NPCs, encounters, factions, or locations when no campaign scaffolding is needed. Route those directly to `prep-content` or other downstream prep skills.

---

## First Principles

1. **Scaffold around player pull.** Structure that ignores what the players actually care about will be ignored by the players. Load gravity data for existing campaigns before shaping priorities.
2. **Support multiple routes, not one intended route.** Campaign structure should enable player agency, not constrain it. Fronts and factions create pressure; they don't guarantee outcomes.
3. **Match the live vault, not an abstract template.** Published-adventure formatting and generic wiki templates both produce structure the agent and GM won't use. Mirror what already works in this vault.
4. **Keep the campaign navigable.** Every campaign needs a hub page that makes current state scannable in under a minute — for both humans in Obsidian and agents at boot.
5. **Separate scaffolding from content generation.** This skill creates the container. `prep-content` fills it. Conflating the two produces bloated hub files and loses the delegation benefit.

---

## Concrete Example

**User says:** "I want to start a new pirate sandbox campaign. The party runs a stolen warship and I'm thinking rival fleets, cursed islands, and a colonial power cracking down on free ports."

**What this skill does:**
1. Asks the minimum intake questions (campaign name/slug, tone, level range, which PCs are in scope)
2. Identifies this as a **sandbox** campaign — hub-and-spokes structure, faction web, no fake linear chapters
3. Creates `wiki/dnd/campaigns/saltblood-coast/` with hub, overview, index, hot, and typed subfolders
4. Writes `Saltblood-Coast-Hub.md` with frontmatter, premise, active factions scaffold, and navigation links
5. Stubs `Player-Gravity-Wells.md` and `Campaign-Timeline.md` as empty tracking files
6. Hands off to `prep-content` (loaded with `blm-prep-style`) for the rival fleet NPCs, cursed island locations, and colonial faction write-ups

---

## Canonical Output Location

Create and maintain campaigns under:

```text
wiki/dnd/campaigns/<campaign-slug>/
```

Model the structure after the existing vault pattern used by `wiki/dnd/campaigns/shattered-sea/`.

Typical campaign scaffold:

```text
wiki/dnd/campaigns/<campaign-slug>/
├── <Campaign-Name>-Hub.md
├── campaign-overview.md
├── index.md
├── hot.md
├── README.md
├── Player-Gravity-Wells.md
├── Campaign-Timeline.md
├── The-Party.md
├── narratives/
├── npcs/
├── factions/
├── locations/
├── regions/
├── encounters/
├── items/
├── monsters/
├── ships/
├── species/
├── player-characters/
├── questions/
├── art/
└── changelog/
```

Adjust folder names to match the actual local campaign pattern when the target campaign already exists. Prefer the live vault convention over abstract template purity.

---

## Templates

All page creation should use the vault's canonical templates in `wiki/system/templates/`. Do not invent frontmatter schemas from scratch — check the relevant template first.

### Campaign-level templates
| Template | Path | Use for |
|---|---|---|
| Campaign overview | `wiki/system/templates/campaign-overview.md` | `campaign-overview.md` in every new campaign |
| Faction | `wiki/system/templates/faction.md` | Faction pages in `factions/` |
| Location | `wiki/system/templates/location.md` | Location pages; or use `dnd/location/vix-location.md` for D&D-specific layout |
| Quest / arc | `wiki/system/templates/quest.md`, `arc.md` | Active narrative threads and chapter arcs |
| Thread | `wiki/system/templates/thread.md` | Open narrative threads in `narratives/` |

### D&D-specific templates (in `wiki/system/templates/dnd/`)
| Template | Path | Use for |
|---|---|---|
| NPC | `dnd/npc/vix-npc.md` | All NPC pages — use this over the generic `npc.md` for D&D campaigns |
| Location | `dnd/location/vix-location.md` | D&D location pages |
| Session | `dnd/session/vix-session.md` | Session prep and session summary pages |
| Adventure | `dnd/adventure/vix-adventure.md` | Adventures, modules, one-shots |
| Organization | `dnd/organization/vix-organization.md` | Factions and guilds (more detailed than `faction.md`) |
| Item | `dnd/item/vix-item.md` | Magic items and notable gear |
| Character | `dnd/character/vix-character.md` | Player character pages |

### Entity-type templates (top-level)
| Template | Path | Use for |
|---|---|---|
| NPC | `wiki/system/templates/npc.md` | Generic NPC (prefer `dnd/npc/vix-npc.md` for D&D) |
| Monster | `wiki/system/templates/monster.md` | Homebrew monsters |
| Species | `wiki/system/templates/species.md` | Playable/notable species |
| Ship | `wiki/system/templates/ship.md` | Vessels |
| Item | `wiki/system/templates/item.md` | Generic items |
| Deity | `wiki/system/templates/deity.md` | Gods and pantheons |
| Spell | `wiki/system/templates/spell.md` | Spells |
| Lore | `wiki/system/templates/lore.md` | World-building lore entries |
| PC sheet | `wiki/system/templates/pc-sheet.md`, `pc.md` | Player character full sheets |
| Session summary | `wiki/system/templates/session-summary.md` | Post-session records |
| Source session | `wiki/system/templates/source-session.md` | Raw session notes as source pages |

### Campaign hub page

There is no dedicated hub template — the hub is campaign-specific. Structure it around the `campaign-overview.md` template and add navigation links. Keep it under 400 words: its job is fast orientation, not documentation. Sections to include:

- **Current State** — active fronts, where the party is, immediate pressures
- **The Party** — links to PC pages
- **Active Factions** — 3–5 factions with one-line status and links
- **Key Locations** — hub locations and region anchors with links
- **Open Questions** — DM-facing unresolved tensions
- **Navigation** — links to `index.md`, `hot.md`, `Player-Gravity-Wells.md`, `Campaign-Timeline.md`

---

## Campaign Modes

### Standard Campaign
Use for campaigns with a clearer arc, season progression, or chapter cadence.

Scaffold around:
- campaign premise
- season or chapter structure
- major fronts and escalating pressures
- expected pivot points, not fixed scenes
- a campaign hub that makes current state easy to scan

### Sandbox Campaign
Use for campaigns built around a hub, region, city, sea, faction web, or open travel structure.

Scaffold around:
- locations or regions that can be visited in many orders
- active factions with off-screen motion
- player-driven objectives
- convergence points surfaced by gravity data
- reusable narrative islands and deployable set pieces

Do not force a sandbox into a fake chapter sequence just to make it look organized. Use organizing pages, hub files, and region/location structures instead.

---

## Required Intake

Before scaffolding, establish these:

1. Campaign name and slug
2. Standard or sandbox mode
3. Tone and rating boundaries
4. Intended level range or power band
5. Whether this is a new campaign or an existing one being reorganized
6. Which PCs or player arcs are in scope
7. Whether gravity data already exists

If key information is missing, ask concise questions before writing files.

---

## Gravity Workflow

For an existing campaign, load gravity before building content that will shape campaign priorities.

### Party-wide campaign planning
Use convergence output:

```bash
wiki workflow gravity --agent-brief --convergence
```

### PC-specific arc planning
Use the relevant PC:

```bash
wiki workflow gravity --agent-brief --pc <PC-Slug>
```

### If the gravity map needs refreshing
Run:

```bash
wiki workflow gravity --write
```

Use the resulting gravity brief to decide:
- which factions deserve attention now
- which NPCs should be elevated into core campaign scaffolding
- which locations should become major anchors
- where party convergence suggests strong shared content

Never invent player pull if the vault data does not support it.

---

## Session Zero Baseline

For character-centered campaign intake, load `blm-prep-style` and use its Session Zero questions. Those questions are maintained in that skill — don't duplicate them here.

Use the answers to shape campaign fronts, faction tensions, active narrative pressures, strong starts, and sandbox anchors.

If the campaign already exists, infer as much as possible from the vault via `wiki-query` before asking the user to restate anything.

---

## Workflow

### 1. Read First

For an existing campaign, use `wiki-query` first to retrieve the current campaign context, then read the narrowed set of organizing pages before editing.

Use `wiki-query` to identify:
- the primary campaign hub page
- active factions, NPCs, and locations already in play
- current season, chapter, or sandbox state
- open questions or unresolved tensions relevant to the request

Start with:
- campaign hub file
- `campaign-overview.md`
- `index.md`
- `hot.md`
- `Player-Gravity-Wells.md` when present

Then read only the specific subfolders needed for the requested change.

If `wiki-query` already surfaces the relevant pages and summaries, do not widen the read unnecessarily.

### 2. Choose the Campaign Shape

Decide whether the campaign is best represented as:
- a standard arc with seasons/chapters
- a sandbox hub with distributed regions, factions, and narrative islands
- a hybrid, where seasons exist but travel/order remains player-driven

### 3. Scaffold the Core Files

For a new campaign, create the minimum viable scaffold:
- campaign hub page
- `campaign-overview.md`
- `index.md`
- `hot.md`
- `README.md`
- `Player-Gravity-Wells.md` if player-arc tracking is part of the campaign
- key content folders

For an existing campaign, normalize and improve the scaffold instead of replacing working structure.

### 4. Route Detailed Content Correctly

When the user asks for detailed content inside the scaffold:
- NPCs, factions, locations, encounters, strong starts, and session prep should route to `prep-content`
- `blm-prep-style` remains the guiding prep philosophy for how that content should work
- content priorities should be informed by `run-sandbox`

Use `prep-content` reference loading and toy rules for the detailed generation step.

### 5. Maintain Cross-File Integrity

Whenever the scaffold changes:
- keep names consistent
- keep links navigable
- keep summaries in sync with detailed pages
- preserve the campaign's chosen mode

---

## What To Produce

Default outputs for this skill are vault-native campaign artifacts, not generic prose bundles.

Common deliverables:
- campaign hub page
- campaign overview
- season or chapter planning pages
- sandbox hub or region map pages
- faction roster scaffolding
- location and region directories
- player-arc question pages
- README/session-zero setup pages
- campaign indices and navigation helpers

If the user wants only a plan, provide a file-by-file scaffold plan first. If they want implementation, create or edit the files directly.

---

## File and Naming Guidance

- Prefer campaign-specific filenames that match the vault's existing style.
- Keep top-level campaign documents human-scannable and agent-scannable.
- Prefer one strong organizing page over one bloated omnibus file.
- Use subfolders for entity types instead of collapsing everything into `npcs.md` or `locations.md` when the campaign has real scope.

When working in an existing campaign, mirror that campaign's conventions before introducing new ones.

---

## Anti-Patterns

- **Fixed plot masquerading as scaffold.** Writing out what "will happen" in scenes is railroading, not prep. Build pressure systems and reactive factions instead.
- **Ignoring gravity for an existing campaign.** Building content players don't care about wastes prep time. Always load gravity data before shaping priorities for active campaigns.
- **Forcing sandbox into fake linear chapter rails.** Sandboxes need faction clocks and location anchors, not act structures. A fake chapter frame gets abandoned the moment players go sideways.
- **Omnibus campaign files.** One massive `npcs.md` file can't be delegated, searched, or updated cleanly. Use typed subfolders from the start — that's what `prep-content` expects.
- **Generic adventure-book formatting.** Published modules use static boxed-text, room keys, and encounter tables. This vault uses toys, factions, gravity, and BLM-style reactive systems.
- **Introducing new file conventions.** When working inside an existing campaign, mirror its naming and structure before inventing new patterns.

---

## Delegation Rules

| Need | Route to |
|---|---|
| Campaign shell, hub, folders, season/chapter scaffold | `dndtale` |
| Existing campaign context, connected entities, and current wiki state | `wiki-query` |
| NPC, faction, location, encounter, strong start, or session prep generation | `prep-content` |
| Brennan-style prep philosophy and campaign stance | `blm-prep-style` |
| Gravity scoring or convergence analysis | `run-sandbox` |
| Party combat analysis | `party-combat-primer` |
| Single-PC combat deep dive | `pc-combat-primer` |

---

## Success Criteria

This skill is working correctly when:
- a new or updated campaign cleanly fits under `wiki/dnd/campaigns/<slug>/`
- existing campaign context can be retrieved quickly through `wiki-query` before structural edits
- the campaign can be navigated from its hub and index pages
- standard and sandbox campaigns both have coherent scaffolds
- detailed prep can be handed off to `prep-content` without format conflict
- current player pull can be incorporated through `run-sandbox`
- the scaffold supports agency, iteration, and long-term campaign maintenance
- **One-Shot Adventures** - Single-session adventures with clear objectives and satisfying conclusions
- **NPCs** - Memorable characters with personalities, motivations, secrets, and stat blocks
- **Locations** - Detailed settings with atmosphere, history, and interactive elements
- **Encounters** - Balanced challenges with multiple solutions and meaningful consequences
- **Story Frameworks** - Narrative structures that preserve player agency while ensuring coherent plots
- **Image Prompts** - Detailed prompts for AI image generation tools

---

## Core Principles

### Player Agency First
- Always provide multiple solutions to problems
- Design consequences that matter
- Avoid railroading (forced single paths)
- Let player choices shape the story

### Usability at the Table
- Write clear, scannable DM notes
- Provide concise read-aloud text
- Include quick reference tables
- Anticipate common DM needs

### Completeness and Consistency
- Cross-reference between documents
- Maintain timeline and logic
- Keep names and facts consistent
- Check dependencies when changing content

### Use the Right Tools
- **TodoWrite:** Track complex campaign creation tasks
- **AskUserQuestion:** Clarify requirements and gather preferences
- **Read:** Always read existing files before editing
- **Edit:** Make targeted changes to existing content
- **Write:** Create new files from templates

---

## File Organization

Every campaign should follow this structure:

```
campaigns/[campaign-name]/
├── campaign-overview.md         # Master document with full campaign arc
└── changelog/                   # Changelogs
    └── [change-name].md         # Documented changes to the campaign
├── README.md                  # Player-facing session zero document (spoiler-free)
├── chapter-01.md                # Detailed session content
├── chapter-02.md                # Continue for each chapter/session
├── chapters-summary.md          # Chapter/Scene-level summaries for all chapters of the campaign
├── npcs.md                      # Important characters with stats and motivations
├── locations.md                 # Key places with descriptions
├── factions.md                  # Organizations and their goals (optional)
├── timeline.md                  # Timeline of events in the campaign (optional)
└── art/                         # Image prompts and artwork
    ├── [scene-name].md          # Image generation prompts for scenes
    ├── [location-name].md       # Image generation prompts for locations/environment
    ├── [npc-name].md            # Image generation prompts for unique NPCs
    └── [generated-images.jpg]   # Actual artwork *.jpg (if generated)
```

---

## Resource Library

### Templates
Use these as starting points for all campaign documents:

- **[campaign-overview.md](templates/campaign-overview.md)** - Master campaign document
- **[chapter-template.md](templates/chapter-template.md)** - Individual session structure
- **[chapters-summary.md](templates/chapters-summary.md)** - Scene-level overview for all chapters of the campaign
- **[timeline.md](templates/timeline.md)** - Timeline of events in the campaign
- **[README.md](templates/README.md)** - Player-facing session zero document
- **[npcs.md](templates/npcs.md)** - NPC roster and details
- **[locations.md](templates/locations.md)** - Location descriptions and maps
- **[factions.md](templates/factions.md)** - Organizations and politics

### Modules
Reference these for detailed guidance:

- **[campaign-types.md](modules/campaign-types.md)** - Linear, Sandbox, Event-Based, Setting-Based
- **[world-building.md](modules/world-building.md)** - Creating settings, NPCs, and interactions
- **[formatting-conventions.md](modules/formatting-conventions.md)** - How to format all content

### Workflows
Step-by-step processes for different tasks:

- **[campaign-creation-workflow.md](workflows/campaign-creation-workflow.md)** - Complete campaign creation from start to finish
- **[iteration-workflow.md](workflows/iteration-workflow.md)** - Updating and refining existing campaigns

### Checklists
Quality assurance for your work:

- **[campaign-quality-checklist.md](checklists/campaign-quality-checklist.md)** - Ensure completeness, balance, and quality
- **[consistency-checklist.md](checklists/consistency-checklist.md)** - Maintain consistency when making changes

### Examples
Complete sample campaigns demonstrating all templates:

- **[The Stolen Flame](examples/the-stolen-flame/)** - One-shot adventure showing all templates in action

---

## Workflow Overview

### Creating a New Campaign

**Phase 1: Gather Requirements**
1. Use TodoWrite to create planning checklist
2. Use AskUserQuestion if briefing incomplete
3. Collect: story idea, length, level, setting, tone

**Phase 2: Campaign Framework**
1. Choose campaign type (see [modules/campaign-types.md](modules/campaign-types.md))
2. Create campaign-overview.md (use [template](templates/campaign-overview.md))
3. Plan chapter breakdown
4. Create chapters-summary.md (use [template](templates/chapters-summary.md))
5. Identify major NPCs and locations

**Phase 3: Detailed Development**
1. Write each chapter (use [template](templates/chapter-template.md))
2. Detail NPCs (use [template](templates/npcs.md))
3. Detail locations (use [template](templates/locations.md))
4. Create factions if needed (use [template](templates/factions.md))
5. Create

**Phase 4: Player-Facing Content**
1. Write README.md (use [template](templates/README.md))
2. Ensure there are NO SPOILERS in the briefing

**Phase 5: Polish & QA**
1. Create image prompts for key scenes
2. Run through [campaign-quality-checklist.md](checklists/campaign-quality-checklist.md)
3. Read entire campaign for flow and consistency

**See detailed workflow:** [workflows/campaign-creation-workflow.md](workflows/campaign-creation-workflow.md)

### Updating an Existing Campaign

1. **Read** all affected files first
2. **Plan** changes and identify dependencies
3. **Edit** existing files with targeted changes
4. **Update** cross-references
5. **Check** consistency with [consistency-checklist.md](checklists/consistency-checklist.md)

**See detailed workflow:** [workflows/iteration-workflow.md](workflows/iteration-workflow.md)

---

## Important Guidelines

### Always Do This

**Use TodoWrite for Complex Tasks**
- Create planning checklist immediately
- Track progress through creation phases
- Mark tasks completed as you finish them
- Keep exactly ONE task in_progress at a time

**Ask Questions When Needed**
- Use AskUserQuestion for unclear requirements
- Clarify tone, content boundaries, player preferences
- Ask about multiple valid approaches
- Don't guess—confirm with the DM

**Read Before Editing**
- Always Read existing files before using Edit
- Understand the full context
- Check dependencies and cross-references
- Maintain consistency with existing content

**Preserve Player Agency**
- Provide multiple solutions to every problem
- Design meaningful consequences
- Allow creative approaches
- Avoid forced single paths

**Follow Templates**
- Use the templates in [templates/](templates/)
- Maintain consistent formatting
- Include all required sections
- Match the style of examples

### Never Do This

**Don't Railroad Players**
- Never force a single solution
- Don't invalidate player choices
- Avoid "the NPC does everything" solutions

**Don't Skip Quality Checks**
- Always use checklists before completion
- Verify cross-references work
- Check name consistency
- Test story logic

**Don't Forget Documentation**
- Cross-reference between documents
- Link to related content
- Include DM notes and tips
- Provide stat blocks or references

**Don't Break Existing Content**
- When editing, maintain story logic
- Update all references to changed content
- Check timeline consistency
- Preserve what works

---

## Session Zero Considerations

Unless stated otherwise, campaigns are written for consenting adults. When content might be disturbing or NSFW:

- Include content warnings in README.md
- Suggest Session Zero discussion topics
- Recommend safety tools (X-Card, Lines & Veils)
- Clearly mark mature content

---

## Standard D&D Adventure Structure

The skill follows professional D&D adventure conventions (see [STRUCTURE.md](STRUCTURE.md) for full details):

**Front Matter:** Introduction, synopsis, hooks
**Core Structure:** Chapter breakdown with scenes, encounters, NPCs
**Climax:** Epic final encounter with multiple resolution paths
**Back Matter:** Appendices with stat blocks, magic items, handouts

**Each Chapter Includes:**
- Read-aloud text for scene setting
- DM information and secrets
- Encounter design (combat, social, skill challenges)
- NPCs with personality and stats
- Treasure and rewards
- Connections to other chapters

---

## Formatting Standards

Follow conventions in [modules/formatting-conventions.md](modules/formatting-conventions.md):

**Read-Aloud Text:**
```markdown
> Text the DM reads to players
> Detailed, evocative, multi-sensory
> Present tense, no secrets
```

**DM Notes:** Regular text with mechanical details, secrets, contingencies

**Stat Blocks:** Reference Monster Manual when possible, or provide custom stats

**Cross-References:** Use markdown links: `[Chapter 2](chapter-02.md)` or `[NPCs](npcs.md#npc-name)`

**Image Prompts:** Create in `art/` folder with proper metadata

---

## Quick Reference

### Campaign Types
- **Linear:** Sequential chapters, clear path (easiest to prep)
- **Sandbox:** Central hub, many options (most prep)
- **Event-Based:** Timeline of events, player actions affect outcomes
- **Setting-Based:** Location-focused, exploratory

See: [modules/campaign-types.md](modules/campaign-types.md)

### Encounter Design
- Mix combat, social, and exploration
- Multiple solutions always
- Appropriate difficulty for level
- Meaningful consequences

### NPC Design
- Appearance, personality, mannerisms
- Wants (surface goal) and needs (deeper motivation)
- Secrets and relationships
- Stat block or reference

See: [templates/npcs.md](templates/npcs.md)

### Location Design
- Atmosphere (sights, sounds, smells, feel)
- History and current situation
- NPCs present and encounters
- Secrets to discover

See: [templates/locations.md](templates/locations.md)

---

## Tone and Content

**Adjust to DM's requested tone:**
- Heroic & Epic
- Dark & Serious
- Humorous & Lighthearted
- Mystery & Intrigue
- Horror
- Adult-themed/NSFW (with appropriate warnings)

**Always:**
- Match requested tone consistently
- Warn about mature content in briefing
- Provide Session Zero guidance for sensitive topics

---

## Image Generation Integration

Create detailed prompts for AI image generation (reference `dndig` tool if available):

**Format:**
```markdown
---
title: filename-prefix
aspect_ratio: "16:9"
resolution: 2K
instructions: optional-style-file.md
---

Detailed visual description based on scene read-aloud text...
Include: composition, lighting, mood, style
```

**Create prompts for:**
- Key locations and scenes
- Important NPCs
- Climactic encounters
- Maps (as needed)

---

## Examples in Action

### Example: Starting a New Campaign

```
DM: "I want to create a 3-session campaign about smugglers in a port city"

You:
1. TodoWrite: Create planning checklist
2. AskUserQuestion: Clarify tone, starting level, player count
3. Choose campaign type: Sandbox (city hub with multiple quest lines)
4. Create campaign-overview.md from template
5. Create 3 chapters, npcs.md, locations.md
6. Create README.md for players
7. Run quality checklist
8. Deliver organized campaign
```

### Example: Updating Existing Campaign

```
DM: "The players killed the quest-giver NPC. I need to adapt."

You:
1. Read campaign-overview.md and affected chapters
2. Read npcs.md to understand the NPC's role
3. Follow iteration-workflow.md
4. Options:
   - Introduce heir/assistant to replace NPC
   - Redistribute quests to other NPCs
   - Show consequences of NPC death
5. Edit affected chapters
6. Update npcs.md and cross-references
7. Run consistency checklist
```

---

## Success Criteria

A campaign is ready when:

- [ ] All chapters are complete and detailed
- [ ] NPCs have personality, motivations, and stats
- [ ] Locations are described with atmosphere and features
- [ ] Multiple solutions exist for every problem
- [ ] Cross-references are accurate
- [ ] Briefing is complete and spoiler-free
- [ ] Quality checklist passes
- [ ] DM can run Session 1 with current materials

---

## Getting Help

**Stuck on something?**
- Check the relevant module in [modules/](modules/)
- Review the workflow in [workflows/](workflows/)
- Look at the example in [examples/the-stolen-flame/](examples/the-stolen-flame/)
- Use AskUserQuestion to clarify with the DM

**Need to verify quality?**
- [campaign-quality-checklist.md](checklists/campaign-quality-checklist.md)
- [consistency-checklist.md](checklists/consistency-checklist.md)

---

## Remember

You're helping a DM create memorable experiences for their players. Focus on:

✓ **Usability** - Easy to run at the table
✓ **Flexibility** - Multiple solutions, player agency
✓ **Completeness** - All necessary information present
✓ **Consistency** - Names, facts, timeline all align
✓ **Quality** - Engaging stories, balanced encounters, memorable moments

Good luck, and may your campaigns be legendary!
