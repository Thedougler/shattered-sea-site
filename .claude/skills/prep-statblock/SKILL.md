---
name: prep-statblock
description: "Use when creating, fixing, extending, or debugging Fantasy Statblocks plugin codeblocks in Obsidian. Use when: creating a new monster or NPC statblock note; fixing a statblock that isn't rendering; wiring a creature to the bestiary; using monster: recall, extends:, or +/- field-append patterns; generating statblock YAML for any layout (5e, Pathfinder 2e, 13th Age, Fate Core, Daggerheart). Trigger on: statblock, fantasy statblocks, bestiary, creature block, monster block, stat block YAML, my statblock is broken, monster note, wire to bestiary, creature recall, homebrew creature, statblock not rendering, layout not working."
---

# Prep Statblock Skill

Produce syntactically valid `statblock` codeblocks and bestiary-wired creature notes for the **Fantasy Statblocks** Obsidian plugin (Javalent / TTRPG Community).

---

## Plugin-Specific Landmines (Things That Break Silently)

These are Fantasy Statblocks failure modes Claude won't know without this skill. Generic YAML errors are not the danger — these are.

- **`layout:` is case-and-space exact.** `"Basic 5e Layout"` ≠ `"basic 5e layout"` ≠ `"Basic 5E Layout"`. A wrong layout name causes the plugin to silently fall back to the default layout with no error shown. Always verify the exact string against **Settings → Statblock Layouts** in Obsidian before committing to it.

- **`monster:` recall silently returns nothing if the SRD bestiary source is disabled.** If the user's vault has the SRD source toggled off, or they're on a fresh install, `monster: Goblin` renders a blank block. Ask whether the SRD bestiary source is enabled if recall isn't working.

- **`extends:` does NOT deep-merge nested lists.** Overriding `actions:` on an extended creature replaces the entire list — not appends to it. Use `actions+:` to add entries, `actions-:` (with `name:` only) to remove by name. Never mix `extends:` with a full `actions:` list expecting a merge.

- **`statblock: inline` frontmatter registers the creature in the bestiary.** For this vault's canonical monster pipeline, monster entries are single-note inline statblocks (matching `raw/monsters/` exemplars). The frontmatter `name:` field must exactly match the codeblock `name:` when `name:` is present.

- **Dice expressions in `desc:` do NOT auto-link in all layouts.** Plain text `2d6+4` inside a description string is not interactive. To get clickable dice in the rendered block, use the `dice:` key at the top level, or format the expression as `dice: 2d6+4` inside a trait/action entry if the layout supports it.

- **`columns: 2` is a codeblock config key, not a layout.** There is no separate "two-column layout" — the standard `Basic 5e Layout` supports columns via the `columns: 2` codeblock option. Never create a new layout for columns.

- **Never auto-resolve stat contradictions.** If GM notes conflict with an existing statblock, flag it with a `> [!contradiction]` callout and present both values. Do not pick a winner.

---

## Decision Trees

### Should I use `monster:` recall or write from scratch?

| Situation | Approach |
|---|---|
| Creature exists in SRD and changes are <50% of fields | `monster: <SRD Name>` + override changed fields only |
| Homebrew with no SRD analog | Write full statblock from scratch |
| SRD base but >50% of fields differ | Write from scratch — recall noise outweighs value |
| SRD bestiary source is disabled in vault | Write from scratch |

### Should I use `extends:` or `monster:`?

- Need to recall a creature from the bestiary (cross-note) → use `monster:`
- Need to inherit from another note in the same vault → use `extends:`
- Both are defined for a creature → `monster:` takes precedence; do not mix them

### Which layout string do I use?

- Standard 5e → `Basic 5e Layout`
- Two-column → `Basic 5e Layout` + `columns: 2` codeblock key (never a separate layout)
- Custom layout → Must be defined in **Settings → Statblock Layouts** first; name must match exactly

---

## Reference Files — Mandatory Loading Triggers

**MANDATORY — read the entire file before generating any content in that category. Do not set line range limits.**

