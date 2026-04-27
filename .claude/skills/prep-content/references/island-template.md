---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
# Narrative Island Template

Use this structure for every island in a session prep document.

---

## Template

```markdown
### Island {N} — {Entity Name} *({Location})* {[OPTIONAL] if applicable}

*Register: {social | exploratory | combat | revelation | hybrid}*

*Reskin: {What scene structure this is — reusable pattern for any session where [condition].}*

*{DM-facing brief — 2–3 sentences: what the party walks into, what the NPC/situation wants, what happens if the party does nothing. The default outcome is the most important sentence — it tells you what the scene is about.}*

> [!secret]
> *{What isn't visible. What the NPC withholds. The hidden mechanic, the secret motive, the thing that makes this scene interesting once revealed. This is your improv fuel — when the scene stalls, crack this open.}*

**Opening (read aloud):**
> {Mercer-voice narration. Sensory. Present tense. Second person. 2–4 sentences max. First sentence establishes space; second establishes the wrong thing — the detail that signals something is off.}

**{NPC Name}**: *"{Opening line — the first thing they say. Must reveal their Active Problem or Consistent Method in subtext. Not exposition.}"*

**If the party pushes back:** {What the NPC concedes, escalates, or reveals under pressure. Not a script — a behavioral rule.}

**If the party ignores this:** {What changes in the world. This must be observable later — another NPC mentions it, evidence appears, or it escalates into a future session's Strong Start.}
```

---

## What Makes a Good Island

An island is a **situation with a ticking clock and a dramatic question the party answers through play.** Not a meeting. Not an errand. Not "go here, get info."

**The diagnostic:** Can you state the dramatic question in one sentence?
- YES → it's an island. *"Will the party side with the smuggler or the harbor master?"*
- NO → it's a task, an errand, or an info dump disguised as a scene. Rework it.

**Every island needs:**
1. An entity at the center with an `active_problem` from their toy frontmatter fields
2. A pressure that will resolve itself if the party doesn't intervene
3. At least one PC whose backstory makes this personal
4. A default outcome the GM can narrate if the party never shows up

---

## Good Island vs. Bad Island

**Bad:**
> Island 2 — Captain Voss *(The Docks)*
> The party meets Captain Voss, who tells them about the smuggling operation and asks for help.

Why it fails: No pressure. No dramatic question. No default outcome. Voss is a quest-giver, not a character in a volatile situation. The party can say "no thanks" and nothing changes.

**Good:**
> Island 2 — Captain Voss *(The Docks)* [OPTIONAL]
> *Register: social*
> Voss is loading contraband onto the Lasting Insult in broad daylight — the harbor master's inspectors are 20 minutes away. She needs crew to help move crates or a distraction to buy time. If ignored, Voss gets caught, loses her ship, and blames whoever she thinks tipped off the inspectors — which might be the party.

Why it works: Voss has a problem happening *right now*. The party can help, hinder, exploit, or ignore — and each choice has consequences. The default outcome feeds future sessions.

---

## Island Failure Modes

These kill scenes at the table. Check every island against this list.

| Failure Mode | Symptom | Fix |
|---|---|---|
| **The Info Dump** | NPC explains lore for 5 minutes, party listens | Give the NPC a problem that forces the party to act *before* they get the info. Info is the reward, not the scene. |
| **The Skill Gate** | One Persuasion check determines everything | Layer the scene: the check opens a door, but behind it is a *new* choice. Multiple paths to the same dramatic question. |
| **The No-Stakes Meeting** | NPC wants to talk, nothing bad happens if party says no | Add a ticking clock or a competing interest. Someone else wants the same thing the NPC is offering. |
| **The Railroad** | Only one outcome is prepped, party must reach it | Write the default outcome (party ignores it) as a complete scene. If you can't imagine the party not doing this, you've written a railroad. |
| **The Dead NPC** | NPC has no Active Problem, just information to deliver | Look up their toy frontmatter fields. If they don't have any, they're not an island — they're set dressing. Wire them to a pressure or cut the island. |
| **The Double Register** | Two islands in a row with the same vibe (two combats, two negotiations) | Alternate registers. If the last island was social, make this one exploratory or combat. Rhythm prevents fatigue. |
