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
- ~~Target platform?~~ → Desktop (Pygame) for prototyping; mobile port aspirations for the future
- Voice acting, music, sound effects — ambitions here?

---

## Tech Stack

**Python + Pygame** — chosen for rapid prototyping. Both collaborators know Python,
and we already have a working JSON-driven adventure engine. Ambitions to port to
mobile in the future (likely via Godot or similar), but Pygame first to get the
game designed, written, and playable.

### Adventure Engine

A generic, reusable point-and-click adventure engine lives in `adventure-engine/`.
Full documentation: [`adventure-engine/ENGINE_REFERENCE.md`](adventure-engine/ENGINE_REFERENCE.md)

**Key facts:**
- **Python 3.12+**, **Pygame 2.6.1** (or pygame-ce)
- **Data-driven** — game designers write JSON, not Python. All scenes, items, dialogues,
  puzzles, and story logic live in `data/` files; the engine reads and executes them
- **Entry point:** `adventure-engine/run_game.py`
- **Run:** `cd adventure-engine && python3 run_game.py` (after `pip install pygame`)

**Project layout:**
```
adventure-engine/
├── run_game.py              # Entry point
├── ENGINE_REFERENCE.md      # Full engine docs (JSON schemas, module guide, how-tos)
├── engine/                  # 18 Python modules (DO NOT edit to add game content)
│   ├── main.py              # Game loop orchestrator
│   ├── scene.py             # Scenes, walkable areas, hotspots, exits
│   ├── player.py            # Player movement + animation
│   ├── character.py         # NPCs + companion AI
│   ├── interaction.py       # Cursor, radial menu, input dispatch
│   ├── inventory.py         # Slide-down inventory UI
│   ├── dialogue.py          # Branching dialogue trees
│   ├── scripting.py         # JSON script action executor
│   ├── pathfinding.py       # A* pathfinding (polygon + mask modes)
│   ├── speech_bubble.py     # Comic-style speech bubbles + typewriter
│   ├── camera.py            # Smooth-follow camera for wide scenes
│   ├── transitions.py       # Fade in/out
│   ├── sound.py             # Music + SFX (fail-silent)
│   ├── state.py             # Flags, inventory, save/load
│   ├── item.py              # Item definitions
│   ├── sprite_sheet.py      # Sprite loading + placeholder generation
│   ├── data_loader.py       # JSON loader
│   └── settings.py          # All engine constants
├── data/                    # Game content (JSON — this is where we build the game)
│   ├── scenes/              # One .json per scene/room
│   ├── dialogues/           # One .json per dialogue tree
│   ├── items.json           # All inventory items
│   ├── characters.json      # All NPCs
│   ├── story_flags.json     # Starting scene + initial flags
│   └── puzzles.json         # Puzzle metadata + hints
└── assets/                  # All media (backgrounds, sprites, items, sounds, fonts, UI)
```

**Adding game content — quick reference:**
- New scene → create `data/scenes/scenename.json`, add background to `assets/backgrounds/`
- New item → add to `data/items.json`, icon to `assets/items/`
- New character → add to `data/characters.json`, sprite to `assets/sprites/`, dialogue to `data/dialogues/`
- New puzzle → wire up items/hotspots/flags in JSON, add metadata to `data/puzzles.json`
- See `ENGINE_REFERENCE.md` for full JSON schemas and how-to guides

**Debug:** F1 = debug overlays, F5 = quick save, F9 = quick load

**Placeholder system:** The engine never crashes on missing assets — missing backgrounds,
sprites, icons, audio, and fonts all get auto-generated placeholders. Build and test
the entire game before creating any art.

---

## Collaboration Notes

- Both collaborators use Claude Code against this shared repo
- Update this document as decisions are made — it's the source of truth
- Use feature branches for experimental ideas
- Claude Code sessions for both collaborators read this file automatically