| Task | Load This File | Do NOT Load |
|---|---|---|
| Creating any 5e statblock | [`shared-references/5e-statblock.md`](../shared-references/5e-statblock.md) | `bestiary.md` unless wiring to bestiary |
| Wiring a creature to the bestiary | [`references/bestiary.md`](references/bestiary.md) | — |
| Using `columns:`, `dice:`, `extends:`, codeblock-level keys | [`references/codeblock-config.md`](references/codeblock-config.md) | — |
| Modifying an SRD creature | `5e-statblock.md` + `codeblock-config.md` | `bestiary.md` unless also wiring |

---

## Workflow

### Creating a new creature note

**MANDATORY — read [`shared-references/5e-statblock.md`](../shared-references/5e-statblock.md) completely before generating any fields.**
Do NOT load `bestiary.md` or `codeblock-config.md` unless the workflow below requires it.

1. Establish: name, size, type, CR, and layout string.
2. Fill all required fields from `shared-references/5e-statblock.md` reference.
3. Add `statblock: inline` to frontmatter so it registers in the bestiary.
4. Ensure the frontmatter `name:` exactly matches the codeblock `name:`.
5. Output a single monster page in the monsters entity directory (vault naming conventions apply).
6. Keep the statblock inline in that same note; do not split into a separate statblock-only file unless explicitly requested.

### Modifying an existing SRD creature

**MANDATORY — read [`references/codeblock-config.md`](references/codeblock-config.md) for `+`/`-` field append syntax before writing any overrides.**

1. Use `monster: <SRD Name>` to baseline.
2. Override only the fields that differ from SRD.
3. Use `actions+:` / `reactions+:` / `traits+:` to append — never overwrite a full section to add one entry.
4. Use `actions-:` with `name:` only to remove a specific action by name.

### Debugging a broken statblock

When a statblock isn't rendering or renders incorrectly, check in this order:

1. **Layout name** — copy the exact string from Settings → Statblock Layouts. This is the #1 silent failure.
2. **Bestiary source** — if using `monster:` recall, confirm the SRD source is enabled.
3. **Frontmatter `name:` vs codeblock `name:`** — must match exactly for bestiary registration.
4. **List-override vs list-append confusion** — if inherited actions disappeared, check for `actions:` vs `actions+:`.
5. **Unquoted colons in strings** — `desc: Melee Attack: +4` will break YAML parsing. Quote the value.
6. Validate standalone YAML at https://www.yamllint.com if root cause is still unclear.

---

## Key Patterns

### Minimal viable 5e statblock
````yaml
```statblock
layout: Basic 5e Layout
name: Goblin Scout
size: Small
type: humanoid
alignment: neutral evil
ac: 15
hp: 7
hit_dice: 2d6
speed: "30 ft."
stats: [8, 14, 10, 10, 8, 8]
cr: 1/4
actions:
  - name: Scimitar
    desc: "Melee Weapon Attack: +4 to hit, reach 5 ft., one target. Hit: 5 (1d6 + 2) slashing damage."
```
````

### Bestiary wire-up (recommended for all new creatures)
````yaml
---
statblock: inline
name: Goblin Shaman
---
```statblock
layout: Basic 5e Layout
name: Goblin Shaman
...
```
````
> `name:` in frontmatter MUST match `name:` in codeblock exactly, or bestiary registration silently misfires.

### Override a bestiary creature (append, not replace)
````yaml
```statblock
layout: Basic 5e Layout
monster: Goblin
name: "Goblin Shaman"
cr: 1
traits+:
  - name: "Spellcasting"
    desc: "The shaman is a 3rd-level spellcaster (Wisdom, DC 11)."
actions-:
  - name: Scimitar
```
````

### Extends / inheritance
````yaml
```statblock
layout: Basic 5e Layout
name: Elder Goblin
extends: Goblin
hp: 21
cr: 1
actions+:
  - name: Multiattack
    desc: "The elder goblin makes two scimitar attacks."
```
````
> Use `actions+:` not `actions:` — `extends:` does not merge lists; a bare `actions:` replaces the parent's entire list.
