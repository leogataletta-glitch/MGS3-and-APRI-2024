"""Le jeu d'icônes du site — un seul endroit, deux façons de s'en servir.

POURQUOI UN MODULE PLUTÔT QUE DES CARACTÈRES

La navigation portait des glyphes typographiques — ◉ ◈ ▦ ⟳ — choisis parce
qu'ils tenaient dans une chaîne de caractères. Ils ne veulent rien dire, leur
graisse varie d'une police système à l'autre, et sur certaines machines ils
tombent en carré vide. Des icônes dessinées disent la fonction, gardent la
même épaisseur de trait partout, et coûtent quelques centaines d'octets.

DEUX SORTIES POUR LE MÊME DESSIN

  · `svg()` rend une balise complète, à poser dans du HTML — les pastilles des
    chiffres de tête, les lignes d'accès rapide.
  · `masque()` rend une URL de données à utiliser en `mask-image` dans une
    feuille de style. C'est le seul moyen de mettre une icône dans un bouton
    Streamlit, dont on ne contrôle pas le contenu : on la peint devant le
    libellé, en `::before`, et elle prend la couleur du texte.

Les tracés suivent une grille de 24, trait de 1,8, extrémités arrondies : la
même main que les icônes de l'interface, pas un mélange de sources.
"""

from urllib.parse import quote

# Le contenu de chaque icône, sans l'enveloppe <svg> — elle est ajoutée par
# les deux fonctions ci-dessous, qui ont besoin d'attributs différents.
TRACES = {
    # --- navigation
    "grille": '<rect x="3.2" y="3.2" width="7.2" height="7.2" rx="1.6"/>'
              '<rect x="13.6" y="3.2" width="7.2" height="7.2" rx="1.6"/>'
              '<rect x="3.2" y="13.6" width="7.2" height="7.2" rx="1.6"/>'
              '<rect x="13.6" y="13.6" width="7.2" height="7.2" rx="1.6"/>',
    "bouclier": '<path d="M12 3l7 2.8v6.1c0 4.3-2.9 8-7 9.1-4.1-1.1-7-4.8-7-9.1'
                'V5.8L12 3z"/><path d="M9.2 12l2 2 3.6-3.8"/>',
    "barres": '<path d="M4.5 20.5V11"/><path d="M12 20.5V3.5"/>'
              '<path d="M19.5 20.5v-6"/>',
    "boucle": '<path d="M20.2 12a8.2 8.2 0 1 1-2.4-5.8"/>'
              '<path d="M20.5 3.6v5.2h-5.2"/>',
    "personnes": '<path d="M15.6 20.4v-1.9a3.9 3.9 0 0 0-3.9-3.9H6.9A3.9 3.9 0 '
                 '0 0 3 18.5v1.9"/><circle cx="9.3" cy="7.4" r="3.3"/>'
                 '<path d="M21 20.4v-1.9a3.9 3.9 0 0 0-2.9-3.8"/>'
                 '<path d="M15.9 4.3a3.3 3.3 0 0 1 0 6.2"/>',
    "fiche": '<path d="M13.8 3.2H7.4a2 2 0 0 0-2 2v13.6a2 2 0 0 0 2 2h9.2a2 2 0 '
             '0 0 2-2V8.4z"/><path d="M13.8 3.2v5.2h5"/>'
             '<path d="M8.6 13h6.8"/><path d="M8.6 16.4h4.4"/>',
    "telecharger": '<path d="M12 3.6v11"/><path d="M7.4 10.2L12 14.8l4.6-4.6"/>'
                   '<path d="M4.6 19.6h14.8"/>',
    # Un hexagone, ses rayons, et un polygone intérieur : la figure même que
    # la rubrique produit. Une icône qui montre son résultat se reconnaît plus
    # vite qu'une icône qui décrit son outil.
    "radar": '<path d="M12 2.6l8.1 4.7v9.4L12 21.4 3.9 16.7V7.3z"/>'
             '<path d="M12 2.6v18.8"/><path d="M3.9 7.3l16.2 9.4"/>'
             '<path d="M20.1 7.3L3.9 16.7"/>'
             '<path d="M12 7.1l4.3 2.5v3.2L12 15.6l-4.3-2.8V9.6z"/>',
    # --- chiffres de tête et filtres
    "epingle": '<path d="M19.8 10.4c0 5-7.8 10.8-7.8 10.8S4.2 15.4 4.2 10.4a7.8 '
               '7.8 0 1 1 15.6 0z"/><circle cx="12" cy="10.2" r="2.8"/>',
    "carte": '<path d="M9 3.6L3.7 5.9v14.5L9 18.1l6 2.3 5.3-2.3V3.6L15 5.9z"/>'
             '<path d="M9 3.6v14.5"/><path d="M15 5.9v14.5"/>',
    "maison": '<path d="M3.8 10.6L12 3.8l8.2 6.8"/>'
              '<path d="M6.2 9.4v10.8h11.6V9.4"/>',
    "montagne": '<path d="M2.8 19.4h18.4L14.1 6.2l-3.4 6.1-2.2-2.7z"/>',
    "rafraichir": '<path d="M20.2 12a8.2 8.2 0 1 1-2.4-5.8"/>'
                  '<path d="M20.5 3.6v5.2h-5.2"/>',
    # --- accès rapides et divers
    "cible": '<circle cx="12" cy="12" r="8.4"/><circle cx="12" cy="12" r="4"/>'
             '<circle cx="12" cy="12" r=".9"/>',
    "chevron": '<path d="M9.6 5.8l6.2 6.2-6.2 6.2"/>',
    "info": '<circle cx="12" cy="12" r="8.6"/><path d="M12 11.2v5.4"/>'
            '<path d="M12 7.6v.9"/>',
    "loupe": '<circle cx="10.8" cy="10.8" r="6.6"/>'
             '<path d="M15.6 15.6l4.6 4.6"/>',
    # --- les trois capacités et la chaîne de mesure, page d'accueil
    # Chaque dessin dit le mot plutôt que l'outil : un œil pour anticiper, un
    # bouclier pour absorber, une pousse pour s'adapter. Le reste de la chaîne
    # suit la même grille de 24 et le même trait de 1,8.
    "oeil": '<path d="M2.4 12S6 5.4 12 5.4 21.6 12 21.6 12 18 18.6 12 18.6 '
            '2.4 12 2.4 12z"/><circle cx="12" cy="12" r="3.1"/>',
    "pousse": '<path d="M12 20.4v-7.2"/>'
              '<path d="M12 13.2C12 9.6 14.8 6.8 18.6 6.8c0 3.6-2.8 6.4-6.6 '
              '6.4z"/>'
              '<path d="M12 15.6C12 12.8 9.7 10.5 6.4 10.5c0 2.8 2.3 5.1 5.6 '
              '5.1z"/>',
    "points": '<circle cx="6" cy="6" r="1.3"/><circle cx="12" cy="6" r="1.3"/>'
              '<circle cx="18" cy="6" r="1.3"/><circle cx="6" cy="12" r="1.3"/>'
              '<circle cx="12" cy="12" r="1.3"/>'
              '<circle cx="18" cy="12" r="1.3"/><circle cx="6" cy="18" r="1.3"/>'
              '<circle cx="12" cy="18" r="1.3"/>'
              '<circle cx="18" cy="18" r="1.3"/>',
    "cube": '<path d="M12 2.8l8.2 4.6v9.2L12 21.2l-8.2-4.6V7.4z"/>'
            '<path d="M3.8 7.4L12 12l8.2-4.6"/><path d="M12 12v9.2"/>',
    "pouls": '<path d="M2.6 12h4l2.4-6.4 4 12.8 2.6-6.4h5.8"/>',
    "jauge": '<path d="M3.4 17.6a9.4 9.4 0 1 1 17.2 0"/>'
             '<path d="M12 17.6l4.4-5"/><circle cx="12" cy="17.6" r="1.3"/>',
    "reseau": '<circle cx="12" cy="5.2" r="2.4"/>'
              '<circle cx="5.4" cy="17" r="2.4"/>'
              '<circle cx="18.6" cy="17" r="2.4"/>'
              '<path d="M10.8 7.4L6.6 14.8"/><path d="M13.2 7.4l4.2 7.4"/>'
              '<path d="M7.8 17h8.4"/>',
}


