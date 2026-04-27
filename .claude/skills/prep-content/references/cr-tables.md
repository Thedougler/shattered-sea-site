---
type: note
created: "2026-04-23"
updated: "2026-04-23"
---
# CR Reference Tables

## Monster Statistics by Challenge Rating

This is the canonical table for balancing monster stat blocks. Use it in conjunction with the CR calculation in SKILL.md.

| CR | XP | Prof Bonus | AC | HP (Low) | HP (High) | Attack Bonus | Save DC | DPR (Low) | DPR (High) |
|----|-----|------------|----|----|----|----|----|----|-----|
| 0 | 0–10 | +2 | ≤13 | 1 | 6 | +3 | 13 | 0 | 1 |
| 1/8 | 25 | +2 | 13 | 7 | 35 | +3 | 13 | 2 | 3 |
| 1/4 | 50 | +2 | 13 | 36 | 49 | +3 | 13 | 4 | 5 |
| 1/2 | 100 | +2 | 13 | 50 | 70 | +3 | 13 | 6 | 8 |
| 1 | 200 | +2 | 13 | 71 | 85 | +3 | 13 | 9 | 14 |
| 2 | 450 | +2 | 13 | 86 | 100 | +3 | 13 | 15 | 20 |
| 3 | 700 | +2 | 13 | 101 | 115 | +4 | 13 | 21 | 26 |
| 4 | 1,100 | +2 | 14 | 116 | 130 | +5 | 14 | 27 | 32 |
| 5 | 1,800 | +3 | 15 | 131 | 145 | +6 | 15 | 33 | 38 |
| 6 | 2,300 | +3 | 15 | 146 | 160 | +6 | 15 | 39 | 44 |
| 7 | 2,900 | +3 | 15 | 161 | 175 | +6 | 15 | 45 | 50 |
| 8 | 3,900 | +3 | 16 | 176 | 190 | +7 | 16 | 51 | 56 |
| 9 | 5,000 | +4 | 16 | 191 | 205 | +7 | 16 | 57 | 62 |
| 10 | 5,900 | +4 | 17 | 206 | 220 | +7 | 16 | 63 | 68 |
| 11 | 7,200 | +4 | 17 | 221 | 235 | +8 | 17 | 69 | 74 |
| 12 | 8,400 | +4 | 17 | 236 | 250 | +8 | 17 | 75 | 80 |
| 13 | 10,000 | +5 | 18 | 251 | 265 | +8 | 18 | 81 | 86 |
| 14 | 11,500 | +5 | 18 | 266 | 280 | +8 | 18 | 87 | 92 |
| 15 | 13,000 | +5 | 18 | 281 | 295 | +8 | 18 | 93 | 98 |
| 16 | 15,000 | +5 | 18 | 296 | 310 | +9 | 18 | 99 | 104 |
| 17 | 18,000 | +6 | 19 | 311 | 325 | +10 | 19 | 105 | 110 |
| 18 | 20,000 | +6 | 19 | 326 | 340 | +10 | 19 | 111 | 116 |
| 19 | 22,000 | +6 | 19 | 341 | 355 | +10 | 19 | 117 | 122 |
| 20 | 25,000 | +6 | 19 | 356 | 400 | +10 | 19 | 123 | 140 |
| 21 | 33,000 | +7 | 19 | 401 | 445 | +11 | 20 | 141 | 158 |
| 22 | 41,000 | +7 | 19 | 446 | 490 | +11 | 20 | 159 | 176 |
| 23 | 50,000 | +7 | 19 | 491 | 535 | +11 | 20 | 177 | 194 |
| 24 | 62,000 | +7 | 19 | 536 | 580 | +12 | 21 | 195 | 212 |
| 25 | 75,000 | +8 | 19 | 581 | 625 | +12 | 21 | 213 | 230 |
| 26 | 90,000 | +8 | 19 | 626 | 670 | +12 | 21 | 231 | 248 |
| 27 | 105,000 | +8 | 19 | 671 | 715 | +13 | 22 | 249 | 266 |
| 28 | 120,000 | +8 | 19 | 716 | 760 | +13 | 22 | 267 | 284 |
| 29 | 135,000 | +9 | 19 | 761 | 805 | +13 | 22 | 285 | 302 |
| 30 | 155,000 | +9 | 19 | 806+ | — | +14 | 23 | 303+ | — |

---

## HP Calculation Guide

Hit dice by size:
| Size | Hit Die | Average per Die |
|------|---------|----------------|
| Tiny | d4 | 2.5 |
| Small | d6 | 3.5 |
| Medium | d8 | 4.5 |
| Large | d10 | 5.5 |
| Huge | d12 | 6.5 |
| Gargantuan | d20 | 10.5 |

