"""Explorateur de réponses — une question, une réponse, et qui répond quoi.

POURQUOI UN SECOND OUTIL À CÔTÉ DU CROISEMENT.
Le croisement libre construit un GROUPE : on empile des conditions — femme,
catégorie C, sans latrine — et on regarde le profil de résilience de ce
groupe. C'est puissant et c'est lent : il faut savoir quel groupe on cherche
avant de commencer.

L'explorateur pose la question inverse, et c'est la plus fréquente : « sur
CETTE question, qui répond CETTE réponse ? ». On choisit la question, la
réponse, l'axe de ventilation — les dix sections communales ou l'un des
quatre groupes d'intérêt — et la part se lit d'un coup, en barres ou en
radar, avec l'option de ne garder que les extrêmes.

LA PART EST CALCULÉE SUR LES RÉPONDANTS À LA QUESTION, PAS SUR L'ÉCHANTILLON.
Une question posée à six cents ménages sur mille deux cents donnerait des
parts deux fois trop basses si le dénominateur était l'échantillon entier :
on confondrait « peu de gens répondent ça » avec « peu de gens ont été
interrogés là-dessus ». Le dénominateur est donc, section par section, le
nombre de ménages de la section AYANT répondu à la question ; l'effectif est
affiché à côté de la part pour que le lecteur voie sur quoi elle porte.

LES EFFECTIFS TROP FAIBLES SONT SIGNALÉS, PAS CACHÉS. Une part calculée sur
huit répondants n'est pas fausse, elle est fragile : elle bouge de douze
points si un seul ménage change d'avis. Elle est donc affichée en pâle, avec
son effectif, plutôt que retirée — retirer une barre laisse croire qu'il n'y
a rien à cet endroit.
"""

import numpy as np
import streamlit as st

import croisement_moteur as M
import i18n
import map_render
import radar
from i18n import T

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT_APRI = "#2a6b3f"
VERT, ROUGE, GRIS = "#1a8a4f", "#c33a24", "#8a93a5"

# LE SEUIL DE FRAGILITÉ EST CELUI DU MOTEUR. Deux seuils différents dans deux
# écrans du même site donneraient deux verdicts sur le même effectif.
N_FRAGILE = 20

# Les axes de ventilation. « section » est la localité ; les quatre autres
# sont les groupes d'intérêt, dans l'ordre où ils éclairent le plus souvent
# une différence.
# LA DIMENSION N'EST PLUS UN AXE, ELLE EST UNE MESURE. Tant que le score
# affiché était l'indice global, ventiler par dimension était la seule façon
# de voir les sept ; maintenant que la dimension — et même l'indicateur — se
# choisit comme on choisissait une question, la garder en axe donnerait deux
# chemins vers le même chiffre.
AXES = [("section", "ex_ax_section"),
        ("sexe", "ex_ax_sexe"),
        ("age", "ex_ax_age"),
        ("richesse", "ex_ax_richesse"),
        ("paysage", "ex_ax_paysage")]
_VALEURS = dict(M.REGISTRES)
# LES DIMENSIONS SONT DES CIBLES, PAS DES AXES : on les choisit comme on
# choisit une question, et le score obtenu se ventile ensuite sur les mêmes
# axes que tout le reste.
_DIMS = [c for c, _l in M.DIMENSIONS]