def svg(nom, couleur="currentColor", taille=20, trait=1.8):
    """Une balise SVG complète, à insérer dans du HTML."""
    t = TRACES.get(nom)
    if not t:
        return ""
    return (f'<svg width="{taille}" height="{taille}" viewBox="0 0 24 24" '
            f'fill="none" stroke="{couleur}" stroke-width="{trait}" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'style="display:block;flex:0 0 auto">{t}</svg>')


def masque(nom, trait=1.8):
    """Une URL de données prête pour `mask-image`, dans une feuille de style.

    Le tracé est peint en noir : c'est le masque qui compte, la couleur vient
    ensuite du `background-color` de l'élément, donc du thème.
    """
    t = TRACES.get(nom)
    if not t:
        return ""
    brut = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'fill="none" stroke="black" stroke-width="{trait}" '
            f'stroke-linecap="round" stroke-linejoin="round">{t}</svg>')
    return f'url("data:image/svg+xml,{quote(brut)}")'


def regle_masque(selecteur, nom, taille=19, marge=12):
    """La règle CSS qui pose une icône devant le libellé d'un bouton.

    On ne peut pas écrire dans le contenu d'un bouton Streamlit ; on peint donc
    l'icône en `::before` sur le bouton lui-même. La couleur est héritée du
    texte, si bien qu'un survol ou un état actif l'emporte avec lui.
    """
    return (f'{selecteur}::before {{ content:""; width:{taille}px; '
            f'height:{taille}px; flex:0 0 {taille}px; margin-right:{marge}px; '
            f'background-color:currentColor; -webkit-mask:{masque(nom)} '
            f'center/contain no-repeat; mask:{masque(nom)} '
            f'center/contain no-repeat; }}')
