# Porting the APRI Streamlit site to a static site (shared brief)

Goal: the APRI Streamlit app (UNEP Haiti, landscape resilience observatory) is being rebuilt as a
static site hosted on GitHub Pages (plain HTML/CSS/ES modules, no build step, no server). Every
section must keep the SAME content, texts, logic and interactivity as the Streamlit version, but run
entirely in the browser from precomputed JSON.

## Where things are
- Site root (you write here): /tmp/claude-0/-home-claude/aea70417-b83e-57e4-9500-5a23c16c150b/scratchpad/site
- Streamlit source, full repo (READ ONLY, never modify): /tmp/work  (identical copy in /tmp/chk, also read only)
  Entry: /tmp/work/app.py, function _rendre_section (around line 2651) dispatches each section.
- A running copy of the Streamlit app for visual/behaviour reference: http://localhost:8613/?lang=fr
  (single scrolling page; sections are containers .st-key-sec_<mode>; many widgets live in iframes).
  Use Playwright (python, chromium preinstalled) to look at it. Add launch args
  ["--use-gl=swiftshader","--enable-unsafe-swiftshader"] or screenshots may hang.
- Static site shell (do not edit, owned by the coordinator): index.html, css/commun.css, js/apri.js,
  js/<section>.js dispatchers. Read them first: they define the contract below and the CSS classes.

## Contract
- A tabbed section `S` with tab `T` is drawn by `js/S/T.js`:
  `export default async function render(el, apri) { ... }` draws everything into `el` from scratch.
  It is called again on language change, so it must be idempotent.
- `apri` helpers: apri.lang ('fr'|'en'), apri.t(fr,en), apri.tt({fr,en}), apri.donnees('data/...json')
  (cached fetch, path relative to site root), apri.esc, apri.h(html), apri.nombre(n,dec), apri.pct(x,dec),
  apri.plier(s) (accent-free lowercase), apri.aller(section, tab) (navigate), apri.barreOnglets(...).
- Non-tabbed sections (ressources, apropos, contact) are js/<section>.js themselves with
  `export const onglets = []` and the same default render signature. You own those files if assigned.
- Data: write JSON to data/<section>/... and the Python script that produces it to
  outils/export_<section>[_<tab>].py. The script must run as `python3 outils/export_x.py` with cwd = site root,
  reading from /tmp/work (sys.path.insert(0,'/tmp/work'); os.chdir('/tmp/work') inside, write with absolute
  paths back to the site). Streamlit modules can be imported in "bare mode"; set language with
  `import streamlit as st; st.session_state['lang']='fr'` (then 'en') before calling translation helpers.
  Prefer extracting texts in both languages (fr, en) rather than copying them by hand.
- CSS: use the classes in css/commun.css (carte-page context, h2/h3, .lead, .note, .etiquette, .onglets,
  .grille/.grille.deux, .tuile, .colonnes, .bouton(.primaire), .pastilles, .champ, label.libelle,
  table.tableau, .barres, details.pli, .vide, .chargement). Extra styles go in css/<section>.css, every rule
  prefixed by `#<section>` (e.g. `#resultats .x{}`); load it from your module once
  (`if(!document.querySelector('link[href="css/x.css"]')) document.head.append(Object.assign(document.createElement('link'),{rel:'stylesheet',href:'css/x.css'}))`).
- Libraries: only if really needed, loaded as ES modules from https://cdn.jsdelivr.net/npm/... or unpkg.
  Prefer plain SVG/HTML for charts. The look must match the Streamlit version (same palette: blues
  #397fa3, greens #2f7a5b, text #1f3a4a; Inter font).
- Languages: French and English only. Every visible string in both. Keep the Streamlit wording.
- Wheel: the page scrolls with the mouse wheel; never let a chart/map/graph capture the wheel for zoom
  (zoom only by buttons), as in the Streamlit version.

## Privacy (mandatory)
Never write household-level (row-level) survey data, names, phone numbers, enumerators, exact GPS points
or household localities into data/. Only aggregates (counts, shares, means, scores by section, landscape,
sex, age group, etc.). Suppress any cell computed on fewer than 5 households (show "n < 5").
Where Streamlit computes on microdata for an arbitrary filter combination, precompute the aggregates for
every combination the UI offers (if the set is finite and reasonable) and look them up in JS. If a feature
truly needs microdata, implement the closest aggregate version and say so in your final report.

## Testing
- Serve the site yourself on your own port (given in your task), e.g.
  `cd <site root> && nohup python3 -m http.server <port> >/dev/null 2>&1 &`, open
  http://localhost:<port>/index.html#<section>/<tab> with Playwright, check: no console errors, both
  languages, desktop 1440x900 and phone 390x844, behaviour matches Streamlit. Look at your screenshots.
- Keep each JSON reasonably small (aim < 1.5 MB per file; split per theme/question if needed, load lazily).

## Report back (final message)
Files created, what is ported, what differs from Streamlit and why, data sizes, any privacy decision.
Do not touch files owned by others. Do not publish anything (no git, no GitHub): the coordinator publishes.
