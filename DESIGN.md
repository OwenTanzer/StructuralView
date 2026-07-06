# StructuralView — Design Document

## Goal

StructuralView is an argument structure viewer for rhetorical annotations produced by The Vehicle's annotation pipeline. It makes the deep structure of cognitive science paper Introductions visible — using color, space, and shape to give a cognitive foothold on rhetorical patterns that are otherwise only readable as flat text.

Two primary display modes:

- **Tag Mode** — sentences laid out in reading order, each rendered as a colored chip labeled with its rhetorical tag. Secondary-tagged sentences are indented under their primary parent. Emphasizes linear sequence over tree structure: reading order is argument flow.
- **Move Mode** — CARS move-level view showing the arc formula (M1→M2→M3 sequence), a proportional arc strip, step-tick strip, per-segment role tooltips on hover, a rendered arc summary, and move stat cards. Emphasizes argument shape over sentence-level detail.

## What It Displays

### Tag Mode
- Tag name and color (primary tags in full saturation; secondary tags desaturated/indented)
- Sentence text inline
- Note field (reviewer annotation visible inline)
- Parent relationship implied by indentation

### Move Mode
- **Arc summary** — 3–4 sentence markdown description of the introduction's rhetorical shape
- **Formula pills** — M1/M2/M3 pills in sequence with tooltips showing span and role description on hover
- **Arc strip** — proportional colored bar per move block; hover reveals segment role
- **Step-tick strip** — one tick per sentence, colored by CARS step (1A–3C)
- **Stat cards** — per-move sentence count, percentage, and step breakdown

### Paper selector
Two dropdowns in the header — **Drafts** (own papers under analysis) and **Corpus** (citation papers). Categorized by `DRAFT_STEMS` set in `build.py`. Selecting from one dropdown resets the other.

## Resources

| Resource | Location |
|---|---|
| Annotated JSON files (with CARS data) | `annotated/` (42 papers) |
| Raw tag JSON files | `data/` (42 papers) |
| Build script | `build.py` |
| Annotation pipeline | `../vehicle_annotation/annotate.py` |
| GitHub | https://github.com/OwenTanzer/StructuralView |

### JSON Schema

**Per-sentence fields:**
```json
{
  "id": 1,
  "text": "Sentence text.",
  "tag": "emph",
  "tier": "primary",
  "parent_id": null,
  "note": null,
  "cars_move": "M1",
  "cars_step": "1A",
  "paragraph": null
}
```

`paragraph` (optional, int or null) — 1-indexed source paragraph number. Most
papers don't track this; it's mainly useful for our own drafts under revision,
where paragraph-level structure matters. When present, Tag Mode renders a
divider each time the paragraph number changes. Populate it by running
`annotate.py` with `--track-paragraphs`.

**Paper-level fields (in annotated/ JSONs):**
```json
{
  "arc_summary": "Markdown prose description of the introduction's rhetorical shape.",
  "structured_arc": "M1 -> M2 -> M3",
  "move_roles": [
    { "move": "M1", "span": [1, 9], "role": "Establishes territory..." }
  ],
  "gloss_version": "v0.3"
}
```

### Tag Vocabulary

**Primary** (full color): `tempstat` · `emph` · `contrast` · `nostat` · `novstat` · `contribution` · `framedef`

**Secondary** (desaturated, indented): `extension:speculative` · `extension:definitional` · `extension:illustrative` · `link:opening` · `link:closing`

### CARS Moves

| Move | Label | Color |
|------|-------|-------|
| M1 | Establishing Territory | Orange |
| M2 | Establishing Niche | Purple |
| M3 | Occupying the Niche | Green |

## Tech Approach

Self-contained HTML/JS — no build tooling, no server, no dependencies beyond the browser. `build.py` inlines all paper data and generates `src/index.html`. Open directly in any browser; works offline.

Color palette, layout, and interactivity in vanilla JS + CSS. No framework. The rendering logic is intentionally readable and easy to modify.

`build.py` reads from `data/` (raw tag JSONs) and `annotated/` (CARS-annotated JSONs), preferring the annotated version when available. Rebuild takes under 1 second for 42 papers.

## Workflow

1. Run annotation pipeline: `python ../vehicle_annotation/annotate.py paper.pdf --cars --gloss`
2. Output lands in `annotated/<stem>_annotated.json`
3. Run `python build.py` to rebuild `src/index.html`
4. Open `src/index.html` in browser

To add a draft paper to the Drafts dropdown: add its stem to `DRAFT_STEMS` in `build.py`.

## Current Data

| Corpus | Papers | Sentences | Status |
|--------|--------|-----------|--------|
| CogSci corpus | 41 | 1,663 | All 4 passes complete |
| Own drafts | 1 (tanzer_2yp) | 54 | All 4 passes complete |
| **Total** | **42** | **1,717** | |

Arc formula survey (corpus only): 22 unique arc patterns; 76% of papers have all 3 moves; dominant pattern M1→M2→M3 (×12).
