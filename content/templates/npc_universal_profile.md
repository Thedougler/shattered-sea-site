---
type: entity
subtype: npc
status: active
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
tags:
  - npc
  - TAG_1
  - TAG_2
sources:
  - Homebrew
source_count: 1
confidence_level: medium
appearance: One-sentence visual first impression.
campaign: shattered-sea
player_gravity: 0
gravity_sources:
  PC_NAME: 0
active_problem: Immediate pressure currently affecting this NPC.
primary_goal: What this NPC is trying to accomplish right now.
consistent_method: Repeatable table behavior pattern.
performance_hooks: One to three memorable DM cues.
link_of_relevance: "[[PC_OR_THREAD_ANCHOR]] — why this NPC matters in play."
faction: "[[FACTION_NAME]]"
location: "[[LOCATION_NAME]]"
species: SPECIES_OR_LINK
role: world role title
disposition: neutral
roleplay_prompt: Performance mashup seed
portrait: raw/assets/portraits/NPC-Name.webp
banner: raw/assets/banners/NPC-Name.webp
cssclasses:
  - wiki-npc
# Optional visibility keys
# public: false
# reveal_status: revealed
---

# NPC_NAME

> [!read-aloud]
> One to three sentences of immediate table-facing first impression.

## Toy Chest

| Active Problem | Primary Goal | Consistent Method | Performance Hooks | Link of Relevance |
| --- | --- | --- | --- | --- |
| Immediate pressure currently affecting this NPC. | What this NPC is trying to accomplish right now. | Repeatable table behavior pattern. | One to three memorable DM cues. | [[PC_OR_THREAD_ANCHOR]] — why this NPC matters in play. |

```columns
id: npc-profile-columns-id
===
<figure class="npc-portrait"><img src="../../../../raw/assets/portraits/NPC-Name.webp" alt="NPC Name" /></figure>

## Appearance

Visual details the table can use instantly.

## Voice & Delivery

- Speech cadence and vocabulary cue.
- Gesture/posture cue.
- Emotional floor and crack condition.

> "Sample line one."
>
> "Sample line two."

===
## Lore Sheet

Two to six short paragraphs of actionable lore.

Use this checklist:
- Origin and current role.
- Relationship to key anchors.
- What they do when off-screen.
- What changes if the party ignores them.
```

## Connections

- [[PC_OR_THREAD_ANCHOR]] — primary narrative anchor
- [[FACTION_NAME]] — factional alignment
- [[LOCATION_NAME]] — current operating location

## Stat Block

Optional. Include only when this NPC needs mechanics in this note.

```statblock
layout: Basic 5e Layout
name: NPC Name
size: Medium
type: humanoid
alignment: neutral
ac: 13
hp: 45
hit_dice: 6d8 + 18
speed: "30 ft."
stats: [12, 14, 16, 11, 12, 14]
senses: "Passive Perception 11"
languages: "Common"
cr: "2"
actions:
  - name: "Multiattack"
    desc: "The NPC makes two attacks."
```

## Session Events

None yet.

Template usage notes:
- Social/support NPC (Felix-style): keep Stat Block section as plain text "None" or omit codeblock.
- Command NPC with mechanics (Simone-style): fill full statblock and add tactical notes in Lore Sheet.
- Mentor NPC (Kyzil-style): prioritize Voice & Delivery and pilgrimage/thread hooks; statblock optional.
