// Compare the JavaScript engine (js/boucles/moteur.js) with the Python reference
// written by outils/verif_boucles.py.   node outils/verif_boucles.mjs <ref.json>
import fs from 'fs';
import * as E from '../js/boucles/moteur.js';
const ref = JSON.parse(fs.readFileSync(process.argv[2] || 'verif_boucles_ref.json', 'utf8'));
const donnees = JSON.parse(fs.readFileSync(new URL('../data/boucles/modele.json', import.meta.url), 'utf8'));
let n = 0, ko = 0, maxErr = 0; const fails = [];
const TOL = 1e-9;
function egal(a, b, ou) {
  n++;
  const rec = (x, y, p) => {
    if (typeof x === 'number' && typeof y === 'number') {
      const e = Math.abs(x - y) / Math.max(1, Math.abs(y)); maxErr = Math.max(maxErr, e);
      if (e > TOL) throw p + ': ' + x + ' != ' + y; return;
    }
    if (x === null || y === null || typeof x !== 'object' || typeof y !== 'object') {
      if (x !== y && !(x == null && y == null)) throw p + ': ' + JSON.stringify(x) + ' != ' + JSON.stringify(y); return;
    }
    if (Array.isArray(y) || ArrayBuffer.isView(y)) {
      x = Array.from(x); y = Array.from(y);
      if (x.length !== y.length) throw p + ': length ' + x.length + ' != ' + y.length;
      y.forEach((v, i) => rec(x[i], v, p + '[' + i + ']')); return;
    }
    const kx = Object.keys(x), ky = Object.keys(y);
    if (kx.join() !== ky.join()) throw p + ': keys ' + kx + ' != ' + ky;
    for (const k of ky) rec(x[k], y[k], p + '.' + k);
  };
  try { rec(a, b, ou); } catch (e) { ko++; if (fails.length < 15) fails.push(String(e).slice(0, 300)); }
}
const obj = map => Object.fromEntries(map);
for (const lang of ['fr', 'en']) {
  const R = ref[lang];
  const m = E.creerModele(donnees, lang);
  egal(m.ids, R.ids, lang + ' ids');
  egal(m.diag.rayon, R.diag.rayon, lang + ' rayon spectral');
  egal(m.diag.facteur, R.diag.facteur, lang + ' facteur');
  egal(m.A.map(r => Array.from(r)), R.A, lang + ' matrice A');
  egal(m.boucles.map(b => [b.noeuds, b.type, b.force]), R.boucles, lang + ' boucles');
  egal(m.leviers, R.leviers, lang + ' leviers');
  // dominant arcs: Python's set order makes ties unstable, compare the counts
  const dom = E.bouclesDominantes(m.boucles, 8);
  egal(dom.map(d => [d.n, d.renf + d.equi]), R.dominantes.map(d => [d.n, d.renf + d.equi]), lang + ' dominantes (comptes)');
  const tousArcs = E.bouclesDominantes(m.boucles, 1000);
  for (const d of R.dominantes) { const j = tousArcs.find(x => x.de === d.de && x.vers === d.vers); egal(j && [j.n, j.renf, j.equi], [d.n, d.renf, d.equi], lang + ' arc ' + d.de + '>' + d.vers); }
  for (const S of R.systemes) {
    const t = lang + ' ' + S.c + '/' + S.n;
    const { rang, aretes } = E.voisinage(m, S.c, S.n);
    egal([...rang.entries()], S.rang, t + ' voisinage');
    egal(aretes.map(a => [a.de, a.vers]), S.aretes, t + ' aretes');
    const { pos } = E.positions(rang, S.c);
    egal(obj(pos), S.pos, t + ' positions');
    const lay = E.causalLayout([...pos.keys()], aretes, S.c);
    egal(obj(lay.pos), S.lay, t + ' schema');
    egal(lay.groups, S.groups, t + ' groupes');
    egal(E.bouclesDe(m, S.c, new Set(rang.keys())).map(b => b.noeuds), S.bcls, t + ' boucles du centre');
    const lev = [];
    for (const lv of m.leviers) {
      if (!rang.has(lv.id)) continue;
      const eff = E.propager(m, { [lv.id]: 1.0 });
      lev.push([lv.id, Object.entries(eff).reduce((s, [k, v]) => s + (k !== lv.id ? Math.abs(v) : 0), 0)]);
    }
    egal(E.trier(lev, x => [-x[1]]).slice(0, 14), S.lev, t + ' leviers (portee)');
  }
  let i = 0;
  for (const c of ['eau', 'foret', 'revenu', 'prod_agri', 'sante', 'cuisson']) for (const k of [5, 10, 20, 30]) {
    egal(E.donneesDirect(m, c, k), R.direct[i++], lang + ' direct ' + c + '/' + k);
  }
  egal(E.donneesRegler(m), R.regler, lang + ' regler');
  for (const [cle, v] of Object.entries(R.correl)) {
    const [a, b] = cle.split('|');
    egal(E.correlation(m, a, b), v, lang + ' correlation ' + cle);
  }
}
const m = E.creerModele(donnees, 'fr');
for (const S of ref.scen) {
  const t = 'scenario ' + JSON.stringify(S.v);
  const eff = E.propager(m, S.v);
  egal(eff, S.eff, t + ' propager');
  egal(E.effetIndice(m, eff, S.v), S.ind, t + ' indice');
  for (const [p, e] of Object.entries(S.etat)) egal(E.etatCourant(m, p), e, t + ' etat ' + p);
  for (const [p, e] of Object.entries(S.apres)) egal(E.apres(E.etatCourant(m, p), eff, S.v), e, t + ' apres ' + p);
  const vg = E.vagues(m, S.v);
  egal(vg.vagues.map(x => Array.from(x)), S.vagues, t + ' vagues');
  egal([vg.converge, vg.k], [S.conv, S.k], t + ' arret');
  for (const [id, s] of Object.entries(S.parqui)) egal(E.parQui(m, id, S.v, eff).map(d => m.noms[d] ?? d).join(', '), s, t + ' par_qui ' + id);
}

