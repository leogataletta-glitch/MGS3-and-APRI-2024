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

import map_render

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

SEUILS_SCORE = [2.5, 5.0, 7.5]
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
        st.info("Le mode « Explorer les questions » reste utilisable : "
                "rebasculez dessus dans la barre latérale.")
        st.stop()
    scorables = _scorables(res)
    poids = {r["ligne"]: (r["ponderation"] or 0.0) for r in res}
    par_ligne = {r["ligne"]: r for r in res}
    sections = list(vent["sections"].keys())

    st.title("Indicateurs de résilience")
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

    st.subheader(f"{titre} — {SOUS_POP_LABEL[pop]}")
    if indic is not None:
        st.caption(f"Question de l'enquête : {indic['question']}")
        if indic["modalites"]:
            st.caption(f"Réponses comptées : {indic['modalites']}")

    petits = [s for s in sections if effectifs[s] < N_FRAGILE]
    if petits:
        st.warning(
            f"Moins de {N_FRAGILE} répondants dans : {', '.join(petits)}. "
            "Sur ces sections, l'ordre de grandeur est utilisable, le chiffre "
            "exact ne l'est pas.")

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
        seuils = SEUILS_SCORE
        polarite = "eleve_bon"          # un score élevé est toujours favorable
        vmax = 10.0
    else:
        valeurs = pourcents
        unite = "%"
        seuils = map_render.nice_thresholds(
            [v for v in valeurs.values() if v is not None])
        polarite = map_render.guess_polarity(indic["question"],
                                             indic["modalites"] or "")
        vmax = max([v for v in valeurs.values() if v is not None] or [1])

    hauteur = 720
    svg, T, rendu = map_render.render_map_svg(
        valeurs, effectifs, seuils, height=hauteur,
        polarity=polarite, unite=unite)

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
            letter-spacing:.05em;margin-right:14px">SEUILS</span>{legende}</div>
          {svg}
        </div>""",
        height=hauteur + 46, scrolling=False)

    if afficher == "score":
        st.caption("Lecture des couleurs : rouge = score le plus bas (résilience la "
                   "plus faible), vert = score le plus élevé. L'échelle est fixe de "
                   "0 à 10, ce qui rend les cartes comparables entre elles.")
    else:
        st.caption(map_render.polarity_caption(polarite))

    # ---------------------------------------------------------- classement
    st.markdown("### Classement des sections communales")
    ordre = sorted((s for s in sections if valeurs.get(s) is not None),
                   key=lambda s: valeurs[s])
    RAMP = map_render.ramp_for(polarite)
    couleurs = {s: RAMP[map_render.bin_of(valeurs[s], T)][0] for s in ordre}
    bars = map_render.render_score_bars_svg(
        [(s, valeurs[s]) for s in ordre], vmax=vmax, unite=unite, colors=couleurs)
    components.html(
        f'<div style="background:#fcfcfb;font-family:system-ui,-apple-system,'
        f"'Segoe UI',sans-serif\">{bars}</div>",
        height=len(ordre) * 28 + 26, scrolling=False)

    # ---------------------------------------------------------- comparaison
    st.markdown("### Comparaison entre sous-populations")
    st.caption("Même sélection, recalculée pour chaque sous-population. "
               "Les cellules sur moins de 30 répondants sont signalées par « · ».")
    lignes_tab = []
    for sec in sections:
        bloc = vent["sections"][sec]
        rec = {"Section communale": sec, "Paysage": vent["paysage"][sec]}
        for p in SOUS_POP:
            v = _score_pondere(lignes, bloc, sec, p, poids)
            n = vent["effectifs"][sec][p]
            rec[p] = None if v is None else (f"{v:.2f} ·" if n < N_FRAGILE
                                             else f"{v:.2f}")
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
               "théorique des indicateurs de résilience.")
    st.caption("Travail réalisé par le Programme des Nations Unies pour "
               "l'environnement (PNUE / UNEP).")
