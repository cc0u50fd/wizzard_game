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

A parody fantasy world wearing a modern British skin. Magic exists but is regulated,
unionised, taxed, and buried under paperwork. The aesthetic is anachronistic —
medieval-ish buildings, vaguely Victorian institutions, modern mundanities (kebab shops,
plastic chairs, takeaway menus, clip-on ties). Think Terry Pratchett's Ankh-Morpork
crossed with a run-down British high street.

**Magic:** Licensed by grade (A–E, with D being "barely functional"). The Wizard's
Union enforces dues. The Licensing Board enforces renewals. Neither enforces competence.

**Era:** Deliberately inconsistent — crystal balls show adverts, golems work as
receptionists, minotaurs wear cheap suits. The anachronism *is* the joke.

---

## Story

- **Premise:** Mortimer Grimshaw is a burnt-out wizard PI running a one-man detective
  agency above a kebab shop. Business is bad. Then a minotaur walks in.
- **The inciting incident:** Gerald the minotaur's labyrinth has been stolen — the whole
  thing, walls and all — and the only clue is a business card from "Bastardo's Discount
  Labyrinth Relocation Services."
- **The goal (what the player thinks they want):** Find Gerald's labyrinth and bring
  The Magnificent Bastardo to justice.
- **The actual goal (what they actually need):** *TBD — something about Grimshaw
  rediscovering his self-worth / renewing his licence / actually being good at his job again*
- **The antagonist:** The Magnificent Bastardo — con artist, showman, and the most wanted
  wizard in three counties. Cheap cologne, business cards everywhere, a flair for the dramatic.

---

## Player Character

- **Name:** Mortimer Grimshaw
- **Title/rank:** Private Investigator, Grade D wizard (expired licence)
- **Personality:** Deeply sarcastic, world-weary, self-deprecating. Narrates his own
  life in hard-boiled detective monologue. Underneath the cynicism, he actually cares —
  he just wishes he didn't.
- **Their fatal flaw (comedically):** He's competent enough to take on cases but too
  burnt-out to finish them efficiently. His inner monologue never stops. He solves
  problems sideways because doing things properly requires paperwork.
- **Why they're the worst possible person for this quest:** His magic licence is expired,
  he owes money to everyone, his wand is broken, and his main investigative tool is an
  empty hip flask and a Grade D crystal ball that gets three channels (two shopping networks).

---

## Key Characters

| Name | Role | Personality | Notes |
|------|------|-------------|-------|
| Mortimer Grimshaw | Player character — wizard PI | Sarcastic, burnt-out, secretly competent | Grade D licence (expired), trench coat, empty hip flask |
| Mrs. Ethel Copperbottom | Receptionist — sentient filing golem | Passive-aggressive, terrifyingly efficient, speaks in filing metaphors | Made of card catalogues and brass index tabs, wears a tiny cardigan |
| Gerald | Client — minotaur | Anxious, earnest, emotional, surprisingly gentle | Cheap suit, clip-on tie, NVQ in Lurking, distinction in Ominous Breathing |
| The Magnificent Bastardo | Antagonist — con artist wizard | *Not yet seen in-game* | Most wanted wizard in three counties, cheap cologne, business cards |
| Pip | Grimshaw's familiar (companion) | Relentlessly cheerful, speaks entirely in wellness buzzwords, genuinely cares, catastrophically unskilled | Permanently bonded via a Grade C exam explosion; more or less indestructible; mistakes sarcasm for progress; has kept a chart of Grimshaw's 'yes' responses |
| Rashid | Kebab shop owner (downstairs) | *Not yet in-game — mentioned only* | Gives Grimshaw a discount (out of pity), tab is "creatively large" |

---

## Puzzle Philosophy

- Puzzles should have internal logic — even if that logic is absurd, it must be *consistent*
- Avoid moon logic: if a solution requires reading the developer's mind, redesign it
- Dialogue should give genuine (if oblique) hints
- Inventory puzzles, dialogue trees, and environmental interactions are all in scope
- A puzzle that makes the player groan and then laugh is a perfect puzzle

---

## Art Direction

- **Style references:** LucasArts adventure games (Monkey Island, Day of the Tentacle),
  Discworld point-and-clicks. Detailed 2D backgrounds, slightly exaggerated character
  proportions.
- **Palette / colour mood:** Warm but dingy — browns, ambers, faded greens, worn wood,
  scuffed leather. Pops of colour from magical items (crystal ball glow, Ethel's brass
  fittings). Think "cosy squalor."
- **UI style:** Engine defaults (parchment tones, radial menus). Works well with the tone.
- **Character design notes:** Big heads, expressive faces/hands. Not realistic but grounded
  enough to sell the comedy. Ethel is boxy/angular (filing cabinet body), Gerald is large
  and hunched (anxiety, not menace).
- **Art prompts:** See [`adventure-engine/ART_PROMPTS.md`](adventure-engine/ART_PROMPTS.md)
  for generation-ready prompts for all assets.

---

## World & Locations

| Location | Description | Purpose in story |
|----------|-------------|-----------------|
| `waiting_room` | Shabby waiting room above a kebab shop — plastic chairs, noticeboard, water cooler, Ethel's reception desk | Starting scene. Meet Gerald and Ethel, begin the case |
| `detectives_office` | Grimshaw's office — desk buried under takeaway containers, crystal ball, filing cabinet, bookshelf, hat stand | Pick up hip flask, use filing cabinet to get case file |

---

## Current Demo Status

A two-scene playable demo is complete (`waiting_room` + `detectives_office`).
All placeholder art — fully playable without real assets.

**Puzzle:** "Accept Gerald's Case" — talk to Gerald → talk to Ethel → get filing
reference → use on filing cabinet → get case file → use on Gerald. Tests conditional
dialogues, item use-on, scene transitions, flags, and cross-scene puzzle flow.

**What's implemented:** 16 hotspots, 2 NPCs, 2 branching dialogue trees (79 nodes total),
3 inventory items (12+ comedic red-herring use_on responses), 13 flags, first-visit
monologues, puzzle metadata with progressive hints.

## Open Questions

Things we haven't decided yet — discuss and move answers into the relevant section above.

- ~~What is the setting's central satirical target?~~ → Fantasy bureaucracy, magical licensing, mundane institutions — all of the above
- Single protagonist or do we play multiple characters?
- What's the scope? (Short demo, episodic, full game?)
- ~~Target platform?~~ → Desktop (Pygame) for prototyping; mobile port aspirations for the future
- Voice acting, music, sound effects — ambitions here?
- What happens after Grimshaw accepts the case? Where does the investigation lead?
- Do we meet Bastardo in person? Is he a boss fight, a chase, or just an escalating series of business cards?
- Should Grimshaw have a companion? (Familiar? Reluctant sidekick? Enchanted pigeon?)

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
