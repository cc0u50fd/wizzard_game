# Art Prompts — Wizard Detective Demo

All assets use the engine's placeholder system, so the game is fully playable without any real art.
When ready, generate these assets and drop them into the `assets/` directories.

---

## Backgrounds (1280x720 PNG)

### Waiting Room — `assets/backgrounds/waiting_room.png`
> A shabby waiting room above a kebab shop. Peeling wallpaper (faded green/brown), scuffed linoleum floor, fluorescent strip light with a flicker. Three bolted-together plastic chairs in the centre. A reception desk/counter on the left side with piles of filing trays. A noticeboard on the back wall covered in yellowed notices. A water cooler in the middle-back. A sad plastic potted plant in the corner. A magazine rack near the chairs. A frosted glass door on the right side labelled "GRIMSHAW & ASSOCIATES". The room feels cramped, slightly grimy, and deeply unglamorous. Point-and-click adventure game style, detailed 2D background, slightly exaggerated proportions, warm but dingy lighting.

### Detective's Office — `assets/backgrounds/detectives_office.png`
> A cramped private detective's office. A large wooden desk dominates the centre-right, buried under takeaway containers, papers, and a crystal ball. A leather office chair behind it. A tall filing cabinet on the right wall. A full bookshelf on the far right. A hat stand near the door on the left with a fedora hanging on it. A wanted poster on the left wall. A window on the back wall showing a grey street outside. The room is messy but has character — it's the office of someone who was once competent and is now just tired. Point-and-click adventure game style, detailed 2D background, warm amber lighting from a desk lamp, dust motes in the air.

---

## Character Sprites

### Ethel Copperbottom — `assets/sprites/ethel_standing/1.png`
**Dimensions:** ~80x150 px (will be depth-scaled by engine)
> A sentient filing golem receptionist. She's made of stacked filing cards, manila folders, and brass index tabs. Her body is a rectangular card catalogue cabinet shape. Her head is a drawer with a brass label holder as a face — reading glasses perched on the edge. Her arms are articulated card strips. She wears a tiny cardigan draped over her boxy shoulders. Her expression is one of permanent, refined disapproval. Right-facing, magenta (#FF00FF) or transparent background. Point-and-click adventure game character sprite.

### Gerald — `assets/sprites/gerald_standing/1.png`
**Dimensions:** ~100x180 px (will be depth-scaled by engine)
> An anxious minotaur in a cheap off-the-rack business suit. Large bull head with short horns, worried brown eyes, and a nervous expression. The suit is grey, too tight across the shoulders, with the sleeves slightly too short for his massive arms. He's wearing a clip-on tie that's slightly crooked. His hooves stick out of the trouser legs. He looks like a school kid who's been sent to the headmaster's office. Standing pose, slightly hunched with anxiety, fidgeting with his hands. Right-facing, magenta (#FF00FF) or transparent background. Point-and-click adventure game character sprite.

### Player Walk Cycle (Mortimer Grimshaw) — `assets/sprites/player_walk/1.png` through `8.png`
**Dimensions:** ~60x140 px per frame
> A burnt-out wizard private investigator. Late 40s, gaunt face, permanent five o'clock shadow, tired eyes that have seen too much (and drank even more). Wearing a rumpled trench coat over a waistcoat, shirt with the top button undone, no tie. A slightly wonky wizard's hat that's seen better days — brim bent, tip flopping. Carrying himself like someone who used to have dignity and is now just going through the motions. 8-frame walk cycle, right-facing, magenta (#FF00FF) or transparent background. Point-and-click adventure game character sprite.

---

## Item Icons (56x56 PNG, transparent background)

### Hip Flask — `assets/items/hip_flask.png`
> A dented silver hip flask, slightly tarnished, with a worn leather wrap around the middle. A few scratches and dings. It looks well-used and empty. Clean line art style, transparent background, suitable for inventory icon.

### Filing Reference Card — `assets/items/filing_reference.png`
> A small rectangular card (like an index card), cream/off-white, with neat handwriting in dark ink. A red reference number at the top. A small brass filing tab clip at the top edge. Clean and precise — clearly made by someone (or something) very organised. Clean line art style, transparent background, suitable for inventory icon.

### Case File — `assets/items/case_file.png`
> A manila folder/case file, slightly thick with papers inside. A handwritten label on the tab reads "GERALD". A red "URGENT" stamp visible on the front. A few papers poking out of the edges. Clean line art style, transparent background, suitable for inventory icon.

---

## Audio (OGG format, optional)

### Music
- `assets/sounds/music/waiting_room.ogg` — Muzak-style hold music, slightly off-key, the kind you hear in a dentist's waiting room. Lo-fi, tinny, repetitive. Maybe 30-60 seconds, loopable.
- `assets/sounds/music/office_theme.ogg` — Jazz noir piano, but played slightly badly. Think film noir detective music performed by someone who learned piano from a correspondence course. Low-key, atmospheric, loopable.

### Sound Effects
- `assets/sounds/sfx/drawer_open.ogg` — Metal filing cabinet drawer sliding open with a slight squeak.
- `assets/sounds/sfx/item_pickup.ogg` — Satisfying "got it" sound — a soft chime or rustle.

---

## Recommended Generation Order

1. **Backgrounds first** — these set the visual tone for everything
2. **Player walk cycle** — 8 frames, most visible character
3. **NPCs** — Ethel and Gerald standing sprites
4. **Item icons** — small, can be quick sketches
5. **Audio** — nice to have, game works silently

## Style Notes

- **Tone:** Warm but dingy. Think Terry Pratchett meets film noir meets a British council office.
- **Palette:** Browns, ambers, faded greens, worn wood, scuffed leather. Pops of colour from magic items (crystal ball glow, Ethel's brass fittings).
- **Detail level:** Enough to be interesting on close inspection, but readable at game scale. Think LucasArts adventure game backgrounds — busy but composed.
- **Character proportions:** Slightly exaggerated — big heads, expressive hands/faces. Not realistic, but grounded enough to sell the comedy.
