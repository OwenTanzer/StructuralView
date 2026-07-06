#!/usr/bin/env python3
"""
StructuralView build script.
Reads JSON from data/ (and annotated/ for CARS data) and generates src/index.html.
Run from the StructuralView directory: python build.py
"""

import json
import webbrowser
from pathlib import Path

TAG_COLORS = {
    'tempstat':               '#4F86C6',
    'emph':                   '#D4883A',
    'contrast':               '#C85252',
    'nostat':                 '#8960B8',
    'novstat':                '#3FAD72',
    'contribution':           '#2EA898',
    'framedef':               '#B8901E',
    'extension:speculative':  '#D4C4E8',
    'extension:definitional': '#C0D4E8',
    'extension:illustrative': '#C0DCC8',
    'link:opening':           '#DDD4C4',
    'link:closing':           '#C4C8D4',
}

TAG_LABELS = {
    'tempstat':               'tempstat',
    'emph':                   'emph',
    'contrast':               'contrast',
    'nostat':                 'nostat',
    'novstat':                'novstat',
    'contribution':           'contribution',
    'framedef':               'framedef',
    'extension:speculative':  'ext·speculative',
    'extension:definitional': 'ext·definitional',
    'extension:illustrative': 'ext·illustrative',
    'link:opening':           'link·opening',
    'link:closing':           'link·closing',
}

MOVE_COLORS = {
    'M1': '#D4883A',
    'M2': '#8960B8',
    'M3': '#3FAD72',
}

MOVE_LABELS = {
    'M1': 'Establishing Territory',
    'M2': 'Establishing Niche',
    'M3': 'Occupying Niche',
}

STEP_COLORS = {
    '1A': '#F5B870', '1B': '#D4883A', '1C': '#A86020',
    '2A': '#C0A0E0', '2B': '#8960B8', '2C': '#60409A', '2D': '#D8C8F0',
    '3A': '#80D4A0', '3B': '#3FAD72', '3C': '#248A50', '3D': '#106830',
}

PRIMARY_TAGS   = ['tempstat','emph','contrast','nostat','novstat','contribution','framedef']
SECONDARY_TAGS = ['extension:speculative','extension:definitional',
                  'extension:illustrative','link:opening','link:closing']

# Paper IDs that are own drafts (shown in Drafts dropdown, not Corpus)
DRAFT_STEMS = {'tanzer_2yp', 'tanzer_2yp_ideal'}


def build(open_browser: bool = True):
    data_dir      = Path(__file__).parent / 'data'
    annotated_dir = Path(__file__).parent / 'annotated'
    out_path      = Path(__file__).parent / 'src' / 'index.html'
    out_path.parent.mkdir(exist_ok=True)

    # Load annotated papers keyed by paper id
    annotated = {}
    if annotated_dir.exists():
        for f in annotated_dir.glob('*.json'):
            p = json.loads(f.read_text(encoding='utf-8'))
            annotated[p['paper']['id']] = p

    # Load data papers, prefer annotated version when available
    papers = []
    for f in sorted(data_dir.glob('*.json')):
        p = json.loads(f.read_text(encoding='utf-8'))
        pid = p['paper']['id']
        papers.append(annotated.get(pid, p))

    # Load outline files (ideal arc structures — paragraph-level blocks, no sentences)
    outlines_dir = Path(__file__).parent / 'outlines'
    if outlines_dir.exists():
        for f in sorted(outlines_dir.glob('*.json')):
            p = json.loads(f.read_text(encoding='utf-8'))
            papers.append(p)

    draft_ids = {p['paper']['id'] for p in papers if p['paper']['id'] in DRAFT_STEMS}
    html = render_html(papers, draft_ids)
    out_path.write_text(html, encoding='utf-8')

    annotated_count = sum(
        1 for p in papers
        if p.get('sentences') and any(s.get('cars_move') for s in p['sentences'])
    )
    print(f'Built {out_path}  ({len(papers)} papers, '
          f'{sum(len(p.get("sentences", [])) for p in papers)} sentences, '
          f'{annotated_count} with CARS data)')

    if open_browser:
        webbrowser.open(out_path.resolve().as_uri())