**Formula**: HP = (number of dice × average per die) + (number of dice × CON modifier)

Example: 15d10 + 45 (CON +3) = 15 × 5.5 + 15 × 3 = 82.5 + 45 = **127 HP**

---

## Effective HP Adjustment for Resistances / Immunities

When calculating defensive CR, adjust HP before looking up in the table:

| Condition | Multiplier | Notes |
|-----------|-----------|-------|
| Resistance to common physical (B/P/S nonmagical) | ×2 | Very common below CR 10 |
| Resistance to one damage type | ×1.25 | Only if commonly used by parties |
| Resistance to two+ damage types | ×1.5 | |
| Immunity to one damage type | ×1.5 | If uncommon type (poison, fire) |
| Immunity to common physical (B/P/S) or multiple types | ×2 | Dramatic defensive uplift |
| Regeneration | +regeneration per round × 4 to effective HP | Only if not suppressed by acid/fire |

---

## Ability Score to Modifier

| Score | Modifier | Score | Modifier |
|-------|----------|-------|----------|
| 1 | −5 | 16–17 | +3 |
| 2–3 | −4 | 18–19 | +4 |
| 4–5 | −3 | 20–21 | +5 |
| 6–7 | −2 | 22–23 | +6 |
| 8–9 | −1 | 24–25 | +7 |
| 10–11 | 0 | 26–27 | +8 |
| 12–13 | +1 | 28–29 | +9 |
| 14–15 | +2 | 30 | +10 |

---

## Common Creature Type Conventions

| Type | Common Ability Scores | Typical Saves | Common Immunities/Resistances |
|------|----------------------|---------------|-------------------------------|
| Aberration | High INT or WIS | INT, WIS | Psychic resistance common |
| Beast | STR or DEX focused | CON | None usually |
| Celestial | CHA, WIS, STR | WIS, CHA | Radiant resistance; poison immune |
| Construct | STR, CON; low INT | CON | Poison, exhaustion immune; psychic immune |
| Dragon | STR, CON, CHA | DEX, CON, WIS | Elemental immunity matching breath weapon |
| Elemental | Matching element | STR or CON | Matching elemental immunity |
| Fey | CHA, DEX | CHA, WIS | Charmed often |
| Fiend | STR, CHA | CON, CHA | Fire/poison resistance; poison immune |
| Giant | STR, CON | CON | Often none |
| Humanoid | Varies by class | Varies | Rarely any |
| Monstrosity | STR, CON | CON | Varies |
| Ooze | STR, CON; low INT/WIS/CHA | CON | Acid; exhaustion, prone immune |
| Plant | CON | CON | Poison; blinded, deafened often |
| Undead | STR or DEX; low CON | WIS | Poison; exhaustion, poison condition immune |

---

## Standard Damage Expressions by CR

Use these as starting points. Adjust for the number of attacks in multiattack.

| CR | One-Attack DPR | Two-Attack DPR Each | Three-Attack DPR Each |
|----|---------------|--------------------|-----------------------|
| 1/4 | 5 | — | — |
| 1/2 | 8 | — | — |
| 1 | 14 | 7 each | — |
| 2 | 20 | 10 each | — |
| 3 | 26 | 13 each | — |
| 4 | 32 | 16 each | — |
| 5 | 38 | 19 each | — |
| 6 | 44 | 22 each | 15 each |
| 8 | 56 | 28 each | 19 each |
| 10 | 68 | 34 each | 23 each |
| 12 | 80 | 40 each | 27 each |
| 15 | 98 | 49 each | 33 each |
| 20 | 132 | 66 each | 44 each |

**Common damage dice quick reference:**
- d4 avg: 2.5 | d6 avg: 3.5 | d8 avg: 4.5 | d10 avg: 5.5 | d12 avg: 6.5 | d20 avg: 10.5
- Useful expressions: 2d6+3=10 | 2d8+4=13 | 3d8+5=18.5 | 4d6+6=20 | 4d10+8=30 | 6d8+10=37 | 8d10+16=60

---

## Multiattack by CR Guide

| CR | Typical Attacks | Notes |
|----|----------------|-------|
| 1–2 | 1 attack or Multiattack ×2 | Simple monsters may have 1 |
| 3–6 | Multiattack ×2 | Standard pattern |
| 7–10 | Multiattack ×2–3 | 3 attacks becoming common |
| 11–15 | Multiattack ×3 | Plus a special action |
| 16–20 | Multiattack ×3–4 | Legendary monsters often have special legendary multiattack |
| 21+ | Multiattack ×4+ | With legendary actions supplementing |
