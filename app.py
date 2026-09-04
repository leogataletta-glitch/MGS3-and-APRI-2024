"""
Enquête ménage 2024 — explorateur interactif
=============================================
Filtres combinables (sexe, catégorie économique, groupe d'âge, paysage,
section communale) + résultats bruts (n / %) et graphique pour n'importe
quelle question de l'enquête, calculés à la volée sur la population filtrée.

Toute la logique de calcul vit dans compute_banner_data.py (déjà utilisée
pour produire les classeurs Excel du projet) : on la relance en sous-processus
avec les filtres choisis passés par variables d'environnement, on récupère
le résultat, et on l'affiche.
"""

import io
import json
import datetime
import os
import pickle
import re
import subprocess
import sys

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# `accueil_page` n'est plus appelé : « Le territoire » ne porte plus que
# ses deux cartes, et son rendu vit dans `territoire_page`.
import accueil_apri
import actualites
import assets
import cadre_page
import analyse_ecarts
import croisement_resultats
import dimension_page
import environnement_page
import explorateur
import fiche_paysages
import filtres
import icones
import interventions_page
import i18n
import map_render
import methodologie_page
import ocb_page
import rapport_donateur
import onglets
import satellite_page
import systeme_complexe
import systeme_direct
import resilience_page
import saillants_page
import si_je_change
import systeme_page
import pistes_page
import synthese_page
import telechargements_page
import territoire_page
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(APP_DIR, "data", "donnees_anonymisees.csv")
QUESTIONS_INDEX = os.path.join(APP_DIR, "data", "questions_index.json")
CACHE_NATIONAL = os.path.join(APP_DIR, "data", "cache_national.pkl")

SUBCOLS = ["Total", "Homme", "Femme", "Cat A", "Cat B", "Cat C",
           "<25", "25-39", "40-59", "60+", "Littoral", "Montagne"]

SECTION_RAW = {
    "Anse à Drick": "Anse e Drick",
    "Barbois": "Barbois",
    "Dumont": "Dumont",
    "Débouchette": "Debouchette",
    "Mouline": "Mouline",
    "Quentin": "Quentin",
    "Beaulieu": "Beaulieu",
    "Blactote": "Blactote",
    "Dalmette": "Dalmette",
    "Trichet": "Trichet",
}
PAYSAGE_RAW = {"Littoral": "Littoral (ou plaene cotiere)", "Montagne": "Montagne"}

# ----------------------------------------------------------------------
# Accès protégé par mot de passe simple (voir le guide de déploiement pour
# configurer APP_PASSWORD dans les "Secrets" de Streamlit Cloud).
# ----------------------------------------------------------------------
def check_password():
    try:
        expected = st.secrets.get("APP_PASSWORD", None)
    except Exception:
        expected = None  # aucun fichier de secrets configuré -> accès libre (usage local)
    if not expected:
        return True  # pas de mot de passe configuré -> accès libre (usage local)
    if st.session_state.get("authed"):
        return True
    st.title("Household resilience survey 2024 — Haiti")
    pw = st.text_input("Mot de passe", type="password")
    if st.button("Entrer") or pw:
        if pw == expected:
            st.session_state["authed"] = True
            st.rerun()
        elif pw:
            st.error("Mot de passe incorrect.")
    return False


@st.cache_data(show_spinner=False)
def load_questions_index():
    with open(QUESTIONS_INDEX, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner="Calcul en cours pour cette combinaison de filtres…")
def compute_filtered(sexe, cat, age, paysage, sections):
    """Run compute_banner_data.py in a subprocess with the given combinable
    filters and return {'base_n':..., 'themes':[...]}. Cached by the exact
    filter tuple, so repeat views are instant."""
    if not (sexe or cat or age or paysage or sections):
        with open(CACHE_NATIONAL, "rb") as f:
            return pickle.load(f)

    env = os.environ.copy()
    env["DATA_CSV_PATH"] = DATA_CSV
    if sexe:
        env["SEXE_FILTER"] = ",".join(sexe)
    if cat:
        env["CAT_FILTER"] = ",".join(cat)
    if age:
        env["AGE_FILTER"] = ",".join(age)
    if paysage:
        env["PAYSAGE_FILTER"] = ",".join(PAYSAGE_RAW[p] for p in paysage)
    if sections:
        env["SECTION_FILTER_MULTI"] = ",".join(SECTION_RAW[s] for s in sections)

    out_path = os.path.join(APP_DIR, "data", "_tmp_live.pkl")
    result = subprocess.run(
        [sys.executable, os.path.join(APP_DIR, "dump_theme_data.py"), out_path],
        cwd=APP_DIR, env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])
    with open(out_path, "rb") as f:
        data = pickle.load(f)
    os.remove(out_path)
    return data


def rows_to_dataframe(theme, base_n):
    recs = []
    for label, group_n in theme["rows"]:
        row = {T("q_modalite"): label}
        for g in SUBCOLS:
            n = group_n.get(g, 0)
            b = base_n.get(g, 0)
            row[f"{g} (n)"] = n
            row[f"{g} (%)"] = round(n / b * 100, 1) if b else 0.0
        recs.append(row)
    return pd.DataFrame(recs)


def export_excel(theme, base_n):
    buf = io.BytesIO()
    df = rows_to_dataframe(theme, base_n)
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=T("q_resultat")[:31], index=False)
    buf.seek(0)
    return buf


# ----------------------------------------------------------------------
# LA COLONNE DE GAUCHE EST OUVERTE, ET ELLE LE RESTE.
# Streamlit laisse replier sa barre latérale d'un clic, et il garde ce choix
# d'une visite à l'autre : un clic malheureux, et le site s'ouvre sans sa
# navigation à la visite suivante, sans que rien n'explique où elle est
# passée. Ici la colonne n'est pas un panneau d'options, c'est le seul chemin
# vers les onze rubriques. On l'ouvre au démarrage, et la feuille de style
# retire le bouton qui permettait de la fermer.
st.set_page_config(page_title="Household resilience survey — Sud & Grand'Anse, Haiti",
                   layout="wide", initial_sidebar_state="expanded")

if not check_password():
    st.stop()