def render_html(papers: list, draft_ids: set) -> str:
    papers_js      = json.dumps(papers,          ensure_ascii=False, separators=(',', ':'))
    draft_ids_js   = json.dumps(list(draft_ids), ensure_ascii=False)
    colors_js      = json.dumps(TAG_COLORS,      ensure_ascii=False)
    labels_js      = json.dumps(TAG_LABELS,      ensure_ascii=False)
    primary_js     = json.dumps(PRIMARY_TAGS)
    secondary_js   = json.dumps(SECONDARY_TAGS)
    move_colors_js = json.dumps(MOVE_COLORS,     ensure_ascii=False)
    move_labels_js = json.dumps(MOVE_LABELS,     ensure_ascii=False)
    step_colors_js = json.dumps(STEP_COLORS,     ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StructuralView</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #F5F3EF;
  color: #222;
  min-height: 100vh;
}}

/* ── Header ─────────────────────────────────────────────── */
.app-header {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid #DDD;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  height: 52px;
}}

.app-title {{
  font-size: 15px;
  font-weight: 700;
  letter-spacing: .04em;
  color: #333;
  white-space: nowrap;
}}

.paper-selectors {{
  display: flex;
  gap: 10px;
  flex: 1;
  align-items: center;
}}

.select-group {{
  display: flex;
  align-items: center;
  gap: 6px;
}}

.select-label {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #999;
  white-space: nowrap;
}}

