"""Onglet « Indicateurs de résilience » du tableau de bord.

Les scores ne sont pas recalculés à la volée : ils sont figés dans deux
fichiers produits par le chantier de vérification (resultats.json pour le
national et la comparaison entre sections, ventilation.json pour le croisement
section × sous-population). L'app ne fait que lire, agréger et dessiner.
"""

import json
import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import assets
import map_render
import radar
import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SOUS_POP = ["Total", "Homme", "Femme", "Cat A", "Cat B", "Cat C",
            "<25", "25-39", "40-59", "60+"]
SOUS_POP_CLE = {
    "Total": "tous_repondants", "Homme": "hommes", "Femme": "femmes",
    "Cat A": "cat_a", "Cat B": "cat_b", "Cat C": "cat_c",
    "<25": "age_25", "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
}


def libelle_pop(code):
    return T(SOUS_POP_CLE.get(code, code))

DIM_CLE = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "dim1",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION": "dim2",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "dim3",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION": "dim4",
    "V. SOCIAL AND COMMUNITY DIMENSION": "dim5",
    "VI. HUMAN DIMENSION": "dim6",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION": "dim7",
}
DIM_ORDRE = list(DIM_CLE)


class _Dim(dict):
    """Nom court de la dimension, dans la langue courante."""
    def __missing__(self, k):
        return T(DIM_CLE.get(k, k))

    def get(self, k, d=None):
        return self[k]


DIM_COURT = _Dim()

N_FRAGILE = 30




def _trouver(nom):
    """Cherche un fichier de données dans data/ puis à la racine du projet.

    Sur GitHub, un glisser-déposer de dossier ne conserve pas toujours
    l'arborescence : plutôt que de planter, on accepte les deux emplacements.
    """
    for chemin in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(chemin):
            return chemin
    return None


@st.cache_data(show_spinner=False)
def _charger():
    chemins = {nom: _trouver(nom) for nom in ("resultats.json", "ventilation.json")}
    manquants = [nom for nom, c in chemins.items() if c is None]
    if manquants:
        return None, manquants
    with open(chemins["resultats.json"], encoding="utf-8") as f:
        res = json.load(f)
    with open(chemins["ventilation.json"], encoding="utf-8") as f:
        vent = json.load(f)
    return res, vent


def nom_indic(r):
    """Nom de l'indicateur dans la langue courante."""
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r["indicateur"]


def expl_indic(r):
    """Explication en langage clair, dans la langue courante."""
    return (r.get("expl_fr") if i18n.get_lang() == "fr" else r.get("expl_en")) or ""


def unite_mesure(indic):
    """Unité et libellé de la mesure brute, selon la source de l'indicateur.

    « 31,9 % des ménages » a du sens pour l'enquête ménage, aucun pour un taux
    de déboisement annuel ou pour un décompte d'organisations. Se tromper ici
    ne produit pas une erreur visible, juste une phrase fausse — d'où ce
    branchement explicite.
    """
    if indic is None:
        return '%', T("r_des_menages")
    source = indic.get("source")
    if source == "OCB":
        if indic.get("unite") == "organisations":
            return '', T("r_des_organisations_n")
        return '%', T("r_des_organisations")
    if source == "satellite":
        return indic.get("unite") or '%', T("r_unite_satellite")
    return '%', T("r_des_menages")


def _pct(score):
    """Position du score sur l'échelle APRI, en pourcentage (5/10 → 50 %)."""
    return None if score is None else round(score * 10, 1)


