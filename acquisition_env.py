"""Ce qu'il reste à mesurer : l'état d'acquisition des 128 indicateurs du
référentiel, et ce qu'il faudrait pour remplir chacun de ceux qui manquent.

POURQUOI CET ÉCRAN EXISTE.
Le cadre décrit un protocole complet ; la plateforme n'en calcule qu'une
partie. Tant que l'écart n'est écrit nulle part, il se raconte de mémoire et
il se raconte mal : on croit manquer la biodiversité et on manque aussi la
connectivité, on croit tenir les mangroves alors qu'on tient des hectares sans
barème, et on ne voit pas que douze indicateurs sont mesurés depuis le début et
n'attendent qu'un barème. Cette page pose l'écart noir sur blanc, dimension par
dimension, et dit pour chacun où aller chercher ce qui manque.

ELLE NE LISTE QUE CE QUI RESTE. Les indicateurs déjà notés sont comptés dans la
barre du haut et nulle part ailleurs : ils se voient partout dans la
plateforme, et les répéter ici noierait ceux qui manquent — la seule question
que cette page pose.

ELLE SE MET À JOUR TOUTE SEULE, ET C'EST TOUT SON INTÉRÊT.
L'état — calculé, partiel, absent — n'est pas saisi : il est LU dans
`resultats.json` à chaque affichage. Le jour où quelqu'un dépose les relevés
de terrain ou fait tourner Conefor, les lignes changent de colonne sans qu'on
touche à une ligne de code. Une liste tenue à la main, elle, aurait divergé du
référentiel en trois semaines, et personne n'aurait su laquelle croire.

CE QUI EST ÉCRIT À LA MAIN, EN REVANCHE, C'EST LA RECETTE.
Où trouver la donnée, avec quel outil, pour quel effort : cela ne se déduit
d'aucun fichier. C'est dans `data/acquisition_env.json`, une fiche par
indicateur, modifiable sans toucher au code — et par quelqu'un qui n'en écrit
pas.
"""

import json
import os

import streamlit as st

import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, AMBRE, ROUGE = "#1a8a4f", "#d1730c", "#c33a24"
DIM_ENV = "III.  ENVIRONMENTAL AND ECOLOGICAL DIMENSION"

# LES DIX SECTIONS ENQUÊTÉES : c'est sur elles que se juge la couverture d'un
# indicateur. Les autres colonnes de `valeurs` sont des sous-populations, qui
# répètent la valeur totale pour une mesure satellitaire et ne disent donc
# rien de plus sur ce qui a été acquis.
SECTIONS = ["Anse à Drick", "Barbois", "Beaulieu", "Blactote", "Dalmette",
            "Débouchette", "Dumont", "Mouline", "Quentin", "Trichet"]

# LES SIX CHANTIERS. Ce ne sont pas les familles du référentiel mais les lots
# de travail réels : ce qui se remplit d'un même geste est rangé ensemble,
# parce que la question qu'on se pose ici est « par quoi je commence », pas
# « à quelle famille appartient cet indice ».
BLOCS = ("terrain", "fragmentation", "sol", "mer", "aires", "satellite")

