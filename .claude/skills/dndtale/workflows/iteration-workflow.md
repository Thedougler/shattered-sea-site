# Campaign Iteration & Refinement Workflow

This workflow guides you through refining, updating, or expanding an existing campaign based on DM feedback or changing needs.

---

## When to Use This Workflow

Use this when:
- DM wants to refine existing content
- Campaign needs adjustment based on playtesting
- Players took unexpected paths
- DM wants to expand or add content
- Content needs updating for consistency

---

## Phase 1: Understand the Change Request

### Step 1: Identify the Type of Change

**Content Addition:**
- New chapter/session
- New NPC
- New location
- New faction
- New subplot or story arc

**Content Refinement:**
- Improve existing chapter
- Add more detail to NPC
- Expand location description
- Enhance encounter design

**Content Adjustment:**
- Change difficulty
- Adjust pacing
- Modify story direction
- Fix inconsistencies

**Player-Driven Changes:**
- Adapt to unexpected player actions
- Account for character death
- Incorporate player backstories
- Follow up on player decisions

### Step 2: Read Existing Content

**Before making changes:**

**2.1: Read Campaign Overview**
- Understand the overall story framework
- Note major themes and tone
- Identify key story beats

**2.2: Read Relevant Chapters**
- What comes before the change?
- What comes after?
- How does this connect to the overall story?

**2.3: Review Related NPCs, Locations, Factions**
- Who's involved?
- Where does this take place?
- What factions are affected?

**2.4: Check for Dependencies**
- What other content references this?
- What references other content?
- What would break if this changes?

### Step 3: Validate Consistency

Before proceeding, ensure you understand:
- The campaign's tone and style
- Existing naming conventions
- Story logic and timeline
- NPC motivations and relationships
- Faction dynamics
- World rules and boundaries

---

## Phase 2: Plan the Change

### Step 4: Design the Solution

**4.1: Clarify the Goal**
- What specifically needs to change?
- Why is this change needed?
- What's the desired outcome?

**4.2: Identify Impact**
- What files need to be edited?
- What cross-references need updating?
- What might break?
- What new content is needed?

**4.3: Plan the Approach**

**For Additions:**
1. Decide where new content fits
2. Plan connections to existing content
3. Identify what to reference vs. create new

**For Refinements:**
1. What's working and should be preserved?
2. What needs improvement?
3. How to enhance without breaking existing content?

**For Adjustments:**
1. What's the minimum change needed?
2. How to maintain story consistency?
3. What downstream effects will occur?

### Step 5: Use AskUserQuestion if Needed

Ask the DM when:
- Multiple valid approaches exist
- Change might affect player experience significantly
- Unclear how much to preserve vs. change
- Need to know what happened in actual play

**Example questions:**
- "Should I preserve the existing NPC personality or redesign them?"
- "Do you want me to adjust just this chapter or future chapters too?"
- "How did the players react to X? Should I account for that?"

---

## Phase 3: Implement Changes

### Step 6: Make Targeted Edits

**6.1: Use Edit Tool for Existing Files**
- Read the file first
- Make precise, targeted changes
- Preserve formatting and style
- Maintain cross-references

**6.2: Create New Files if Needed**
- Use appropriate templates
- Match existing style and format
- Follow naming conventions

**6.3: Update Cross-References**
- If adding content, link to it from relevant locations
- If changing content, update references
- If removing content, remove dead links

**6.4: Document changes**
- Create a new markdown document in folder ./changelog
- Document all changes made to the campaign

### Step 7: Preserve Story Logic

**While editing, ensure:**

**7.1: Timeline Consistency**
- Events happen in logical order
- Time passing makes sense
- No contradictions in "when" things occur

**7.2: NPC Consistency**
- Characters act according to their motivations
- Relationships remain logical
- Character knowledge is consistent (they know what they should know)

**7.3: Location Consistency**
- Geographic relationships make sense
- Travel times remain consistent
- Locations don't contradict each other

**7.4: Faction Consistency**
- Faction goals remain coherent
- Relationships between factions stay logical
- Actions align with faction values

**7.5: Tone Consistency**
- Changes match the campaign's tone
- Style remains consistent
- Level of detail matches existing content

---

## Phase 4: Expand and Enhance

### Step 8: Add Related Content

**When adding new content, consider:**

**8.1: NPCs**
- Does this change introduce new NPCs?
- Do existing NPCs need updates?
- Add to npcs.md if significant

**8.2: Locations**
- New locations needed?
- Existing locations affected?
- Add to locations.md if important

**8.3: Factions**
- Do factions react to this change?
- New faction alliances or conflicts?
- Update factions.md if relevant

**8.4: Consequences**
- How does this change ripple through the campaign?
- What future chapters are affected?
- Update campaign-overview.md if story changes

### Step 9: Add Image Prompts

**For new significant content:**
- Create image prompts for new locations
- Create prompts for new major NPCs
- Create prompts for new important scenes

---

## Phase 5: Quality Assurance

### Step 10: Check Consistency

Use [checklists/consistency-checklist.md](../checklists/consistency-checklist.md):

**10.1: Cross-Reference Check**
- All internal links work
- References to NPCs/locations/chapters are correct
- No broken references to removed content

**10.2: Name Consistency**
- Names spelled consistently
- Titles and roles consistent
- No accidental name changes

**10.3: Story Logic**
- Timeline makes sense
- Character motivations remain coherent
- No plot holes introduced

**10.4: Mechanical Consistency**
- DCs remain appropriate for level
- Stat blocks correct
- Treasure and rewards balanced

### Step 11: Integration Check