def _bandeau_scores(entrees, libelle_mesure=None, unite='%'):
    """Un cartouche par entrée : la mesure brute en % de ménages quand elle
    existe, puis le score APRI qu'elle produit, et ce score en % de l'échelle.

    Les deux chiffres répondent à deux questions différentes et doivent rester
    visibles ensemble : « 31,8 % des ménages ont un assainissement amélioré »
    dit ce qui se passe sur le terrain ; « score 2,3 » dit où cela place
    la section sur l'échelle de comparaison internationale.
    """
    cols = st.columns(len(entrees))
    for col, (libelle, score, mesure) in zip(cols, entrees):
        coul = map_render.RAMP_APRI[
            map_render.bin_of(score, map_render.SEUILS_APRI)][0]
        note_score = T("r_note_score", p=f"{_pct(score):.0f}")
        # Le score garde deux décimales : entre 4,04 et 4,25 il n'y a qu'un
        # centième d'écart de rang, l'arrondi au dixième les confondrait.
        score_txt = f'{score:.2f}'.replace('.', ',')
        if mesure is None:
            html = map_render.cartouche_html(
                libelle, score_txt, '', note_score, couleur=coul)
        else:
            html = map_render.cartouche_html(
                libelle, round(mesure, 1), unite,
                libelle_mesure or T("r_des_menages"),
                score_txt, '', note_score, couleur=coul)
        with col:
            st.markdown(html, unsafe_allow_html=True)


def _radar_html(svg, series, hauteur):
    return (f'<div style="background:#ffffff;font-family:system-ui,-apple-system,'
            f"'Segoe UI',sans-serif\">"
            f'<div style="margin:0 0 6px 8px">{radar.legende_html(series)}</div>'
            f'{svg}</div>')


def _section_radars(res, vent, scorables, poids, sections, pop, dims_scorees):
    """Deux niveaux de radar : le profil des dimensions, puis le détail des
    indicateurs à l'intérieur d'une dimension — la même logique de zoom que
    dans le cadre théorique APRI."""
    niveau = st.radio(
        T("r_niveau"),
        ["dimensions", "indicateurs"],
        format_func=lambda k: {"dimensions": T("r_niveau1"),
                               "indicateurs": T("r_niveau2")}[k],
        horizontal=True, key=f"radar_niveau_{i18n.get_lang()}")

    NOTION_DIM = {"dim1": "dim_physique", "dim2": "dim_institutionnelle",
                  "dim3": "dim_environnementale", "dim4": "dim_economique",
                  "dim5": "dim_sociale", "dim6": "dim_humaine",
                  "dim7": "dim_culturelle"}

    if niveau == "dimensions":
        axes_dim = dims_scorees
        axes = [DIM_COURT[d] for d in axes_dim]
        groupes = {DIM_COURT[d]: [r["ligne"] for r in scorables
                                  if r["dimension"] == d] for d in axes_dim}
    else:
        dim = st.selectbox(
            T("r_dim_detail"), dims_scorees,
            format_func=lambda d: DIM_COURT[d], key=f"radar_dim_{i18n.get_lang()}")
        dedans = [r for r in scorables if r["dimension"] == dim]
        if len(dedans) < 3:
            st.info(T("r_trop_peu", n=len(dedans)))
            return
        axes = [nom_indic(r) for r in dedans]
        groupes = {nom_indic(r): [r["ligne"]] for r in dedans}
        _n = NOTION_DIM.get(DIM_CLE.get(dim))
        if _n:
            st.markdown(
                '<p style="font-size:15px;color:#3c4761;margin:0 0 6px">'
                + map_render.bulle_notion(_n) + '</p>', unsafe_allow_html=True)

    # Codes stables : « __toutes__ » plutôt que le libellé traduit, sinon un
    # changement de langue laisserait une sélection orpheline.
    a_comparer = ["__toutes__"] + list(sections)
    choisies = st.multiselect(
        T("r_comparer"), a_comparer,
        format_func=lambda c: T("r_ensemble") if c == "__toutes__" else c,
        default=["__toutes__"], max_selections=3, key=f"radar_cmp_{niveau}_{i18n.get_lang()}")
    if not choisies:
        st.info(T("r_choisir_section"))
        return

    def valeurs_pour(nom):
        vals = []
        for ax in axes:
            lgs = groupes[ax]
            if nom == "__toutes__":
                pris = [_score_pondere(lgs, vent["sections"][s], s, pop, poids)
                        for s in sections]
                pris = [v for v in pris if v is not None]
                vals.append(round(sum(pris) / len(pris), 2) if pris else None)
            else:
                vals.append(_score_pondere(lgs, vent["sections"][nom],
                                           nom, pop, poids))
        return vals

    def _nom(c):
        return T("r_ensemble") if c == "__toutes__" else c

    series = [(_nom(nom), valeurs_pour(nom), None) for nom in choisies]
    svg = radar.render_radar_svg(axes, series, taille=620)
    components.html(_radar_html(svg, series, 640), height=690, scrolling=False)

    st.caption(T("r_radar_dim") if niveau == "dimensions" else T("r_radar_ind"))

    # Au niveau des indicateurs, la mesure brute accompagne chaque score.
    mesures = {}
    if niveau == "indicateurs":
        for ax in axes:
            lg = groupes[ax][0]
            for nom in choisies:
                if nom == "__toutes__":
                    pris = [vent["sections"][s][str(lg)]["valeurs"].get(pop)
                            for s in sections]
                    pris = [v for v in pris if v is not None]
                    mesures[(ax, _nom(nom))] = (round(sum(pris) / len(pris), 1)
                                                if pris else None)
                else:
                    mesures[(ax, _nom(nom))] = \
                        vent["sections"][nom][str(lg)]["valeurs"].get(pop)

    tab = []
    for i, ax in enumerate(axes):
        rec = {T("r_axe"): ax}
        for nom, vals, _ in series:
            v = vals[i]
            if v is None:
                rec[nom] = None
                continue
            texte = f"{v:.2f}".replace(".", ",") + f" — {_pct(v):.0f} %"
            m = mesures.get((ax, nom))
            if m is not None:
                texte = (f'{f"{m:.1f}".replace(".", ",")} % '
                         + T("r_des_menages_court") + f' → {texte}') 
            rec[nom] = texte
        tab.append(rec)
    st.dataframe(pd.DataFrame(tab), use_container_width=True, hide_index=True)
    if niveau == "indicateurs":
        st.caption(T("r_lecture_cellule"))