.paper-select {{
  padding: 5px 28px 5px 10px;
  border: 1px solid #CCC;
  border-radius: 6px;
  background: #fff;
  font-size: 12px;
  font-weight: 500;
  color: #333;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23999'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 9px center;
  max-width: 220px;
}}
.paper-select:focus {{ outline: none; border-color: #888; }}
.paper-select.has-selection {{ border-color: #888; color: #111; font-weight: 600; }}

.mode-toggle {{
  display: flex;
  border: 1px solid #CCC;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}}
.mode-btn {{
  padding: 5px 14px;
  border: none;
  background: transparent;
  font-size: 11px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  letter-spacing: .03em;
  transition: background .1s, color .1s;
}}
.mode-btn:hover {{ background: #F0EDE8; }}
.mode-btn.active {{ background: #222; color: #fff; }}

.legend-toggle {{
  padding: 5px 12px;
  border: 1px solid #CCC;
  background: transparent;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: #555;
  cursor: pointer;
  white-space: nowrap;
}}
.legend-toggle:hover {{ background: #F0EDE8; }}

/* ── Layout ──────────────────────────────────────────────── */
.app-body {{
  display: flex;
  gap: 0;
}}

/* ── Legend ──────────────────────────────────────────────── */
.legend {{
  width: 200px;
  min-width: 200px;
  padding: 20px 16px;
  border-right: 1px solid #DDD;
  background: #fff;
  position: sticky;
  top: 52px;
  height: calc(100vh - 52px);
  overflow-y: auto;
  display: none;
}}
.legend.visible {{ display: block; }}

.legend-section-label {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: #999;
  margin: 14px 0 6px;
}}
.legend-section-label:first-child {{ margin-top: 0; }}

.legend-item {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}}

.legend-chip {{
  display: inline-block;
  width: 28px;
  height: 18px;
  border-radius: 4px;
  flex-shrink: 0;
}}

.legend-label {{
  font-size: 11px;
  color: #444;
}}

/* ── Ribbon ──────────────────────────────────────────────── */
.ribbon {{
  flex: 1;
  padding: 28px 32px 60px;
  max-width: 900px;
}}

.paper-meta {{
  margin-bottom: 24px;
}}
.paper-meta h2 {{
  font-size: 16px;
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
}}
.paper-meta .authors {{
  font-size: 12px;
  color: #777;
}}

/* ── Tag mode ────────────────────────────────────────────── */
.sentence-row {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 5px 0;
  border-radius: 6px;
  transition: background .08s;
}}
.sentence-row:hover {{ background: rgba(0,0,0,.03); }}
.sentence-row.is-secondary {{ padding-left: 36px; }}

.sentence-num {{
  font-size: 10px;
  color: #BBB;
  min-width: 24px;
  text-align: right;
  padding-top: 4px;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}}

.tag-chip {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 130px;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .03em;
  flex-shrink: 0;
  line-height: 1.4;
}}
.tag-chip.is-primary {{ color: #fff; }}
.tag-chip.is-secondary {{ color: #444; font-weight: 500; }}

.sentence-body {{
  flex: 1;
  min-width: 0;
}}

.sentence-text {{
  font-size: 13.5px;
  line-height: 1.55;
  color: #222;
}}

.sentence-note {{
  font-size: 11px;
  color: #999;
  font-style: italic;
  margin-top: 3px;
  line-height: 1.4;
}}

/* ── Move mode ───────────────────────────────────────────── */
.arc-summary {{
  font-size: 13px;
  line-height: 1.65;
  color: #555;
  border-left: 3px solid #DDD;
  padding: 2px 0 2px 14px;
  margin-bottom: 22px;
}}

.arc-formula {{
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}}

.arc-pill {{
  padding: 5px 16px;
  border-radius: 20px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .05em;
}}

.arc-arrow {{
  color: #BBB;
  font-size: 16px;
  font-weight: 300;
  line-height: 1;
}}

.arc-strips {{
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}}

.move-strip {{
  display: flex;
  height: 48px;
}}

.move-segment {{
  display: flex;
  align-items: center;
  justify-content: center;
  transition: filter .1s;
  cursor: default;
  overflow: hidden;
}}
.move-segment:hover {{ filter: brightness(1.08); }}

.move-segment-label {{
  color: rgba(255,255,255,.92);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .06em;
  pointer-events: none;
  white-space: nowrap;
}}

.step-strip {{
  display: flex;
  height: 14px;
}}

.step-tick {{
  flex-shrink: 0;
  cursor: default;
  transition: filter .1s;
}}
.step-tick:hover {{ filter: brightness(1.15); }}
.step-tick + .step-tick {{
  border-left: 1px solid rgba(255,255,255,.25);
}}

.move-stats {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}}

.move-stat-card {{
  flex: 1;
  min-width: 180px;
  padding: 14px 16px;
  background: #fff;
  border-radius: 8px;
  border-left: 4px solid #CCC;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}}

.stat-move {{
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 3px;
  letter-spacing: .02em;
}}

.stat-count {{
  font-size: 11px;
  color: #999;
  margin-bottom: 10px;
}}

.stat-steps {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}}

.step-chip {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  color: #fff;
  letter-spacing: .02em;
}}

.move-pending {{
  color: #AAA;
  font-size: 14px;
  padding: 40px 0;
  font-style: italic;
}}

/* ── Outline mode ────────────────────────────────────────── */
.outline-blocks {{
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
}}

.outline-block {{
  background: #fff;
  border-radius: 8px;
  padding: 16px 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  border-left: 4px solid #CCC;
}}

.outline-block-header {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}}

.outline-block-move {{
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  letter-spacing: .05em;
  flex-shrink: 0;
}}

.outline-block-id {{
  font-size: 11px;
  font-weight: 700;
  color: #555;
  letter-spacing: .06em;
  text-transform: uppercase;
  flex-shrink: 0;
}}

.outline-block-label {{
  font-size: 13px;
  font-weight: 600;
  color: #222;
  flex: 1;
}}

.outline-block-span {{
  font-size: 10px;
  color: #AAA;
  font-style: italic;
  flex-shrink: 0;
}}

.outline-block-role {{
  font-size: 13px;
  line-height: 1.65;
  color: #444;
  margin-bottom: 4px;
}}

.outline-block-sources {{
  font-size: 11px;
  color: #AAA;
  font-style: italic;
  border-top: 1px solid #F0EDE8;
  padding-top: 6px;
  margin-top: 6px;
}}

/* ── Empty state ─────────────────────────────────────────── */
.empty {{
  color: #AAA;
  font-size: 14px;
  padding: 40px 0;
}}

/* ── Custom tooltip ──────────────────────────────────────── */
#tip {{
  position: fixed;
  z-index: 9999;
  background: rgba(24,24,24,.93);
  color: #F0EDE8;
  padding: 8px 12px;
  border-radius: 7px;
  font-size: 11.5px;
  line-height: 1.55;
  max-width: 400px;
  pointer-events: none;
  display: none;
  white-space: pre-wrap;
  box-shadow: 0 2px 10px rgba(0,0,0,.25);
}}

.arc-pill[data-tip] {{ cursor: help; }}
</style>
</head>
<body>

<header class="app-header">
  <div class="app-title">StructuralView</div>
  <div class="paper-selectors">
    <div class="select-group">
      <span class="select-label">Drafts</span>
      <select class="paper-select" id="draftSelect" onchange="selectFromDraft(this.value)">
        <option value="">— select —</option>
      </select>
    </div>
    <div class="select-group">
      <span class="select-label">Corpus</span>
      <select class="paper-select" id="corpusSelect" onchange="selectFromCorpus(this.value)">
        <option value="">— select —</option>
      </select>
    </div>
  </div>
  <div class="mode-toggle">
    <button class="mode-btn active" id="modeTag"  onclick="setMode('tag')">Tag</button>
    <button class="mode-btn"        id="modeMove" onclick="setMode('move')">Move</button>
  </div>
  <button class="legend-toggle" id="legendToggle">Legend</button>
</header>

<div id="tip"></div>
<div class="app-body">
  <aside class="legend" id="legend"></aside>
  <main class="ribbon" id="ribbon">
    <p class="empty">Select a paper above.</p>
  </main>
</div>

<script>
const PAPERS      = {papers_js};
const DRAFT_IDS   = new Set({draft_ids_js});
const COLORS      = {colors_js};
const LABELS      = {labels_js};
const PRIMARY     = {primary_js};
const SECONDARY   = {secondary_js};
const MOVE_COLORS = {move_colors_js};
const MOVE_LABELS = {move_labels_js};
const STEP_COLORS = {step_colors_js};

// ── State ──────────────────────────────────────────────────
let activePaper = null;
let legendOpen  = false;
let activeMode  = 'tag';

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {{
  buildLegend();
  buildSelectors();

  document.getElementById('legendToggle').addEventListener('click', () => {{
    legendOpen = !legendOpen;
    document.getElementById('legend').classList.toggle('visible', legendOpen);
  }});

  // Deep link: ?paper=<id>[&mode=move]
  const params    = new URLSearchParams(location.search);
  const wantId    = params.get('paper');
  const wantMode  = params.get('mode');
  const wantIndex = wantId ? PAPERS.findIndex(p => p.paper.id === wantId) : -1;

  if (wantMode === 'move' || wantMode === 'tag') setMode(wantMode);

  if (wantIndex !== -1) {{
    const sel = DRAFT_IDS.has(PAPERS[wantIndex].paper.id) ? 'draftSelect' : 'corpusSelect';
    document.getElementById(sel).value = wantIndex;
    document.getElementById(sel).classList.add('has-selection');
    selectPaper(wantIndex);
    return;
  }}

  // Default: first draft if any, else first corpus paper
  const firstDraft = PAPERS.findIndex(p => DRAFT_IDS.has(p.paper.id));
  if (firstDraft !== -1) {{
    document.getElementById('draftSelect').value = firstDraft;
    document.getElementById('draftSelect').classList.add('has-selection');
    selectPaper(firstDraft);
  }} else if (PAPERS.length > 0) {{
    document.getElementById('corpusSelect').value = 0;
    document.getElementById('corpusSelect').classList.add('has-selection');
    selectPaper(0);
  }}
}});

// ── Mode ───────────────────────────────────────────────────
function setMode(mode) {{
  activeMode = mode;
  document.getElementById('modeTag').classList.toggle('active',  mode === 'tag');
  document.getElementById('modeMove').classList.toggle('active', mode === 'move');
  if (mode === 'move') {{
    legendOpen = false;
    document.getElementById('legend').classList.remove('visible');
  }}
  renderPaper(activePaper);
}}

// ── Legend ─────────────────────────────────────────────────
function buildLegend() {{
  const el = document.getElementById('legend');
  let html = '<div class="legend-section-label">Primary</div>';
  for (const tag of PRIMARY)   html += legendItem(tag);
  html += '<div class="legend-section-label">Secondary</div>';
  for (const tag of SECONDARY) html += legendItem(tag);
  el.innerHTML = html;
}}

function legendItem(tag) {{
  return `<div class="legend-item">
    <span class="legend-chip" style="background:${{COLORS[tag] || '#CCC'}}"></span>
    <span class="legend-label">${{LABELS[tag] || tag}}</span>
  </div>`;
}}

// ── Selectors ──────────────────────────────────────────────
function buildSelectors() {{
  const draftSel  = document.getElementById('draftSelect');
  const corpusSel = document.getElementById('corpusSelect');
  PAPERS.forEach((p, i) => {{
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = shortTitle(p.paper);
    if (DRAFT_IDS.has(p.paper.id)) draftSel.appendChild(opt);
    else                            corpusSel.appendChild(opt);
  }});
}}

function shortTitle(meta) {{
  const author = meta.authors ? meta.authors[0].split(',')[0] : meta.id;
  const year   = meta.year   ? ` (${{meta.year}})` : '';
  const tag    = meta.version ? ' · ideal' : '';
  return `${{author}}${{year}}${{tag}}`;
}}

function selectFromDraft(val) {{
  if (val === '') return;
  const corpusSel = document.getElementById('corpusSelect');
  corpusSel.value = '';
  corpusSel.classList.remove('has-selection');
  document.getElementById('draftSelect').classList.add('has-selection');
  selectPaper(parseInt(val, 10));
}}

function selectFromCorpus(val) {{
  if (val === '') return;
  const draftSel = document.getElementById('draftSelect');
  draftSel.value = '';
  draftSel.classList.remove('has-selection');
  document.getElementById('corpusSelect').classList.add('has-selection');
  selectPaper(parseInt(val, 10));
}}

function selectPaper(i) {{
  activePaper = i;
  renderPaper(i);
}}

// ── Paper render ───────────────────────────────────────────
function renderPaper(i) {{
  const paper = PAPERS[i];
  if (!paper) return;
  const el = document.getElementById('ribbon');

  const meta    = paper.paper;
  const authStr = meta.authors ? meta.authors.join(', ') : '';

  let html = `<div class="paper-meta">
    <h2>${{esc(meta.title)}}</h2>
    <div class="authors">${{esc(authStr)}} &middot; ${{meta.year}}</div>
  </div>`;

  if (activeMode === 'move' || isOutlineData(paper)) {{
    html += renderMoveMode(paper);
  }} else {{
    for (const s of paper.sentences) html += renderRow(s);
  }}

  el.innerHTML = html;
}}

// ── Tag mode ───────────────────────────────────────────────
function renderRow(s) {{
  const tag     = s.tag || 'unknown';
  const tier    = s.tier || (PRIMARY.includes(tag) ? 'primary' : 'secondary');
  const color   = COLORS[tag] || '#CCC';
  const label   = LABELS[tag] || tag;
  const isSec   = tier === 'secondary';

  const noteHtml = s.note
    ? `<div class="sentence-note">${{esc(s.note)}}</div>` : '';

  return `<div class="${{isSec ? 'sentence-row is-secondary' : 'sentence-row'}}">
    <span class="sentence-num">${{s.id}}</span>
    <span class="${{isSec ? 'tag-chip is-secondary' : 'tag-chip is-primary'}}"
          style="background:${{color}}">${{esc(label)}}</span>
    <div class="sentence-body">
      <div class="sentence-text">${{esc(s.text)}}</div>
      ${{noteHtml}}
    </div>
  </div>`;
}}

// ── Move / Outline mode ────────────────────────────────────
function isOutlineData(paper) {{
  return !paper.sentences || paper.sentences.length === 0;
}}

function hasCarsData(paper) {{
  return paper.sentences && paper.sentences.some(s => s.cars_move);
}}

function computeArcSegments(sentences) {{
  const segs = [];
  let cur = null;
  for (const s of sentences) {{
    if (!s.cars_move) continue;
    if (!cur || s.cars_move !== cur.move) {{
      cur = {{ move: s.cars_move, sentences: [s] }};
      segs.push(cur);
    }} else {{
      cur.sentences.push(s);
    }}
  }}
  return segs;
}}

function renderMoveMode(paper) {{
  if (isOutlineData(paper)) {{
    return renderOutlineMode(paper);
  }}
  if (!hasCarsData(paper)) {{
    return `<div class="move-pending">CARS annotation not yet available for this paper.</div>`;
  }}
  const segs  = computeArcSegments(paper.sentences);
  const total = paper.sentences.filter(s => s.cars_move).length;
  return [
    renderArcSummary(paper.arc_summary),
    renderArcFormula(paper),
    renderArcStrips(segs, total, paper.move_roles || null),
    renderMoveStats(segs, total),
  ].join('');
}}

function renderMd(text) {{
  if (!text) return '';
  let s = esc(text);
  s = s.replace(/[*][*]([^*]+)[*][*]/g, '<strong>$1</strong>');
  return s;
}}

function renderArcSummary(text) {{
  if (!text) return '';
  return `<div class="arc-summary">${{renderMd(text)}}</div>`;
}}

function renderArcFormula(paper) {{
  const roles = paper.move_roles;
  if (roles && roles.length) {{
    const html = roles.map((r, i) => {{
      const color = MOVE_COLORS[r.move] || '#CCC';
      const tip   = r.span
        ? `${{r.move}} · S${{r.span[0]}}–${{r.span[1]}}\n${{r.role || ''}}`
        : `${{r.move}} · ${{r.id || ''}} · ${{r.label || ''}}\n${{r.span_note || ''}}\n${{r.role || ''}}`;
      const label = r.id || r.move;
      const arrow = i < roles.length - 1 ? `<span class="arc-arrow">&#8594;</span>` : '';
      return `<span class="arc-pill" style="background:${{color}}" data-tip="${{esc(tip)}}">${{esc(label)}}</span>${{arrow}}`;
    }}).join('');
    return `<div class="arc-formula">${{html}}</div>`;
  }}
  const formula = paper.structured_arc;
  if (!formula) return '';
  const parts = formula.split(' -> ');
  const html = parts.map((m, i) => {{
    const color = MOVE_COLORS[m] || '#CCC';
    const arrow = i < parts.length - 1 ? `<span class="arc-arrow">&#8594;</span>` : '';
    return `<span class="arc-pill" style="background:${{color}}">${{esc(m)}}</span>${{arrow}}`;
  }}).join('');
  return `<div class="arc-formula">${{html}}</div>`;
}}

function renderArcStrips(segs, total, roles) {{
  const moveStrip = segs.map((seg, i) => {{
    const w     = (seg.sentences.length / total * 100).toFixed(2);
    const color = MOVE_COLORS[seg.move] || '#CCC';
    const label = seg.sentences.length / total > 0.08 ? seg.move : '';
    const role  = roles && roles[i];
    const tip   = role
      ? `${{seg.move}} · S${{role.span[0]}}–${{role.span[1]}}\n${{role.role}}`
      : `${{seg.move}}: ${{seg.sentences.length}} sentence${{seg.sentences.length > 1 ? 's' : ''}}`;
    return `<div class="move-segment" style="width:${{w}}%;background:${{color}}" data-tip="${{esc(tip)}}">
              <span class="move-segment-label">${{esc(label)}}</span>
            </div>`;
  }}).join('');

  const stepTicks = segs.flatMap(seg =>
    seg.sentences.map(s => {{
      const w    = (1 / total * 100).toFixed(3);
      const color = STEP_COLORS[s.cars_step] || MOVE_COLORS[s.cars_move] || '#CCC';
      const tip  = `#${{s.id}} · ${{s.tag || ''}} · ${{s.cars_move}}/${{s.cars_step || '?'}}\n${{s.text || ''}}`;
      return `<div class="step-tick" style="width:${{w}}%;background:${{color}}" data-tip="${{esc(tip)}}"></div>`;
    }})
  ).join('');

  return `<div class="arc-strips">
    <div class="move-strip">${{moveStrip}}</div>
    <div class="step-strip">${{stepTicks}}</div>
  </div>`;
}}

function renderMoveStats(segs, total) {{
  const order  = ['M1', 'M2', 'M3'];
  const byMove = {{}};
  for (const seg of segs) {{
    if (!byMove[seg.move]) byMove[seg.move] = {{ sentences: [], steps: {{}} }};
    byMove[seg.move].sentences.push(...seg.sentences);
    for (const s of seg.sentences) {{
      if (s.cars_step) {{
        byMove[seg.move].steps[s.cars_step] =
          (byMove[seg.move].steps[s.cars_step] || 0) + 1;
      }}
    }}
  }}

  const cards = order.filter(m => byMove[m]).map(m => {{
    const data  = byMove[m];
    const color = MOVE_COLORS[m] || '#CCC';
    const pct   = Math.round(data.sentences.length / total * 100);
    const chips = Object.entries(data.steps)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([step, count]) => {{
        const sc = STEP_COLORS[step] || color;
        return `<span class="step-chip" style="background:${{sc}}">${{esc(step)}} &times;${{count}}</span>`;
      }}).join('');
    return `<div class="move-stat-card" style="border-left-color:${{color}}">
      <div class="stat-move" style="color:${{color}}">${{esc(m)}} &mdash; ${{esc(MOVE_LABELS[m] || '')}}</div>
      <div class="stat-count">${{data.sentences.length}} sentences &middot; ${{pct}}%</div>
      <div class="stat-steps">${{chips}}</div>
    </div>`;
  }}).join('');

  return `<div class="move-stats">${{cards}}</div>`;
}}

// ── Outline mode ───────────────────────────────────────────
function renderOutlineMode(paper) {{
  const roles = paper.move_roles || [];
  return [
    renderArcSummary(paper.arc_summary),
    renderArcFormula(paper),
    renderOutlineStrip(roles),
    renderOutlineBlocks(roles),
  ].join('');
}}

function renderOutlineStrip(roles) {{
  if (!roles.length) return '';
  const n = roles.length;
  const segments = roles.map(r => {{
    const w     = (100 / n).toFixed(2);
    const color = MOVE_COLORS[r.move] || '#CCC';
    const tip   = `${{r.move}} · ${{r.id || ''}}\n${{r.label || ''}} · ${{r.span_note || ''}}`;
    return `<div class="move-segment" style="width:${{w}}%;background:${{color}}" data-tip="${{esc(tip)}}">
              <span class="move-segment-label">${{esc(r.id || r.move)}}</span>
            </div>`;
  }}).join('');
  return `<div class="arc-strips"><div class="move-strip">${{segments}}</div></div>`;
}}

function renderOutlineBlocks(roles) {{
  const blocks = roles.map(r => {{
    const color  = MOVE_COLORS[r.move] || '#CCC';
    const srcHtml = r.sources_from_draft && r.sources_from_draft.length
      ? `<div class="outline-block-sources">Sources from draft: ${{esc(r.sources_from_draft.join(' · '))}}</div>`
      : '';
    return `<div class="outline-block" style="border-left-color:${{color}}">
      <div class="outline-block-header">
        <span class="outline-block-move" style="background:${{color}}">${{esc(r.move)}}</span>
        <span class="outline-block-id">${{esc(r.id || '')}}</span>
        <span class="outline-block-label">${{esc(r.label || '')}}</span>
        <span class="outline-block-span">${{esc(r.span_note || '')}}</span>
      </div>
      <div class="outline-block-role">${{esc(r.role || '')}}</div>
      ${{srcHtml}}
    </div>`;
  }}).join('');
  return `<div class="outline-blocks">${{blocks}}</div>`;
}}

function esc(str) {{
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}}

// ── Floating tooltip ───────────────────────────────────────
const tipEl = document.getElementById('tip');

document.addEventListener('mouseover', e => {{
  const t = e.target.closest('[data-tip]');
  if (!t) {{ tipEl.style.display = 'none'; return; }}
  tipEl.textContent = t.dataset.tip;
  tipEl.style.display = 'block';
}});

document.addEventListener('mousemove', e => {{
  if (tipEl.style.display === 'none') return;
  const x = e.clientX + 14;
  const y = e.clientY + 14;
  const r = tipEl.getBoundingClientRect();
  tipEl.style.left = (x + r.width  > window.innerWidth  ? e.clientX - r.width  - 8 : x) + 'px';
  tipEl.style.top  = (y + r.height > window.innerHeight ? e.clientY - r.height - 8 : y) + 'px';
}});

document.addEventListener('mouseout', e => {{
  if (!e.relatedTarget || !e.relatedTarget.closest('[data-tip]')) {{
    tipEl.style.display = 'none';
  }}
}});
</script>
</body>
</html>"""


if __name__ == '__main__':
    build()
