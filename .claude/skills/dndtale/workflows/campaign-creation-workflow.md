# Campaign Creation Workflow

This workflow guides you through creating a complete D&D campaign from initial concept to ready-to-play content.

---

## Phase 1: Gathering Requirements

### Step 1: Collect Basic Information

**If the DM provides a briefing document**, extract:
- Story or plot hook
- Campaign length (one-shot, short arc, long campaign)
- Starting level and number of players
- World backdrop (classic D&D, custom, sci-fi, etc.)
- Tone and vibe

**If no briefing is provided**, or the briefing is missing critical information, use AskUserQuestion to gather:

```
Questions to ask:
1. What's your core concept or story idea?
   - Epic quest to stop an evil
   - Political intrigue
   - Dungeon crawl
   - Exploration-focused
   - Mystery investigation

2. How long should this campaign be?
   - One-shot (single session)
   - Short (3-5 sessions)
   - Medium (6-12 sessions)
   - Long (13+ sessions)

3. What's the player starting level and party size?
   - Level range: 1-20
   - Party size: typically 3-6 players

4. What's the setting/backdrop?
   - Classic D&D (Forgotten Realms, Greyhawk, etc.)
   - Homebrew fantasy world
   - Sci-fi or modern
   - Specific published setting

5. What's the tone?
   - Heroic & epic
   - Dark & serious
   - Humorous & lighthearted
   - Mystery & intrigue
   - Horror
   - Adult-themed/NSFW
```

**Use TodoWrite** to create a planning checklist:
- [ ] Gather requirements
- [ ] Choose campaign type
- [ ] Create campaign overview
- [ ] Design chapters
- [ ] Create a timeline of events in the chapters
- [ ] Detail NPCs
- [ ] Detail locations
- [ ] Create factions
- [ ] Write briefing document
- [ ] Quality check

### Step 2: Choose Campaign Type

Based on requirements, recommend a campaign type (see [modules/campaign-types.md](../modules/campaign-types.md)):

**For new DMs or tightly plotted stories:** Linear
**For experienced DMs or exploration:** Sandbox/Hub
**For political/time-sensitive plots:** Event-Based
**For dungeon crawls or mystery:** Setting-Based

**Ask the DM** if unsure which type fits best.

---

## Phase 2: Campaign Framework

### Step 3: Create Campaign Overview

Using [templates/campaign-overview.md](../templates/campaign-overview.md):

**3.1: Write Adventure Background**
- What happened before the campaign starts?
- What forces are in motion?
- What's the core conflict?

**3.2: Write Adventure Synopsis**
- High-level overview of the story
- Major story beats (Chapter 1, Chapter 2, Chapter 3)
- Key decision points

**3.3: Create Adventure Hooks**
- Primary hook that pulls characters in
- 2-3 alternate hooks for different character motivations
- Connection to broader world (if applicable)

**3.4: Plan Chapter Breakdown**
- How many chapters needed?
- What's the focus of each chapter?
- What level should characters be?

**Examples:**
- One-shot: 1 chapter, 4-6 hours
- Short campaign: 3-5 chapters
- Medium campaign: 6-12 chapters
- Long campaign: 13+ chapters

**3.5: Identify Key Elements**
- Major NPCs (at least 3-5)
- Key locations (at least 3-5)
- Factions (optional, but recommended for complexity)

### Step 4: Design Story Framework

Following [modules/world-building.md](../modules/world-building.md):

