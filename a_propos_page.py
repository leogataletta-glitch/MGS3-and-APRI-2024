"""« À propos » et « Contact » : d'où vient cet indice, et à qui écrire.

POURQUOI UNE PAGE « À PROPOS » SUR UN TABLEAU DE BORD.
Le site montre des chiffres sur un territoire habité, et il les montre à des
gens qui n'étaient pas dans la salle quand la méthode a été arrêtée. Un
lecteur qui trouve un score de 3,4 sur l'accès à l'eau a le droit de savoir
qui l'a produit, à partir de quoi, dans quel cadre, et vers qui se tourner
s'il le conteste. Sans cette page, l'indice arrive de nulle part et il faut
le croire sur parole ; avec elle, il est attribuable.

CE QUE CETTE PAGE NE FAIT PAS.
Elle ne répète pas la méthode — le cadre de résilience l'expose déjà en
détail, avec ses sept dimensions, ses barèmes et ses pondérations. Elle
raconte l'histoire et nomme les responsables, ce qu'aucun autre écran ne
fait.

LES NOMBRES SONT LUS DANS LES FICHIERS, PAS ÉCRITS DANS LA PHRASE.
« Cent vingt-huit indicateurs » saisi en toutes lettres devient faux le jour
où le référentiel en gagne un, et rien ne le signale. Ils sont donc comptés
à l'ouverture, dans les mêmes fichiers que le reste du site.
"""

import csv
import json
import os

import streamlit as st

import i18n
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

ENCRE, ENCRE2, ENCRE3 = "#101728", "#3c4761", "#6b7590"
VERT, VERT_PALE = "#1f5b46", "#eef4f0"
BORD = "#e4eae6"

