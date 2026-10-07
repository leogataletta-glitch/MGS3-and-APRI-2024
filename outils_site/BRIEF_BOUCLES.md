# Feedback loops: making the model scientifically honest and friendly (shared brief)

Read BRIEF.md first (site structure, apri helpers, CSS classes, testing, privacy). This brief adds
the specific rules for the "Boucles de rétroaction / Feedback Loops" section (js/boucles.js, tabs
js/boucles/<tab>.js, engine js/boucles/moteur.js, data data/boucles/modele.json + textes.json,
Python reference engine /tmp/work/boucles_moteur.py and data /tmp/work/data/graphe_causal.json).

## Why
A scientific review of the section found: link strengths are expert classes (0.2, 0.35, 0.5, 0.65,
0.8) rescaled by one arbitrary factor so the spectral radius equals 0.6; outputs like "+0.012 on the
index" look precise but are not; the lever ranking is not guaranteed to survive another rescaling
(paths of length k scale with factor^k); the model is linear and cannot tip; only 7 of 101 links
are negative; 17 of 48 nodes are unmeasured; validation over 10 sections is weak.

## Shared definitions (use exactly these)
Strength classes (the same in every tab, in the rule, in the workshop and in the Monte Carlo):
| class | FR | EN | central value | draw interval |
| 1 | très faible | very weak | 0.20 | 0.125 to 0.275 |
| 2 | faible | weak | 0.35 | 0.275 to 0.425 |
| 3 | moyenne | moderate | 0.50 | 0.425 to 0.575 |
| 4 | forte | strong | 0.65 | 0.575 to 0.725 |
| 5 | très forte | very strong | 0.80 | 0.725 to 0.875 |
(a stored value of 0.6 belongs to class 4.)
Model stability target (spectral radius after rescaling): central 0.6, Monte Carlo range 0.5 to 0.8.

Qualitative wording of an effect (on the 0 to 10 score scale, absolute value of the change):
| below 0.05 | négligeable / negligible |
| 0.05 to 0.2 | faible / weak |
| 0.2 to 0.5 | modéré / moderate |
| 0.5 and more | fort / strong |
combined with a direction: "positif / positive", "négatif / negative" (e.g. "effet faible, positif").
Use arrows and colour (green up, red down, grey flat) next to the words. No decimals in what the
reader sees by default; exact numbers may stay available in a folded "Détail chiffré / Figures"
panel or in CSV exports, labelled as model values, not measurements.

## Tone and design (the most important requirement from the user)
Simple, friendly, inviting, easy to understand for a non-specialist (ministry staff, donors,
community leaders). Short sentences, plain words, one idea per block, visual first (bars, dots,
icons, colours), explanations folded away for those who want them. No jargon on the main screen
("rayon spectral" goes in folded details as "stabilité du modèle"). Every new screen starts with
one sentence saying what it is for and one saying how to use it. Consistent with the rest of the
site (css/commun.css classes, palette, Inter). Works on phone. French and English.

## Files and ownership
- Agent A (qualitative + Monte Carlo): owns all existing js/boucles/*.js files and may add
  js/boucles/incertitude.js. Exports a reusable API from moteur.js:
  `classeDe(force)`, `CLASSES`, `qualifier(delta, lang)` (wording above), `tirerModele(m, rng)`
  (one Monte Carlo draw), `monteCarlo(m, {n, graine})`. Others may import these read-only.
- Agent B (workshop + method): new js/boucles/atelier.js and js/boucles/methode.js only.
- Agent C (forest stock-and-flow model): new js/boucles/foret.js only.
- css/boucles.css is shared: only APPEND rules, each prefixed `#boucles .<yourprefix>-`
  (A: `.qual-` and `.mc-`, B: `.at-` and `.me-`, C: `.fo-`). Never rewrite others' rules.
- js/boucles.js (tab list) is owned by the coordinator: tabs foret, atelier, methode already exist.
- Agents B and C must not edit moteur.js; if you need something from it that Agent A has not
  written yet, implement a small local helper in your own file.

## Testing
Serve the site root yourself on your port, open http://localhost:<port>/index.html#boucles/<tab>,
check FR and EN, desktop 1440x900 and phone 390x844, no console errors. Stub js/territoire.js in
Playwright if the 3D map freezes headless Chromium (route carte_*.html to an empty page).
Do not publish anything; report back with what you did, what you verified, and what remains.
