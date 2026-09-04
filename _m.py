import re, sys
from streamlit.testing.v1 import AppTest
import i18n, filtres, ondes_choc, systeme_page, rapport_donateur, si_je_change  # ils enregistrent leurs libellés

# « rapport » ne figure plus : le rapport donateur n'est plus une entrée de
# menu, et le harnais ne doit pas garantir un écran qui n'est plus atteignable.
PAGES = ["portail","accueil","methodologie","dimensions","boucles","actions","donnees"]
# LES RUBRIQUES DEVENUES SOUS-ONGLETS RESTENT COUVERTES. Elles ne sont plus
# des valeurs d'`app_mode` : on les adresse par leur page hôte plus le libellé
# de la vue à sélectionner. Sans cela, quatre pages entières cesseraient
# d'être testées sans que rien ne le signale.
# « Trajectoires » ne figure plus : elle est rendue avec le cadre de
# résilience, dont AppTest dessine les deux onglets.
# Les selecteurs retiennent un CODE : on les pilote donc par le code, sans
# avoir a deviner le libelle traduit — qui, lui, depend de l'ordre des imports.
SOUS_VUES = {
    # LES SIX ONGLETS D'ANALYSE DES RÉSULTATS. « dimensions » rend le
    # premier ; les cinq autres sont adressés par leur code de vue.
    # LES DEUX SOURCES DES RÉSULTATS BRUTS. Le satellite est un écran entier
    # que le harnais ne verrait jamais si « brut » ne rendait que le
    # questionnaire.
    "ra_sat":     ("dimensions", "ra_source", "satellite"),
    "ra_scores":  ("dimensions", "ra_vue",  "scores"),
    "ra_indic":   ("dimensions", "ra_vue",  "indic"),
    "ra_paysage": ("dimensions", "ra_vue",  "paysage"),
    "ra_groupe":  ("dimensions", "ra_vue",  "groupe"),
    "ra_solutions": ("dimensions", "ra_vue", "solutions"),
    # LES CINQ ÉCRANS DES BOUCLES. « boucles » rend le premier ; les quatre
    # autres sont adressés par leur code de vue.
    "bcl_rel":    ("boucles",    "bcl_vue", "relations"),
    "bcl_lev":    ("boucles",    "bcl_vue", "leviers"),
    "bcl_sim":    ("boucles",    "bcl_vue", "simuler"),
    "bcl_vag":    ("boucles",    "bcl_vue", "vagues"),
    # LE CADRE DE RÉSILIENCE A SEPT ONGLETS, et « methodologie » n'en rend
    # qu'un — le premier. Sans ces six entrées, six écrans entiers, dont le
    # plan de sondage et les limites qui viennent d'être remis en service,
    # ne seraient jamais rendus une seule fois par le harnais.
    "cad_sources": ("methodologie", "cad_vue", "sources"),
    "cad_ind":     ("methodologie", "cad_vue", "indicateurs"),
    "cad_score":   ("methodologie", "cad_vue", "score"),
    "cad_boucles": ("methodologie", "cad_vue", "boucles"),
    "cad_env":     ("methodologie", "cad_vue", "environnement"),
    "cad_doc":     ("methodologie", "cad_vue", "document"),
}
PAGES += list(SOUS_VUES)
DIMS  = ["dim1","dim3","dim6","dim4"]
COMBOS = [
    {"f_section": filtres.TOUTES, "f_groupe": filtres.TOUS, "f_paysage": filtres.TOUS_P},
    {"f_section": "Dumont",       "f_groupe": filtres.TOUS, "f_paysage": filtres.TOUS_P},
    {"f_section": filtres.TOUTES, "f_groupe": "Femme",      "f_paysage": "Montagne"},
    {"f_section": "Trichet",      "f_groupe": "60+",        "f_paysage": "Littoral"},
]
# LES QUATRE ÉCRANS, PAS TROIS. La liste d'avant commençait à 2 : l'écran 1
# n'était jamais rendu, et c'est justement celui qui porte la carte du
# territoire et son lien. Trois combinaisons pour quatre écrans, on tourne.
ETAPE = [1, 2]
n = 0; probs = []
for lang in ("fr", "en"):
    for page in PAGES:
        for i, c in enumerate(COMBOS):
            at = AppTest.from_file("app.py", default_timeout=300)
            at.session_state["authed"] = True
            at.session_state["choix_langue"] = lang      # la bonne clé
            _mode, _cle_vue, _code = SOUS_VUES.get(page, (page, None, None))
            at.session_state["app_mode"] = _mode         # la bonne clé
            if _cle_vue:
                at.session_state[_cle_vue] = _code
            if page in ("dimensions", "ra_sat"):
                at.session_state["dim_active"] = DIMS[i]
                at.session_state["ra_vue"] = "brut"
            # LE PARCOURS D'ACCUEIL A QUATRE ÉCRANS, et n'en rendre que le
            # premier laissait passer une erreur sur le troisième. On les
            # parcourt tous les quatre.
            if page == "portail":
                at.session_state["portail_etape"] = ETAPE[i % len(ETAPE)]
            # LES BOUCLES ONT DEUX VUES, et n'en rendre qu'une laisserait
            # l'autre sans filet — c'est exactement le défaut qui avait
            # laissé passer une erreur sur le troisième écran de l'accueil.
            # LES TROIS ACTES DU RAPPORT DONATEUR. Quatre combinaisons pour
            # trois actes, on tourne, et le décalage d'une langue à l'autre
            # évite que les deux passes voient exactement la même chose.
            if page == "rapport":
                at.session_state["rap_chapitre"] = (i + (0 if lang == "fr" else 1)) % 3 + 1
            # L'OUTIL D'EXPLICATION : on fait tourner la variable choquée et
            # le sens du choc, pour qu'aucune combinaison ne reste sans filet.
            # LE SYSTÈME REGARDÉ TOURNE : variable centrale, population et
            # profondeur changent d'une combinaison à l'autre, sinon quatre
            # écrans sur cinq ne seraient jamais vus qu'avec un seul système.
            if page.startswith("bcl_") or page == "boucles":
                at.session_state["bcl_centre"] = ("foret", "eau", "elec",
                                                  "revenu")[i]
                at.session_state["bcl_pop"] = ("Total", "Femme", "Montagne",
                                               "Cat A")[i]
                at.session_state["bcl_prof"] = (2, 1, 3, 2)[i]
                at.session_state["sx_pousse_v"] = [("foret", "eau", "elec",
                                                    "revenu")[i]]
                at.session_state["sx_d_" + ("foret", "eau", "elec",
                                            "revenu")[i]] = (1.0, -1.5,
                                                             2.0, 0.5)[i]
            if page == "boucles":
                at.session_state["bcl_vue"] = "construire"
            for k, v in c.items():
                at.session_state[k] = v
            at.run()
            if at.exception:
                probs.append((lang, page, i, "EXC " + str(at.exception[0].value)[:260]))
                continue
            txt = " ".join([e.value for e in at.markdown] + [e.value for e in at.caption]
                           + [e.value for e in at.info] + [e.value for e in at.warning])
            txt = re.sub(r'<style>.*?</style>', ' ', txt, flags=re.S)
            txt = re.sub(r'<svg.*?</svg>', ' ', txt, flags=re.S)
            br = {b for b in re.findall(r'\b[a-z]{1,3}_[a-z0-9_]{2,}\b', txt) if b in i18n.DICO}
            if br:
                probs.append((lang, page, i, "CLES " + str(sorted(br)[:8])))
            n += 1
print("RENDUS:", n)
for p in probs: print("  !", p)
print("PROBLEMES:", len(probs))
