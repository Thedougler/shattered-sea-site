---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
# Session Pacing & Thread Selection Heuristics

Expert-level knowledge for assembling a session that *feels* right at the table — not just a list of scenes, but a shaped experience with rhythm, escalation, and breathing room.

---

## Thread Selection

You have 8–15 open threads in `wiki/hot.md`. A session can meaningfully advance 2–3. Choosing the wrong ones makes the session feel scattered. Choosing the right ones makes it feel inevitable.

### Selection Heuristics

**Priority 1 — PC personal arcs that haven't had spotlight in 2+ sessions.** Players track this even when they don't say anything. If the rogue's backstory hasn't surfaced in three sessions, the player is starting to wonder if it matters.

**Priority 2 — Faction threads with Off-Screen momentum.** If a faction has been acting off-screen for multiple sessions, the results should become visible. Players should feel the world moving. Pick the faction whose actions would be hardest to ignore this session given the party's current location.

**Priority 3 — Threads marked `[urgent]` or with explicit timelines.** If a clock is ticking, it should tick visibly. Don't waste urgency — if you flagged something as urgent, it should matter in the next 1–2 sessions or the urgency was fake.

**Priority 4 — Threads with a ready-to-stage location.** If the party is in Kalowe and three threads can fire in Kalowe, those are cheaper (in narrative distance) than a thread that requires travel to a new location. Proximity lowers the activation cost.

### Selection Anti-Patterns

| Anti-Pattern | Problem | Rule |
|---|---|---|
| **Thread Flooding** | 4+ faction threads in one session | **Max 2 faction threads per session.** Players can track "the Ironmantle and the Antheri are both moving" but not "four factions are all doing things." |
| **Arc Neglect** | A PC's personal thread hasn't surfaced in 3+ sessions | **Mandatory spotlight rotation.** If a PC hasn't had a personal beat in 2 sessions, one island this session must connect to their arc. |
| **False Urgency** | Marking threads `[urgent]` then not advancing them | **Urgent means this session or next.** If it can wait 3 sessions, it's not urgent — it's important. Different queue. |
| **Geography Sprawl** | Islands that require the party to be in 4 different places | **Max 2 locations per session** unless travel *is* the session. If islands require distant locations, pick the ones that cluster. |
| **Sequel Neglect** | Last session ended with a dramatic moment that isn't addressed | **The Strong Start must acknowledge the last session's ending.** If the party killed the duke, session N doesn't open with shopping. |

### When Threads Are Sparse

Not every session has 8–15 open threads. Early campaigns, post-arc lulls, and single-location lockdowns need different strategies.

| Situation | Thread Count | Strategy |
|---|---|---|
| **Early campaign** (sessions 1–3) | 2–4 threads | Go deeper, not wider. One thread per island, fully explored. Use Discovery or Interrupted Routine strong starts to seed new threads *through play*, not by fiat. Lean on PC backstory — it's the richest untapped source. |
| **Post-arc lull** (major arc just resolved) | 1–3 active threads | This is a breathing session. Open with a Return strong start (consequences of the resolved arc). Use one island for fallout, one for a PC personal beat, one to plant the seed of the next arc. Lower intensity is correct here — don't force a new crisis. |
| **Single-location lockdown** (party confined to one place) | Normal count, but geography-constrained | Filter threads by *which ones can fire here*. Islands become layered — multiple pressures in the same physical space, creating forced encounters between NPCs who wouldn't normally interact. This is a pressure cooker session. |
| **One dominant thread** (everything orbits one crisis) | 1 thread, multiple facets | Break the single thread into facets: the political angle (social island), the physical threat (combat island), the hidden truth (revelation island). One thread ≠ one island. |

**The rule:** Sparse threads don't mean a thin session — they mean a *focused* session. Fewer threads = more time per thread = deeper play. Resist the urge to invent new threads to fill space.

---

## Session Rhythm

