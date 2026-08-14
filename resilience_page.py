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

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SOUS_POP = ["Total", "Homme", "Femme", "Cat A", "Cat B", "Cat C",
            "<25", "25-39", "40-59", "60+"]
SOUS_POP_LABEL = {
    "Total": "Tous les répondants",
    "Homme": "Hommes", "Femme": "Femmes",
    "Cat A": "Cat A — pauvreté extrême",
    "Cat B": "Cat B — pauvreté",
    "Cat C": "Cat C — non pauvre",
    "<25": "Moins de 25 ans", "25-39": "25 à 39 ans",
    "40-59": "40 à 59 ans", "60+": "60 ans et plus",
}

DIM_COURT = {
    "I. PHYSICAL AND INFRASTRUCTURAL DIMENSION": "I. Physique et infrastructures",
    "II. INSTITUTIONAL, TECHNOLOGICAL, AND GOVERNANCE  DIMENSION":
        "II. Institutions et gouvernance",
    "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION": "III. Environnement et écologie",
    "IV. ECONOMIC, LIVELIHOODS, AND FOOD SECURITY DIMENSION":
        "IV. Économie et sécurité alimentaire",
    "V. SOCIAL AND COMMUNITY DIMENSION": "V. Social et communautaire",
    "VI. HUMAN DIMENSION": "VI. Humain",
    "VII. CULTURAL, IDENTITY-BASED, AND PSYCHOLOGICAL DIMENSION":
        "VII. Culturel et psychologique",
}
DIM_ORDRE = list(DIM_COURT)

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


def _pct(score):
    """Position du score sur l'échelle APRI, en pourcentage (5/10 → 50 %)."""
    return None if score is None else round(score * 10, 1)


def _bandeau_scores(entrees, libelle_mesure=None):
    """Un cartouche par entrée : la mesure brute en % de ménages quand elle
    existe, puis le score APRI qu'elle produit, et ce score en % de l'échelle.

    Les deux chiffres répondent à deux questions différentes et doivent rester
    visibles ensemble : « 31,8 % des ménages ont un assainissement amélioré »
    dit ce qui se passe sur le terrain ; « score 2,3 / 10 » dit où cela place
    la section sur l'échelle de comparaison internationale.
    """
    cols = st.columns(len(entrees))
    for col, (libelle, score, mesure) in zip(cols, entrees):
        coul = map_render.RAMP_APRI[
            map_render.bin_of(score, map_render.SEUILS_APRI)][0]
        note_score = (f"score de résilience — {_pct(score):.0f} % de l'échelle APRI")
        # Le score garde deux décimales : entre 4,04 et 4,25 il n'y a qu'un
        # centième d'écart de rang, l'arrondi au dixième les confondrait.
        score_txt = f'{score:.2f}'.replace('.', ',')
        if mesure is None:
            html = map_render.cartouche_html(
                libelle, score_txt, '/ 10', note_score, couleur=coul)
        else:
            html = map_render.cartouche_html(
                libelle, round(mesure, 1), '%',
                libelle_mesure or 'des ménages (mesure brute)',
                score_txt, '/ 10', note_score, couleur=coul)
        with col:
            st.markdown(html, unsafe_allow_html=True)


def _radar_html(svg, series, hauteur):
    return (f'<div style="background:#fcfcfb;font-family:system-ui,-apple-system,'
            f"'Segoe UI',sans-serif\">"
            f'<div style="margin:0 0 6px 8px">{radar.legende_html(series)}</div>'
            f'{svg}</div>')


