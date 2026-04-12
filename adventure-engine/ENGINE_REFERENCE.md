# Point-and-Click Adventure Engine Reference

A comprehensive architecture and design guide for a JSON-driven, 2D point-and-click adventure engine built with Pygame. Use this as a prompt/reference when building a new game on the same architecture.

---

## Table of Contents

1. [Setup & Requirements](#setup--requirements)
2. [Project Structure](#project-structure)
3. [Running the Game](#running-the-game)
4. [Architecture Overview](#architecture-overview)
5. [The Game Loop](#the-game-loop)
6. [JSON Schema Reference](#json-schema-reference)
   - [Scenes](#scenes)
   - [Characters](#characters)
   - [Items](#items)
   - [Dialogues](#dialogues)
   - [Story Flags](#story-flags)
   - [Puzzles](#puzzles)
7. [Script Actions Reference](#script-actions-reference)
8. [Condition System](#condition-system)
9. [Engine Modules](#engine-modules)
10. [Art & Asset Pipeline](#art--asset-pipeline)
11. [How To: Add a New Scene](#how-to-add-a-new-scene)
12. [How To: Add a New Item & Puzzle](#how-to-add-a-new-item--puzzle)
13. [How To: Add a New Dialogue Tree](#how-to-add-a-new-dialogue-tree)
14. [How To: Add a New Character](#how-to-add-a-new-character)
15. [Key Design Patterns](#key-design-patterns)
16. [Debug Tools](#debug-tools)
17. [Constants & Tuning](#constants--tuning)

---

## Setup & Requirements

### Python & Pygame

- **Python 3.12+**
- **Pygame 2.6.1** (standard `pygame` — or `pygame-ce` Community Edition, both work)
- No other runtime dependencies

### Virtual Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame          # or: pip install pygame-ce
```

### Entry Point

```python
#!/usr/bin/env python3
"""Adventure Game - Entry Point"""
from engine.main import GameEngine

if __name__ == "__main__":
    game = GameEngine()
    game.run()
```

Save as `run_game.py` in the project root.

---

## Project Structure

```
project_root/
├── run_game.py              # Entry point (3 lines)
├── engine/                  # Python engine modules (18 files)
│   ├── main.py              # GameEngine class — game loop orchestrator
│   ├── scene.py             # Scene, WalkableArea, MaskWalkableArea, Hotspot, Exit
│   ├── player.py            # Player character movement + animation
│   ├── character.py         # NPCs + companion AI
│   ├── interaction.py       # Cursor management, radial menu, input dispatch
│   ├── inventory.py         # Slide-down inventory UI
│   ├── item.py              # Item definitions + icon loading
│   ├── dialogue.py          # Branching dialogue tree system
│   ├── scripting.py         # JSON script action executor
│   ├── sprite_sheet.py      # Sprite loader + placeholder generator
│   ├── sound.py             # Music + SFX manager (fail-silent)
│   ├── camera.py            # Smooth-follow camera for wide scenes
│   ├── pathfinding.py       # A* on visibility graph + grid-based A*
│   ├── speech_bubble.py     # Comic-style speech bubbles with typewriter effect
│   ├── transitions.py       # Fade in/out screen transitions
│   ├── state.py             # Game flags, inventory state, save/load
│   ├── data_loader.py       # JSON file loader
│   └── settings.py          # All engine constants (speeds, sizes, colours)
├── data/                    # JSON-driven game content (NO code needed here)
│   ├── scenes/              # One .json per scene/room
│   ├── dialogues/           # One .json per dialogue tree
│   ├── items.json           # All inventory items
│   ├── characters.json      # All NPC definitions
│   ├── story_flags.json     # Starting scene + initial flag values
│   └── puzzles.json         # Puzzle metadata + hints
├── assets/                  # All media files
│   ├── backgrounds/         # Scene backgrounds (PNG)
│   ├── sprites/             # Character sprites (per-frame PNGs in subdirs)
│   ├── items/               # Inventory item icons (56x56 PNG)
│   ├── sounds/
│   │   ├── music/           # Background music (OGG, looped)
│   │   └── sfx/             # Sound effects (OGG)
│   ├── fonts/               # TTF fonts
│   └── ui/                  # Cursors, radial menu icons, inventory background
├── saves/                   # Auto-created save files (JSON)
└── fonts/                   # Source TTF files (symlinked into assets/fonts/)
```

### Key Principle: Data-Driven Design

**Game designers write JSON, not Python.** All scenes, items, dialogues, puzzles, and story logic are defined in `data/` files. The engine reads these at startup and executes them. You should never need to edit `engine/` code to add game content.

---

## Running the Game

```bash
source venv/bin/activate
python3 run_game.py
```

### Controls

| Input | Action |
|-------|--------|
| Left click ground | Walk to position |
| Double left click | Run to position |
| Right click hotspot | Show radial action menu |
| Click top of screen / `I` | Toggle inventory |
| Left click item then hotspot | Use item on hotspot |
| Right click inventory item | Examine item |
| `F1` | Toggle debug overlays |
| `F5` | Quick save (slot 1) |
| `F9` | Quick load (slot 1) |
| `ESC` | Close inventory / quit |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      GameEngine                         │
│  (owns all subsystems, runs the game loop)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DataLoader ──→ loads all JSON at startup                │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │  Player   │  │ Camera   │  │ Interaction  │          │
│  │ (movement │  │ (smooth  │  │ (input, radial│          │
│  │  + anim)  │  │  follow) │  │  menu, cursor)│          │
│  └──────────┘  └──────────┘  └──────────────┘          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │Characters│  │Inventory │  │ ScriptRunner │          │
│  │ (NPCs +  │  │ (UI bar, │  │ (action queue│          │
│  │companion)│  │  slots)  │  │  executor)   │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │Dialogue  │  │  Speech  │  │ Transitions  │          │
│  │ Manager  │  │ Manager  │  │ (fades)      │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
│                                                         │
│  ┌──────────┐  ┌──────────┐                             │
│  │  Sound   │  │GameState │                             │
│  │ Manager  │  │(flags,   │                             │
│  │          │  │ save/load│                             │
│  └──────────┘  └──────────┘                             │
└─────────────────────────────────────────────────────────┘
```

---

## The Game Loop

Every frame (60 FPS), three phases run in order:

### 1. Handle Input
Events are routed based on the current game state:
- **Transition active** → all input blocked
- **Dialogue active** → only dialogue system receives events
- **Speech bubble showing** → click advances/dismisses
- **Script waiting** → click advances speech
- **Otherwise** → InteractionManager handles (walking, menus, inventory)

### 2. Update State
All systems update with delta time (`dt`, capped at 50ms to prevent spiral):
- Script queue execution
- Player movement along path
- Companion AI follow logic
- NPC updates
- Speech bubble typewriter
- Dialogue advancement
- Camera follow
- Inventory slide animation
- Edge exit collision checks

### 3. Draw (back to front)
1. Scene background
2. All entities **Y-sorted** (player, companion, NPCs) — lower Y drawn first
3. Speech bubbles (screen-space, offset by camera)
4. Dialogue UI (choice panel)
5. Radial menu overlay
6. Inventory bar
7. Transition overlay (fade)
8. Debug HUD (if enabled)

**Delta time:** All movement uses `speed * dt` so everything runs at consistent speed regardless of frame rate.

---

## JSON Schema Reference

### Scenes

Each scene is a single JSON file in `data/scenes/`. The engine auto-discovers all `*.json` files in that directory.

```jsonc
{
  "id": "tavern",                              // REQUIRED: unique scene identifier
  "name": "The Rusty Anchor Tavern",           // Optional: display name (defaults to id)
  "background": "backgrounds/tavern.png",      // Path relative to assets/
  "bounds": [1280, 720],                       // [width, height] — use >1280 for scrolling scenes
  "music": "sounds/music/tavern_theme.ogg",    // Optional: background music (loops)

  "depth_config": {                            // Perspective scaling
    "horizon_y": 200,                          // Y where characters are smallest
    "ground_y": 680,                           // Y where characters are largest
    "min_scale": 0.4,                          // Scale at horizon (0.4 = 40%)
    "max_scale": 1.0                           // Scale at ground (1.0 = 100%)
  },

  "walkable_area": {                           // WHERE the player can walk
    "polygons": [                              // Array of polygon vertex arrays
      [[50, 450], [800, 440], [1230, 700], [50, 700]]
    ]
  },
  // ALTERNATIVE: provide a *_walkable.png mask image (magenta pixels = walkable)
  // If the mask exists, it takes priority over polygons

  "entry_points": {                            // Named spawn positions
    "default": [640, 600],                     // REQUIRED: at least "default"
    "from_street": [100, 550],                 // Named by the scene the player came from
    "from_cellar": [800, 650]
  },

  "hotspots": [                                // Interactive clickable regions
    {
      "id": "bar_counter",                     // REQUIRED: unique within scene
      "name": "Bar Counter",                   // Display name (shown in UI)
      "rect": [400, 350, 200, 100],            // [x, y, width, height] click region
      "walk_to": [500, 500],                   // Where player walks before interacting
      "look_at_dir": "right",                  // "left" or "right" — player faces this way
      "enabled": true,                         // Optional (default true), can be toggled by scripts
      "conditions": {"flag": "door_open"},     // Optional: only visible/active when condition met
      "actions": {                             // Dict of action_name → script action arrays
        "look": [
          {"type": "say", "speaker": "player", "text": "A well-worn bar counter..."}
        ],
        "use": [
          {"type": "say", "speaker": "player", "text": "I lean on the bar and wait."}
        ],
        "talk": [
          {"type": "start_dialogue", "dialogue_id": "bartender_chat"}
        ]
      }
    }
  ],

  "exits": [                                   // Scene transitions
    {
      "id": "to_street",                       // REQUIRED
      "exit_type": "edge_right",               // "edge_left"|"edge_right"|"edge_top"|"edge_bottom"|"hotspot"
      "rect": [1248, 400, 32, 310],            // Trigger zone
      "target_scene": "village_street",        // Scene ID to load
      "target_entry": "from_tavern",           // Entry point name in target scene
      "conditions": {"flag": "bouncer_gone"}   // Optional: blocks exit until condition met
    },
    {
      "id": "to_cellar",
      "exit_type": "hotspot",                  // Requires explicit click (not auto-trigger)
      "rect": [700, 500, 80, 60],
      "walk_to": [740, 560],                   // Player walks here first
      "target_scene": "cellar",
      "target_entry": "from_tavern"
    }
  ],

  "npcs": ["bartender", "mysterious_stranger"], // Character IDs from characters.json

  "on_enter": [],                              // Script actions to run when scene loads
  "on_exit": []                                // Script actions to run when leaving
}
```

**Exit types:**
- `edge_left/right/top/bottom` — auto-triggers when the player walks into the rect during movement
- `hotspot` — requires the player to click on it (shows in radial menu as "Walk to")

**Scene sizes:**
- Standard: `[1280, 720]` — no camera scrolling
- Wide: `[1792, 720]` or any width > 1280 — camera smoothly follows the player

### Characters

All NPCs defined in a single `data/characters.json` file. One entry can be marked as the auto-following companion.

```jsonc
{
  "characters": [
    {
      "id": "bartender",                       // REQUIRED: unique identifier
      "name": "Bartender",                     // Display name
      "sprite": "sprites/bartender_standing",  // Path to sprite directory (contains 1.png)
      "scene_id": "tavern",                    // Which scene this NPC lives in
      "x": 500,                                // Initial X position (world coords)
      "y": 450,                                // Initial Y position (foot anchor)
      "facing": "left",                        // "left" or "right"
      "speed": 100,                            // Walk speed in pixels/second
      "dialogue_id": "bartender_chat"          // Dialogue tree to load on "talk" action
    },
    {
      "id": "dog",                             // Companion example
      "name": "Dog",
      "is_companion": true,                    // Marks this as the auto-following companion
      "follow_distance": 70,                   // Optional: override COMPANION_FOLLOW_DISTANCE
      "speed_mult": 1.1                        // Optional: override COMPANION_FOLLOW_SPEED_MULT
    }
  ]
}
```

**Sprite loading:** The engine looks for `assets/{sprite}/1.png`. If found, it creates left/right idle and walk frames by flipping. If missing, it generates a coloured placeholder.

**Companion character:** If a character has `"is_companion": true`, it becomes the auto-following companion instead of a regular NPC. Companion walk sprites are loaded from `assets/sprites/companion_walk/`. If no companion entry exists in characters.json, a default placeholder companion is created.

### Items

All inventory items defined in a single `data/items.json` file.

```jsonc
{
  "items": [
    {
      "id": "brass_key",                       // REQUIRED: unique identifier
      "name": "Brass Key",                     // Display name (shown in tooltip)
      "icon": "items/brass_key.png",           // Path relative to assets/ (56x56 recommended)
      "examine_text": "A small brass key with an ornate handle.",  // Right-click description

      "combinable_with": {                     // Combine with other inventory items
        "locked_box": [                        // other_item_id → script actions
          {"type": "say", "speaker": "player", "text": "The key fits the box!"},
          {"type": "remove_item", "item_id": "brass_key"},
          {"type": "remove_item", "item_id": "locked_box"},
          {"type": "give_item", "item_id": "old_letter"},
          {"type": "set_flag", "flag": "opened_box", "value": true}
        ]
      },

      "use_on": {                              // Use on world hotspots
        "locked_door": [                       // hotspot_id → script actions
          {"type": "say", "speaker": "player", "text": "The key turns with a click."},
          {"type": "remove_item", "item_id": "brass_key"},
          {"type": "set_flag", "flag": "door_unlocked", "value": true},
          {"type": "disable_hotspot", "hotspot_id": "locked_door"},
          {"type": "enable_hotspot", "hotspot_id": "open_door"}
        ]
      }
    }
  ]
}
```

**Item use-on flow:** Player clicks item in inventory (selects it), then clicks a hotspot. Engine looks up `item.use_on[hotspot.id]`. If found, player walks to hotspot, faces it, and the script runs. If not found, a default "I can't use that here" message plays.

### Dialogues

Each dialogue tree is a separate JSON file in `data/dialogues/`.

```jsonc
{
  "id": "bartender_chat",                      // Matches the dialogue_id in characters.json
  "nodes": {
    "start": {                                 // Entry node (always named "start")
      "type": "conditional",
      "branches": [
        {
          "condition": {"flag": "talked_to_bartender", "equals": false},
          "next": "first_meeting"
        },
        {
          "condition": {"has_item": "old_letter"},
          "next": "about_letter"
        }
      ],
      "default": "generic_greeting"            // Fallback if no branch matches
    },

    "first_meeting": {                         // NPC speaks
      "type": "say",
      "speaker": "bartender",
      "text": "Welcome, stranger. What'll it be?",
      "style": "normal",                       // "normal"|"shout"|"whisper"|"thought"
      "next": "player_response"
    },

    "player_response": {                       // Player character speaks
      "type": "player_say",
      "text": "Just information, thanks.",
      "next": "main_choices"
    },

    "main_choices": {                          // Player picks from options
      "type": "choice",
      "choices": [
        {
          "text": "Tell me about this town.",
          "next": "town_info"
        },
        {
          "text": "Seen anything suspicious lately?",
          "next": "suspicious_info",
          "condition": {"flag": "knows_about_theft"}  // Only shows if condition met
        },
        {
          "text": "Never mind. Goodbye.",
          "next": "farewell"
        }
      ]
    },

    "town_info": {
      "type": "say",
      "speaker": "bartender",
      "text": "Quiet place, mostly. Fishing village. Been here forty years.",
      "next": "main_choices"                   // Loop back to choices
    },

    "farewell": {
      "type": "action",                        // Run script actions mid-dialogue
      "actions": [
        {"type": "set_flag", "flag": "talked_to_bartender", "value": true}
      ],
      "next": "end_node"
    },

    "end_node": {                              // End the conversation
      "type": "end"
    }
  }
}
```

**Node types:**

| Type | Description |
|------|-------------|
| `say` | NPC speaks (speech bubble, typewriter effect, click to advance) |
| `player_say` | Player character speaks (same mechanics) |
| `choice` | Show clickable response options at bottom of screen |
| `conditional` | Branch based on flags/items/visited scenes |
| `action` | Execute script actions (set flags, give items, etc.) |
| `end` | End the conversation, return to gameplay |

**Speech styles:** `normal` (rounded bubble), `shout` (spiky border, larger font), `whisper` (dashed border), `thought` (cloud shape with bubble pointer).

### Story Flags

`data/story_flags.json` defines the starting state.

```jsonc
{
  "starting_scene": "tavern",                  // Scene to load on new game
  "initial_flags": {                           // Any JSON values — all start here
    "talked_to_bartender": false,
    "door_unlocked": false,
    "coins": 0,
    "knows_about_theft": false
  }
}
```

Flags are the backbone of all conditional logic. They can be any JSON type (boolean, integer, string, null). Scripts modify them with `set_flag`, and conditions check them everywhere.

### Puzzles

`data/puzzles.json` — metadata for tracking and optional hint systems.

```jsonc
{
  "puzzles": [
    {
      "id": "unlock_cellar",                   // Unique identifier
      "name": "Access the Cellar",             // Display name
      "description": "Find a way to get past the locked cellar door",
      "hints": [                               // Progressive hints (vague → explicit)
        "Look around the tavern for something useful.",
        "The bartender might know where the key is.",
        "Ask the bartender about the cellar, then search behind the bar."
      ],
      "completion_flag": "door_unlocked"        // Flag that marks puzzle as solved
    }
  ]
}
```

Puzzles are metadata only — the engine doesn't enforce them. The actual puzzle logic lives in hotspot scripts, item use-on definitions, and dialogue branches.

---

## Script Actions Reference

Scripts are arrays of action objects. They appear in hotspot actions, item use-on/combine, scene on_enter/on_exit, and dialogue action nodes.

### Blocking Actions (pause queue until complete)

#### `say` — Show speech bubble
```json
{"type": "say", "speaker": "character_id", "text": "Hello there!", "style": "normal"}
```
- `speaker`: character ID or `"player"` for the protagonist
- `style`: `"normal"` | `"shout"` | `"whisper"` | `"thought"` (optional, defaults to normal)
- Blocks until player clicks to dismiss

#### `walk_to` — Move a character
```json
{"type": "walk_to", "who": "player", "target": [500, 600]}
```
- `who`: `"player"` or a character ID
- Blocks until character arrives at destination

#### `wait` — Pause
```json
{"type": "wait", "duration": 1.5}
```
- Duration in seconds

#### `change_scene` — Transition to new scene
```json
{"type": "change_scene", "scene_id": "cellar", "entry": "from_tavern"}
```
- Triggers fade out → load → fade in
- `entry`: entry point name (defaults to `"default"`)

#### `fade_in` / `fade_out` — Manual fade control
```json
{"type": "fade_out", "duration": 0.5}
```

### Immediate Actions (execute instantly, queue continues)

#### `face` — Turn character
```json
{"type": "face", "who": "player", "direction": "left"}
```

#### `set_flag` — Modify game state
```json
{"type": "set_flag", "flag": "door_unlocked", "value": true}
```
- Value can be any JSON type

#### `give_item` — Add to inventory
```json
{"type": "give_item", "item_id": "brass_key"}
```

#### `remove_item` — Remove from inventory
```json
{"type": "remove_item", "item_id": "brass_key"}
```

#### `enable_hotspot` / `disable_hotspot` — Toggle hotspot visibility
```json
{"type": "enable_hotspot", "hotspot_id": "open_door"}
{"type": "disable_hotspot", "hotspot_id": "locked_door"}
```

#### `play_sfx` — Play sound effect
```json
{"type": "play_sfx", "sfx": "sounds/sfx/door_creak.ogg"}
```

#### `start_dialogue` — Begin dialogue tree
```json
{"type": "start_dialogue", "dialogue_id": "bartender_chat", "start_node": "start"}
```

#### `check_flag` — Conditional branching
```json
{
  "type": "check_flag",
  "condition": {"flag": "has_key", "equals": true},
  "then": [
    {"type": "say", "speaker": "player", "text": "I can use this key!"}
  ],
  "else": [
    {"type": "say", "speaker": "player", "text": "I need to find the key first."}
  ]
}
```

---

## Condition System

Conditions are used in: `check_flag` scripts, hotspot `conditions`, exit `conditions`, dialogue `conditional` nodes, and dialogue choice `condition` filters.

```jsonc
// Simple flag checks
{"flag": "has_key", "equals": true}           // Exact match
{"flag": "coins", "gte": 5}                   // Greater than or equal
{"flag": "attempts", "lt": 3}                 // Less than
{"flag": "door_unlocked"}                     // Truthy check (exists and not false/0/null)

// Inventory check
{"has_item": "brass_key"}                     // Player has this item

// Scene visit check
{"visited": "cellar"}                         // Player has been to this scene

// Logical operators (nestable)
{"and": [{"flag": "has_key"}, {"visited": "cellar"}]}
{"or": [{"has_item": "crowbar"}, {"flag": "door_unlocked"}]}
{"not": {"flag": "guard_alerted"}}
```

---

## Engine Modules

### `main.py` — GameEngine
The orchestrator. Owns all subsystems, runs the game loop (input → update → draw). Handles scene changes with fade transitions. Routes input based on game state priority: transitions > dialogue > speech > scripts > interaction.

### `scene.py` — Scene, WalkableArea, Hotspot, Exit
Loads scene JSON into objects. Two walkable area modes:
- **MaskWalkableArea**: Reads a `*_walkable.png` image. Magenta pixels (R>180, G<80, B>180) = walkable. Uses 8px downsampled grid for A* pathfinding.
- **WalkableArea**: Polygon-based. Uses visibility graph A* — polygon vertices become nodes, connected if line-of-sight exists within the polygon.

### `player.py` — Player
Float position (x, y) at foot anchor. Path-following with waypoint queue. Walk (180px/s) and run (340px/s, double-click). Depth scaling based on Y position. Animation states: idle_left/right, walk_left/right.

### `character.py` — CharacterRegistry, Character, Companion
NPCs use the same animation/movement system as the player. Companion AI auto-follows the player: pathfinds toward a point behind the protagonist when distance > threshold, moves at 1.1x speed to catch up.

### `pathfinding.py` — A* pathfinding
Two modes matching the walkable area type:
- **Polygon mode**: Visibility graph between polygon vertices, A* with Euclidean heuristic
- **Mask mode**: 8-directional A* on downsampled grid, with line-of-sight shortcutting

Utilities: `point_in_polygon()` (ray casting), `segments_intersect()`, `find_nearest_point_in_polygon()`.

### `interaction.py` — InteractionManager, RadialMenu, CursorManager
Central input router. Handles: walk-to-click, double-click-to-run, right-click radial menu on hotspots, inventory item selection + use-on-hotspot, exit triggers. Radial menu shows available actions in a circle around the hotspot.

### `scripting.py` — ScriptRunner
Sequential action queue executor. Pops actions one at a time, dispatches to handler functions. Blocking actions pause the queue until complete (callbacks resume). Supports nested branching via `check_flag`.

### `dialogue.py` — DialogueManager, DialogueTree
Tree traversal system. Loads dialogue JSON lazily, caches in memory. Processes nodes by type. Choice UI renders as a semi-transparent panel at screen bottom with hover highlighting.

### `inventory.py` — Inventory
Slide-down UI bar from top of screen. 64x64 slots, centered. Item selection for use-on interactions. Right-click to examine. Synced with GameState.

### `item.py` — ItemRegistry, Item
Loads items.json, provides lookup. Icons scaled to 56x56 or auto-generated as coloured squares with first letter.

### `speech_bubble.py` — SpeechManager, SpeechBubble
Comic-style bubbles positioned above speakers. Typewriter text reveal (40 chars/s). Click once to finish typing, click again to dismiss. Queue system for sequential speech. Four visual styles (normal, shout, whisper, thought).

### `camera.py` — Camera
Smooth-follow for scenes wider than 1280px. Lerp-based interpolation (smoothing factor 5.0). Clamped to scene bounds. Provides `screen_to_world()` and `apply()` coordinate conversion.

### `transitions.py` — TransitionManager
Fade in/out effects (0.5s default). Scene changes use: fade out → midpoint callback (load new scene) → fade in. Full-screen black surface with alpha.

### `sound.py` — SoundManager
Music: looped playback, crossfade on scene change (1000ms fadeout). SFX: cached Sound objects. **Fail-silent** — missing audio files are skipped without crashing.

### `state.py` — GameState
Holds all persistent data: flags (dict), inventory items (list), visited scenes (set), current scene, player position. Save/load to `saves/save_N.json`. Condition checking engine used by scripts, dialogues, hotspots, exits.

### `sprite_sheet.py` — Sprite loading + placeholders
Loads per-frame PNGs from directories (`sprites/character_name/1.png`, `2.png`, etc.). Magenta colorkey removal (R>180, G<80, B>180 → transparent). Generates coloured placeholder sprites if real art is missing — the game is always playable without art.

### `data_loader.py` — DataLoader
Loads all JSON files at startup: scenes from `data/scenes/*.json`, items, characters, story flags, puzzles. Dialogues loaded lazily by DialogueManager.

### `settings.py` — Constants
All tuning values in one file. See [Constants & Tuning](#constants--tuning).

---

## Art & Asset Pipeline

### Backgrounds
- Standard scene: **1280x720 PNG**
- Wide/scrolling scene: **1792x720 PNG** (or any width > 1280)
- Path: `assets/backgrounds/scenename.png`

### Walkable Masks
- Same dimensions as the background
- **Black background** with **magenta pixels** `(255, 0, 255)` marking walkable areas
- Path: `assets/backgrounds/scenename_walkable.png`
- If this file exists, it overrides the JSON `walkable_area.polygons`

### Character Sprites
- Per-frame PNGs in a subdirectory: `assets/sprites/character_name/1.png`, `2.png`, ...
- **Foot anchor** at bottom-center of sprite
- Right-facing by default — the engine auto-flips for left-facing
- Use **magenta colorkey** `(255, 0, 255)` for transparency, or use PNGs with alpha channel
- Standing characters: single frame (`1.png`) — engine creates idle + walk from it
- Walking characters: multiple frames (8-11 typical) for walk cycle

### Sprite scaling
- Configure `PLAYER_SPRITE_SCALE` and `COMPANION_SPRITE_SCALE` in settings.py for real sprites
- Player walk sprites go in `assets/sprites/player_walk/1.png`, `2.png`, ...
- Companion walk sprites go in `assets/sprites/companion_walk/1.png`, `2.png`, ...
- Depth scaling further adjusts based on Y position in the scene

### Item Icons
- **56x56 PNG** (or any size — engine scales to 56x56)
- Path: `assets/items/itemname.png`
- If missing, engine generates a coloured square with the first letter

### Audio
- Music: **OGG format**, placed in `assets/sounds/music/`
- SFX: **OGG format**, placed in `assets/sounds/sfx/`
- Missing files fail silently — no crash

### Fonts
- **TTF format**, placed in `assets/fonts/`
- Filenames configured in settings.py: `FONT_NORMAL` (default `"adventure.ttf"`) and `FONT_SHOUT` (default `"adventure_shout.ttf"`)
- Falls back to pygame system font if missing

### Placeholder/Fallback System
The engine **never crashes on missing assets**:
- Missing background → gradient placeholder (sky blue → ground green)
- Missing walkable mask → falls back to JSON polygons → falls back to bottom 300px of scene
- Missing character sprite → coloured placeholder rectangle
- Missing item icon → coloured square with first letter
- Missing audio → silent (no error)
- Missing font → pygame default system font

This means you can build and test the entire game before creating any art.

---

## How To: Add a New Scene

1. **Create the scene JSON** — `data/scenes/your_scene.json`:
   ```json
   {
     "id": "your_scene",
     "name": "Your Scene Name",
     "background": "backgrounds/your_scene.png",
     "bounds": [1280, 720],
     "depth_config": {
       "horizon_y": 200, "ground_y": 680,
       "min_scale": 0.4, "max_scale": 1.0
     },
     "walkable_area": {
       "polygons": [[[50, 450], [1230, 450], [1230, 700], [50, 700]]]
     },
     "entry_points": {
       "default": [640, 600],
       "from_other_scene": [100, 550]
     },
     "hotspots": [],
     "exits": [],
     "npcs": [],
     "on_enter": [],
     "on_exit": []
   }
   ```

2. **Add background art** — place `your_scene.png` in `assets/backgrounds/` (or let the placeholder work)

3. **Optionally add a walkable mask** — `assets/backgrounds/your_scene_walkable.png` (magenta on black)

4. **Connect it** — add an exit in another scene that targets `"your_scene"`:
   ```json
   {
     "id": "to_your_scene",
     "exit_type": "edge_right",
     "rect": [1248, 400, 32, 310],
     "target_scene": "your_scene",
     "target_entry": "from_other_scene"
   }
   ```

5. **Run the game** — the DataLoader auto-discovers all scene JSON files.

### Walkable Area Tips
- Use **F1 debug mode** to see the walkable overlay (green tint/outlines)
- Polygon vertices are `[x, y]` pairs defining the boundary — player can only walk inside
- For complex rooms, use a painted mask (`*_walkable.png`) — much easier for irregular shapes
- Multiple polygons supported for disconnected walkable regions

---

## How To: Add a New Item & Puzzle

1. **Add the item** to `data/items.json`:
   ```json
   {
     "id": "silver_coin",
     "name": "Silver Coin",
     "icon": "items/silver_coin.png",
     "examine_text": "An old silver coin. Might be worth something to someone.",
     "combinable_with": {},
     "use_on": {
       "vending_machine": [
         {"type": "say", "speaker": "player", "text": "Let's see what this gets me..."},
         {"type": "remove_item", "item_id": "silver_coin"},
         {"type": "give_item", "item_id": "mysterious_potion"},
         {"type": "set_flag", "flag": "used_vending_machine", "value": true}
       ]
     }
   }
   ```

2. **Add a pickup hotspot** in the relevant scene:
   ```json
   {
     "id": "loose_floorboard",
     "name": "Loose Floorboard",
     "rect": [300, 600, 80, 40],
     "walk_to": [340, 620],
     "look_at_dir": "right",
     "actions": {
       "look": [
         {"type": "say", "speaker": "player", "text": "One of the floorboards is loose."}
       ],
       "use": [
         {"type": "say", "speaker": "player", "text": "There's a coin hidden underneath!"},
         {"type": "give_item", "item_id": "silver_coin"},
         {"type": "play_sfx", "sfx": "sounds/sfx/item_pickup.ogg"},
         {"type": "disable_hotspot", "hotspot_id": "loose_floorboard"},
         {"type": "set_flag", "flag": "found_coin", "value": true}
       ]
     }
   }
   ```

3. **Add puzzle metadata** to `data/puzzles.json`:
   ```json
   {
     "id": "use_vending_machine",
     "name": "The Mysterious Vending Machine",
     "description": "Find a coin to use in the old vending machine",
     "hints": [
       "Look around the tavern floor carefully.",
       "One of the floorboards seems loose.",
       "Use the loose floorboard near the bar to find a silver coin, then use it on the vending machine."
     ],
     "completion_flag": "used_vending_machine"
   }
   ```

### Common Puzzle Patterns
- **Key-and-lock**: Item `use_on` a hotspot → `remove_item` + `set_flag` + `disable_hotspot` + `enable_hotspot`
- **Fetch quest**: NPC dialogue checks for item (`has_item` condition) → gives different dialogue/reward
- **Multi-step**: Chain of flags — each step enables the next hotspot/dialogue option
- **Combine items**: `combinable_with` → removes both items, gives new one

---

## How To: Add a New Dialogue Tree

1. **Create** `data/dialogues/your_dialogue.json`:
   ```json
   {
     "id": "your_dialogue",
     "nodes": {
       "start": {
         "type": "say",
         "speaker": "bartender",
         "text": "What can I do for you?",
         "next": "main_choices"
       },
       "main_choices": {
         "type": "choice",
         "choices": [
           {"text": "I need information.", "next": "info"},
           {"text": "Nothing, sorry.", "next": "goodbye"}
         ]
       },
       "info": {
         "type": "say",
         "speaker": "bartender",
         "text": "Information costs money around here.",
         "next": "main_choices"
       },
       "goodbye": {
         "type": "end"
       }
     }
   }
   ```

2. **Wire it up** — either via a character's `dialogue_id` in `characters.json`, or via a hotspot talk action:
   ```json
   "talk": [
     {"type": "start_dialogue", "dialogue_id": "your_dialogue"}
   ]
   ```

### Dialogue Patterns
- **Conditional start node**: Use `"type": "conditional"` as the start node to give different greetings based on game progress
- **Gated choices**: Add `"condition"` to individual choices to show/hide them based on flags
- **Mid-dialogue actions**: Use `"type": "action"` nodes to set flags or give items between speech nodes
- **Looping**: Point a node's `next` back to a choice node to let the player ask multiple questions
- **Progressive dialogue**: Use conditions at the start node to branch to entirely different conversation trees based on story progress

---

## How To: Add a New Character

1. **Add to** `data/characters.json`:
   ```json
   {
     "id": "guard",
     "name": "Town Guard",
     "sprite": "sprites/guard_standing",
     "scene_id": "village_gate",
     "x": 800,
     "y": 550,
     "facing": "left",
     "speed": 120,
     "dialogue_id": "guard_dialogue"
   }
   ```

2. **Add sprite** — at minimum, place `assets/sprites/guard_standing/1.png` (a single standing frame). The engine flips it for left/right facing.

3. **Add the NPC to a scene** — in the scene JSON's `npcs` array:
   ```json
   "npcs": ["guard"]
   ```

4. **Add a talk hotspot** (usually overlapping the character's position):
   ```json
   {
     "id": "guard_hs",
     "name": "Town Guard",
     "rect": [750, 400, 100, 200],
     "walk_to": [700, 550],
     "look_at_dir": "right",
     "actions": {
       "look": [{"type": "say", "speaker": "player", "text": "A stern-looking guard."}],
       "talk": [{"type": "start_dialogue", "dialogue_id": "guard_dialogue"}]
     }
   }
   ```

5. **Create the dialogue** — `data/dialogues/guard_dialogue.json`

### Companion Character
The engine supports an auto-following companion (like a pet or sidekick):
- Follows the player when distance > threshold (default 70px)
- Pathfinds using the scene's walkable area
- Moves slightly faster (1.1x) to catch up
- Configurable in `character.py` — the companion class has follow distance, speed multiplier, and target offset settings

---

## Key Design Patterns

### Y-Sorting for Depth
All visible entities (player, companion, NPCs) are sorted by Y coordinate before drawing. Lower Y = farther back = drawn first. This creates natural depth overlap.

### Depth Scaling
Characters scale linearly between `min_scale` (at `horizon_y`) and `max_scale` (at `ground_y`):
```
t = (y - horizon_y) / (ground_y - horizon_y)
scale = min_scale + (max_scale - min_scale) * clamp(t, 0, 1)
```

### Scene Change Sequence
1. `change_scene()` starts a fade-out transition
2. At the midpoint (full black): run old scene's `on_exit`, clear speech, load new scene
3. `_apply_scene()`: set camera bounds, player depth config, place player at entry point, place companion nearby, load NPCs, play music, run `on_enter`
4. Fade-in reveals the new scene

### Script Execution Flow
1. `ScriptRunner.run(actions, callback)` queues an action list
2. `_execute_next()` pops the first action, dispatches to its handler
3. **Blocking** handlers set `waiting=True` and store a resume callback
4. When the blocking action completes (e.g. speech dismissed), it calls `_on_blocking_done()`
5. Queue continues until empty, then fires the completion callback

### Hotspot Interaction Flow
1. Right-click on hotspot → radial menu appears
2. Player picks an action (Look, Use, Pick up, Talk)
3. Player auto-walks to the hotspot's `walk_to` point
4. Player faces the hotspot's `look_at_dir`
5. Script actions for that action key execute

### Item Use-On Flow
1. Player clicks an item in the inventory bar (selects it, cursor changes)
2. Player clicks a hotspot in the world
3. Engine checks `item.use_on[hotspot.id]`
4. If match found: walk to hotspot → face it → run the script → deselect item
5. If no match: show default "can't use that here" message → deselect item

### The Hotspot Enable/Disable Pattern
A very common pattern for state-changing interactions:
```json
"use_on": {
  "locked_door": [
    {"type": "remove_item", "item_id": "key"},
    {"type": "set_flag", "flag": "door_unlocked", "value": true},
    {"type": "disable_hotspot", "hotspot_id": "locked_door"},
    {"type": "enable_hotspot", "hotspot_id": "open_door"}
  ]
}
```
This replaces the "locked door" hotspot with an "open door" hotspot, changing available actions.

---

## Debug Tools

### F1 Debug Mode
- **Green overlay** for walkable areas (semi-transparent green on masks, polygon outlines)
- **Red rectangles** around all hotspots with name labels
- **Red rectangles** around all exits with target scene labels
- **Red crosshairs** at entry points with name labels
- **Red rectangles** around all entity sprites (player, companion, NPCs)
- **Red dot** at player's foot anchor point
- **Top-left HUD**: Mouse position in world coords and screen coords
- **Bottom-left HUD**: FPS, scene ID, player position + scale, camera offset, flag count

### Console Output
- Save/load confirmations
- Missing scene warnings
- Mixer initialization failures (non-blocking)

---

## Constants & Tuning

All constants live in `engine/settings.py`. Key values:

### Player Identity
| Constant | Default | Description |
|----------|---------|-------------|
| `PLAYER_ID` | `"player"` | Default speaker/actor ID in scripts and dialogues |

### Display
| Constant | Default | Description |
|----------|---------|-------------|
| `SCREEN_WIDTH` | 1280 | Window width in pixels |
| `SCREEN_HEIGHT` | 720 | Window height in pixels |
| `FPS` | 60 | Target frame rate |

### Movement
| Constant | Default | Description |
|----------|---------|-------------|
| `WALK_SPEED` | 180 | Player walk speed (px/s) |
| `RUN_SPEED` | 340 | Player run speed (px/s) |
| `ANIM_FPS` | 8 | Character animation frames per second |
| `DOUBLE_CLICK_TIME` | 0.35 | Double-click detection window (seconds) |

### Depth Scaling Defaults
| Constant | Default | Description |
|----------|---------|-------------|
| `DEFAULT_HORIZON_Y` | 200 | Far/small end |
| `DEFAULT_GROUND_Y` | 680 | Near/large end |
| `DEFAULT_MIN_SCALE` | 0.4 | Scale at horizon |
| `DEFAULT_MAX_SCALE` | 1.0 | Scale at ground |

### Camera
| Constant | Default | Description |
|----------|---------|-------------|
| `CAMERA_SMOOTHING` | 5.0 | Follow interpolation (higher = snappier) |
| `CAMERA_DEAD_ZONE` | 50 | Pixels from center before camera moves |

### UI
| Constant | Default | Description |
|----------|---------|-------------|
| `INVENTORY_HEIGHT` | 80 | Inventory bar height in pixels |
| `INVENTORY_SLOT_SIZE` | 64 | Item slot dimensions |
| `INVENTORY_SLIDE_SPEED` | 400 | Slide animation speed (px/s) |
| `RADIAL_RADIUS` | 60 | Radial menu distance from center |
| `RADIAL_ICON_SIZE` | 32 | Radial menu icon size |

### Speech Bubbles
| Constant | Default | Description |
|----------|---------|-------------|
| `SPEECH_FONT_SIZE` | 20 | Normal text size |
| `SPEECH_SHOUT_FONT_SIZE` | 24 | Shout style text size |
| `SPEECH_TYPEWRITER_SPEED` | 40 | Characters per second |
| `SPEECH_MAX_WIDTH` | 300 | Max bubble width |
| `SPEECH_PADDING` | 12 | Inner padding |

### Sound
| Constant | Default | Description |
|----------|---------|-------------|
| `MUSIC_VOLUME` | 0.5 | Background music volume (0-1) |
| `SFX_VOLUME` | 0.7 | Sound effect volume (0-1) |
| `MUSIC_FADEOUT_MS` | 1000 | Music crossfade duration |

### Transitions
| Constant | Default | Description |
|----------|---------|-------------|
| `FADE_DURATION` | 0.5 | Default fade time in seconds |

### Colours
| Constant | RGB(A) | Usage |
|----------|--------|-------|
| `COLOR_SPEECH_BG` | (255, 255, 240) | Speech bubble fill |
| `COLOR_SPEECH_BORDER` | (40, 40, 40) | Speech bubble outline |
| `COLOR_INVENTORY_BG` | (45, 35, 25, 220) | Inventory bar background |
| `COLOR_INVENTORY_SLOT` | (80, 65, 50) | Empty slot colour |
| `COLOR_INVENTORY_HIGHLIGHT` | (200, 170, 100) | Selected slot highlight |
| `COLOR_MENU_BG` | (50, 40, 30, 230) | Radial menu background |
| `COLOR_MENU_TEXT` | (240, 220, 180) | Menu text |
| `COLOR_MENU_HIGHLIGHT` | (255, 200, 80) | Menu hover |
| `COLOR_DIALOGUE_BG` | (0, 0, 0, 180) | Dialogue choice panel |
| `COLOR_DIALOGUE_CHOICE` | (240, 220, 180) | Choice text |
| `COLOR_DIALOGUE_HOVER` | (255, 200, 80) | Choice hover |
| `COLORKEY_MAGENTA` | (255, 0, 255) | Sprite transparency key |

### Sprite Scaling
| Constant | Default | Description |
|----------|---------|-------------|
| `PLAYER_SPRITE_SCALE` | 0.295 | Scale factor for real player walk sprites |
| `COMPANION_SPRITE_SCALE` | 0.18 | Scale factor for real companion walk sprites |
| `PLACEHOLDER_SCALE` | 2 | Scale multiplier for placeholder sprites |

### Fonts
| Constant | Default | Description |
|----------|---------|-------------|
| `FONT_NORMAL` | `"adventure.ttf"` | Normal speech font filename (in assets/fonts/) |
| `FONT_SHOUT` | `"adventure_shout.ttf"` | Shout speech font filename (in assets/fonts/) |

### Companion AI
| Constant | Default | Description |
|----------|---------|-------------|
| `COMPANION_FOLLOW_DISTANCE` | 70 | Min distance before companion follows |
| `COMPANION_FOLLOW_SPEED_MULT` | 1.1 | Speed multiplier when catching up |

---

## Save/Load System

- **F5** saves to `saves/save_1.json`
- **F9** loads from `saves/save_1.json`
- Save file contains: all flags, inventory items, current scene, player position, visited scenes
- On load: scene is fully reloaded, player repositioned, inventory restored, NPCs refreshed

Save format:
```json
{
  "flags": {"talked_to_bartender": true, "coins": 3},
  "inventory_items": ["brass_key", "old_map"],
  "current_scene": "tavern",
  "player_pos": [500, 600],
  "visited_scenes": ["tavern", "village_street"],
  "dialogue_states": {}
}
```

---

## Quick Checklist: Adding Content

### New Scene
- [ ] Create `data/scenes/scenename.json` with all required fields
- [ ] Add background PNG to `assets/backgrounds/`
- [ ] Optionally add `scenename_walkable.png` mask
- [ ] Add exit(s) in other scenes pointing to this scene
- [ ] Add entry points matching the exit names from other scenes
- [ ] Test with F1 debug to verify walkable area and hotspot rects

### New Item
- [ ] Add entry to `data/items.json` with id, name, icon, examine_text
- [ ] Add icon PNG to `assets/items/`
- [ ] Add `use_on` entries for relevant hotspots
- [ ] Add pickup hotspot(s) in scene(s) with `give_item` action
- [ ] Add `disable_hotspot` after pickup so item can't be picked up twice

### New Character
- [ ] Add entry to `data/characters.json`
- [ ] Add sprite(s) to `assets/sprites/character_name/`
- [ ] Add character ID to the scene's `npcs` array
- [ ] Add talk hotspot overlapping the character
- [ ] Create dialogue tree in `data/dialogues/`

### New Puzzle
- [ ] Define the items, hotspots, and flags involved
- [ ] Wire up the use_on / pickup / dialogue scripts
- [ ] Add initial flags to `story_flags.json` (usually `false`)
- [ ] Add puzzle metadata to `puzzles.json`
- [ ] Test the full puzzle flow end-to-end
