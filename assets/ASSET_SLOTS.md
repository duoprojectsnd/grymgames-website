# OKUBI Website — Asset Slot Reference

Drop your files into the correct subfolder and name them using the **slot code** below.  
Accepted formats: `.jpg`, `.png`, `.webp` for images — `.mp4`, `.webm` for videos.  
Just tell me "I added assets" and I'll wire them in.

---

## 📁 `assets/home/` — Main Landing Page

| Slot Code | Type | Description |
|-----------|------|-------------|
| `HERO-BG` | video/image | Full-screen hero background (top of page) |
| `WELCOME-BG` | image | Welcome showcase section background |
| `WELCOME-SIDE` | image | Welcome showcase offset side image (right of text, gradient-faded top) |
| `ABOUT-PREVIEW` | video/image | Gameplay preview in the About section |
| `FEAT-01` | image | Feature carousel — Crafting slide background |
| `FEAT-02` | image | Feature carousel — Dynamic World Events slide |
| `FEAT-03` | image | Feature carousel — Player-Driven Economy slide |
| `FEAT-04` | image | Feature carousel — Arenas slide |
| `FEAT-05` | image | Feature carousel — Planet Incursion slide |
| `FEAT-06` | image | Feature carousel — Gathering slide |
| `COMBAT-BG` | image | Combat showcase ("Wings of War") background |
| `WORLD-BG` | image | World/Corruption showcase background |
| `FOUNDER-IMG` | image | Founder's Bundle promo image |

### Archetype Cards (main page carousel)

| Slot Code | Type | Description |
|-----------|------|-------------|
| `CARD-reaper` | image | Reaper card thumbnail |
| `CARD-berserker` | image | Berserker card thumbnail |
| `CARD-guardian` | image | Guardian card thumbnail |
| `CARD-pathfinder` | image | Pathfinder card thumbnail |
| `CARD-invoker` | image | Invoker card thumbnail |
| `CARD-assassin` | image | Assassin card thumbnail |
| `CARD-tempest` | image | Tempest card thumbnail (placeholder class) |
| `CARD-pyromancer` | image | Pyromancer card thumbnail (placeholder class) |
| `CARD-warden` | image | Warden card thumbnail (placeholder class) |
| `CARD-crystalmancer` | image | Crystalmancer card thumbnail (placeholder class) |
| `CARD-voidwalker` | image | Voidwalker card thumbnail (placeholder class) |

---

## 📁 `assets/classes/` — Archetype Detail Pages

For each class, replace `{CLASS}` with: `reaper`, `berserker`, `guardian`, `pathfinder`, `invoker`, `assassin`

| Slot Code | Type | Description |
|-----------|------|-------------|
| `{CLASS}-lore-1` | image | First lore image (concept art) |
| `{CLASS}-lore-2` | image | Second lore image (in-combat) |
| `{CLASS}-spell-1` | video | Spell 1 preview video (Slot 1 — top-left ability) |
| `{CLASS}-spell-2` | video | Spell 2 preview video |
| `{CLASS}-spell-3` | video | Spell 3 preview video |
| `{CLASS}-spell-4` | video | Spell 4 preview video |
| `{CLASS}-spell-5` | video | Spell 5 preview video |
| `{CLASS}-spell-6` | video | Spell 6 preview video |
| `{CLASS}-spell-7` | video | Spell 7 preview video |
| `{CLASS}-spell-8` | video | Spell 8 preview video (Ultimate) |

**Example:** `reaper-lore-1.jpg`, `reaper-spell-3.mp4`

---

## 📁 `assets/factions/` — Faction Section

| Slot Code | Type | Description |
|-----------|------|-------------|
| `SOL-emblem` | image | Solari Covenant emblem/crest |
| `SOL-lore` | image | Solari lore panel image |
| `UMBRA-emblem` | image | Umbral Pact emblem/crest |
| `UMBRA-lore` | image | Umbral lore panel image |

---

## Total Slots: ~75

### Quick count
- Home page: 12 backgrounds + 11 class cards = **23**
- Class pages: 6 classes × (2 lore + 8 spells) = **60**
- Factions: **4**
