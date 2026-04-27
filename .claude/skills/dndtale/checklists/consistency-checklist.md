# Consistency Checklist

Use this checklist when iterating on or updating existing campaign content to ensure nothing breaks.

---

## Before Making Changes

### Read and Understand

- [ ] Read campaign-overview.md to understand the full story
- [ ] Read all chapters that might be affected by this change
- [ ] Read relevant NPC, location, and faction documents
- [ ] Note all mentions of content you're changing
- [ ] Understand dependencies and connections

### Document Current State

- [ ] Note what's about to change
- [ ] List all files that reference this content
- [ ] Identify potential ripple effects
- [ ] Create backup if making major changes

---

## During Changes

### Name Consistency

- [ ] Use exact same spelling for character names
- [ ] Use exact same spelling for location names
- [ ] Use exact same spelling for faction names
- [ ] Be consistent with titles (Captain Smith vs. Smith the Captain)
- [ ] Be consistent with epithets (The Red Wizard vs. Red Wizard Tharn)

**Quick Test:** Search for the name in all documents. Every instance should be spelled identically.

### Number Consistency

- [ ] Chapter numbers match file names and references
- [ ] NPC ages don't change between documents
- [ ] Distances and travel times remain consistent
- [ ] Dates and timeline remain consistent
- [ ] DCs for the same task remain consistent

### Reference Consistency

When mentioning NPCs:
- [ ] Description matches npcs.md
- [ ] Personality traits match across documents
- [ ] Relationships match across documents
- [ ] Location matches where they're stated to be

When mentioning locations:
- [ ] Description matches locations.md
- [ ] Features match across documents
- [ ] Geographic relationships remain consistent

When mentioning factions:
- [ ] Goals match factions.md
- [ ] Relationships match across documents
- [ ] Activities align with faction goals

---

## Timeline Consistency

### Event Order

- [ ] Events happen in logical chronological order
- [ ] "Before" events actually happen before
- [ ] "After" events actually happen after
- [ ] "At the same time" events are possible if there are multiple storylines
- [ ] No circular time dependencies or causal loops
- [ ] Avoid time-travel paradoxes like the 'Grandfather Paradox'

### Knowledge Consistency

For each NPC, check:
- [ ] They know things they've learned or witnessed
- [ ] They don't know things they haven't learned yet
- [ ] Information spreads logically
- [ ] Secrets remain secret until revealed

**Example Timeline Issues:**
- ❌ NPC mentions event that hasn't happened yet
- ❌ Character knows secret they weren't told
- ❌ Players learn information before it's revealed
- ✅ NPCs learn about events that already happened
- ✅ News spreads from location to location over time

### Time Passing

