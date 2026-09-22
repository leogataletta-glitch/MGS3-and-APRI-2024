"""Croiser le cas étudié avec UNE variable choisie : un profil ou une autre question.

L'écran des corrélations simples classait automatiquement tous les profils
associés au cas. Léo voulait aussi pouvoir poser lui-même la question
« ceux qui sèment du riz, selon le sexe ? selon le littoral ? » : une seule
variable, choisie, et le tableau croisé qui va avec.
"""
import math
from html import escape
import numpy as np
import pandas as pd
import streamlit as st
import i18n
import liens_profils as LP
import liens_inference as I
import themes_enquete as T
import libelles_enquete as L
from traductions import text as tr

PROFILS = ['sexe', 'paysage', 'age', 'richesse', 'section']
SEUIL = 30


# ---------------------------------------------------------------- statistique
def _gammainc_upper(a, x):
    """Q(a, x) : fonction gamma incomplète régularisée supérieure (sans scipy)."""
    if x <= 0:
        return 1.0
    if x < a + 1:
        # série
        term = 1.0 / a; total = term; n = 1
        while n < 500:
            term *= x / (a + n); total += term
            if abs(term) < abs(total) * 1e-14:
                break
            n += 1
        return 1.0 - total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # fraction continue (Lentz)
    tiny = 1e-300
    b = x + 1 - a; c = 1 / tiny; d = 1 / b; h = d
    for i in range(1, 500):
        an = -i * (i - a); b += 2
        d = an * d + b; d = tiny if abs(d) < tiny else d
        c = b + an / c; c = tiny if abs(c) < tiny else c
        d = 1 / d; delta = d * c; h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x, df):
    return _gammainc_upper(df / 2.0, x / 2.0) if df > 0 and x > 0 else 1.0


def tableau(y, common, groups):
    """Une ligne par modalité : effectif, cas, pourcentage."""
    rows = []
    for name, mask in groups.items():
        v = common & mask; n = int(v.sum()); k = int((v & y).sum())
        if n:
            rows.append(dict(groupe=name, n=n, cas=k, pct=100 * k / n))
    return rows


def khi2(rows):
    """Khi² d'indépendance sur le tableau (modalités × cas oui/non)."""
    obs = np.array([[r['cas'], r['n'] - r['cas']] for r in rows], float)
    if obs.shape[0] < 2 or obs.sum() == 0:
        return None
    exp = obs.sum(1, keepdims=True) * obs.sum(0, keepdims=True) / obs.sum()
    if (exp == 0).any():
        return None
    stat = float(((obs - exp) ** 2 / exp).sum()); df = obs.shape[0] - 1
    n = obs.sum(); v = math.sqrt(stat / (n * min(obs.shape[0] - 1, 1))) if n else float('nan')
    return dict(stat=stat, df=df, p=chi2_sf(stat, df), v=v, faible=bool((exp < 5).any()))


