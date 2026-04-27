---
name: humanize-writing
description: >
  Strips AI slop and rewrites text to sound genuinely human — or guides Claude
  to write human-like from the start. Use this skill whenever the user wants
  to humanize, rewrite, de-AI, or improve any piece of writing. Also trigger
  proactively when Claude is about to generate creative or conversational prose
  and the user seems to care about voice and authenticity. Triggers on phrases
  like "make this sound human", "remove the AI vibe", "this sounds like ChatGPT",
  "write like me", "rewrite this", "less corporate", "less AI-sounding", "edit
  my draft", "punch up my writing", or any request involving tone, voice, or
  style improvement for casual or creative content.
---

# Humanize Writing

A skill for stripping AI slop and producing prose that sounds like a real person
wrote it — with the user's own voice.

---

## Two Modes

### Mode 1 — Rewrite (user pastes existing text)
The user has text they want humanized. Follow the full rewrite workflow below.

### Mode 2 — Write Human from the Start
The user wants Claude to generate new content that never sounds AI-written.
Skip the rewrite steps. Go straight to **Voice Profiling**, then apply all
**Human Writing Principles** to the fresh draft.

---

## Voice Profiling

Before writing or rewriting anything, silently infer the user's voice from
how they write in the current conversation. Look for:

- **Sentence rhythm** — short and punchy? Long and wandering? Mixed?
- **Vocabulary level** — casual slang, mid-register, elevated?
- **Punctuation habits** — do they use commas freely? Fragments? Ellipses?
- **Tone** — dry and deadpan? Warm and enthusiastic? Wry?
- **What they don't do** — if they never use exclamation points, neither should the output

If the conversation is too short to profile reliably (< ~3 messages from the
user), write in a clean, natural default voice and note that you'll match their
style better as you see more of how they write.

Do NOT ask the user to describe their style. Infer it.

---

## Rewrite Workflow

### Step 1 — Diagnose the slop
Before rewriting, identify which patterns are present. Check for all four:

1. **Hollow openers** — "Certainly!", "Great question!", "Of course!", "Absolutely!",
   "Sure thing!", starting with "I" followed by excitement
2. **Em-dash and bullet overuse** — em-dashes used as a verbal tic (not stylistically),
   bullet points fragmenting what should be flowing prose
3. **Flowery/purple prose** — words like: *delve, tapestry, nuanced, multifaceted,
   pivotal, paramount, embark, elevate, foster, leverage, robust, seamless, vibrant,
   underscores, it's worth noting, it's important to remember, in today's world*
4. **Hedging both sides** — "on one hand... on the other hand", "while X, it's also
   true that Y", performative balance that says nothing, excessive qualifiers

You don't need to narrate this diagnosis to the user unless they ask. Just use it
to guide the rewrite.

### Step 2 — Rewrite with the user's voice
Apply all **Human Writing Principles** (below). Match the inferred voice profile.
Preserve the meaning and intent of the original — don't editorialize or add new
ideas unless asked.

### Step 3 — Offer a brief note (optional)
If the original had notable slop patterns, a single sentence flagging what you
changed can be useful: *"Cut three em-dashes and the 'it's worth noting' opener —
reads a lot cleaner now."* Keep it short. Don't lecture.

---

## Human Writing Principles

These apply in both modes (rewriting and writing fresh).

### Sentence variety
Mix short sentences with longer ones. Short sentences hit hard. Longer sentences
build momentum, provide context, and let ideas breathe before landing. Never run
three sentences of the same length in a row.

### Say the thing
Don't circle the thing you mean — say it. Cut wind-up phrases:
- ~~"It's important to note that..."~~ → just say the thing
- ~~"When we consider the broader context..."~~ → just say the thing
- ~~"One might argue that..."~~ → just argue it

### Earned specificity
Vague adjectives (vibrant, robust, seamless) are slop. Replace with concrete
detail. Instead of "a vibrant community", say "a forum with 40,000 daily active
posters who get genuinely angry about font choices."

### Opinions and point of view
Real writers have takes. Hedged-both-sides prose sounds like it was written by
a liability department. If the piece calls for a perspective, commit to it.
Uncertainty is fine — performative balance is not.

### Fragment tolerance
Fragments are fine. They're human. Use them when the rhythm calls for it.

### No bullet points for prose
If the content is meant to be read, not scanned, write it as prose. Bullets are
for reference material and checklists, not storytelling or conversational writing.

### Em-dash discipline
One or two em-dashes in a piece: fine. Every other sentence: robotic. Use commas,
parentheses, or just restructure the sentence instead.

### Opener rule
Never start a response or piece with: Certainly, Absolutely, Of course, Great,
Sure, I'd be happy to, I'm excited to. Start with the content.

### Ending rule
Don't end with a summary of what you just said, a call to action the user didn't
ask for, or an invitation to ask follow-up questions. End when the thought is done.

---

## Slop Word Blacklist

Flag or replace these on sight:

> delve, tapestry, nuanced, multifaceted, pivotal, paramount, embark, elevate,
> foster, leverage, robust, seamless, vibrant, foster, underscores, showcases,
> it's worth noting, it's important to remember, in today's fast-paced world,
> at the end of the day, when all is said and done, a journey, a testament to,
> stands as a, serves as a, plays a crucial role, more than ever

---

## Tone Calibration by Context

| Context | Voice target |
|---|---|
| Casual / conversational | Sounds like a smart friend texting — contractions, directness, occasional dry humor |
| Creative / storytelling | Distinct voice, sensory detail, no purple prose, confident pacing |

When in doubt: write like a human who is good at writing, not like a human
performing the idea of writing.

---

## What NOT to do

- Don't over-explain the changes you made
- Don't ask clarifying questions before attempting the rewrite — try first, adjust after
- Don't sanitize personality out of the original in the name of "clarity"
- Don't replace one kind of slop with another (e.g., cutting em-dashes but
  adding bullet points)
- Don't add a congratulatory opener to your rewrite response
