"""Onglet « Croiser des questions ».

On empile des conditions — « n'a pas de toilettes améliorées » ET « n'a pas
d'eau améliorée » ET « pas d'électricité » — et on obtient le nombre de foyers
concernés, la carte par section communale et la ventilation par sexe,
catégorie économique et âge.

Le calcul repose sur `data/croisement.npz` : pour chaque réponse de chaque
question, l'appartenance de chacun des 1211 répondants, en bits. Les effectifs
seuls ne permettraient pas de calculer une intersection.
"""

import json
import os

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import map_render

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Beaulieu", "Blactote", "Dalmette",
            "Débouchette", "Dumont", "Mouline", "Quentin", "Trichet"]
SOUS_POP = ["Homme", "Femme", "Cat A", "Cat B", "Cat C",
            "<25", "25-39", "40-59", "60+", "Littoral", "Montagne"]
SOUS_POP_LABEL = {
    "Homme": "Hommes", "Femme": "Femmes",
    "Cat A": "Cat A — pauvreté extrême", "Cat B": "Cat B — pauvreté",
    "Cat C": "Cat C — non pauvre",
    "<25": "Moins de 25 ans", "25-39": "25 à 39 ans",
    "40-59": "40 à 59 ans", "60+": "60 ans et plus",
    "Littoral": "Littoral", "Montagne": "Montagne",
}
N_FRAGILE = 30
MAX_CONDITIONS = 5


def _trouver(nom):
    for chemin in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(chemin):
            return chemin
    return None


@st.cache_data(show_spinner=False)
def _charger():
    ci, cn = _trouver("croisement_index.json"), _trouver("croisement.npz")
    if ci is None or cn is None:
        manquants = [n for n, c in (("croisement_index.json", ci),
                                    ("croisement.npz", cn)) if c is None]
        return None, manquants, None, None
    with open(ci, encoding="utf-8") as f:
        index = json.load(f)
    z = np.load(cn)
    n = int(z["n"][0])
    bits = np.unpackbits(z["bits"], axis=1)[:, :n].astype(bool)
    grp = np.unpackbits(z["groupes"], axis=1)[:, :n].astype(bool)
    groupes = {nom: grp[k] for k, nom in enumerate(index["groupes"])}
    return index, None, bits, groupes


def _vecteur(index, bits, qi, labels):
    """Foyers ayant coché au moins une des réponses listées."""
    q = next(x for x in index["questions"] if x["i"] == qi)
    m = np.zeros(bits.shape[1], dtype=bool)
    for lab in labels:
        if lab in q["modalites"]:
            m |= bits[q["debut"] + q["modalites"].index(lab)]
    return m


