"""Onglet « Méthodologie d'enquête ».

Le contenu vit dans data/methodologie.json : sept sections, chacune avec un
titre et un corps en anglais et en français. Le texte est repris de la note de
cadrage méthodologique IRLA — on ne le reformule pas ici, on le met en page.
"""

import json
import os

import streamlit as st

import i18n
import map_render
from i18n import T

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

# Une pilule de couleur par section, pour que le sommaire et les blocs se
# répondent visuellement plutôt que d'aligner sept titres identiques.
TEINTE = {
    "contexte": "", "cadre": "vert", "echantillon": "ambre",
    "questionnaire": "", "indicateurs": "vert", "lecture": "ambre",
    "limites": "",
}

# Les notions de l'article qui éclairent chaque section. Elles sont déjà
# rédigées dans i18n.NOTIONS : on les rappelle sous le bloc concerné.
NOTIONS_SECTION = {
    "cadre": ["resilience", "apri", "attributs_aaa", "resilience_generale"],
    "echantillon": ["paysage"],
    "indicateurs": ["ponderation", "echelle_0_10"],
    "lecture": ["pas_de_seuil", "bareme_comparatif", "score_capacite_pas_resilience"],
    "limites": ["limites", "appropriation"],
}


def _bulle_notion(cle):
    """Bulle de définition, sans dépendre de la version de map_render déployée.

    Sur GitHub, les fichiers ne sont pas toujours poussés dans le même commit :
    une page qui appelle une fonction absente de l'ancienne version de
    map_render fait tomber toute l'application. On dégrade donc proprement —
    bulle complète si la fonction existe, sinon le terme seul.
    """
    fn = getattr(map_render, "bulle_notion", None)
    if fn is not None:
        return fn(cle)
    terme, defi = i18n.notion(cle)
    if not defi:
        return ""
    bulle = getattr(map_render, "bulle", None)
    if bulle is not None:
        try:
            return bulle(cle, definition=defi, texte=terme)
        except TypeError:
            pass
    return f'<strong>{terme}</strong>'


def _styles_bulle():
    fn = getattr(map_render, "styles_bulle", None)
    return fn() if fn is not None else ""


def _trouver(nom):
    for chemin in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(chemin):
            return chemin
    return None


@st.cache_data(show_spinner=False)
def _charger():
    chemin = _trouver("methodologie.json")
    if chemin is None:
        return None
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _titre(sec):
    return sec.get(f"titre_{i18n.get_lang()}") or sec.get("titre_en", "")


def _corps(sec):
    return sec.get(f"corps_{i18n.get_lang()}") or sec.get("corps_en", "")


def render():
    doc = _charger()
    st.markdown(_styles_bulle(), unsafe_allow_html=True)

    st.title(T("m_titre"))
    st.markdown(
        '<p style="font-size:11.5px;color:#6b7590;letter-spacing:.06em;'
        'text-transform:uppercase;margin:-8px 0 0 2px;font-weight:600">'
        + T("m_sous_titre") + "</p>", unsafe_allow_html=True)

    if doc is None:
        st.error("methodologie.json")
        st.stop()

    sections = doc.get("sections", [])

    st.markdown(
        '<div style="background:#fff;border:1px solid #e3eaf3;border-left:5px '
        'solid #1a6bb0;border-radius:14px;padding:13px 17px;font-size:14.5px;'
        'color:#3c4761;box-shadow:0 1px 2px rgba(16,23,40,.05),'
        '0 8px 20px rgba(16,23,40,.06);margin:10px 0 4px">'
        + T("m_intro") + "</div>", unsafe_allow_html=True)

    # ---- sommaire : sept pastilles numérotées, en une ligne ----------------
    puces = "".join(
        '<span style="display:inline-flex;align-items:center;gap:8px;'
        'background:#f4f8fc;border:1px solid #e6ecf4;border-radius:999px;'
        'padding:7px 15px;margin:0 8px 8px 0;font-size:13px;color:#3c4761">'
        '<span style="display:inline-flex;align-items:center;justify-content:'
        'center;width:21px;height:21px;border-radius:999px;background:#1a6bb0;'
        f'color:#fff;font-size:11px;font-weight:700">{i}</span>{_titre(s)}</span>'
        for i, s in enumerate(sections, 1))
    st.markdown(
        '<p style="font-size:11px;color:#6b7590;letter-spacing:.07em;'
        'text-transform:uppercase;font-weight:700;margin:14px 0 6px 2px">'
        + T("m_sommaire") + "</p><div>" + puces + "</div>",
        unsafe_allow_html=True)

    # ---- les sept blocs ----------------------------------------------------
    for i, sec in enumerate(sections, 1):
        with st.container(border=True):
            classe = TEINTE.get(sec.get("cle"), "")
            st.markdown(
                f'<div class="titre-bloc {classe}">{i} · {_titre(sec)}</div>',
                unsafe_allow_html=True)
            st.markdown(_corps(sec))

            cles = NOTIONS_SECTION.get(sec.get("cle"), [])
            bulles = [_bulle_notion(c) for c in cles]
            bulles = [b for b in bulles if b]
            if bulles:
                st.markdown(
                    '<p style="font-size:11px;color:#6b7590;letter-spacing:.07em;'
                    'text-transform:uppercase;font-weight:700;margin:14px 0 4px">'
                    + T("m_notions") + '</p>'
                    '<p style="font-size:14px;color:#3c4761;margin:0">'
                    + " &nbsp;·&nbsp; ".join(bulles) + "</p>",
                    unsafe_allow_html=True)

    st.caption(T("m_source"))
    st.caption(T("credit"))