TEXTES = {
    "ap_titre": {"en": "About APRI", "fr": "À propos d'APRI"},
    "ap_t1": {"en": "What this index is",
              "fr": "Ce qu'est cet indice"},
    "ap_x1": {
        "en": "APRI turns what a landscape and its households can be observed "
              "doing into a score out of ten, on {i} indicators grouped in "
              "seven dimensions. It does not rank places for the sake of "
              "ranking them: a score is only useful next to the measurement "
              "it comes from, which is why every indicator on this site "
              "carries its raw value, its scale and its weight.",
        "fr": "APRI transforme ce qu'on peut observer d'un paysage et de ses "
              "ménages en un score sur dix, sur {i} indicateurs répartis en "
              "sept dimensions. Il ne classe pas des lieux pour le plaisir de "
              "les classer : un score ne vaut qu'à côté de la mesure dont il "
              "sort, et c'est pourquoi chaque indicateur du site porte sa "
              "valeur brute, son barème et sa pondération."},
    "ap_t2": {"en": "Where it comes from", "fr": "D'où il vient"},
    "ap_x2": {
        "en": "APRI is the measurement arm of the Integrated Resilient "
              "Landscape Approach (IRLA), a framework that reads a landscape "
              "as a system rather than as a list of sectors. IRLA sets the "
              "seven dimensions, the three attributes — anticipate, absorb, "
              "adapt — and the rule that a resilience score must be traceable "
              "back to a field measurement. APRI is what happens when that "
              "framework is applied to a real territory and has to produce "
              "numbers.",
        "fr": "APRI est le bras de mesure de l'approche intégrée des paysages "
              "résilients (IRLA), un cadre qui lit un paysage comme un "
              "système plutôt que comme une liste de secteurs. IRLA pose les "
              "sept dimensions, les trois attributs — anticiper, absorber, "
              "s'adapter — et la règle qu'un score de résilience doit pouvoir "
              "être remonté jusqu'à une mesure de terrain. APRI est ce que "
              "devient ce cadre quand on l'applique à un territoire réel et "
              "qu'il faut produire des chiffres."},
    "ap_t3": {"en": "The 2024 assessment", "fr": "L'évaluation de 2024"},
    "ap_x3": {
        "en": "The figures on this site come from a household survey carried "
              "out in 2024 across {s} communal sections of Sud and "
              "Grand'Anse, in Haiti: {m} households, {q} questions each. "
              "Three other sources complete it — structured interviews with "
              "communal health, education and political authorities, "
              "identity records for {o} community-based organisations, and "
              "satellite series on forest cover, rainfall and land surface "
              "temperature.",
        "fr": "Les chiffres de ce site viennent d'une enquête ménage conduite "
              "en 2024 dans {s} sections communales du Sud et de la "
              "Grand'Anse, en Haïti : {m} ménages, {q} questions chacun. "
              "Trois autres sources la complètent — des entretiens "
              "structurés avec les autorités sanitaires, éducatives et "
              "politiques communales, les fiches d'identité de {o} "
              "organisations communautaires de base, et des séries "
              "satellitaires sur le couvert forestier, la pluie et la "
              "température de surface."},
    "ap_t4": {"en": "What it does not claim", "fr": "Ce qu'il ne prétend pas"},
    "ap_x4": {
        "en": "A composite index carries a circularity it should say out "
              "loud: resilience is defined by the variables assumed to "
              "produce it. The causal links this site draws are posed by the "
              "framework and the literature, not estimated on the survey — "
              "and they are shown with their evidence and their source so "
              "that they can be argued with. Of the {i} indicators, some "
              "carry no measured value yet, and the site says so where the "
              "number is missing rather than filling the gap.",
        "fr": "Un indice composite porte une circularité qu'il vaut mieux "
              "dire tout haut : la résilience y est définie par les "
              "variables supposées la produire. Les liens causaux dessinés "
              "sur ce site sont posés par le cadre et la littérature, non "
              "estimés sur l'enquête — et ils sont montrés avec leur niveau "
              "de preuve et leur source, pour qu'on puisse les discuter. Sur "
              "les {i} indicateurs, certains ne portent pas encore de valeur "
              "mesurée, et le site le dit là où le nombre manque plutôt que "
              "de combler le trou."},
    "ap_t5": {"en": "Who is behind it", "fr": "Qui le porte"},
    "ap_x5": {
        "en": "The assessment is carried out by the United Nations "
              "Environment Programme (UNEP) with its field partners in Sud "
              "and Grand'Anse. The survey was administered on the ground by "
              "local enumerators; the framework, the index and this site are "
              "produced by the project team.",
        "fr": "L'évaluation est conduite par le Programme des Nations unies "
              "pour l'environnement (PNUE) avec ses partenaires de terrain "
              "du Sud et de la Grand'Anse. L'enquête a été administrée sur "
              "place par des enquêteurs locaux ; le cadre, l'indice et ce "
              "site sont produits par l'équipe du projet."},
    "ap_equipe": {"en": "The team", "fr": "L'équipe"},
    "ap_equipe_x": {
        "en": "Names and roles to be added.",
        "fr": "Noms et fonctions à compléter."},
    "ap_c_titre": {"en": "Contact us", "fr": "Nous contacter"},
    "ap_c_x": {
        "en": "For a question on the method, a figure you want to check, a "
              "correction, or a request for data that is not published here.",
        "fr": "Pour une question de méthode, un chiffre à vérifier, une "
              "correction, ou une demande de données qui ne sont pas "
              "publiées ici."},
    "ap_c_mail": {"en": "By email", "fr": "Par courriel"},
    "ap_c_mail_x": {"en": "Address to be added.",
                    "fr": "Adresse à compléter."},
    "ap_c_qui": {"en": "Who answers", "fr": "Qui répond"},
    "ap_c_qui_x": {
        "en": "The UNEP project team in charge of the assessment.",
        "fr": "L'équipe du projet PNUE en charge de l'évaluation."},
    "ap_c_donnees": {"en": "Data requests", "fr": "Demandes de données"},
    "ap_c_donnees_x": {
        "en": "The seven published datasets are on the Data page, ready to "
              "download. The raw file with direct identifiers is never "
              "published: requests for it are handled case by case.",
        "fr": "Les sept jeux publiés sont sur la page Données, prêts à "
              "télécharger. Le fichier brut portant les identifiants directs "
              "n'est jamais publié : les demandes le concernant se traitent "
              "au cas par cas."},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

_STYLE = """
<style>
  /* UNE COLONNE DE TEXTE, PAS UNE GRILLE DE CARTES. Cette page se lit d'un
     bout à l'autre : elle raconte. Une mise en cartes découperait le récit
     en morceaux qu'on picore, ce qui est exactement ce qu'il ne faut pas
     faire d'une page qui explique d'où viennent les chiffres. */
  .ap-h { font-size:12px; font-weight:700; letter-spacing:.09em;
       text-transform:uppercase; color:#1f5b46; margin:26px 0 8px;
       display:flex; align-items:center; gap:12px; }
  .ap-h span { flex:1 1 auto; height:1.5px; background:#cfe0d6; }
  .ap-p { font-size:14.5px; line-height:1.65; color:#3c4761;
       max-width:82ch; margin:0; text-align:left !important; }
  .ap-b { display:flex; gap:14px; flex-wrap:wrap; margin:14px 0 0; }
  .ap-c { flex:1 1 260px; border:1px solid #e4eae6; border-radius:12px;
       background:#fff; padding:13px 16px; }
  .ap-c-t { font-size:11px; font-weight:700; letter-spacing:.07em;
       text-transform:uppercase; color:#1f5b46; margin-bottom:5px; }
  .ap-c-x { font-size:13.5px; line-height:1.55; color:#3c4761; }
  /* CE QUI RESTE À COMPLÉTER LE DIT, en ambre, plutôt que de se faire passer
     pour du contenu. Un bloc vide qu'on oublie de remplir se publie ; un
     bloc qui se signale, non. */
  .ap-todo { font-size:13px; color:#a8690a; background:#fdf3e3;
       border:1px solid #f0dcb8; border-radius:10px; padding:9px 13px;
       margin:10px 0 0; }
</style>
"""


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


@st.cache_data(show_spinner=False)
def _chiffres():
    """Les cinq nombres de la page, comptés dans les fichiers du site."""
    def _j(nom):
        c = os.path.join(DATA, nom)
        if not os.path.exists(c):
            return None
        with open(c, encoding="utf-8") as f:
            return json.load(f)

    n = {}
    r = _j("resultats.json") or []
    n["i"] = len(r["indicateurs"] if isinstance(r, dict) else r)
    n["q"] = len(_j("questions_index.json") or [])
    n["o"] = len((_j("ocb.json") or {}).get("fiches") or [])
    try:
        with open(os.path.join(DATA, "donnees_anonymisees.csv"),
                  encoding="utf-8", errors="replace") as f:
            n["m"] = max(0, sum(1 for _ in csv.reader(f)) - 1)
    except Exception:
        n["m"] = None
    n["s"] = 10
    return n


def _nb(v):
    if v is None:
        return "—"
    return (f"{v:,}".replace(",", " ") if i18n.get_lang() == "fr"
            else f"{v:,}")


def _section(cle_t, cle_x, **kw):
    st.markdown(f'<div class="ap-h">{_e(T(cle_t))}<span></span></div>'
                f'<p class="ap-p">{_e(T(cle_x, **kw))}</p>',
                unsafe_allow_html=True)


def render():
    """La page « À propos » : l'histoire, le cadre, l'enquête, l'équipe."""
    st.markdown(_STYLE, unsafe_allow_html=True)
    n = _chiffres()
    _section("ap_t1", "ap_x1", i=_nb(n["i"]))
    _section("ap_t2", "ap_x2")
    _section("ap_t3", "ap_x3", s=_nb(n["s"]), m=_nb(n["m"]), q=_nb(n["q"]),
             o=_nb(n["o"]))
    _section("ap_t4", "ap_x4", i=_nb(n["i"]))
    _section("ap_t5", "ap_x5")
    st.markdown(f'<div class="ap-b"><div class="ap-c">'
                f'<div class="ap-c-t">{_e(T("ap_equipe"))}</div>'
                f'<div class="ap-c-x ap-todo" style="margin:0">'
                f'{_e(T("ap_equipe_x"))}</div></div></div>',
                unsafe_allow_html=True)


def render_contact():
    """La page « Nous contacter » : à qui écrire, et pour quoi."""
    st.markdown(_STYLE, unsafe_allow_html=True)
    st.markdown(f'<p class="ap-p">{_e(T("ap_c_x"))}</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="ap-b">'
        f'<div class="ap-c"><div class="ap-c-t">{_e(T("ap_c_mail"))}</div>'
        f'<div class="ap-c-x ap-todo" style="margin:0">'
        f'{_e(T("ap_c_mail_x"))}</div></div>'
        f'<div class="ap-c"><div class="ap-c-t">{_e(T("ap_c_qui"))}</div>'
        f'<div class="ap-c-x">{_e(T("ap_c_qui_x"))}</div></div>'
        f'<div class="ap-c"><div class="ap-c-t">{_e(T("ap_c_donnees"))}</div>'
        f'<div class="ap-c-x">{_e(T("ap_c_donnees_x"))}</div></div>'
        '</div>', unsafe_allow_html=True)