**4.1: Establish the Setting**
- Define boundaries (don't build the entire world)
- Create structured creative space
- Establish tone clearly

**4.2: Plan Major NPCs**
- Create 3-5 major NPCs:
  - At least one ally/quest giver
  - At least one antagonist/villain
  - Supporting characters

**4.3: Design Key Locations**
- Create 3-5 major locations:
  - Starting location
  - At least one dungeon/challenge location
  - Climax location
  - Supporting locations

**4.4: Develop Factions (optional)**
- For complex campaigns, create 2-4 factions
- Define their goals and conflicts
- Show how they interact with each other

---

## Phase 3: Detailed Development

### Step 5: Write Chapters

For each chapter, using [templates/chapter-template.md](../templates/chapter-template.md):

**5.1: Chapter Overview**
- Synopsis
- Objectives (primary, secondary, optional)
- Expected duration
- Time of the events in the chapter

**5.2: Break Into Scenes**
- Each chapter should have 3-5 scenes
- Each scene should have:
  - Read-aloud description
  - DM information
  - Possible player actions
  - Encounters or challenges
  - Connections to other scenes

**5.3: Design Encounters**
- Mix combat, social, and exploration encounters
- Ensure variety within each chapter
- Match difficulty to party level
- Provide multiple solutions

**5.4: Create Scene Climax**
- Each chapter should build to a meaningful moment
- Multiple resolution paths (combat, diplomacy, stealth)
- Consequences that matter

**5.5: Add Transitions**
- How does this chapter lead to the next?
- What hooks or cliffhangers set up future content?

**Pacing guideline:**
- 1 hour per scene
- 3-5 scenes per session
- Budget time for roleplay and player creativity

### Step 6: Detail NPCs

Using [templates/npcs.md](../templates/npcs.md):

**6.1: Major NPCs** (3-5)
- Full details: appearance, personality, motivations, secrets
- Stat blocks
- Roleplaying tips
- How they evolve through the campaign

**6.2: Supporting NPCs** (5-10)
- Condensed format
- Key information and quirks
- What they know and want

**6.3: Minor NPCs** (as needed)
- Quick reference table
- One memorable trait each

### Step 7: Detail Locations

Using [templates/locations.md](../templates/locations.md):

**7.1: Major Locations** (3-5)
- Full details: atmosphere, history, key features
- Sub-locations within
- NPCs present
- Secrets and encounters

**7.2: Supporting Locations** (5-10)
- Quick format
- Essential information
- What players can do there

**7.3: Travel & Maps**
- How locations connect
- Travel times
- Random encounters

### Step 8: Detail Factions (if applicable)

Using [templates/factions.md](../templates/factions.md):

**8.1: Create 2-4 Factions**
- Goals and motivations
- Leadership and structure
- Resources and activities
- Relationships with other factions

**8.2: Define Faction Dynamics**
- Conflicts between factions
- How party can influence them
- Quests and rewards

---

## Phase 4: Player-Facing Content

### Step 9: Write Briefing Document

Using [templates/README.md](../templates/README.md):

**9.1: Campaign Overview**
- Spoiler-free description
- Essential information (level, length, tone)

**9.2: Setting Information**
- What characters living in this world would know
- Recent events
- Common knowledge

**9.3: Character Creation Guidelines**
- Allowed content
- Ability score method
- Character concept guidance

**9.4: Session Zero Topics**
- Table rules
- Content warnings and boundaries
- Safety tools
- Playstyle preferences

**IMPORTANT:** No spoilers! Only include information players should know before starting.

---

## Phase 5: Polish & Enhancement

### Step 10: Create Image Prompts

For key locations, NPCs, and scenes:

**10.1: Identify Visual Moments**
- Opening scenes
- Important locations
- Major NPCs
- Climactic encounters

**10.2: Write Prompts**
- Based on read-aloud descriptions
- Include style guidance
- Specify mood and atmosphere

**Format:**
```markdown
---
title: filename
aspect_ratio: "16:9"
resolution: 2K
instructions: style-file.md
---

Detailed visual description based on scene...
```

### Step 11: Add Supporting Materials

**11.1: Handouts** (optional)
- Letters, clues, maps players find
- In-world documents

**11.2: Custom Content** (optional)
- Magic items
- Monster stat blocks
- Homebrew rules

**11.3: Random Tables** (optional)
- Random encounters
- Random NPCs
- Treasure tables

Using [templates/timeline.md](../templates/timeline.md):

**11.4: Timeline**
- Sequential timeline of events in the campaign, ordered by chapter and scene
- List of important events and their time the DM should know about

---

## Phase 6: Quality Assurance

### Step 12: Quality Check

Use [checklists/campaign-quality-checklist.md](../checklists/campaign-quality-checklist.md):

**12.1: Completeness Check**
- All chapters written
- All NPCs detailed
- All locations described
- Briefing document complete

**12.2: Consistency Check**
- Names consistent throughout
- Timeline makes sense
- NPCs and locations appear where stated
- Cross-references correct

**12.3: Balance Check**
- Encounters appropriate for level
- Variety in challenge types
- Pacing feels right

**12.4: Story Check**
- Clear hooks and motivations
- Multiple resolution paths
- Player agency preserved
- Consequences matter

### Step 13: Final Review

**13.1: Read-Through**
- Read the entire campaign as a DM would use it
- Check for clarity and usability at the table

**13.2: Cross-References**
- Ensure all links between documents work
- Check all references to other sections

**13.3: DM Notes**
- Add any missing tips or guidance
- Include common pitfalls and solutions

**13.4: Timeline**
- Verify the timeline and update timeline.md if there are inconsistencies

---

## Phase 7: Delivery

### Step 14: Organize Files

Ensure proper structure:

```
campaigns/[campaign-name]/
├── campaign-overview.md
├── README.md
├── chapter-01.md
├── chapter-02.md
├── [additional chapters]
├── chapters-summary.md
├── npcs.md
├── locations.md
├── factions.md
├── art/
│   ├── [image-prompts].md
│   └── [generated images]
└── [optional additional files]
```

### Step 15: Summary

Provide the DM with:
- Location of all files
- Overview of what was created
- Recommended next steps
- How to use the campaign

---

## Tips for Efficient Workflow

### Time Management

**Phase 1-2 (Framework):** 20% of time
- Get this right; everything builds on it

**Phase 3 (Details):** 50% of time
- Most labor-intensive
- Can be done incrementally

**Phase 4-5 (Polish):** 20% of time
- Don't skip this; makes campaign usable

**Phase 6-7 (QA & Delivery):** 10% of time
- Final touches matter

### Iterative Development

**Don't try to perfect everything at once:**
1. Complete framework (Phases 1-2)
2. Write first chapter in detail
3. Get DM feedback
4. Adjust approach for remaining chapters
5. Detail remaining chapters
6. Polish and quality check

### Use Todo List

Track progress with TodoWrite:
```
[ ] Requirements gathered
[ ] Campaign type chosen
[ ] Campaign overview complete
[ ] Chapter 1 complete
[ ] Chapter 2 complete
[...continue for all chapters]
[ ] NPCs detailed
[ ] Locations detailed
[ ] Factions detailed
[ ] Briefing written
[ ] Quality check passed
```

### Ask Questions

Don't hesitate to use AskUserQuestion when:
- Requirements are unclear
- Multiple valid approaches exist
- DM preference matters
- Ambiguity in the story

### Stay Focused

**Do:**
- Follow the templates
- Maintain consistency
- Think about usability at the table
- Provide multiple solutions

**Don't:**
- Over-detail minor NPCs or locations
- Write railroad plots
- Create content that will never be used
- Forget player agency