**11.1: Read Before and After**
- Read the chapter/section before the change
- Read the changed content
- Read the chapter/section after the change
- Ensure smooth flow

**11.2: Check Impact on Overall Story**
- Does the change support the main story?
- Are themes still coherent?
- Does the climax still make sense?

### Step 12: Document Changes

**If significant changes were made:**

Add a DM note documenting what changed and why:

```markdown
---
**📝 DM Note - Updated [Date]**

**Changes Made:**
- [What was changed]
- [Why it was changed]
- [What to watch for in future sessions]

---
```

---

## Common Iteration Scenarios

### Scenario 1: Player Took Unexpected Path

**Situation:** Players went somewhere or did something unexpected.

**Workflow:**
1. Understand what players did
2. Identify what content is now needed
3. Create new content for the unexpected path
4. Add alternative connections from existing content
5. Update campaign overview if story significantly changed

**Example:**
- Players skipped Chapter 2 and went straight to Chapter 3
- Create a new way for Chapter 1 to connect to Chapter 3
- Move important info/items from Chapter 2 to Chapter 3
- Update NPCs' knowledge (they don't know what happened in Ch 2)

### Scenario 2: Key NPC Died

**Situation:** An important NPC died unexpectedly.

**Workflow:**
1. Check where this NPC appears in future chapters
2. Decide: Replace with new NPC or redistribute their role?
3. Update all references to this NPC
4. Add consequences to the story
5. Update faction dynamics if applicable

**Example:**
- Quest-giver NPC died in combat
- Option A: Introduce their assistant/heir who takes over
- Option B: Redistribute quests to other NPCs
- Add funeral/consequences to show NPC death mattered

### Scenario 3: DM Wants to Add Subplot

**Situation:** DM wants to add a new story thread.

**Workflow:**
1. Clarify the subplot's purpose and connection to main story
2. Identify where to introduce it
3. Plan 2-3 scenes across multiple chapters
4. Create related NPCs/locations if needed
5. Add hooks in existing chapters
6. Plan resolution

**Example:**
- Adding a romance subplot
- Introduce NPC in Chapter 2
- Add interactions in Chapters 3, 5, 7
- Create meaningful choice in Chapter 8
- Resolve in Chapter 9 or ongoing

### Scenario 4: Difficulty Adjustment

**Situation:** Content is too easy or too hard.

**Workflow:**
1. Identify specific encounters that need adjustment
2. Modify enemy numbers or stats
3. Adjust DCs for skill challenges
4. Add or remove environmental hazards
5. Update tactical notes for DM

**Don't:** Change the story to fix difficulty
**Do:** Change mechanical elements only

### Scenario 5: Incorporating Player Backstory

**Situation:** DM wants to tie in a player's backstory.

**Workflow:**
1. Understand the player's backstory
2. Find natural connection points in the campaign
3. Create or modify an NPC related to backstory
4. Add a scene or side quest
5. Connect to main story if possible

**Example:**
- Player's backstory includes a missing sibling
- Create NPC sibling who appears in Chapter 5
- Sibling has information relevant to main plot
- Add personal stake to the climax

### Scenario 6: Expanding Existing Content

**Situation:** DM wants more detail or options.

**Workflow:**
1. Read existing content carefully
2. Identify what to expand (more encounters, more NPCs, more paths)
3. Add new content that enhances, doesn't replace
4. Maintain existing structure and flow
5. Add "optional" labels so DM knows what's required vs. bonus

**Example:**
- Chapter has one path through dungeon
- Add alternative routes
- Add optional encounters
- Add secret areas with extra loot
- Mark clearly which are required vs. optional

---

## Best Practices for Iteration

### Do:
- **Preserve what works** - Don't change things unnecessarily
- **Maintain consistency** - Match existing style and tone
- **Think holistically** - Consider ripple effects
- **Document changes** - Help DM track what's different
- **Test logic** - Make sure story still makes sense

### Don't:
- **Break existing content** - Changes shouldn't invalidate other chapters
- **Change tone** - Stay consistent with campaign style
- **Over-complicate** - Simple solutions are often best
- **Ignore dependencies** - Update all references
- **Forget player agency** - Keep multiple paths available

### When to Use Edit vs. Write

**Use Edit when:**
- Modifying existing files
- Making targeted changes
- Preserving most of the content
- Updating specific sections

**Use Write when:**
- Creating entirely new chapters/content
- The change is so extensive a rewrite is easier
- Creating new supporting files

### Track Your Changes

Use TodoWrite for complex iterations:

```
[ ] Read all affected files
[ ] Identify all changes needed
[ ] Edit Chapter 3
[ ] Update NPC references in npcs.md
[ ] Update location references in locations.md
[ ] Add new connections to campaign-overview.md
[ ] Check consistency
[ ] Update cross-references
```

---

## Emergency Fixes

### Quick Fixes Between Sessions

**When the DM needs something fast:**

1. **Identify the immediate need**
2. **Make minimum viable change**
3. **Note what still needs doing**
4. **Follow up with proper iteration later**

**Example:**
- Session tonight, players did unexpected thing
- Quick: Add basic content for what they'll encounter
- Later: Properly integrate into campaign, update all references

### Recovering from Mistakes

**If you notice an error in previous content:**

1. **Assess impact**
   - How many sessions has this been wrong?
   - What has it affected?
   - Can it be retconned?

2. **Fix forward if possible**
   - Make the "error" intentional
   - Add explanation that makes it make sense
   - Better than retconning if possible

3. **If retcon necessary**
   - Fix all affected files
   - Add DM note explaining what to retcon
   - Provide suggested explanation to players
