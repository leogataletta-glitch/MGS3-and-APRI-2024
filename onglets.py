"""La barre d'onglets du site, en un seul endroit.

POURQUOI UN MODULE POUR UNE BARRE.
Trois pages portaient chacune leur propre barre, avec sa feuille de style
recopiée. Elles se ressemblaient sans être identiques, et chaque retouche
devait être faite trois fois — ce qui n'arrive jamais : au bout de quelques
passes, la barre du cadre n'avait plus tout à fait la même graisse que celle
des résultats, et le lecteur qui passait de l'une à l'autre changeait de site
sans changer de page. Une seule fonction, une seule feuille de style : la
continuité n'est plus une intention, elle est une conséquence.

LA CARTE PORTE DEUX LIGNES, ET LA SECONDE FAIT TOUT LE TRAVAIL.
« Par paysage » ne dit pas ce qu'on y trouve ; « ce qui distingue un paysage
du reste » le dit. Un titre seul oblige à cliquer pour savoir ; un titre suivi
d'une ligne de description laisse choisir depuis la barre. C'est le format des
cartes de l'accueil, et c'est exactement pour cela qu'il est repris ici : la
page d'accueil promet cinq destinations, chaque page tient la promesse avec la
même forme.

LA CLÉ DE CONTENEUR COMMENCE TOUJOURS PAR « ong_ », ET C'EST LOAD-BEARING.
Streamlit pose la classe `st-key-<clé>` sur le bloc, et la feuille de style
vise `class*="st-key-ong_"` : un appel qui nommerait sa clé autrement
n'hériterait de rien et retomberait sur les pastilles par défaut.
"""

import streamlit as st

