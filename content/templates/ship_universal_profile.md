---
type: entity
subtype: ship
status: active
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
tags:
  - ship
  - tier-1
  - role-tag
sources:
  - Homebrew
source_count: 1
confidence_level: medium
banner: raw/assets/banners/Ship-Name.webp
campaign: shattered-sea
# Optional gravity keys
# player_gravity: 0
# gravity_sources:
#   PC_NAME: 0
tier: 1
ship_class: sloop (courier-rigged)
# Optional identity anchors
# captain: "[[Captain-Name]]"
# home_port: "[[Port-Tidefall]]"
current_location: CURRENT_LOCATION
cssclasses:
  - wiki-ship
---

# SHIP_NAME

> [!read-aloud]
> One to three sentences of visual first pass from dock or deck level.

```columns
id: ship-profile-columns-id
===
## Current State

Current condition, legal state, and practical readiness.

## Overview

Hull profile, role, and why it matters in play.

## History / Wreck / Current Notes

Pick one state-appropriate heading block:
- `## History` for active operational context
- `## The Wreck` plus `## The Aftermath` for destroyed ships
- `## Current Notes` for impounded or salvage opportunities

===
## Stat Block
| | |
| --- | --- |
| **Type** | SHIP_CLASS |
| **Tier** | TIER |
| **Status** | STATUS |
| **Hull Points** | HP |
| **Hull AC** | AC |
| **Condition** | CONDITION |
| **Speed (good wind)** | GOOD_WIND_SPEED |
| **Speed (poor wind)** | POOR_WIND_SPEED |
| **Speed (calm)** | CALM_SPEED_OR_DASH |
| **Maneuverability** | MANEUVERABILITY |
| **Profile** | PROFILE |
| **Crew (min/full/max)** | MIN / FULL / MAX |
| **Cargo** | CARGO_CAPACITY |
| **Gun Mounts** | MOUNT_COUNT |
| **Weapons** | WEAPON_LOADOUT |
| **Upkeep** | WEEKLY_COST |
| **Available Space** | SPACE_UNITS_OR_DASH |
```

## Layout

Explain deck-by-deck traversal and function.

### Weather Deck

Topside operations and visible features.

### Mid Deck / Cannon Deck

Work, combat, and command flow.

### Lower Deck / Hold

Storage, engineering, medical, powder, or hidden compartments.

## Bastion Notes

Upgrade vectors and strategic fit. Omit if not relevant.

## Acquisition

Use for impounded/sale ships: legal release process, total cost, and gatekeepers.

## Crew

Assigned or missing crew state.

## Session Events

None yet.

## Connections

- [[Faction-Or-Captain]] — operating authority
- [[Port-Or-Region]] — current location anchor
- [[Ship-Bastion]] — upgrade framework
- [[wiki/dnd/rules/Ship-Mechanics]] — mechanical rules anchor

Template usage notes:
- Destroyed flagship (Red Lady-style): emphasize The Wreck and The Aftermath sections.
- Impounded vessel (Lasting Insult-style): emphasize Acquisition and Current Notes.
- Active vessel: keep Crew and Bastion Notes fully populated.