TEXTES = {
    "ex_titre": {"en": "Answer explorer", "fr": "Explorateur de réponses"},
    "ex_intro": {
        "en": "Pick a question, then an answer: the share of households "
              "giving that answer is broken down by communal section or by "
              "interest group. Shares are computed on the households who "
              "answered the question, never on the whole sample.",
        "fr": "Choisissez une question, puis une réponse : la part de ménages "
              "qui la donnent est ventilée par section communale ou par "
              "groupe d'intérêt. Les parts portent sur les ménages ayant "
              "répondu à la question, jamais sur l'échantillon entier."},
    "ex_question": {"en": "Question", "fr": "Question"},
    "ex_reponse": {"en": "Answer", "fr": "Réponse"},
    "ex_axe": {"en": "Break down by", "fr": "Ventiler par"},
    "ex_ax_section": {"en": "Communal section", "fr": "Section communale"},
    "ex_ax_sexe": {"en": "Sex", "fr": "Sexe"},
    "ex_ax_age": {"en": "Age group", "fr": "Tranche d'âge"},
    "ex_ax_richesse": {"en": "Economic category", "fr": "Catégorie économique"},
    "ex_ax_paysage": {"en": "Landscape", "fr": "Paysage"},
    "ex_mesure": {"en": "Measure", "fr": "Mesure"},
    "ex_m_part": {"en": "Share of an answer", "fr": "Part d'une réponse"},
    "ex_m_score": {"en": "Resilience score", "fr": "Score de résilience"},
    "ex_score": {"en": "score out of 10", "fr": "score sur 10"},
    "ex_cible": {"en": "Resilience indicator",
                 "fr": "Indicateur de résilience"},
    "ex_c_global": {"en": "Overall resilience index",
                    "fr": "Indice de résilience global"},
    "ex_c_dims": {"en": "Dimensions", "fr": "Dimensions"},
    "ex_t_score": {"en": "Resilience score explorer",
                   "fr": "Explorateur des scores de résilience"},
    "ex_intro_score": {
        "en": "Pick the overall index, a dimension or a single indicator: its "
              "0–10 score is computed for every communal section, landscape "
              "and social group, on the households of each.",
        "fr": "Choisissez l'indice global, une dimension ou un indicateur : "
              "son score sur 10 est calculé pour chaque section communale, "
              "chaque paysage et chaque groupe social, sur les ménages de "
              "chacun."},
    "ex_tableau": {"en": "Table", "fr": "Tableau"},
    "ex_carte": {"en": "Map", "fr": "Carte"},
    "ex_carte_sec": {
        "en": "The map is drawn by communal section: it is available when "
              "the breakdown includes the communal sections.",
        "fr": "La carte se dessine par section communale : elle est "
              "disponible quand la ventilation contient les sections "
              "communales."},
    "ex_filtre": {"en": "Restrict to", "fr": "Restreindre à"},
    "ex_f_section": {"en": "Communal section", "fr": "Section communale"},
    "ex_f_paysage": {"en": "Landscape", "fr": "Paysage"},
    "ex_f_tous": {"en": "All", "fr": "Tout"},
    "ex_filtre_n": {"en": "Restricted to {n} households of {t}.",
                    "fr": "Restreint à {n} ménages sur {t}."},
    "ex_filtre_vide": {
        "en": "No household matches all the restrictions at once.",
        "fr": "Aucun ménage ne réunit toutes les restrictions à la fois."},
    "ex_format": {"en": "Chart", "fr": "Graphique"},
    "ex_barres": {"en": "Bar chart", "fr": "Histogramme"},
    "ex_radar": {"en": "Radar chart", "fr": "Diagramme radar"},
    "ex_extremes": {"en": "Show", "fr": "Afficher"},
    "ex_tous": {"en": "All", "fr": "Tout"},
    "ex_top": {"en": "Highest three", "fr": "Les trois plus hauts"},
    "ex_flop": {"en": "Lowest three", "fr": "Les trois plus bas"},
    "ex_topflop": {"en": "Highest and lowest three",
                   "fr": "Les trois plus hauts et les trois plus bas"},
    "ex_ecart": {"en": "Biggest gap with the whole sample",
                 "fr": "Plus fort écart avec l'ensemble"},
    "ex_part": {"en": "share of respondents",
                "fr": "part des répondants"},
    "ex_ens": {"en": "All respondents", "fr": "Ensemble des répondants"},
    "ex_n": {"en": "{k} of {n} respondents",
             "fr": "{k} sur {n} répondants"},
    # L'INTITULÉ DE COLONNE N'EST PAS LA PHRASE. `ex_n` est un gabarit à deux
    # trous ; posé tel quel en tête de colonne, il s'affichait « {k} of {n}
    # respondents ». Une clé par usage.
    "ex_col_n": {"en": "respondents", "fr": "répondants"},
    "ex_fragile": {
        "en": "Bars in pale green rest on fewer than {n} respondents: they "
              "move by several points if one household answers differently.",
        "fr": "Les barres en vert pâle reposent sur moins de {n} répondants : "
              "elles bougent de plusieurs points si un seul ménage répond "
              "autrement."},
    "ex_vide": {"en": "No household answered this question in the selected "
                      "breakdown.",
                "fr": "Aucun ménage n'a répondu à cette question dans la "
                      "ventilation choisie."},
    "ex_radar_court": {
        "en": "A radar needs at least three points; this breakdown has "
              "fewer. Showing the bar chart.",
        "fr": "Un radar demande au moins trois sommets ; cette ventilation en "
              "compte moins. L'histogramme est affiché."},
    "ex_radar_ech": {
        "en": "The radar is drawn on a 0–10 scale: a share of {p} % sits at "
              "{v} on the web.",
        "fr": "Le radar est tracé sur une échelle de 0 à 10 : une part de "
              "{p} % se lit {v} sur la toile."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .ex-lab { font-size:10.5px; font-weight:700; letter-spacing:.09em;
            text-transform:uppercase; color:#8a93a5; margin:0 0 4px; }
  .ex-tab { width:100%; border-collapse:collapse; margin-top:14px; }
  .ex-tab th { font-size:10.5px; font-weight:700; letter-spacing:.09em;
            text-transform:uppercase; color:#8a93a5; text-align:left;
            padding:0 10px 7px 0; border-bottom:1px solid #e9eef4; }
  .ex-tab th.n, .ex-tab td.n { text-align:right;
            font-variant-numeric:tabular-nums; }
  .ex-tab td { font-size:12.5px; color:#3c4761; padding:7px 10px 7px 0;
            border-bottom:1px solid #f2f5f9; }
  .ex-tab td.v { font-weight:700; color:#101728; }
  .ex-note { font-size:11.5px; color:#8a93a5; line-height:1.5;
            margin:10px 0 0; text-align:left !important; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _f(v, dec=1):
    if v is None:
        return "—"
    s = f"{v:.{dec}f}"
    return s.replace(".", ",") if i18n.get_lang() == "fr" else s


def _lib(v):
    """Le libellé d'une valeur de segmentation, dans la langue courante."""
    cles = {"Homme": "hommes", "Femme": "femmes", "Cat A": "cat_a",
            "Cat B": "cat_b", "Cat C": "cat_c", "<25": "age_25",
            "25-39": "age_25_39", "40-59": "age_40_59", "60+": "age_60",
            "Littoral": "pay_Littoral", "Montagne": "pay_Montagne"}
    return T(cles[v]) if v in cles else v


def _masque_filtres(cat, choix):
    """Le sous-échantillon retenu par les trois filtres, en ET.

    LES TROIS NIVEAUX SE CUMULENT, ET C'EST VOULU. « Littoral » ET « femmes »
    ET « Trichet » restreint trois fois de suite ; l'effectif restant est
    annoncé sous les commandes, parce qu'une part calculée sur onze ménages
    doit se lire en sachant qu'ils sont onze.
    """
    m = np.ones(cat["n"], dtype=bool)
    for v in choix:
        if not v:
            continue
        g = cat["groupes"].get(v)
        if g is not None:
            m &= g
    return m


def _filtres(cat):
    """Une barre déroulante par registre : localité, sexe, âge, richesse,
    paysage.

    UN MENU PAR REGISTRE, PAS UN MENU POUR TROIS. Les trois registres sociaux
    tenaient dans une seule liste aplatie — « Sexe · Femmes », « Âge · 60+ »,
    « Catégorie · Cat C » à la suite — et cette liste ne permettait d'en
    retenir qu'un : demander les femmes de plus de soixante ans était
    impossible alors que le croisement, lui, l'était. Cinq menus séparés
    posent la question comme on la pense, et se cumulent en ET.
    """
    cles = [("section", "ex_f_section", "sec", None),
            ("sexe", "ex_ax_sexe", "sexe", _lib),
            ("age", "ex_ax_age", "age", _lib),
            ("richesse", "ex_ax_richesse", "rich", _lib),
            ("paysage", "ex_f_paysage", "pay", _lib)]
    cols = st.columns(len(cles))
    choix = []
    for (axe, lab, suff, fmt), col in zip(cles, cols):
        with col:
            v = st.selectbox(
                T(lab), [None] + list(_VALEURS.get(axe, [])),
                key=f"ex_f_{suff}",
                format_func=lambda v, f=fmt: (T("ex_f_tous") if v is None
                                              else (f(v) if f else v)))
            choix.append(v)
    return _masque_filtres(cat, choix), any(choix)


def _carte(lignes):
    """La part par section communale, portée sur la carte du territoire.

    LA CARTE NE MONTRE QUE LES SECTIONS. Les autres axes — sexe, âge,
    catégorie — n'ont pas de géographie : les porter sur une carte
    inventerait un territoire qu'ils n'ont pas.
    """
    vals = {l["cle"]: l["part"] for l in lignes
            if l.get("axe_code") == "section" and l["part"] is not None}
    if len(vals) < 2:
        return None
    dispo = list(vals.values())
    seuils = map_render.nice_thresholds(dispo)
    svg, seuils_ret, _m = map_render.render_map_svg(
        vals, {s: 1 for s in vals}, seuils, height=560,
        polarity="neutre", unite="%")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px"><span style="width:20px;height:11px;'
        f'border-radius:3px;background:{c}"></span>'
        f'<span style="font-size:11.5px;color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "neutre", "%"))
    return (f'<div style="margin:6px 0 8px">{legende}</div>{svg}')


def _cases(cat, axe):
    """Les cases d'un axe : (clé technique, libellé affiché)."""
    return [(v, _lib(v)) for v in _VALEURS.get(axe, [])]


def _nom_ind(ind):
    return ((ind.get("nom_fr") or ind.get("nom")) if i18n.get_lang() == "fr"
            else (ind.get("nom") or ind.get("nom_fr")))


def _inds_tries(cat):
    """Les indicateurs calculables, rangés par dimension puis par nom."""
    return sorted(cat.get("indicateurs") or [],
                  key=lambda x: (x["dim"], _nom_ind(x)))


def _mesure_ind(ind, masque):
    """Le score d'UN indicateur sur UN masque, sans calculer les autres.

    `profil` calcule les soixante-six indicateurs d'un coup ; pour une
    ventilation en dix sections, en demander un seul par ce chemin ferait six
    cent soixante calculs pour n'en afficher que dix.
    """
    base = ind["base"] & masque
    nb = int(base.sum())
    if nb == 0:
        return 0, None
    val = 100.0 * float((ind["cible"] & masque).sum()) / nb
    return nb, M._score_de(val, ind["bornes"], ind["decroissant"])


def _cibles(cat):
    """Ce qu'on peut mesurer : l'indice, les dimensions, les indicateurs.

    LA CIBLE REMPLACE LA QUESTION, ELLE NE S'AJOUTE PAS À ELLE. Sur les
    résultats bruts on choisit une question puis une réponse ; sur les scores
    il n'y a rien à choisir dans les réponses — le score est déjà l'agrégat de
    toutes. Ce qui reste à choisir, c'est le NIVEAU : l'indice global, l'une
    des dimensions, ou l'un des indicateurs qui les composent.

    Les codes sont stables (`global`, `d:dim3`, `i:12`) parce qu'ils sont
    retenus en session : un index de liste changerait de cible dès que la
    langue change l'ordre alphabétique des indicateurs.
    """
    inds = _inds_tries(cat)
    opts = [("global", T("ex_c_global"), None)]
    for c in _DIMS:
        opts.append((f"d:{c}", f'{T("ex_c_dims")} · {T(c)}', None))
    for k, ind in enumerate(inds):
        opts.append((f"i:{k}", f'{T(ind["dim"])} · {_nom_ind(ind)}', ind))
    return opts


def _ventiler(cat, mesure, q, modalite, axes, filtre=None, cible=None):
    """Une ligne par case, pour tous les axes retenus, dans leur ordre.

    LES AXES S'ADDITIONNENT, ILS NE SE CROISENT PAS. Cumuler « localité » et
    « sexe » donne douze lignes — dix sections puis deux sexes — et non vingt
    croisements. Le croisement de deux axes divise l'effectif par vingt et
    produit des cases de trois ménages ; l'outil qui sert à cela est le
    constructeur libre, juste en dessous, qui affiche l'effectif de chaque
    condition posée.

    LE DÉNOMINATEUR EST LE NOMBRE DE RÉPONDANTS À LA QUESTION dans la case,
    et il est renvoyé avec la part : sans lui, 100 % sur trois ménages et
    100 % sur cent quarante se liraient pareil.
    """
    if filtre is None:
        filtre = np.ones(cat["n"], dtype=bool)
    if mesure == "score":
        return _ventiler_score(cat, axes, filtre, cible)

    m_rep = np.zeros(cat["n"], dtype=bool)          # a répondu à la question
    for j in range(len(q["modalites"])):
        m_rep |= cat["bits"][q["debut"] + j]
    m_rep &= filtre
    m_mod = cat["bits"][q["debut"] + q["modalites"].index(modalite)] & filtre

    out = []
    for axe in axes:
        for v, lib in _cases(cat, axe):
            g = cat["groupes"].get(v)
            if g is None:
                continue
            base = int((m_rep & g).sum())
            out.append({"nom": lib, "cle": v, "axe": T(dict(AXES)[axe]),
                        "axe_code": axe,
                        "n": base, "k": int((m_mod & g).sum()),
                        "part": (100 * int((m_mod & g).sum()) / base)
                                if base else None})
    ens_base = int(m_rep.sum())
    ens = {"n": ens_base, "k": int(m_mod.sum()),
           "part": (100 * int(m_mod.sum()) / ens_base) if ens_base else None}
    return out, ens


def _score_cible(cat, masque, cible, ind):
    """Le score de la cible choisie sur un sous-échantillon : (n, score).

    LES TROIS NIVEAUX SE CALCULENT SUR LES MÊMES MÉNAGES, jamais sur trois
    échantillons différents : l'indice global, la dimension et l'indicateur
    d'une même section portent sur la section, et se lisent donc l'un à côté
    de l'autre sur la même échelle de 0 à 10.

    L'EFFECTIF D'UN INDICATEUR EST SA BASE, pas la case entière. Un indicateur
    qui ne concerne que les ménages cultivateurs n'est pas calculé sur les
    autres ; annoncer l'effectif de la case laisserait croire que le score
    porte sur tout le monde.
    """
    nb = int(masque.sum())
    if not nb:
        return 0, None
    if ind is not None:
        return _mesure_ind(ind, masque)
    ag = M.agreger(M.profil(cat, masque))
    if cible == "global":
        return nb, ag["global"]
    return nb, ag["dimensions"].get(cible.split(":", 1)[1])


def _ventiler_score(cat, axes, filtre=None, cible=None):
    """Le score de la cible choisie, case par case, pour tous les axes.

    LA CIBLE EST CE QU'ON MESURE, L'AXE EST LÀ OÙ ON LE MESURE. Tant que le
    chiffre affiché était forcément l'indice global, la dimension devait être
    un axe pour qu'on puisse en voir sept ; maintenant qu'elle se choisit
    comme cible, elle sortirait deux fois du même écran.
    """
    tout = filtre if filtre is not None else np.ones(cat["n"], dtype=bool)
    cible = cible or "global"
    ind = None
    if cible.startswith("i:"):
        inds = _inds_tries(cat)
        k = int(cible.split(":", 1)[1])
        ind = inds[k] if k < len(inds) else None
        if ind is None:
            cible = "global"

    out = []
    for axe in axes:
        for v, lib in _cases(cat, axe):
            g = cat["groupes"].get(v)
            if g is None:
                continue
            nb, sc = _score_cible(cat, g & tout, cible, ind)
            out.append({"nom": lib, "cle": v, "axe": T(dict(AXES)[axe]),
                        "axe_code": axe, "n": nb,
                        "k": None, "part": sc, "score": sc})
    nb_t, sc_t = _score_cible(cat, tout, cible, ind)
    ens = {"n": nb_t, "k": None, "part": sc_t, "score": sc_t}
    return out, ens


def _filtrer(lignes, choix, ens=None):
    """Ne garder que les extrêmes, si on les a demandés.

    L'ORDRE D'ORIGINE EST CONSERVÉ. Trier les barres par valeur donnerait un
    classement ; ce n'en est pas un — les sections ont un ordre géographique
    et les tranches d'âge un ordre naturel, qu'un tri par part détruirait.

    L'ÉCART SE MESURE CONTRE L'ENSEMBLE DES RÉPONDANTS, et c'est le seul
    terme qui ait un sens ici : « la plus forte différence » sans dire avec
    quoi ne veut rien dire, et le repère déjà tracé en pointillés sur le
    graphique est justement celui-là. Une case à 62 % quand l'ensemble est à
    31 % s'écarte plus qu'une case à 90 % quand l'ensemble est à 88 %, même
    si la seconde est plus haute.
    """
    mesurees = [x for x in lignes if x["part"] is not None]
    if choix == "tous" or len(mesurees) <= 3:
        return lignes
    if choix == "ecart":
        ref = (ens or {}).get("part")
        if ref is None:
            return lignes
        tri = sorted(mesurees, key=lambda x: -abs(x["part"] - ref))
        garder = {id(x) for x in tri[:3]}
        return [x for x in lignes if id(x) in garder]
    tri = sorted(mesurees, key=lambda x: x["part"])
    garder = set()
    if choix in ("top", "topflop"):
        garder |= {id(x) for x in tri[-3:]}
    if choix in ("flop", "topflop"):
        garder |= {id(x) for x in tri[:3]}
    return [x for x in lignes if id(x) in garder]


def _barres(lignes, ens, mesure):
    """L'histogramme, dessiné.

    LA LIGNE DE L'ENSEMBLE EST TRACÉE EN POINTILLÉS. Sans repère, une part de
    38 % ne dit rien ; comparée aux 31 % de l'ensemble des répondants, elle
    dit quelque chose. C'est la seule référence dont la barre a besoin.

    LES BARRES CHANGENT D'ÉCHELLE AVEC LA MESURE, jamais de forme : une part
    court de 0 à 100, un score de 0 à 10. Garder l'échelle des parts pour un
    score écraserait toutes les barres sur le premier dixième.
    """
    if not lignes:
        return ""
    vmax = 100.0 if mesure == "part" else 10.0
    dec = 0 if mesure == "part" else 2
    unite = "&#8201;%" if mesure == "part" else ""
    LARG, H_L, GAP, H_AXE = 1000, 30, 9, 26
    MG_G, MG_H, MG_B = 210, 26, 30
    n_axes = len({l.get("axe") for l in lignes if l.get("axe")})
    H = (MG_H + len(lignes) * (H_L + GAP)
         + max(n_axes - 1, 0) * H_AXE + MG_B)
    utile = LARG - MG_G - 96
    parts, axe_vu, y = [], None, MG_H

    if ens["part"] is not None:
        x = MG_G + utile * ens["part"] / vmax
        parts.append(
            f'<line x1="{x:.1f}" y1="{MG_H - 12}" x2="{x:.1f}" '
            f'y2="{H - MG_B + 6}" stroke="{ENCRE3}" stroke-width="1" '
            f'stroke-dasharray="3 4"/>'
            f'<text x="{x:.1f}" y="{MG_H - 17}" text-anchor="middle" '
            f'font-size="11" fill="{ENCRE3}">'
            f'{_e(T("ex_ens"))} {_f(ens["part"], dec)}{unite}</text>')

    for l in lignes:
        pale = mesure == "part" and l["n"] < N_FRAGILE
        coul = "#a8cbb6" if pale else VERT_APRI
        # LE NOM DE L'AXE EST ÉCRIT AU-DESSUS DE SES RANGS, SUR SA PROPRE
        # LIGNE. Cumulées, dix sections et deux sexes se suivent sans rien qui
        # dise où l'on passe de l'un à l'autre ; posé dans la marge de la
        # première barre, l'intitulé venait buter contre son libellé.
        if l.get("axe") and l["axe"] != axe_vu:
            if axe_vu is not None:
                y += H_AXE
            axe_vu = l["axe"]
            parts.append(
                f'<text x="0" y="{y - 8}" font-size="9.5" font-weight="700" '
                f'letter-spacing="1.2" fill="{GRIS}">'
                f'{_e(l["axe"].upper())}</text>')
        parts.append(
            f'<text x="{MG_G - 12}" y="{y + 15}" text-anchor="end" '
            f'font-size="12.5" fill="{ENCRE}">{_e(l["nom"])}</text>'
            f'<rect x="{MG_G}" y="{y + 3}" width="{utile}" height="16" rx="8" '
            f'fill="#eef3f0"/>')
        if l["part"] is not None:
            w = max(utile * min(l["part"], vmax) / vmax, 2)
            parts.append(
                f'<rect x="{MG_G}" y="{y + 3}" width="{w:.1f}" height="16" '
                f'rx="8" fill="{coul}"/>'
                f'<text x="{MG_G + utile + 12}" y="{y + 15}" font-size="12.5" '
                f'font-weight="700" fill="{ENCRE}">'
                f'{_f(l["part"], dec)}{unite}</text>')
        if mesure == "part":
            parts.append(
                f'<text x="{LARG - 4}" y="{y + 15}" font-size="11" '
                f'fill="{GRIS}" text-anchor="end">{l["k"]}/{l["n"]}</text>')
        y += H_L + GAP

    return (f'<svg viewBox="0 0 {LARG} {H}" width="100%" '
            f'style="max-width:{LARG}px;display:block" role="img" '
            f'font-family="Inter,system-ui,sans-serif">'
            + "".join(parts) + '</svg>')


def _tableau(lignes, ens, mesure):
    dec = 1 if mesure == "part" else 2
    unite = "&#8201;%" if mesure == "part" else " / 10"
    col = T("ex_part") if mesure == "part" else T("ex_score")
    r = ['<table class="ex-tab"><thead><tr>'
         f'<th>{_e(T("ex_axe"))}</th>'
         f'<th class="n">{_e(col)}</th>']
    if mesure == "part":
        r.append(f'<th class="n">{_e(T("ex_col_n"))}</th>')
    else:
        r.append(f'<th class="n">n</th>')
    r.append('</tr></thead><tbody>')
    for l in lignes:
        n = (f'{l["k"]} / {l["n"]}' if mesure == "part" else str(l["n"]))
        r.append(f'<tr><td>{_e(l["nom"])}</td>'
                 f'<td class="n v">{_f(l["part"], dec)}{unite}</td>'
                 f'<td class="n">{n}</td></tr>')
    n = (f'{ens["k"]} / {ens["n"]}' if mesure == "part" else str(ens["n"]))
    r.append(f'<tr><td>{_e(T("ex_ens"))}</td>'
             f'<td class="n v">{_f(ens["part"], dec)}{unite}</td>'
             f'<td class="n">{n}</td></tr>')
    r.append('</tbody></table>')
    return "".join(r)


def _libelle_question(q):
    mod = (q.get("category") or "").split(". ", 1)[-1]
    return f'{mod} · {q["question"]}'


def render(cat, mode=None):
    """L'explorateur, dans l'ordre : mesure, question, ventilation, format.

    `mode` fige la mesure quand la page n'en propose qu'une : « brut » pour
    les résultats d'enquête, « score » pour les scores de résilience. Deux
    onglets qui traitent chacun d'une seule mesure ne doivent pas demander au
    lecteur de la choisir avant de commencer.

    L'ORDRE DES COMMANDES EST L'ORDRE DE LA PENSÉE. On ne choisit pas un
    format de graphique avant de savoir ce qu'on regarde : ce qu'on mesure
    vient d'abord, la ventilation ensuite, le dessin en dernier.
    """
    if not cat or not cat.get("questions"):
        return
    st.markdown(STYLE, unsafe_allow_html=True)

    questions = cat["questions"]
    if mode == "brut":
        mesure = "part"
    elif mode == "score":
        mesure = "score"
    else:
        mesure = None

    st.markdown(
        f'<div class="titre-bloc">'
        f'{_e(T("ex_t_score") if mesure == "score" else T("ex_titre"))}</div>'
        f'<p class="ex-note" style="margin:0 0 12px;max-width:96ch">'
        f'{_e(T("ex_intro_score") if mesure == "score" else T("ex_intro"))}'
        f'</p>', unsafe_allow_html=True)

    if mesure is None:
        mesure = st.radio(
            T("ex_mesure"), ["part", "score"], horizontal=True, key="ex_mes",
            format_func=lambda m: T("ex_m_" + m))

    q, modalite, cible = None, None, None
    if mesure == "score":
        # ---- 1 · la cible : l'indice, une dimension ou un indicateur -----
        opts = _cibles(cat)
        libs = {c: lib for c, lib, _i in opts}
        cible = st.selectbox(T("ex_cible"), [c for c, _l, _i in opts],
                             key="ex_cible_sel",
                             format_func=lambda c: libs.get(c, c))
    if mesure == "part":
        # ---- 1 · la question, puis la réponse ----------------------------
        g, d = st.columns([1.55, 1])
        with g:
            qi = st.selectbox(
                T("ex_question"), [x["i"] for x in questions], key="ex_q",
                format_func=lambda i: _libelle_question(
                    next(x for x in questions if x["i"] == i)))
        q = next(x for x in questions if x["i"] == qi)
        with d:
            # LA CLÉ DE LA RÉPONSE DÉPEND DE LA QUESTION : sans cela, changer
            # de question garderait l'index de l'ancienne réponse et
            # afficherait une modalité qui n'a rien à voir.
            modalite = st.selectbox(T("ex_reponse"), q["modalites"],
                                    key=f"ex_m_{qi}")

    # ---- 2 · la ventilation, le format, les extrêmes ---------------------
    # UNE SEULE VENTILATION À LA FOIS, ET C'EST UN CHOIX, PAS UNE LIMITE. Le
    # menu à cocher permettait d'empiler les cinq registres : l'écran
    # affichait alors les dix sections, les deux sexes, les quatre tranches
    # d'âge, les trois catégories et les deux paysages — vingt-et-une barres
    # d'un coup, dont dix-neuf que personne n'avait demandées. On regarde un
    # registre, on en change d'un geste, et les autres servent à restreindre.
    dispo = [a for a, _ in AXES]
    c1, c2, c3 = st.columns([1.6, 1, 1.15])
    with c1:
        axe = st.selectbox(
            T("ex_axe"), dispo, key=f"ex_axe_{mesure}",
            format_func=lambda a: T(dict(AXES)[a]))
    axes = [axe]
    with c2:
        formes = ["barres", "radar", "tableau", "carte"]
        forme = st.selectbox(T("ex_format"), formes, key="ex_forme",
                             format_func=lambda f: T("ex_" + f))
    with c3:
        extremes = st.selectbox(
            T("ex_extremes"), ["tous", "top", "flop", "topflop", "ecart"],
            key="ex_ext",
            format_func=lambda c: T({"tous": "ex_tous", "top": "ex_top",
                                     "flop": "ex_flop",
                                     "topflop": "ex_topflop",
                                     "ecart": "ex_ecart"}[c]))

    # ---- les trois niveaux de restriction --------------------------------
    st.markdown(f'<div class="ex-lab" style="margin:10px 0 2px">'
                f'{_e(T("ex_filtre"))}</div>', unsafe_allow_html=True)
    filtre, actif = _filtres(cat)
    n_f = int(filtre.sum())
    if n_f == 0:
        st.info(T("ex_filtre_vide"))
        return
    if actif:
        st.markdown(
            f'<p class="ex-note" style="margin:2px 0 0">'
            f'{_e(T("ex_filtre_n", n=n_f, t=cat["n"]))}</p>',
            unsafe_allow_html=True)

    lignes, ens = _ventiler(cat, mesure, q, modalite, axes, filtre, cible)
    lignes = [l for l in lignes if l["n"] > 0]
    if not lignes:
        st.info(T("ex_vide"))
        return
    montrees = _filtrer(lignes, extremes, ens)

    # ---- 3 · le dessin ---------------------------------------------------
    # LE TABLEAU EST UN MODE, PAS UNE ANNEXE. Il était accroché sous chaque
    # dessin : on lisait la même colonne de chiffres deux fois, une fois au
    # bout des barres et une fois dessous, et l'écran doublait de hauteur pour
    # rien. Qui veut les chiffres choisit « Tableau ».
    if forme == "radar" and len(montrees) < 3:
        st.info(T("ex_radar_court"))
        forme = "barres"

    if forme == "carte":
        svg = _carte(montrees)
        if svg is None:
            st.info(T("ex_carte_sec"))
            forme = "barres"
        else:
            st.markdown(
                f'<div style="font-family:Inter,system-ui,sans-serif">{svg}'
                f'</div>', unsafe_allow_html=True)

    if forme == "radar":
        # LE RADAR EST GRADUÉ DE 0 À 10, comme tous les radars du site : le
        # même dessin ne peut pas porter deux échelles selon la page. Une
        # part y est donc divisée par dix, et la règle de lecture est écrite
        # sous le dessin plutôt que laissée à deviner.
        vals = [((l["part"] / 10 if mesure == "part" else l["part"])
                 if l["part"] is not None else None) for l in montrees]
        nom = (_e(modalite) if mesure == "part"
               else {c: l for c, l, _i in _cibles(cat)}.get(
                   cible or "global", T("ex_m_score")))
        svg = radar.render_radar_svg(
            [l["nom"] for l in montrees], [(nom, vals, VERT_APRI)],
            taille=430)
        st.markdown(f'<div style="max-width:760px;margin:6px auto 0">{svg}'
                    f'</div>', unsafe_allow_html=True)
        if mesure == "part":
            st.markdown(
                '<p class="ex-note">'
                + _e(T("ex_radar_ech", p=_f(ens["part"], 0),
                       v=_f((ens["part"] or 0) / 10, 1))) + '</p>',
                unsafe_allow_html=True)
    elif forme == "tableau":
        st.markdown(_tableau(montrees, ens, mesure), unsafe_allow_html=True)
    else:
        st.markdown(_barres(montrees, ens, mesure), unsafe_allow_html=True)

    if mesure == "part" and any(l["n"] < N_FRAGILE for l in montrees):
        st.markdown(
            f'<p class="ex-note">{_e(T("ex_fragile", n=N_FRAGILE))}</p>',
            unsafe_allow_html=True)
