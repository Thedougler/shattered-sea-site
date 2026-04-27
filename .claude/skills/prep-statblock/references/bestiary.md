---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
# Bestiary — Creature Storage Patterns

The bestiary is Fantasy Statblocks' internal creature database. Creatures in the bestiary can be recalled by name in any statblock codeblock and are available to Initiative Tracker.

---

## Three Ways to Add Creatures

### 1. Inline Codeblock (Recommended)

Set `statblock: inline` in the note's frontmatter. The plugin reads the first `statblock` codeblock in the note and registers it automatically.

```yaml
---
statblock: inline
name: Goblin Shaman
tags: [monster, goblinoid]
campaign: shattered-sea
---

```statblock
layout: Basic 5e Layout
name: Goblin Shaman
size: Small
type: humanoid
subtype: goblinoid
alignment: neutral evil
ac: 13
hp: 14
hit_dice: 4d6
speed: "30 ft."
stats: [8, 14, 10, 10, 8, 8]
cr: 1
traits:
  - name: Spellcasting
    desc: "The shaman is a 3rd-level spellcaster (Wisdom, spell save DC 11, +3 to hit)."
actions:
  - name: Quarterstaff
    desc: "Melee Weapon Attack: +2 to hit, reach 5 ft., one target. Hit: 3 (1d6) bludgeoning damage."
spells:
  - "Cantrips (at will): poison spray, sacred flame"
  - "1st level (4 slots): bane, cure wounds, inflict wounds"
` ``
```

This method is future-proof and recommended for all homebrew monster notes.

---

### 2. Frontmatter Only (Advanced)

Set all statblock fields directly in the note's YAML frontmatter with `statblock: true`. No codeblock required.

```yaml
---
statblock: true
name: Cave Goblin
size: Small
type: humanoid
ac: 12
hp: 7
stats: [8, 14, 10, 10, 8, 8]
cr: "1/4"
---
```

⚠ This method has more edge cases. Prefer inline codeblock unless you have a reason to avoid codeblocks.

---

### 3. Save Manually from a Codeblock

Render any `statblock` codeblock in a note, then click the menu icon (top-left of the rendered block) → **Save to Bestiary**. One-time manual action.

---

## Recall by Name

Once in the bestiary, any creature can be recalled by name:

```yaml
```statblock
monster: Goblin Shaman
` ``
```

The creature's full statblock is pulled from the database. This works with both SRD creatures (built-in) and homebrew creatures you have added.

---

## Overriding Fields on Recall

Combine `monster:` with any field to override specific values. Only listed fields change; everything else is inherited.

```yaml
```statblock
layout: Basic 5e Layout
monster: Goblin
name: "Goblin Boss"
hp: 21
cr: 1
traits+:
  - name: "Redirect Attack"
    desc: "When targeted by an attack, the boss redirects it to an adjacent goblin."
` ``
```

---

## Adding Fields with `+`

Append items to list fields without replacing existing content:

```yaml
actions+:
  - name: "New Ability"
    desc: "Description here."
```

Works on: `traits`, `actions`, `reactions`, `legendary_actions`, `bonus_actions`, `spells`.

---

## Removing Fields with `-`

Remove specific list items by name:

```yaml
actions-:
  - name: Tentacles
```

If multiple items share a name (e.g., `Melee`), include `desc:` to disambiguate:

```yaml
actions-:
  - name: Melee
    desc: "The partial description text to match."
```

---

## Extends / Inheritance

Create a new creature based on one or more existing ones. Later entries take precedence. Direct fields take final precedence.

```yaml
```statblock
layout: Basic 5e Layout
name: Veteran Goblin
extends: Goblin
hp: 21
ac: 16
cr: 1
` ``
```

Multiple parents (later overrides earlier):

```yaml
extends:
  - Ancient Black Dragon
  - Goblin
```

`extends` is recursive — if the parent itself extends another creature, all three levels of properties are inherited.

---

## Bestiary Control Fields

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `bestiary` | boolean | `true` | Set `false` to prevent a codeblock from appearing in the bestiary and Initiative Tracker. |
| `source` | string | — | Groups the creature under a named bestiary source in settings. |
| `player` | boolean | `false` | If `true`, Initiative Tracker treats this as a player character. |

---

## Note File Location

For this vault's canonical monster workflow, monsters are single-note inline entries (frontmatter + `statblock` codeblock in the same file), matching the exemplars in `raw/monsters/`.

Recommended frontmatter shape for monster entries:

```yaml
---
type: entity
subtype: monster
cr: 6
creature_type: monstrosity
environment: cave, coast
str: 18
dex: 12
con: 16
int: 8
wis: 12
cha: 10
status: bestiary
confidence_level: high
sources: XMM
page: 123
tags:
  - creature
  - monstrosity
  - xmm
created: '2026-04-26'
updated: '2026-04-26'
cssclasses:
  - wiki-monster
statblock: inline
source_count: 1
---
```

Keep the creature's H1 and statblock in the same note. Split lore/statblock files are optional, not the default.