# --------------------------------------------------------------------- rendu
def _barres(rows, t):
    """Barres horizontales : une par modalité, le pourcentage écrit au bout."""
    import map_render as MR
    BAR_H, GAP, LAB_W, TOP, W = 20, 10, 300, 6, 860
    plot_w = W - LAB_W - 150
    vmax = max(max(r['pct'] for r in rows), 1e-9)
    h = TOP * 2 + len(rows) * (BAR_H + GAP) - GAP
    parts = [f'<svg viewBox="0 0 {W} {h}" width="100%" style="max-width:{W}px;display:block" role="img">',
             '<style>.xl{font:13px system-ui,sans-serif;fill:#3c4761}.xv{font:600 13px system-ui,sans-serif;fill:#25384b}</style>']
    for i, r in enumerate(rows):
        yy = TOP + i * (BAR_H + GAP)
        w = plot_w * r['pct'] / vmax
        lab = r['label'] if len(r['label']) <= 40 else r['label'][:39] + '…'
        parts.append(f'<text class="xl" x="{LAB_W - 10}" y="{yy + 14}" text-anchor="end">{escape(lab)}</text>')
        parts.append(f'<rect x="{LAB_W}" y="{yy}" width="{w:.1f}" height="{BAR_H}" rx="3" fill="{MR.BAR_COLOR}"/>')
        parts.append(f'<text class="xv" x="{LAB_W + w + 8:.1f}" y="{yy + 14}">{r["pct"]:.1f} % · {r["cas"]}/{r["n"]}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def render(cat, y, base, conditions, t):
    """Le bloc « comparer avec une variable choisie ». `y` et `base` viennent du
    cas défini au-dessus ; `conditions` sert à exclure les questions déjà
    utilisées."""
    fr = i18n.get_lang() == 'fr'
    noms = {'sexe': t('Sexe', 'Sex'), 'paysage': t('Paysage (littoral / montagne)', 'Landscape (coastal / mountain)'),
            'age': t('Âge', 'Age'), 'richesse': t('Niveau économique', 'Economic level'),
            'section': t('Section communale', 'Communal section'), '__question__': t('Une autre question de l’enquête', 'Another survey question')}
    choix = st.selectbox(t('Comparer le cas avec', 'Compare the outcome with'), PROFILS + ['__question__'],
                         format_func=lambda v: noms[v], key='xt_variable')
    groups = None; gbase = None; titre = noms[choix]
    if choix == '__question__':
        qs = {q['i']: q for q in cat['questions'] if len(LP.answers(cat, q)[0]) > 1}
        used = {qid for qid, _ in conditions}
        codes = [c for c in [c for c, _, _ in T.THEMES] + [T.CALCULE, T.AUTRES]
                 if any(T.theme_de(q.get('category')) == c for q in qs.values())]
        cols = st.columns([1, 2])
        with cols[0]:
            theme = st.selectbox(t('Thème', 'Theme'), ['__all__'] + codes,
                                 format_func=lambda c: t('Tous les thèmes', 'All themes') if c == '__all__' else tr(i18n.T(T.libelle(c))),
                                 key='xt_theme')
        visible = [k for k, q in qs.items() if (theme == '__all__' or T.theme_de(q.get('category')) == theme) and k not in used]
        if st.session_state.get('xt_question') not in visible:
            st.session_state['xt_question'] = None
        with cols[1]:
            qid = st.selectbox(t('Question', 'Question'), visible, index=None,
                               format_func=lambda k: tr(L.question(qs[k]['question'])),
                               placeholder=t('Tapez un mot-clé…', 'Type a keyword…'), key='xt_question')
        if qid is None:
            st.caption(t('Choisissez la question à croiser avec le cas.', 'Choose the question to cross with the outcome.'))
            return
        groups, gbase = LP.answers(cat, qs[qid]); titre = tr(L.question(qs[qid]['question']))
    else:
        groups, gbase = LP.registry(cat, choix)
    common = base & gbase
    rows = tableau(y, common, groups)
    for r in rows:
        r['label'] = tr(L.modalite(r['groupe']))
    if len(rows) < 2:
        st.info(t('Pas assez de modalités renseignées pour croiser.', 'Not enough recorded categories to cross.'))
        return
    n = int(common.sum()); k = int((y & common).sum())
    st.markdown(f'**{escape(titre)}** · ' + t(f'{n} ménages avec réponse aux deux variables, dont {k} concernés par le cas ({100 * k / n:.1f} %).',
                                               f'{n} households with an answer to both variables, {k} of them affected ({100 * k / n:.1f}%).'))
    st.markdown(_barres(rows, t), unsafe_allow_html=True)
    table = pd.DataFrame([{t('Modalité', 'Category'): r['label'], t('Ménages', 'Households'): r['n'],
                           t('Concernés', 'Affected'): r['cas'], t('Fréquence du cas', 'Outcome frequency'): round(r['pct'], 1)} for r in rows])
    st.dataframe(table, hide_index=True, use_container_width=True)

    petits = [r['label'] for r in rows if r['n'] < SEUIL]
    if petits:
        st.caption(t('Moins de 30 ménages pour : ', 'Fewer than 30 households for: ') + ', '.join(petits)
                   + t('. Les pourcentages de ces lignes sont fragiles.', '. Percentages on these rows are fragile.'))
    # Question à réponses multiples : les modalités se recouvrent, aucun test
    # d'indépendance n'a de sens sur ce tableau ; on s'en tient aux pourcentages.
    recouvrement = int(sum(int((common & m).sum()) for m in groups.values())) > n
    if recouvrement:
        st.caption(t('Question à réponses multiples : un ménage peut figurer sur plusieurs lignes, les pourcentages se lisent ligne par ligne et aucun test global n’est calculé.',
                     'Multiple-response question: a household can appear on several rows; read percentages row by row, no overall test is computed.'))
        return
    stats = khi2(rows)
    if stats is None:
        return
    lignes = []
    if len(rows) == 2:
        z = common & groups[rows[0]['groupe']]
        res = I.test(y[common], z[common], I.section_ids(cat)[common])
        phi = res['phi']
        if np.isfinite(phi):
            lignes.append(t(f'φ = {phi:+.3f} (signe rapporté à « {rows[0]["label"]} »).', f'phi = {phi:+.3f} (sign relative to “{rows[0]["label"]}”).'))
        if np.isfinite(res['p']):
            lignes.append(t(f'p = {res["p"]:.3f}, test bootstrap regroupé par section, le même que pour les classements.',
                            f'p = {res["p"]:.3f}, section-clustered bootstrap test, the same as for the rankings.'))
        else:
            lignes.append(t('Test regroupé par section non calculable ici (effectif ou sections insuffisants).',
                            'Section-clustered test not computable here (insufficient sample or sections).'))
    lignes.append(t(f'V de Cramér = {stats["v"]:.3f} ; khi² = {stats["stat"]:.1f} ({stats["df"]} ddl), p ≈ {stats["p"]:.3f}, approximation qui ignore le regroupement par section.',
                    f'Cramér’s V = {stats["v"]:.3f}; chi-square = {stats["stat"]:.1f} ({stats["df"]} df), p ≈ {stats["p"]:.3f}, an approximation that ignores section clustering.'))
    if stats['faible']:
        lignes.append(t('Certaines cases attendues sont inférieures à 5 : le khi² est peu fiable.', 'Some expected cells are below 5: the chi-square is unreliable.'))
    st.caption(' '.join(lignes))
    st.caption(t('Lecture : V (et φ) mesurent la force du lien, de 0 (aucun) à 1 (parfait) ; p dit si l’écart entre modalités dépasse ce que le hasard produirait. Un lien n’est pas une cause.',
                 'Reading: V (and phi) measure the strength of the association, from 0 (none) to 1 (perfect); p says whether the gap between categories exceeds what chance would produce. An association is not a cause.'))