STYLE = """
<style>
  /* Les enveloppes que Streamlit interpose sont forcées à la pleine largeur :
     sans cela, un `flex: 1 1 0` sur les cases se calcule contre un parent
     ajusté au contenu, et la barre entière se replie sur trois mots. */
  div[class*="st-key-ong_"],
  div[class*="st-key-ong_"] div[data-testid="stElementContainer"],
  div[class*="st-key-ong_"] div[data-testid="stRadio"] {
      width: 100% !important;
  }
  div[class*="st-key-ong_"] div[role="radiogroup"] {
      display: flex !important; flex-wrap: wrap !important;
      gap: 10px !important; width: 100% !important;
      align-items: stretch; margin: 2px 0 16px;
  }
  div[class*="st-key-ong_"] div[role="radiogroup"] > label {
      flex: 1 1 150px !important; min-width: 0 !important;
      margin: 0 !important; cursor: pointer; position: relative;
      background: #fff !important;
      border: 1px solid #e3eaf3 !important; border-radius: 12px !important;
      padding: 13px 15px 14px !important;
      transition: border-color .15s ease, background .15s ease,
                  box-shadow .15s ease;
  }
  /* LA PASTILLE RONDE DU SÉLECTEUR EST ENFOUIE DE TROIS NIVEAUX et n'est ni le
     premier enfant du label ni un pseudo-élément — d'où le chemin complet. */
  div[class*="st-key-ong_"] div[role="radiogroup"]
      > label > div > div > div:first-child { display: none !important; }
  div[class*="st-key-ong_"] div[role="radiogroup"] > label > div > div {
      gap: 0 !important; width: 100% !important;
  }
  /* La première ligne est le titre, la seconde la description : deux
     paragraphes dans le même libellé, et le CSS les distingue par leur rang
     plutôt que par une classe qu'on ne peut pas poser dans un libellé. */
  div[class*="st-key-ong_"] div[role="radiogroup"] > label p {
      margin: 0 !important; text-align: center !important;
  }
  div[class*="st-key-ong_"] div[role="radiogroup"] > label p:first-child {
      font-size: 13px !important; font-weight: 700 !important;
      color: #101728 !important; line-height: 1.3 !important;
  }
  div[class*="st-key-ong_"] div[role="radiogroup"] > label p:not(:first-child) {
      font-size: 11.5px !important; font-weight: 400 !important;
      color: #6b7590 !important; line-height: 1.45 !important;
      margin-top: 5px !important;
  }
  div[class*="st-key-ong_"] div[role="radiogroup"] > label:hover {
      border-color: #c6d3c9 !important; background: #fbfdfc !important;
  }
  /* L'ONGLET COURANT : un fond très pâle, un bord vert et un filet plein en
     haut. Un fond saturé, sur une rangée de sept, aurait fait une tache ; le
     filet dit la même chose sans peser, et il se lit même en niveaux de gris. */
  div[class*="st-key-ong_"] div[role="radiogroup"]
      > label:has(input:checked) {
      background: #f4f9f6 !important;
      border-color: #2a6b3f !important;
      box-shadow: inset 0 3px 0 0 #2a6b3f !important;
  }
  div[class*="st-key-ong_"] div[role="radiogroup"]
      > label:has(input:checked) p:first-child { color: #1a6b52 !important; }
  div[class*="st-key-ong_"] div[role="radiogroup"]
      > label:has(input:checked) p:not(:first-child) {
      color: #3c4761 !important;
  }
  /* SUR ÉCRAN ÉTROIT LES CASES SE METTENT À DEUX PAR RANGÉE. Sept cartes de
     cent cinquante pixels sur un téléphone donneraient sept lignes ; deux
     colonnes gardent la barre lisible sans la faire défiler. */
  @media (max-width: 760px) {
    div[class*="st-key-ong_"] div[role="radiogroup"] > label {
        flex: 1 1 44% !important; padding: 10px 12px !important;
    }
    div[class*="st-key-ong_"] div[role="radiogroup"]
        > label p:not(:first-child) { display: none !important; }
  }

  /* LES ONGLETS NATIFS DE STREAMLIT, LÀ OÙ IL EN RESTE, empruntent la même
     famille : mêmes graisses, même vert, même filet. Ils vivent deux niveaux
     plus bas que la barre de page et n'ont pas de description à porter ; ce
     qui doit se ressembler, c'est la façon dont l'onglet courant se signale. */
  div[data-testid="stTabs"] button[data-baseweb="tab"] p {
      font-size: 12.5px !important; font-weight: 600 !important;
      color: #6b7590 !important;
  }
  div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p {
      color: #1a6b52 !important; font-weight: 700 !important;
  }
  div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
      background: #2a6b3f !important;
  }
</style>
"""


def barre(cle, codes, titre, description=None, defaut=None):
    """Une barre d'onglets, et le code de celui qui est choisi.

    `titre` et `description` prennent un code et rendent une chaîne déjà
    traduite : la barre ne connaît pas i18n, elle ne connaît que du texte.
    Une description absente donne une carte à une ligne — utile pour deux
    onglets dont les titres se suffisent.

    LE CODE EST RETENU, PAS L'INDEX. Un index de liste change de sens dès que
    l'ordre des onglets change ou que la langue réordonne quoi que ce soit ;
    un code stable retrouve toujours le même écran.
    """
    st.markdown(STYLE, unsafe_allow_html=True)
    if defaut and st.session_state.get(cle) not in codes:
        st.session_state[cle] = defaut

    def _lib(c):
        t = titre(c)
        d = description(c) if description else None
        # DEUX PARAGRAPHES, PAS UN SAUT DE LIGNE. Le libellé d'un radio est
        # rendu en markdown : une ligne vide y fait deux <p>, que la feuille
        # de style distingue par leur rang. Un <br> serait échappé.
        return f"**{t}**\n\n{d}" if d else f"**{t}**"

    with st.container(key=cle if cle.startswith("ong_") else f"ong_{cle}"):
        return st.radio(cle, codes, horizontal=True,
                        label_visibility="collapsed", key=cle,
                        format_func=_lib)