def _scorables(res):
    return [r for r in res if r["calculable"] != "non" and not r["bareme_absent"]]


def _score_pondere(lignes, bloc, sec, pop, poids):
    """Moyenne des scores pondérée par les pondérations de la théorie."""
    num = den = 0.0
    for lg in lignes:
        sc = bloc[str(lg)]["scores"].get(pop)
        if sc is None:
            continue
        p = poids[lg]
        num += p * sc
        den += p
    return round(num / den, 2) if den else None


def render():
    res, vent = _charger()
    if res is None:
        st.title(T("r_titre"))
        st.error(T("r_fichiers_absents", f="**, **".join(vent)))
        st.info(T("r_autre_onglet"))
        st.stop()
    scorables = _scorables(res)
    poids = {r["ligne"]: (r["ponderation"] or 0.0) for r in res}
    par_ligne = {r["ligne"]: r for r in res}
    sections = list(vent["sections"].keys())

    col_logo, col_titre = st.columns([1, 6])
    with col_logo:
        st.markdown(
            f'<img src="data:image/png;base64,{assets.LOGO_APRI}" '
            f'style="width:118px;margin-top:6px">', unsafe_allow_html=True)
    with col_titre:
        st.title(T("r_titre"))
        st.markdown(
            '<p style="font-size:12.5px;color:#6b7590;letter-spacing:.06em;'
            'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
            + T("r_sous_titre") + "</p>", unsafe_allow_html=True)
    st.markdown(map_render.styles_bulle(), unsafe_allow_html=True)
    st.caption(T("r_intro", n=len(scorables), t=len(res)))
    st.markdown(
        '<p style="font-size:15px;color:#3c4761;margin:2px 0 0">'
        + map_render.bulle_notion("resilience") + " &nbsp;·&nbsp; "
        + map_render.bulle_notion("apri") + " &nbsp;·&nbsp; "
        + map_render.bulle_notion("attributs_aaa") + " &nbsp;·&nbsp; "
        + map_render.bulle_notion("ponderation") + " &nbsp;·&nbsp; "
        + map_render.bulle_notion("pas_de_seuil") + "</p>",
        unsafe_allow_html=True)

    # ---------------------------------------------------------- sélecteurs
    with st.sidebar:
        st.header(T("r_titre_court"))
        pop = st.selectbox(
            T("r_sous_pop"), SOUS_POP,
            format_func=lambda k: libelle_pop(k),
            help=T("r_sous_pop_aide"))

    OPT_FINAL = T("r_score_final")
    dims_scorees = [d for d in DIM_ORDRE
                    if any(r["dimension"] == d for r in scorables)]
    opt_dims = [T("r_dimension_prefix") + DIM_COURT[d] for d in dims_scorees]
    opt_ind = [f"{DIM_COURT[r['dimension']]} · {nom_indic(r)}" for r in scorables]
    choix = st.selectbox(T("r_quoi_carto"), [OPT_FINAL] + opt_dims + opt_ind)

    if choix == OPT_FINAL:
        lignes = [r["ligne"] for r in scorables]
        titre = T("r_score_final")
        indic = None
    elif choix.startswith(T("r_dimension_prefix")):
        dim = next(d for d in dims_scorees
                   if DIM_COURT[d] == choix[len(T("r_dimension_prefix")):])
        lignes = [r["ligne"] for r in scorables if r["dimension"] == dim]
        titre = DIM_COURT[dim]
        indic = None
    else:
        indic = scorables[opt_ind.index(choix)]
        lignes = [indic["ligne"]]
        titre = nom_indic(indic)

    # ---------------------------------------------------------- valeurs
    scores, pourcents, effectifs = {}, {}, {}
    for sec in sections:
        bloc = vent["sections"][sec]
        effectifs[sec] = vent["effectifs"][sec][pop]
        scores[sec] = _score_pondere(lignes, bloc, sec, pop, poids)
        if indic is not None:
            pourcents[sec] = bloc[str(indic["ligne"])]["valeurs"].get(pop)

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("r_bloc1")}</div>',
                    unsafe_allow_html=True)
        st.subheader(f"{titre} — {libelle_pop(pop)}")
        if indic is not None:
            _def = []
            if indic.get("metrique"):
                _def.append(T("r_definition") + indic["metrique"])
            if indic.get("echelle"):
                _def.append(T("r_bareme") + indic["echelle"])
            if indic.get("note"):
                _def.append(T("r_reserve") + indic["note"])
            _clair = expl_indic(indic)
            if _clair:
                st.markdown(
                    '<div style="background:#f4f8fc;border-left:4px solid #1a6bb0;'
                    'border-radius:0 10px 10px 0;padding:12px 16px;margin:2px 0 10px">'
                    '<div style="font-size:11.5px;letter-spacing:.09em;'
                    'text-transform:uppercase;font-weight:700;color:#1a6bb0;'
                    'margin-bottom:5px">' + T("r_expl_indic") + '</div>'
                    '<div style="font-size:15.5px;line-height:1.6;color:#2b3446">'
                    + _clair + '</div></div>', unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:15px;color:#3c4761;margin:0 0 4px">'
                + T("r_ce_que_mesure")
                + map_render.bulle("_indic", definition="<br><br>".join(_def),
                                   texte="")
                + " &nbsp;·&nbsp; " + T("r_question_enquete", q=indic["question"])
                + '</p>', unsafe_allow_html=True)
            if indic["modalites"]:
                st.caption(T("r_reponses_comptees", m=indic["modalites"]))

        # ---- le chiffre en tête : score sur 10 ET en pourcentage de l'échelle --
        dispo = [v for v in scores.values() if v is not None]
        if dispo:
            moyenne = sum(dispo) / len(dispo)
            haut = max((s for s in sections if scores[s] is not None),
                       key=lambda s: scores[s])
            bas = min((s for s in sections if scores[s] is not None),
                      key=lambda s: scores[s])

            def mesure(sec=None):
                """Mesure brute en % de ménages — seulement sur un indicateur seul."""
                if indic is None:
                    return None
                if sec is not None:
                    return pourcents.get(sec)
                pris = [v for v in pourcents.values() if v is not None]
                return round(sum(pris) / len(pris), 1) if pris else None

            _unite, _libelle_mesure = unite_mesure(indic)
            _bandeau_scores(
                [(T("r_moyenne"), moyenne, mesure()),
                 (T("r_plus_haut", s=haut), scores[haut], mesure(haut)),
                 (T("r_plus_bas", s=bas), scores[bas], mesure(bas))],
                libelle_mesure=_libelle_mesure, unite=_unite)
            if indic is not None:
                st.markdown(
                    '<p style="font-size:15px;color:#3c4761;margin:8px 0 0">'
                    + map_render.bulle("mesure brute")
                    + T("r_deux_lectures")
                    + map_render.bulle("score APRI")
                    + T("r_deux_lectures_suite") + "</p>", unsafe_allow_html=True)
            else:
                st.caption(T("r_agregat"))

        petits = [s for s in sections if effectifs[s] < N_FRAGILE]
        if petits:
            st.warning(T("r_petits", n=N_FRAGILE, liste=", ".join(petits)))

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc ambre">{T("r_bloc2")}</div>',
                    unsafe_allow_html=True)
        # ---------------------------------------------------------- carte
        afficher = st.radio(
            T("r_colorier"),
            ["score", "pourcentage"] if indic is not None else ["score"],
            format_func=lambda k: {"score": T("r_par_score"),
                                   "pourcentage": T("r_par_brut")}[k],
            horizontal=True, key=f"aff_{choix}_{pop}_{i18n.get_lang()}")

        if afficher == "score":
            valeurs = scores
            unite = ""
            seuils = map_render.SEUILS_APRI
            rampe = map_render.RAMP_APRI
            polarite = "eleve_bon"          # un score élevé est toujours favorable
            vmax = 10.0
        else:
            valeurs = pourcents
            unite = "%"
            rampe = None
            seuils = map_render.nice_thresholds(
                [v for v in valeurs.values() if v is not None])
            polarite = map_render.guess_polarity(indic["question"],
                                                 indic["modalites"] or "")
            vmax = max([v for v in valeurs.values() if v is not None] or [1])

        hauteur = 720
        # L'infobulle porte toujours les deux chiffres, quelle que soit la couche
        # affichée : la mesure brute et le score qu'elle produit.
        bulles = {}
        if indic is not None:
            for s in sections:
                morceaux = []
                if pourcents.get(s) is not None:
                    morceaux.append(f'{pourcents[s]:.1f}'.replace('.', ',')
                                + ' % ' + T("r_des_menages_court"))
                if scores.get(s) is not None:
                    morceaux.append(T("r_score_mot") + f" {scores[s]:.0f}")
                if morceaux:
                    bulles[s] = ' · '.join(morceaux)

        svg, seuils_ret, rendu = map_render.render_map_svg(
            valeurs, effectifs, seuils, height=hauteur,
            polarity=polarite, unite=unite, ramp=rampe, infos=bulles)

        if rampe is map_render.RAMP_APRI:
            st.markdown(
                '<p style="font-size:15px;color:#3c4761;margin:2px 0 6px">'
                + map_render.bulle_notion("echelle_0_10", texte=T("r_echelle_titre"))
                + " &nbsp;·&nbsp; "
                + map_render.bulle_notion("bareme_comparatif")
                + " &nbsp;·&nbsp; "
                + map_render.bulle_notion("score_capacite_pas_resilience")
                + "</p>", unsafe_allow_html=True)
            # Onze classes, une par point de score : la légende reprend l'échelle
            # APRI telle quelle, du rouge (0) au vert foncé (10).
            legende = "".join(
                f'<span style="display:inline-flex;flex-direction:column;'
                f'align-items:center;margin-right:6px">'
                f'<span style="width:30px;height:14px;background:{c};'
                f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)"></span>'
                f'<span style="font-size:11.5px;color:#52514e;margin-top:2px">{i}</span>'
                f'</span>'
                for i, (c, _) in enumerate(map_render.RAMP_APRI))
        else:
            legende = "".join(
                f'<span style="display:inline-flex;align-items:center;gap:7px;margin-right:18px">'
                f'<span style="width:22px;height:12px;border-radius:3px;background:{c};'
                f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)"></span>'
                f'<span style="font-size:13px;color:#52514e">{lab}</span></span>'
                for c, lab in map_render.legend_items(seuils_ret, polarite, unite))

        components.html(
            f"""<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
                            background:#ffffff">
              <div style="margin:0 0 8px"><span style="font-size:11.5px;color:#898781;
                letter-spacing:.05em;margin-right:14px">{"SCORE APRI" if rampe else "SEUILS"}</span>{legende}</div>
              {svg}
            </div>""",
            height=hauteur + 46, scrolling=False)

        if afficher == "score":
            st.caption(T("r_legende_apri"))
        else:
            st.caption(map_render.polarity_caption(polarite))

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("r_bloc3")}</div>',
                    unsafe_allow_html=True)
        # ---------------------------------------------------------- classement
        ordre = sorted((s for s in sections if valeurs.get(s) is not None),
                       key=lambda s: valeurs[s])
        RAMP = rampe or map_render.ramp_for(polarite)
        couleurs = {s: RAMP[map_render.bin_of(valeurs[s], seuils_ret)][0] for s in ordre}
        # Sur un indicateur précis, chaque barre porte les deux chiffres : le score
        # et, en gris, la mesure brute qui l'a produit.
        annot = {}
        if indic is not None:
            for s in ordre:
                if afficher == "score" and pourcents.get(s) is not None:
                    annot[s] = ('(' + f'{pourcents[s]:.1f}'.replace('.', ',')
                            + ' % ' + T("r_des_menages_court") + ')')
                elif afficher != "score" and scores.get(s) is not None:
                    annot[s] = "(" + T("r_score_mot") + f" {scores[s]:.0f})"
        bars = map_render.render_score_bars_svg(
            [(s, valeurs[s]) for s in ordre], vmax=vmax, unite=unite, colors=couleurs,
            annotations=annot)
        components.html(
            f'<div style="background:#ffffff;font-family:system-ui,-apple-system,'
            f"'Segoe UI',sans-serif\">{bars}</div>",
            height=len(ordre) * 28 + 26, scrolling=False)

        if afficher == "score":
            st.caption(T("r_rappel_echelle"))

    # ---------------------------------------------------------- radars
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("r_bloc4")}</div>',
                    unsafe_allow_html=True)
        _section_radars(res, vent, scorables, poids, sections, pop, dims_scorees)

    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("r_bloc5")}</div>',
                    unsafe_allow_html=True)
        # ---------------------------------------------------------- comparaison
        st.caption(T("r_comparaison"))
        lignes_tab = []
        for sec in sections:
            bloc = vent["sections"][sec]
            rec = {T("section_communale"): sec,
                   T("paysage"): T("littoral") if vent["paysage"][sec] == "Littoral"
                   else T("montagne")}
            for p in SOUS_POP:
                v = _score_pondere(lignes, bloc, sec, p, poids)
                n = vent["effectifs"][sec][p]
                if v is None:
                    rec[p] = None
                    continue
                texte = f"{v:.2f}".replace(".", ",")
                if indic is not None:
                    brut = bloc[str(indic["ligne"])]["valeurs"].get(p)
                    if brut is not None:
                        texte = f'{f"{brut:.1f}".replace(".", ",")} % → {texte}'
                else:
                    texte = f"{texte} — {_pct(v):.0f} %"
                rec[p] = texte + (" ·" if n < N_FRAGILE else "")
            lignes_tab.append(rec)
        df = pd.DataFrame(lignes_tab)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            T("r_telecharger_csv"),
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"resilience_{titre[:30].replace(' ', '_')}.csv",
            mime="text/csv")

    # ---------------------------------------------------------- réserves
    with st.expander(T("r_reserves_titre")):
        non_calc = [r for r in res if r["calculable"] == "non"]
        st.markdown(T("r_reserves_texte", n_score=len(scorables), n_non=len(non_calc)))
        if indic is not None:
            st.markdown(T("r_reserve_indic") + indic["note"])

    st.caption(T("r_source"))
    st.caption(T("credit"))
