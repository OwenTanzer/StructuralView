#!/usr/bin/env python3
"""
StructuralView build script.
Reads JSON files from data/ and generates src/index.html.
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

PRIMARY_TAGS   = ['tempstat','emph','contrast','nostat','novstat','contribution','framedef']
SECONDARY_TAGS = ['extension:speculative','extension:definitional',
                  'extension:illustrative','link:opening','link:closing']


def build(open_browser: bool = True):
    data_dir = Path(__file__).parent / 'data'
    out_path  = Path(__file__).parent / 'src' / 'index.html'
    out_path.parent.mkdir(exist_ok=True)

    papers = []
    for f in sorted(data_dir.glob('*.json')):
        papers.append(json.loads(f.read_text(encoding='utf-8')))

    html = render_html(papers)
    out_path.write_text(html, encoding='utf-8')
    print(f'Built {out_path}  ({len(papers)} papers, '
          f'{sum(len(p["sentences"]) for p in papers)} sentences)')

    if open_browser:
        webbrowser.open(out_path.resolve().as_uri())


def render_html(papers: list) -> str:
    papers_js   = json.dumps(papers,      ensure_ascii=False, separators=(',', ':'))
    colors_js   = json.dumps(TAG_COLORS,  ensure_ascii=False)
    labels_js   = json.dumps(TAG_LABELS,  ensure_ascii=False)
    primary_js  = json.dumps(PRIMARY_TAGS)
    secondary_js = json.dumps(SECONDARY_TAGS)

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
  gap: 24px;
  height: 52px;
}}

.app-title {{
  font-size: 15px;
  font-weight: 700;
  letter-spacing: .04em;
  color: #333;
  white-space: nowrap;
}}

.paper-tabs {{
  display: flex;
  gap: 2px;
  overflow-x: auto;
  flex: 1;
}}

.tab {{
  padding: 6px 14px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
  transition: background .12s, color .12s;
}}
.tab:hover {{ background: #F0EDE8; color: #333; }}
.tab.active {{ background: #222; color: #fff; }}

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

/* ── Empty state ─────────────────────────────────────────── */
.empty {{
  color: #AAA;
  font-size: 14px;
  padding: 40px 0;
}}
</style>
</head>
<body>

<header class="app-header">
  <div class="app-title">StructuralView</div>
  <nav class="paper-tabs" id="tabs"></nav>
  <button class="legend-toggle" id="legendToggle">Legend</button>
</header>

<div class="app-body">
  <aside class="legend" id="legend"></aside>
  <main class="ribbon" id="ribbon">
    <p class="empty">Select a paper above.</p>
  </main>
</div>

<script>
const PAPERS    = {papers_js};
const COLORS    = {colors_js};
const LABELS    = {labels_js};
const PRIMARY   = {primary_js};
const SECONDARY = {secondary_js};

// ── State ──────────────────────────────────────────────────
let activePaper = 0;
let legendOpen  = false;

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {{
  buildLegend();
  buildTabs();
  renderPaper(0);

  document.getElementById('legendToggle').addEventListener('click', () => {{
    legendOpen = !legendOpen;
    document.getElementById('legend').classList.toggle('visible', legendOpen);
  }});
}});

// ── Legend ─────────────────────────────────────────────────
function buildLegend() {{
  const el = document.getElementById('legend');
  let html = '<div class="legend-section-label">Primary</div>';
  for (const tag of PRIMARY) {{
    html += legendItem(tag);
  }}
  html += '<div class="legend-section-label">Secondary</div>';
  for (const tag of SECONDARY) {{
    html += legendItem(tag);
  }}
  el.innerHTML = html;
}}

function legendItem(tag) {{
  return `<div class="legend-item">
    <span class="legend-chip" style="background:${{COLORS[tag] || '#CCC'}}"></span>
    <span class="legend-label">${{LABELS[tag] || tag}}</span>
  </div>`;
}}

// ── Tabs ───────────────────────────────────────────────────
function buildTabs() {{
  const nav = document.getElementById('tabs');
  nav.innerHTML = PAPERS.map((p, i) => {{
    const label = shortTitle(p.paper);
    return `<button class="tab${{i === 0 ? ' active' : ''}}"
              onclick="selectPaper(${{i}})">${{label}}</button>`;
  }}).join('');
}}

function shortTitle(meta) {{
  const author = meta.authors ? meta.authors[0].split(',')[0] : meta.id;
  return `${{author}} (${{meta.year}})`;
}}

function selectPaper(i) {{
  activePaper = i;
  document.querySelectorAll('.tab').forEach((t, j) =>
    t.classList.toggle('active', i === j));
  renderPaper(i);
}}

// ── Ribbon ─────────────────────────────────────────────────
function renderPaper(i) {{
  const paper = PAPERS[i];
  if (!paper) return;
  const el = document.getElementById('ribbon');

  const meta = paper.paper;
  const authStr = meta.authors ? meta.authors.join(', ') : '';

  let html = `<div class="paper-meta">
    <h2>${{esc(meta.title)}}</h2>
    <div class="authors">${{esc(authStr)}} &middot; ${{meta.year}}</div>
  </div>`;

  for (const s of paper.sentences) {{
    html += renderRow(s);
  }}

  el.innerHTML = html;
}}

function renderRow(s) {{
  const tag     = s.tag || 'unknown';
  const tier    = s.tier || (PRIMARY.includes(tag) ? 'primary' : 'secondary');
  const color   = COLORS[tag] || '#CCC';
  const label   = LABELS[tag] || tag;
  const isSecondary = tier === 'secondary';

  const chipClass = isSecondary ? 'tag-chip is-secondary' : 'tag-chip is-primary';
  const rowClass  = isSecondary ? 'sentence-row is-secondary' : 'sentence-row';

  const noteHtml = s.note
    ? `<div class="sentence-note">${{esc(s.note)}}</div>`
    : '';

  return `<div class="${{rowClass}}">
    <span class="sentence-num">${{s.id}}</span>
    <span class="${{chipClass}}" style="background:${{color}}">${{esc(label)}}</span>
    <div class="sentence-body">
      <div class="sentence-text">${{esc(s.text)}}</div>
      ${{noteHtml}}
    </div>
  </div>`;
}}

function esc(str) {{
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}}
</script>
</body>
</html>"""


if __name__ == '__main__':
    build()