def _section_radars(res, vent, scorables, poids, sections, pop, dims_scorees):
    """Deux niveaux de radar : le profil des dimensions, puis le détail des
    indicateurs à l'intérieur d'une dimension — la même logique de zoom que
    dans le cadre théorique APRI."""
    niveau = st.radio(
        "Niveau de lecture",
        ["dimensions", "indicateurs"],
        format_func=lambda k: {
            "dimensions": "Niveau 1 — les dimensions",
            "indicateurs": "Niveau 2 — les indicateurs d'une dimension"}[k],
        horizontal=True, key="radar_niveau")

    if niveau == "dimensions":
        axes_dim = dims_scorees
        axes = [DIM_COURT[d] for d in axes_dim]
        groupes = {DIM_COURT[d]: [r["ligne"] for r in scorables
                                  if r["dimension"] == d] for d in axes_dim}
    else:
        dim = st.selectbox(
            "Dimension à détailler", dims_scorees,
            format_func=lambda d: DIM_COURT[d], key="radar_dim")
        dedans = [r for r in scorables if r["dimension"] == dim]
        if len(dedans) < 3:
            st.info("Cette dimension ne compte que "
                    f"{len(dedans)} indicateur(s) scorable(s) : un radar demande "
                    "au moins trois axes. Choisissez-en une autre.")
            return
        axes = [r["indicateur"] for r in dedans]
        groupes = {r["indicateur"]: [r["ligne"]] for r in dedans}

    a_comparer = ["Ensemble des 10 sections"] + list(sections)
    choisies = st.multiselect(
        "Comparer (3 au maximum)", a_comparer,
        default=[a_comparer[0]], max_selections=3, key=f"radar_cmp_{niveau}")
    if not choisies:
        st.info("Choisissez au moins une section à afficher.")
        return

    def valeurs_pour(nom):
        vals = []
        for ax in axes:
            lgs = groupes[ax]
            if nom == "Ensemble des 10 sections":
                pris = [_score_pondere(lgs, vent["sections"][s], s, pop, poids)
                        for s in sections]
                pris = [v for v in pris if v is not None]
                vals.append(round(sum(pris) / len(pris), 2) if pris else None)
            else:
                vals.append(_score_pondere(lgs, vent["sections"][nom],
                                           nom, pop, poids))
        return vals

    series = [(nom, valeurs_pour(nom), None) for nom in choisies]
    svg = radar.render_radar_svg(axes, series, taille=620)
    components.html(_radar_html(svg, series, 640), height=690, scrolling=False)

    st.caption(
        "Échelle fixe de 0 à 10 sur chaque axe : deux radars se superposent "
        "directement. Un contour en pointillés signale un profil dont un axe "
        "au moins n'est pas mesuré." if niveau == "dimensions" else
        "Un axe par indicateur de la dimension, sur la même échelle 0 à 10.")

    # Au niveau des indicateurs, la mesure brute accompagne chaque score.
    mesures = {}
    if niveau == "indicateurs":
        for ax in axes:
            lg = groupes[ax][0]
            for nom in choisies:
                if nom == "Ensemble des 10 sections":
                    pris = [vent["sections"][s][str(lg)]["valeurs"].get(pop)
                            for s in sections]
                    pris = [v for v in pris if v is not None]
                    mesures[(ax, nom)] = (round(sum(pris) / len(pris), 1)
                                          if pris else None)
                else:
                    mesures[(ax, nom)] = \
                        vent["sections"][nom][str(lg)]["valeurs"].get(pop)

    tab = []
    for i, ax in enumerate(axes):
        rec = {"Axe": ax}
        for nom, vals, _ in series:
            v = vals[i]
            if v is None:
                rec[nom] = None
                continue
            texte = f"{v:.2f} / 10".replace(".", ",") + f" — {_pct(v):.0f} %"
            m = mesures.get((ax, nom))
            if m is not None:
                texte = f'{f"{m:.1f}".replace(".", ",")} % des ménages → {texte}' 
            rec[nom] = texte
        tab.append(rec)
    st.dataframe(pd.DataFrame(tab), use_container_width=True, hide_index=True)
    if niveau == "indicateurs":
        st.caption("Lecture d'une cellule : la mesure brute sur le terrain, "
                   "puis le score que le barème lui attribue et sa position sur "
                   "l'échelle APRI.")


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
        st.title("Indicateurs de résilience")
        st.error(
            "Fichier(s) de données absent(s) du projet : **"
            + "**, **".join(vent) + "**.\n\n"
            "Déposez-les sur GitHub dans le sous-dossier `data/` (à côté de "
            "`donnees_anonymisees.csv`), ou à la racine du dépôt — les deux "
            "emplacements fonctionnent. L'application redémarre toute seule "
            "ensuite.")
        st.info("Le mode « Résultats de toutes les questions aux 1200 ménages » "
                "reste utilisable : rebasculez dessus dans la barre latérale.")
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
        st.title("Indicateurs de résilience — APRI")
        st.markdown(
            '<p style="font-size:12.5px;color:#52514e;letter-spacing:.05em;'
            'text-transform:uppercase;margin:-8px 0 0 2px">'
            "IRLA / APRI — Indice de résilience des paysages ruraux</p>",
            unsafe_allow_html=True)
    st.caption(
        "Scores de 0 à 10 obtenus en appliquant les barèmes du cadre théorique aux "
        "valeurs recalculées depuis l'enquête. Un score élevé = situation plus "
        f"favorable. {len(scorables)} indicateurs sur 118 sont scorables depuis un "
        "questionnaire ménage — voir la note en bas de page."
    )

    # ---------------------------------------------------------- sélecteurs
    with st.sidebar:
        st.header("Résilience")
        pop = st.selectbox(
            "Sous-population", SOUS_POP,
            format_func=lambda k: SOUS_POP_LABEL[k],
            help="Le score est recalculé sur cette sous-population à l'intérieur "
                 "de chaque section communale.")

    OPT_FINAL = "Score final — toutes dimensions"
    dims_scorees = [d for d in DIM_ORDRE
                    if any(r["dimension"] == d for r in scorables)]
    opt_dims = [f"Dimension — {DIM_COURT[d]}" for d in dims_scorees]
    opt_ind = [f"{DIM_COURT[r['dimension']]} · {r['indicateur']}"
               for r in scorables]
    choix = st.selectbox("Quoi cartographier", [OPT_FINAL] + opt_dims + opt_ind)

    if choix == OPT_FINAL:
        lignes = [r["ligne"] for r in scorables]
        titre = "Score final de résilience"
        indic = None
    elif choix.startswith("Dimension — "):
        dim = next(d for d in dims_scorees
                   if DIM_COURT[d] == choix[len("Dimension — "):])
        lignes = [r["ligne"] for r in scorables if r["dimension"] == dim]
        titre = DIM_COURT[dim]
        indic = None
    else:
        indic = scorables[opt_ind.index(choix)]
        lignes = [indic["ligne"]]
        titre = indic["indicateur"]

    # ---------------------------------------------------------- valeurs
    scores, pourcents, effectifs = {}, {}, {}
    for sec in sections:
        bloc = vent["sections"][sec]
        effectifs[sec] = vent["effectifs"][sec][pop]
        scores[sec] = _score_pondere(lignes, bloc, sec, pop, poids)
        if indic is not None:
            pourcents[sec] = bloc[str(indic["ligne"])]["valeurs"].get(pop)

    with st.container(border=True):
        st.markdown('<div class="titre-bloc">1 · Le score en bref</div>',
                    unsafe_allow_html=True)
        st.subheader(f"{titre} — {SOUS_POP_LABEL[pop]}")
        if indic is not None:
            st.caption(f"Question de l'enquête : {indic['question']}")
            if indic["modalites"]:
                st.caption(f"Réponses comptées : {indic['modalites']}")

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

            _bandeau_scores(
                [("Moyenne des 10 sections", moyenne, mesure()),
                 (f"Score le plus élevé — {haut}", scores[haut], mesure(haut)),
                 (f"Score le plus faible — {bas}", scores[bas], mesure(bas))],
                libelle_mesure="des ménages (mesure brute)")
            if indic is not None:
                st.caption(
                    "Deux lectures à garder ensemble : le pourcentage du haut dit ce "
                    "qui est mesuré sur le terrain, le score du bas dit où cela place "
                    "la section sur l'échelle de comparaison internationale APRI. "
                    "C'est le barème qui fait le passage de l'un à l'autre — et il "
                    "n'est pas linéaire.")
            else:
                st.caption(
                    "Agrégat de plusieurs indicateurs : il n'y a pas de pourcentage "
                    "de ménages unique à afficher ici. Choisissez un indicateur précis "
                    "dans « Quoi cartographier » pour voir la mesure brute à côté du "
                    "score. Le pourcentage indiqué est la position du score sur "
                    "l'échelle APRI (5 sur 10 = 50 %).")

        petits = [s for s in sections if effectifs[s] < N_FRAGILE]
        if petits:
            st.warning(
                f"Moins de {N_FRAGILE} répondants dans : {', '.join(petits)}. "
                "Sur ces sections, l'ordre de grandeur est utilisable, le chiffre "
                "exact ne l'est pas.")

    with st.container(border=True):
        st.markdown('<div class="titre-bloc ambre">2 · Où, sur le territoire</div>',
                    unsafe_allow_html=True)
        # ---------------------------------------------------------- carte
        afficher = st.radio(
            "Colorier la carte selon",
            ["score", "pourcentage"] if indic is not None else ["score"],
            format_func=lambda k: {"score": "Le score de résilience (0-10)",
                                   "pourcentage": "La valeur brute (%)"}[k],
            horizontal=True, key=f"aff_{choix}_{pop}")

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
                    morceaux.append(f'{pourcents[s]:.1f} % des ménages'.replace('.', ','))
                if scores.get(s) is not None:
                    morceaux.append(f'score {scores[s]:.0f} / 10')
                if morceaux:
                    bulles[s] = ' · '.join(morceaux)

        svg, T, rendu = map_render.render_map_svg(
            valeurs, effectifs, seuils, height=hauteur,
            polarity=polarite, unite=unite, ramp=rampe, infos=bulles)

        if rampe is map_render.RAMP_APRI:
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
                for c, lab in map_render.legend_items(T, polarite, unite))

        components.html(
            f"""<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
                            background:#fcfcfb">
              <div style="margin:0 0 8px"><span style="font-size:11.5px;color:#898781;
                letter-spacing:.05em;margin-right:14px">{"SCORE APRI" if rampe else "SEUILS"}</span>{legende}</div>
              {svg}
            </div>""",
            height=hauteur + 46, scrolling=False)

        if afficher == "score":
            st.caption("Échelle de couleurs APRI : une couleur par point de score, du rouge "
                       "(0, résilience la plus faible) au vert foncé (10). L'échelle est fixe, "
                       "ce qui rend toutes les cartes comparables entre elles.")
        else:
            st.caption(map_render.polarity_caption(polarite))

    with st.container(border=True):
        st.markdown('<div class="titre-bloc vert">3 · Le classement des sections</div>',
                    unsafe_allow_html=True)
        # ---------------------------------------------------------- classement
        ordre = sorted((s for s in sections if valeurs.get(s) is not None),
                       key=lambda s: valeurs[s])
        RAMP = rampe or map_render.ramp_for(polarite)
        couleurs = {s: RAMP[map_render.bin_of(valeurs[s], T)][0] for s in ordre}
        # Sur un indicateur précis, chaque barre porte les deux chiffres : le score
        # et, en gris, la mesure brute qui l'a produit.
        annot = {}
        if indic is not None:
            for s in ordre:
                if afficher == "score" and pourcents.get(s) is not None:
                    annot[s] = f'({pourcents[s]:.1f} % des ménages)'.replace('.', ',')
                elif afficher != "score" and scores.get(s) is not None:
                    annot[s] = f'(score {scores[s]:.0f} / 10)'
        bars = map_render.render_score_bars_svg(
            [(s, valeurs[s]) for s in ordre], vmax=vmax, unite=unite, colors=couleurs,
            annotations=annot)
        components.html(
            f'<div style="background:#fcfcfb;font-family:system-ui,-apple-system,'
            f"'Segoe UI',sans-serif\">{bars}</div>",
            height=len(ordre) * 28 + 26, scrolling=False)

        if afficher == "score":
            st.caption("Rappel : 4,0 sur 10 = 40 % de l'échelle APRI. "
                       "Le tableau ci-dessous donne les deux lectures.")

    # ---------------------------------------------------------- radars
    with st.container(border=True):
        st.markdown('<div class="titre-bloc">4 · Le profil en radar</div>',
                    unsafe_allow_html=True)
        _section_radars(res, vent, scorables, poids, sections, pop, dims_scorees)

    with st.container(border=True):
        st.markdown('<div class="titre-bloc">5 · Comparer les sous-populations</div>',
                    unsafe_allow_html=True)
        # ---------------------------------------------------------- comparaison
        st.caption("Même sélection, recalculée pour chaque sous-population. "
                   "Les cellules sur moins de 30 répondants sont signalées par « · ».")
        lignes_tab = []
        for sec in sections:
            bloc = vent["sections"][sec]
            rec = {"Section communale": sec, "Paysage": vent["paysage"][sec]}
            for p in SOUS_POP:
                v = _score_pondere(lignes, bloc, sec, p, poids)
                n = vent["effectifs"][sec][p]
                if v is None:
                    rec[p] = None
                    continue
                texte = f"{v:.2f} / 10".replace(".", ",")
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
            "Télécharger ce tableau (CSV)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"resilience_{titre[:30].replace(' ', '_')}.csv",
            mime="text/csv")

    # ---------------------------------------------------------- réserves
    with st.expander("Ce que ces scores couvrent — et ce qu'ils ne couvrent pas"):
        non_calc = [r for r in res if r["calculable"] == "non"]
        st.markdown(
            f"""
- **{len(scorables)} indicateurs** sur les 118 du cadre théorique reçoivent un score ici.
- **{len(non_calc)} ne sont pas calculables** depuis un questionnaire ménage : 37 des 38
  indicateurs environnementaux (NDVI, mangroves, connectivité des habitats) relèvent de
  l'imagerie satellitaire, les densités de personnel de santé et les couvertures
  vaccinales des registres sanitaires.
- **9 indicateurs de la dimension culturelle** ont une valeur mais pas de score : leur
  barème porte sur un indice composite de 0 à 8 points, pas sur un pourcentage.
- Conséquence : le score final ne pèse **pas les sept dimensions à parts égales**.
  Il est solide sur les infrastructures, la gouvernance, l'économie, le social et
  l'humain ; muet sur l'environnement et le culturel.
- **Trois barèmes sont inversés dans le cadre théorique** (FIES, population victime de
  violences, pratiques de pêche destructrices) : ils attribuent le score 10 à la pire
  valeur. Ils ont été retournés ici pour rester cohérents avec les seize autres
  indicateurs négatifs.
- Sur le **FIES**, le score vaut 0 partout : l'insécurité alimentaire sévère va de 54 %
  à 73 % selon les sections, alors que la classe la plus dégradée du barème s'arrête à
  29,2 %. L'échelle a été calibrée sur une réalité moins sévère que celle de la zone.
""")
        if indic is not None:
            st.markdown(f"**Réserve propre à cet indicateur :** {indic['note']}")

    st.caption("Source : enquête ménage sept. 2024 (1211 répondants), barèmes du cadre "
               "théorique IRLA / APRI. Échelle de couleurs : « International "
               "comparative empirical scenarios », référentiel APRI.")
    st.caption("Travail réalisé par le Programme des Nations Unies pour "
               "l'environnement (PNUE / UNEP).")
