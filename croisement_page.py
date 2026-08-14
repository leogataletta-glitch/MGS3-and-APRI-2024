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
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Beaulieu", "Blactote", "Dalmette",
            "Débouchette", "Dumont", "Mouline", "Quentin", "Trichet"]
SOUS_POP = ["Homme", "Femme", "Cat A", "Cat B", "Cat C",
            "<25", "25-39", "40-59", "60+", "Littoral", "Montagne"]
SOUS_POP_CLE = {
    "Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a", "Cat B": "cat_b",
    "Cat C": "cat_c", "<25": "age_25", "25-39": "age_25_39",
    "40-59": "age_40_59", "60+": "age_60",
    "Littoral": "littoral", "Montagne": "montagne",
}


def libelle_pop(code):
    return T(SOUS_POP_CLE.get(code, code))
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
        st.title(T("c_titre"))
        st.error(T("c_fichiers_absents", f="**, **".join(manquants)))
        st.stop()

    n_total = bits.shape[1]
    questions = index["questions"]

    st.title(T("c_titre"))
    st.markdown(map_render.styles_bulle(), unsafe_allow_html=True)
    st.caption(T("c_intro", n=len(questions)))

    # ------------------------------------------------------------ conditions
    if "nb_conditions" not in st.session_state:
        st.session_state["nb_conditions"] = 2

    liaison = st.radio(
        T("c_combiner"),
        ["ET", "OU"],
        format_func=lambda k: {"ET": T("c_et"), "OU": T("c_ou")}[k],
        horizontal=True, key=f"croix_liaison_{i18n.get_lang()}")

    libelles = [f"{q['category'].split('. ', 1)[-1]} · {q['question']}"
                for q in questions]

    masques, resumes = [], []
    for k in range(st.session_state["nb_conditions"]):
        with st.container(border=True):
            c1, c2 = st.columns([3, 2])
            with c1:
                choix = st.selectbox(T("c_condition_q", k=k + 1), libelles,
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
                    T("c_le_foyer"), ["a", "n_a_pas"],
                    format_func=lambda s: {"a": T("c_a_repondu"),
                                           "n_a_pas": T("c_na_pas_repondu")}[s],
                    key=f"cs_{k}_{i18n.get_lang()}")
            reponses = st.multiselect(
                T("c_reponses"), q["modalites"], key=f"cm_{k}",
                help=T("c_reponses_aide"))
            if not reponses:
                st.caption(T("c_ignoree"))
                continue
            m = _vecteur(index, bits, q["i"], reponses)
            if sens == "n_a_pas":
                m = ~m
            masques.append(m)
            mot = T("c_a") if sens == "a" else T("c_na_pas")
            resumes.append(f"{mot} « {T('c_ou_mot').join(reponses)} » "
                           f"({q['question']})")
            st.caption(T("c_seule", n=int(m.sum()),
                         p=f"{m.mean() * 100:.1f}"))

    c_moins, c_plus, _ = st.columns([1, 1, 4])
    with c_plus:
        if st.button(T("c_ajouter"), use_container_width=True,
                     disabled=st.session_state["nb_conditions"] >= MAX_CONDITIONS):
            st.session_state["nb_conditions"] += 1
            st.rerun()
    with c_moins:
        if st.button(T("c_retirer"), use_container_width=True,
                     disabled=st.session_state["nb_conditions"] <= 1):
            st.session_state["nb_conditions"] -= 1
            st.rerun()

    if not masques:
        st.info(T("c_choisir"))
        return

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("c_bloc2")}</div>',
                    unsafe_allow_html=True)
        # ------------------------------------------------------------ résultat
        total = masques[0].copy()
        for m in masques[1:]:
            total = (total & m) if liaison == "ET" else (total | m)

        n_ret = int(total.sum())
        pct = n_ret / n_total * 100

        st.markdown(
            T("c_qui_en_meme_temps") if liaison == "ET"
            else T("c_qui_au_moins"))
        for r in resumes:
            st.markdown(f"- {r}")

        # Un cumul de conditions n'est jamais le produit des taux : si les
        # privations frappent les mêmes foyers, le cumul observé dépasse ce que
        # l'indépendance prédirait. L'écart est l'information intéressante.
        attendu = np.prod([m.mean() for m in masques]) * 100 if liaison == "ET" else None
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(map_render.cartouche_html(
                T("c_foyers_concernes"), int(n_ret), T("c_sur", n=n_total),
                T("c_effectif_brut"), couleur="#1a6bb0"),
                unsafe_allow_html=True)
        with c2:
            st.markdown(map_render.cartouche_html(
                T("c_part"), round(pct, 1), "%",
                T("c_des_menages"), couleur="#1a6bb0"),
                unsafe_allow_html=True)
        with c3:
            if attendu is not None and len(masques) > 1:
                ecart = pct - attendu
                coul = "#98161c" if ecart > 0 else "#3d9e4f"
                st.markdown(map_render.cartouche_html(
                    T("c_si_independantes"), round(attendu, 1), "%",
                    (T("c_plus_eleve") if ecart > 0 else T("c_plus_faible")),
                    couleur=coul), unsafe_allow_html=True)
            else:
                st.markdown(map_render.cartouche_html(
                    T("c_conditions_empilees"), int(len(masques)), "",
                    T("c_combinees", op=liaison), couleur="#5b6b7a"),
                    unsafe_allow_html=True)

        if n_ret < N_FRAGILE:
            st.warning(
                T("c_trop_peu", n=n_ret))

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("c_bloc3")}</div>',
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
            T("sens_couleurs"),
            ["eleve_mauvais", "eleve_bon", "neutre"],
            format_func=lambda k: {"eleve_mauvais": T("pol_mauvais"),
                                   "eleve_bon": T("pol_bon"),
                                   "neutre": T("pol_neutre")}[k],
            horizontal=True, key=f"croix_pol_{i18n.get_lang()}")

        infos = {s: T("c_foyers_sur", n=int((total & groupes[s]).sum()),
                      base=bases[s]) for s in SECTIONS if s in groupes}
        hauteur = 720
        svg, seuils_ret, _ = map_render.render_map_svg(
            valeurs, bases, seuils, height=hauteur, polarity=polarite, infos=infos)
        legende = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:7px;margin-right:18px">'
            f'<span style="width:22px;height:12px;border-radius:3px;background:{c};'
            f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)"></span>'
            f'<span style="font-size:13px;color:#52514e">{lab}</span></span>'
            for c, lab in map_render.legend_items(seuils_ret, polarite))
        components.html(
            f"""<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
                            background:#ffffff">
              <div style="margin:0 0 8px"><span style="font-size:11.5px;color:#898781;
                letter-spacing:.05em;margin-right:14px">{T("legende_seuils")}</span>{legende}</div>
              {svg}
            </div>""",
            height=hauteur + 46, scrolling=False)

    # ------------------------------------------------------------ classement
    ordre = sorted((s for s in valeurs if valeurs[s] is not None),
                   key=lambda s: valeurs[s])
    RAMP = map_render.ramp_for(polarite)
    bars = map_render.render_score_bars_svg(
        [(s, valeurs[s]) for s in ordre], vmax=max(valeurs.values() or [1]),
        unite=" %", colors={s: RAMP[map_render.bin_of(valeurs[s], seuils_ret)][0]
                            for s in ordre},
        annotations={s: "(" + T("c_foyers_sur",
                                n=int((total & groupes[s]).sum()),
                                base=bases[s]) + ")" for s in ordre})
    components.html(
        f'<div style="background:#ffffff;font-family:system-ui,-apple-system,'
        f"'Segoe UI',sans-serif\">{bars}</div>",
        height=len(ordre) * 28 + 26, scrolling=False)

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("c_bloc4")}</div>',
                    unsafe_allow_html=True)
        # ------------------------------------------------------------ ventilation
        lignes = []
        for g in SOUS_POP:
            m = groupes.get(g)
            if m is None or not m.sum():
                continue
            touche = int((total & m).sum())
            lignes.append({
                T("c_sous_population"): libelle_pop(g),
                T("c_foyers_col"): touche,
                T("c_base_col"): int(m.sum()),
                T("c_part_col"): round(touche / m.sum() * 100, 1),
            })
        df = pd.DataFrame(lignes).sort_values(T("c_part_col"), ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(T("c_part_note"))
        st.markdown(
            '<p style="font-size:15px;color:#3c4761;margin:8px 0 0">'
            + map_render.bulle("indépendance",
                               texte=T("c_pourquoi_independance"))
            + '</p>', unsafe_allow_html=True)

    st.download_button(
        T("r_telecharger_csv"),
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="croisement_questions.csv", mime="text/csv")

    st.caption(T("c_source"))
    st.caption(T("credit"))
