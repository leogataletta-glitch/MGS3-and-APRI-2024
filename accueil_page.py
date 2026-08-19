"""Page d'accueil — la vue d'ensemble de l'APRI.

L'entrée d'un tableau de bord institutionnel ne doit pas être un menu : elle
doit répondre, en un écran, à « de quoi parle ce site, sur quel territoire,
avec quelles données, et qu'est-ce que ça donne ». Le reste — le détail par
dimension, la méthode, les téléchargements — vient après, pour qui veut
creuser.

D'où l'ordre de cette page : trois chiffres de périmètre et la localisation,
l'histoire du projet ensuite — ce qu'est APRI, d'où cela vient, ce que l'indice
ne prétend pas dire — puis les résultats saillants, la carte et les livraisons
récentes.

AUCUN LOGO DANS LE CONTENU. La marque APRI et celle du PNUE vivent dans la
colonne de gauche, où elles sont visibles en permanence ; les répéter en tête
de chaque page vole la place du titre sans rien apprendre à personne.

TOUS LES CHIFFRES SONT CALCULÉS, AUCUN N'EST ÉCRIT EN DUR. Une page d'accueil
qui affiche des nombres figés devient fausse à la première mise à jour des
données, et personne ne s'en aperçoit — c'est le pire défaut possible pour une
vitrine.
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components

import filtres
import icones
import i18n
import map_render
from i18n import T

# Les textes de cette page voyagent avec elle — même règle que partout
# ailleurs : versés dans le dictionnaire commun à l'import, et seulement si la
# clé n'y est pas déjà.
TEXTES = {
    "a_p_sections_s": {"en": "Covered in Sud and Grand'Anse",
                       "fr": "Couvertes dans le Sud et la Grand'Anse"},
    "a_p_departements_s": {"en": "Sud and Grand'Anse",
                           "fr": "Sud et Grand'Anse"},
    "a_p_menages_s": {"en": "Household survey, 2024",
                      "fr": "Enquête ménage, 2024"},
    "a_acces": {"en": "Quick access", "fr": "Accès rapides"},
    "a_acces_dimensions": {"en": "Explore the indicators",
                           "fr": "Explorer les indicateurs"},
    "a_acces_synthese": {"en": "Data by territory",
                         "fr": "Données par territoire"},
    "a_acces_actions": {"en": "Solutions and actions",
                        "fr": "Solutions et actions"},
    "a_acces_donnees": {"en": "Available datasets",
                        "fr": "Jeux de données disponibles"},
}
for _c, _v in TEXTES.items():
    i18n.DICO.setdefault(_c, _v)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, "data")

SECTIONS = ["Anse à Drick", "Barbois", "Dumont", "Débouchette", "Mouline",
            "Quentin", "Beaulieu", "Blactote", "Dalmette", "Trichet"]

# Les cinq chiffres de tête. Chacun pointe une ligne réelle de l'indice : la
# valeur affichée est relue du fichier de résultats, jamais recopiée.
VEDETTES = [
    (4, "eau", "#2a78d6", False),          # accès à l'eau de boisson
    (3, "assainissement", "#6b4fa8", False),
    (5, "electricite", "#c98a2e", False),
    (108, "alimentaire", "#b4451f", True),  # insécurité : le haut est mauvais
]


def _e(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt(v, dec=1):
    if v is None:
        return "—"
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def _trouver(nom):
    for c in (os.path.join(DATA, nom), os.path.join(APP_DIR, nom)):
        if os.path.exists(c):
            return c
    return None


@st.cache_data(show_spinner=False)
def _charger():
    res = None
    if _trouver("resultats.json"):
        with open(_trouver("resultats.json"), encoding="utf-8") as f:
            res = json.load(f)
    return res


def nom_indic(r):
    if i18n.get_lang() == "fr" and r.get("indicateur_fr"):
        return r["indicateur_fr"]
    return r["indicateur"]


def score_pondere(res, cible):
    """Moyenne pondérée de tous les indicateurs scorés, pour une cible.

    Les indicateurs non calculés sont exclus du dénominateur, jamais comptés
    comme des zéros — même règle que dans les pages de dimension, et elle doit
    le rester : deux moyennes calculées différemment sur le même site
    finiraient par ne plus concorder, et personne ne saurait laquelle croire.
    """
    num = den = 0.0
    for r in res:
        sc = (r.get("scores_corriges") or {}).get(cible)
        if sc is None:
            continue
        p = r.get("ponderation") or 1
        num += sc * p
        den += p
    return (num / den) if den else None


def _carte_vignette(res):
    valeurs = {s: score_pondere(res, s) for s in SECTIONS}
    valeurs = {s: (round(v, 2) if v is not None else None)
               for s, v in valeurs.items()}
    dispo = [v for v in valeurs.values() if v is not None]
    if not dispo:
        return None, 0
    seuils = map_render.nice_thresholds(dispo)
    hauteur = 620
    svg, seuils_ret, _m = map_render.render_map_svg(
        valeurs, {s: 1 for s in SECTIONS}, seuils, width=1040, height=hauteur,
        polarity="eleve_bon", unite="")
    legende = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'margin-right:14px"><span style="width:18px;height:11px;'
        f'border-radius:3px;background:{c};box-shadow:inset 0 0 0 1px '
        f'rgba(0,0,0,.12)"></span><span style="font-size:12px;'
        f'color:#52514e">{lab}</span></span>'
        for c, lab in map_render.legend_items(seuils_ret, "eleve_bon", ""))
    return ('<div style="font-family:system-ui,-apple-system,\'Segoe UI\','
            'sans-serif;background:#ffffff"><div style="margin:0 0 6px">'
            f'{legende}</div>{svg}</div>'), hauteur


def _menages_enquetes(res):
    """Le nombre de ménages enquêtés.

    Pas de `@st.cache_data` ici : le cache devrait hacher `res`, une liste de
    128 dictionnaires, ce qui coûterait plus cher que le calcul lui-même.

    L'ancienne version affichait `max(n)` sur toutes les lignes de résultat,
    soit 2 700 — qui est le nombre d'ENFANTS de la ligne 24 (enregistrement
    des naissances), pas de ménages. Le site annonçait donc en vitrine plus du
    double du vrai chiffre.

    Toutes les lignes ne comptent pas la même chose : la plupart comptent des
    ménages, quelques-unes comptent des individus. On borne donc le max par
    les effectifs par section communale, qui, eux, comptent des questionnaires
    et rien d'autre. Une ligne qui déclare nettement plus que ce total ne
    compte pas des ménages, et sort du calcul.

    Reste l'écart entre les deux : 1 211 questionnaires collectés, 1 206
    rattachés à une section communale. C'est le premier chiffre — le nombre de
    foyers réellement interrogés — qui est annoncé ici.
    """
    p = _trouver("ventilation.json")
    if not p or not res:
        return None
    with open(p, encoding="utf-8") as f:
        eff = (json.load(f) or {}).get("effectifs") or {}
    rattaches = sum((d or {}).get("Total") or 0 for d in eff.values())
    if not rattaches:
        return None
    plafond = rattaches * 1.1
    plausibles = [n for n in ((r.get("n") or {}).get("Total") for r in res)
                  if n and n <= plafond]
    return max(plausibles) if plausibles else rattaches


def menages_filtres(res):
    """Le nombre de ménages que la sélection courante désigne.

    Afficher un filtre au-dessus d'un chiffre qui ne bouge pas est pire que de
    ne pas afficher le filtre du tout. Les effectifs par section et par
    sous-population sont dans `ventilation.json` ; on les additionne selon ce
    qui est demandé, dans le même ordre de priorité que `filtres.cible()`.
    """
    p = _trouver("ventilation.json")
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        v = json.load(f) or {}
    eff = v.get("effectifs") or {}
    pays = v.get("paysage") or {}
    s, g, pa = filtres.section(), filtres.groupe(), filtres.paysage()
    col = g if g != filtres.TOUS else "Total"
    if s != filtres.TOUTES:
        return (eff.get(s) or {}).get(col)
    if pa != filtres.TOUS_P:
        return sum((eff.get(k) or {}).get(col) or 0
                   for k in eff if pays.get(k) == pa) or None
    if g != filtres.TOUS:
        return sum((d or {}).get(col) or 0 for d in eff.values()) or None
    return _menages_enquetes(res)


_STYLE_PERIMETRE = """
<style>
  /* LES TROIS CHIFFRES DE PÉRIMÈTRE, EN CARTES.
     Ils tenaient sur une ligne, en petit, et se lisaient comme une légende.
     Une carte par chiffre, avec sa pastille d'icône, son nombre en grand et
     sa précision dessous : c'est la première chose qu'on voit en arrivant,
     elle doit peser ce qu'elle vaut. */
  .a-kpi      { display:grid; grid-template-columns:repeat(auto-fit,
                minmax(260px,1fr)); gap:16px; margin:18px 0 6px; }
  .a-kpi-c    { display:flex; align-items:center; gap:15px; background:#fff;
                border:1px solid #e6ecf4; border-radius:14px;
                padding:16px 18px;
                box-shadow:0 1px 2px rgba(16,23,40,.04),
                           0 6px 18px rgba(16,23,40,.05); }
  .a-kpi-p    { width:52px; height:52px; flex:0 0 52px; border-radius:14px;
                display:flex; align-items:center; justify-content:center; }
  .a-kpi-v    { font-size:31px; font-weight:700; letter-spacing:-.025em;
                line-height:1; font-variant-numeric:tabular-nums; }
  .a-kpi-l    { font-size:14.5px; font-weight:600; color:#101728;
                margin-top:4px; }
  .a-kpi-s    { font-size:12.5px; color:#8a93a5; margin-top:2px;
                line-height:1.35; }
  /* L'encadré de localisation : une note de cadrage, pas un paragraphe de
     corps de texte — d'où le fond bleuté et la pastille d'information. */
  .a-note     { display:flex; gap:14px; align-items:flex-start;
                background:#f2f7fd; border:1px solid #dfeaf6;
                border-radius:14px; padding:15px 18px; margin:12px 0 6px; }
  .a-note-p   { width:34px; height:34px; flex:0 0 34px; border-radius:999px;
                background:#dbeafe; display:flex; align-items:center;
                justify-content:center; }
  .a-note-x   { font-size:15px; color:#3c4761; line-height:1.6; margin:0;
                max-width:96ch; }
  .a-hist-t    { font-size:13px; letter-spacing:.06em; text-transform:uppercase;
                 font-weight:700; color:#1f7a5a; margin:0 0 4px; }
  .a-hist-p    { font-size:15.5px; color:#3c4761; line-height:1.65;
                 max-width:92ch; margin:0 0 15px; }
  .a-hist-p:last-child { margin-bottom:2px; }
  .a-hist-p b  { color:#101728; font-weight:650; }
  /* Les accès rapides : une ligne par destination, icône colorée à gauche,
     chevron à droite. Ce sont de vrais boutons Streamlit — le chevron et
     l'icône sont peints par la feuille de style, le libellé et le
     sous-titre voyagent dans le libellé du bouton. */
  .a-liens-t  { font-size:15px; font-weight:700; color:#101728;
                margin:2px 0 10px; }
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button {
      display:flex !important; justify-content:flex-start !important;
      align-items:center !important; text-align:left !important;
      background:#fff !important; border:1px solid #eef2f7 !important;
      border-radius:11px !important; padding:9px 12px !important;
      min-height:56px !important; box-shadow:none !important;
      margin-bottom:6px; }
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button:hover {
      background:#f6f9fd !important; border-color:#dbe6f2 !important;
      transform:none !important; }
  /* Titre et sous-titre dans un seul libellé : Streamlit rend le markdown
     du bouton, `**gras**` devient un <strong> qu'on peut viser, et
     `white-space:pre-line` conserve le passage à la ligne. C'est le procédé
     déjà employé par les cartes de dimension. */
  /* Le bouton de Streamlit centre son contenu à trois niveaux imbriqués : il
     faut forcer l'alignement sur les conteneurs intérieurs, sinon les titres
     ne commencent pas tous à la même abscisse. */
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button > div,
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button
    div[data-testid="stMarkdownContainer"] {
      width:100% !important; text-align:left !important;
      display:block !important; }
  /* `!important` n'est pas un caprice : la feuille générale impose 18 px et
     600 aux libellés de bouton, et sans cela le sous-titre se lisait plus
     gros que le titre — exactement l'inverse de ce qu'il faut. */
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button p {
      text-align:left !important; margin:0 !important;
      white-space:pre-line !important;
      font-size:12.5px !important; font-weight:400 !important;
      color:#8a93a5 !important; line-height:1.45 !important; }
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button p strong {
      display:block; font-size:14.5px !important; font-weight:600 !important;
      color:#101728 !important; line-height:1.4 !important; }
  div[class*="st-key-acces_"] div[data-testid="stButton"] > button::after {
      content:"›"; margin-left:auto; font-size:19px; color:#b6bfcd;
      line-height:1; }
</style>
"""

# Les quatre destinations de l'encadré « accès rapides », et la couleur de
# leur pastille. L'identifiant de mode est celui d'app.py : le raccourci ne
# fait que le poser dans l'état de session, comme le ferait un clic dans la
# colonne de gauche.
ACCES = [
    ("dimensions", "barres", "#2f7fd6", "#e8f1fc"),
    ("synthese", "personnes", "#1f7a5a", "#e6f4ee"),
    ("actions", "cible", "#7048b6", "#efe9f9"),
    ("donnees", "telecharger", "#c98a2e", "#fdf3e3"),
]


def _aller(mode):
    """Le raccourci pose simplement le mode dans l'état de session — le même
    que celui qu'écrit un clic dans la colonne de gauche. Pas de callback à
    faire descendre depuis app.py : une chaîne de plus à maintenir pour une
    affectation d'une ligne."""
    st.session_state["app_mode"] = mode


def render(actualites=None):
    res = _charger()
    st.markdown(_STYLE_PERIMETRE, unsafe_allow_html=True)

    # ------------------------------------------------------------- bandeau
    # RIEN SOUS LE BANDEAU. Ni logo, ni pavé de bienvenue, ni titre : « APRI —
    # Observatoire de la résilience des paysages » répétait mot pour mot ce
    # que la colonne de gauche affiche en permanence, à quinze centimètres de
    # là. La page commence donc par le premier fait — le périmètre — au lieu
    # de se présenter une deuxième fois.
    if not res:
        st.info(T("e_absent"))
        st.stop()

    scores_sec = {s: score_pondere(res, s) for s in SECTIONS}
    scores_sec = {s: v for s, v in scores_sec.items() if v is not None}

    # --------------------------------------------------------- le périmètre
    # Cinq tuiles disaient cinq chiffres dont trois n'apprenaient rien à qui
    # arrive sur le site. Il en reste trois, sur une ligne, suivis de la
    # localisation : de quel territoire parle-t-on, et sur quelle base.
    #
    # ATTENTION AU NOMBRE DE MÉNAGES. L'ancienne tuile affichait le maximum
    # des effectifs de toutes les lignes, soit 2 700 — qui est le nombre
    # d'ENFANTS de la ligne 24 (enregistrement des naissances), pas de
    # ménages. Le bon dénominateur est le nombre de questionnaires, lu dans
    # les effectifs par section : ne pas revenir à un max() sur les lignes.
    kpis = [
        (str(len(SECTIONS)), T("a_p_sections"), T("a_p_sections_s"),
         "epingle", "#2f7fd6", "#e8f1fc"),
        ("2", T("a_p_departements"), T("a_p_departements_s"),
         "carte", "#1f7a5a", "#e6f4ee"),
        (_fmt(menages_filtres(res), 0), T("a_p_menages"),
         T("a_p_menages_s"), "personnes", "#7048b6", "#efe9f9"),
    ]
    st.markdown(
        '<div class="a-kpi">' + ''.join(
            f'<div class="a-kpi-c">'
            f'<div class="a-kpi-p" style="background:{fond}">'
            f'{icones.svg(ico, coul, 25, 1.9)}</div><div>'
            f'<div class="a-kpi-v" style="color:{coul}">{_e(v)}</div>'
            f'<div class="a-kpi-l">{_e(lib)}</div>'
            f'<div class="a-kpi-s">{_e(sous)}</div></div></div>'
            for v, lib, sous, ico, coul, fond in kpis)
        + '</div>'
        f'<div class="a-note"><div class="a-note-p">'
        f'{icones.svg("info", "#2f7fd6", 19, 2)}</div>'
        f'<p class="a-note-x">{T("a_localisation")}</p></div>',
        unsafe_allow_html=True)

    # LES FILTRES SONT ICI AUSSI, ET ILS AGISSENT VRAIMENT. Les afficher sur
    # la page d'accueil sans qu'ils changent quoi que ce soit serait pire que
    # de ne pas les afficher : les chiffres saillants et le nombre de ménages
    # suivent donc la sélection, et la carte reste la vue par section, qui est
    # sa raison d'être.
    filtres.barre(cle="accueil")

    # -------------------------------------------------------- l'histoire
    # Quatre volets « quoi / où / comment / pourquoi » disaient les mêmes
    # choses en trop peu de mots pour qu'on comprenne de quoi il s'agit. Un
    # récit court les remplace : d'où vient la démarche, ce qu'elle mesure,
    # comment elle est construite, et ce qu'elle ne prétend pas dire — cette
    # dernière partie n'est pas une précaution de style, c'est la condition
    # pour que les chiffres soient utilisés correctement.
    # L'histoire à gauche, les accès rapides à droite : le récit se lit, les
    # raccourcis se cliquent, et les deux n'ont pas à se disputer la largeur
    # de la page.
    _g, _d = st.columns([2.35, 1])
    with _g:
        with st.container(border=True):
            st.markdown(
                f'<div class="titre-bloc ambre">{T("a_histoire")}</div>',
                unsafe_allow_html=True)
            st.markdown(
                ''.join(f'<p class="a-hist-p"><b>{_e(T("a_h_" + c + "_t"))}</b> '
                        f'{T("a_h_" + c)}</p>'
                        for c in ("origine", "mesure", "construction",
                                  "portee")),
                unsafe_allow_html=True)
    with _d:
        with st.container(border=True):
            st.markdown(
                "<style>" + "".join(
                    icones.regle_masque(
                        f'div[class*="st-key-acces_{m}"] '
                        f'div[data-testid="stButton"] > button', ico, 21, 13)
                    + f'div[class*="st-key-acces_{m}"] '
                      f'div[data-testid="stButton"] > button::before '
                      f'{{ background-color:{coul}; }}'
                    for m, ico, coul, _f in ACCES) + "</style>"
                + f'<div class="a-liens-t">{_e(T("a_acces"))}</div>',
                unsafe_allow_html=True)
            for mode, _ico, _c, _f in ACCES:
                st.button(f'**{T("mode_" + mode)}**\n{T("a_acces_" + mode)}',
                          key=f"acces_{mode}", use_container_width=True,
                          on_click=_aller, args=(mode,))

    # ------------------------------------------------- résultats saillants
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc">{T("a_bloc_saillants")}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:15.5px;line-height:1.6;color:#3c4761;'
            f'margin:4px 0 12px;max-width:92ch">{T("a_bloc_saillants_texte")}'
            f'</p>', unsafe_allow_html=True)
        par_ligne = {r["ligne"]: r for r in res}
        cartes = []
        for lg, cle, coul, inverse in VEDETTES:
            r = par_ligne.get(lg)
            if not r:
                continue
            # Sous le filtre courant, et non plus sur le total : la barre
            # de filtres est au-dessus, elle doit commander ces chiffres.
            val = filtres.valeur(r)
            sc = filtres.score(r)
            cartes.append(
                f'<div style="flex:1 1 210px;min-width:190px;background:#fff;'
                f'border:1px solid #e7ecf3;border-left:4px solid {coul};'
                f'border-radius:13px;padding:14px 16px">'
                f'<div style="font-size:34px;font-weight:700;color:{coul};'
                f'font-variant-numeric:tabular-nums;letter-spacing:-.03em;'
                f'line-height:1.05">{_fmt(val)}'
                f'<span style="font-size:17px;margin-left:2px">%</span></div>'
                f'<div style="font-size:13.5px;color:#3c4761;font-weight:600;'
                f'margin-top:5px;line-height:1.35">{_e(T("a_v_" + cle))}</div>'
                f'<div style="font-size:12px;color:#8a93a5;margin-top:3px">'
                f'{_e(T("a_v_score", s=sc))} · {_e(T("a_v_ligne", n=lg))}'
                f'</div></div>')
        st.markdown('<div style="display:flex;gap:12px;flex-wrap:wrap">'
                    + ''.join(cartes) + '</div>', unsafe_allow_html=True)
        st.caption(T("a_bloc_saillants_note"))

    # ------------------------------------------------------------- la carte
    # Le diagramme en barres est retiré. Il disait la même chose que la carte
    # — le classement des dix sections — mais sans dire OÙ, et son échelle
    # arrondissait des écarts de trois dixièmes en barres identiques. La carte
    # porte le score ET la géographie ; deux vues du même chiffre, dont l'une
    # en dit moins, ne valent pas deux blocs.
    with st.container(border=True):
        st.markdown(f'<div class="titre-bloc vert">{T("a_bloc_carte")}</div>',
                    unsafe_allow_html=True)
        carte = _carte_vignette(res)
        if carte[0]:
            components.html(carte[0], height=carte[1] + 40, scrolling=False)
        st.caption(T("a_bloc_carte_note",
                     h=max(scores_sec, key=scores_sec.get),
                     b=min(scores_sec, key=scores_sec.get)))

    if actualites is not None:
        actualites()

    st.caption(T("e_source"))
    st.caption(T("credit"))
