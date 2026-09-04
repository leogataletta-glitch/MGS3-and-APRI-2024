"""Les libellés du questionnaire, dans la langue du site.

POURQUOI CE MODULE EXISTE.
Le catalogue des réponses vient du questionnaire de terrain : ses quatre cent
quatre-vingt-trois questions, ses quarante-deux modules et ses cinq cent
dix-neuf modalités sont écrits en français, parce que c'est la langue dans
laquelle l'enquête a été administrée. Le site, lui, se lit dans deux langues,
et la version anglaise affichait donc « Est originaire de cette section
communale » au milieu d'une page entièrement traduite.

LA TRADUCTION EST UN FICHIER, PAS UNE COLONNE DU JEU DE DONNÉES.
`data/questions_en.json` fait correspondre chaque chaîne française à sa
version anglaise. Le jeu de données n'est pas touché : les libellés français
restent les CLÉS partout — dans les masques binaires, dans l'index, dans les
états de session — et la traduction ne sert qu'à l'affichage. Un libellé
traduit qui deviendrait une clé casserait la première sélection enregistrée
avant un changement de langue.

CE QUI MANQUE RESTE EN FRANÇAIS, ET C'EST LE BON DÉFAUT.
Une question ajoutée au questionnaire sans passer par la traduction
s'affichera en français dans la version anglaise : c'est visible, corrigible,
et infiniment préférable à une page qui refuse de se dessiner.
"""

import json
import os

import streamlit as st

import i18n

APP_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data(show_spinner=False)
def _table():
    """Les trois dictionnaires de traduction, lus une fois."""
    for base in (os.path.join(APP_DIR, "data"), APP_DIR):
        chemin = os.path.join(base, "questions_en.json")
        if os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                d = json.load(f)
            return (d.get("categories") or {}, d.get("questions") or {},
                    d.get("modalites") or {})
    return {}, {}, {}


def _tr(quoi, texte):
    if not texte or i18n.get_lang() != "en":
        return texte
    cats, questions, mods = _table()
    return {"c": cats, "q": questions, "m": mods}[quoi].get(texte, texte)


def module(nom):
    """Le module du questionnaire, avec son code de lettre."""
    return _tr("c", nom)


def question(texte):
    return _tr("q", texte)


def modalite(texte):
    return _tr("m", texte)


def libelle(q, avec_module=True):
    """Le libellé complet d'une question : son module, puis son intitulé.

    LE CODE DE LETTRE DU MODULE NE S'AFFICHE PAS. « AQ. » ordonne le
    questionnaire, il n'apprend rien au lecteur ; c'est le nom du module qui
    situe la question.
    """
    nom = question(q.get("question") or "")
    if not avec_module:
        return nom
    mod = module(q.get("category") or "").split(". ", 1)[-1]
    return f"{mod} · {nom}" if mod else nom