// ---------------------------------------------------------------- Monte Carlo
{
  const m = E.creerModele(donnees, 'fr');
  // 1. the nominal draw (stored strengths, stability 0.6) IS the current engine, bit for bit
  const nom = E.tirerModele(m, E.aleatoire(1), { forces: 'nominales', cible: 0.6 });
  let diff = 0; m.A.forEach((r, i) => r.forEach((x, j) => { diff = Math.max(diff, Math.abs(x - nom.A[i][j])); }));
  egal(diff, 0, 'MC tirage nominal = matrice du moteur (écart max)');
  for (const S of ref.scen) egal(E.propager(nom, S.v), S.eff, 'MC tirage nominal propager ' + JSON.stringify(S.v));
  // 2. the exact inverse used by the draws gives the same effects as propager
  const inv = E.inverseIA(m.A), mc1 = { n: 1, N: m.ids.length, ids: m.ids, idx: m.idx, inv };
  for (const S of ref.scen) egal(E.propagerTirage(mc1, 0, S.v), S.eff, 'MC inverse (I-A)^-1 ' + JSON.stringify(S.v));
  // 3. class-centre strengths, stability 0.6: same matrix as numpy (exact eigenvalues)
  const cen = E.tirerModele(m, E.aleatoire(1), { forces: 'centrales', cible: 0.6 });
  egal(cen.rayon, ref.centrales.rayon, 'MC centres de classe rayon (rapide vs numpy)');
  egal(cen.A.map(r => Array.from(r)), ref.centrales.A, 'MC centres de classe matrice');
  // 4. classes and wording
  egal(donnees.graphe.aretes.map(e => E.classeDe(e.force).c === e.force || (e.force === 0.6 && E.classeDe(e.force).k === 4)), donnees.graphe.aretes.map(() => true), 'classes des forces');
  egal([0, 0.049, 0.05, 0.19, 0.2, 0.49, 0.5, 3, -0.3].map(x => E.qualifier(x, 'fr').texte),
    ['effet négligeable', 'effet négligeable', 'effet faible, positif', 'effet faible, positif', 'effet modéré, positif', 'effet modéré, positif', 'effet fort, positif', 'effet fort, positif', 'effet modéré, négatif'], 'qualifier');
  // 5. reproducible, and statistically consistent with the numpy Monte Carlo
  const t0 = Date.now();
  const mc = E.monteCarlo(m, { n: 1000, graine: 2026 });
  const ms = Date.now() - t0;
  const mcb = E.monteCarlo(m, { n: 50, graine: 2026 });
  egal(Array.from(mcb.portee), Array.from(mc.portee.slice(0, 50 * m.ids.length)), 'MC reproductible (même graine)');
  const tous = E.rangsLeviers(mc, ref.mc.ids);
  let ecartMax = 0;
  tous.forEach((u, i) => { ecartMax = Math.max(ecartMax, Math.abs(u.pTop3 - ref.mc.p_top3[i])); });
  n++; if (ecartMax > 0.05) { ko++; fails.push('MC vs numpy: P(top 3) differs by ' + ecartMax.toFixed(3)); }
  // 6. robustness of the ranking, for the coordinator
  const robust = (ids, titre) => {
    const cent = E.trier(ids.map(id => { const e = E.propager(m, { [id]: 1 }); let p = 0; for (const [k, v] of Object.entries(e)) if (k !== id) p += Math.abs(v); return [id, p]; }), x => [-x[1]]).map(x => x[0]);
    const st = E.rangsLeviers(mc, cent), top = cent.slice(0, 3);
    let ordre = 0, ensemble = 0, chacun = 0;
    for (let d = 0; d < mc.n; d++) {
      const r = st.slice(0, 3).map(u => u.rangs[d]);
      if (r[0] === 1 && r[1] === 2 && r[2] === 3) ordre++;
      if (r.every(x => x <= 3)) ensemble++;
    }
    console.log(`\n${titre} (${ids.length} variables), top 3 at central values: ${top.map(i => m.noms[i]).join(', ')}`);
    console.log(`  same three in the same order: ${(100 * ordre / mc.n).toFixed(1)} % of draws; same three, any order: ${(100 * ensemble / mc.n).toFixed(1)} %`);
    st.slice(0, 6).forEach((u, i) => console.log(`  ${i + 1}. ${m.noms[u.id]}: P(top 3) ${(100 * u.pTop3).toFixed(1)} %, median rank ${u.rangMed}, 90 % interval ${u.rangLo}-${u.rangHi}`));
    void chacun;
  };
  console.log(`Monte Carlo: 1000 draws in ${ms} ms (node); max |P(top 3) JS - numpy| = ${ecartMax.toFixed(3)}`);
  robust(m.ids, 'Whole model');
  const centre = E.trier(m.ids, i => [m.noms[i]])[0];
  robust([...E.voisinage(m, centre, 10).rang.keys()], `Default system (${m.noms[centre]}, 10 variables)`);
}
console.log(`${n} comparisons, ${ko} failed, max relative error ${maxErr.toExponential(2)}`);
fails.forEach(f => console.log('  ' + f));
process.exit(ko ? 1 : 0);
