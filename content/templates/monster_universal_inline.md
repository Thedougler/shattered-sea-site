---
type: entity
subtype: monster
cr: CR_VALUE
creature_type: CREATURE_TYPE
environment: ENVIRONMENT_LIST
str: STR_SCORE
dex: DEX_SCORE
con: CON_SCORE
int: INT_SCORE
wis: WIS_SCORE
cha: CHA_SCORE
status: bestiary
confidence_level: high
sources: SOURCE_CODE
page: PAGE_NUMBER
tags:
  - creature
  - CREATURE_TYPE
  - SOURCE_CODE_LOWER
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
cssclasses:
  - wiki-monster
statblock: inline
source_count: 1
---

# MONSTER_NAME

```statblock
layout: Basic 5e Layout
name: "MONSTER_NAME"
size: SIZE
type: CREATURE_TYPE
alignment: ALIGNMENT
ac: AC_VALUE
hp: HP_VALUE
hit_dice: HIT_DICE
speed: "SPEED_STRING"
stats: [STR_SCORE, DEX_SCORE, CON_SCORE, INT_SCORE, WIS_SCORE, CHA_SCORE]

# Optional defenses and proficiencies (delete unused keys)
# saves:
#   - constitution: SAVE_BONUS
#   - wisdom: SAVE_BONUS
# skillsaves:
#   - perception: SKILL_BONUS
# damage_resistances: "RESISTANCE_LIST"
# damage_immunities: "IMMUNITY_LIST"
# condition_immunities: "CONDITION_LIST"

senses: "SENSES_AND_PASSIVE"
languages: "LANGUAGES_OR_HYPHEN"
cr: "DISPLAY_CR"

# Optional trait block (advanced monsters)
# traits:
#   - name: "TRAIT_NAME"
#     desc: "TRAIT_TEXT"

actions:
  - name: "Multiattack"
    desc: "ATTACK_ROUTINE_OR_REMOVE"
  - name: "PRIMARY_ATTACK"
    desc: "ATTACK_TEXT"

# Optional bonus actions
# bonus_actions:
#   - name: "BONUS_ACTION_NAME"
#     desc: "BONUS_ACTION_TEXT"

# Optional reactions
# reactions:
#   - name: "REACTION_NAME"
#     desc: "REACTION_TEXT"

# Optional legendary actions (legendary monsters)
# legendary_actions:
#   - name: "LEGENDARY_ACTION_NAME"
#     desc: "LEGENDARY_ACTION_TEXT"

# Optional spellcasting block (spellcasters)
# spells:
#   - "SPELLCASTING_HEADER"
#   - "Cantrips (at will): SPELL_LIST"
#   - "1st level (4 slots): SPELL_LIST"
#   - "2nd level (3 slots): SPELL_LIST"
```

Template usage notes:
- Simple monsters (Ape-style): keep only core fields + actions.
- Advanced monsters (Asteroid Spider-style): add saves/skills/traits/bonus_actions.
- Legendary monsters (Aboleth-style): add legendary_actions.
- Legendary spellcasters (Niv-Mizzet-style): add defenses + spells + legendary_actions.