def render():
    index, manquants, bits, groupes = _charger()
    if index is None:
        st.title("Croiser des questions")
        st.error(
            "Fichier(s) absent(s) du projet : **" + "**, **".join(manquants)
            + "**.\n\nDéposez-les sur GitHub dans `data/` ou à la racine du "
              "dépôt — les deux emplacements fonctionnent.")
        st.stop()

    n_total = bits.shape[1]
    questions = index["questions"]

    st.title("Croiser des questions")
    st.caption(
        "Empilez des conditions pour compter les foyers qui les remplissent "
        "toutes en même temps — par exemple sans toilettes améliorées, sans eau "
        "améliorée et sans électricité. "
        f"{len(questions)} des 503 questions de l'enquête sont croisables.")

    # ------------------------------------------------------------ conditions
    if "nb_conditions" not in st.session_state:
        st.session_state["nb_conditions"] = 2

    liaison = st.radio(
        "Comment combiner les conditions",
        ["ET", "OU"],
        format_func=lambda k: {
            "ET": "ET — le foyer remplit TOUTES les conditions (cumul)",
            "OU": "OU — le foyer remplit AU MOINS UNE condition"}[k],
        horizontal=True, key="croix_liaison")

    libelles = [f"{q['category'].split('. ', 1)[-1]} · {q['question']}"
                for q in questions]

    masques, resumes = [], []
    for k in range(st.session_state["nb_conditions"]):
        with st.container(border=True):
            c1, c2 = st.columns([3, 2])
            with c1:
                choix = st.selectbox(f"Condition {k + 1} — question", libelles,
                                     index=min(k, len(libelles) - 1),
                                     key=f"cq_{k}")
            q = questions[libelles.index(choix)]
            # Changer de question vide les réponses cochées, qui appartenaient
            # à l'ancienne : on repositionne d'office sur la première, sinon la
            # condition disparaît silencieusement sous les yeux de l'utilisateur.
            memo = f"cq_prec_{k}"
            if st.session_state.get(memo) != choix:
                st.session_state[memo] = choix
                st.session_state[f"cm_{k}"] = q["modalites"][:1]
            with c2:
                sens = st.selectbox(
                    "Le foyer…", ["a", "n_a_pas"],
                    format_func=lambda s: {"a": "a répondu…",
                                           "n_a_pas": "n'a PAS répondu…"}[s],
                    key=f"cs_{k}")
            reponses = st.multiselect(
                "Réponse(s) concernée(s)", q["modalites"], key=f"cm_{k}",
                help="Plusieurs réponses se cumulent : le foyer compte s'il en "
                     "a coché au moins une.")
            if not reponses:
                st.caption("Condition ignorée : aucune réponse choisie.")
                continue
            m = _vecteur(index, bits, q["i"], reponses)
            if sens == "n_a_pas":
                m = ~m
            masques.append(m)
            mot = "a" if sens == "a" else "n'a pas"
            resumes.append(f"{mot} « {' ou '.join(reponses)} » "
                           f"({q['question']})")
            st.caption(f"Cette condition seule : **{int(m.sum())} foyers** "
                       f"({m.mean() * 100:.1f} %)")

    c_moins, c_plus, _ = st.columns([1, 1, 4])
    with c_plus:
        if st.button("Ajouter une condition", use_container_width=True,
                     disabled=st.session_state["nb_conditions"] >= MAX_CONDITIONS):
            st.session_state["nb_conditions"] += 1
            st.rerun()
    with c_moins:
        if st.button("Retirer la dernière", use_container_width=True,
                     disabled=st.session_state["nb_conditions"] <= 1):
            st.session_state["nb_conditions"] -= 1
            st.rerun()

    if not masques:
        st.info("Choisissez au moins une réponse pour lancer le calcul.")
        return

    with st.container(border=True):
        st.markdown('<div class="titre-bloc vert">2 · Le résultat</div>',
                    unsafe_allow_html=True)
        # ------------------------------------------------------------ résultat
        total = masques[0].copy()
        for m in masques[1:]:
            total = (total & m) if liaison == "ET" else (total | m)

        n_ret = int(total.sum())
        pct = n_ret / n_total * 100

        st.markdown(
            "Foyers qui, **en même temps** :" if liaison == "ET"
            else "Foyers qui remplissent **au moins une** de ces conditions :")
        for r in resumes:
            st.markdown(f"- {r}")

        # Un cumul de conditions n'est jamais le produit des taux : si les
        # privations frappent les mêmes foyers, le cumul observé dépasse ce que
        # l'indépendance prédirait. L'écart est l'information intéressante.
        attendu = np.prod([m.mean() for m in masques]) * 100 if liaison == "ET" else None
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(map_render.cartouche_html(
                "Foyers concernés", int(n_ret), f"sur {n_total}",
                "effectif brut dans l'échantillon", couleur="#1a6bb0"),
                unsafe_allow_html=True)
        with c2:
            st.markdown(map_render.cartouche_html(
                "Part de l'échantillon", round(pct, 1), "%",
                "des 1211 ménages enquêtés", couleur="#1a6bb0"),
                unsafe_allow_html=True)
        with c3:
            if attendu is not None and len(masques) > 1:
                ecart = pct - attendu
                coul = "#98161c" if ecart > 0 else "#3d9e4f"
                st.markdown(map_render.cartouche_html(
                    "Si les conditions étaient indépendantes",
                    round(attendu, 1), "%",
                    ("observé plus élevé : les situations se cumulent sur les mêmes "
                     "foyers" if ecart > 0 else
                     "observé plus faible : les situations se recoupent peu"),
                    couleur=coul), unsafe_allow_html=True)
            else:
                st.markdown(map_render.cartouche_html(
                    "Conditions empilées", int(len(masques)), "",
                    "combinées par « " + liaison + " »", couleur="#5b6b7a"),
                    unsafe_allow_html=True)

        if n_ret < N_FRAGILE:
            st.warning(
                f"Seulement {n_ret} foyers correspondent à cette combinaison. "
                "Le chiffre national reste lisible, mais la répartition par section "
                "communale et par sous-population n'est plus fiable — quelques "
                "foyers par case.")

    with st.container(border=True):
        st.markdown('<div class="titre-bloc ambre">3 · Où sont ces foyers</div>',
                    unsafe_allow_html=True)
        # ------------------------------------------------------------ carte
        valeurs, bases = {}, {}
        for s in SECTIONS:
            g = groupes.get(s)
            if g is None:
                continue
            bases[s] = int(g.sum())
            valeurs[s] = round(float((total & g).sum()) / g.sum() * 100, 1) if g.sum() else None

        seuils = map_render.nice_thresholds([v for v in valeurs.values()
                                             if v is not None])
        polarite = st.radio(
            "Sens de lecture des couleurs",
            ["eleve_mauvais", "eleve_bon", "neutre"],
            format_func=lambda k: {
                "eleve_mauvais": "Un pourcentage élevé est défavorable (vert → rouge)",
                "eleve_bon": "Un pourcentage élevé est favorable (rouge → vert)",
                "neutre": "Ni bon ni mauvais — dégradé de bleu"}[k],
            horizontal=True, key="croix_pol")

        infos = {s: f"{int((total & groupes[s]).sum())} foyers sur {bases[s]}"
                 for s in SECTIONS if s in groupes}
        hauteur = 720
        svg, T, _ = map_render.render_map_svg(
            valeurs, bases, seuils, height=hauteur, polarity=polarite, infos=infos)
        legende = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:7px;margin-right:18px">'
            f'<span style="width:22px;height:12px;border-radius:3px;background:{c};'
            f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)"></span>'
            f'<span style="font-size:13px;color:#52514e">{lab}</span></span>'
            for c, lab in map_render.legend_items(T, polarite))
        components.html(
            f"""<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
                            background:#fcfcfb">
              <div style="margin:0 0 8px"><span style="font-size:11.5px;color:#898781;
                letter-spacing:.05em;margin-right:14px">SEUILS</span>{legende}</div>
              {svg}
            </div>""",
            height=hauteur + 46, scrolling=False)

    # ------------------------------------------------------------ classement
    ordre = sorted((s for s in valeurs if valeurs[s] is not None),
                   key=lambda s: valeurs[s])
    RAMP = map_render.ramp_for(polarite)
    bars = map_render.render_score_bars_svg(
        [(s, valeurs[s]) for s in ordre], vmax=max(valeurs.values() or [1]),
        unite=" %", colors={s: RAMP[map_render.bin_of(valeurs[s], T)][0]
                            for s in ordre},
        annotations={s: f"({int((total & groupes[s]).sum())} foyers sur {bases[s]})"
                     for s in ordre})
    components.html(
        f'<div style="background:#fcfcfb;font-family:system-ui,-apple-system,'
        f"'Segoe UI',sans-serif\">{bars}</div>",
        height=len(ordre) * 28 + 26, scrolling=False)

    with st.container(border=True):
        st.markdown('<div class="titre-bloc">4 · Qui sont ces foyers</div>',
                    unsafe_allow_html=True)
        # ------------------------------------------------------------ ventilation
        lignes = []
        for g in SOUS_POP:
            m = groupes.get(g)
            if m is None or not m.sum():
                continue
            touche = int((total & m).sum())
            lignes.append({
                "Sous-population": SOUS_POP_LABEL.get(g, g),
                "Foyers concernés": touche,
                "Base": int(m.sum()),
                "Part du groupe (%)": round(touche / m.sum() * 100, 1),
            })
        df = pd.DataFrame(lignes).sort_values("Part du groupe (%)", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(
            "« Part du groupe » = proportion de ce groupe qui remplit la combinaison. "
            "C'est cette colonne qui se compare d'une ligne à l'autre, pas l'effectif : "
            "les groupes n'ont pas la même taille.")

    st.download_button(
        "Télécharger ce tableau (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="croisement_questions.csv", mime="text/csv")

    st.caption("Source : enquête ménage sept. 2024 (1211 répondants). "
               "Les combinaisons sont calculées répondant par répondant, pas à "
               "partir des pourcentages agrégés.")
    st.caption("Travail réalisé par le Programme des Nations Unies pour "
               "l'environnement (PNUE / UNEP).")
