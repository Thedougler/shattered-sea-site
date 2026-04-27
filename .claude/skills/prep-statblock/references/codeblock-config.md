---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
# Codeblock Config Keys

These keys go at the top of the `statblock` codeblock — before creature data fields — and control rendering behaviour rather than content.

---

## Layout

```yaml
layout: Basic 5e Layout
```

Selects which layout to render. The name must **exactly** match the layout name in plugin settings (case-sensitive, including spaces).

### Built-in Layout Names

| System | Layout Name |
|---|---|
| D&D 5e | `Basic 5e Layout` |
| Pathfinder 2e | `Basic Pathfinder 2e Layout` |
| 13th Age | `Basic 13th Age Monster Layout` |
| Fate Core | `Basic Fate Core Layout` |
| Daggerheart | `Basic Daggerheart Adversary Layout` |

To use a custom layout: duplicate an existing layout in settings, rename it, and use that exact name.

---

## Dice Integration

```yaml
dice: true      # Enable clickable dice rollers (requires Dice Roller plugin)
render: true    # Show 3D dice animations on roll (requires dice: true)
```

The plugin auto-detects common dice patterns:
- To-hit: `+15 to hit`
- Damage: `19 (2d10 + 8)`
- Save: `Strength +5`

---

## Columns

```yaml
columns: 2              # Split statblock into N columns (default: 1, max useful: 2-3)
forceColumns: true      # Force column split regardless of note width (default: false)
columnHeight: 750px     # Max height per column before wrapping (default: 600px)
columnWidth: 550px      # Width of each column (default: 400px)
```

Use `columns: 2` + `forceColumns: true` for large statblocks (dragons, bosses) to keep them compact.

---

## Bestiary & Source

```yaml
source: "Homebrew"      # Tags this creature under a named source in bestiary settings
bestiary: false         # Exclude from bestiary and Initiative Tracker (default: true)
player: false           # If true, Initiative Tracker counts as a PC (default: false)
```

---

## Export

```yaml
export: false           # Disable the "Export to PNG" menu option on this block
```

---

## Monster Recall

```yaml
monster: Ancient Black Dragon   # Load full statblock from bestiary by name
```

Combine with any other field to override specific values. Fields defined in the codeblock always take final precedence over the retrieved bestiary entry.

---

## Extends

```yaml
extends: Goblin                 # Inherit all fields from a named bestiary creature
```

Or multiple parents (last wins on conflict):

```yaml
extends:
  - Ancient Black Dragon
  - Goblin
```

Recursive: if the parent uses `extends`, all ancestor fields are inherited.

---

## Full Config Skeleton

```yaml
```statblock
# --- Config ---
layout: Basic 5e Layout
dice: true
render: false
columns: 2
forceColumns: true
columnHeight: 700px
columnWidth: 450px
source: "Homebrew"
bestiary: true
export: true

# --- Base (optional) ---
monster: Goblin       # or: extends: Goblin

# --- Creature Data ---
name: "Goblin Warchief"
hp: 45
cr: 3
...
` ``
```

---

## Common YAML Mistakes

| Symptom | Fix |
|---|---|
| Statblock renders blank | Check `name:` is present |
| "Unknown layout" error | Check `layout:` matches settings exactly |
| List item not rendering | Ensure `- name:` is indented 2 spaces under the parent key |
| Colon in a value breaks parse | Wrap the entire string in double quotes |
| Dice not rolling | Enable "Integrate Dice Roller" in plugin settings, or add `dice: true` to the block |
| Creature not appearing in bestiary | Check `statblock: inline` is in frontmatter and "Parse Frontmatter for Creatures" is on in settings |
