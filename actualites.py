"""Le panneau « Actualités et ressources » de la page d'accueil.

Ce que la maquette appelle « Actualités & Rapports ». Ici ce ne sont pas des
nouvelles au sens journalistique — un observatoire n'en produit pas — mais les
LIVRABLES : ce qui vient d'être calculé, ce qu'on peut télécharger, ce qui
explique la méthode. C'est l'information dont un partenaire a besoin en
arrivant sur le site : qu'est-ce qui a bougé depuis ma dernière visite.

CHAQUE ENTRÉE POINTE VERS UN ONGLET RÉEL DU SITE, jamais vers une page qui
n'existe pas. Une liste de ressources qui mène à des impasses détruit la
confiance plus sûrement qu'une liste courte.

La pastille « Nouveau » est portée par la donnée, pas écrite à la main : elle
suit la liste NOUVEAUTES ci-dessous, qu'on met à jour en même temps que le
contenu qu'elle annonce.
"""

import streamlit as st

from i18n import T

# clé, onglet visé, icône, nouveauté
ENTREES = [
    ("thermique", "dimensions", "◍", True),
    ("vegetation", "dimensions", "❦", True),
    ("saison", "dimensions", "◈", True),
    ("methodo", "methodologie", "§", False),
    ("base", "donnees", "⤓", False),
]


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def rendre(bascule):
    """`bascule` est la fonction qui change d'onglet — passée par app.py pour
    que ce module n'ait pas à connaître l'état de session de l'application."""
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("n_titre")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:14.5px;color:#6b7590;line-height:1.55;'
            f'margin:2px 0 12px">{T("n_sous_titre")}</p>',
            unsafe_allow_html=True)

        for cle, onglet, icone, neuf in ENTREES:
            st.markdown(
                f'<div class="n-item">'
                f'<div class="n-icone">{icone}</div>'
                f'<div class="n-corps">'
                f'<div class="n-titre">{_e(T("n_" + cle))}'
                + (f'<span class="n-badge">{_e(T("n_nouveau"))}</span>'
                   if neuf else '')
                + f'</div>'
                f'<div class="n-texte">{_e(T("n_" + cle + "_texte"))}</div>'
                f'</div></div>', unsafe_allow_html=True)
            st.button(T("n_ouvrir"), key=f"n_btn_{cle}",
                      on_click=bascule, args=(onglet,),
                      use_container_width=True)
