# StructuralView — Design Document

## Goal

StructuralView is an argument ribbon viewer for rhetorical tag annotations produced by The Vehicle's two-pass annotation system. It makes the deep structure of cognitive science paper Introductions visible — using color, space, and shape to give a cognitive foothold on rhetorical patterns that are otherwise only readable as flat text.

The primary display unit is the **argument ribbon**: sentences laid out sequentially in reading order, each rendered as a colored block labeled with its tag. Secondary-tagged sentences are indented under their primary parent. The viewer emphasizes **linear sequence over tree structure** — reading order is argument flow, and that is the primary thing to see.

## What It Displays

Each sentence block shows:
- Tag name and color (primary tags in full saturation; secondary tags desaturated/indented)
- Sentence text (full, readable inline)
- Note field on hover or expansion
- Parent relationship implied by indentation depth

Future layers (data fields already present in the schema, currently null):
- CARS move assignment (`cars_move`: M1 / M2 / M3)
- CARS step (`cars_step`: e.g. 1A, 2B, 3C)
- Toggle between papers for cross-paper comparison

## Resources

| Resource | Location |
|---|---|
| Annotation JSON files | `data/` (4 papers) |
| Parser (annotation .txt → JSON) | `../vehicle_annotation/parser.py` |
| Annotation source files (.txt) | `../vehicle_annotation/annotations/` |
| Tag vocabulary + prompt docs | Notion: Claude Project Setup — Tag Annotator (subpage of ONT-64) |

### JSON Schema (per sentence)

```json
{
  "id": 1,
  "text": "Sentence text.",
  "tag": "emph",
  "tier": "primary",
  "parent_id": null,
  "note": null,
  "cars_move": null,
  "cars_step": null
}
```

### Tag Vocabulary

**Primary** (full color): `tempstat` · `emph` · `contrast` · `nostat` · `novstat` · `contribution` · `framedef`

**Secondary** (desaturated, indented): `extension:speculative` · `extension:definitional` · `extension:illustrative` · `link:opening` · `link:closing`

## Tech Approach

Self-contained HTML/JS — no build tooling, no server, no dependencies beyond the browser. Open `src/index.html` directly. JSON data loaded from `../data/` via fetch or inline. Viewer should work offline.

Color palette, layout, and interactivity handled in vanilla JS + CSS. No framework. Keep it simple enough that the rendering logic is easy to read and modify.

## Workflow

**Prototype first.** Get a working ribbon view of one paper on screen as fast as possible. It doesn't have to be pretty — it has to be informative. The primary milestone is: open index.html, see the Aswamenakul annotation as a color-coded ribbon, understand the argument structure at a glance.

**Lazy iteration after that.** Major changes (paper switcher, CARS move overlay, cross-paper comparison, better typography, export) come back to when the data layer is richer and the use cases are clearer. Don't over-engineer the prototype.

## Current Data

| Paper | Sentences | Status |
|---|---|---|
| Aswamenakul et al. (2025) | 40 | Tags complete · CARS pending |
| Ryskin et al. (2025) | 18 | Tags complete · CARS pending |
| Kello & Bruna (2023) | 23 | Tags complete · CARS pending |
| Hart et al. (2017) | 47 | Tags complete · CARS pending |