# Typographie de toute l'application. Deux principes : une seule famille
# (Roboto, la police institutionnelle du PNUE, avec repli système si la
# connexion aux polices Google échoue), et une largeur de ligne bornée —
# une phrase qui court sur 1400 px est illisible, c'est ce qui rendait les
# blocs de texte pénibles à lire.
st.markdown(("""
<style>
  /* UNE SEULE FAMILLE, ET C'EST UN CHOIX DE SOBRIÉTÉ. Les titres étaient en
     Outfit, une géométrique aux formes rondes qui donnait au site un air de
     page produit ; le corps était en Inter. Deux dessins qui se répondaient
     mal, et un contraste qui attirait l'œil sur la police au lieu du chiffre.
     Inter porte maintenant tout : ses chiffres sont tabulaires, ses formes
     neutres, et un observatoire n'a pas à avoir de voix typographique. */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* ------------------------------------------------------------------
     Parti pris : une page web, pas un document. Fond teinté, contenu
     posé dessus en cartes blanches avec du relief, coins arrondis,
     survol qui répond. Aucun texte gris minuscule : les commentaires
     de lecture sont lisibles ou ils n'ont pas lieu d'être.
     ------------------------------------------------------------------ */
  :root {
    --encre:      #101728;
    --encre-2:    #3c4761;
    --encre-3:    #6b7590;
    --fond:       #ffffff;
    --fond-2:     #f4f8fc;
    --carte:      #ffffff;
    --bord:       #e6ecf4;
    /* L'ACCENT DU CONTENU EST VERT DEPUIS QUE LES ÉTATS SÉLECTIONNÉS LE
       SONT. Il restait bleu — hérité d'une charte antérieure — et servait la
       pastille de rubrique, le filet des encadrés d'information, le liseré de
       champ actif : trois pièces de chrome qui juraient avec un onglet actif
       vert à quelques centimètres. Les couleurs de données ne bougent pas :
       un graphique bleu reste bleu, c'est une donnée, pas un état. */
    --accent:     #1a6b52;
    --accent-2:   #0f9d8f;
    --accent-3:   #f0a02a;
    --ombre:      0 1px 2px rgba(16,23,40,.04), 0 6px 18px rgba(16,23,40,.05);
    --ombre-haut: 0 3px 6px rgba(16,23,40,.07), 0 20px 44px rgba(16,23,40,.14);
  }

  /* Fond de travail blanc : les graphiques sont dessinés sur blanc, et aucune
     teinte de page ne peut jurer avec eux. La compartimentation ne passe donc
     plus par la couleur mais par le relief — filet fin, ombre douce, et une
     élévation franche au survol. */
  .stApp { background: var(--papier); }
  html, body, [class*="css"], .stApp {
    font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
    color: var(--encre-2);
  }
  /* padding-top nul : la photo est le premier élément de la page d'entrée et
     doit toucher le haut de la fenêtre. Sur les autres pages, où il n'y a
     plus rien au-dessus du titre, c'est .bh-vide qui redonne l'air. */
  /* ================= LA DENSITÉ DE LA PAGE ==============================
     Le site se lisait en descendant sans arrêt : une page tenait rarement sur
     un écran, et le lecteur passait son temps à faire défiler pour retrouver
     ce qu'il venait de voir. La cause n'était pas seulement la taille des
     lettres, c'était surtout l'air entre les blocs.

     DEUX RÉGLAGES, ET LE SECOND FAIT L'ESSENTIEL :

     1. L'espace entre deux blocs empilés descend d'un cran, et le pied de
        page perd la moitié de son vide. Cinq rem de blanc sous le dernier
        élément, c'était un demi-écran pour rien.
     2. Le contenu est mis à l'échelle de `--z`, une fois pour toutes. Réduire
        seulement la taille des lettres n'aurait presque rien donné : les
        pages sont hautes à cause des marges, des rembourrages de carte et
        des hauteurs de graphique, tous écrits en pixels dans une vingtaine
        de fichiers. `zoom` les prend tous ensemble, dans la même proportion,
        sans qu'aucune valeur ait à être retouchée et sans rien déformer.

     LA COLONNE DE GAUCHE N'EST PAS MISE À L'ÉCHELLE : une navigation qui
     rétrécit avec le contenu devient moins facile à viser, alors qu'elle ne
     coûte rien en hauteur. Le zoom ne porte que sur la zone de contenu. */
  /* LA RACINE DESCEND DE 16 À 14,5 PIXELS. C'est le seul levier qui atteigne
     le corps de texte du site : la très grande majorité des paragraphes
     n'ont aucune taille écrite, ils héritent de la racine. Tout ce que
     Streamlit exprime en `rem` — gouttières, hauteurs de widget, marges de
     titre — suit dans la même proportion, ce qui évite qu'un texte plus petit
     flotte dans des blocs restés grands. */
  /* LA TAILLE REMONTE, MAINTENANT QUE LA PAGE EST PLEINE LARGEUR. Le corps
     avait été descendu à 14,5 px et le zoom à 0,88 pour faire tenir plus de
     contenu sur un écran, à une époque où la colonne était bornée à 1240 px.
     La borne ayant sauté, la largeur ne manque plus : c'est la lisibilité qui
     manquait. Le zoom porte l'essentiel de la reprise, parce qu'il agit sur
     tout — y compris les dizaines de composants dont la taille est écrite en
     pixels fixes — et conserve donc exactement les proportions entre les
     éléments. La racine suit d'un cran, pour le texte courant qui en hérite.
     Total : environ 12 % de plus qu'avant. */
  html { font-size: 15.2px; }
  :root { --z: .95; --dz: 1.0526; }
  section.stMain, div[data-testid="stMain"] { zoom: var(--z); }
  /* PLEINE LARGEUR. La colonne était bornée à 1240 px : sur un grand écran,
     un tiers de la page restait blanc à droite pendant que les tableaux se
     serraient. La borne saute, deux gouttières suffisent à empêcher le texte
     de toucher les bords. */
  .block-container { max-width: none; padding-top: 0; padding-bottom: 0;
                     padding-left: 2.6rem; padding-right: 2.6rem; }
  /* LE HAUT DE PAGE TOUCHE LE HAUT DE L'ÉCRAN. Le pouce de blanc que
     Streamlit réserve au-dessus du bloc principal décollait le bandeau et le
     menu du bord ; le blanc qui sépare vraiment deux choses est rendu plus
     bas, dans la page. */
  div[data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
  /* UNE FEUILLE DE STYLE OCCUPE UNE CASE DANS LA COLONNE. Chaque appel à
     `st.markdown("<style>…")` produit un bloc de hauteur nulle — invisible,
     mais compté par le `gap` du conteneur vertical, et deux d'entre eux
     suffisaient à décoller le haut de page de vingt pixels. On les retire de
     la mise en page, eux et l'enveloppe qui ne contient qu'eux ; le
     `:only-child` garantit qu'on ne vise que les blocs qui ne portent QUE du
     style, jamais un texte qui porterait sa mise en forme avec lui. */
  div[data-testid="stElementContainer"]:has(
      div[data-testid="stMarkdownContainer"] > style:only-child),
  div[data-testid="stVerticalBlock"] > div:has(
      > div[data-testid="stElementContainer"]:only-child
        div[data-testid="stMarkdownContainer"] > style:only-child) {
      display: none !important;
  }
  /* --- LES ÉTAPES NUMÉROTÉES DES ÉCRANS DE RÉSULTATS ---------------------
     La feuille est ici, et non dans l'explorateur, parce que la première
     étape — le choix de la source — est rendue par l'aiguillage, avant que
     l'explorateur n'ait posé la sienne. Deux feuilles pour un même objet
     finissent toujours par diverger. */
  .ex-etape { display:flex; align-items:center; gap:11px; margin:22px 0 3px; }
  .ex-etape .n { flex:0 0 22px; width:22px; height:22px; border-radius:50%;
            background:#1a6b52; color:#fff; font-size:11.5px; font-weight:700;
            display:flex; align-items:center; justify-content:center;
            font-variant-numeric:tabular-nums; }
  .ex-etape .t { font-size:11px; font-weight:700; letter-spacing:.09em;
            text-transform:uppercase; color:#101728; white-space:nowrap; }
  .ex-etape-o { font-size:10.5px; color:#8a93a5; font-style:italic;
            white-space:nowrap; }
  .ex-etape .l { flex:1 1 auto; height:1px; background:#e6ece8; }
  p.ex-etape-x { font-size:12.5px !important; color:#6b7590 !important;
            margin:0 0 10px 33px !important; line-height:1.5 !important;
            text-align:left !important; }


  /* LA SOURCE RETENUE PORTE UNE COCHE. Sur une rangée de quatre cartes de
     même forme, le filet vert du haut dit laquelle est ouverte, mais il se
     confond avec le bord au premier coup d'œil ; la coche, elle, ne se
     confond avec rien. */
  div[class*="st-key-ra_source"] div[role="radiogroup"]
      > label:has(input:checked)::after {
      content: "✓"; position: absolute; top: 9px; right: 13px;
      color: #1a6b52; font-size: 13px; font-weight: 700; line-height: 1;
  }

  /* --- LE PIED FERME L'ÉCRAN, MÊME QUAND LA PAGE EST COURTE -------------
     Il n'y a jamais de blanc sous la bande verte : la colonne principale
     reçoit une hauteur minimale d'un écran, et le pied une marge haute
     automatique. Il descend donc jusqu'au bas de la fenêtre quand le contenu
     ne l'y pousse pas, et se laisse pousser plus bas quand la page est
     longue.

     LA HAUTEUR EST CORRIGÉE DU FACTEUR DE ZOOM. Le bloc principal porte un
     `zoom: .95` ; une hauteur de 100vh y serait rendue à quatre-vingt-quinze
     pour cent de l'écran. `--dz` est l'inverse de ce facteur — c'est déjà
     lui qui rend le bandeau et le pied pleine largeur. Les seize pixels
     retirés sont ceux que Streamlit retire lui-même : l'enveloppe du dernier
     bloc est mesurée seize pixels plus courte que son contenu, et c'est
     constant, quelle que soit la fenêtre et quel que soit le zoom. */
  /* LE BLOC PRINCIPAL EST ÉTIRÉ À LA HAUTEUR RÉELLE DE LA FENÊTRE. Réduit à
     quatre-vingt-quinze pour cent par le zoom, il s'arrêtait un vingtième
     d'écran trop haut : le pied se posait là, et les cinquante pixels qui
     restaient dessous étaient remplis par le vert du fond. La bande verte
     paraissait alors deux fois trop épaisse. Étiré de `--dz` — l'inverse du
     facteur de zoom — il va jusqu'au bord, et le pied avec lui. */
  section[data-testid="stMain"], div[data-testid="stMain"] {
      min-height: calc(100vh * var(--dz));
  }
  div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
      min-height: calc(100vh * var(--dz) - 16px);
  }
  /* ET LE FOND DE L'APPLICATION EST VERT, PARCE QUE LE ZOOM LAISSE UNE
     BANDE. Le bloc principal est réduit à quatre-vingt-quinze pour cent :
     sa boîte ne couvre donc que quatre-vingt-quinze pour cent de la hauteur
     de la fenêtre, et les cinq pour cent du bas ne lui appartiennent pas —
     ni au pied, qui ne peut pas descendre plus bas que la boîte qui le
     contient sans se faire couper. Peindre CE fond-là en vert ferme la
     fenêtre pour de bon : sous la bande, c'est la même couleur, et il n'y a
     plus jamais de blanc. La page, elle, garde son blanc — il est posé sur
     le bloc principal, qui couvre tout le reste. */
  div[data-testid="stApp"], .stApp,
  div[data-testid="stAppViewContainer"],
  section[data-testid="stMain"], div[data-testid="stMain"] {
      background: #1f5b46 !important;
  }
  /* LE BLANC DE LA PAGE EST PORTÉ PAR LE BLOC DE CONTENU, PAS PAR LE CADRE.
     Peint sur le bloc principal, le blanc s'arrêtait un pixel après la bande
     verte et laissait un trait clair entre elle et le fond : le zoom de
     quatre-vingt-quinze pour cent tombe entre deux pixels. Descendu d'un
     cran, il ne va que jusqu'au bas du contenu, et tout ce qui suit — le
     dernier pixel de la bande comme le bas de la fenêtre — est du même
     vert. */
  div[data-testid="stMainBlockContainer"] { background: #ffffff !important; }
  div[data-testid="stLayoutWrapper"]:has(> div[class*="st-key-zone_pied"]) {
      margin-top: auto !important; padding-top: 34px !important;
      /* SANS CELA, LE FLEX LE COMPRIME : la colonne rétrécit son dernier
         bloc pour tenir la hauteur promise, et la bande verte dépassait de
         sa boîte par le bas. Le pied ne se comprime pas. */
      flex: 0 0 auto !important;
  }
  /* L'ÉCART AU-DESSUS DU PIED EST PORTÉ PAR L'ENVELOPPE, PAS PAR LE PIED :
     une marge posée sur le pied lui-même sort de la boîte que le flex
     mesure. */
  .pied { margin-top: 0 !important;
    /* ET SON VERT SE PROLONGE SOUS ELLE. Entre le bas de la bande et le bas
       du bloc principal, il restait un filet de blanc — seize pixels, ceux
       que Streamlit ne compte pas — et sous le bloc reprenait le vert du
       fond : on lisait deux bandes vertes séparées par un trait clair.
       L'ombre portée, sans flou ni étalement, peint une copie de la bande
       cent pixels plus bas, élargie de six : l'élargissement fait remonter
       la copie de six pixels sous la bande, ce qui recouvre le trait d'un
       pixel que le zoom laissait à la jointure. Le vert est continu jusqu'au
       bord de la fenêtre, et rien n'a bougé dans la mise en page. */
    box-shadow: 0 100px 0 6px #1f5b46 !important;
    /* ET QUATRE PIXELS DE BORD, DE LA MÊME COULEUR : la boîte descend
       jusqu'au bas du bloc principal, et le trait blanc que le zoom laissait
       à sa dernière ligne disparaît sous elle. */
    border-bottom: 4px solid #1f5b46 !important; }
  /* ET SES ENVELOPPES LE MESURENT VRAIMENT. Streamlit centre le contenu d'un
     conteneur de markdown : la bande verte, plus haute que la ligne de texte
     qu'elle porte, débordait de sa boîte au lieu de l'agrandir. */
  div[class*="st-key-zone_pied"],
  div[data-testid="stLayoutWrapper"]:has(> div[class*="st-key-zone_pied"]),
  div[class*="st-key-zone_pied"] div[data-testid="stElementContainer"],
  div[class*="st-key-zone_pied"] div[data-testid="stMarkdown"],
  div[class*="st-key-zone_pied"] div[data-testid="stMarkdown"] > div,
  div[class*="st-key-zone_pied"] div[data-testid="stMarkdownContainer"] {
      height: auto !important; min-height: 0 !important;
      display: block !important;
  }
  div[data-testid="stVerticalBlock"] { gap: .65rem; }
  div[data-testid="stElementContainer"] { margin-bottom: 0; }

  /* ================= la barre d'outils de Streamlit : SUPPRIMÉE ==========
     « Share », « Deploy », le menu ⋮, la barre colorée de chargement : ce sont
     les commandes de l'ATELIER Streamlit, pas du site. Elles se posaient en
     haut à droite, par-dessus le logo du PNUE, et n'ont rien à faire dans un
     tableau de bord institutionnel qu'on montre à des partenaires.

     Les rendre transparentes ne suffisait pas — le texte restait lisible sur
     le vert. Elles sont maintenant retirées de la mise en page, à tous les
     noms sous lesquels Streamlit les publie : le nom change d'une version à
     l'autre, et n'en viser qu'un revient à voir la barre revenir au prochain
     déploiement.

     Ce qui n'est PAS touché : le bouton de repli de la colonne de gauche, qui
     appartient à la barre latérale et non à cet en-tête. */
  header[data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stToolbarActions"],
  [data-testid="stStatusWidget"],
  [data-testid="stDecoration"],
  [data-testid="stAppDeployButton"],
  [data-testid="stMainMenu"],
  #MainMenu,
  .stDeployButton,
  .stAppDeployButton,
  footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
  }

  /* LES QUELQUES ENDROITS QUE STREAMLIT HABILLE LUI-MÊME. Les légendes, les
     libellés de widgets et le contenu des menus déroulants portent la police
     du thème — « Source Sans » — et non la nôtre : trois familles cohabitaient
     donc sur la même page sans que personne ne l'ait décidé. On les ramène à
     Inter, et on rend aux icônes leur propre fonte juste après, sinon elles
     s'affichent en toutes lettres. */
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
  [data-testid="stWidgetLabel"] *, [data-testid="stRadio"] label *,
  [data-baseweb="select"] div, [data-baseweb="select"] span,
  [data-baseweb="popover"] li, [data-baseweb="tab"] *,
  [data-testid="stExpander"] summary p {
    font-family: "Inter", system-ui, -apple-system, sans-serif !important;
  }
  /* ET ON REND AUX ICÔNES LEUR FONTE. Une icône Streamlit est une ligature :
     le mot « arrow_right » dessiné par la fonte Material. Lui imposer Inter
     l'affiche en toutes lettres au milieu du titre — c'est arrivé sur les
     volets repliés, et la règle ci-dessus l'a causé avant de le corriger. */
  [data-testid="stIconMaterial"], span[class*="material-symbols"],
  [data-testid="stExpander"] summary svg + span:empty,
  .material-icons, .material-symbols-rounded, .material-symbols-outlined {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
  }

  /* --- titres --- */
  h1, h2, h3 {
    font-family: "Inter", system-ui, -apple-system, sans-serif !important;
    color: var(--encre); letter-spacing: -0.02em;
  }
  /* Les trois niveaux de titre sont coupés en plus de la racine : c'est là
     que la taille se voyait le plus, un titre de page occupant à lui seul une
     bande de l'écran pour six mots. */
  h1 { font-weight: 700 !important; font-size: 2rem !important;
       line-height: 1.14 !important; }
  h2 { font-weight: 700 !important; font-size: 1.35rem !important;
       margin-top: .2rem !important; padding-bottom: .2rem !important; }
  h3 { font-weight: 600 !important; font-size: 1.1rem !important;
       margin-top: .2rem !important; }

  /* --- texte : jamais minuscule, jamais délavé --- */
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] li {
    font-size: 14.5px; line-height: 1.66; color: var(--encre-2);
  }
  [data-testid="stMarkdownContainer"] strong { color: var(--encre); }
  [data-testid="stCaptionContainer"] p {
    font-size: 14px !important; line-height: 1.62 !important;
    color: var(--encre-2) !important; max-width: 92ch;
  }

  /* ------------------------------------------------------------------
     LES CARTES. Tout bloc encadré (st.container(border=True)) devient
     une carte blanche en relief qui se soulève au survol.
     ------------------------------------------------------------------ */
  /* Une carte = un bloc encadré qui contient une pilule de titre. On le cible
     par son contenu (:has), parce que Streamlit ne donne pas de marqueur propre
     aux conteneurs bordés — et que le nom technique de ces conteneurs change
     d'une version à l'autre. */
  div[data-testid="stVerticalBlock"]:has(
      > div[data-testid="stElementContainer"] .titre-bloc),
  div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--carte) !important;
    border: 1px solid var(--bord) !important;
    border-radius: 18px !important;
    box-shadow: var(--ombre);
    padding: 16px 20px 18px !important;
    transition: box-shadow .2s ease, transform .2s ease, border-color .2s ease;
    animation: apparition .5s cubic-bezier(.2,.7,.3,1) both;
  }
  div[data-testid="stVerticalBlock"]:has(
      > div[data-testid="stElementContainer"] .titre-bloc):hover,
  div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: var(--ombre-haut); transform: translateY(-3px) !important;
    border-color: #c3ded0 !important;
  }
  /* Les blocs des conditions du croisement, imbriqués, restent discrets. */
  div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"]
      .titre-bloc) div[data-testid="stVerticalBlock"][style*="border"] {
    box-shadow: none; animation: none;
  }

  @keyframes apparition {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: none; }
  }

  /* --- l'entête de section, en pilule colorée --- */
  .titre-bloc {
    display: inline-flex; align-items: center; gap: 9px;
    font-family: "Inter", system-ui, sans-serif; font-weight: 700; font-size: 12px;
    letter-spacing: .06em; text-transform: uppercase;
    color: var(--accent); background: #eaf5f0;
    padding: 6px 13px; border-radius: 999px; margin: 0 0 4px;
  }
  .titre-bloc.vert  { color: #0b7f74; background: #e5f6f3; }
  .titre-bloc.ambre { color: #a8690a; background: #fdf3e3; }

  /* --- menus : champs pleins, arrondis, réactifs --- */
  label[data-testid="stWidgetLabel"] p {
    font-size: 12px !important; font-weight: 700 !important;
    letter-spacing: .04em; color: var(--encre-3) !important;
    text-transform: uppercase;
  }
  div[data-baseweb="select"] > div {
    font-size: 14.5px; border-radius: 11px; border: 1.5px solid var(--bord);
    background: #f7fafd; transition: border-color .15s ease, box-shadow .15s ease;
  }
  div[data-baseweb="select"] > div:hover { border-color: #b6d8c6; }
  div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent); box-shadow: 0 0 0 3px rgba(26,107,82,.16);
  }

  /* --- bandeau d'info --- */
  div[data-testid="stAlert"] {
    border: 1px solid var(--bord); border-left: 5px solid var(--accent);
    border-radius: 14px; background: var(--carte); box-shadow: var(--ombre);
    padding: 3px 6px;
  }
  div[data-testid="stAlert"] > div {
    background: transparent !important; border: none !important;
    padding: 12px 14px !important;
  }
  div[data-testid="stAlert"] p {
    font-size: 14.5px !important; color: var(--encre-2) !important; margin: 0;
  }

  details {
    background: var(--carte); border: 1px solid var(--bord) !important;
    border-radius: 14px !important; box-shadow: var(--ombre);
  }
  details summary p {
    font-size: 14px !important; font-weight: 600 !important;
    color: var(--encre-2);
  }

  .org-mention {
    font-size: 11.5px; color: var(--encre-3); letter-spacing: .12em;
    text-transform: uppercase; margin: 0 0 3px 1px; font-weight: 700;
  }

  /* --- les trois entrées : grandes tuiles en relief --- */
  div[data-testid="stButton"] > button {
    height: 92px; border-radius: 16px; border: 1.5px solid var(--bord);
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 16.5px !important; font-weight: 600 !important;
    line-height: 1.3; white-space: normal; padding: 12px 20px;
    background: var(--carte); box-shadow: var(--ombre);
    transition: transform .18s cubic-bezier(.2,.7,.3,1), box-shadow .18s ease,
                background .18s ease, border-color .18s ease;
  }
  div[data-testid="stButton"] > button p {
    font-size: 16.5px !important; font-weight: 600 !important;
  }
  div[data-testid="stButton"] > button:hover {
    transform: translateY(-3px); box-shadow: var(--ombre-haut);
    border-color: #b6d8c6;
  }
  div[data-testid="stButton"] > button[kind="primary"],
  div[data-testid="stButton"] > button[kind="primary"] p,
  div[data-testid="stButton"] > button[kind="primary"] div { color: #fff !important; }
  /* L'ÉTAT SÉLECTIONNÉ EST VERT, PAS BLEU, ET IL L'EST PARTOUT.
     Le bleu venait d'une charte antérieure et ne se justifiait plus : la
     colonne de navigation, les pastilles de filtre et l'emblème sont verts,
     de sorte qu'un onglet actif en bleu était la seule pièce d'une autre
     couleur — l'œil y lisait un autre type d'objet. Même teinte pour tous
     les états sélectionnés, du bouton à l'onglet en passant par la carte de
     dimension. */
  div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #2b8663 0%, #1c6349 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 2px 6px rgba(28,99,73,.28), 0 14px 30px rgba(28,99,73,.24);
  }
  div[data-testid="stButton"] > button[kind="secondary"],
  div[data-testid="stButton"] > button[kind="secondary"] p {
    color: var(--encre) !important;
  }

  /* La barre d'onglets du site vit dans `onglets.py`, avec sa feuille de
     style : trois pages la partagent, et une seule source évite qu'elles
     divergent. Rien à styler ici. */

  /* --- radios : pastilles cliquables --- */
  .stRadio > div[role="radiogroup"] { gap: 8px; flex-wrap: wrap; }
  .stRadio > div[role="radiogroup"] > label {
    background: #f4f8fc; border: 1.5px solid var(--bord);
    border-radius: 999px; padding: 7px 15px 7px 11px;
    transition: all .15s ease;
  }
  .stRadio > div[role="radiogroup"] > label:hover {
    border-color: #b6d8c6; background: #eef8f2;
  }
  .stRadio > div[role="radiogroup"] > label > div:last-child p {
    font-size: 13.5px !important; font-weight: 600 !important;
    color: var(--encre-2);
  }

  /* --- barre latérale --- */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f4f8f5 0%, #fafcfb 100%); border-right: 1px solid var(--bord);
  }
  section[data-testid="stSidebar"] h2 {
    font-size: 1.15rem !important; margin-top: .3rem !important;
  }

  /* --- tableaux --- */
  div[data-testid="stDataFrame"] {
    border: 1px solid var(--bord); border-radius: 12px; overflow: hidden;
  }

  /* --- téléchargements : bouton doux --- */
  div[data-testid="stDownloadButton"] > button {
    height: auto; padding: 9px 18px !important; border-radius: 999px;
    background: #eaf5f0 !important; border: 1.5px solid #cde4d9 !important;
    color: var(--accent) !important; font-weight: 600 !important;
    font-size: 13.5px !important; box-shadow: none;
  }
  div[data-testid="stDownloadButton"] > button:hover {
    background: #dcefe5 !important; transform: translateY(-1px);
  }

  /* --- iframes des graphiques : coins arrondis, fond blanc --- */
  iframe { border-radius: 12px; background: #ffffff; }

  /* ================= barre latérale : la navigation du site =============
     LE VERT PROFOND EST PARTI. Une colonne pleine de couleur sombre pesait
     sur toute la page : elle criait plus fort que le contenu qu'elle sert à
     atteindre, et il fallait tout écrire en blanc dessus, ce qui alourdit
     encore. La colonne est maintenant blanche, séparée du contenu par un
     simple filet, et le seul retour visuel est un fond très clair au
     survol. La navigation se voit quand on la cherche et se tait le reste
     du temps, ce qui est exactement son métier. */
  section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--bord) !important;
    width: 310px !important; min-width: 310px !important;
  }
  /* LA COLONNE NE SE REPLIE PLUS, SUR ÉCRAN LARGE.
     Repliée, Streamlit ne la cache pas : il la fait glisser hors de l'écran
     par une translation, en passant `aria-expanded` à false. Deux règles
     suffisent donc, et il faut les deux : annuler la translation dans cet
     état-là, et retirer le chevron qui la déclenche. Sans la première, un
     état replié mémorisé par le navigateur rouvrirait la page sans
     navigation ; sans la seconde, le chevron resterait là à promettre une
     action qui ne se passe plus.

     LE SEUIL EST INDISPENSABLE. Sous mille pixels, Streamlit ne pousse plus
     le contenu à côté de la colonne : il la pose PAR-DESSUS. Forcer
     l'ouverture là aussi enfermerait le lecteur derrière un panneau qu'il ne
     pourrait plus refermer, ce qui est pire que le défaut qu'on corrige. En
     dessous du seuil, on ne touche à rien et le chevron revient. */
  @media (min-width: 1001px) {
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"][aria-expanded="false"] {
      transform: none !important; visibility: visible !important;
      margin-left: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
      display: none !important;
    }
    /* CETTE BANDE VIDE EN HAUT DE LA COLONNE ÉTAIT LE LOGEMENT DU CHEVRON.
       Streamlit lui réserve une hauteur fixe qu'il occupait seul ; le chevron
       retiré, il ne restait qu'un rectangle de blanc au-dessus du choix de
       langue. Il disparaît avec lui, et le contenu remonte en haut de
       l'écran. Sous le seuil, le chevron revient : sa loge aussi. */
    [data-testid="stSidebarHeader"] {
      display: none !important;
    }
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] { padding-top: 0 !important; }
    [data-testid="stSidebarUserContent"] { padding-top: 6px !important; }
  }
  /* Le bloc de marque remonte : dix-huit pixels de blanc au-dessus d'un
     logo, sur une colonne qui commence en haut de l'écran, ne servaient
     qu'à repousser l'identité vers le bas. */
  section[data-testid="stSidebar"] > div { padding: 0 14px 14px; }

  /* Le bloc de marque, sur le modèle de la charte : l'emblème détouré posé
     directement sur le vert — pas de carte blanche, qui faisait une tache —
     puis le nom en texte et un filet vert sous le sigle. L'emblème est
     l'image EMBLEME_APRI, découpée du logo complet : le verbal « IRLA/APRI »
     du fichier d'origine devenait illisible à cette taille. */
  .apri-marque {
    display: flex; align-items: center; gap: 15px;
    padding: 0 2px 14px; margin-bottom: 0;
    border-bottom: 1px solid var(--bord);
  }
  .apri-marque img {
    width: 76px; height: 76px; flex: 0 0 76px; display: block;
  }
  .apri-bloc-nom { min-width: 0; }
  .apri-nom {
    font-family: "Inter", system-ui, sans-serif; font-size: 33.5px; font-weight: 700;
    color: var(--encre); letter-spacing: .01em; line-height: 1;
  }
  .apri-filet {
    width: 64px; height: 3px; border-radius: 2px; background: #6ba03a;
    margin: 5px 0 0;
  }
  /* Deux niveaux dans l'accroche, comme sur la charte : ce qu'est
     l'observatoire, en vert clair, puis où il porte, en blanc. Une seule
     ligne grise disait les deux d'un même souffle et on ne lisait ni l'un ni
     l'autre. */
  .apri-baseline {
    font-size: 11px; color: #5d8c2b; line-height: 1.3;
    margin-top: 6px; font-weight: 500;
  }
  .apri-lieu {
    font-size: 11.5px; color: var(--encre-2); line-height: 1.3;
    margin-top: 3px; font-weight: 600;
  }
  /* Pied de colonne : le logo du PNUE y descend, puisque les logos ne
     doivent plus apparaître dans le contenu des pages. */
  .apri-org {
    display: flex; align-items: center; gap: 10px;
    margin-top: 14px; padding-top: 13px;
    border-top: 1px solid var(--bord);
  }
  /* Le logo institutionnel n'a plus besoin de sa plaque blanche : la colonne
     est blanche. Une plaque sur un fond de même couleur ne se voit pas, elle
     se devine, et une bordure devinée est une bordure de trop. */
  .apri-org img {
    width: 34px; height: 34px; flex: 0 0 34px; object-fit: contain;
  }
  .nav-groupe {
    font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--encre-3); font-weight: 700;
    margin: 18px 0 8px 4px;
  }
  .apri-pied {
    font-size: 10.5px; color: var(--encre-3); line-height: 1.5;
    padding: 14px 4px 4px; margin-top: 10px;
    border-top: 1px solid var(--bord);
  }
  /* Dans le bloc PNUE, la mention institutionnelle est déjà séparée par le
     filet de .apri-org : lui laisser le sien dessinait deux traits l'un sur
     l'autre. */
  .apri-org .apri-pied {
    border-top: none; padding: 0; margin: 0; font-size: 11px;
    color: var(--encre-3);
  }

  /* --- les entrées de menu ---------------------------------------------
     Trois réglages qui comptent, et qui manquaient tous les trois au premier
     essai :

     ALIGNEMENT — le bouton de Streamlit centre son contenu par défaut, à
     trois niveaux imbriqués. Un libellé sur deux lignes se retrouvait alors
     indenté au premier rang et collé au bord au second. Il faut forcer
     l'alignement à gauche sur le bouton ET sur ses conteneurs internes, sinon
     l'un des trois reprend la main.

     TAILLE — 15,5 px et 46 px de hauteur minimale : un menu se vise au
     curseur sans regarder, il lui faut une cible franche.

     SURVOL — un fond très clair, et rien d'autre : ni contour, ni ombre, ni
     déplacement. Sans retour au survol, rien ne distingue une ligne
     cliquable d'un simple titre ; avec trois retours à la fois, la colonne
     s'agite. */
  /* LE MENU SUIT LA LECTURE, IL NE RESTE PAS EN HAUT DE PAGE.
     Il vivait dans une colonne aussi haute que son contenu : sur les pages
     longues — Données, Rapport donateur, Analyse des résultats — on le
     perdait de vue au troisième écran et il fallait remonter tout en haut
     pour changer de rubrique. La colonne se colle donc au haut de la fenêtre
     et y reste. `align-self: flex-start` est indispensable : sans lui,
     Streamlit étire la colonne sur toute la hauteur de la ligne, et un
     élément étiré ne peut pas coller. Si le menu dépasse la fenêtre, il
     défile pour son propre compte. */
  /* LA BARRE EST UNE RANGÉE, ET ELLE RESTE EN HAUT.
     Streamlit empile ses éléments : on met donc son bloc vertical en `flex`
     avec `flex-wrap`, et les boutons se rangent côte à côte. Chacun prend la
     largeur de son mot — plus de `width:100%` — et la rangée passe à la ligne
     quand la fenêtre se rétrécit. `position: sticky` la garde à l'écran quand
     la page défile, ce que la colonne de gauche faisait déjà. */
  /* LE CONTENEUR À CLÉ EST LUI-MÊME LE BLOC VERTICAL. Streamlit pose la
     classe `st-key-…` sur le `stVerticalBlock`, pas sur un parent : c'est
     donc lui qu'on met en `flex`, et ses enfants directs — les conteneurs
     d'élément — deviennent les cases de la rangée. */
  div[class*="st-key-zone_nav"] {
    display: flex !important; flex-direction: column !important;
    align-items: stretch !important; gap: 1px !important;
    /* COLLANTE, PAS FLOTTANTE. Elle suit la page quand on descend et
       s'arrête d'elle-même en haut de la fenêtre ; elle ne recouvre jamais
       le contenu, qui a sa propre colonne. `align-self: flex-start` est
       indispensable : sans lui la colonne de Streamlit s'étire sur toute la
       hauteur de la page et `sticky` n'a plus rien à quoi se coller. */
    position: sticky; top: 10px; align-self: flex-start;
    border: 1px solid #e4e2de;
    /* LE FOND EST POSÉ SUR LA COLONNE, PAS DERRIÈRE ELLE. Un dégradé qui
       blanchit à mi-hauteur disparaissait avant le bas de la liste : la
       moitié inférieure du menu était sur le même blanc que la page, et la
       colonne ne se distinguait plus. Le vert pâle tient sur toute la
       hauteur, et il n'est éclairci que légèrement vers le bas. */
    /* UN VERT TRÈS PÂLE, JUSTE ASSEZ POUR QUE LA COLONNE SE DÉTACHE. Toute
       blanche, elle se confondait avec la page et avec le blanc du bandeau :
       seul son bord la signalait, et un bord ne fait pas une zone. Le vert
       est celui du site, dilué jusqu'à la limite du perceptible, et il
       s'éclaircit vers le bas pour ne pas peser sous la dernière rubrique. */
    background: linear-gradient(180deg, #f4f8f5 0%, #fafcfb 100%);
    /* ELLE TOUCHE LE BORD GAUCHE DE L'ÉCRAN. La gouttière du bloc principal
       — 2,6 rem — laissait une bande blanche entre le bord de la fenêtre et
       la colonne, alors que le bandeau au-dessus, lui, va d'un bord à
       l'autre : les deux zones de cadre ne s'alignaient pas et la colonne
       paraissait posée de travers. La marge négative annule exactement cette
       gouttière, le bord et les deux coins de gauche disparaissent avec
       elle, et le rembourrage gauche est augmenté d'autant pour que les
       rubriques ne collent pas au bord. */
    border-left: none;
    border-radius: 0 14px 14px 0;
    padding: 12px 12px 16px 16px;
    margin: 0 0 0 -2.6rem;
  }
  /* LES ENTRÉES RESPIRENT. Streamlit colle ses conteneurs d'élément les uns
     aux autres : le fond de survol d'une ligne venait alors toucher celui de
     la ligne au-dessus, et l'on croyait avoir survolé les deux. Quatre pixels
     entre deux lignes suffisent à ce que la zone qui s'allume soit
     visiblement UNE ligne — c'est peu, et c'est exactement ce qui manquait. */
  div[class*="st-key-zone_nav"] div[data-testid="stElementContainer"]:has(
      div[data-testid="stButton"]) {
    margin: 3px 0 !important;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stElementContainer"],
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] {
    width: 100% !important; flex: 0 0 auto !important;
  }
  /* LE TITRE DE FAMILLE : petit, en capitales espacées, vert sourd. Il ne
     doit pas peser autant que les rubriques qu'il coiffe — c'est une
     étiquette de rangement, pas une destination. */
  div[class*="st-key-zone_nav"] .nav-famille {
    font-size: 10px; font-weight: 700; letter-spacing: .11em;
    text-transform: uppercase; color: #2f6b4f;
    margin: 20px 0 7px; padding-left: 10px;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button {
    display: flex !important; align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important; min-height: 30px !important; height: auto !important;
    padding: 8px 10px !important; border-radius: 8px !important;
    border: none !important;
    background: transparent !important; box-shadow: none !important;
    transition: background .15s ease, color .15s ease;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button > div,
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button
    div[data-testid="stMarkdownContainer"] {
    width: 100% !important; text-align: left !important;
    display: block !important;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button p {
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 12.5px !important; font-weight: 500 !important;
    line-height: 1.3 !important;
    color: var(--encre-2) !important;
    text-align: left !important; margin: 0 !important;
  }
  div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button:hover {
    background: #f1f6f4 !important; transform: none !important;
  }
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button:hover p {
    color: var(--encre) !important;
  }
  /* L'ENTRÉE ACTIVE : un filet vert à gauche, un fond très pâle, le mot en
     gras vert. Dans une colonne, le filet se pose au bord d'attaque de la
     ligne — c'est là que l'œil descend, et il n'a rien à chercher. */
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button[kind="primary"] {
    background: #f1f6f4 !important;
    border: none !important; box-shadow: none !important;
    border-left: 3px solid var(--accent) !important;
    border-radius: 0 8px 8px 0 !important;
    padding-left: 9px !important;
  }
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button[kind="primary"] p {
    color: var(--accent) !important; font-weight: 700 !important;
  }
  div[class*="st-key-zone_nav"]
    div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #e8f1ec !important;
  }

  /* SUR ÉCRAN ÉTROIT LA COLONNE REDEVIENT UNE RANGÉE. Une colonne de menu
     large de quatre-vingts pixels sur un téléphone ne sert personne : les
     entrées se remettent côte à côte et passent à la ligne. */
  @media (max-width: 860px) {
    div[class*="st-key-zone_nav"] {
      flex-direction: row !important; flex-wrap: wrap !important;
      position: static; border-right: 0;
      border-bottom: 1px solid #eef2f7; padding: 2px 0 6px;
    }
    div[class*="st-key-zone_nav"] div[data-testid="stElementContainer"],
    div[class*="st-key-zone_nav"] div[data-testid="stButton"] {
      width: auto !important;
    }
    div[class*="st-key-zone_nav"] div[data-testid="stButton"] > button {
      width: auto !important; padding: 6px 9px !important;
    }
    div[class*="st-key-zone_nav"]
      div[data-testid="stButton"] > button[kind="primary"] {
      border-left: 0 !important;
      border-bottom: 2px solid var(--accent) !important;
      border-radius: 8px 8px 0 0 !important; padding-left: 9px !important;
    }
  }
  /* Le sélecteur de langue, seul widget non bouton de la colonne */
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] .stRadio label p {
    color: var(--encre-2) !important;
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: #fbfcfe; border-color: var(--bord);
    color: var(--encre);
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: var(--encre-3);
  }

  /* --- le raccourci « filtres rapides » de la colonne ------------------ */
  .f-separateur {
    height: 1px; background: var(--bord); margin: 16px 2px 2px;
  }
  .nav-etat {
    font-size: 11.5px; color: var(--encre-3); line-height: 1.45;
    padding: 6px 6px 0;
  }
  /* Le bouton de remise à zéro ne doit pas se lire comme une entrée de menu :
     il agit sur le filtre, pas sur la navigation. Contour discret, hauteur
     réduite, et son icône de rafraîchissement. */
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button {
    min-height: 38px !important; padding: 8px 13px !important;
    border: 1px solid var(--bord) !important;
    background: #fbfcfe !important;
    border-radius: 9px !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button p {
    font-size: 12.5px !important; font-weight: 500 !important;
  }
  section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"]
    div[data-testid="stButton"] > button:disabled { opacity: .5; }
  __ICONE_RESET__
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label p {
    font-size: 11.5px !important; letter-spacing: .04em;
    color: var(--encre-3) !important; font-weight: 600 !important;
    text-transform: uppercase;
  }
  /* Le bouton « Réinitialiser » ne doit pas ressembler à une entrée de menu :
     il agit sur le filtre, pas sur la navigation. C'est le seul bouton de la
     colonne placé dans une rangée de colonnes — on le cible par là, faute de
     pouvoir donner une classe à un bouton Streamlit. */
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button {
    min-height: 0 !important; padding: 4px 9px !important;
    justify-content: center !important; margin: 0;
    border: 1px solid var(--bord) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button p {
    font-size: 11.5px !important; font-weight: 600 !important;
    text-align: center !important;
    color: var(--encre-2) !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
    div[data-testid="stButton"] > button:disabled {
    opacity: .45; border-color: var(--bord) !important;
  }
  .f-chips { display: flex; flex-direction: column; gap: 6px; margin-top: 11px; }
  .f-chip {
    display: flex; align-items: baseline; gap: 8px;
    background: #f6f9fd; border: 1px solid var(--bord);
    border-radius: 9px; padding: 7px 11px;
  }
  .f-chip-cle {
    font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
    color: var(--encre-3); font-weight: 700; white-space: nowrap;
  }
  .f-chip-val {
    font-size: 12.5px; color: var(--encre); font-weight: 600;
  }
  .f-vide {
    font-size: 11.5px; color: var(--encre-3); line-height: 1.5;
    margin-top: 10px; padding: 0 3px;
  }

  /* ================= l'en-tête de page ===================================
     IL N'Y A PLUS DE RUBAN, et les règles qui l'habillaient ont été retirées
     avec lui : une rangée pleine largeur, des boutons de langue déguisés en
     pastilles, un cadre pour le logo. Les trois contenus sont partis ailleurs
     — la langue en tête de la colonne verte, le logo sur la photo, les
     onglets dans la colonne depuis longtemps — et une feuille de style qui
     décrit un élément disparu est un piège pour la prochaine retouche. */

  /* La photo déborde la colonne de texte et touche les deux bords : c'est
     un en-tête, pas une illustration posée dans le contenu. */
  /* L'enveloppe existe pour que le logo puisse se poser DANS la photo :
     un élément en position absolue se place par rapport au premier parent
     positionné, et l'image seule n'en est pas un. */
  .bandeau-enveloppe { position: relative; display: block; line-height: 0; }
  /* L'ILLUSTRATION OCCUPE TOUTE LA LARGEUR, ET SON VOILE EST DANS LE FICHIER.
     Le dégradé blanc qui éclaircit le tiers gauche a été composé dans l'image
     elle-même plutôt qu'en CSS : il devait effacer une marque déjà incrustée
     dans l'illustration fournie, ce qu'un dégradé posé par-dessus n'aurait pas
     fait proprement aux jointures. */
  /* LES TROIS DÉCLARATIONS SONT FORCÉES. Streamlit impose à toute image un
     `object-fit: scale-down` : l'illustration se réduisait alors pour tenir
     entière dans le bandeau, et se retrouvait posée en petit au milieu d'une
     bande blanche au lieu de la remplir. */
  /* LE PIED DE PAGE, EN PLEINE LARGEUR ET EN VERT PROFOND. Il ferme la page
     comme le bandeau l'ouvre : deux barres de la même largeur, l'une claire
     et l'autre foncée, entre lesquelles le contenu tient. Sans lui, la page
     s'arrêtait sur du blanc et rien ne disait qu'on était arrivé au bout. */
  .pied {
    display: flex; align-items: center; justify-content: space-between;
    gap: 20px; flex-wrap: wrap;
    background: #1f5b46; color: #e6f0ea;
    padding: 13px calc(2.6rem * var(--dz)); margin-top: 34px;
    font-size: 12px; line-height: 1.5;
  }
  .pied .pd-g { display: flex; align-items: center; gap: 10px; }
  .pied .pd-devise { color: #cfe3d8; }
  .pied .pd-credit { color: #a9c7b8; }
  @media (max-width: 700px) { .pied { justify-content: flex-start; } }

  /* L'ILLUSTRATION OCCUPE TOUTE LA LARGEUR, ET SON VOILE EST DANS LE FICHIER.
     Le dégradé blanc qui éclaircit le tiers gauche a été composé dans l'image
     elle-même plutôt qu'en CSS : il devait effacer une marque déjà incrustée
     dans l'illustration fournie, ce qu'un dégradé posé par-dessus n'aurait pas
     fait proprement aux jointures. */
  /* LES TROIS DÉCLARATIONS SONT FORCÉES. Streamlit impose à toute image un
     `object-fit: scale-down` : l'illustration se réduisait alors pour tenir
     entière dans le bandeau, et se retrouvait posée en petit au milieu d'une
     bande blanche au lieu de la remplir. */
  /* LE PIED DE PAGE, EN PLEINE LARGEUR ET EN VERT PROFOND. Il ferme la page
     comme le bandeau l'ouvre : deux barres de la même largeur, l'une claire
     et l'autre foncée, entre lesquelles le contenu tient. Sans lui, la page
     s'arrêtait sur du blanc et rien ne disait qu'on était arrivé au bout. */
  .pied {
    display: flex; align-items: center; justify-content: space-between;
    gap: 20px; flex-wrap: wrap;
    background: #1f5b46; color: #e6f0ea;
    padding: 13px calc(2.6rem * var(--dz)); margin-top: 34px;
    font-size: 12px; line-height: 1.5;
  }
  .pied .pd-g { display: flex; align-items: center; gap: 10px; }
  .pied .pd-devise { color: #cfe3d8; }
  .pied .pd-credit { color: #a9c7b8; }
  @media (max-width: 700px) { .pied { justify-content: flex-start; } }


  /* LE LOGO DU PNUE EST UN CALQUE, PAS UN MORCEAU DE LA PHOTOGRAPHIE. Le
     coin haut-droit du cadrage mêle du ciel vif et des frondaisons sombres :
     recomposé dans l'image, un logo blanc s'y perdait par endroits et un
     logo foncé ailleurs, et tout voile assez fort pour le sauver se voyait.
     Posé en calque, il garde son ombre portée — laquelle le détache aussi
     bien du clair que du sombre, sans rien changer à l'image. */
  /* LE LOGO EST BLANC, ET SES OMBRES SONT CE QUI LE REND LISIBLE. Sur un
     dessin au crayon, du blanc sur du blanc ne se verrait pas : les deux
     ombres portées lui dessinent un contour sombre, et c'est ce contour
     qu'on lit là où le papier est clair. La hauteur suit celle du bandeau,
     qui vient d'être raccourci. */
  .bandeau-logo {
    position: absolute; top: 13px; right: 30px; height: 44px; width: auto;
    display: block; pointer-events: none; z-index: 4;
    filter: drop-shadow(0 1px 2px rgba(30,45,35,.85))
            drop-shadow(0 0 6px rgba(30,45,35,.55));
  }

  /* L'ILLUSTRATION OCCUPE TOUTE LA LARGEUR ET N'EST PAS ROGNÉE. Streamlit
     impose à toute image un `object-fit: scale-down` et un `max-width` :
     l'illustration se réduisait alors pour tenir entière dans une bande
     blanche au lieu de la remplir, d'où les trois déclarations forcées. La
     hauteur est laissée libre — la composition va d'un logo à l'autre, et
     toute hauteur fixée en couperait un. */
  .bandeau-fond {
    width: 100% !important; height: auto !important;
    object-fit: fill !important;
    display: block !important; max-width: none !important;
  }

  /* LE PIED, LUI, RESTE PLEINE LARGEUR : il est rendu hors des colonnes, et
     c'est cette règle qui l'étend d'un bord à l'autre de la fenêtre. */
  .bandeau-haut {
    width: calc(100vw * var(--dz)) !important;
    max-width: calc(100vw * var(--dz)) !important;
    margin-left: calc(50% - 100vw * var(--dz) / 2);
  }
  /* L'ILLUSTRATION, ELLE, TIENT DANS SA COLONNE — et la déborde à droite du
     seul rembourrage du bloc principal, pour aller toucher le bord de
     l'écran comme le menu touche l'autre. Elle porte les deux classes ; la
     règle qui suit celle du pied la reprend donc entièrement. */
  .bandeau-haut.bandeau-enveloppe {
    width: calc(100% + 2.6rem) !important;
    max-width: calc(100% + 2.6rem) !important;
    margin-left: 0 !important; margin-right: -2.6rem !important;
  }
  /* LES TEXTES SONT JUSTIFIÉS.
     Un paragraphe au fer à gauche laisse un bord droit en dents de scie qui,
     sur une colonne large, fait paraître la page moins tenue qu'elle ne l'est.
     La règle ne touche que les paragraphes et les listes du contenu : les
     libellés, les cellules de tableau et les légendes gardent leur alignement,
     sans quoi une ligne de deux mots s'étirerait d'un bord à l'autre. */
  div[data-testid="stMarkdownContainer"] > p,
  div[data-testid="stMarkdownContainer"] > ul > li,
  div[data-testid="stMarkdownContainer"] > ol > li {
    text-align: justify; text-justify: inter-word;
  }
  .f-etiquette { height: 22px; }

  /* --- LES DEUX LANGUES, AU BOUT DE LA BARRE D'ONGLETS -----------------
     EN NOIR SUR BLANC, ET NON PLUS EN BLANC SUR LA PHOTO. L'illustration ne
     paraît plus que sur l'accueil ; un réglage qui n'existerait que sur une
     page n'est pas un réglage. Les pastilles reviennent donc dans la barre,
     poussées tout à droite par une marge automatique, à la même hauteur que
     les rubriques.

     LA LANGUE EN COURS SE MARQUE PAR SON CONTOUR, PAS PAR UN APLAT. Un fond
     plein, au bout d'une rangée d'onglets, se serait lu comme un onglet
     actif de plus — et il aurait fallu du blanc pour le texte, ce qu'on
     cherche justement à quitter. Le trait d'encre et la graisse suffisent :
     tout est noir, rien n'est peint.

     Elles empruntent la classe `st-key-lang_*` de leur bouton : c'est le seul
     point d'accroche stable que Streamlit offre sur un widget précis. Tout ce
     que la barre impose aux boutons est défait ici, explicitement. */
  /* STREAMLIT ENVELOPPE UN CONTENEUR À CLÉ DANS UN BLOC DE MISE EN PAGE, et
     c'est LUI le voisin des onglets dans la rangée. Réglé sur le seul bloc
     intérieur, le retrait automatique laissait l'enveloppe prendre toute la
     largeur : la paire tombait sur une deuxième ligne, à droite mais en
     dessous. Les deux reçoivent donc la même largeur et la même marge. */
  /* LE SÉLECTEUR DE LANGUE EST POSÉ DANS LE BANDEAU, dans son angle bas-droit,
     par-dessus l'herbe. `zone_ruban` devient le repère de position ; sans
     cela le bloc se placerait par rapport à la fenêtre et glisserait au
     défilement. */
  div[class*="st-key-zone_ruban"] { position: relative; }
  /* LES DEUX COLONNES PARTENT DU MÊME BORD HAUT, et c'est le bandeau qui
     ouvre celle de droite. Le filet de blanc qui le séparait du contenu est
     porté par son propre conteneur : sur les pages sans illustration, la
     colonne de droite commence donc au même pixel que le menu. */
  div[class*="st-key-zone_page"] { margin-top: 0 !important; }
  div[class*="st-key-zone_ruban"] { margin: 0 0 14px !important; }
  /* LE SÉLECTEUR OUVRE LA COLONNE DE MENU. Il était posé en absolu dans
     l'angle du bandeau ; le bandeau ne paraît plus que sur l'accueil, et un
     réglage qui change de place selon la page n'est plus un réglage. Il
     prend donc sa place dans le flux, en tête de la colonne, séparé de la
     première rubrique par un filet — au-dessus de la table des matières,
     sans en faire partie. */
  div[class*="st-key-zone_langue"] {
    width: auto !important; margin: 2px 0 10px 2px !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid #edecea !important;
  }
  /* LE GLOBE, PEINT EN MASQUE DEVANT LES DEUX CODES. On ne peut rien écrire
     dans le contenu d'un bouton Streamlit ; le tracé est donc posé en
     `::before` sur le conteneur, où il devient une case de la rangée. */
  div[class*="st-key-zone_langue"]::before {
    content: ""; width: 15px; height: 15px; flex: 0 0 15px;
    margin-right: 9px; background-color: #6b7590;
    -webkit-mask: MASQUE center/contain no-repeat;
    mask: MASQUE center/contain no-repeat;
  }
  /* Streamlit donne au conteneur du bouton la largeur de son mot : sans ces
     deux lignes, le `width:100%` du bouton vaut 100 % de vingt-cinq pixels,
     et la pastille se ferme en rond. La classe à clé est posée SUR le
     conteneur d'élément, pas sur un parent : elle se sélectionne donc
     directement. */
  /* DEUX MOTS EN BLANC, PAS DEUX PASTILLES. Une pastille est un bouton
     d'action ; la langue n'est pas une action, c'est un état du site. Posés
     sur l'herbe du bandeau, les deux codes sont blancs, et une ombre portée
     les détache là où le vert passe clair — une plaque translucide, elle,
     découperait un rectangle net dans la photographie. */
  div[class*="st-key-lang_"],
  div[class*="st-key-lang_"] div[data-testid="stButton"] {
    width: auto !important;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button,
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] {
    background: transparent !important;
    border: none !important; border-radius: 0 !important;
    box-shadow: none !important; padding: 2px 4px !important;
    min-height: 0 !important; height: auto !important; width: auto !important;
    justify-content: flex-start !important; transform: none !important;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button p {
    font-size: 11.5px !important; font-weight: 600 !important;
    letter-spacing: .08em !important; text-transform: uppercase;
    color: #6b7590 !important; text-align: left !important;
    transition: color .15s ease;
  }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button:hover { background: transparent !important; }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button:hover p { color: #1a6b52 !important; }
  div[class*="st-key-lang_"]
  div[data-testid="stButton"] > button[kind="primary"] p {
    color: #1a6b52 !important; font-weight: 800 !important;
  }
  div[class*="st-key-zone_langue"] div[data-testid="stColumn"]:last-child
  div[class*="st-key-lang_"] { position: relative; padding-left: 13px; }
  div[class*="st-key-zone_langue"] div[data-testid="stColumn"]:last-child
  div[class*="st-key-lang_"]::before {
    content: "/"; position: absolute; left: 2px; top: 2px;
    font-size: 11.5px; color: #b6bdc9;
  }
  div[class*="st-key-zone_langue"] {
    display: flex !important; flex-direction: row !important;
    align-items: center !important;
  }
  div[class*="st-key-zone_langue"] div[data-testid="stElementContainer"],
  div[class*="st-key-zone_langue"] div[data-testid="stHorizontalBlock"] {
    padding: 0; margin: 0; max-width: 96px; gap: 0 !important;
    flex-wrap: nowrap !important; width: auto !important;
  }
  div[class*="st-key-zone_langue"] div[data-testid="stColumn"] {
    width: auto !important; flex: 0 0 auto !important; min-width: 0 !important;
  }

  /* La ligne de contexte, sous le ruban : la page courante à gauche, ce sur
     quoi porte l'affichage à droite. Un chiffre lu sans savoir qu'un filtre
     est posé est un chiffre mal lu. */
  .bh-contexte {
    display: flex; align-items: center; justify-content: flex-start;
    gap: 16px; flex-wrap: wrap; margin: 12px 0 10px;
  }
  /* Sans ligne de contenu, le bandeau collerait au titre de la page. */
  .bh-vide { height: 20px; }
  .bh-page {
    font-size: 15px; font-weight: 700; color: #101728;
    letter-spacing: -.01em;
  }
  .bh-filtre {
    font-size: 12px; color: #1f7a5a; font-weight: 600;
    background: #eaf6f0; border: 1px solid #cfe9dd; border-radius: 999px;
    padding: 5px 14px;
  }

  /* ================= les cartes des six dimensions ======================
     Le sélecteur de dimension de « Analyse des résultats ». Chaque carte porte
     le nom de la dimension et une ligne qui dit ce qu'on y trouve — comme sur
     une couverture de dossier. La carte courante prend un aplat plein ; les
     autres restent blanches, avec un filet et une ombre légère qui se
     renforcent au survol.

     Le libellé du bouton contient deux lignes séparées par un saut : Streamlit
     les rend dans un même paragraphe, d'où `white-space: pre-line` — sans lui,
     le saut serait avalé et les deux lignes se colleraient. */
  /* ================= justification du texte courant ====================
     Les paragraphes du contenu sont justifies : sur une colonne bornee a
     1240 px, un bord droit en dents de scie hache la lecture, et le site
     est fait de blocs de prose autant que de chiffres.

     CE QUI EN EST EXCLU, ET POURQUOI : les libelles de bouton (justifier
     deux mots ecarte les lettres), les legendes sous les figures (deux
     lignes justifiees creusent des rivieres blanches), et les cellules de
     tableau (leur alignement porte un sens — les nombres a droite). */
  /* LA JUSTIFICATION EST POSÉE SUR LE CONTENEUR, PAS SUR LES PARAGRAPHES.
     Visée sur `p` et `li`, elle laissait de côté tout ce que les pages
     injectent en HTML — les encadrés, les cartes, les fiches — dont le texte
     vit dans des `div` et des `span`. Posée sur le conteneur, elle descend
     par héritage dans tout ce qui n'a pas d'alignement à lui, et les
     alignements explicites, un nombre calé à droite, un intitulé centré,
     gardent le dessus sans qu'on ait à les rappeler un par un. */
  section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] {
    text-align: justify; text-justify: inter-word; hyphens: auto;
  }
  section[data-testid="stMain"] div[data-testid="stButton"] p,
  section[data-testid="stMain"] div[data-testid="stCaptionContainer"] p,
  section[data-testid="stMain"] table p,
  section[data-testid="stMain"] td p, section[data-testid="stMain"] th p {
    text-align: inherit; hyphens: none;
  }
  section[data-testid="stMain"] div[data-testid="stButton"] p {
    text-align: left;
  }
  .cartes-ancre { display: none; }
  /* UN TRAIT SOUS LES SIX CARTES. Sans lui, la rangée de dimensions et le
     titre de la dimension ouverte se touchaient : on ne voyait pas où
     finissait le choix et où commençait le résultat. Le filet ferme le
     sélecteur, comme le bord bas d'une rangée d'onglets. */
  .cartes-trait {
    height: 1px; background: linear-gradient(90deg, #d7e0ec 0%,
      #e6ecf4 55%, rgba(230,236,244,0) 100%);
    margin: 18px 0 4px;
  }

  /* Les cartes sont visées par leur CLÉ : Streamlit pose une classe
     « st-key-<clé> » sur le conteneur de chaque widget. C'est la seule
     accroche stable — viser « tous les boutons de cette rangée » attraperait
     aussi ceux des pages rendues en dessous. */
  div[class*="st-key-carte_dim"] > div > button {
    display: flex !important; flex-direction: column !important;
    align-items: flex-start !important; justify-content: flex-start !important;
    text-align: left !important; white-space: pre-line !important;
    width: 100% !important; min-height: 104px !important; height: 100% !important;
    padding: 15px 17px !important; border-radius: 14px !important;
    background: #ffffff !important; border: 1px solid #e3eaf3 !important;
    color: #101728 !important;
    font-size: 14.5px !important; font-weight: 700 !important;
    line-height: 1.3 !important; letter-spacing: -.01em !important;
    box-shadow: 0 1px 2px rgba(16,23,40,.05) !important;
    transition: box-shadow .15s ease, transform .15s ease,
                border-color .15s ease !important;
  }
  div[class*="st-key-carte_dim"] > div > button:hover {
    border-color: #c3ded0 !important;
    box-shadow: 0 3px 6px rgba(16,23,40,.07),
                0 14px 30px rgba(16,23,40,.10) !important;
    transform: translateY(-2px) !important;
  }
  /* Le libellé porte le titre en gras markdown et la ligne descriptive en
     texte simple. Streamlit les rend dans un même paragraphe : le titre
     devient un <strong>, ce qui suffit à les habiller séparément.
     (Le premier essai passait par ::first-line — mais ce pseudo-élément vise
     la première ligne VISUELLE, si bien que le début du sous-titre héritait
     du gras dès que le titre tenait sur une seule ligne.) */
  div[class*="st-key-carte_dim"] > div > button p {
    font-size: 11.5px !important; font-weight: 400 !important;
    color: #6b7590 !important; line-height: 1.45 !important;
    text-align: left !important; margin: 0 !important;
  }
  div[class*="st-key-carte_dim"] > div > button p strong {
    display: block; margin-bottom: 7px;
    font-size: 14.5px; font-weight: 700; color: #101728;
    line-height: 1.3; letter-spacing: -.01em;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] {
    background: #1c6349 !important; border-color: #1c6349 !important;
    box-shadow: 0 3px 8px rgba(28,99,73,.28) !important;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] p {
    color: rgba(255,255,255,.84) !important;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"] p strong {
    color: #ffffff;
  }
  div[class*="st-key-carte_dim"] > div > button[kind="primary"]:hover {
    background: #237556 !important; border-color: #237556 !important;
  }

  /* --- le panneau des dernières livraisons ---------------------------- */
  .n-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 11px 0 3px;
  }
  .n-icone {
    flex: 0 0 34px; width: 34px; height: 34px; border-radius: 9px;
    background: #eaf6f0; color: #1f7a5a; font-size: 14.5px;
    display: flex; align-items: center; justify-content: center;
  }
  .n-corps { flex: 1 1 auto; min-width: 0; }
  .n-titre {
    font-size: 13.5px; font-weight: 700; color: #101728; line-height: 1.35;
  }
  .n-badge {
    display: inline-block; margin-left: 7px; vertical-align: middle;
    background: #eaf6f0; color: #1f7a5a; border: 1px solid #cfe9dd;
    border-radius: 999px; padding: 1px 8px;
    font-size: 10px; font-weight: 700; letter-spacing: .06em;
    text-transform: uppercase;
  }
  .n-texte {
    font-size: 12px; color: #6b7590; line-height: 1.5; margin-top: 3px;
  }

  /* --- sous-onglets : mêmes codes que les tuiles d'entrée, en compact ---
     Les onglets natifs de Streamlit sont un soulignement discret ; à dix
     entrées, on ne voit plus lesquelles sont cliquables. On leur donne la
     forme des tuiles principales — bordure, relief, sélection pleine — pour
     qu'un sous-onglet se lise comme une navigation et non comme un titre. */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px; flex-wrap: wrap; border-bottom: none; margin-bottom: 6px;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] {
    background: var(--carte); border: 1.5px solid var(--bord);
    border-radius: 12px; padding: 9px 16px; height: auto;
    box-shadow: 0 1px 2px rgba(16,23,40,.04);
    transition: transform .16s cubic-bezier(.2,.7,.3,1), box-shadow .16s ease,
                background .16s ease, border-color .16s ease;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] p {
    font-family: "Inter", system-ui, sans-serif !important;
    font-size: 14px !important; font-weight: 600 !important;
    color: var(--encre-2) !important; margin: 0;
  }
  .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"]:hover {
    transform: translateY(-2px); border-color: #b6d8c6; background: #f2f9f5;
    box-shadow: 0 2px 5px rgba(16,23,40,.07), 0 10px 22px rgba(16,23,40,.09);
  }
  .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #2b8663 0%, #1c6349 100%);
    border-color: transparent;
    box-shadow: 0 2px 6px rgba(28,99,73,.26), 0 10px 22px rgba(28,99,73,.20);
  }
  .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
    color: #ffffff !important;
  }
  .stTabs [data-baseweb="tab-highlight"],
  .stTabs [data-baseweb="tab-border"] { display: none; }

  /* --- les cartouches de chiffres se soulèvent aussi --- */
  .cartouche { transition: box-shadow .2s ease, transform .2s ease,
                           border-color .2s ease; }
  .cartouche:hover {
    transform: translateY(-3px) !important; border-color: #c3ded0 !important;
    box-shadow: 0 3px 6px rgba(16,23,40,.07), 0 18px 38px rgba(16,23,40,.13) !important;
  }
</style>
""").replace("__ICONE_RESET__", icones.regle_masque(
    'section[data-testid="stSidebar"] div[class*="st-key-f_reset_global"] '
    'div[data-testid="stButton"] > button', "rafraichir", 16, 10))
   # LE GLOBE DU SÉLECTEUR DE LANGUE. Le tracé est injecté ici plutôt
   # qu'écrit dans la feuille : il vient du même jeu d'icônes que le reste du
   # site, et une URL de données recopiée à la main dériverait du tracé.
   .replace("MASQUE", icones.masque("monde")),
    unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# APP.PY PORTE LES INTITULÉS DE SA PROPRE NAVIGATION.
#
# C'est le principe déjà appliqué à `questions_dimension.py`, et je ne l'avais
# pas suivi ici : les six noms de rubrique et les six lignes de carte vivaient
# dans `i18n.py` seul. Un `i18n.py` resté en arrière — ce qui arrive, les
# fichiers étant poussés à la main — et la page s'arrêtait sur « il manque des
# clés », alors que le fichier réellement neuf était app.py.
#
# DEUX TRAITEMENTS, ET LA DIFFÉRENCE COMPTE :
#   · les clés NOUVELLES (les lignes de carte) sont posées en setdefault — un
#     i18n.py à jour reste maître ;
#   · les clés RENOMMÉES (les six rubriques) sont ÉCRASÉES. Un setdefault ne
#     servirait à rien : la clé existe déjà dans l'ancien fichier, avec
#     l'ancien nom, et c'est précisément celui-là qu'il faut remplacer.
#
# `i18n.py` garde les mêmes valeurs et son rôle de catalogue complet.
# ---------------------------------------------------------------------------
TEXTES_NAV = {
    "mode_accueil": {"en": "The territory", "fr": "Le territoire"},
    "mode_methodo": {"en": "Resilience Framework",
                     "fr": "Cadre de résilience"},
    "mode_dimensions": {"en": "Results Analysis",
                        "fr": "Analyse des résultats"},
    "mode_synthese": {"en": "Territorial and Social Profiles",
                      "fr": "Profils territoriaux et sociaux"},
    "mode_actions": {"en": "Intervention Profiles",
                     "fr": "Fiches d'intervention"},
    "mode_donnees": {"en": "Data", "fr": "Données"},
    "dim1_carte": {
        "en": "Housing, water, sanitation, energy, roads, schools and health "
              "facilities",
        "fr": "Logement, eau, assainissement, énergie, routes, écoles et "
              "centres de santé"},
    "dim2_carte": {
        "en": "Civil registration, governance, early warning, disaster "
              "preparedness, participation",
        "fr": "État civil, gouvernance, alerte précoce, préparation aux "
              "catastrophes, participation"},
    "dim3_carte": {
        "en": "Forest cover, rainfall, vegetation, surface temperature and "
              "aridity, by satellite",
        "fr": "Couvert forestier, pluie, végétation, température de surface "
              "et aridité, par satellite"},
    "dim4_carte": {
        "en": "Employment, income, savings and credit, farming, fishing, "
              "food security",
        "fr": "Emploi, revenus, épargne et crédit, agriculture, pêche, "
              "sécurité alimentaire"},
    "dim5_carte": {
        "en": "Social capital, mutual aid, community organisations and their "
              "reach",
        "fr": "Capital social, entraide, organisations communautaires et "
              "leur portée"},
    "dim6_carte": {
        "en": "Education, health, support networks and access to essential "
              "services",
        "fr": "Éducation, santé, réseaux de soutien et accès aux services "
              "essentiels"},
    "mode_boucles": {"en": "Feedback Loops", "fr": "Boucles de rétroaction"},
    "mode_radar": {"en": "Resilience Radar",
                   "fr": "Diagramme radar de résilience"},
    "mode_croisement": {"en": "Cross-tabulation of results",
                        "fr": "Croisement des résultats"},
    "mode_fiche": {"en": "Landscape synthesis sheet",
                   "fr": "Fiche synthèse, paysages"},
    # Les trois onglets de « Profils territoriaux et sociaux », qui ont
    # absorbé le radar et la fiche paysages.
    "syn_o_profils": {"en": "By territory or group",
                      "fr": "Par territoire ou par groupe"},
    "syn_o_paysages": {"en": "Coast against mountain",
                       "fr": "Littoral contre montagne"},
    "syn_o_radar": {"en": "Resilience radar",
                    "fr": "Diagramme radar"},
    # Les deux lectures du graphe causal : l'onde, puis l'analyse.
    "bcl_vue_analyse": {"en": "Loops, levers, total effect",
                        "fr": "Boucles, leviers, effet total"},
    # « NOTE AUX BAILLEURS » EST DEVENU « ENSEIGNEMENTS CLÉS ». Le titre disait
    # à qui la page s'adresse ; celui-ci dit ce qu'on y trouve, ce qui est le
    # seul renseignement utile à quelqu'un qui parcourt un menu. La page
    # elle-même n'a pas bougé d'une ligne.
    "mode_bailleurs": {"en": "Key Lessons", "fr": "Enseignements clés"},
    # LES SIX VUES D'« ANALYSE DES RÉSULTATS », dans l'ordre de la lecture :
    # ce que les gens ont répondu, ce que le référentiel en fait, puis trois
    # façons de chercher les écarts, puis ce qu'on peut y faire.
    #
    # « PAR DIMENSION » N'EST PLUS UN ONGLET. Ce n'est pas une façon de
    # regarder les résultats à côté des autres : c'est la structure du score
    # lui-même. Elle est donc rangée là où le score se lit, dans le second
    # onglet, sous son propre sélecteur.
    #
    # « ENSEIGNEMENTS CLÉS » A ÉTÉ RETIRÉ de la rangée : une note de
    # restitution n'est pas une lecture des résultats, c'est un texte sur
    # eux.
    "ra_o_brut": {"en": "Raw Results", "fr": "Résultats bruts"},
    "ra_o_scores": {"en": "Resilience Scores",
                    "fr": "Scores de résilience"},
    "ra_o_indic": {"en": "By Indicator", "fr": "Par indicateur"},
    "ra_o_paysage": {"en": "By Landscape", "fr": "Par paysage"},
    "ra_o_groupe": {"en": "By Social Group", "fr": "Par groupe social"},
    # L'ONGLET NE PROPOSE PLUS DES SOLUTIONS, IL DÉSIGNE DES CIBLES. Une
    # piste d'action lue avant d'avoir nommé la variable qui décroche est une
    # opinion ; nommer la variable, c'est le point de départ des boucles.
    "sx_deplier_syst": {
        "en": "Open the interactive system — hold variables and watch it settle",
        "fr": "Ouvrir le système interactif — tenir des variables et le "
              "regarder se poser"},
    # LA DESCRIPTION DE CHAQUE ONGLET, une ligne, sous son titre. Elle dit ce
    # qu'on y trouve plutôt que comment ça s'appelle : « Par paysage » oblige
    # à cliquer pour savoir, « ce qui distingue un paysage du reste » laisse
    # choisir depuis la barre.
    "ra_d_brut": {
        "en": "What households answered and satellites measured",
        "fr": "Ce que les ménages ont répondu et ce que les satellites ont "
              "mesuré"},
    "ra_d_scores": {
        "en": "The 0–10 index, on any combination of groups",
        "fr": "L'indice sur 10, sur n'importe quelle combinaison de groupes"},
    "ra_d_indic": {
        "en": "One indicator, read across the whole territory",
        "fr": "Un indicateur, lu à travers tout le territoire"},
    "ra_d_paysage": {
        "en": "What sets a landscape apart from the rest",
        "fr": "Ce qui distingue un paysage du reste"},
    "ra_d_groupe": {
        "en": "What sets a social group apart from the rest",
        "fr": "Ce qui distingue un groupe social du reste"},
    "ra_d_solutions": {
        "en": "Where to start, and why there rather than elsewhere",
        "fr": "Par où commencer, et pourquoi là plutôt qu'ailleurs"},
    "sx_d1": {"en": "A critical variable, and the system around it",
              "fr": "Une variable critique, et le système autour d'elle"},
    "sx_d2": {"en": "Correlation, mechanism and evidence, kept apart",
              "fr": "Corrélation, mécanisme et preuve, tenus séparés"},
    "sx_d3": {"en": "Where a push travels furthest",
              "fr": "Où une poussée voyage le plus loin"},
    "sx_d4": {"en": "Push several variables at once",
              "fr": "Pousser plusieurs variables à la fois"},
    "sx_d5": {"en": "Wave after wave, and what the loops add",
              "fr": "Vague après vague, et ce que les boucles ajoutent"},
    "sx_d6": {"en": "Push a variable and watch the system move, live",
              "fr": "Poussez une variable et regardez le système bouger, "
                    "en direct"},
    "ra_srcd_menages": {"en": "1,211 households, 483 questions",
                        "fr": "1 211 ménages, 483 questions"},
    "ra_srcd_satellite": {"en": "Forest cover and vegetation indices",
                          "fr": "Couverture forestière et indices de "
                                "végétation"},
    "ra_srcd_institutions": {
        "en": "Communal authorities, services and local organisations",
        "fr": "Autorités communales, services et organisations locales"},
    "ra_srcd_biodiversite": {
        "en": "Field inventories of species and habitats",
        "fr": "Inventaires de terrain, espèces et habitats"},
    # L'ONGLET EXISTE AVANT SES DONNÉES, ET C'EST VOULU. Les deux enquêtes
    # ont été menées ; leurs fichiers ne sont pas encore versés sur la
    # plateforme. Un onglet qui annonce l'attente vaut mieux qu'un onglet
    # absent : le lecteur sait que la mesure existe, et il sait qu'il la
    # trouvera ici. Rien n'est inventé en attendant.
    "ra_attente_t": {"en": "Data not yet loaded",
                     "fr": "Données pas encore versées"},
    "ra_attente_inst": {
        "en": "The institutional survey has been carried out. Its answers "
              "are being cleaned and coded, and will be published on this "
              "page as soon as they are loaded onto the platform.",
        "fr": "L'enquête institutionnelle a été réalisée. Ses réponses sont "
              "en cours d'apurement et de codage ; elles seront publiées sur "
              "cette page dès leur versement sur la plateforme."},
    "ra_attente_bio": {
        "en": "The biodiversity survey has been carried out. Its inventories "
              "are being consolidated and will be published on this page as "
              "soon as they are loaded onto the platform.",
        "fr": "L'enquête biodiversité a été réalisée. Ses inventaires sont "
              "en cours de consolidation ; ils seront publiés sur cette page "
              "dès leur versement sur la plateforme."},

    # --- les quatre familles de la colonne de menu
    "nav_g_comprendre": {"en": "Understand", "fr": "Comprendre"},
    "nav_g_analyser": {"en": "Analyse", "fr": "Analyser"},
    "nav_g_agir": {"en": "Act", "fr": "Agir"},
    "nav_g_ressources": {"en": "Resources", "fr": "Ressources"},

    # --- le pied de page
    "pied_devise": {
        "en": "Measuring today to strengthen tomorrow's resilience.",
        "fr": "Mesurer aujourd'hui pour renforcer la résilience de demain."},
    "pied_credit": {
        "en": "© {a} United Nations Environment Programme",
        "fr": "© {a} Programme des Nations Unies pour l'environnement"},

    "ra_src": {"en": "Measured by", "fr": "Mesuré par"},
    "ra_e1_t": {"en": "Select your data source",
                "fr": "Choisissez votre source de données"},
    "ra_src_menages": {"en": "Household survey",
                       "fr": "Enquête ménage"},
    "ra_src_satellite": {"en": "Satellite", "fr": "Satellite"},
    "ra_src_institutions": {"en": "Institutional survey",
                            "fr": "Enquête institutionnelle"},
    "ra_src_biodiversite": {"en": "Biodiversity survey",
                            "fr": "Enquête biodiversité"},
    "ra_o_solutions": {"en": "Most alarming variables",
                       "fr": "Variables les plus alarmantes"},
    "mode_levier": {"en": "If I change one thing",
                    "fr": "Si je change une chose"},
    # LE RAPPORT ET LA NOTE NE FONT PAS LE MÊME MÉTIER. La note tient sur une
    # page et se cite ; le rapport se lit en six chapitres et raconte ce que
    # l'argent a produit comme connaissance. L'un est un extrait, l'autre le
    # récit dont il est extrait.
    "mode_rapport": {"en": "Donor report", "fr": "Rapport donateur"},
    "nav_titre": {"en": "Navigation", "fr": "Navigation"},
    "nav_filtres_rapides": {"en": "Quick filters", "fr": "Filtres rapides"},
    "f_reinit_long": {"en": "Reset the filters",
                      "fr": "Réinitialiser les filtres"},
    "f_groupe_long": {"en": "Respondent group", "fr": "Groupe de répondants"},
    "f_auto": {
        "en": "Results update automatically as you change the filters.",
        "fr": "Les résultats se mettent à jour automatiquement selon vos "
              "filtres."},
}
# Les sept rubriques : app.py est la source, puisqu'il est le seul à s'en servir
# et qu'il est toujours du voyage.
_RENOMMEES = ("mode_accueil", "mode_methodo", "mode_dimensions",
              "mode_synthese", "mode_actions", "mode_donnees",
              "mode_boucles", "mode_croisement", "mode_rapport",
              "mode_levier", "mode_bailleurs", "ra_o_brut", "ra_o_scores",
              "ra_o_indic", "ra_o_paysage", "ra_o_groupe", "ra_o_solutions")
for _c, _v in TEXTES_NAV.items():
    if _c in _RENOMMEES:
        i18n.DICO[_c] = _v
    else:
        i18n.DICO.setdefault(_c, _v)


# ----------------------------------------------------------------------
# Garde-fou : les fichiers sont poussés à la main sur GitHub, un par un. Si le
# dictionnaire de traduction est resté sur une version antérieure, l'application
# ne plante pas — elle affiche le nom des clés manquantes au milieu du texte, ce
# qui est beaucoup plus déroutant qu'une erreur franche. On préfère le dire.
# ----------------------------------------------------------------------
I18N_ATTENDU = "2026-08-18-cadre"

# CE QUI EST VÉRIFIÉ, C'EST LA PRÉSENCE DES CLÉS, PAS LA DATE.
#
# La première version du garde-fou comparait `i18n.VERSION` à la date attendue,
# et arrêtait l'application au moindre écart. C'était trop strict : une mise à
# jour qui ne touche qu'à la mise en page bloquait tout le site alors que rien
# n'était cassé, et le message envoyait renvoyer un fichier de 230 ko sans
# raison. Ce faux positif a coûté plus de temps que la panne qu'il prévient.
#
# Le vrai défaut à attraper est précis : une clé appelée par le code manque du
# dictionnaire, et son NOM s'affiche à la place du texte. C'est donc cela qu'on
# teste — les clés introduites par les mises à jour récentes. Manquantes, on
# arrête franchement ; présentes, on se tait, quelle que soit la date.
I18N_CLES_REQUISES = [
    "a_lieu", "a_titre_court", "a_localisation", "a_histoire",
    "a_h_origine", "a_h_mesure", "a_h_construction", "a_h_portee",
    "dim_sous_titre", "syn_sous_titre", "syn_intro",
    "f_paysage", "f_tous_paysages", "f_resume_paysage",
    "f_resume_section_pay", "f_resume_paysage_groupe", "f_incoherent",
    "s_mode_paysage", "s_note_paysage", "pay_Littoral", "pay_Montagne",
]
# Les textes de l'onglet « questions » ne figurent PAS dans cette liste, bien
# qu'ils soient nouveaux : `questions_dimension.py` les porte lui-même et les
# verse dans le dictionnaire à l'import, avant que ce contrôle ne s'exécute.
# C'est le principe qu'il faut suivre pour toute fonction nouvelle — un module
# qui apporte une fonction apporte ses textes — de sorte qu'un `i18n.py` resté
# en arrière ne puisse plus bloquer une page qui, elle, est complète.
_manquantes = [c for c in I18N_CLES_REQUISES if c not in getattr(i18n, "DICO", {})]
if _manquantes:
    st.error(
        f"**i18n.py n'est pas à jour** — il manque "
        f"{len(_manquantes)} clé(s) de traduction que le reste de "
        f"l'application appelle : `" + "`, `".join(_manquantes[:6]) + "`"
        + ("…" if len(_manquantes) > 6 else "") + ".\n\n"
        f"Version attendue `{I18N_ATTENDU}`, trouvée "
        f"`{getattr(i18n, 'VERSION', 'aucune')}`. Sans ces clés, les textes "
        f"s'affichent sous forme de noms (`mode_ocb`, `o_intro`…). Renvoyer "
        f"sur GitHub le `i18n.py` livré avec cette mise à jour, à la racine du "
        f"dépôt, corrige l'affichage.\n\n"
        f"*i18n.py is missing translation keys — re-upload the version "
        f"delivered with this update to the repository root.*")
    # On ARRÊTE ici. L'application continuait autrefois de se dessiner avec des
    # noms de clés en guise de textes, et le message rouge se perdait au-dessus
    # d'une page qui semblait fonctionner — au point qu'on a pris plusieurs
    # fois l'affichage cassé pour un défaut de mise en page. Une page vide sous
    # un message franc est plus honnête qu'une page à moitié juste.
    st.stop()

st.markdown(map_render.styles_bulle(), unsafe_allow_html=True)

# ---- choix de la langue, avant tout le reste ---------------------------
# Le menu est l'unique source de vérité : on recopie simplement son état dans
# `lang`, que toutes les pages lisent. Pas de rerun forcé — Streamlit relance
# déjà le script quand le menu change, et le reste de la page est construit
# après cette ligne.
# La colonne se construit en trois conteneurs réservés d'avance : le choix de
# la langue doit être LU avant tout appel à T(), mais AFFICHÉ en bas de la
# barre. Les conteneurs gardent leur place dans la page pendant qu'on les
# remplit dans un autre ordre — sans eux, la langue s'afficherait au-dessus du
# logo, ce qui n'a aucun sens dans un menu.
# LA LANGUE EST MONTÉE EN TÊTE DE LA COLONNE, AU-DESSUS DE LA MARQUE.
# Elle occupait le ruban blanc du haut, qui n'existait que pour elle et pour
# le logo ; les deux étant partis — la langue ici, le logo sur la photo — le
# ruban a disparu et chaque page commence par son titre.
# LA COLONNE DE GAUCHE A DISPARU, ET AVEC ELLE LA MOITIÉ DE SON CONTENU.
# Elle portait quatre choses : la langue, la marque, la navigation et le
# rappel des filtres. Les deux premières sont montées dans le bandeau, où
# elles identifient le site au lieu de border le contenu. La navigation
# devient un menu déroulant sous le bandeau : douze entrées empilées le long
# d'une page pleine largeur, c'était une colonne de trois cents pixels
# occupée à répéter ce qu'un seul champ suffit à dire. Les filtres restent
# à côté du menu, puisque c'est la seule commande qu'on cherche depuis
# n'importe quelle page.
# L'ORDRE DE CRÉATION EST L'ORDRE D'AFFICHAGE. Le bandeau doit être
# réservé en premier : créé plus bas, il se dessinait sous le menu.
# LA NAVIGATION EST UNE BARRE HORIZONTALE, ET ELLE OUVRE LA PAGE.
# Elle occupait une colonne de gauche : un sixième de la largeur, sur toute la
# hauteur, pour quatorze mots. Le contenu — cartes, tableaux, graphiques —
# était comprimé d'autant, alors que c'est lui qu'on vient voir. En haut, sur
# une seule ligne qui se replie si besoin, elle rend l'écran entier à la page.
# LE MENU MONTE JUSQU'EN HAUT, ET LE BANDEAU SE RANGE À CÔTÉ DE LUI.
# Le bandeau tenait toute la largeur au-dessus des deux colonnes : la colonne
# de menu commençait alors deux cent cinquante pixels plus bas que le haut de
# l'écran, et l'on descendait pour atteindre la première rubrique d'un site
# dont l'en-tête, lui, ne dit rien qu'on ait à lire deux fois. Les deux
# colonnes partent maintenant du même bord haut : le menu à gauche,
# l'illustration en tête de la page, à sa droite.
# La colonne de menu est étroite et fixe ; la page prend tout le reste.
_col_nav, _col_page = st.columns([1, 5.0], gap="medium")
_zone_nav = _col_nav.container(key="zone_nav")
# LE BANDEAU EST DANS LA COLONNE DE DROITE, ET IL Y VIENT EN PREMIER : c'est
# l'ordre de création des conteneurs qui fixe l'ordre à l'écran, pas celui
# des appels qui les remplissent.
_ruban = _col_page.container(key="zone_ruban")
# Réservé maintenant, peint tout en bas : il doit venir après les deux
# colonnes dans le flux, et son contenu n'est connu qu'une fois la page rendue.
_pied = st.container(key="zone_pied")
_zone_barre = st.container()

# LA LANGUE EST LUE ICI, AVANT TOUT APPEL À T(), ET CHANGÉE DANS LE BANDEAU.
# Le menu déroulant de la colonne de gauche a disparu : deux mots côte à côte
# se lisent et se cliquent d'un seul geste, là où un menu demandait d'ouvrir,
# viser, choisir. Le bouton n'écrit que dans l'état de session ; Streamlit
# relance le script derrière, et la langue est déjà bonne quand la première
# ligne de texte se dessine.
st.session_state.setdefault("choix_langue", i18n.DEFAUT)
i18n.set_lang(st.session_state["choix_langue"])


def _changer_langue(code):
    st.session_state["choix_langue"] = code

# ---- bandeau : logo PNUE + les deux entrées du tableau de bord ----------
# Le mode est stocké sous un code stable, pas sous son libellé : sinon un
# changement de langue laisserait dans la session une valeur qui ne correspond
# plus à aucun mode.
# Dix entrées : les six dimensions du cadre APRI, puis la méthode, les
# données, les fiches actions et la synthèse. La septième dimension du cadre —
# culturelle, identitaire et psychologique — n'a aucun indicateur calculé et
# n'a donc pas d'onglet ; elle reste listée dans la méthodologie, pour qu'une
# absence ne passe pas pour une inexistence.
MODE_ACCUEIL = "accueil"
MODES_DIM = ["dim1", "dim2", "dim3", "dim4", "dim5", "dim6"]
MODE_METHODO, MODE_DONNEES = "methodologie", "donnees"
MODE_ACTIONS = "actions"
MODE_SYNTHESE = "synthese"
MODE_BOUCLES = "boucles"
MODE_CROISEMENT = "croisement"
MODE_BAILLEURS = "bailleurs"
MODE_RAPPORT = "rapport"
MODE_LEVIER = "levier"
# LA PAGE D'ACCUEIL, ET C'EST ELLE QUI OUVRE LE SITE. On arrivait jusqu'ici
# sur le cadre méthodologique : avant d'apprendre quoi que ce soit du
# territoire, on apprenait comment on le mesure. C'est l'ordre d'un rapport,
# pas celui d'un tableau de bord.
MODE_PORTAIL = "portail"
# LE TEMPS, ENFIN MONTRÉ COMME DU TEMPS. Trois jeux satellitaires sont des
# séries — la forêt depuis 2000, la pluie depuis 1981, la température depuis
# 2001 — et le site les lisait comme des instantanés.
MODE_TRAJECTOIRES = "trajectoires"
LIBELLE_MODE = {m: T(m) for m in MODES_DIM}
LIBELLE_MODE.update({MODE_ACCUEIL: T("mode_accueil"),
                     "dimensions": T("mode_dimensions"),
                     MODE_METHODO: T("mode_methodo"),
                     MODE_DONNEES: T("mode_donnees"),
                     MODE_ACTIONS: T("mode_actions"),
                     MODE_BOUCLES: T("mode_boucles"),
                     MODE_SYNTHESE: T("mode_synthese"),
                     MODE_CROISEMENT: T("mode_croisement"),
                     MODE_BAILLEURS: T("mode_bailleurs"),
                     MODE_RAPPORT: T("mode_rapport"),
                     MODE_LEVIER: T("mode_levier"),
                     MODE_PORTAIL: T("mode_portail"),
                     MODE_TRAJECTOIRES: T("mode_trajectoires")})

# L'état de navigation doit exister AVANT la barre du haut, qui affiche le nom
# de la page courante. L'initialiser plus bas laissait la barre lire une clé
# absente — et Streamlit lève alors une erreur qui masque toute la page.
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = MODE_PORTAIL


def _bascule(mode):
    st.session_state["app_mode"] = mode


# L'identité APRI vit maintenant dans la barre latérale : la répéter en haut
# du contenu volerait un tiers d'écran avant le premier chiffre. Il reste ici
# une ligne institutionnelle — le commanditaire et le titre long, qu'une
# capture d'écran doit porter avec elle — et le bandeau, réduit de moitié pour
# rester un décor.
# Un SEUL bloc HTML : Streamlit isole chaque appel à st.markdown dans son
# propre conteneur, si bien qu'une balise ouverte dans l'un et fermée dans le
# suivant ne s'emboîte jamais — le style se perd sans qu'aucune erreur ne le
# signale.
# La barre du haut : à gauche le commanditaire et la page courante, à droite ce
# sur quoi porte l'affichage — un chiffre lu sans savoir qu'un filtre est posé
# est un chiffre mal lu.
# Plus aucun logo ici. Les deux marques sont réunies dans la colonne de gauche —
# APRI en tête, le PNUE en pied — et le contenu des pages n'en porte aucun : un
# logo répété à chaque en-tête mange la place du titre sans rien apprendre à
# personne, puisqu'il est déjà à l'écran en permanence.

# Les deux entrées sont mises au même niveau, en haut de page : ce sont deux
# lectures différentes de la même enquête, pas un mode principal et une option.
# Deux grands pavés cliquables plutôt qu'un bouton radio : l'entrée dans le
# tableau de bord doit se voir de loin.


# Trois entrées d'analyse sur la première rangée, les deux entrées documentaires
# sur la seconde : cinq pavés d'affilée deviendraient trop étroits pour que
# leur intitulé reste lisible.
# La navigation vit dans la barre latérale, groupée : l'entrée générale, les
# six dimensions du cadre, puis ce qui sert à agir et à vérifier. Onze entrées
# en pavés sur la page occupaient un écran entier avant le premier chiffre ;
# en colonne fixe, elles tiennent sans rien pousser vers le bas, et l'onglet
# courant reste visible où qu'on soit dans la page.
# Six entrées seulement dans la colonne. Les six dimensions n'y sont PAS :
# elles forment une famille homogène qu'on parcourt en comparant, et une
# rangée d'onglets se parcourt du regard alors qu'une liste verticale se lit
# une ligne après l'autre. Elles vivent donc sous l'entrée « Les six
# dimensions », en onglets, comme avant la refonte.
MODE_DIMENSIONS = "dimensions"
# L'ORDRE EST CELUI DE LA LECTURE, pas celui de la fabrication : on découvre le
# territoire (vue d'ensemble), on apprend ce qu'on mesure et comment (cadre de
# résilience), on lit les résultats par dimension, on compare les territoires
# et les groupes, on passe à l'action, et les données brutes ferment la marche
# pour qui veut refaire les calculs.
# L'ORDRE A CHANGÉ : le cadre de résilience ouvre la marche, le territoire
# vient juste après. On dit d'abord ce qu'on mesure, puis où on l'a mesuré ;
# les résultats suivent. L'accueil, devenu « Le territoire », n'a plus à porter
# le récit de la méthode, qui est passé dans le cadre.
# LE MENU EST RANGÉ EN QUATRE FAMILLES, ET C'EST UNE AIDE À LA DÉCISION, PAS
# UNE DÉCORATION. Sept entrées à la file se lisent comme sept choix
# équivalents, alors qu'elles n'en sont pas : on vient comprendre, ou
# analyser, ou agir, ou chercher un fichier. Le titre de famille dit lequel
# des quatre on est en train de faire, et il divise par quatre la liste où
# l'œil doit chercher.
#
# L'ACCUEIL N'A PAS DE FAMILLE, et il ne doit pas en avoir une : il est le
# point d'où l'on part, pas une des choses qu'on y fait.
_NAV_FAMILLES = [
    (None, [(MODE_PORTAIL, "maison")]),
    # LE CADRE PASSE DEVANT LE TERRITOIRE. On dit d'abord ce qu'on mesure,
    # ensuite où on l'a mesuré : une carte de dix sections ne dit rien tant
    # qu'on ne sait pas ce qui y est compté, alors que la définition de
    # l'indice se lit sans connaître le terrain.
    ("nav_g_comprendre", [(MODE_METHODO, "bouclier"),
                          (MODE_ACCUEIL, "epingle")]),
    ("nav_g_analyser", [(MODE_DIMENSIONS, "barres"),
                        (MODE_BOUCLES, "boucle")]),
    ("nav_g_agir", [(MODE_ACTIONS, "fiche")]),
    ("nav_g_ressources", [(MODE_DONNEES, "telecharger")]),
]
# LA LISTE PLATE RESTE LA SOURCE UNIQUE dont d'autres vues se servent — elle
# est dérivée des familles, jamais recopiée à côté d'elles : deux listes des
# mêmes rubriques divergent au premier ajout.
# LES TRAJECTOIRES, « SI JE CHANGE UNE CHOSE », LE CROISEMENT, LES PROFILS,
# LES ENSEIGNEMENTS ET LE RAPPORT DONATEUR NE SONT PLUS DES ENTRÉES : ils sont
# devenus des vues à l'intérieur des rubriques qui les portent. Leurs codes de
# mode restent valides, et rien ne les rend depuis le menu.
_NAV = [e for _fam, entrees in _NAV_FAMILLES for e in entrees]

# LES ICÔNES REVIENNENT, PARCE QUE LA COLONNE A CHANGÉ DE FORME. Alignées dans
# une rangée horizontale, elles meublaient : le libellé était juste à côté et
# disait la même chose. Dans une colonne rangée en familles, elles font un
# travail que le texte ne fait pas — elles donnent à chaque ligne une amorce
# à hauteur constante, ce qui permet de descendre la liste sans lire, et de
# reconnaître une rubrique déjà visitée à sa forme.
#
# ELLES SONT PEINTES EN MASQUE, PAS INSÉRÉES DANS LE BOUTON. On ne peut rien
# écrire dans le contenu d'un bouton Streamlit ; le tracé est donc posé en
# `::before` avec `currentColor`, si bien que l'icône prend la couleur du
# texte — verte quand la rubrique est active, grise sinon — sans une règle de
# plus par état.
_CSS_ICONES_NAV = "<style>" + "".join(
    icones.regle_masque(
        f'div[class*="st-key-nav_{_m}"] div[data-testid="stButton"] > button',
        _ic, taille=17, marge=10)
    for _m, _ic in _NAV) + "</style>"


def _entree_nav(mode, icone):
    actif = st.session_state["app_mode"] == mode
    st.button(LIBELLE_MODE[mode], key=f"nav_{mode}",
              on_click=_bascule, args=(mode,),
              type="primary" if actif else "secondary",
              use_container_width=True)


# ---------------------------------------------------------------- le ruban
# La m\u00eame navigation qu'\u00e0 gauche, en onglets horizontaux dans le ruban vert.
# DEUX CHEMINS VERS LES M\u00caMES PAGES, ET C'EST VOULU : la colonne se lit ligne
# \u00e0 ligne quand on cherche, le ruban se parcourt du regard quand on sait d\u00e9j\u00e0
# o\u00f9 l'on va. Ce qu'il ne faut surtout pas, c'est que les deux listes
# divergent \u2014 d'o\u00f9 la source unique `_NAV`, dont les deux se servent.
@st.cache_data(show_spinner=False)
def _bandeau_b64(lang="fr"):
    """L'illustration du bandeau, encodée une fois pour toutes.

    UNE COMPOSITION PAR LANGUE. Le titre et le sous-titre sont peints DANS
    l'image : un bandeau français en tête d'un site anglais afficherait
    « Observatoire de la résilience » au-dessus d'une page entièrement
    traduite. Le fichier anglais est cherché d'abord quand la langue servie
    est l'anglais ; s'il manque, le français reprend sa place plutôt que de
    laisser l'en-tête vide.

    Le fichier fait deux cent quarante kilo-octets : l'encoder à chaque
    réexécution de la page coûterait plus cher que de le garder en mémoire.
    """
    import base64 as _b64
    # LA VERSION RECADRÉE D'ABORD. Le fichier d'origine porte, sur son tiers
    # gauche, un aplat blanc pur qui avait été peint pour couvrir un logo
    # incrusté : ce tiers-là ne contient aucune image, et c'était le vide
    # qu'on voyait sous le titre. La version recadrée ne garde que la partie
    # qui porte le paysage. L'original reste en repli.
    # TROIS CHEMINS, DANS L'ORDRE DE PRÉFÉRENCE. Le bandeau composé d'abord —
    # celui qui porte déjà la marque, le titre et le logo du PNUE — puis les
    # versions nues, qui ne servent plus que de filet. Chacun cherché dans
    # `data/` puis à la racine : le dépôt déployé n'a pas toujours la même
    # arborescence que l'atelier.
    chemin = None
    # LE DESSIN PASSE DEVANT LA PHOTOGRAPHIE. La composition au crayon tient
    # sur le même blanc que la page et la colonne de menu : les trois se
    # lisent comme une seule feuille, là où la photographie posait un
    # rectangle de couleur en haut de l'écran. La photographie reste sous
    # `bandeau_apri_site.jpg` — retirer le dessin la remet en service.
    noms = ["bandeau_apri_dessin.jpg", "bandeau_apri_site.jpg",
            "bandeau_apri_large.jpg", "bandeau_apri.jpg"]
    if lang == "en":
        noms.insert(0, "bandeau_apri_dessin_en.jpg")
    for nom in noms:
        for base in (os.path.join(APP_DIR, "data"), APP_DIR):
            essai = os.path.join(base, nom)
            if os.path.exists(essai):
                chemin = essai
                break
        if chemin:
            break
    if not chemin:
        return None
    with open(chemin, "rb") as f:
        return _b64.b64encode(f.read()).decode()


def _rendre_ruban(avec_image):
    """Le bandeau composé, en tête de l'accueil.

    IL EST DÉJÀ COMPLET, ET ON N'Y AJOUTE RIEN. Le fichier porte la marque
    APRI, le filet, le titre, le sous-titre et le logo du PNUE : les
    superposer une seconde fois en CSS ferait dire deux fois chaque chose, et
    c'est exactement ce que faisaient la couche de titre et la réglette des
    pages intérieures. Elles sont retirées toutes les deux.

    IL N'EST PLUS QUE SUR L'ACCUEIL. Répété en tête des quinze pages, il
    prenait le quart de chaque écran pour redire à chaque fois de quel site
    il s'agit — une couverture qu'on relit à chaque chapitre. L'accueil la
    porte, les pages intérieures partent droit au contenu. Le sélecteur de
    langue, lui, reste partout : il vit dans le ruban et se pose dans le
    flux, à droite, dès que l'illustration n'est pas là pour l'accueillir.

    IL N'EST PAS ROGNÉ. Sa composition va du logo de gauche à celui de
    droite : `object-fit: cover` couperait l'un des deux dès que la fenêtre
    change de proportion. La hauteur suit donc la largeur, et rien ne sort.
    """
    with _ruban:
        img = _bandeau_b64(i18n.get_lang()) if avec_image else None
        if avec_image and not img:
            avec_image = False
        if not avec_image:
            return
        st.markdown(
            f'<div class="bandeau-haut bandeau-enveloppe">'
            f'<img class="bandeau-fond" alt="APRI" '
            f'src="data:image/jpeg;base64,{img}">'
            f'<img class="bandeau-logo" alt="UNEP" '
            f'src="data:image/png;base64,{assets.LOGO_UNEP_BLANC}">'
            f'</div>', unsafe_allow_html=True)


with _zone_nav:
    # LES ENTRÉES SE LISENT DE HAUT EN BAS, UNE PAR LIGNE.
    # Rien n'est replié derrière un déroulant et rien ne passe à la ligne :
    # la colonne se lit comme une table des matières, et la rubrique où l'on
    # se trouve s'y repère sans la chercher. `position: sticky` la garde à
    # l'écran quand la page défile — c'est ce qui la rend « toujours
    # disponible » sans qu'elle ait à flotter par-dessus le contenu.
    st.markdown(_CSS_ICONES_NAV, unsafe_allow_html=True)
    # LA LANGUE OUVRE LA COLONNE. Elle vivait dans l'angle du bandeau, qui
    # n'existe plus que sur l'accueil : sur les quinze autres pages, le
    # réglage se serait trouvé ailleurs qu'à l'endroit où on l'avait laissé.
    # En tête de la colonne, il est au même endroit partout, au-dessus de la
    # table des matières sans en faire partie — un réglage du site, pas une
    # destination.
    with st.container(key="zone_langue"):
        _cl = st.columns(2)
        # L'ORDRE SUIT LA LANGUE PAR DÉFAUT : la langue servie est en tête.
        _ordre = ("en", "fr") if i18n.DEFAUT == "en" else ("fr", "en")
        for _col, _code in zip(_cl, _ordre):
            with _col:
                st.button(_code.upper(), key=f"lang_{_code}",
                          on_click=_changer_langue, args=(_code,),
                          type=("primary"
                                if st.session_state["choix_langue"] == _code
                                else "secondary"))
    for _fam, _entrees in _NAV_FAMILLES:
        if _fam:
            st.markdown(f'<div class="nav-famille">{T(_fam)}</div>',
                        unsafe_allow_html=True)
        for _mode, _icone in _entrees:
            _entree_nav(_mode, _icone)

# LA PAGE OCCUPE LA COLONNE DE DROITE. Le conteneur est ouvert ici, avant
# l'aiguillage, pour que chaque page se dessine dedans sans avoir à savoir
# où elle est.
_c_contenu = _col_page.container(key="zone_page")

# Le ruban est peint maintenant, dans le conteneur réservé plus haut : il a
# besoin de la langue choisie et du résumé des filtres, tous deux fixés par
# la colonne de gauche qu'on vient de rendre.
_rendre_ruban(st.session_state["app_mode"] == MODE_PORTAIL)

app_mode = st.session_state["app_mode"]

# Les six onglets de dimension passent tous par le même module ; deux d'entre
# eux prolongent leur page avec un détail qui existait déjà, plutôt que d'en
# dupliquer la logique — l'environnement avec ses onze indicateurs
# satellitaires, le social avec les fiches d'organisations de base.
# TOUT L'AIGUILLAGE SE DESSINE DANS LA COLONNE DE DROITE.
# Chaque page reste écrite comme avant ; c'est le contexte qui change, en un
# seul endroit, plutôt que quarante modules qui devraient savoir où ils sont.
with _c_contenu:
    if app_mode == MODE_PORTAIL:
        # Quatre écrans : où, ce qu'on a mesuré, ce qu'on a trouvé, quoi faire.
        accueil_apri.render()

    if app_mode == MODE_ACCUEIL:
        territoire_page.render()

    if app_mode == MODE_DIMENSIONS:
        # QUATRE VUES SOUS UNE SEULE ENTRÉE, ET C'EST LA MÊME QUESTION.
        #
        #   · par dimension — les sept familles d'indicateurs, une à la fois ;
        #   · par croisement — deux variables l'une contre l'autre ;
        #   · par territoire ou par groupe — les profils comparés ;
        #   · les enseignements — ce qu'il faut retenir de tout cela.
        #
        # Elles étaient quatre entrées de menu voisines, ce qui laissait au
        # lecteur le soin de deviner qu'elles répondent à la même question.
        # Une seule entrée, quatre vues : la porte est unique, le découpage
        # se choisit après. Comme pour les boucles, un sélecteur plutôt que
        # `st.tabs` — seule la vue regardée est calculée.
        # LE SÉLECTEUR RETIENT UN CODE, PAS UN LIBELLÉ. Une valeur de session
        # égale au texte affiché change de langue avec lui : il faut alors une
        # clé par langue, et la vue choisie se perd au premier basculement.
        # `format_func` sépare ce qu'on stocke de ce qu'on montre.
        # LA BARRE PREND LE FORMAT DU CADRE DE RÉSILIENCE : numéro en gras,
        # titre à côté, filet sous la rangée et soulignement vert sur l'onglet
        # ouvert. Quatre pastilles rondes se lisaient comme un formulaire à
        # cocher ; ce sont des onglets, ils en ont la forme.
        # SIX ONGLETS, ET L'ORDRE EST CELUI DE LA LECTURE.
        #
        #   01 Raw Results      — ce que les ménages répondent, sans calcul ;
        #   02 Resilience Scores— ce que le référentiel en fait, dimension
        #                         par dimension ;
        #   03 By Indicator     — un indicateur, ses écarts sur le territoire ;
        #   04 By Landscape     — un paysage contre l'autre ;
        #   05 By Social Group  — un groupe contre tous les autres ;
        #   06 Solutions        — ce qu'on peut faire de tout cela.
        #
        # Les trois écrans du milieu répondent à la même question sous trois
        # angles : où sont les écarts, et quels indicateurs les font. Ils
        # partagent donc un seul moteur de calcul.
        _CODES_RA = ["brut", "scores", "indic", "paysage", "groupe",
                     "solutions"]
        _ra = onglets.barre("ra_vue", _CODES_RA,
                            titre=lambda c: T("ra_o_" + c),
                            description=lambda c: T("ra_d_" + c),
                            defaut="brut")

        # LE CATALOGUE EST CHARGÉ UNE FOIS POUR LES CINQ PREMIERS ONGLETS.
        # C'est le même fichier de réponses individuelles ; le charger dans
        # chaque module en ferait cinq copies en mémoire.
        _cat = croisement_resultats._catalogue() \
            if _ra in ("brut", "scores", "indic", "paysage", "groupe",
                       "solutions") \
            else None

        if _ra == "brut":
            # LES RÉSULTATS BRUTS SONT CE QUI A ÉTÉ MESURÉ, et rien d'autre :
            # aucun barème, aucune pondération. Deux instruments l'ont mesuré
            # et ils ont leur place au même endroit — le questionnaire, qui
            # interroge des ménages, et le satellite, qui regarde le sol. Un
            # seul des deux à la fois : ils ne se ventilent pas pareil, et
            # les empiler ferait deux écrans sur une page.
            # L'ÉTAPE 1 COIFFE LES QUATRE SOURCES. La rangée de cartes ne
            # disait pas ce qu'on attendait du lecteur : quatre objets de même
            # rang, dont on ne savait pas s'il fallait en choisir un ou les
            # lire tous. Numérotée et suivie d'une ligne d'aide, elle devient
            # le premier geste d'un parcours en quatre temps.
            st.markdown(
                f'<div class="ex-etape"><span class="n">1</span>'
                f'<span class="t">{T("ra_e1_t")}</span>'
                f'<span class="l"></span></div>',
                unsafe_allow_html=True)
            _src = onglets.barre(
                "ra_source",
                ["menages", "institutions", "biodiversite", "satellite"],
                titre=lambda c: T("ra_src_" + c),
                description=lambda c: T("ra_srcd_" + c), defaut="menages")
            if _src == "satellite":
                satellite_page.render()
            elif _src in ("institutions", "biodiversite"):
                _msg = T("ra_attente_inst" if _src == "institutions"
                         else "ra_attente_bio")
                st.markdown(
                    f'<div style="border:1px solid #e4e2de;'
                    f'background:#faf9f7;border-radius:12px;'
                    f'padding:20px 22px;margin:6px 0 4px;max-width:96ch">'
                    f'<div style="font-size:12px;letter-spacing:.09em;'
                    f'text-transform:uppercase;color:#8a7f6d;'
                    f'font-weight:600;margin-bottom:7px">'
                    f'{T("ra_attente_t")}</div>'
                    f'<p style="margin:0;font-size:14px;line-height:1.6;'
                    f'color:#3c4761;text-align:justify">{_msg}</p>'
                    f'</div>', unsafe_allow_html=True)
            else:
                explorateur.render(_cat, mode="brut")

        elif _ra == "scores":
            # LES SCORES SE DEMANDENT, ILS NE SE DÉVERSENT PAS, et le volet
            # repliable est parti avec le reste. Il portait une page de
            # dimension entière — ses indicateurs un par un, ses cartes, ses
            # compléments — sous un écran qui venait justement d'être réglé
            # pour ne montrer QUE la combinaison demandée. Replié, il n'en
            # restait pas moins un second écran posé sous le premier, avec
            # ses propres commandes et son propre découpage ; on ne peut pas
            # promettre « rien par défaut » et garder au bas de la page de
            # quoi tout déplier. Ce qui s'affiche ici, désormais, c'est le
            # mode d'affichage choisi et rien d'autre.
            explorateur.render_scores(_cat)

        elif _ra == "indic":
            analyse_ecarts.render_indicateur(_cat)

        elif _ra == "paysage":
            # LA FICHE PAYSAGE EXISTAIT DÉJÀ et se lit d'une traite ; l'écran
            # d'écarts la prolonge par ce qu'elle ne disait pas — quels
            # indicateurs, précisément, séparent un paysage de l'autre.
            # LA FICHE NE SUIT QUE SI L'ÉCRAN DU HAUT A RÉPONDU. Tant qu'aucun
            # mode d'affichage n'est choisi, la page doit rester vide : une
            # fiche complète posée dessous — sa barre de filtres, son radar —
            # annulerait la promesse faite deux lignes plus haut.
            if analyse_ecarts.render_paysage(_cat):
                st.markdown('<div style="height:30px"></div>',
                            unsafe_allow_html=True)
                fiche_paysages.render(entete=False)

        elif _ra == "groupe":
            if analyse_ecarts.render_groupe(_cat):
                st.markdown('<div style="height:30px"></div>',
                            unsafe_allow_html=True)
                synthese_page.render(entete=False)

        else:
            # LES VARIABLES ALARMANTES SE LISENT APRÈS LES ÉCARTS, et c'est
            # la seule place qui leur convienne : elles sont le résultat des
            # cinq écrans précédents, et l'entrée des boucles causales.
            analyse_ecarts.render_alarmes(_cat)

    if app_mode == MODE_METHODO:
        # « Cadre de résilience » a remplacé la page de méthodologie : des schémas
        # à la place de sept blocs de texte. Le document complet n'est pas perdu —
        # il est rendu dans le volet replié du bas. Une fonction qui marchait ne se
        # supprime pas au motif qu'on a réorganisé la façade ; on la range.
        #
        # L'OUTIL DE « CROISEMENT LIBRE » A ÉTÉ RETIRÉ D'ICI, ET SUPPRIMÉ DU DÉPÔT.
        # Il empilait des conditions sur les mêmes 483 questions, avec la même
        # carte par section et la même ventilation par sexe, catégorie et âge que
        # « Croisement des résultats » — qui fait tout cela et davantage : profil
        # de résilience du sous-groupe, comparaison de deux groupes, effectif
        # attendu sous indépendance. Deux outils qui font la même chose divergent
        # tôt ou tard, et le lecteur ne sait jamais lequel fait autorité.
        def _document_methodologique():
            methodologie_page.render()

        cadre_page.render(doc_complet=_document_methodologique)

    if app_mode == MODE_BOUCLES:
        # CINQ ÉCRANS QUI SONT UN SEUL PARCOURS, ET UN SEUL RENDU À LA FOIS.
        #
        #   1 · construire le système autour d'une variable critique ;
        #   2 · en justifier chaque relation, corrélation et preuve séparées ;
        #   3 · y chercher où appuyer ;
        #   4 · appuyer, sur plusieurs variables à la fois ;
        #   5 · regarder ce que ça fait vague après vague.
        #
        # Le système — variable centrale, population regardée, profondeur — est
        # choisi UNE fois, dans le premier onglet, et les quatre autres
        # travaillent dessus. C'est ce qui en fait un parcours et non cinq
        # outils qui se ressembleraient.
        #
        # `st.tabs` rendrait les cinq à chaque affichage : l'énumération des
        # boucles et les propagations seraient calculées ensemble pour n'en
        # montrer qu'une. Un sélecteur ne rend que ce qu'on regarde.
        # L'ANIMATION SUIT IMMÉDIATEMENT LA CONSTRUCTION, et c'est l'ordre
        # naturel du parcours : on dessine le système, puis on le fait
        # tourner. Les trois écrans d'analyse — relations, leviers,
        # interventions — viennent après, quand on a vu le système bouger et
        # qu'on sait quelles questions lui poser.
        _CODES_SX = ["construire", "direct", "relations", "leviers",
                     "simuler", "vagues"]
        _N_SX = dict(zip(_CODES_SX, ("sx_o1", "sx_o6", "sx_o2", "sx_o3",
                                     "sx_o4", "sx_o5")))
        _D_SX = dict(zip(_CODES_SX, ("sx_d1", "sx_d6", "sx_d2", "sx_d3",
                                     "sx_d4", "sx_d5")))
        _vue = onglets.barre("bcl_vue", _CODES_SX,
                             titre=lambda c: T(_N_SX[c]),
                             description=lambda c: T(_D_SX[c]),
                             defaut="construire")
        if _vue == "construire":
            systeme_complexe.render_construire()
        elif _vue == "relations":
            systeme_complexe.render_relations()
        elif _vue == "leviers":
            systeme_complexe.render_leviers()
        elif _vue == "simuler":
            systeme_complexe.render_simuler()
            with st.expander(T("sx_deplier_syst")):
                systeme_page.render(entete=False)
        elif _vue == "vagues":
            systeme_complexe.render_vagues()
        else:
            # L'ONDE SE REGARDE SUR LE SCHÉMA, PAS DANS DES COLONNES. Les
            # colonnes de vagues disent combien et quand ; elles ne disent pas
            # par où. Or c'est « par où » qui fait comprendre une boucle : on
            # ne voit pas un effet revenir sur son point de départ dans un
            # tableau, on le voit quand la bille repasse par la même flèche.
            # Le dessin est donc celui du premier onglet, avec les mêmes
            # positions, et il bouge. La lecture en colonnes reste dessous
            # pour qui veut les chiffres vague par vague.
            systeme_direct.render()

    if app_mode == MODE_ACTIONS:
        # Les fiches descendent des leviers calculés par l'analyse des boucles.
        # LES PISTES D'ACTION LES SUIVENT, ET C'EST ICI QU'ELLES VONT. Elles
        # fermaient l'écran des variables alarmantes, qui dit où le problème
        # se trouve ; elles disent, elles, ce qu'on peut y faire — c'est la
        # question de cette page-ci, pas de celle-là.
        interventions_page.render()
        st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
        pistes_page.render()

    if app_mode == MODE_DONNEES:
        # LA PAGE NE PORTE QUE LES FICHIERS. Sous les sept documents venait
        # le fil des livraisons récentes — des cartouches, des descriptions,
        # des boutons qui mènent ailleurs. On vient ici prendre un fichier,
        # pas lire ce qui a été calculé cette semaine : chaque écran dit ce
        # qu'il a à dire, et celui-ci n'a que des documents à donner.
        telechargements_page.render()


# LE PIED EST RENDU HORS DE LA COLONNE DE DROITE, pour qu'il prenne toute la
# largeur — colonne de menu comprise. Rendu dedans, il se serait arrêté au
# bord du contenu et aurait laissé un angle blanc sous le menu.
with _pied:
    st.markdown(
        f'<div class="bandeau-haut pied">'
        f'<div class="pd-g">'
        + icones.svg("pousse", couleur="#8fc4a8", taille=16)
        + f'<span class="pd-devise">{T("pied_devise")}</span></div>'
        f'<span class="pd-credit">'
        f'{T("pied_credit", a=datetime.date.today().year)}</span>'
        f'</div>', unsafe_allow_html=True)