- [ ] Travel time consistent with distances
- [ ] Events take reasonable amount of time
- [ ] Actions take reasonable amount of time
- [ ] No impossible timing (can't be in two places at once)
- [ ] Seasons change appropriately
- [ ] Age references remain consistent

---

## Story Logic Consistency

### Cause and Effect

- [ ] Effects have causes
- [ ] Causes produce logical effects
- [ ] No events without explanation
- [ ] No missing links in causal chain

**Test:** For each major event, ask "Why did this happen?" and "What happens because of this?"

### Character Motivations

- [ ] NPCs act according to their stated motivations
- [ ] Behavior changes have explanations
- [ ] Goals remain consistent or evolve logically
- [ ] Contradictory actions are explained

**Red Flags:**
- Character suddenly acts against their motivation
- Character makes decision that doesn't fit their personality
- Character forgets their goals
- Character's beliefs change without explanation

### Faction Consistency

- [ ] Factions pursue stated goals
- [ ] Faction actions align with values
- [ ] Faction resources match activities
- [ ] Relationships between factions remain logical

**Example Issues:**
- ❌ Good faction commits evil acts without reason
- ❌ Poor faction suddenly has unlimited resources
- ❌ Allied factions working against each other
- ✅ Faction behavior matches stated goals
- ✅ Faction evolution explained by events

---

## Geographic Consistency

### Spatial Relationships

- [ ] Locations have consistent relative positions
- [ ] "North of X" remains north of X
- [ ] Travel routes make sense
- [ ] Distances remain consistent

### Travel Consistency

- [ ] Same journey takes same time
- [ ] Faster methods (horse, teleport) take less time
- [ ] Travel times scale with distance
- [ ] Terrain affects travel time consistently

**Create Reference Table:**

| From | To | Distance | Time (foot) | Time (horse) |
|------|-----|----------|-------------|--------------|
| A | B | 50 mi | 3 days | 1 day |
| A | C | 25 mi | 1.5 days | 12 hours |

### Environmental Consistency

- [ ] Climate appropriate for location
- [ ] Terrain matches descriptions
- [ ] Natural features (rivers, mountains) don't move
- [ ] Weather patterns make sense for climate

---

## Mechanical Consistency

### Stat Blocks

- [ ] Same creature has same stats in all encounters
- [ ] Modified versions noted as such
- [ ] References to books are accurate
- [ ] Custom creatures balanced consistently

### DCs and Difficulty

- [ ] Similar tasks have similar DCs
- [ ] DC doesn't change for same task
- [ ] Difficulty scales with level appropriately
- [ ] No sudden jumps in difficulty

**DC Reference:**
- Picking the same lock: Always same DC
- Persuading the same NPC: DC may change based on circumstances, but base difficulty consistent
- Similar challenges at same level: Similar DCs

### Rewards and Treasure

- [ ] Treasure value appropriate for level
- [ ] Similar challenges provide similar rewards
- [ ] No duplicate unique items
- [ ] Magic item rarity consistent

---

## Cross-Reference Consistency

### Document Links

- [ ] All markdown links point to correct files
- [ ] All section links (#anchors) work
- [ ] No broken links to removed content
- [ ] References to "Chapter X" have correct chapter number
- [ ] All artwork links have a matching prompt markdown file

### Content References

When a document says an NPC appears somewhere:
- [ ] That NPC actually appears there
- [ ] The NPC's role matches the description
- [ ] The timing works out

When a document says something happens:
- [ ] It actually happens in that chapter
- [ ] It happens when stated
- [ ] Prerequisites are met

### Quick Cross-Reference Test

For each important element:
1. Find all mentions in all documents
2. Verify each mention is accurate
3. Check that descriptions match
4. Ensure no contradictions

---

## Formatting Consistency

### Style Consistency

- [ ] Headers follow same pattern
- [ ] Blockquotes used consistently for read-aloud text
- [ ] Code blocks used consistently for stat blocks
- [ ] Tables formatted similarly

### Naming Convention Consistency

- [ ] File names follow pattern: chapter-01.md, chapter-02.md, etc.
- [ ] Section headers follow same capitalization
- [ ] Lists formatted consistently (all bullets or all numbers)

### Voice and Tone

- [ ] Same narrative voice throughout
- [ ] Tone matches campaign style
- [ ] Level of formality consistent
- [ ] Present vs past tense used consistently

---

## After Making Changes

### Immediate Verification

- [ ] Re-read what you changed
- [ ] Check surrounding content still makes sense
- [ ] Verify you updated all references to changed content
- [ ] Test any links you added or modified

### Ripple Effect Check

For each change, ask:
- [ ] What else references this?
- [ ] What does this reference?
- [ ] What happens before this?
- [ ] What happens after this?
- [ ] Do any of those need updates?

### Full Document Scan

- [ ] Search for name/term you changed across all files
- [ ] Verify each instance is correct
- [ ] Update any that reference old state
- [ ] Check for orphaned references

---

## Common Consistency Problems

### Problem: NPC Name Variations

**Example:** "Theron Darkblade" / "Theron" / "Lord Darkblade" / "The Dark Lord"

**Fix:**
- Choose one primary name: "Theron Darkblade"
- Use it consistently in narration and NPCs.md
- Other NPCs can call him by title or nickname, but be consistent
- Search/replace to fix inconsistencies

### Problem: Changing Timeline

**Example:** Added new chapter between existing chapters, now references are wrong

**Fix:**
- Update all chapter numbers in cross-references
- Update campaign-overview.md chapter list
- Check that timeline still flows correctly
- Verify NPC knowledge still makes sense

### Problem: Contradictory Descriptions

**Example:** Location described as "bustling city" in one place, "quiet town" in another

**Fix:**
- Decide which is correct
- Update all descriptions to match
- If both can be true (change over time), explain the change

### Problem: Impossible Geography

**Example:** Town A is north of B in one chapter, south of B in another

**Fix:**
- Create a simple map or list of relative positions
- Verify all references match
- Update incorrect references
- Add map to locations.md as reference

### Problem: Character Knowledge Errors

**Example:** NPC knows something they shouldn't know yet

**Fix:**
- Check when they could have learned it
- Either: Add scene where they learn it
- Or: Remove reference to knowledge
- Or: Change what they know to something appropriate

### Problem: Broken Motivation

**Example:** NPC suddenly acts against their goals without explanation

**Fix:**
- Add explanation for behavior change
- Or: Modify the action to align with motivation
- Or: Reveal this was secretly their goal all along (double agent, etc.)

---

## Consistency Audit Workflow

Use this workflow for major updates:

### 1. Create Change Log
Document what you're changing and why. Create a document in ./chagelog for this.

### 2. Map Dependencies
List all content that might be affected

### 3. Make Changes
Update primary content

### 4. Update References
Fix all references to changed content

### 5. Verify Consistency
Go through this checklist

### 6. Read-Through Test
Read affected sections to ensure flow

### 7. Mark as Reviewed
Add note that consistency was checked

---

## Quick Reference: Where to Check

When you change:

### An NPC:
- [ ] npcs.md
- [ ] All chapters where they appear
- [ ] campaign-overview.md (key NPCs section)
- [ ] factions.md (if they're faction member)
- [ ] locations.md (if they're associated with location)
- [ ] art/npc-name.md if description changed

### A Location:
- [ ] locations.md
- [ ] All chapters where it appears
- [ ] campaign-overview.md (key locations section)
- [ ] Other locations (for travel times, connections)
- [ ] npcs.md (if NPCs are stationed there)
- [ ] art/location-name.md if description changed

### A Chapter:
- [ ] The chapter file itself
- [ ] campaign-overview.md (chapter list)
- [ ] Previous chapter (transition)
- [ ] Next chapter (assumed knowledge)
- [ ] npcs.md (if introducing new NPCs)
- [ ] locations.md (if introducing new locations)

### A Faction:
- [ ] factions.md
- [ ] All chapters where they appear
- [ ] npcs.md (faction members)
- [ ] locations.md (faction holdings)
- [ ] Other factions (relationships)

### Timeline/Events:
- [ ] All affected chapters
- [ ] campaign-overview.md
- [ ] NPC knowledge in npcs.md
- [ ] Faction activities in factions.md
- [ ] Location states in locations.md

---

## Emergency Consistency Fixes

If you discover inconsistency that's already been played:

### Option 1: Retcon
- Fix all instances to be consistent
- Provide DM with explanation for players
- Update all documents

### Option 2: Fix Forward
- Leave past as-is
- Make the inconsistency make sense
- Add explanation (it was a disguise, misinformation, magic, etc.)
- Update going forward

### Option 3: Ignore
- If the inconsistency is minor and no one noticed
- If fixing would cause more problems
- Note it for your own reference but don't change

**When in doubt, fix forward rather than retcon.**
