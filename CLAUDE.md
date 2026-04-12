# Wizzard Game — Design Document

This is a living design document for our 2D point-and-click adventure game.
Update it freely as ideas evolve. Claude Code reads this automatically every session.

---

## Concept & Tone

A 2D point-and-click adventure game in the spirit of Monkey Island and Discworld.
Irreverent, satirical, and proudly silly. Magic exists but is largely bureaucratic,
overregulated, and disappointingly mundane. The world takes itself very seriously;
the player does not.

**Tone pillars:**
- Satire first — genre conventions, fantasy tropes, institutions, and pomposity are all fair targets
- Puzzles that reward lateral thinking and absurdist logic (if it *should* work, it probably doesn't; if it *shouldn't* work, it might)
- Dialogue-heavy, character-driven — the writing is the game
- Warmly British in sensibility (dry wit, understatement, mild chaos)

---

## Setting

> *To be developed — add your ideas here*

Some starter questions to discuss:
- Is this a classic fantasy world, a parody of one, or something stranger?
- What's the state of magic? (Unionised? Taxed? Outsourced to the lowest bidder?)
- What's the rough era/aesthetic — medieval, vaguely Victorian, anachronistic mix?

---

## Story

> *To be developed*

- **Premise:** ...
- **The inciting incident:** ...
- **The goal (what the player thinks they want):** ...
- **The actual goal (what they actually need):** ...
- **The antagonist:** ...

---

## Player Character

> *To be developed*

- **Name:** ...
- **Title/rank:** ...
- **Personality:** ...
- **Their fatal flaw (comedically):** ...
- **Why they're the worst possible person for this quest:** ...

---

## Key Characters

> *Add characters as they emerge*

| Name | Role | Personality | Notes |
|------|------|-------------|-------|
| TBD  |      |             |       |

---

## Puzzle Philosophy

- Puzzles should have internal logic — even if that logic is absurd, it must be *consistent*
- Avoid moon logic: if a solution requires reading the developer's mind, redesign it
- Dialogue should give genuine (if oblique) hints
- Inventory puzzles, dialogue trees, and environmental interactions are all in scope
- A puzzle that makes the player groan and then laugh is a perfect puzzle

---

## Art Direction

> *To be decided*

- Style references: ...
- Palette / colour mood: ...
- UI style: ...
- Character design notes: ...

---

## World & Locations

> *Add locations as they are conceived*

| Location | Description | Purpose in story |
|----------|-------------|-----------------|
| TBD      |             |                 |

---

## Open Questions

Things we haven't decided yet — discuss and move answers into the relevant section above.

- What is the setting's central satirical target? (Fantasy bureaucracy? Academia? Guild culture? All of the above?)
- Single protagonist or do we play multiple characters?
- What's the scope? (Short demo, episodic, full game?)
- Target platform? (Desktop, browser, mobile?)
- Voice acting, music, sound effects — ambitions here?

---

## Tech Stack

> *To be decided once story/scope is clearer*

Candidates to evaluate:
- **Python + Pygame** — simple, good for rapid prototyping
- **Godot** — full-featured, free, good 2D support, GDScript is approachable
- **JavaScript + Phaser** — browser-native, easy to share/playtest
- **Ren'Py** — purpose-built for dialogue-heavy adventure games

Decision criteria: scope, art pipeline, ease of collaboration, target platform.

---

## Collaboration Notes

- Both collaborators use Claude Code against this shared repo
- Update this document as decisions are made — it's the source of truth
- Use feature branches for experimental ideas
- Claude Code sessions for both collaborators read this file automatically