A session is not a list of scenes — it's a shaped experience. Register variation creates rhythm; monotone creates fatigue.

### Register Types

| Register | Energy | Examples |
|---|---|---|
| **Social** | Medium-low | Negotiation, persuasion, faction politics, tavern encounters |
| **Exploratory** | Medium | Investigation, puzzle, dungeon navigation, discovery |
| **Combat** | High | Fights, chases, physical contests, escape sequences |
| **Revelation** | Variable | Plot twist, backstory reveal, mystery resolution, betrayal |

### Rhythm Rules

**Rule 1: Never repeat a register back-to-back.** Two combats in a row creates mechanical fatigue. Two social scenes in a row makes half the table check their phones. Alternate.

**Rule 2: Open high or low, not medium.** A combat or revelation Strong Start grabs attention. A social or exploratory start is fine if the table just had a combat-heavy session and needs decompression. Medium starts (exploration, investigation) risk feeling like the session hasn't begun.

**Rule 3: The climax doesn't have to be combat.** A social scene where the party confronts a betrayer can be the most intense moment of the session. A revelation that reframes everything they thought they knew can be the peak. Don't assume escalation = fighting.

**Rule 4: End on an up-note or a cliffhanger, never a plateau.** The last island should either resolve something satisfying (up-note) or reveal something that demands continuation (cliffhanger). Ending mid-investigation or mid-travel is a plateau — the players leave without momentum.

**Rule 5: The `[OPTIONAL]` island should be the most fun.** If you can't bear to skip it, it's not optional — redesign the session so it's mandatory and something else is optional. The optional island is your safety valve; it must be genuinely cuttable without the session feeling incomplete.

### Pacing Failure Modes

| Failure | Symptom at Table | Fix |
|---|---|---|
| **Escalation Fatigue** | Three high-tension islands in a row; players seem exhausted, not excited | Insert a low-energy breather between high-energy scenes. A short social beat, a travel moment, a comedic NPC. |
| **The Slow Middle** | Session opens strong, then two exploration islands drain momentum | Front-load one social-combat hybrid island after the Strong Start. Save pure exploration for the back half when players have context. |
| **Combat Slog** | A single combat eats 90 minutes; remaining islands are rushed | If an encounter will take 45+ minutes, it counts as 2 islands. Plan fewer other islands. Check § Encounter for streamlining. |
| **Revelation Overload** | Two major reveals in one session; players can't process either | **Max 1 major revelation per session.** If you have two, save one for next session. Players need time to react to revelations before the next one lands. |
| **The Orphan Ending** | Session runs out of time mid-island | Plan 3 mandatory islands, 1 optional. If time is short, cut the optional island and end on island 3's resolution. Don't start an island you can't finish. |

---

## Faction Off-Screen Actions

Factions don't pause while the party is busy. Every session, 1–2 factions should visibly advance their agenda.

### How to Write Off-Screen Actions

1. Read the faction's toy frontmatter fields — specifically `off_screen_action` and `primary_goal`
2. Advance the faction one logical step toward their goal
3. Make the evidence **observable but not explained** — the party sees the effect, not the cause

**Good:** *"Three more warehouses near the docks have been bought by anonymous buyers this week. The dock workers are nervous."* (Faction is consolidating control — party sees the effect.)

**Bad:** *"The Ironmantle faction has continued their plan to control the shipping lanes by purchasing dock property."* (This is narrator voice explaining faction mechanics. Players can't observe this.)

### Off-Screen Action Rules

- **1–2 factions per session.** More than 2 overwhelms the party's tracking capacity.
- **Advance the faction the party is NOT currently engaging.** The faction they're interacting with advances through play. The others advance off-screen.
- **Make evidence specific and physical.** Not "tensions are rising" but "three more soldiers arrived on the morning ferry."
- **Connect to an island when possible.** An NPC in an island might mention the off-screen change. This makes the world feel interconnected without dedicating a whole scene to it.