TEXTES = {
    "aq_onglet": {"en": "What is left to measure",
                  "fr": "Ce qu'il reste à mesurer"},
    "aq_court": {"en": "Left to Measure", "fr": "Reste à mesurer"},
    "aq_desc": {"en": "Every framework indicator not yet in the system, and "
                      "how to fill it",
                "fr": "Tous les indicateurs du référentiel qui ne sont pas "
                      "encore dans le système, et comment les remplir"},
    "aq_intro": {
        "en": "The framework describes {t} indicators across the seven "
              "dimensions; the platform grades part of them. This screen "
              "lists what is left, dimension by dimension, and says for each "
              "one where the missing data can be found, with which tool and "
              "for how much work. The state of each indicator is read from "
              "the results file at every display: it is never entered by "
              "hand, so it cannot drift from what the platform actually "
              "holds.",
        "fr": "Le référentiel décrit {t} indicateurs sur les sept "
              "dimensions ; la plateforme en note une partie. Cet écran "
              "liste ce qui reste, dimension par dimension, et dit pour "
              "chacun où trouver la donnée manquante, avec quel outil et "
              "pour quel travail. L'état de chaque indicateur est lu dans le "
              "fichier de résultats à chaque affichage : il n'est jamais "
              "saisi à la main, il ne peut donc pas s'écarter de ce que la "
              "plateforme détient réellement."},
    "aq_e_calcule": {"en": "Computed", "fr": "Calculé"},
    "aq_e_partiel": {"en": "Partial", "fr": "Partiel"},
    "aq_e_absent": {"en": "Missing", "fr": "Absent"},
    "aq_e_calcule_x": {
        "en": "a score on ten, on all ten communal sections",
        "fr": "une note sur dix, sur les dix sections communales"},
    "aq_e_partiel_x": {
        "en": "values exist but no score, or fewer than ten sections are "
              "covered",
        "fr": "des valeurs existent mais aucune note, ou moins de dix "
              "sections sont couvertes"},
    "aq_e_absent_x": {"en": "no value at all", "fr": "aucune valeur"},
    "aq_sections": {"en": "{n} of 10 sections", "fr": "{n} sections sur 10"},
    "aq_sans_note": {"en": "values without a scale",
                     "fr": "des valeurs sans barème"},
    "aq_b_terrain": {"en": "Field biodiversity",
                     "fr": "Biodiversité de terrain"},
    "aq_b_fragmentation": {"en": "Fragmentation and connectivity",
                           "fr": "Fragmentation et connectivité"},
    "aq_b_sol": {"en": "Soil and degradation", "fr": "Sol et dégradation"},
    "aq_b_mer": {"en": "Sea, coast and water", "fr": "Mer, côte et eau"},
    "aq_b_aires": {"en": "Protected areas", "fr": "Aires protégées"},
    "aq_b_satellite": {"en": "Vegetation and climate",
                       "fr": "Végétation et climat"},
    # LES SEPT DIMENSIONS, NOMMÉES COMME AILLEURS SUR LE SITE.
    "aq_d_I": {"en": "I · Physical and infrastructural",
               "fr": "I · Physique et infrastructurelle"},
    "aq_d_II": {"en": "II · Institutional, technological and governance",
                "fr": "II · Institutionnelle, technologique et gouvernance"},
    "aq_d_III": {"en": "III · Environmental and ecological",
                 "fr": "III · Environnementale et écologique"},
    "aq_d_IV": {"en": "IV · Economic, livelihoods and food security",
                "fr": "IV · Économique, moyens d'existence et sécurité "
                      "alimentaire"},
    "aq_d_V": {"en": "V · Social and community",
               "fr": "V · Sociale et communautaire"},
    "aq_d_VI": {"en": "VI · Human", "fr": "VI · Humaine"},
    "aq_d_VII": {"en": "VII · Cultural, identity-based and psychological",
                 "fr": "VII · Culturelle, identitaire et psychologique"},
    "aq_dim_complete": {
        "en": "Nothing left: every indicator of this dimension is graded on "
              "the ten sections.",
        "fr": "Rien à faire : tous les indicateurs de cette dimension sont "
              "notés sur les dix sections."},
    # LE NOM DU CHANTIER, sous celui de l'indicateur. Il dit de quelle NATURE
    # est le travail qui manque — un barème à écrire n'est pas une campagne de
    # terrain — et c'est ce qui permet de lire la page comme un plan de
    # travail plutôt que comme une liste de manques.
    "aq_b_bareme": {"en": "Scale to be written", "fr": "Barème à écrire"},
    "aq_b_ocb": {"en": "Institutional survey, two sections left",
                 "fr": "Enquête institutionnelle, deux sections à faire"},
    "aq_b_sante": {"en": "National health statistics",
                   "fr": "Statistiques sanitaires nationales"},
    "aq_b_menage_a_ajouter": {"en": "Question to add to the survey",
                              "fr": "Question à ajouter à l'enquête"},
    "aq_b_peche": {"en": "Landing records", "fr": "Relevés de débarquement"},
    "aq_b_registres": {"en": "Administrative registers",
                       "fr": "Registres administratifs"},
    "aq_b_social_a_ajouter": {"en": "Social module to add",
                              "fr": "Module social à ajouter"},
    "aq_b_reseau": {"en": "Road network and population",
                    "fr": "Réseau routier et population"},
    "aq_b_ecoles": {"en": "School facility survey",
                    "fr": "Enquête d'établissement scolaire"},
    "aq_b_decision": {"en": "A decision to make", "fr": "Une décision à prendre"},
    "aq_l_donnee": {"en": "Where to find it", "fr": "Où la chercher"},
    "aq_l_outil": {"en": "With what", "fr": "Avec quoi"},
    "aq_l_effort": {"en": "What it costs", "fr": "Ce que ça coûte"},
    "aq_l_faire": {"en": "What to do", "fr": "Ce qu'il faut faire"},
    "aq_l_source": {"en": "Source planned by the framework",
                    "fr": "Source prévue par le cadre"},
    "aq_rien": {
        "en": "No indicator was found in the results file.",
        "fr": "Aucun indicateur n'a été trouvé dans le fichier de "
              "résultats."},
    "aq_ordre": {
        "en": "Only what is left is listed. Within a dimension, indicators "
              "are grouped by the work that fills them: one written scale "
              "fills twelve of them, one imagery chain filled seven, and it "
              "is that piece of work that gets planned, not the line of the "
              "framework.",
        "fr": "Seul ce qui reste est listé. Dans une dimension, les "
              "indicateurs sont groupés par le travail qui les remplit : un "
              "barème écrit en remplit douze, une chaîne d'imagerie en a "
              "rempli sept, et c'est ce travail-là qu'on planifie, pas la "
              "ligne du référentiel."},
    "aq_maj": {
        "en": "Read from the results file. This page changes on its own as "
              "files arrive.",
        "fr": "Lu dans le fichier de résultats. Cette page change d'elle-même "
              "à mesure que les fichiers arrivent."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

STYLE = """
<style>
  .aq-bar { display:flex; gap:2px; margin:14px 0 6px; height:12px;
        border-radius:7px; overflow:hidden; }
  .aq-bar span { display:block; }
  .aq-cpt { display:flex; gap:26px; flex-wrap:wrap; margin:2px 0 4px; }
  .aq-cpt div { font-size:12px; color:#6b7590; }
  .aq-cpt b { font-size:19px; font-weight:700; margin-right:6px;
        font-variant-numeric:tabular-nums; }
  .aq-h { font-family:Georgia,"Times New Roman",serif; font-size:19px;
        color:#16241c; margin:26px 0 2px; font-weight:400; }
  .aq-hx { font-size:12px; color:#8a93a5; margin:0 0 10px; }
  .aq-l { display:grid; grid-template-columns:1fr 96px 118px;
        gap:10px; align-items:center; padding:9px 2px;
        border-bottom:1px solid #eef1ef; }
  .aq-n { font-size:13.5px; color:#26332c; line-height:1.35; }
  .aq-p { font-size:11px; color:#9aa7a0; margin-top:2px; }
  .aq-et { font-size:10.5px; font-weight:700; letter-spacing:.06em;
        text-transform:uppercase; text-align:right; }
  .aq-cv { font-size:11px; color:#8a93a5; text-align:right;
        font-variant-numeric:tabular-nums; }
  .aq-f { font-size:12.5px; color:#3c4761; line-height:1.6;
        text-align:justify; }
  .aq-fl { font-size:10px; font-weight:700; letter-spacing:.07em;
        text-transform:uppercase; color:#2a6b3f; margin:10px 0 2px; }
  .aq-fv { font-size:12.5px; color:#3c4761; line-height:1.5; }
  .aq-x { font-size:12px; color:#8a93a5; line-height:1.55; margin:8px 0 0;
        text-align:justify; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


@st.cache_data(show_spinner=False)
def _fiches():
    """Les recettes d'acquisition, lues dans `data/`.

    Elles sont du texte écrit pour un territoire et un budget, pas du code :
    elles doivent pouvoir être corrigées par quelqu'un qui n'ouvre jamais un
    fichier Python.
    """
    p = os.path.join(DATA, "acquisition_env.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return (json.load(f) or {}).get("fiches") or {}


@st.cache_data(show_spinner=False)
def _indicateurs():
    """Les indicateurs du référentiel, tous, et leur état réel.

    L'ÉTAT EST DÉDUIT, JAMAIS DÉCLARÉ. Trois cas seulement, et ils se lisent
    dans le fichier de résultats :

      · calculé : une note d'ensemble existe ET les dix sections en portent
        une. C'est la seule situation où l'indicateur entre vraiment dans
        l'indice ;
      · partiel : il y a quelque chose — des valeurs sans barème, ou un
        barème appliqué à cinq sections sur dix. Cette catégorie existe parce
        que la confondre avec « absent » ferait relancer une acquisition déjà
        faite, et la confondre avec « calculé » ferait publier un score qui
        ne couvre pas le territoire ;
      · absent : rien, nulle part.
    """
    p = os.path.join(DATA, "resultats.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    lst = d["indicateurs"] if isinstance(d, dict) and "indicateurs" in d else d
    out = []
    for r in lst or []:
        val = r.get("valeurs") or {}
        sco = r.get("scores") or {}
        n_val = sum(1 for s in SECTIONS if val.get(s) is not None)
        n_sco = sum(1 for s in SECTIONS if sco.get(s) is not None)
        total = sco.get("Total")
        if total is not None and n_sco >= len(SECTIONS):
            etat = "calcule"
        elif n_val or n_sco or total is not None:
            etat = "partiel"
        else:
            etat = "absent"
        out.append({
            "ligne": r.get("ligne"),
            "dim": _dim_code(r.get("dimension")),
            "nom_fr": r.get("indicateur_fr") or r.get("indicateur") or "",
            "nom_en": r.get("indicateur") or "",
            "source": (r.get("source") or "").strip(),
            "etat": etat, "n_val": n_val, "n_sco": n_sco,
            "total": total,
        })
    return out


# LES SEPT DIMENSIONS, DANS L'ORDRE DU RÉFÉRENTIEL. Le chiffre romain est
# écrit en tête de chaque dimension du fichier de résultats ; on le lit
# plutôt que de le déduire d'un libellé traduit.
DIMS = ("I", "II", "III", "IV", "V", "VI", "VII")


def _dim_code(nom):
    t = str(nom or "").strip().upper()
    for c in ("VII", "VI", "IV", "V", "III", "II", "I"):
        if t.startswith(c + "."):
            return c
    return ""


def _couleur(etat):
    return {"calcule": VERT, "partiel": AMBRE}.get(etat, ROUGE)


def _couverture(r):
    """Ce qu'on dit à droite de l'état, en une ligne.

    Un « partiel » sans précision oblige à ouvrir la fiche pour savoir s'il
    manque un barème ou la moitié du territoire : ce sont deux travaux
    différents, l'un d'une journée, l'autre d'une campagne.
    """
    if r["etat"] == "calcule":
        return ""
    if r["etat"] == "absent":
        return ""
    if r["n_val"] and not r["n_sco"]:
        return T("aq_sans_note")
    return T("aq_sections", n=max(r["n_sco"], r["n_val"]))


def _ligne(r, fiche, lang):
    nom = r["nom_fr"] if lang == "fr" else r["nom_en"]
    coul = _couleur(r["etat"])
    st.markdown(
        f'<div class="aq-l"><div>'
        f'<div class="aq-n">{_e(nom)}</div>'
        f'<div class="aq-p">{T("aq_l_source")} · '
        f'{_e(r["source"] or T("aq_b_" + ((fiche or {}).get("bloc") or "satellite")))}'
        f'</div>'
        f'</div>'
        f'<div class="aq-et" style="color:{coul}">'
        f'{_e(T("aq_e_" + r["etat"]))}</div>'
        f'<div class="aq-cv">{_e(_couverture(r))}</div></div>',
        unsafe_allow_html=True)


def _fiche_bloc(fiche, lang):
    """La recette du chantier, écrite une fois pour tout le bloc.

    Elle est commune à ses indicateurs parce que c'est un seul travail : on
    ne va pas chercher WorldCover sept fois pour sept métriques de patchs.
    La répéter sous chaque ligne aurait fait croire à sept chantiers.
    """
    if not fiche:
        return
    sfx = "" if lang == "fr" else "_en"
    lignes = (("aq_l_donnee", "donnee"), ("aq_l_outil", "outil"),
              ("aq_l_effort", "effort"))
    st.markdown(
        '<div style="border-left:3px solid #cfe0d6;padding:2px 0 2px 14px;'
        'margin:12px 0 6px">'
        + "".join(
            f'<div class="aq-fl">{_e(T(cle))}</div>'
            f'<div class="aq-fv">{_e(fiche.get(champ + sfx) or fiche.get(champ, ""))}</div>'
            for cle, champ in lignes)
        + f'<div class="aq-fl">{_e(T("aq_l_faire"))}</div>'
          f'<div class="aq-f">'
          f'{_e(fiche.get("quoi" + sfx) or fiche.get("quoi", ""))}</div>'
        + (f'<div class="aq-fv" style="margin-top:8px">'
           f'<a href="{_e(fiche["url"])}" target="_blank" '
           f'rel="noopener">{_e(fiche["url"])}</a></div>'
           if fiche.get("url") else "")
        + '</div>', unsafe_allow_html=True)


def render():
    lang = i18n.get_lang()
    st.markdown(STYLE, unsafe_allow_html=True)
    lst = _indicateurs()
    if not lst:
        st.info(T("aq_rien"))
        return
    fiches = _fiches()

    st.markdown(f'<p class="aq-f">{_e(T("aq_intro", t=len(lst)))}</p>',
                unsafe_allow_html=True)

    # LE COMPTE D'ABORD, ET EN PROPORTION. Trois nombres et une barre : c'est
    # la seule chose qu'un bailleur retiendra de cette page, et elle doit
    # tenir avant le pli.
    n = {e: sum(1 for r in lst if r["etat"] == e)
         for e in ("calcule", "partiel", "absent")}
    tot = len(lst)
    st.markdown(
        '<div class="aq-bar">'
        + "".join(
            f'<span style="background:{_couleur(e)};'
            f'width:{100.0*n[e]/tot:.1f}%"></span>'
            for e in ("calcule", "partiel", "absent") if n[e])
        + '</div><div class="aq-cpt">'
        + "".join(
            f'<div><b style="color:{_couleur(e)}">{n[e]}</b>'
            f'{_e(T("aq_e_" + e))} · {_e(T("aq_e_" + e + "_x"))}</div>'
            for e in ("calcule", "partiel", "absent"))
        + '</div>', unsafe_allow_html=True)
    st.caption(T("aq_maj"))

    # LA PAGE NE LISTE QUE CE QUI RESTE, dimension par dimension. Les
    # soixante-cinq indicateurs déjà notés sont comptés dans la barre et
    # nulle part ailleurs : ils sont visibles partout dans la plateforme, et
    # les répéter ici noierait les soixante-trois qui manquent — ce qui est
    # précisément la question que cette page pose.
    st.markdown(f'<p class="aq-x">{_e(T("aq_ordre"))}</p>',
                unsafe_allow_html=True)

    for dim in DIMS:
        lot_dim = [r for r in lst if r["dim"] == dim]
        if not lot_dim:
            continue
        reste = [r for r in lot_dim if r["etat"] != "calcule"]
        nb = {e: sum(1 for r in lot_dim if r["etat"] == e)
              for e in ("calcule", "partiel", "absent")}
        detail = " · ".join(
            f'{nb[e]} {T("aq_e_" + e).lower()}'
            for e in ("calcule", "partiel", "absent") if nb[e])
        st.markdown(
            f'<div class="aq-h">{_e(T("aq_d_" + dim))}</div>'
            f'<div class="aq-hx">{len(lot_dim)} · {_e(detail)}</div>',
            unsafe_allow_html=True)
        if not reste:
            st.markdown(f'<p class="aq-x" style="margin:2px 0 14px">'
                        f'{_e(T("aq_dim_complete"))}</p>',
                        unsafe_allow_html=True)
            continue
        # DANS UNE DIMENSION, LES INDICATEURS SONT GROUPÉS PAR RECETTE. Une
        # même démarche remplit souvent plusieurs lignes du référentiel — un
        # barème à écrire en remplit douze, une chaîne de fragmentation en
        # remplissait sept — et c'est la démarche qu'on planifie, pas la
        # ligne.
        vus, groupes = [], []
        for r in reste:
            f = fiches.get(str(r["ligne"])) or {}
            cle = f.get("quoi") or f.get("bloc") or "?"
            if cle in vus:
                groupes[vus.index(cle)][1].append(r)
            else:
                vus.append(cle)
                groupes.append((f, [r]))
        for f, rs in groupes:
            for r in rs:
                _ligne(r, f, lang)
            _fiche_bloc(f, lang)


def render_bloc(bloc):
    """Un seul chantier, hors de sa page.

    APPELÉ PAR L'ÉCRAN DES RÉSULTATS BRUTS. L'onglet « biodiversité » n'a
    aucun résultat à montrer ; plutôt qu'une carte d'attente vide, il montre
    le chantier lui-même — les sept indicateurs, leur état, et la recette qui
    les remplirait. Même code, donc même information des deux côtés.
    """
    lang = i18n.get_lang()
    st.markdown(STYLE, unsafe_allow_html=True)
    lst = _indicateurs()
    if not lst:
        return
    fiches = _fiches()
    lot = []
    for r in lst:
        f = fiches.get(str(r["ligne"])) or {}
        if f.get("bloc", "satellite") == bloc:
            lot.append((r, f))
    _rendre_bloc(bloc, lot, lang)


def _rendre_bloc(bloc, lot, lang):
    """Un chantier : son titre, ses indicateurs, ses recettes.

    IL EST SORTI DE LA BOUCLE POUR POUVOIR ÊTRE APPELÉ SEUL. L'écran des
    résultats bruts montre le chantier « biodiversité de terrain » à la place
    de sa carte d'attente : c'est la même information — sept indicateurs, ce
    qu'ils demandent — et la dupliquer aurait garanti qu'elle diverge.
    """
    if lot:
        nb = {e: sum(1 for r, _f in lot if r["etat"] == e)
              for e in ("calcule", "partiel", "absent")}
        detail = " · ".join(
            f'{nb[e]} {T("aq_e_" + e).lower()}'
            for e in ("calcule", "partiel", "absent") if nb[e])
        st.markdown(
            f'<div class="aq-h">{_e(T("aq_b_" + bloc))}</div>'
            f'<div class="aq-hx">{len(lot)} · {_e(detail)}</div>',
            unsafe_allow_html=True)
        # UN CHANTIER PEUT PORTER DEUX RECETTES, ET IL FAUT ALORS DEUX
        # ENCADRÉS. L'indice de diversité des cultures est rangé avec la
        # biodiversité parce qu'il en mesure une, mais il se calcule depuis
        # les réponses des ménages et ne demande aucun terrain : lui coller la
        # recette des transects ferait attendre une campagne là où deux jours
        # suffisent. Les lignes sont donc groupées par recette.
        vus, groupes = [], []
        for r, f in lot:
            cle = f.get("quoi") or f.get("bloc") or bloc
            if cle in vus:
                groupes[vus.index(cle)][1].append(r)
            else:
                vus.append(cle)
                groupes.append((f, [r]))
        for f, rs in groupes:
            for r in rs:
                _ligne(r, f, lang)
            _fiche_bloc(f, lang)
