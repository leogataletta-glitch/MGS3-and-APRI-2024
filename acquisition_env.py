"""Ce qu'il reste à mesurer : l'état d'acquisition des trente-huit
indicateurs environnementaux, et ce qu'il faudrait pour remplir chacun.

POURQUOI CET ÉCRAN EXISTE.
Le cadre décrit un protocole complet ; la plateforme n'en calcule qu'une
partie. Tant que l'écart n'est écrit nulle part, il se raconte de mémoire et
il se raconte mal : on croit manquer la biodiversité et on manque aussi la
connectivité, on croit tenir les mangroves alors qu'on tient des hectares sans
barème. Cette page pose l'écart noir sur blanc, indicateur par indicateur, et
dit pour chacun où aller chercher la donnée manquante.

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
    "aq_desc": {"en": "The state of the 38 environmental indicators, and how "
                      "to fill the gaps",
                "fr": "L'état des 38 indicateurs environnementaux, et comment "
                      "combler les manques"},
    "aq_intro": {
        "en": "The environmental framework describes a full protocol; the "
              "platform computes part of it. This screen states the gap "
              "indicator by indicator, and says for each one where the "
              "missing data can be found, with which tool and for how much "
              "work. The state of each indicator is read from the results "
              "file at every display: it is never entered by hand, so it "
              "cannot drift from what the platform actually holds.",
        "fr": "Le cadre environnemental décrit un protocole complet ; la "
              "plateforme en calcule une partie. Cet écran pose l'écart "
              "indicateur par indicateur, et dit pour chacun où trouver la "
              "donnée manquante, avec quel outil et pour quel travail. "
              "L'état de chaque indicateur est lu dans le fichier de "
              "résultats à chaque affichage : il n'est jamais saisi à la "
              "main, il ne peut donc pas s'écarter de ce que la plateforme "
              "détient réellement."},
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
    "aq_l_donnee": {"en": "Where to find it", "fr": "Où la chercher"},
    "aq_l_outil": {"en": "With what", "fr": "Avec quoi"},
    "aq_l_effort": {"en": "What it costs", "fr": "Ce que ça coûte"},
    "aq_l_faire": {"en": "What to do", "fr": "Ce qu'il faut faire"},
    "aq_l_source": {"en": "Source planned by the framework",
                    "fr": "Source prévue par le cadre"},
    "aq_rien": {
        "en": "No environmental indicator was found in the results file.",
        "fr": "Aucun indicateur environnemental n'a été trouvé dans le "
              "fichier de résultats."},
    "aq_ordre": {
        "en": "Blocks are ordered by what they unblock, not by how many "
              "indicators they hold: the field records are first because no "
              "imagery will ever replace them and because the answer is a "
              "decision, not a computation.",
        "fr": "Les chantiers sont rangés par ce qu'ils débloquent, non par le "
              "nombre d'indicateurs qu'ils portent : les relevés de terrain "
              "viennent d'abord parce qu'aucune image ne les remplacera et "
              "parce que la réponse est une décision, pas un calcul."},
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
    """Les trente-huit indicateurs environnementaux et leur état réel.

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
        if not str(r.get("dimension", "")).startswith("III"):
            continue
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
            "nom_fr": r.get("indicateur_fr") or r.get("indicateur") or "",
            "nom_en": r.get("indicateur") or "",
            "source": (r.get("source") or "").strip(),
            "etat": etat, "n_val": n_val, "n_sco": n_sco,
            "total": total,
        })
    return out


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

    st.markdown(f'<p class="aq-f">{_e(T("aq_intro"))}</p>',
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

    # LES CHANTIERS SONT RANGÉS PAR CE QU'ILS DÉBLOQUENT. Le terrain d'abord
    # parce qu'il est le seul irremplaçable, la fragmentation ensuite parce
    # qu'une seule chaîne y remplit sept indicateurs, et les indices
    # satellitaires en dernier parce qu'ils tournent déjà.
    par_bloc = {}
    for r in lst:
        f = fiches.get(str(r["ligne"])) or {}
        par_bloc.setdefault(f.get("bloc", "satellite"), []).append((r, f))

    st.markdown(f'<p class="aq-x">{_e(T("aq_ordre"))}</p>',
                unsafe_allow_html=True)

    for bloc in BLOCS:
        lot = par_bloc.get(bloc)
        if not lot:
            continue
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
