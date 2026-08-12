import pandas as pd
import os

_DEFAULT_CSV = '/root/.claude/uploads/dd64e98e-1cd6-5c35-b652-d6a659dcc81e/74bee669-Donn_esbrutesV3.csv'
_CSV_PATH = os.environ.get('DATA_CSV_PATH', '').strip() or _DEFAULT_CSV
df = pd.read_csv(_CSV_PATH, low_memory=False)

# Unfiltered snapshot, kept around so that dynamically-discovered category
# lists (built via .dropna().unique() on some free-text/coded column) stay
# IDENTICAL across a filtered run and the national run — otherwise a
# small filtered subset that never has, say, the "1000" superficie code would
# end up with a different row/modality set than the national file, breaking
# any attempt to line filtered runs up against each other.
df_full = df.copy()

def _classify_cat(x):
    if 'pauvrete extreme' in x: return 'A'
    if 'non pauvre' in x or 'non considere comme pauvre' in x: return 'C'
    if 'situation de pauvrete' in x: return 'B'
    return None

def _classify_age(a):
    if pd.isna(a): return None
    if a < 25: return '<25'
    if a < 40: return '25-39'
    if a < 60: return '40-59'
    return '60+'

_sexe_full = df_full['Sexe du repondant ?']
_cat_full = df_full['Stratefinale'].fillna('').apply(_classify_cat)
_age_full = df_full['ege du repondant ?'].apply(_classify_age)
_paysage_full = df_full['Sans poser la question selectionner le paysage.']
_section_full = df_full['Dans quelle section communale reside le repondant ?']

# Optional filters, combinable (AND across dimensions, OR within a dimension
# via comma-separated values). Every downstream group/base_n/THEMES
# computation in this module is derived from `df`, so filtering here cascades
# correctly through the entire script. SECTION_FILTER (single raw value) is
# kept for backward compatibility with the existing per-section batch builds;
# the *_FILTER variables below are the general, combinable form used by the
# interactive app.
SECTION_FILTER = os.environ.get('SECTION_FILTER', '').strip()
SECTION_FILTER_MULTI = [v for v in os.environ.get('SECTION_FILTER_MULTI', '').split(',') if v]
SEXE_FILTER = [v for v in os.environ.get('SEXE_FILTER', '').split(',') if v]
CAT_FILTER = [v for v in os.environ.get('CAT_FILTER', '').split(',') if v]
AGE_FILTER = [v for v in os.environ.get('AGE_FILTER', '').split(',') if v]
PAYSAGE_FILTER = [v for v in os.environ.get('PAYSAGE_FILTER', '').split(',') if v]

_mask = pd.Series(True, index=df_full.index)
if SECTION_FILTER:
    _mask &= (_section_full == SECTION_FILTER)
if SECTION_FILTER_MULTI:
    _mask &= _section_full.isin(SECTION_FILTER_MULTI)
if SEXE_FILTER:
    _mask &= _sexe_full.isin(SEXE_FILTER)
if CAT_FILTER:
    _mask &= _cat_full.isin(CAT_FILTER)
if AGE_FILTER:
    _mask &= _age_full.isin(AGE_FILTER)
if PAYSAGE_FILTER:
    _mask &= _paysage_full.isin(PAYSAGE_FILTER)

if not _mask.all():
    df = df_full[_mask].reset_index(drop=True)

# --- derive banner dimensions ---
sexe = df['Sexe du repondant ?']

strate = df['Stratefinale'].fillna('')
def cat(x):
    if 'pauvrete extreme' in x: return 'A'
    if 'non pauvre' in x or 'non considere comme pauvre' in x: return 'C'
    if 'situation de pauvrete' in x: return 'B'
    return None
poverty_cat = strate.apply(cat)

age = df['ege du repondant ?']
def bin_age(a):
    if pd.isna(a): return None
    if a < 25: return '<25'
    if a < 40: return '25-39'
    if a < 60: return '40-59'
    return '60+'
agebin = age.apply(bin_age)

paysage = df['Sans poser la question selectionner le paysage.']
section = df['Dans quelle section communale reside le repondant ?']

groups = [
    ('Total',        pd.Series(True, index=df.index)),
    ('Homme',        sexe == 'Homme'),
    ('Femme',        sexe == 'Femme'),
    ('Cat A',        poverty_cat == 'A'),
    ('Cat B',        poverty_cat == 'B'),
    ('Cat C',        poverty_cat == 'C'),
    ('<25',          agebin == '<25'),
    ('25-39',        agebin == '25-39'),
    ('40-59',        agebin == '40-59'),
    ('60+',          agebin == '60+'),
    ('Littoral',     paysage == 'Littoral (ou plaene cotiere)'),
    ('Montagne',     paysage == 'Montagne'),
    ('Anse à Drick', section == 'Anse e Drick'),
    ('Barbois',      section == 'Barbois'),
    ('Dumont',       section == 'Dumont'),
    ('Débouchette',  section == 'Debouchette'),
    ('Mouline',      section == 'Mouline'),
    ('Quentin',      section == 'Quentin'),
    ('Beaulieu',     section == 'Beaulieu'),
    ('Blactote',     section == 'Blactote'),
    ('Dalmette',     section == 'Dalmette'),
    ('Trichet',      section == 'Trichet'),
]
group_names = [g[0] for g in groups]
base_n = {name: int(mask.sum()) for name, mask in groups}
# sanity print
print("Base sizes:", base_n)

def crosstab_rows(modalities):
    """modalities: list of (label, indicator_series 0/1 or bool). Returns list of
    (label, {group_name: n}) sorted by Total n desc."""
    out = []
    for label, ind in modalities:
        ind = ind.fillna(0)
        row_n = {}
        for name, mask in groups:
            row_n[name] = int(ind[mask].sum())
        out.append((label, row_n))
    out.sort(key=lambda x: -x[1]['Total'])
    return out

def pct(n, group_name):
    b = base_n[group_name]
    return round(n / b * 100, 1) if b else 0.0

# ============ THEMES ============

def col(name):
    return df[name]

def col_full(name):
    """Unfiltered version of col(), for deriving a stable category/modality
    list regardless of SECTION_FILTER (see df_full above)."""
    return df_full[name]

# 1. Eclairage
eclairage_main = "Quelle source d'energie utilisez vous pour vous eclairer chez vous ?"
eclairage_opts = [
    ('Ampoules rechargeables', col(eclairage_main + '/Ampoules rechargeables')),
    ('Autre', col(eclairage_main + '/Autre')),
    ('Lampes à kérosène', col(eclairage_main + '/Lampes e kerosene')),
    ('Des panneaux solaires', col(eclairage_main + '/Des panneaux solaires')),
    ('Bougies', col(eclairage_main + '/Bougies')),
    ('Aucune', col(eclairage_main + '/Aucune')),
    ('Génératrice', col(eclairage_main + '/Generatrice')),
    ('Infrastructure publique (EDH)', col(eclairage_main + '/Infrastructure publique (EDH)')),
]

# 2. Cuisson
cuisson_main = "Quel combustible utilisez vous pour cuisiner ?"
cuisson_opts = [
    ('Bois sec', col(cuisson_main + '/Du bois sec')),
    ('Charbon de bois', col(cuisson_main + '/Du charbon de bois')),
    ('Gaz', col(cuisson_main + '/Du gaz')),
    ('Fours solaires', col(cuisson_main + '/Fours solaires')),
    ('Kérosène', col(cuisson_main + '/Kerosene')),
    ('Autre', col(cuisson_main + '/Autre')),
]

# 3. Signal telephonique (single-select)
signal_col = col("Avez vous du signal telephonique chez vous  ?")
signal_opts = [
    ('Signal intermittent', (signal_col == 'De maniere intermittente').astype(int)),
    ('Signal disponible',   (signal_col == 'Oui').astype(int)),
    ('Absence de signal',   (signal_col == 'Non').astype(int)),
]

# 4. Dechets solides
dechets_main = "Comment vous vous debarrassez de vos dechets (solides) ?"
dechets_opts = [
    ('Jetage mer / terrain vague', col(dechets_main + '/Jetage e la mer/dans un terrain vague')),
    ('Incinération', col(dechets_main + '/Ordures incinerees')),
    ('Enfouissement', col(dechets_main + '/Ordures enfouies')),
    ('Collecte — service public', col(dechets_main + '/Collectes par un service public')),
    ('Collecte — service privé', col(dechets_main + '/Collectes par un service privee')),
    ('Autre', col(dechets_main + '/Autre')),
    ('Ne souhaite pas répondre', col(dechets_main + '/Ne souhaite pas repondre')),
]

# 5. Recyclage (single-select Oui/Non)
recyc_col = col("Est-ce que vous recyclez ou reutilisez certains de vos dechets ?")
recyc_opts = [
    ('Non', (recyc_col == 'Non').astype(int)),
    ('Oui', (recyc_col == 'Oui').astype(int)),
]

THEMES = [
    dict(category="C. ÉNERGIE DOMESTIQUE", question="Source d'éclairage",
         rows=crosstab_rows(eclairage_opts), multi=True,
         note="Question à choix multiples (chaque répondant peut cocher plusieurs sources) — les % ne totalisent pas 100%."),
    dict(category="C. ÉNERGIE DOMESTIQUE", question="Combustible utilisé pour cuisiner",
         rows=crosstab_rows(cuisson_opts), multi=True,
         note="Question à choix multiples (chaque répondant peut cocher plusieurs combustibles) — les % ne totalisent pas 100%."),
    dict(category="D. CONNECTIVITÉ / COMMUNICATION", question="Accès et fiabilité du réseau téléphonique",
         rows=crosstab_rows(signal_opts), multi=False,
         note="Question à réponse unique."),
    dict(category="E. GESTION DES DÉCHETS SOLIDES", question="Mode d'élimination des déchets solides",
         rows=crosstab_rows(dechets_opts), multi=True,
         note="Question à choix multiples (chaque répondant peut citer plusieurs modes) — les % ne totalisent pas 100%."),
    dict(category="E. GESTION DES DÉCHETS SOLIDES", question="Recyclage / réutilisation des déchets",
         rows=crosstab_rows(recyc_opts), multi=False,
         note="Question à réponse unique (Oui / Non)."),
]

import json
if __name__ == '__main__':
    for t in THEMES:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 2 : accès aux démarches administratives + infrastructures
# =====================================================================

def crosstab_rows_fixed_order(col_series, order):
    """Same as crosstab_rows but keeps a fixed (logical) order instead of
    sorting by Total n desc. Ignores modalities not present in `order`."""
    out = []
    for label in order:
        ind = (col_series == label).astype(int)
        row_n = {}
        for name, mask in groups:
            row_n[name] = int(ind[mask].sum())
        out.append((label, row_n))
    return out

DOC_LOCATION_ORDER = [
    'Dans cette section', 'Section voisine', 'Ville de la commune',
    'Jeremie ou Cayes', 'Port-au-Prince', 'Ne sait pas',
]

doc_types = [
    ('Acte de naissance', 'Acte de naissance'),
    ('Acte de décès', 'Acte de deces'),
    ('Passeport', 'Passeport'),
    ('Acte notarié (achat des terres)', 'Acte notarie (achat des terres)'),
    ("Carte d'identification nationale", "Carte d'identification nationale"),
    ('Permis de conduire', 'Permis de conduire'),
    ("Carte d'électeur", "Carte d'electeur"),
]

THEMES_ADMIN = []
for label, raw_col in doc_types:
    THEMES_ADMIN.append(dict(
        category="F. ACCÈS AUX SERVICES ADMINISTRATIFS",
        question=f"Où se rendre pour obtenir : {label}",
        rows=crosstab_rows_fixed_order(col(raw_col), DOC_LOCATION_ORDER),
        multi=False,
        note="Question à réponse unique. Lieu où le foyer doit se rendre pour effectuer cette démarche.",
    ))

HEALTH_TIME_ORDER = [
    'Moins de 15 minutes', 'Entre 15 minutes et 30 minutes', 'Entre 30 minutes et 45 minutes',
    'Entre 45 minutes et 1 heure', 'Entre 1 heure et 1 heure 30', 'Entre 1 heure 30 et 2 heures',
    'Entre 2 heures et 3 heures', 'Plus de 3 heures',
]
SCHOOL_TIME_ORDER = [
    'Moins de 15 min', 'Entre 15 et 30 min', 'Entre 30 min et 1h',
    'Entre 1h et 2h', 'Entre 2h et 3h', 'Plus de 3h',
]

health_col = col("Lorsque vous ou un membre de votre foyer etes malade, combien de temps e pied devez vous tarder pour vous rendre e l'infrastructure de sante la plus proche (seulement aller) ?")
primaire_col = col('Section primaire')
secondaire_col = col('Section secondaire')

THEMES_INFRA = [
    dict(category="G. ACCÈS AUX INFRASTRUCTURES DE SANTÉ ET D'ÉDUCATION",
         question="Temps à pied jusqu'à l'infrastructure de santé la plus proche (aller simple)",
         rows=crosstab_rows_fixed_order(health_col, HEALTH_TIME_ORDER), multi=False,
         note="Question à réponse unique."),
    dict(category="G. ACCÈS AUX INFRASTRUCTURES DE SANTÉ ET D'ÉDUCATION",
         question="Temps à pied jusqu'à l'école — section primaire (aller simple)",
         rows=crosstab_rows_fixed_order(primaire_col, SCHOOL_TIME_ORDER), multi=False,
         note="Question à réponse unique. Concerne les foyers ayant des enfants scolarisés en primaire."),
    dict(category="G. ACCÈS AUX INFRASTRUCTURES DE SANTÉ ET D'ÉDUCATION",
         question="Temps à pied jusqu'à l'école — section secondaire (aller simple)",
         rows=crosstab_rows_fixed_order(secondaire_col, SCHOOL_TIME_ORDER), multi=False,
         note="Question à réponse unique. Concerne les foyers ayant des enfants scolarisés au secondaire."),
]

THEMES2 = THEMES_ADMIN + THEMES_INFRA

if __name__ == '__main__':
    for t in THEMES2:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 3 : enfants nés dans la section communale + gouvernance
# =====================================================================

def bin_series(series, edges, labels):
    out = pd.Series(index=series.index, dtype=object)
    for i, lab in enumerate(labels):
        lo, hi = edges[i], edges[i+1]
        if hi == float('inf'):
            mask = series >= lo
        else:
            mask = (series >= lo) & (series < hi)
        out[mask] = lab
    return out

def crosstab_rows_from_bins(binned_series, labels):
    out = []
    for label in labels:
        ind = (binned_series == label).astype(int)
        row_n = {}
        for name, mask in groups:
            row_n[name] = int(ind[mask].sum())
        out.append((label, row_n))
    return out

a_enfants_col = col('Avez vous des enfants nes dans la section communale ?')
a_enfants_opts_order = ['Oui', 'Non']
a_enfants_rows = crosstab_rows_fixed_order(a_enfants_col, a_enfants_opts_order)
a_enfants_rows.sort(key=lambda x: -x[1]['Total'])

combien_labels = ['0', '1', '2', '3', '4', '5 et plus']
combien_binned = bin_series(col('Si oui, combien ?'), [0,1,2,3,4,5,float('inf')], combien_labels)
combien_rows = crosstab_rows_from_bins(combien_binned, combien_labels)

assist_labels = ['0', '1', '2', '3', '4 et plus']
assist_binned = bin_series(col('Pour combien deentre eux, vous (ou votre femme) avez vous ete assistee par un personnel de sante (medecin, infermiere ou matronne)  ?'),
                            [0,1,2,3,4,float('inf')], assist_labels)
assist_rows = crosstab_rows_from_bins(assist_binned, assist_labels)

acte_labels = ['0', '1', '2', '3', '4', '5 et plus']
acte_binned = bin_series(col("Combien de vos enfants nes dans la section communale disposent d'un acte de naissance ?"),
                          [0,1,2,3,4,5,float('inf')], acte_labels)
acte_rows = crosstab_rows_from_bins(acte_binned, acte_labels)

scol_labels = ['0', '1', '2', '3', '4 et plus']
scol_binned = bin_series(col("Nombre d'enfants de plus de 6 ans scolarises"), [0,1,2,3,4,float('inf')], scol_labels)
scol_rows = crosstab_rows_from_bins(scol_binned, scol_labels)

nonscol_labels = ['0', '1', '2', '3 et plus']
nonscol_binned = bin_series(col("Nombre d'enfants de plus de 6 ans non scolarises"), [0,1,2,3,float('inf')], nonscol_labels)
nonscol_rows = crosstab_rows_from_bins(nonscol_binned, nonscol_labels)

potdevin_col = col('Avez-vous de verser un pot de vin a un agent public dans la communaute durant les 12 derniers mois pour recevoir un service ou eviter une sanction ?')
potdevin_rows = crosstab_rows_fixed_order(potdevin_col, ['Non', 'Oui'])

# "Si oui, pour quel type de service ?" : texte libre, n=12 -> non ventilable en banner,
# on liste les reponses brutes dans la note plutot qu'en lignes de tableau.
service_texts = df['Si oui, pour quel type de service ?'].dropna().tolist()

THEMES_ENFANTS = [
    dict(category="H. ENFANTS NÉS DANS LA SECTION COMMUNALE",
         question="Avez-vous des enfants nés dans la section communale ?",
         rows=a_enfants_rows, multi=False,
         note="Question à réponse unique."),
    dict(category="H. ENFANTS NÉS DANS LA SECTION COMMUNALE",
         question="Nombre d'enfants nés dans la section communale (si oui)",
         rows=combien_rows, multi=False,
         note="Base : foyers ayant répondu « Oui » à la question précédente (n=915). % calculés sur la base fixe totale (voir bandeau)."),
    dict(category="H. ENFANTS NÉS DANS LA SECTION COMMUNALE",
         question="Nombre d'entre eux assistés par un personnel de santé (médecin, infirmière ou matronne)",
         rows=assist_rows, multi=False,
         note="Base : foyers ayant des enfants nés dans la section communale."),
    dict(category="H. ENFANTS NÉS DANS LA SECTION COMMUNALE",
         question="Nombre d'enfants nés dans la section communale disposant d'un acte de naissance",
         rows=acte_rows, multi=False,
         note="Base : foyers ayant des enfants nés dans la section communale."),
    dict(category="H. ENFANTS NÉS DANS LA SECTION COMMUNALE",
         question="Nombre d'enfants de plus de 6 ans scolarisés",
         rows=scol_rows, multi=False,
         note="Trois valeurs extrêmes (20, 30, 88) regroupées dans « 4 et plus » — probables erreurs de saisie à vérifier."),
    dict(category="H. ENFANTS NÉS DANS LA SECTION COMMUNALE",
         question="Nombre d'enfants de plus de 6 ans non scolarisés",
         rows=nonscol_rows, multi=False,
         note="Question à réponse unique."),
    dict(category="I. GOUVERNANCE ET INTÉGRITÉ",
         question="A versé un pot-de-vin à un agent public (12 derniers mois) pour recevoir un service ou éviter une sanction",
         rows=potdevin_rows, multi=False,
         note="Question à réponse unique. Réponses « Oui » : n=12 (0,99% de l'échantillon)."),
    dict(category="I. GOUVERNANCE ET INTÉGRITÉ",
         question="Si oui, pour quel type de service ? (réponses en texte libre, non ventilées par sous-groupe)",
         rows=[], multi=False,
         note="Échantillon trop faible (n=12) et réponses en texte libre non standardisées pour une ventilation par sous-groupe. "
              "Réponses brutes : " + " · ".join(service_texts) + "."),
]

THEMES3 = THEMES_ENFANTS

if __name__ == '__main__':
    for t in THEMES3:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 4 : gestion des risques / alertes + participation citoyenne
# =====================================================================

def keyword_multi_rows(series, keyword_map, other_label="Autre / non précisé"):
    """series: raw free-text column. keyword_map: OrderedDict label -> list of
    substrings (lowercased, matched anywhere). A response can match several
    categories (counted in each, like a multi-select). Returns crosstab rows
    sorted by Total n desc, plus an 'other' bucket for unmatched non-null text."""
    s = series.fillna('').astype(str).str.lower()
    matched_any = pd.Series(False, index=series.index)
    modalities = []
    for label, keywords in keyword_map.items():
        ind = s.apply(lambda x: any(k in x for k in keywords)).astype(int)
        matched_any = matched_any | (ind == 1)
        modalities.append((label, ind))
    has_text = series.notna() & (s.str.strip() != '')
    other_ind = (has_text & ~matched_any).astype(int)
    modalities.append((other_label, other_ind))
    rows = crosstab_rows(modalities)
    return rows

# --- 1. Formation gestion des risques ---
formation_rows = crosstab_rows_fixed_order(
    col('Avez-vous participe durant les 12 derniers mois e une formation sur la gestion des risques dans la communaute ?'),
    ['Oui', 'Non'])

# --- 2. Message d'alerte recu (multi-select, sous-colonnes dediees) ---
alerte_main = 'Avez-vous reeu un message dealerte lors du dernier cyclone /ouragan ?'
alerte_opts = [
    ('Oui : sur mon téléphone', col(alerte_main + '/Oui : sur mon telephone')),
    ('Oui : message diffusé au marché / église / OCB / haut-parleur', col(alerte_main + '/Oui : message diffuse au marche, e leeglise, OCB, Haut-parleur')),
    ('Oui : message diffusé dans la section (porte à porte)', col(alerte_main + '/Oui message diffuse dans la section communale (porte e porte)')),
    ('Oui : message diffusé à la radio', col(alerte_main + '/Oui : message diffuse e la radio')),
    ('Non', col(alerte_main + '/Non')),
]
alerte_rows = crosstab_rows(alerte_opts)

# --- 3. Prise en compte du message d'alerte ---
prise_compte_order = [
    "Je l'ai compris et l'ai pris en compte",
    "Je l'ai compris et l'ai ignoré parce que je n'y crois pas",
    "Je l'ai compris et ignoré parce que j'avais d'autres préoccupations",
    "Je ne l'ai pas compris",
]
prise_compte_raw = col("Avez-vous pris en compte le message dealerte si vous leavez reeu ?")
_map_pc = {
    "Je leai compris et leai pris en compte": "Je l'ai compris et l'ai pris en compte",
    "Je leai compris et leai ignore parce que je ney crois pas": "Je l'ai compris et l'ai ignoré parce que je n'y crois pas",
    "Je leai compris et ignore parce que j'avais d'autres preoccupations": "Je l'ai compris et ignoré parce que j'avais d'autres préoccupations",
    "Je ne leai pas compris": "Je ne l'ai pas compris",
}
prise_compte_clean = prise_compte_raw.map(_map_pc)
prise_compte_rows = crosstab_rows_fixed_order(prise_compte_clean, prise_compte_order)

# --- 4. Exercice de simulation ---
simulation_rows = crosstab_rows_fixed_order(
    col('Avez-vous participe durant les douze derniers mois e un exercice de simulation ?'),
    ['Oui', 'Non'])

# --- 5-7. Sensibilisation (3 sujets, Oui/Non chacun) ---
sujet1_rows = crosstab_rows_fixed_order(col("1er sujet de sensibilisation : Oe et comment trouver les abris deurgence ou se mettre e l'abri?"), ['Oui', 'Non'])
sujet2_rows = crosstab_rows_fixed_order(col('2nd sujet de sensibilisation : : Comment etablir un stock de contingence familiale?'), ['Oui', 'Non'])
sujet3_rows = crosstab_rows_fixed_order(col('3eme sujet de sensibilisation : : Comment selectionner et proteger les papiers importants?'), ['Oui', 'Non'])

# --- 8. Reunion communautaire ---
reunion_rows = crosstab_rows_fixed_order(col('Avez-vous participe e une reunion communautaire durant les 12 derniers mois ?'), ['Oui', 'Non'])

# --- 9. Vote pour mise en oeuvre projet/regle communautaire ---
vote_projet_rows = crosstab_rows_fixed_order(
    col('Avez-vous deje eu leoccasion de voter pour la mise en euvre deun projet / ou deune regle communautaire durant les derniers 24 mois, une mesure qui a ete ensuite mise en euvre ? '),
    ['Oui', 'Non'])

# --- 10. Domaine concerne (texte libre classifie) ---
DOMAINE_KEYWORDS = {
    'Environnement': ['anviwonman', 'anviwenman', 'anvironman', 'environnement', 'environment', 'anviroman'],
    'Infrastructure / eau': ['enfrastrikti', 'enfrastricture', 'infrastructure', 'route', 'dlo', 'pwi', 'kiosque', 'kyosque'],
    'Santé': ['sante'],
    'Éducation': ['edikasyon', 'education', "l'ecole", 'ecole'],
    'Agriculture / pêche': ['agricult', 'peche', 'pech'],
    'Social / religieux': ['sosyal', 'social', 'legliz', 'eglise'],
}
domaine_rows = keyword_multi_rows(col('Si oui, cela concernait quel domaine (ex: education, infrastructure, sante, environnement .... ) ?'), DOMAINE_KEYWORDS)

# --- 11. Comment vous impliquez-vous comme citoyen -> colonne vide ---
implication_col_empty = col('Comment vous impliquez vous comme citoyen ?').notna().sum()

# --- 12. Manifestation / greve ---
manif_rows = crosstab_rows_fixed_order(col('Avez-vous deje participe e une manifestation publique ou une greve ?'), ['Oui', 'Non'])

# --- 13-14. Elections ---
vote_dernieres_rows = crosstab_rows_fixed_order(col('Avez-vous vote aux dernieres elections ?'), ['Oui', 'Non'])
vote_prochaines_rows = crosstab_rows_fixed_order(col('Comptez vous voter aux prochaines elections ?'), ['Oui', 'Non'])

# --- 15. Contribution financiere ---
contrib_fin_rows = crosstab_rows_fixed_order(col('Avez-vous contribue financierement e un projet de la zone ?'), ['Oui', 'Non'])

# --- 16. Nettoyage espace public ---
nettoyage_rows = crosstab_rows_fixed_order(col("Avez-vous deje pris part e une activite de nettoyage ou d'entretien d'un espace public ?"), ['Oui', 'Non'])

# --- 17. Comite de gestion communautaire ---
comite_rows = crosstab_rows_fixed_order(col("Faites vous partie d'un comite de gestion communautaire ?"), ['Oui', 'Non'])

# --- 18. Organisation communautaire de base ---
organisation_rows = crosstab_rows_fixed_order(col('Faites-vous partie deune organisation communautaire de base ?'), ['Oui', 'Non'])

# --- 19. Secteur (si oui, texte libre classifie) ---
SECTEUR_KEYWORDS = {
    'Agriculture': ['agricult', 'agrikel', 'agrikilti', 'agrikol', 'planteur'],
    'Pêche': ['peche', 'pech'],
    'Mutuelle / solidarité': ['muso', 'mutuel', 'mityel', 'solidarite'],
    'Économie / commerce': ['enkonomik', 'economi'],
    'Environnement': ['anvironman', 'anviwonman', 'environnement'],
    'Social / développement communautaire': ['social', 'sosyal', 'devlopman', 'kominote'],
    'Religieux': ['religieux', 'evangelique'],
    'Éducation': ['education', 'edikasyon'],
    'Coopérative': ['cooperative', 'kooperativ'],
    'Eau': ['eau', 'maskreti'],
}
secteur_rows = keyword_multi_rows(col('Si oui, dans quel secteur ?'), SECTEUR_KEYWORDS)

THEMES4 = [
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="A participé à une formation sur la gestion des risques dans la communauté (12 derniers mois)",
         rows=formation_rows, multi=False, note="Question à réponse unique."),
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="A reçu un message d'alerte lors du dernier cyclone / ouragan",
         rows=alerte_rows, multi=True,
         note="Question à choix multiples (canaux cumulables) — les % ne totalisent pas 100%."),
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="A pris en compte le message d'alerte (si reçu)",
         rows=prise_compte_rows, multi=False, note="Question à réponse unique. Base : répondants ayant reçu un message d'alerte."),
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="A participé à un exercice de simulation (12 derniers mois)",
         rows=simulation_rows, multi=False, note="Question à réponse unique."),
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="Sensibilisé — Où et comment trouver les abris d'urgence / se mettre à l'abri",
         rows=sujet1_rows, multi=False, note="Question à réponse unique."),
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="Sensibilisé — Comment établir un stock de contingence familiale",
         rows=sujet2_rows, multi=False, note="Question à réponse unique."),
    dict(category="J. GESTION DES RISQUES ET DES CATASTROPHES",
         question="Sensibilisé — Comment sélectionner et protéger les papiers importants",
         rows=sujet3_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="A participé à une réunion communautaire (12 derniers mois)",
         rows=reunion_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="A voté pour la mise en œuvre d'un projet / règle communautaire, effectivement mis en œuvre (24 derniers mois)",
         rows=vote_projet_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="Si oui, domaine concerné (réponse libre reclassée par mots-clés)",
         rows=domaine_rows, multi=True,
         note="Texte libre reclassé par mots-clés (une réponse peut couvrir plusieurs domaines) — les % ne totalisent pas 100%. Base : n=133 réponses exploitables. Classification indicative, à valider."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="Comment vous impliquez-vous comme citoyen ?",
         rows=[], multi=False,
         note=f"Colonne vide dans la base brute (0 réponse sur 1211) — question non renseignée, rien à ventiler."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="A déjà participé à une manifestation publique ou une grève",
         rows=manif_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="A voté aux dernières élections",
         rows=vote_dernieres_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="Compte voter aux prochaines élections",
         rows=vote_prochaines_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="A contribué financièrement à un projet de la zone",
         rows=contrib_fin_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="A déjà pris part à une activité de nettoyage / entretien d'un espace public",
         rows=nettoyage_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="Fait partie d'un comité de gestion communautaire",
         rows=comite_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="Fait partie d'une organisation communautaire de base",
         rows=organisation_rows, multi=False, note="Question à réponse unique."),
    dict(category="K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE",
         question="Si oui, secteur de l'organisation (réponse libre reclassée par mots-clés)",
         rows=secteur_rows, multi=True,
         note="Texte libre reclassé par mots-clés (une réponse peut couvrir plusieurs secteurs) — les % ne totalisent pas 100%. Base : n=216 réponses exploitables. Classification indicative, à valider."),
]

if __name__ == '__main__':
    for t in THEMES4:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])
    print('implication citoyen non-null count:', implication_col_empty)

# =====================================================================
# THEMES 5 : dimension sociale (vie communautaire, sécurité, conflits)
# =====================================================================

FREQ_ORDER = ['Jamais', '1x par an', 'Plusieurs par an', '1xmois', '1xsemaine et+']

def freq_block(question_label, raw_col_name):
    return dict(
        category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
        question=f"Fréquence de participation — {question_label}",
        rows=crosstab_rows_fixed_order(col(raw_col_name), FREQ_ORDER),
        multi=False,
        note="Question à réponse unique (fréquence de participation à ce groupe/activité)."
    )

corvee_rows = crosstab_rows_fixed_order(col('Avez-vous participe a une corvee agricole durant les 12 derniers mois ?'), ['Oui', 'Non'])
muso_rows = crosstab_rows_fixed_order(col("etes-vous membre d'une mutuelle d'epargne (MUSO, TIPA, etc.) ou d'une banque communautaire?"), ['Oui', 'Non'])
securite_rows = crosstab_rows_fixed_order(col('Vous sentez-vous en securite la nuit dans votre communaute ?'), ['Oui', 'Non'])

PEUR_KEYWORDS = {
    'Insécurité / bandits': ['bandi', 'ensekirite', 'insecurite', 'malfekte', 'lame ti manchet', 'mauvais entourage'],
    'Absence de police / autorité': ['policier', 'police', 'otorite', 'autorite'],
    'Vol': ['vole', 'voleur', 'vol '],
    'Logement/abri inadéquat': ['abri', 'fenet', 'porte'],
}
peur_rows = keyword_multi_rows(col('Si non, de quoi avez vous peur ?'), PEUR_KEYWORDS)

danger_arrivants_rows = crosstab_rows_fixed_order(
    col('Pensez vous que les nouveaux arrivants soient un danger pour la communaute ?'),
    ['Oui', 'Non', 'Je ne sais pas'])

eleve_seul_rows = crosstab_rows_fixed_order(col('Elevez-vous vos enfants seul(e) ?'), ['Oui', 'Non'])

POURQUOI_SEUL_ORDER = ['Deces', 'Separation', 'Abandon',
                        "On est ensemble mais l'autre parent vit ailleurs (Hors communaute)", 'Autre']
POURQUOI_SEUL_LABELS = {'Deces': 'Décès', 'Separation': 'Séparation', 'Abandon': 'Abandon',
                         "On est ensemble mais l'autre parent vit ailleurs (Hors communaute)": "L'autre parent vit ailleurs (hors communauté)",
                         'Autre': 'Autre'}
_pourquoi_raw = col("Si c'est le cas  pourquoi ?")
pourquoi_seul_rows = crosstab_rows_fixed_order(_pourquoi_raw, POURQUOI_SEUL_ORDER)
pourquoi_seul_rows = [(POURQUOI_SEUL_LABELS[l], v) for l, v in pourquoi_seul_rows]

def age_bin_rows(raw_col_name):
    labels = ['Sans objet (0)', '<18 ans', '18-19 ans', '20-24 ans', '25-29 ans', '30 ans et plus']
    edges = [0, 1, 18, 20, 25, 30, float('inf')]
    binned = bin_series(col(raw_col_name), edges, labels)
    return crosstab_rows_from_bins(binned, labels)

age_union_rows = age_bin_rows('A quel ege avez-vous commence e vivre avec un partenaire (en mariage ou concubinage)?')
age_1erenfant_rows = age_bin_rows('Si vous en avez, e quel ege avez-vous eu votre premier enfant?')

conflit_24m_rows = crosstab_rows_fixed_order(
    col('Au cours des vingt-quatre derniers mois, avez-vous ete implique(e) dans un conflit avec une autre personne dans votre communaute ?'),
    ['Oui', 'Non'])

CONFLIT_TYPE_COLS = [
    ('Propriété de terrain', 'Propriete de terrain'),
    ('Accès à des ressources naturelles communautaires (eau, zones boisées, etc.)', 'Acces a des ressources communautaires naturelles (eau, zones boisees, ect)'),
    ('Problèmes liés au travail', 'Problemes lies au travail'),
    ('Problèmes liés à la politique', 'Problemes lies a la politique'),
    ("Problèmes liés à l'argent", "Problemes lies a l'argent"),
    ('Problèmes de voisinage', 'Problemes de voisinage'),
    ('Vol de produits agricoles', 'Vol de produits agricoles'),
    ('Vol de bétail', 'Vol de betail'),
]
conflit_type_opts = [(lbl, (col(rawc) == 'Oui').astype(int)) for lbl, rawc in CONFLIT_TYPE_COLS]
conflit_type_rows = crosstab_rows(conflit_type_opts)

RESOLUTION_COLS = [
    ('Propriété de terrain', 'Propriete de terrain.1'),
    ('Accès à des ressources naturelles', 'Acces a des ressources naturelles'),
    ('Problèmes liés au travail', 'Problemes lies au travail.1'),
    ('Problèmes liés à la politique', 'Problemes lies a la politique.1'),
    ("Problèmes liés à l'argent", "Problemes lies a l'argent.1"),
    ('Problèmes de voisinage', 'Problemes de voisinage.1'),
    ('Vol de produits agricoles', 'Vol de produits agricoles.1'),
    ('Vol de bétail', 'Vol de betail.1'),
]
RESOLUTION_MODES_ORDER = ["Mediation d'un proche", 'Religieux', 'Casec', 'Police', 'Tribunal', 'ONG']
RESOLUTION_LABELS = {"Mediation d'un proche": "Médiation d'un proche", 'Religieux': 'Religieux',
                      'Casec': 'CASEC', 'Police': 'Police', 'Tribunal': 'Tribunal', 'ONG': 'ONG'}

THEMES_SOCIAL = [
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="A participé à une corvée agricole (12 derniers mois)",
         rows=corvee_rows, multi=False, note="Question à réponse unique."),
    freq_block("Groupe de l'église", "Groupe de l'eglise"),
    freq_block("Association de quartier", "Association de quartier"),
    freq_block("OCB / association liée au travail", "OCB/association lie a votre travail"),
    freq_block("Groupe d'amis / famille", "Groupe d'amis/famille"),
    freq_block("Groupe politique", "Groupe politique"),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Membre d'une mutuelle d'épargne (MUSO, TIPA, etc.) ou d'une banque communautaire",
         rows=muso_rows, multi=False, note="Question à réponse unique."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Se sent en sécurité la nuit dans sa communauté",
         rows=securite_rows, multi=False, note="Question à réponse unique."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Si non, de quoi a peur (réponse libre reclassée par mots-clés)",
         rows=peur_rows, multi=True,
         note="Texte libre reclassé par mots-clés (une réponse peut couvrir plusieurs thèmes) — les % ne totalisent pas 100%. Base : n=223 répondants se sentant en insécurité. Classification indicative, à valider."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Pense que les nouveaux arrivants sont un danger pour la communauté",
         rows=danger_arrivants_rows, multi=False, note="Question à réponse unique."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Élève ses enfants seul(e)",
         rows=eleve_seul_rows, multi=False, note="Question à réponse unique."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Si oui, pourquoi",
         rows=pourquoi_seul_rows, multi=False,
         note="Base : répondants élevant leurs enfants seul(e)s (n=225). Question à réponse unique."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Âge au début de la vie en couple (mariage ou concubinage)",
         rows=age_union_rows, multi=False,
         note="« Sans objet (0) » = valeur 0 saisie dans la base (jamais vécu en couple ou non applicable) — à vérifier auprès de l'équipe terrain."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Âge au premier enfant",
         rows=age_1erenfant_rows, multi=False,
         note="« Sans objet (0) » = valeur 0 saisie dans la base (pas d'enfant ou non applicable) — à vérifier auprès de l'équipe terrain."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="A été impliqué(e) dans un conflit avec une autre personne de la communauté (24 derniers mois)",
         rows=conflit_24m_rows, multi=False, note="Question à réponse unique."),
    dict(category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
         question="Types de conflit rencontrés",
         rows=conflit_type_rows, multi=True,
         note="Question à choix multiples — les % ne totalisent pas 100%. Base réelle très faible : n=71 répondants ayant rapporté un conflit (5,9% de l'échantillon) ; à lire avec prudence, surtout au niveau des sous-groupes."),
]

for lbl, rawc in RESOLUTION_COLS:
    rows = crosstab_rows_fixed_order(col(rawc), RESOLUTION_MODES_ORDER)
    rows = [(RESOLUTION_LABELS[l], v) for l, v in rows]
    THEMES_SOCIAL.append(dict(
        category="L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE",
        question=f"Mode de résolution du conflit — {lbl}",
        rows=rows, multi=False,
        note="Question à réponse unique. Base extrêmement faible (quelques dizaines de répondants au maximum, souvent moins de 20) — lecture indicative uniquement, non représentative par sous-groupe."
    ))

THEMES5 = THEMES_SOCIAL

if __name__ == '__main__':
    for t in THEMES5:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 6 : education, soutien social, securite alimentaire, migration
# =====================================================================

scol_main = 'Avez-vous ete scolarise ?'
scolarise_opts = [
    ("Oui et j'ai arrêté avant la fin du parcours scolaire", col(scol_main + "/Oui et j'ai arrete avant la fin du parcours scolaire")),
    ("Non, je n'ai jamais été à l'école", col(scol_main + "/Non, je n'ai jamais ete a l'ecole")),
    ("Oui et j'ai eu mon diplôme de philo", col(scol_main + "/Oui et j'ai eu mon dipleme de philo")),
    ("Oui, je suis encore à l'école", col(scol_main + "/Oui, je suis encore a l'ecole")),
]
scolarise_rows = crosstab_rows(scolarise_opts)

niveau_labels = ['1-3 (primaire, 1er cycle)', '4-6 (primaire, 2e cycle)', '7-9 (secondaire, 1er cycle)']
niveau_binned = bin_series(col('Si vous avez arrete, a quel niveau ?'), [1,4,7,10], niveau_labels)
niveau_rows = crosstab_rows_from_bins(niveau_binned, niveau_labels)

soucis_main = "Partagez-vous vos soucis avec quelqu'un de confiance dans la communaute, quand vous en avez ?"
soucis_opts = [
    ('Membre de la famille', col(soucis_main + '/Membre de la famille')),
    ('Non (ne partage pas)', col(soucis_main + '/Non')),
    ('Mon ou ma compagne', col(soucis_main + '/Mon ou ma compagne')),
    ('Ami(e)', col(soucis_main + '/Ami (e)')),
    ('Représentant religieux', col(soucis_main + '/Representant religieux')),
    ('Autre', col(soucis_main + '/Autre')),
]
soucis_rows = crosstab_rows(soucis_opts)

DETENTE_KEYWORDS = {
    'Football / sport': ['football', 'foutbol', 'foutbel', 'sport', 'match', 'championnat'],
    'Musique / chant': ['musique', 'mizik', 'chante'],
    'Domino / jeux': ['domino', 'jwe kat', 'kat '],
    'Commerce / business': ['komes', 'commerce', 'biznis', 'business'],
    'Église / religion': ["l'eglise", 'legliz', 'eglise', "aller e l'eglise"],
    'Gaguère (combats de coqs)': ['gage', 'gaguere', 'guaguere'],
    'Médias / réseaux sociaux': ['radio', 'reseaux sociaux', 'video', 'telephone', 'tande mizik'],
    'Agriculture / travail': ['agriculture', 'travail', 'travay'],
    'Rien / aucune activité': ['anyen', 'aucun', 'rien', 'repo'],
}
detente_rows = keyword_multi_rows(col('Quelle(s) activite(s) vous parait la plus propice pour vous detendre ?'), DETENTE_KEYWORDS)

FIES_ITEMS = [
    ("Inquiet(e) de ne pas avoir suffisamment de nourriture", 'Ete inquiets de ne pas avoir suffisamment de nourriture ?'),
    ("N'a pas pu manger une nourriture saine et nutritive", "N'avez pas pu manger une nourriture saine et nutritive ?"),
    ("A mangé une nourriture peu variée", 'Avez mange une nourriture peu variee'),
    ("A dû sauter un repas", 'Avez de sauter un repas'),
    ("A mangé moins que ce qu'il/elle pensait devoir manger", 'Avez mange moins que ce que vous pensiez que vous auriez de'),
    ("Le foyer n'avait plus de nourriture", "N'avait plus de nourriture"),
    ("A eu faim mais n'a pas mangé", "Avez eu faim mais vous n'avez pas mange"),
    ("A passé toute une journée sans manger", 'Avez passe toute une journee sans manger'),
]
fies_theme_rows = [(lbl, crosstab_rows_fixed_order(col(rawc), ['Oui', 'Non'])) for lbl, rawc in FIES_ITEMS]

cantine_labels = ['0', '1', '2', '3 et plus']
cantine_binned = bin_series(col("Combien de vos enfants beneficient d'un programme de cantine scolaire?"), [0,1,2,3,float('inf')], cantine_labels)
cantine_rows = crosstab_rows_from_bins(cantine_binned, cantine_labels)

DOC_STATUS_ORDER = ["Oui, je l'ai", 'Démarches en cours', 'Non']
_doc_status_map = {"Oui, je l'ai": "Oui, je l'ai", 'Demarches en cours': 'Démarches en cours', 'Non': 'Non'}
DOC2_COLS = [
    ('Acte de naissance', 'Acte de naissance.1'),
    ("Carte d'identification nationale", "Carte d'identification nationale.1"),
    ('Passeport', 'Passeport.1'),
    ("Carte d'électeur", "Carte d'electeur.1"),
    ('Permis de conduire', 'Permis de conduire.1'),
]

accueil_labels = ['0', '1', '2', '3', '4 et plus']
accueil_binned = bin_series(col("Combien de personnes, fuyant des zones d'insecurite, avez-vous accueillies pendant les cinq dernieres annees, dans votre foyer?"), [0,1,2,3,4,float('inf')], accueil_labels)
accueil_rows = crosstab_rows_from_bins(accueil_binned, accueil_labels)

accueil_femmes_binned = bin_series(col('Combien de femmes ?'), [0,1,2,3,4,float('inf')], accueil_labels)
accueil_femmes_rows = crosstab_rows_from_bins(accueil_femmes_binned, accueil_labels)

migr_labels = ['0', '1', '2', '3 et plus']
migr_binned = bin_series(col('Combien de personnes au niveau de votre menage ont voyage vers un pays etranger pendant les cinq dernieres annees?'), [0,1,2,3,float('inf')], migr_labels)
migr_rows = crosstab_rows_from_bins(migr_binned, migr_labels)

migr_femmes_binned = bin_series(col('Combien de femmes il y a parmi les personnes de votre menage qui ont laisse le pays pendant les cinq dernieres annees?'), [0,1,2,3,float('inf')], migr_labels)
migr_femmes_rows = crosstab_rows_from_bins(migr_femmes_binned, migr_labels)

etranger_main = "Oe sont-ils e l'etranger?"
etranger_opts = [
    ('États-Unis', col(etranger_main + '/Etats-Unis')),
    ('Autre pays', col(etranger_main + '/Autre')),
    ('République dominicaine', col(etranger_main + '/Republique Dominicaine')),
    ('Canada', col(etranger_main + '/Canada')),
    ('Brésil', col(etranger_main + '/Bresil')),
    ('Chili', col(etranger_main + '/Chili')),
    ('Mexique', col(etranger_main + '/Mexique')),
    ('Guyane française', col(etranger_main + '/Guyane franeaise')),
    ('Bahamas', col(etranger_main + '/Bahamas')),
    ('Martinique', col(etranger_main + '/Martinique')),
    ('France', col(etranger_main + '/France')),
    ('Guadeloupe', col(etranger_main + '/Guadeloupe')),
]
etranger_rows = crosstab_rows(etranger_opts)

THEMES6 = [
    dict(category="M. ÉDUCATION ET SOUTIEN SOCIAL",
         question="A été scolarisé",
         rows=scolarise_rows, multi=True,
         note="Question à choix multiples (rares réponses combinées) — les % ne totalisent pas 100%."),
    dict(category="M. ÉDUCATION ET SOUTIEN SOCIAL",
         question="Si arrêté avant la fin, à quel niveau (années de scolarité)",
         rows=niveau_rows, multi=False,
         note="Base : répondants ayant arrêté l'école avant la fin du parcours (n=562)."),
    dict(category="M. ÉDUCATION ET SOUTIEN SOCIAL",
         question="Partage ses soucis avec quelqu'un de confiance dans la communauté",
         rows=soucis_rows, multi=True,
         note="Question à choix multiples — les % ne totalisent pas 100%."),
    dict(category="M. ÉDUCATION ET SOUTIEN SOCIAL",
         question="Activité perçue comme la plus propice pour se détendre (réponse libre reclassée par mots-clés)",
         rows=detente_rows, multi=True,
         note="Texte libre reclassé par mots-clés (une réponse peut couvrir plusieurs activités) — les % ne totalisent pas 100%. Classification indicative, à valider."),
]

for lbl, rows in fies_theme_rows:
    THEMES6.append(dict(
        category="N. SÉCURITÉ ALIMENTAIRE (12 DERNIERS MOIS)",
        question=lbl, rows=rows, multi=False,
        note="Question à réponse unique. Item du module d'échelle de sécurité alimentaire (type FIES)."
    ))

THEMES6.append(dict(
    category="N. SÉCURITÉ ALIMENTAIRE (12 DERNIERS MOIS)",
    question="Nombre d'enfants bénéficiant d'un programme de cantine scolaire",
    rows=cantine_rows, multi=False, note="Question à réponse unique."
))

for lbl, rawc in DOC2_COLS:
    raw = col(rawc).map(_doc_status_map)
    rows = crosstab_rows_fixed_order(raw, DOC_STATUS_ORDER)
    THEMES6.append(dict(
        category="M. ÉDUCATION ET SOUTIEN SOCIAL",
        question=f"Dispose de : {lbl}",
        rows=rows, multi=False, note="Question à réponse unique."
    ))

THEMES6 += [
    dict(category="O. MIGRATION",
         question="Nombre de personnes fuyant des zones d'insécurité accueillies dans le foyer (5 dernières années)",
         rows=accueil_rows, multi=False, note="Question à réponse unique."),
    dict(category="O. MIGRATION",
         question="Dont nombre de femmes",
         rows=accueil_femmes_rows, multi=False, note="Base : foyers ayant accueilli des personnes fuyant l'insécurité."),
    dict(category="O. MIGRATION",
         question="Nombre de personnes du ménage ayant voyagé/émigré vers un pays étranger (5 dernières années)",
         rows=migr_rows, multi=False, note="Question à réponse unique."),
    dict(category="O. MIGRATION",
         question="Dont nombre de femmes",
         rows=migr_femmes_rows, multi=False, note="Base : foyers ayant des membres partis à l'étranger."),
    dict(category="O. MIGRATION",
         question="Où sont-ils à l'étranger",
         rows=etranger_rows, multi=True,
         note="Question à choix multiples (plusieurs destinations possibles par foyer) — les % ne totalisent pas 100%. Base : foyers ayant des membres partis à l'étranger."),
]

if __name__ == '__main__':
    for t in THEMES6:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 7 : moyens de subsistance, epargne, credit, foncier, migration eco.
# =====================================================================

import re

NSP_PATTERNS = ['pa konnen', 'pa sonje', 'ne sait pas', "sais pas"]
ZERO_PATTERNS = ['okenn', 'oken', 'ras', 'aucun', 'zero', r'^non$', r'^nn$', r'^o$', 'pa gen', 'pa resevwa', 'mwen pa resevwa']

def parse_amount_bucket(raw_text):
    """Classe un montant en texte libre en : 'Aucun (0)', 'Ne sait pas / non précisé', ou renvoie un float (gourdes)."""
    if pd.isna(raw_text):
        return None
    s = str(raw_text).strip().lower()
    if s == '':
        return None
    for p in NSP_PATTERNS:
        if re.search(p, s):
            return 'NSP'
    for p in ZERO_PATTERNS:
        if re.search(p, s):
            return 0.0
    m = re.search(r'(\d+(?:[.,]\d+)?)', s.replace(' ', ''))
    if m:
        try:
            return float(m.group(1).replace(',', '.'))
        except ValueError:
            return 'NSP'
    return 'NSP'

def amount_bins(raw_series, edges, labels, nsp_label='Ne sait pas / non précisé'):
    parsed = raw_series.apply(parse_amount_bucket)
    out = pd.Series(index=raw_series.index, dtype=object)
    for idx, v in parsed.items():
        if v is None:
            continue
        elif v == 'NSP':
            out[idx] = nsp_label
        else:
            for i, lab in enumerate(labels):
                lo, hi = edges[i], edges[i+1]
                if hi == float('inf'):
                    if v >= lo:
                        out[idx] = lab
                        break
                else:
                    if lo <= v < hi:
                        out[idx] = lab
                        break
    all_labels = labels + [nsp_label]
    return crosstab_rows_from_bins(out, all_labels)

# --- 1. Processus pour partir a l'etranger ---
depart_etranger_rows = crosstab_rows_fixed_order(col('Avez-vous entame un processus pour partir definitivement e leetranger ?'), ['Oui', 'Non'])

# --- 2. Souhaite enfants restent au village ---
enfants_village_rows = crosstab_rows_fixed_order(col('Souhaitez-vous que vos enfants restent au village soit en reprenant votre activite agricole ou apres avoir etudie ?'), ['Oui', 'Non'])

# --- 3. Si non, pourquoi (texte libre) ---
POURQUOI_PARTIR_KEYWORDS = {
    'Insécurité': ['ensekirite', 'insecurite'],
    "Manque d'opportunités / économie": ['manque', "pa devlope", 'lavi miye', 'bon vi', 'peyi a pa bon', 'bonne vie'],
    'Pas d’enfants / non applicable': ["pas d'enfant", 'san timoun'],
}
pourquoi_partir_rows = keyword_multi_rows(col('Si non pourquoi ?'), POURQUOI_PARTIR_KEYWORDS)

# --- 4. Statut d'emploi (multi-select) ---
emploi_opts = [
    ("Salarié, contrat longue durée (+d'un an)", (col("Salarie avec un contrat de longue duree (plus d'un an?)") == 'Oui').astype(int)),
    ('Salarié, contrat courte durée (-3 mois)', (col('Salarie avec un contrat de courte duree (moins de trois mois) ?') == 'Oui').astype(int)),
    ('Salarié journalier sans contrat', (col('Salarie journalier sans contrat') == 'Oui').astype(int)),
    ('Auto-entrepreneur', (col('Auto-entrepreneur') == 'Oui').astype(int)),
    ('Sans emploi', (col('Sans emploi') == 'Oui').astype(int)),
]
emploi_rows = crosstab_rows(emploi_opts)

# --- 5. Revenu mensuel estime (bins) ---
revenu_labels = ['0 - 2 500 HTG', '2 501 - 6 500 HTG', '6 501 - 13 000 HTG', '13 001 - 30 000 HTG', '30 001 HTG et plus']
revenu_rows = amount_bins(col("Quel est votre revenu mensuel si vous pouvez l'estimer ou si vous le connaissez ?"),
                           [0, 2500, 6500, 13000, 30000, float('inf')], revenu_labels)

# --- 6. Compte dans institution financiere (multi-select) ---
compte_main = 'Avez-vous un compte dans une institution financiere ?'
compte_opts = [
    ('Banque commerciale', col(compte_main + '/Dans une banque commerciale')),
    ('Caisse populaire', col(compte_main + '/Dans une caisse populaire')),
    ('MUSO', col(compte_main + '/Dans une muso')),
    ('Autre', col(compte_main + '/Autre')),
]
compte_rows = crosstab_rows(compte_opts)

# --- 7. Droits sur terrain agricole ---
DROITS_TERRAIN_ORDER = [
    "J'ai un terrain avec un titre de propriete",
    "Non je n'ai pas de terres agricoles",
    'J\'ai acces e un terrain sous le regime "de-moitie"',
    'Je possede un terrain sous propriete coutumiere',
    'Je possede un terrain sans aucun droits',
    "J'afferme ou je loue un terrain",
    'Autre',
]
DROITS_TERRAIN_LABELS = {
    "J'ai un terrain avec un titre de propriete": "A un terrain avec titre de propriété",
    "Non je n'ai pas de terres agricoles": "N'a pas de terres agricoles",
    'J\'ai acces e un terrain sous le regime "de-moitie"': 'Accès à un terrain sous régime "de-moitié"',
    'Je possede un terrain sous propriete coutumiere': 'Terrain sous propriété coutumière',
    'Je possede un terrain sans aucun droits': 'Terrain sans aucun droit',
    "J'afferme ou je loue un terrain": 'Afferme ou loue un terrain',
    'Autre': 'Autre',
}
droits_terrain_rows = crosstab_rows_fixed_order(col('Avez-vous des droits sur un terrain agricole?'), DROITS_TERRAIN_ORDER)
droits_terrain_rows.sort(key=lambda x: -x[1]['Total'])
droits_terrain_rows = [(DROITS_TERRAIN_LABELS[l], v) for l, v in droits_terrain_rows]

# --- 8. Si possede un terrain, peut ... (multi-select Oui/Non chacun) ---
terrain_actions = [
    ('Le vendre', 'Le vendre'),
    ('Le donner en héritage', 'Le donner en heritage'),
    ('Le mettre en fermage', 'Le mettre en fermage'),
    ("L'exploiter à moitié", "L'exploiter e moitie"),
]
terrain_action_opts = [(lbl, (col(rawc) == 'Oui').astype(int)) for lbl, rawc in terrain_actions]
terrain_action_rows = crosstab_rows(terrain_action_opts)

# --- 9. Economies / filet de securite ---
economies_rows = crosstab_rows_fixed_order(col('Avez-vous des economies ou tout autre filet de securite autre que les proprietes foncieres?'), ['Oui', 'Non'])

# --- 10. Sous quelle forme (texte libre) ---
FORME_EPARGNE_KEYWORDS = {
    'Aucune': ['okenn', 'oken', 'ras', 'aucun', r'^non$', 'pa genyen', 'pa gen', '^0$'],
    'Espèces (cash, coffre)': ['cash', 'lajan', "l'argent", 'coffre', 'kane'],
    'Bétail / élevage': ['vann bet', 'elevage', 'elvaj', 'betail', r'\bbet\b'],
    'Mutuelle / épargne collective': ['mutuelle', 'muso', 'tipa'],
}
forme_epargne_rows = keyword_multi_rows(col('Si oui, sous quelle forme ?.1'), FORME_EPARGNE_KEYWORDS)

# --- 11. Duree de resilience des economies (texte libre parse) ---
def parse_duration_months(text):
    if pd.isna(text):
        return None
    s = str(text).strip().lower()
    if s == '':
        return None
    if any(k in s for k in ['pa konnen', 'pa sonje', 'pap travay', 'mpap travay', r'^wi$', r'^non$']):
        return 'NSP'
    m = re.search(r'(\d+)', s)
    if not m:
        return 'NSP'
    n = int(m.group(1))
    if re.search(r'\b(an|ane|ans|zan)\b', s) or 'an' in s.replace('mwa','').replace('mois',''):
        # heuristique : presence de 'an'/'ane'/'ans' hors 'mwa'/'mois' -> annees
        if re.search(r'an', s) and not re.search(r'mwa|mois', s):
            return n * 12
    if re.search(r'mwa|mois', s):
        return n
    if re.search(r'\ban\b|ane|ans|zan', s):
        return n * 12
    return 'AMBIGU'

def duree_resilience_rows(raw_series):
    labels = ['Moins de 3 mois', '3 à 5 mois', '6 à 11 mois', '1 an et plus', 'Ne sait pas / non applicable', 'Format non précisé']
    out = pd.Series(index=raw_series.index, dtype=object)
    for idx, val in raw_series.items():
        months = parse_duration_months(val)
        if months is None:
            continue
        elif months == 'NSP':
            out[idx] = 'Ne sait pas / non applicable'
        elif months == 'AMBIGU':
            out[idx] = 'Format non précisé'
        elif months < 3:
            out[idx] = 'Moins de 3 mois'
        elif months < 6:
            out[idx] = '3 à 5 mois'
        elif months < 12:
            out[idx] = '6 à 11 mois'
        else:
            out[idx] = '1 an et plus'
    return crosstab_rows_from_bins(out, labels)

duree_resilience_rows_result = duree_resilience_rows(col('Combien de temps pensez-vous pouvoir vivre de vos economies si vous perdez votre emploi ou votre source de revenus ?'))

# --- 12. Transferts de fonds reguliers ---
TRANSFERT_ORDER = [
    "Non je n'en recois pas",
    'Oui de temps en temps, pas regulierement',
    'Oui tous les 3 mois ou 6 mois',
    'Oui tous les mois',
    'Oui, toutes les semaines',
]
TRANSFERT_LABELS = {
    "Non je n'en recois pas": "Non, n'en reçoit pas",
    'Oui de temps en temps, pas regulierement': 'Oui, de temps en temps (pas régulier)',
    'Oui tous les 3 mois ou 6 mois': 'Oui, tous les 3 à 6 mois',
    'Oui tous les mois': 'Oui, tous les mois',
    'Oui, toutes les semaines': 'Oui, toutes les semaines',
}
transferts_rows = crosstab_rows_fixed_order(col('Recevez vous des transferts de fonds regulierement?'), TRANSFERT_ORDER)
transferts_rows = [(TRANSFERT_LABELS[l], v) for l, v in transferts_rows]

# --- 13. Montant recu (12 mois) bins ---
montant_recu_labels = ['0 (aucun)', '1 - 10 000 HTG', '10 001 - 50 000 HTG', '50 001 - 150 000 HTG', '150 001 HTG et plus']
montant_recu_rows = amount_bins(col('Pourriez vous nous donner une estimation du montant recu durant les 12 derniers mois ?'),
                                 [0.0001, 10000, 50000, 150000, float('inf')], montant_recu_labels[1:])
# reinsert the explicit zero bucket computed separately since amount_bins traite 0 comme le premier edge
def montant_recu_full():
    parsed = col('Pourriez vous nous donner une estimation du montant recu durant les 12 derniers mois ?').apply(parse_amount_bucket)
    out = pd.Series(index=parsed.index, dtype=object)
    labels = ['0 (aucun)', '1 - 10 000 HTG', '10 001 - 50 000 HTG', '50 001 - 150 000 HTG', '150 001 HTG et plus', 'Ne sait pas / non précisé']
    for idx, v in parsed.items():
        if v is None:
            continue
        if v == 'NSP':
            out[idx] = 'Ne sait pas / non précisé'
        elif v == 0:
            out[idx] = '0 (aucun)'
        elif v < 10000:
            out[idx] = '1 - 10 000 HTG'
        elif v < 50000:
            out[idx] = '10 001 - 50 000 HTG'
        elif v < 150000:
            out[idx] = '50 001 - 150 000 HTG'
        else:
            out[idx] = '150 001 HTG et plus'
    return crosstab_rows_from_bins(out, labels)
montant_recu_rows = montant_recu_full()

# --- 14. D'ou vient l'argent (multi-select pays) ---
envoi_main = "D'oe vous envoie t'on de l'argent ?"
envoi_opts = [
    ('États-Unis', col(envoi_main + '/Etats-Unis')),
    ('Autre pays', col(envoi_main + '/Autre')),
    ('République dominicaine', col(envoi_main + '/Republique Dominicaine')),
    ('Chili', col(envoi_main + '/Chili')),
    ('Canada', col(envoi_main + '/Canada')),
    ('France', col(envoi_main + '/France')),
    ('Brésil', col(envoi_main + '/Bresil')),
    ('Guyane française', col(envoi_main + '/Guyane franeaise')),
    ('Bahamas', col(envoi_main + '/Bahamas')),
    ('Martinique', col(envoi_main + '/Martinique')),
    ('Guadeloupe', col(envoi_main + '/Guadeloupe')),
    ('Mexique', col(envoi_main + '/Mexique')),
]
envoi_rows = crosstab_rows(envoi_opts)

# --- 15. Vers qui pour obtenir un credit ---
CREDIT_ORDER = [
    'Un proche dans la communaute', 'Mutuelle solidarite', 'Un proche en dehors de la communaute',
    'caisse populaire', 'Preteur sur gage', "banque commerciale d'etat (BNC, BUH, BPH..)", 'banque commerciale privee',
]
CREDIT_LABELS = {
    'Un proche dans la communaute': 'Un proche dans la communauté', 'Mutuelle solidarite': 'Mutuelle / solidarité',
    'Un proche en dehors de la communaute': 'Un proche hors de la communauté', 'caisse populaire': 'Caisse populaire',
    'Preteur sur gage': 'Prêteur sur gage', "banque commerciale d'etat (BNC, BUH, BPH..)": "Banque commerciale d'État (BNC, BUH, BPH…)",
    'banque commerciale privee': 'Banque commerciale privée',
}
credit_rows = crosstab_rows_fixed_order(col('Vers qui vous vous etes tournes ou bien vous tourneriez vous en priorite pour obtenir un credit/pret en priorite en cas de besoin ?'), CREDIT_ORDER)
credit_rows.sort(key=lambda x: -x[1]['Total'])
credit_rows = [(CREDIT_LABELS[l], v) for l, v in credit_rows]

# --- 16. Taux d'interet ---
def parse_rate_bucket(text):
    if pd.isna(text):
        return None
    s = str(text).strip().lower()
    if s == '':
        return None
    if any(k in s for k in ['pa konnen', 'ne sait pas']):
        return 'NSP'
    if any(k in s for k in ['san entere', 'san antere', 'sans interet', 'sans condition', 'pa gen entere', 'aucun', 'okenn', r'^non$', r'^0%?$']):
        return 0.0
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*%?', s)
    if m:
        try:
            return float(m.group(1).replace(',', '.'))
        except ValueError:
            return 'NSP'
    return 'NSP'

def taux_interet_rows():
    raw = col("Si vous le connaissez, quel est le taux d'interet pour ces credits obtenus ?")
    labels = ['0% / sans intérêt', '1-5%', '6-10%', '11-20%', 'Plus de 20%', 'Ne sait pas / non précisé']
    out = pd.Series(index=raw.index, dtype=object)
    for idx, val in raw.items():
        v = parse_rate_bucket(val)
        if v is None:
            continue
        if v == 'NSP':
            out[idx] = 'Ne sait pas / non précisé'
        elif v == 0:
            out[idx] = '0% / sans intérêt'
        elif v <= 5:
            out[idx] = '1-5%'
        elif v <= 10:
            out[idx] = '6-10%'
        elif v <= 20:
            out[idx] = '11-20%'
        else:
            out[idx] = 'Plus de 20%'
    return crosstab_rows_from_bins(out, labels)
taux_interet_rows_result = taux_interet_rows()

# --- 17. Montant minimum decent par mois (numerique propre) ---
montant_decent_labels = ['Moins de 15 000 HTG', '15 000 - 24 999 HTG', '25 000 - 34 999 HTG', '35 000 - 49 999 HTG', '50 000 HTG et plus']
montant_decent_edges = [0, 15000, 25000, 35000, 50000, float('inf')]
_montant_decent_col = col('Quel est le montant minimum dont votre menage a besoin pour vivre decemment par mois ?')
_binned_decent = bin_series(_montant_decent_col, montant_decent_edges, montant_decent_labels)
montant_decent_rows = crosstab_rows_from_bins(_binned_decent, montant_decent_labels)

THEMES7 = [
    dict(category="P. MIGRATION ÉCONOMIQUE ET ASPIRATIONS",
         question="A entamé un processus pour partir définitivement à l'étranger",
         rows=depart_etranger_rows, multi=False, note="Question à réponse unique."),
    dict(category="P. MIGRATION ÉCONOMIQUE ET ASPIRATIONS",
         question="Souhaite que ses enfants restent au village (agriculture ou après études)",
         rows=enfants_village_rows, multi=False, note="Question à réponse unique."),
    dict(category="P. MIGRATION ÉCONOMIQUE ET ASPIRATIONS",
         question="Si non, pourquoi (réponse libre reclassée par mots-clés)",
         rows=pourquoi_partir_rows, multi=True,
         note="Texte libre reclassé par mots-clés — les % ne totalisent pas 100%. Classification indicative, à valider ; beaucoup de réponses ne correspondent à aucun mot-clé retenu."),
    dict(category="Q. EMPLOI ET REVENUS",
         question="Statut d'emploi",
         rows=emploi_rows, multi=True,
         note="Question à choix multiples — les % ne totalisent pas 100%."),
    dict(category="Q. EMPLOI ET REVENUS",
         question="Revenu mensuel estimé",
         rows=revenu_rows, multi=False,
         note="Montants extraits d'un champ texte libre (gourdes) ; réponses non numériques classées en « Ne sait pas / non précisé »."),
    dict(category="Q. EMPLOI ET REVENUS",
         question="Possède un compte dans une institution financière",
         rows=compte_rows, multi=True,
         note="Question à choix multiples — les % ne totalisent pas 100%."),
    dict(category="R. FONCIER AGRICOLE",
         question="Droits sur un terrain agricole",
         rows=droits_terrain_rows, multi=False, note="Question à réponse unique."),
    dict(category="R. FONCIER AGRICOLE",
         question="Si possède un terrain, peut...",
         rows=terrain_action_rows, multi=True,
         note="Question à choix multiples — les % ne totalisent pas 100%. Base : propriétaires/détenteurs de droits fonciers."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="A des économies ou un autre filet de sécurité (hors foncier)",
         rows=economies_rows, multi=False, note="Question à réponse unique."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Si oui, sous quelle forme (réponse libre reclassée par mots-clés)",
         rows=forme_epargne_rows, multi=True,
         note="Texte libre reclassé par mots-clés — les % ne totalisent pas 100%. Classification indicative, à valider."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Temps de résilience estimé grâce aux économies (perte d'emploi/revenus)",
         rows=duree_resilience_rows_result, multi=False,
         note="Durées extraites d'un champ texte libre (mois/années, créole et français mêlés) — parsing indicatif, à valider. « Format non précisé » = valeur numérique sans unité claire."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Reçoit des transferts de fonds régulièrement",
         rows=transferts_rows, multi=False, note="Question à réponse unique."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Montant reçu en transferts (12 derniers mois)",
         rows=montant_recu_rows, multi=False,
         note="Montants extraits d'un champ texte libre (gourdes) ; réponses non numériques classées en « Ne sait pas / non précisé ». Base : répondants recevant des transferts."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="D'où vient l'argent envoyé",
         rows=envoi_rows, multi=True,
         note="Question à choix multiples (plusieurs origines possibles) — les % ne totalisent pas 100%. Base : répondants recevant des transferts."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Vers qui se tourner en priorité pour obtenir un crédit/prêt",
         rows=credit_rows, multi=False, note="Question à réponse unique."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Taux d'intérêt connu pour ces crédits",
         rows=taux_interet_rows_result, multi=False,
         note="Taux extraits d'un champ texte libre — parsing indicatif, à valider."),
    dict(category="S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE",
         question="Montant minimum nécessaire au foyer pour vivre décemment par mois",
         rows=montant_decent_rows, multi=False, note="Question à réponse unique (montant en gourdes)."),
]

if __name__ == '__main__':
    for t in THEMES7:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 8 : agriculture (1/n) - pratiques generales, cultures, intrants
# =====================================================================

pratique_agri_rows = crosstab_rows_fixed_order(col("Pratiquez-vous, vous meme, l'agriculture ? "), ['Oui', 'Non'])

CROP_COLS = [
    ('Maïs', 'Maes'), ('Pois congo', 'Pois Congo'), ('Banane', 'Banane'), ('Patate', 'Patate'),
    ('Haricot', 'Haricot'), ('Igname', 'Igname'), ('Manioc', 'Manioc'), ('Sorgho / petit mil', 'Sorgho/petit mil'),
    ('Pistache (arachide)', 'Pistache'), ('Patate douce', 'Patate douce'), ('Malanga', 'Malanga'),
    ('Café', 'Cafe'), ('Gombo', 'Gombo'), ('Ananas', 'Ananas'), ('Riz', 'Riz'), ('Autre', 'Autre'),
    ('Tomate', 'Tomate'), ('Chou', 'Chou'), ('Carotte', 'Carotte'), ('Aubergine', 'Aubergine'),
    ('Mazonbèl', 'Mazonbel'), ('Oignon', 'Oignon'), ('Betterave', 'Betterave'),
    ('Ne souhaite pas répondre', 'Ne souhaite pas repondre'),
]
crop_opts = [(lbl, col(rawc).notna().astype(int)) for lbl, rawc in CROP_COLS]
crop_rows = crosstab_rows(crop_opts)

TREE_COLS = [
    ('Manguier', 'Manguier'), ('Avocatier', 'Avocatier'), ('Arbre véritable (fruit à pain)', 'Arbre veritable (fruit e pain)'),
    ('Cocotier', 'Cocotier'), ('Cachiman', 'Cachiman'), ('Oranger', 'Oranger'), ('Corrossolier', 'Corrossolier'),
    ('Citronnier', 'Citronnier'), ('Labapen', 'Labapen'), ('Papaye', 'Papaye'), ('Anacardier (noix)', 'Anarcardier (noix)'),
    ('Grenadia', 'Grenadia'), ('Cacao', 'Cacao'), ('Cerisier', 'Cerisier'), ('Grenadine', 'Grenadine'),
    ('Grenade', 'Grenade'), ('Fruit de la passion', 'Fruit de la passion'), ('Ne souhaite pas répondre', 'Ne souhaite pas repondre.1'),
]
tree_opts = [(lbl, col(rawc).notna().astype(int)) for lbl, rawc in TREE_COLS]
tree_rows = crosstab_rows(tree_opts)

def rotation_rows_fn():
    raw = col('Quelles rotations culturales avez-vous realisees pendant un cycle agricole ?')
    labels = ['Aucune rotation (monoculture)', '2 cultures', '3 cultures', '4 cultures',
              '5 cultures et plus', 'Plusieurs (nombre non précisé)', 'Autre / non précisé']
    out = pd.Series(index=raw.index, dtype=object)
    for idx, val in raw.items():
        if pd.isna(val):
            continue
        s = str(val).strip().lower()
        if re.search(r'pas de rotation|^aucune$|monoculture|une seule culture|^1$', s):
            out[idx] = 'Aucune rotation (monoculture)'
        elif re.search(r'^2$', s):
            out[idx] = '2 cultures'
        elif re.search(r'^3$', s):
            out[idx] = '3 cultures'
        elif re.search(r'^4$', s):
            out[idx] = '4 cultures'
        elif re.search(r'^[5-9]$', s):
            out[idx] = '5 cultures et plus'
        elif re.search(r'plizye|plizie|polyculture', s):
            out[idx] = 'Plusieurs (nombre non précisé)'
        else:
            out[idx] = 'Autre / non précisé'
    return crosstab_rows_from_bins(out, labels)
rotation_rows = rotation_rows_fn()

FERTILITE_KEYWORDS = {
    'Fumier / engrais organique': ['fumier', 'fimye', 'compost', 'konpes'],
    'Rien / aucune pratique': ['anyen', 'rien', 'aucun', 'mpa fe', 'mwen pa fe'],
    'Sarclage / labour': ['saclage', 'sarclage', 'sakle', 'saklaj', 'laboure', 'labouraj', 'netwaye'],
    'Jachère / repos du sol': ['jachere', 'zachere', 'repo', 'repoze', 'poze'],
}
fertilite_rows = keyword_multi_rows(col('Comment maintenez-vous la fertilite de vos sols entre les cultures ?'), FERTILITE_KEYWORDS)

INTRANT_ORDER = ['Oui', 'Non', 'Ne souhaite pas repondre']
INTRANT_LABELS = {'Oui': 'Oui', 'Non': 'Non', 'Ne souhaite pas repondre': 'Ne souhaite pas répondre'}
def intrant_rows(rawc):
    rows = crosstab_rows_fixed_order(col(rawc), INTRANT_ORDER)
    return [(INTRANT_LABELS[l], v) for l, v in rows]

engrais_rows = intrant_rows('Utilisez vous des engrais azotes ?')
herbicides_rows = intrant_rows('Utilisez vous des herbicides ?')
insecticides_rows = intrant_rows('Utilisez vous des insecticides ?')
fongicides_rows = intrant_rows('Utilisez vous des fongicides ?')

THEMES8 = [
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Pratique personnellement l'agriculture",
         rows=pratique_agri_rows, multi=False, note="Question à réponse unique."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Cultures pratiquées",
         rows=crop_rows, multi=True,
         note="Question à choix multiples (plusieurs cultures possibles par foyer) — les % ne totalisent pas 100%. Base : répondants pratiquant l'agriculture (n=670)."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Arbres fruitiers cultivés",
         rows=tree_rows, multi=True,
         note="Question à choix multiples (plusieurs arbres possibles par foyer) — les % ne totalisent pas 100%. Base : répondants pratiquant l'agriculture."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Nombre de rotations culturales réalisées pendant un cycle agricole",
         rows=rotation_rows, multi=False,
         note="Réponses texte libre reclassées (chiffres et mentions créoles) — classification indicative, à valider."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Comment la fertilité des sols est maintenue entre les cultures (réponse libre reclassée par mots-clés)",
         rows=fertilite_rows, multi=True,
         note="Texte libre reclassé par mots-clés (une réponse peut couvrir plusieurs pratiques) — les % ne totalisent pas 100%. Classification indicative, à valider."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Utilise des engrais azotés",
         rows=engrais_rows, multi=False, note="Question à réponse unique. Base : répondants pratiquant l'agriculture."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Utilise des herbicides",
         rows=herbicides_rows, multi=False, note="Question à réponse unique. Base : répondants pratiquant l'agriculture."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Utilise des insecticides",
         rows=insecticides_rows, multi=False, note="Question à réponse unique. Base : répondants pratiquant l'agriculture."),
    dict(category="T. AGRICULTURE — PRATIQUES GÉNÉRALES",
         question="Utilise des fongicides",
         rows=fongicides_rows, multi=False, note="Question à réponse unique. Base : répondants pratiquant l'agriculture."),
]

if __name__ == '__main__':
    for t in THEMES8:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 9 : agriculture (2/n) - rendements annuels et evolution par culture
# =====================================================================

CROP_TREE_LABELS = [
    'Maïs', 'Haricot', 'Pois congo', 'Igname', 'Patate', 'Banane', 'Riz', 'Sorgho / petit mil',
    'Chou', 'Carotte', 'Aubergine', 'Manioc', 'Café', 'Oignon', 'Gombo (kalalou)', 'Tomate',
    'Betterave', 'Patate douce', 'Malanga', 'Mazonbèl', 'Pistache (arachide)', 'Ananas', 'Cacao',
    'Papaye', 'Cocotier', 'Cerisier', 'Oranger', 'Banane (variante 2)', 'Citronnier', 'Grenade',
    'Grenadia', 'Grenadine', 'Fruit de la passion', 'Corrossolier', 'Labapen',
    'Arbre véritable (fruit à pain)', 'Cachiman', 'Avocatier', 'Anacardier (noix)', 'Autre',
]

RENDEMENT_RAW_COLS = list(df.columns[604:644])   # 40 colonnes, question 'rendements annuels en KG'
EVOLUTION_RAW_COLS = list(df.columns[646:687])   # 41 colonnes, question 'evolution des rendements sur 5 ans'

RENDEMENT_ORDER = ['-de50', '50-100', '100-250', '250-500', '500-750', '750-1000', '+de1000']
RENDEMENT_LABELS = {
    '-de50': 'Moins de 50 kg', '50-100': '50-100 kg', '100-250': '100-250 kg', '250-500': '250-500 kg',
    '500-750': '500-750 kg', '750-1000': '750-1 000 kg', '+de1000': 'Plus de 1 000 kg',
}
EVOLUTION_ORDER = ['Augmentation', 'Stable', 'Diminution']

THEMES9_RENDEMENT = []
for label, rawc in zip(CROP_TREE_LABELS, RENDEMENT_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), RENDEMENT_ORDER)
    rows = [(RENDEMENT_LABELS[l], v) for l, v in rows]
    THEMES9_RENDEMENT.append(dict(
        category="U. AGRICULTURE — RENDEMENTS ANNUELS PAR CULTURE",
        question=f"Rendement annuel estimé (kg) — {label}",
        rows=rows, multi=False,
        note="Question à réponse unique. Base : répondants cultivant cette culture/cet arbre (échantillon parfois très faible pour les cultures peu répandues)."
    ))

THEMES9_EVOLUTION = []
for label, rawc in zip(CROP_TREE_LABELS + ['Ne souhaite pas répondre'], EVOLUTION_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), EVOLUTION_ORDER)
    THEMES9_EVOLUTION.append(dict(
        category="V. AGRICULTURE — ÉVOLUTION DES RENDEMENTS (5 ANS) PAR CULTURE",
        question=f"Évolution du rendement sur 5 ans — {label}",
        rows=rows, multi=False,
        note="Question à réponse unique. Base : répondants cultivant cette culture/cet arbre (échantillon parfois très faible pour les cultures peu répandues)."
    ))

if __name__ == '__main__':
    for t in THEMES9_RENDEMENT[:3]:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])
    for t in THEMES9_EVOLUTION[:3]:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])


# =====================================================================
# THEMES 10 : agriculture (3/n) - circonstances et % de perte par culture
# =====================================================================

CROP_TREE_LABELS_41 = CROP_TREE_LABELS + ['Ne souhaite pas répondre']

PERTE_CIRCONSTANCE_RAW_COLS = list(df.columns[710:751])
PERTE_PCT_RAW_COLS = list(df.columns[752:793])

CIRCONSTANCE_ORDER = ['Sur pied', 'Durant la recolte', 'Stockage', 'Transport', 'Vente', 'Transformation']
CIRCONSTANCE_LABELS = {
    'Sur pied': 'Sur pied (au champ)', 'Durant la recolte': 'Durant la récolte', 'Stockage': 'Stockage',
    'Transport': 'Transport', 'Vente': 'Vente', 'Transformation': 'Transformation',
}

PERTE_PCT_ORDER = ['-de10', '10', '20', '30', '40', '50', '60', '70', '80', '90', '+de90']
PERTE_PCT_LABELS = {
    '-de10': 'Moins de 10%', '10': '10%', '20': '20%', '30': '30%', '40': '40%', '50': '50%',
    '60': '60%', '70': '70%', '80': '80%', '90': '90%', '+de90': 'Plus de 90%',
}

THEMES10_CIRCONSTANCE = []
for label, rawc in zip(CROP_TREE_LABELS_41, PERTE_CIRCONSTANCE_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), CIRCONSTANCE_ORDER)
    rows = [(CIRCONSTANCE_LABELS[l], v) for l, v in rows]
    THEMES10_CIRCONSTANCE.append(dict(
        category="W. AGRICULTURE — CIRCONSTANCES DE PERTE DE PRODUCTION PAR CULTURE",
        question=f"Circonstance de perte la plus fréquente — {label}",
        rows=rows, multi=False,
        note="Question à réponse unique. Base : répondants cultivant cette culture/cet arbre (échantillon parfois très faible)."
    ))

THEMES10_PCT = []
for label, rawc in zip(CROP_TREE_LABELS_41, PERTE_PCT_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), PERTE_PCT_ORDER)
    rows = [(PERTE_PCT_LABELS[l], v) for l, v in rows]
    THEMES10_PCT.append(dict(
        category="X. AGRICULTURE — POURCENTAGE DE PRODUCTION PERDUE PAR CULTURE",
        question=f"Part de la production perdue — {label}",
        rows=rows, multi=False,
        note="Question à réponse unique. Base : répondants cultivant cette culture/cet arbre (échantillon parfois très faible)."
    ))

if __name__ == '__main__':
    for t in THEMES10_CIRCONSTANCE[:2]:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])
    for t in THEMES10_PCT[:2]:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 11 : peche
# =====================================================================

pratique_peche_rows = crosstab_rows_fixed_order(col('Pratiquez vous, vous meme, la peche ? '), ['Oui', 'Non'])

TECH_PECHE_MAIN = 'Quelles techniques de peche ?'
TECH_PECHE_COLS = [
    ('Filets bleus', 'Filets bleus'), ('Nasses', 'Nasses'), ("Ligne / palancre", 'Ligne/palancre'),
    ('Senne', 'Senne'), ('Batterie', 'Batterie'), ('Fusil / plongée', 'Fusil/plonge'), ('DCP', 'DCP'),
    ('Trois nappes', 'Trois nappes'), ('Folle', 'Folle'), ('Compresseur (narguilé/tube)', 'Compresseur (narguilet/tube)'),
    ('Autre', 'Autre'),
]
tech_peche_opts = [(lbl, col(TECH_PECHE_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in TECH_PECHE_COLS]
tech_peche_rows = crosstab_rows(tech_peche_opts)

EMBARCATION_COLS = [
    ('Bois fouillé (pirogue)', 'Bois fouille'), ('Bateau à bois à moteur', 'Bateau e bois e moteur'),
    ('Bateau à voile', 'Bateau e voile'), ('Fibre de verre à moteur', 'Fibre de verre e moteur'),
    ('Bateau senne', 'Bateau senne'), ('Autre', 'Autre.7'),
]
EMBARCATION_STATUT_ORDER = ['En propre', 'En location']
embarcation_theme_rows = []
for lbl, rawc in EMBARCATION_COLS:
    rows = crosstab_rows_fixed_order(col(rawc), EMBARCATION_STATUT_ORDER)
    embarcation_theme_rows.append((lbl, rows))

THEMES11_GENERAL = [
    dict(category="Y. PÊCHE — PRATIQUES GÉNÉRALES",
         question="Pratique personnellement la pêche",
         rows=pratique_peche_rows, multi=False, note="Question à réponse unique."),
    dict(category="Y. PÊCHE — PRATIQUES GÉNÉRALES",
         question="Techniques de pêche utilisées",
         rows=tech_peche_rows, multi=True,
         note="Question à choix multiples — les % ne totalisent pas 100%. Base : répondants pratiquant la pêche (n=78, échantillon faible)."),
]
for lbl, rows in embarcation_theme_rows:
    THEMES11_GENERAL.append(dict(
        category="Y. PÊCHE — PRATIQUES GÉNÉRALES",
        question=f"Embarcation utilisée — {lbl}",
        rows=rows, multi=False,
        note="Question à réponse unique (propriété/location). Base : répondants pratiquant la pêche et utilisant ce type d'embarcation (échantillon très faible, souvent < 10)."
    ))

# --- especes pechees et zone ---
SPECIES_LABELS = [
    'Sardes rouges', 'Colas', 'Crocos jaunes', 'Kaptenn', 'Kofre', 'Bécunes', 'Nèg', 'Pisquette',
    'Chirurgien', 'Sardine', 'Sar argenté', 'Cardino / Cardinal pourpre', 'Coco', 'Thon', 'Bonite',
    'Tazard', 'Balbaren', 'Bonite (2)', 'Mère balaou', 'Dorade', 'Vivaneau', 'Requin', 'Langouste',
    'Crevette', 'Triton', 'Lambi', 'Autre',
]
ZONE_RAW_COLS = list(df.columns[816:843])
ZONE_ORDER = ['Plateau', 'Grand fond']

THEMES11_ZONE = []
for label, rawc in zip(SPECIES_LABELS, ZONE_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), ZONE_ORDER)
    THEMES11_ZONE.append(dict(
        category="Z. PÊCHE — ESPÈCES PÊCHÉES ET ZONE",
        question=f"Zone de pêche — {label}",
        rows=rows, multi=False,
        note="Question à réponse unique. Base : répondants pêchant cette espèce (échantillon très faible, souvent < 10)."
    ))

# --- montant par sortie et par espece ---
MONTANT_RAW_COLS = list(df.columns[844:871])
MONTANT_ORDER = ['Moins de mille', 'Mille e 5 mille', '5 e 10 mille', '10 e 20 mille', '+ de 20 mille']
MONTANT_LABELS = {
    'Moins de mille': 'Moins de 1 000 HTG', 'Mille e 5 mille': '1 000 - 5 000 HTG',
    '5 e 10 mille': '5 000 - 10 000 HTG', '10 e 20 mille': '10 000 - 20 000 HTG', '+ de 20 mille': 'Plus de 20 000 HTG',
}
THEMES11_MONTANT = []
for label, rawc in zip(SPECIES_LABELS, MONTANT_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), MONTANT_ORDER)
    rows = [(MONTANT_LABELS[l], v) for l, v in rows]
    THEMES11_MONTANT.append(dict(
        category="AA. PÊCHE — MONTANT PAR SORTIE ET PAR ESPÈCE",
        question=f"Montant rapporté par sortie — {label}",
        rows=rows, multi=False,
        note="Question à réponse unique (montant en gourdes). Base : répondants pêchant cette espèce (échantillon très faible, souvent < 10)."
    ))

# --- moment le plus rentable par espece ---
MOMENT_RAW_COLS = list(df.columns[872:899])
MOMENT_ORDER = ['J', 'F', 'M', 'A', 'S', 'O', 'N', 'D']
MOMENT_LABELS = {'J': 'J (Janv./Juin/Juil. — code ambigu)', 'F': 'Février', 'M': 'M (Mars/Mai — code ambigu)',
                  'A': 'A (Avril/Août — code ambigu)', 'S': 'Septembre', 'O': 'Octobre', 'N': 'Novembre', 'D': 'Décembre'}
THEMES11_MOMENT = []
for label, rawc in zip(SPECIES_LABELS, MOMENT_RAW_COLS):
    rows = crosstab_rows_fixed_order(col(rawc), MOMENT_ORDER)
    rows = [(MOMENT_LABELS[l], v) for l, v in rows]
    THEMES11_MOMENT.append(dict(
        category="AB. PÊCHE — MOMENT LE PLUS RENTABLE PAR ESPÈCE",
        question=f"Mois le plus rentable — {label}",
        rows=rows, multi=False,
        note="Codes mensuels tels que saisis dans la base (lettre initiale du mois en français) : certains sont ambigus (M = Mars ou Mai, J = Janvier/Juin/Juillet, A = Avril/Août) — à clarifier avec l'équipe terrain avant usage. Base : répondants pêchant cette espèce (échantillon très faible, souvent < 10)."
    ))

if __name__ == '__main__':
    for t in THEMES11_GENERAL:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])
    for t in THEMES11_ZONE[:2] + THEMES11_MONTANT[:2] + THEMES11_MOMENT[:2]:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 12 : elevage (colonnes 899-971)
# =====================================================================

ELEVAGE_COLS = list(df.columns[899:972])

possede_elevage_rows = crosstab_rows_fixed_order(col("Avez vous en votre nom des animaux d'elevage "), ['Oui', 'Non'])

TYPE_ANIMAL_MAIN = 'Possedez vous en votre nom :'
TYPE_ANIMAL_COLS = [('Volailles', 'Vollailes'), ('Porcins', 'Porcins'), ('Caprins', 'Caprins'),
                     ('Bovins', 'Bovins'), ('Autre', 'Autre')]
type_animal_opts = [(lbl, col(TYPE_ANIMAL_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in TYPE_ANIMAL_COLS]
type_animal_rows = crosstab_rows(type_animal_opts)

# --- nombre d'animaux possedes personnellement (bins) ---
nb_labels = ['0', '1-5', '6-10', '11-20', '21 et plus']
nb_edges = [0, 1, 6, 11, 21, float('inf')]
nb_volailles_rows = crosstab_rows_from_bins(bin_series(col('Combien de volailles possedez-vous personnellement ?'), nb_edges, nb_labels), nb_labels)
nb_porcins_rows = crosstab_rows_from_bins(bin_series(col('Combien de porcins possedez-vous personnellement ?'), nb_edges, nb_labels), nb_labels)
nb_caprins_rows = crosstab_rows_from_bins(bin_series(col('Combien de caprins possedez-vous personnellement ?'), nb_edges, nb_labels), nb_labels)
nb_bovins_rows = crosstab_rows_from_bins(bin_series(col('Combien de bovins possedez-vous personnellement ?'), nb_edges, nb_labels), nb_labels)

# --- aliments donnes (texte libre, classification par mots-cles) ---
aliment_volailles_map = {
    'Maïs (mayi/maes)': ['mae', 'mayi', 'mais'],
    'Pitimi / sorgho': ['pitimi'],
    'Blé / concentré (son de blé, concentré)': ['ble', 'konsantre'],
}
aliment_volailles_rows = keyword_multi_rows(col('Quels aliments donnez-vous e vos vollailles ?'), aliment_volailles_map)

aliment_porcins_map = {
    'Son de blé': ['son de ble', 'sondeble', 'sonde ble', 'sondebleu', 'son deble', 'son debleu', 'sodeble'],
    'Restes de cuisine / déchets végétaux': ['po manje', 'pe manje', 'dechet', 'residus de cuisine', 'res rekot',
                                              'reste cuisine', 'res cuisine', 'tout bagay', 'residus des recoltes'],
    'Fruits (avocat, veritab, banane...)': ['avocat', 'zaboka', 'goyave', 'veritab', 'banann', 'mango'],
}
aliment_porcins_rows = keyword_multi_rows(col('Quels aliments donnez-vous e vos porcins ?'), aliment_porcins_map)

aliment_caprins_map = {
    'Herbe / fourrage (zèb, raje, fourrage)': ['zeb', 'herb', 'fourrag', 'fourag', 'raje', 'hrebre'],
    'Laissés en pâturage libre (mare/attaché dans la végétation)': ['mare nan raje', 'mare yo nan raje'],
}
aliment_caprins_rows = keyword_multi_rows(col('Quels aliments donnez-vous e vos caprins ?'), aliment_caprins_map)

aliment_bovins_map = {
    'Herbe / fourrage (zèb, herbe, fourrage, pâturage)': ['zeb', 'herb', 'fourrag', 'fourag', 'paturage', 'patiraj'],
    'Tim adanm / feuillage complémentaire': ['timadanm', 'timadann', 'fey bannann'],
}
aliment_bovins_rows = keyword_multi_rows(col('Quels aliments donnez-vous e vos bovins ?'), aliment_bovins_map)

THEMES12_GENERAL = [
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Possède des animaux d'élevage en son nom propre",
         rows=possede_elevage_rows, multi=False, note="Question à réponse unique."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Type d'animaux possédés personnellement",
         rows=type_animal_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants possédant des animaux d'élevage (n=675)."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Nombre de volailles possédées personnellement",
         rows=nb_volailles_rows, multi=False,
         note="Base : répondants possédant des volailles (n=455). % calculés sur la base fixe totale (voir bandeau)."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Nombre de porcins possédés personnellement",
         rows=nb_porcins_rows, multi=False,
         note="Base : répondants possédant des porcins (n=280). % calculés sur la base fixe totale (voir bandeau)."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Nombre de caprins possédés personnellement",
         rows=nb_caprins_rows, multi=False,
         note="Base : répondants possédant des caprins (n=398). % calculés sur la base fixe totale (voir bandeau)."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Nombre de bovins possédés personnellement",
         rows=nb_bovins_rows, multi=False,
         note="Base : répondants possédant des bovins (n=317). % calculés sur la base fixe totale (voir bandeau)."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Aliments donnés aux volailles",
         rows=aliment_volailles_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés, à valider. Un répondant peut citer plusieurs aliments."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Aliments donnés aux porcins",
         rows=aliment_porcins_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés, à valider. Un répondant peut citer plusieurs aliments."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Aliments donnés aux caprins",
         rows=aliment_caprins_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés, à valider. Un répondant peut citer plusieurs aliments."),
    dict(category="AC. ÉLEVAGE — GÉNÉRALITÉS", question="Aliments donnés aux bovins",
         rows=aliment_bovins_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés, à valider. Un répondant peut citer plusieurs aliments."),
]

# --- mortalite (nombre de betes mortes, 12 derniers mois) ---
mort_labels = ['0', '1-5', '6-10', '11-20', '21 et plus']
mort_edges = [0, 1, 6, 11, 21, float('inf')]
mort_volailles_rows = crosstab_rows_from_bins(bin_series(col("Quelle a ete la mortalite dans votre elevage de volailles au cours de l'annee derniere ?"), mort_edges, mort_labels), mort_labels)
mort_porcins_rows = crosstab_rows_from_bins(bin_series(col("Quelle a ete la mortalite dans votre elevage de porcs au cours de l'annee derniere ?"), mort_edges, mort_labels), mort_labels)
mort_caprins_rows = crosstab_rows_from_bins(bin_series(col("Quelle a ete la mortalite dans votre elevage de caprins au cours de l'annee derniere ?"), mort_edges, mort_labels), mort_labels)
mort_bovins_rows = crosstab_rows_from_bins(bin_series(col("Quelle a ete la mortalite dans votre elevage de bovins au cours de l'annee derniere ?"), mort_edges, mort_labels), mort_labels)

CAUSE_MORT_OPTS = [('Maladies infectieuses', 'Maladies Infectieuses'), ('Parasites', 'Parasites'),
    ('Problèmes nutritionnels (manque de nourriture)', 'Problemes Nutritionnels (manque de nourriture)'),
    ('Accidents', 'Accidents'), ('Problèmes de gestion', 'Problemes de Gestion'),
    ('Problèmes génétiques', 'Problemes Genetiques'), ('Attaque autre animal', 'Attaque autre animal'),
    ("Attaque par l'homme (machette, magie, empoisonnement, vol...)", "Attaque par l'homme (machette, magie, empoisement, vol,....)"),
    ('Catastrophes naturelles', 'Catastrophes naturelles'), ('Autre', 'Autre')]

def cause_mortalite_rows(main_q):
    opts = [(lbl, col(main_q + '/' + rawc).fillna(0)) for lbl, rawc in CAUSE_MORT_OPTS]
    return crosstab_rows(opts)

cause_mort_volailles_rows = cause_mortalite_rows('Quelle est la cause principale de la mortalite dans votre elevage de volailles ?')
cause_mort_porcins_rows = cause_mortalite_rows('Quelle est la cause principale de la mortalite dans votre elevage de porcins?')
cause_mort_caprins_rows = cause_mortalite_rows('Quelle est la cause principale de la mortalite dans votre elevage de caprins ?')
cause_mort_bovins_rows = cause_mortalite_rows('Quelle est la cause principale de la mortalite dans votre elevage de bovins ?')

THEMES12_MORTALITE = [
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Mortalité dans l'élevage de volailles au cours des 12 derniers mois (nombre de bêtes)",
         rows=mort_volailles_rows, multi=False, note="Base : répondants possédant des volailles (n=453 ayant répondu)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Cause principale de la mortalité — volailles",
         rows=cause_mort_volailles_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants ayant renseigné une cause (n=389)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Mortalité dans l'élevage de porcins au cours des 12 derniers mois (nombre de bêtes)",
         rows=mort_porcins_rows, multi=False, note="Base : répondants possédant des porcins (n=274 ayant répondu)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Cause principale de la mortalité — porcins",
         rows=cause_mort_porcins_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants ayant renseigné une cause (n=170)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Mortalité dans l'élevage de caprins au cours des 12 derniers mois (nombre de bêtes)",
         rows=mort_caprins_rows, multi=False, note="Base : répondants possédant des caprins (n=391 ayant répondu)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Cause principale de la mortalité — caprins",
         rows=cause_mort_caprins_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants ayant renseigné une cause (n=271)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Mortalité dans l'élevage de bovins au cours des 12 derniers mois (nombre de bêtes)",
         rows=mort_bovins_rows, multi=False, note="Base : répondants possédant des bovins (n=304 ayant répondu)."),
    dict(category="AD. ÉLEVAGE — MORTALITÉ", question="Cause principale de la mortalité — bovins",
         rows=cause_mort_bovins_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants ayant renseigné une cause (n=121)."),
]

# --- facteur limitant les benefices (peche/agriculture/elevage confondus) ---
FACTEUR_MAIN = "Quel est le facteur principal qui vous empreche de realiser de meilleurs benefices (tant peche, agriculture qu'elevage)"
FACTEUR_OPTS = [
    ('Meilleures conditions pour conserver mes produits', 'Meilleures conditions pour conserver mes produits'),
    ('La distance aux marchés', 'La distance aux marches'),
    ('Les conditions de transport de mes produits', 'Les conditions de transport de mes produits'),
    ('La capacité financière pour augmenter mon fonds de commerce', 'La capacite financiere pour augmenter mon fonds de commerce'),
    ("La capacité des acheteurs à acheter au prix que je souhaiterais vendre", 'La capacite des acheteurs a acheter au prix que je souhaiterai vendre'),
    ('Autre', 'Autre'),
]
facteur_opts = [(lbl, col(FACTEUR_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in FACTEUR_OPTS]
facteur_rows = crosstab_rows(facteur_opts)

THEMES12_FACTEURS = [
    dict(category="AE. FACTEUR LIMITANT LES BÉNÉFICES (PÊCHE / AGRICULTURE / ÉLEVAGE)",
         question="Facteur principal empêchant de réaliser de meilleurs bénéfices",
         rows=facteur_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants ayant répondu (n=998)."),
]

if __name__ == '__main__':
    for t in THEMES12_GENERAL + THEMES12_MORTALITE + THEMES12_FACTEURS:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# Liste maitresse de tous les themes/questions (utilisee pour les
# classeurs "toutes questions par section communale")
# =====================================================================
ALL_THEMES_FULL = (
    THEMES + THEMES2 + THEMES3 + THEMES4 + THEMES5 + THEMES6 + THEMES7 + THEMES8 +
    THEMES9_RENDEMENT + THEMES9_EVOLUTION + THEMES10_CIRCONSTANCE + THEMES10_PCT +
    THEMES11_GENERAL + THEMES11_ZONE + THEMES11_MONTANT + THEMES11_MOMENT +
    THEMES12_GENERAL + THEMES12_MORTALITE + THEMES12_FACTEURS
)

# =====================================================================
# THEMES 13 : composition du foyer et sources de revenus
# (module initialement omis - colonnes ~13-208, en amont du bloc "energie"
#  par lequel les traitements avaient commence)
# =====================================================================

nb_adultes_order = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15 et plus']
nb_adultes_rows = crosstab_rows_fixed_order(col('Combien deadultes vivent dans votre foyer, y compris vous meme ?'), nb_adultes_order)

nb_adultes_dep_labels = ['0', '1', '2', '3', '4 et plus']
nb_adultes_dep_rows = crosstab_rows_from_bins(
    bin_series(col("Combien d'adultes ne vivant pas dans votre foyer mais sont dependants de vos revenus ?"),
               [0,1,2,3,4,float('inf')], nb_adultes_dep_labels), nb_adultes_dep_labels)

nb_enfants_charge_labels = ['0', '1-2', '3-4', '5-6', '7 et plus']
nb_enfants_charge_rows = crosstab_rows_from_bins(
    bin_series(col("Combien d'enfants avez-vous e charge dans et en dehors de votre foyer ?"),
               [0,1,3,5,7,float('inf')], nb_enfants_charge_labels), nb_enfants_charge_labels)

nb_revenu_order = ['Aucun', '1', '2', '3', '4', '5 et plus']
nb_revenu_rows = crosstab_rows_fixed_order(col('Combien de personnes dans votre foyer apportent un revenu ?'), nb_revenu_order)

SOURCES_REVENU_MAIN = 'Quelles sont, pour leensemble du foyer, ces sources de revenus ?'
SOURCES_REVENU_COLS = [('Pêche', 'a. Peche'), ('Agriculture', 'b. Agriculture'), ('Élevage', 'c. Elevage'),
    ('Artisanat', 'd. Artisanat'), ('Commerce', 'e. Commerce'),
    ('Salariat (professeur, infirmier, employé...)', 'f. Salariat (professeur.re, infermier.e, employe.e...)'),
    ("Assistance d'un parent/proche", "g. Assistance d'un parent/proche"),
    ("Autre auto-entrepreneuriat/business/travail indépendant", "i. Autre forme d'auto-entreprenenariat, business ou de travail independant"),
    ('Autre activité', 'j. Autre activite')]
sources_revenu_opts = [(lbl, col(SOURCES_REVENU_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in SOURCES_REVENU_COLS]
sources_revenu_rows = crosstab_rows(sources_revenu_opts)

# --- estimation du montant de revenu par source (meme echelle a 4 categories, question posee separement par source) ---
MONTANT_REVENU_ORDER = [
    'Inférieur à 6 500 HTG/mois',
    'Entre 6 500 et 13 000 HTG/mois',
    'Supérieur à 13 000 HTG/mois',
    'Ne souhaite pas répondre / ne sait pas',
]
MONTANT_REVENU_LABEL_MAP = {
    'Inferieurs e 6 500 HTG par mois (ou e 80 000 HTG par an, 1 500 HTG par semaine, 215 HTG par jour)': 'Inférieur à 6 500 HTG/mois',
    'Des revenus mensuels entre 6 500 et 13 000 gourdes': 'Entre 6 500 et 13 000 HTG/mois',
    'Superieur e 13 000 HTG par mois (160 000 HTG par an , 3 000 HTG par semaine, 430 HTG par jour)': 'Supérieur à 13 000 HTG/mois',
    'Ne souhaite pas repondre ou ne connaet pas la reponse.': 'Ne souhaite pas répondre / ne sait pas',
}
def montant_revenu_rows(raw_col_name):
    s = col(raw_col_name).map(MONTANT_REVENU_LABEL_MAP)
    return crosstab_rows_fixed_order(s, MONTANT_REVENU_ORDER)

montant_peche_rows = montant_revenu_rows('Dans le cas du revenu lie la peche, pouvez vous nous donner une estimation du montant par mois ou par annee ?')
montant_agri_rows = montant_revenu_rows("Si vous travaillez dans l'agriculture, pouvez vous nous donner une estimation du montant par mois ?")
montant_artisanat_rows = montant_revenu_rows("Dans le cas du revenu lie a leartisanat, pouvez vous nous donner une estimation du montant percu par mois ?")
montant_commerce_rows = montant_revenu_rows("Dans le cas du revenu lie au commerce, pouvez vous nous donner une estimation du montant percu par mois ?")
montant_salariat_rows = montant_revenu_rows("Si vous etes salarie, pouvez vous nous donner une estimation de vos revenus  (par personne) ?")
montant_autoentr_rows = montant_revenu_rows("S'il y a un revenu lie e de l'auto-entreprenariat, pouvez vous nous donner une estimation du montant percu par mois ou par annee ?")
montant_autre_rows = montant_revenu_rows("Si revenu lie e une autre activite non mentionnee, pouvez vous nous donner une estimation du montant percu par mois ou par annee ?")

# transferts d'argent : deja en sous-colonnes 0/1 par tranche
TRANSFERT_MAIN = "Dans le cas d'un revenu lie aux transferts d'argent (d'un proche), pouvez vous nous donner une estimation du montant percu par mois ?"
TRANSFERT_COLS = [
    ('Inférieur à 6 500 HTG/mois', 'Inferieurs e 6 500 HTG par mois (ou e 80 000 HTG par an, 1 500 HTG par semaine, 215 HTG par jour)'),
    ('Entre 6 500 et 13 000 HTG/mois', 'Des revenus mensuels entre 6 500 et 13 000 gourdes'),
    ('Supérieur à 13 000 HTG/mois', 'Superieur e 13 000 HTG par mois (160 000 HTG par an , 3 000 HTG par semaine, 430 HTG par jour)'),
    ('Ne souhaite pas répondre / ne sait pas', 'Ne souhaite pas repondre ou ne connaet pas la reponse.'),
]
transfert_opts = [(lbl, col(TRANSFERT_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in TRANSFERT_COLS]
_transfert_rows_by_label = dict(crosstab_rows(transfert_opts))
montant_transfert_rows = [(l, _transfert_rows_by_label[l]) for l in MONTANT_REVENU_ORDER]

# --- actifs agricoles / commerce declares en cas de non-reponse au montant (echantillons tres faibles) ---
AGRI_ASSETS_MAIN = "Si vous ne souhaitez pas repondre pouvez vous nous donner des details lies a l'activite ? Avez-vous :"
AGRI_ASSETS_COLS = [
    ('Tous les outils de base en propre', 'Tous les outils de base en propre (machette, pelle, piquet, serpette, houe, couteau digo, beche)'),
    ('Seulement quelques outils de base en propre', 'Seuls quelques uns des outils de base en propre (machette, pelle, piquet, serpette, houe, couteau digo, beche)'),
    ('Aucun outil de base en propre', 'Aucun des outils de base en propre (machette, pelle, piquet, serpette, houe, couteau digo, beche)'),
    ('Accès à des outils de transformation (moulins, presses à huile)', 'Acces e des outils de transformation (moulins e grains, presses e huile..)'),
    ('Des employés/salariés', 'Des employes/salaries'),
    ('Accès aux engrais', 'Acces aux engrais'),
    ('Outils mécanisés', 'Outils mecanises'),
    ('Moyens de stockage de semences (silos)', 'Moyens de stockage de semences (silos)'),
    ('Suffisamment de production pour la vente', 'Suffisament de production pour la vente'),
    ("Accès à l'eau pour l'irrigation", "Acces e l'eau pour l'irrigation (puits, systeme d'irrigation)"),
    ('Des terres en location ou en métayage/fermage', 'Des terres en locations ou en metayage/fermage'),
    ('Des terres en propriété privée', 'Des terres en propriete privee'),
    ('Autre', 'Autre'),
]
agri_assets_opts = [(lbl, col(AGRI_ASSETS_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in AGRI_ASSETS_COLS]
agri_assets_rows = crosstab_rows(agri_assets_opts)

# sous-colonnes situees positionnellement a 163-169 (le nom de la question mere
# est identique au bloc agriculture ci-dessus, seul le suffixe pandas ".1" differe
# sur la colonne mere elle-meme, pas sur les sous-colonnes)
COMMERCE_ASSETS_SUBCOLS = list(df.columns[163:170])
COMMERCE_ASSETS_LABELS = ['Étal (bâche à même le sol ou simple table)', 'Vente de surplus agricole uniquement',
    'Petit magasin (construction fixe)', 'Capacité de faire crédit aux clients', 'Des employés',
    'Rachat de surplus agricole et revente', 'Aucune des options précédentes']
commerce_assets_opts = [(lbl, col(rawc).fillna(0)) for lbl, rawc in zip(COMMERCE_ASSETS_LABELS, COMMERCE_ASSETS_SUBCOLS)]
commerce_assets_rows = crosstab_rows(commerce_assets_opts)

# --- tailles d'elevage (proxy de richesse, module scoring - distinct du module "elevage" plus loin dans le questionnaire) ---
taille_labels_order = ['0', 'Entre 1 et 5', 'Entre 5 et 10', 'Entre 10 et 25', 'Entre 25 et 50']
taille_poules_rows = crosstab_rows_fixed_order(col('Poul'), taille_labels_order)
taille_pijon_rows = crosstab_rows_fixed_order(col('Pijon'), taille_labels_order)
taille_kana_rows = crosstab_rows_fixed_order(col('Kana'), taille_labels_order)
taille_kodenn_rows = crosstab_rows_fixed_order(col('Kodenn'), taille_labels_order)
taille_pentad_rows = crosstab_rows_fixed_order(col('Pentad'), taille_labels_order)

taille_lapin_labels = ['0', '1-5', '6-10', '11 et plus']
taille_lapin_rows = crosstab_rows_from_bins(bin_series(col('Taille de l\'elevage de lapin  ?'), [0,1,6,11,float('inf')], taille_lapin_labels), taille_lapin_labels)
taille_caprin_labels = ['0', '1-5', '6-10', '11-20', '21 et plus']
taille_caprin_rows = crosstab_rows_from_bins(bin_series(col('Taille elevage caprin (x 0,5 si gardiennage) ?'), [0,1,6,11,21,float('inf')], taille_caprin_labels), taille_caprin_labels)
taille_porcin_rows = crosstab_rows_from_bins(bin_series(col('Taille elevage porcin (x 0,5 si gardiennage) ?'), [0,1,6,11,21,float('inf')], taille_caprin_labels), taille_caprin_labels)
taille_bovin_rows = crosstab_rows_from_bins(bin_series(col('Taille elevage bovin (x 0,5 si gardiennage) ?'), [0,1,6,11,21,float('inf')], taille_caprin_labels), taille_caprin_labels)

THEMES13 = [
    dict(category="AF. COMPOSITION DU FOYER", question="Nombre d'adultes vivant dans le foyer (y compris le répondant)",
         rows=nb_adultes_rows, multi=False, note="Question à réponse unique."),
    dict(category="AF. COMPOSITION DU FOYER", question="Nombre d'adultes ne vivant pas dans le foyer mais dépendants des revenus du foyer",
         rows=nb_adultes_dep_rows, multi=False, note="Question à réponse unique."),
    dict(category="AF. COMPOSITION DU FOYER", question="Nombre d'enfants à charge (dans et en dehors du foyer)",
         rows=nb_enfants_charge_rows, multi=False, note="Question à réponse unique."),
    dict(category="AF. COMPOSITION DU FOYER", question="Nombre de personnes du foyer qui apportent un revenu",
         rows=nb_revenu_rows, multi=False, note="Question à réponse unique."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Sources de revenus du foyer",
         rows=sources_revenu_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — pêche",
         rows=montant_peche_rows, multi=False, note="Base : foyers ayant un revenu lié à la pêche (n=96)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — agriculture",
         rows=montant_agri_rows, multi=False, note="Base : foyers ayant un revenu lié à l'agriculture (n=711)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Détails sur les actifs agricoles (si refus de préciser le montant du revenu agricole)",
         rows=agri_assets_rows, multi=True,
         note="Question à réponses multiples, posée uniquement en cas de non-réponse à l'estimation du revenu agricole — échantillon très faible (n=38). Les pourcentages ne totalisent pas 100%."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — artisanat",
         rows=montant_artisanat_rows, multi=False, note="Base très faible : foyers ayant un revenu lié à l'artisanat (n=10)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — commerce",
         rows=montant_commerce_rows, multi=False, note="Base : foyers ayant un revenu lié au commerce (n=546)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Détails sur les actifs de commerce (si refus de préciser le montant du revenu commercial)",
         rows=commerce_assets_rows, multi=True,
         note="Question à réponses multiples, posée uniquement en cas de non-réponse à l'estimation du revenu de commerce. Les pourcentages ne totalisent pas 100%."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — salariat",
         rows=montant_salariat_rows, multi=False, note="Base : foyers ayant un revenu lié au salariat (n=66)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — transferts d'argent (d'un proche)",
         rows=montant_transfert_rows, multi=False, note="Base très faible : foyers ayant un revenu lié aux transferts (n=42)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — auto-entrepreneuriat",
         rows=montant_autoentr_rows, multi=False, note="Base : foyers ayant un revenu lié à l'auto-entrepreneuriat (n=61)."),
    dict(category="AG. SOURCES DE REVENUS DU FOYER", question="Estimation du revenu mensuel — autre activité",
         rows=montant_autre_rows, multi=False, note="Base : foyers ayant un revenu lié à une autre activité (n=120)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de poules",
         rows=taille_poules_rows, multi=False, note="Module distinct de la section « élevage » détaillée plus loin dans le questionnaire (sert au calcul de la catégorie économique). Base : répondants ayant précisé (n=407)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de pigeons",
         rows=taille_pijon_rows, multi=False, note="Base : répondants ayant précisé (n=148)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de canards",
         rows=taille_kana_rows, multi=False, note="Base : répondants ayant précisé (n=158)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de dindes",
         rows=taille_kodenn_rows, multi=False, note="Base : répondants ayant précisé (n=159)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de pintades",
         rows=taille_pentad_rows, multi=False, note="Base très faible : répondants ayant précisé (n=131)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de lapins",
         rows=taille_lapin_rows, multi=False, note="Base : répondants ayant précisé (n=338)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de caprins",
         rows=taille_caprin_rows, multi=False, note="Base : répondants ayant précisé (n=411)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de porcins",
         rows=taille_porcin_rows, multi=False, note="Base : répondants ayant précisé (n=392)."),
    dict(category="AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)", question="Taille de l'élevage de bovins",
         rows=taille_bovin_rows, multi=False, note="Base : répondants ayant précisé (n=412)."),
]

if __name__ == '__main__':
    for t in THEMES13:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 14 : logement / habitat (colonnes ~211-267)
# =====================================================================

superficie_terres_col = col("Quelle est la superficie totale des terres que possedent le foyer (terrain d'habitation, terres agricoles et forestieres comprises) ?")
superficie_terres_categories = col_full("Quelle est la superficie totale des terres que possedent le foyer (terrain d'habitation, terres agricoles et forestieres comprises) ?").dropna().unique()
superficie_terres_rows = crosstab_rows(
    [(lbl, (superficie_terres_col == lbl).astype(int)) for lbl in superficie_terres_categories]
)

nb_pieces_labels = ['1', '2', '3', '4', '5', '6', '7 et plus']
nb_pieces_rows = crosstab_rows_from_bins(bin_series(col('Combien de pieces votre logement comporte ?'), [1,2,3,4,5,6,7,float('inf')],
    ['1','2','3','4','5','6','7 et plus']), nb_pieces_labels)

MATERIAUX_MAIN = 'Quels sont les types de materiaux de votre maison ?'
MATERIAUX_COLS = ['Mur en paille', 'Mur en terre ', 'Mur en blocs', 'Mur en pierre',
    'Maison de fortune avec des beches plastiques', 'Mur en clissade', 'Mur en planche',
    'Toiture en dalle', 'Toiture en tele de zinc', 'Toiture en vetiver', 'Toiture en plastique',
    'Pas de maison propre', 'Autre']
MATERIAUX_LABELS = ['Mur en paille', 'Mur en terre', 'Mur en blocs', 'Mur en pierre',
    'Maison de fortune (bâches plastiques)', 'Mur en clissade', 'Mur en planche',
    'Toiture en dalle', 'Toiture en tôle de zinc', 'Toiture en vétiver', 'Toiture en plastique',
    'Pas de maison propre', 'Autre']
materiaux_opts = [(lbl, col(MATERIAUX_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in zip(MATERIAUX_LABELS, MATERIAUX_COLS)]
materiaux_rows = crosstab_rows(materiaux_opts)

def parse_surface(text):
    import re as _re
    if pd.isna(text): return None
    t = str(text).lower().strip().replace(',', '.')
    m = _re.search(r'(\d+(?:\.\d+)?)\s*(?:m\.?e?|me|metres?|m2)?\s*[x\*]\s*(\d+(?:\.\d+)?)', t)
    if m:
        try: return float(m.group(1)) * float(m.group(2))
        except: pass
    m = _re.search(r'(\d+(?:\.\d+)?)', t)
    if m:
        try: return float(m.group(1))
        except: pass
    return None

surface_parsed = col('Quelle surface fait votre maison (le repondant peut donner les infos sur la longueur et la largeur, si disponibles, pour que l\'enqueteur calcule la surface)?').apply(parse_surface)
surface_labels = ['< 20 m²', '20-39 m²', '40-59 m²', '60-99 m²', '100 m² et plus', 'Valeur aberrante (à vérifier)', 'Non chiffré / non numérique']
def surface_bucket(v, raw):
    if v is None:
        return 'Non chiffré / non numérique' if pd.notna(raw) else None
    if v > 10000:
        return 'Valeur aberrante (à vérifier)'
    if v < 20: return '< 20 m²'
    if v < 40: return '20-39 m²'
    if v < 60: return '40-59 m²'
    if v < 100: return '60-99 m²'
    return '100 m² et plus'
raw_surface_col = col('Quelle surface fait votre maison (le repondant peut donner les infos sur la longueur et la largeur, si disponibles, pour que l\'enqueteur calcule la surface)?')
surface_bucketed = pd.Series([surface_bucket(v, r) for v, r in zip(surface_parsed, raw_surface_col)], index=df.index)
surface_rows = crosstab_rows_from_bins(surface_bucketed, surface_labels)

DOMMAGE_MAIN = "Votre logement a t-il ete endommage par l'un de ces phenomenes durant les 5 dernieres annees ?"
DOMMAGE_COLS = ['Inondation', 'Eboulement', 'Vents forts', 'Forte pluie', 'Tremblement de terre',
    'Glissement de terrain', 'Tsunami', 'Secheresse', 'Non', 'Autre']
DOMMAGE_LABELS = ['Inondation', 'Éboulement', 'Vents forts', 'Forte pluie', 'Tremblement de terre',
    'Glissement de terrain', 'Tsunami', 'Sécheresse', 'Non (aucun dommage)', 'Autre']
dommage_opts = [(lbl, col(DOMMAGE_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in zip(DOMMAGE_LABELS, DOMMAGE_COLS)]
dommage_rows = crosstab_rows(dommage_opts)

mesure_dommage_order = ['Aucun dégât', 'Dégâts minimes', 'Dégâts modérés', 'Dégâts importants']
mesure_dommage_map = {'Aucun deget': 'Aucun dégât', 'Degets minimes': 'Dégâts minimes',
                       'Degets moderes': 'Dégâts modérés', 'Degets importants': 'Dégâts importants'}
mesure_dommage_rows = crosstab_rows_fixed_order(col("Dans quelle mesure votre maison a-t-elle ete endommagee ?").map(mesure_dommage_map), mesure_dommage_order)

THEMES14 = [
    dict(category="AI. LOGEMENT / HABITAT", question="Superficie totale des terres possédées par le foyer",
         rows=superficie_terres_rows, multi=False,
         note="Question à réponse unique (catégories en carreaux). Attention : certains symboles de fraction (¼, ½...) du questionnaire original ont été corrompus lors d'un nettoyage d'encodage antérieur et apparaissent ici comme « e » ou « ? » — les libellés affichés sont donc approximatifs ; se référer au questionnaire original / codebook pour les bornes exactes."),
    dict(category="AI. LOGEMENT / HABITAT", question="Nombre de pièces du logement",
         rows=nb_pieces_rows, multi=False,
         note="Question à réponse unique. Quelques valeurs extrêmes (jusqu'à 200 pièces) regroupées dans « 7 et plus » — probables erreurs de saisie à vérifier."),
    dict(category="AI. LOGEMENT / HABITAT", question="Types de matériaux de construction de la maison",
         rows=materiaux_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AI. LOGEMENT / HABITAT", question="Surface de la maison",
         rows=surface_rows, multi=False,
         note="Réponses en texte libre (mètres, formats « longueur x largeur », estimations qualitatives), parsées automatiquement — classification indicative à valider. Une quarantaine de valeurs manifestement aberrantes (plusieurs millions de m²) isolées dans une catégorie dédiée plutôt qu'exclues silencieusement."),
    dict(category="AI. LOGEMENT / HABITAT", question="Dommages subis par le logement au cours des 5 dernières années",
         rows=dommage_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AI. LOGEMENT / HABITAT", question="Ampleur des dommages subis par la maison",
         rows=mesure_dommage_rows, multi=False,
         note="Base : logements ayant subi des dommages."),
]

if __name__ == '__main__':
    for t in THEMES14:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 15 : eau, assainissement et hygiene - WASH approfondi (colonnes ~268-303)
# =====================================================================

TOILETTES_MAIN = 'Quel type de toilettes les membres de votre menage utilisent-ils habituellement ?'
TOILETTES_COLS = [
    ('Aucun (défécation eaux de surface / air libre)', 'Aucun (Defecation dans les eaux de surface et/ou latrines suspendues et defecation e leair libre : buissons, champs, fosses)'),
    ("Toilettes à chasse d'eau raccordées à des drains ouverts", "Toilettes e chasse d'eau raccordees e des drains ouverts"),
    ('Seaux, bassines, plateaux ou autres récipients', 'Les seaux, bassines, e plateaux e ou autres recipients'),
    ('Latrines à fosse sans dalle', 'Latrines e fosse sans dalle'),
    ('Latrines à fosse sèche avec dalle', 'Latrines e fosse seche avec dalle'),
    ('Toilettes à compostage', 'Toilettes e compostage'),
    ('Latrines à fosse avec dalle', 'Latrines e fosse avec dalle'),
    ('Latrines à fosse ventilée améliorée', 'Latrines e fosse ventilee amelioree'),
    ("Toilettes à chasse d'eau raccordées à des égouts/fosses septiques", "Toilettes e chasse d'eau raccordees e des systemes d'egouts ou e des fosses septiques"),
    ('Autre', 'Autre'),
]
toilettes_opts = [(lbl, col(TOILETTES_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in TOILETTES_COLS]
toilettes_rows = crosstab_rows(toilettes_opts)

sanitaires_partages_rows = crosstab_rows_fixed_order(col('Est-ce que les sanitaires que vous utilisez sont partages par plusieurs foyers ?'), ['Oui', 'Non'])

EAU_MAIN = "D'ou obtenez vous l'eau que vous buvez ?"
EAU_COLS = [
    ('Eaux de surface non protégées (rivières, réservoirs, lacs...)', "Eaux de surface non sers (rivieres, reservoirs, lacs, etangs, ruisseaux, canaux et canaux d'irrigation)"),
    ('Sources protégées', 'Sources protegees (que veut dire protegees ?)'),
    ('Eau de réseau', 'Eau de reseau'),
    ('Forages ou puits tubulaires', 'Forages ou puits tubulaires'),
    ('Puits creusés protégés', 'Puits creuses proteges'),
    ('Eau de pluie', 'Eau de pluie'),
    ('Kiosques à eau', 'Kiosques e eau'),
    ('Eau en bouteille, livrée ou en sachet', 'Eau en bouteille ou livree ou eau en sachet'),
    ('Puits creusés non protégés / sources non protégées', 'Les puits creuses non proteges, les sources non protegees.'),
    ('Autre', 'Autre'),
]
eau_opts = [(lbl, col(EAU_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in EAU_COLS]
eau_source_rows = crosstab_rows(eau_opts)

distance_eau_order = ['Moins de 15 minutes de temps de trajet', 'Entre 15 et 30 minutes de temps de trajet',
    'Entre 30 minutes et 1 heure de temps de trajet', 'Entre 1h et 2h de temps de trajet', 'Plus de 2h de temps de trajet']
distance_eau_rows = crosstab_rows_fixed_order(col("A combien de temps de votre maison se trouve le point deeau que vous utilisez (Allez-retour) ?"), distance_eau_order)

TRAITEMENT_EAU_MAIN = "Comment traitez vous l'eau potable ?"
TRAITEMENT_EAU_COLS = [('Chlore ou aquatab', 'Chlore ou aquatab'), ('Bouillir', 'Bouillir'),
                        ('Aucun traitement', 'Aucun traitement'), ('Autre', 'Autre')]
traitement_eau_opts = [(lbl, col(TRAITEMENT_EAU_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in TRAITEMENT_EAU_COLS]
traitement_eau_rows = crosstab_rows(traitement_eau_opts)

semaines_penurie_labels = ['0', '1-4', '5-8', '9-12', '13 et plus']
semaines_penurie_rows = crosstab_rows_from_bins(
    bin_series(col("Combien de semaines par an avez-vous du mal a trouver de l'eau e votre point d'acces habituel ?"),
               [0,1,5,9,13,float('inf')], semaines_penurie_labels), semaines_penurie_labels)

penurie_moment_map = {
    'Pas de pénurie / toujours de l\'eau': ['toujou gen dlo', 'aucun', 'ras', 'okenn', '0', 'nan moman'],
    'Saison sèche (carême / été)': ['sech', 'ete', 'careme', 'ka rem'],
}
penurie_moment_rows = keyword_multi_rows(col("A quels moments de l'annee arrivent ces penuries ?"), penurie_moment_map, other_label="Mois précis cité / autre")

penurie_raison_map = {
    "Manque de pluie / sécheresse": ['secheres', 'sech', 'lapli pa tonbe', 'peu de precipitation', 'manke lapli'],
    "Pas de pénurie / sans objet": ['toujou gen dlo', 'aucun', 'ras', 'okenn', '0'],
}
penurie_raison_rows = keyword_multi_rows(col('Pour quelles raisons ?'), penurie_raison_map, other_label="Autre raison / non classée")

solution_alt_map = {
    "Aucune solution / sans objet": ['ras', 'aucun', 'okenn', '0', 'toujou gen dlo'],
    "Aller chercher ailleurs (autre source/kilomètres)": ['al nan', 'aller', 'ailleurs', 'kilomet', 'sous', 'source'],
    "Acheter de l'eau": ['achte', 'achet'],
}
solution_alt_rows = keyword_multi_rows(col('Quelles solutions alternatives avez vous dans ces cas ?'), solution_alt_map, other_label="Autre / non classée")

THEMES15 = [
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Type de toilettes habituellement utilisées par le ménage",
         rows=toilettes_rows, multi=True, note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Sanitaires partagés avec plusieurs foyers",
         rows=sanitaires_partages_rows, multi=False, note="Question à réponse unique."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Source d'eau de boisson",
         rows=eau_source_rows, multi=True, note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Distance (aller-retour) jusqu'au point d'eau utilisé",
         rows=distance_eau_rows, multi=False, note="Question à réponse unique."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Traitement de l'eau potable",
         rows=traitement_eau_rows, multi=True, note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Nombre de semaines par an avec difficulté à trouver de l'eau au point d'accès habituel",
         rows=semaines_penurie_rows, multi=False, note="Question à réponse unique."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Moment de l'année où surviennent les pénuries d'eau",
         rows=penurie_moment_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés — à valider. Base : foyers ayant signalé des pénuries."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Raisons des pénuries d'eau",
         rows=penurie_raison_rows, multi=True,
         note="Réponses en texte libre, classification indicative par mots-clés — à valider."),
    dict(category="AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)", question="Solutions alternatives en cas de pénurie d'eau",
         rows=solution_alt_rows, multi=True,
         note="Réponses en texte libre, classification indicative par mots-clés — à valider."),
]

if __name__ == '__main__':
    for t in THEMES15:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 16 : entraide communautaire + complements agriculture (superficie,
# semis, arbres plantes, intrants en quantite, irrigation)
# =====================================================================

AIDE_RECUE_MAIN = 'Au cours des six derniers mois, avez-vous reeu une aide/service de la part :'
AIDE_RECUE_COLS = [("D'un membre de la communauté", "Oui, d'un membre de la communaute"),
    ('De ma famille élargie', 'Oui, de ma famille elargie'), ("D'un voisin immédiat", "Oui, d'un voisin immediat"),
    ('Non', 'Non')]
aide_recue_opts = [(lbl, col(AIDE_RECUE_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in AIDE_RECUE_COLS]
aide_recue_rows = crosstab_rows(aide_recue_opts)

aide_recue_forme_map = {
    "Nourriture": ['manje', 'manger', 'nouriture', 'nourriture', 'manje'],
    "Argent / prêt": ['lajan', 'argent', 'pret'],
    "Travail / main d'œuvre": ['travay', 'travail', 'main doeuvre', "main d'oeuvre"],
    "Matériel/outils": ['zouti', 'materiel', 'outil'],
}
aide_recue_forme_rows = keyword_multi_rows(col('Si oui, sous quelle forme ?'), aide_recue_forme_map, other_label="Autre / non classée")

AIDE_RENDUE_MAIN = 'Au cours des six derniers mois, avez-vous rendu un service/aide e :'
AIDE_RENDUE_COLS = [('À un membre de la communauté', 'Oui, a un membre de la communaute'),
    ('À ma famille élargie', 'Oui, a ma famille elargie'), ('À un voisin immédiat', 'Oui, a un voisin immediat'),
    ('Non', 'Non')]
aide_rendue_opts = [(lbl, col(AIDE_RENDUE_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in AIDE_RENDUE_COLS]
aide_rendue_rows = crosstab_rows(aide_rendue_opts)

aide_rendue_forme_rows = keyword_multi_rows(col('Si oui, sous quelles formes'), aide_recue_forme_map, other_label="Autre / non classée")

THEMES16_ENTRAIDE = [
    dict(category="AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)", question="A reçu une aide/service de la part de...",
         rows=aide_recue_rows, multi=True, note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)", question="Forme de l'aide reçue",
         rows=aide_recue_forme_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés — à valider."),
    dict(category="AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)", question="A rendu un service/aide à...",
         rows=aide_rendue_rows, multi=True, note="Question à réponses multiples — les pourcentages ne totalisent pas 100%."),
    dict(category="AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)", question="Forme de l'aide rendue",
         rows=aide_rendue_forme_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés — à valider."),
]

# --- superficie dediee par culture (memes 25 colonnes que "cultures pratiquees", valeur brute cette fois) ---
SUPERFICIE_CROP_COLS = CROP_COLS  # meme liste (label, raw_col) que la table de presence
THEMES16_SUPERFICIE = []
for lbl, rawc in SUPERFICIE_CROP_COLS:
    s = col(rawc)
    categories = col_full(rawc).dropna().unique()
    if len(categories) == 0:
        continue
    rows = crosstab_rows([(v, (s == v).astype(int)) for v in categories])
    THEMES16_SUPERFICIE.append(dict(
        category="AL. AGRICULTURE — SUPERFICIE DÉDIÉE PAR CULTURE",
        question=f"Superficie dédiée (en carreaux) — {lbl}",
        rows=rows, multi=False,
        note="Base : répondants cultivant cette culture. Attention : certains symboles de fraction (¼, ½...) ont été corrompus lors d'un nettoyage d'encodage antérieur et apparaissent comme « e » ou « ? » — se référer au questionnaire original pour les bornes exactes."
    ))

# --- moment de semis par culture ---
SEMIS_RAW_COLS = list(df.columns[549:571])
SEMIS_LABELS = ['Maïs', 'Haricot', 'Pois congo', 'Igname', 'Patate', 'Banane', 'Riz', 'Sorgho / petit mil',
    'Chou', 'Carotte', 'Aubergine', 'Manioc', 'Café', 'Gombo (kalalou)', 'Tomate', 'Betterave',
    'Patate douce', 'Malanga', 'Mazonbèl', 'Pistache (arachide)', 'Ananas', 'Autre']
SEMIS_MONTH_LABELS = {'F': 'Février', 'M': 'M (Mars/Mai — code ambigu)', 'A': 'A (Avril/Août — code ambigu)',
                       'J': 'J (Janvier/Juin/Juillet — code ambigu)', 'S': 'Septembre', 'O': 'Octobre', 'N': 'Novembre', 'D': 'Décembre'}
SEMIS_ORDER = ['F', 'M', 'A', 'J', 'S', 'O', 'N', 'D']
THEMES16_SEMIS = []
for lbl, rawc in zip(SEMIS_LABELS, SEMIS_RAW_COLS):
    s = col(rawc)
    if col_full(rawc).notna().sum() == 0:
        continue
    rows = crosstab_rows_fixed_order(s, SEMIS_ORDER)
    rows = [(SEMIS_MONTH_LABELS[l], v) for l, v in rows]
    THEMES16_SEMIS.append(dict(
        category="AM. AGRICULTURE — MOMENT DE SEMIS PAR CULTURE",
        question=f"Mois de semis — {lbl}",
        rows=rows, multi=False,
        note="Codes mensuels tels que saisis dans la base (lettre initiale du mois en français) : certains sont ambigus (M = Mars ou Mai, J = Janvier/Juin/Juillet, A = Avril/Août) — à clarifier avec l'équipe terrain avant usage. Base : répondants cultivant cette culture."
    ))

# --- nombre de pieds d'arbres fruitiers plantes ---
ARBRE_RAW_COLS = list(df.columns[573:592])
ARBRE_LABELS = ['Manguier', 'Avocatier', 'Anacardier (noix)', 'Cachiman', 'Arbre véritable (fruit à pain)',
    'Labapen', 'Corrossolier', 'Fruit de la passion', 'Grenadine', 'Grenade', 'Grenadia', 'Cerisier',
    'Cocotier', 'Cacao', 'Papaye', 'Oranger', 'Citronnier', 'Ne souhaite pas répondre', 'Autre']
ARBRE_ORDER = ['Aucun', '1 et 10', '10 et 25', 'Entre 25 et 50', 'Entre 50 et 100', '100 et plus']
THEMES16_ARBRES = []
for lbl, rawc in zip(ARBRE_LABELS, ARBRE_RAW_COLS):
    s = col(rawc)
    if col_full(rawc).notna().sum() == 0:
        continue
    rows = crosstab_rows_fixed_order(s, ARBRE_ORDER)
    THEMES16_ARBRES.append(dict(
        category="AN. AGRICULTURE — NOMBRE DE PIEDS D'ARBRES FRUITIERS PLANTÉS",
        question=f"Nombre de pieds plantés — {lbl}",
        rows=rows, multi=False,
        note="Base : répondants cultivant cet arbre fruitier."
    ))

# --- quantite d'intrants appliques (echantillons tres faibles) ---
_QTE_ENGRAIS_COL = "Si oui , quelle est la quantite d'engrais azote (en kg) que vous appliquez e vos cultures  ?"
_QTE_HERBICIDE_COL = 'Si oui, quelle est la quantite d\'herbicide (en litre) que vous appliquez e vos cultures (tous herbicides confondus)?'
_QTE_INSECTICIDE_COL = 'SI oui, quelle est la quantite insecticide (en litre) que vous appliquez e vos cultures (tous insecticides confondus)?'
_QTE_FONGICIDE_COL = 'Si oui, quelle est la quantite de fongicides (en litre) que vous appliquez e vos cultures (tous fongicides confondus)?'
qte_engrais_rows = crosstab_rows([(v, (col(_QTE_ENGRAIS_COL) == v).astype(int)) for v in col_full(_QTE_ENGRAIS_COL).dropna().unique()])
qte_herbicide_rows = crosstab_rows([(v, (col(_QTE_HERBICIDE_COL) == v).astype(int)) for v in col_full(_QTE_HERBICIDE_COL).dropna().unique()])
qte_insecticide_rows = crosstab_rows([(v, (col(_QTE_INSECTICIDE_COL) == v).astype(int)) for v in col_full(_QTE_INSECTICIDE_COL).dropna().unique()])
qte_fongicide_rows = crosstab_rows([(v, (col(_QTE_FONGICIDE_COL) == v).astype(int)) for v in col_full(_QTE_FONGICIDE_COL).dropna().unique()])

# --- irrigation ---
irrigation_order = ['Non, aucune', 'Oui mais insuffisant', 'Oui et suffisant']
irrigation_rows = crosstab_rows_fixed_order(col("Disposez-vous deune source deeau pour irriguer vos cultures ?"), irrigation_order)

IRRIG_SYS_MAIN = "Si oui, de quel systeme d'irrigation disposez-vous ?"
IRRIG_SYS_COLS = ['Transport manuel', 'Captage par derivation', 'Barrage et captage par derivation',
    'Pompe solaire', 'Pompe e essence', 'Systeme goutte e goutte', 'Autre']
IRRIG_SYS_LABELS = ['Transport manuel', 'Captage par dérivation', 'Barrage et captage par dérivation',
    'Pompe solaire', 'Pompe à essence', 'Système goutte à goutte', 'Autre']
irrig_sys_opts = [(lbl, col(IRRIG_SYS_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in zip(IRRIG_SYS_LABELS, IRRIG_SYS_COLS)]
irrig_sys_rows = crosstab_rows(irrig_sys_opts)

THEMES16_INTRANTS_IRRIGATION = [
    dict(category="AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE", question="Quantité d'engrais azoté appliquée (kg)",
         rows=qte_engrais_rows, multi=False, note="Échantillon extrêmement faible (n=10) — indicatif uniquement."),
    dict(category="AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE", question="Quantité d'herbicide appliquée (litres)",
         rows=qte_herbicide_rows, multi=False, note="Échantillon extrêmement faible (n=2) — indicatif uniquement."),
    dict(category="AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE", question="Quantité d'insecticide appliquée (litres)",
         rows=qte_insecticide_rows, multi=False, note="Échantillon extrêmement faible (n=10) — indicatif uniquement."),
    dict(category="AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE", question="Quantité de fongicides appliquée (litres)",
         rows=qte_fongicide_rows, multi=False, note="Échantillon extrêmement faible (n=2) — indicatif uniquement."),
    dict(category="AP. AGRICULTURE — IRRIGATION", question="Dispose d'une source d'eau pour irriguer les cultures",
         rows=irrigation_rows, multi=False, note="Question à réponse unique. Base : répondants pratiquant l'agriculture ayant répondu (n=667)."),
    dict(category="AP. AGRICULTURE — IRRIGATION", question="Système d'irrigation utilisé",
         rows=irrig_sys_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Échantillon faible (n=36, répondants disposant d'une source d'eau)."),
]

THEMES16 = THEMES16_ENTRAIDE + THEMES16_SUPERFICIE + THEMES16_SEMIS + THEMES16_ARBRES + THEMES16_INTRANTS_IRRIGATION

if __name__ == '__main__':
    for t in THEMES16:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# =====================================================================
# THEMES 17 : derniers elements identifies (originaire de la section,
# facteurs de baisse/hausse des rendements agricoles)
# =====================================================================

originaire_rows = crosstab_rows_fixed_order(col('etes vous originaire de cette section communale ?'), ['Oui', 'Non'])

FACTEUR_BAISSE_MAIN = 'Si diminution, quel est le facteur principal qui a contribue e la diminution de vos rendements ?'
FACTEUR_BAISSE_COLS = ['Secheresse', 'maladies', 'Ravageurs', "Innondation/exces d'humidite",
    'Deterioration de la fertilite du sol', "Manque de main d'oeuvre", 'Forts vents', 'Qualite de semences', 'Autre']
FACTEUR_BAISSE_LABELS = ['Sécheresse', 'Maladies', 'Ravageurs', "Inondation / excès d'humidité",
    'Détérioration de la fertilité du sol', "Manque de main-d'œuvre", 'Forts vents', 'Qualité des semences', 'Autre']
facteur_baisse_opts = [(lbl, col(FACTEUR_BAISSE_MAIN + '/' + rawc).fillna(0)) for lbl, rawc in zip(FACTEUR_BAISSE_LABELS, FACTEUR_BAISSE_COLS)]
facteur_baisse_rows = crosstab_rows(facteur_baisse_opts)

facteur_hausse_map = {
    "Pluie favorable / bonne pluviométrie": ['lapli', 'pluie', 'dlo', 'lapli tonbe'],
    "Pas d'augmentation / sans objet": ['pa gen ogmantasyon', 'ras', 'anyen', 'aucun'],
}
facteur_hausse_rows = keyword_multi_rows(col("Si augmentation, quels sont les facteurs qui ont contribue e l'augmentation de vos rendements ?"), facteur_hausse_map, other_label="Autre / non classée")

THEMES17 = [
    dict(category="AQ. PROFIL DU RÉPONDANT", question="Est originaire de cette section communale",
         rows=originaire_rows, multi=False, note="Question à réponse unique."),
    dict(category="AR. AGRICULTURE — FACTEURS D'ÉVOLUTION DES RENDEMENTS", question="Facteur principal de la diminution des rendements (si diminution)",
         rows=facteur_baisse_rows, multi=True,
         note="Question à réponses multiples — les pourcentages ne totalisent pas 100%. Base : répondants ayant rapporté une baisse de rendement sur au moins une culture."),
    dict(category="AR. AGRICULTURE — FACTEURS D'ÉVOLUTION DES RENDEMENTS", question="Facteurs de l'augmentation des rendements (si augmentation)",
         rows=facteur_hausse_rows, multi=True,
         note="Réponses en texte libre (créole/français), classification indicative par mots-clés — à valider. Base : répondants ayant rapporté une hausse de rendement (n≈250)."),
]

if __name__ == '__main__':
    for t in THEMES17:
        print('===', t['category'], '-', t['question'])
        for label, rown in t['rows']:
            print(' ', label, rown['Total'])

# Extension de la liste maitresse avec les themes ajoutes suite au fichier
# "toutes les questions que j'ai besoin que tu traites" (gap-filling)
ALL_THEMES_FULL = ALL_THEMES_FULL + THEMES13 + THEMES14 + THEMES15 + THEMES16 + THEMES17

# Themes ajoutes dans cette passe de completion (pour regenerer uniquement le delta)
NEW_THEMES_BATCH = THEMES13 + THEMES14 + THEMES15 + THEMES16 + THEMES17

# =====================================================================
# Reordonnancement de ALL_THEMES_FULL selon l'ordre reel des questions
# dans le questionnaire (indice de colonne source approximatif par
# categorie), plutot que l'ordre chronologique dans lequel les themes
# ont ete ajoutes au fil de la conversation.
# =====================================================================
CATEGORY_COL_ORDER = {
    "AQ. PROFIL DU RÉPONDANT": 5,
    "AF. COMPOSITION DU FOYER": 13,
    "AG. SOURCES DE REVENUS DU FOYER": 65,
    "AH. ÉLEVAGE (PROXY DE RICHESSE — MODULE DE SCORING)": 128,
    "AI. LOGEMENT / HABITAT": 211,
    "AJ. EAU, ASSAINISSEMENT ET HYGIÈNE (WASH)": 268,
    "C. ÉNERGIE DOMESTIQUE": 304,
    "D. CONNECTIVITÉ / COMMUNICATION": 322,
    "E. GESTION DES DÉCHETS SOLIDES": 323,
    "F. ACCÈS AUX SERVICES ADMINISTRATIFS": 335,
    "G. ACCÈS AUX INFRASTRUCTURES DE SANTÉ ET D'ÉDUCATION": 342,
    "H. ENFANTS NÉS DANS LA SECTION COMMUNALE": 346,
    "I. GOUVERNANCE ET INTÉGRITÉ": 352,
    "J. GESTION DES RISQUES ET DES CATASTROPHES": 354,
    "K. PARTICIPATION COMMUNAUTAIRE ET CITOYENNE": 367,
    "AK. ENTRAIDE COMMUNAUTAIRE (6 DERNIERS MOIS)": 379,
    "L. VIE SOCIALE ET CAPITAL COMMUNAUTAIRE": 399,
    "M. ÉDUCATION ET SOUTIEN SOCIAL": 427,
    "N. SÉCURITÉ ALIMENTAIRE (12 DERNIERS MOIS)": 442,
    "O. MIGRATION": 458,
    "P. MIGRATION ÉCONOMIQUE ET ASPIRATIONS": 476,
    "Q. EMPLOI ET REVENUS": 479,
    "S. ÉPARGNE, CRÉDIT ET RÉSILIENCE FINANCIÈRE": 486,
    "R. FONCIER AGRICOLE": 494,
    "T. AGRICULTURE — PRATIQUES GÉNÉRALES": 521,
    "AL. AGRICULTURE — SUPERFICIE DÉDIÉE PAR CULTURE": 522,
    "AM. AGRICULTURE — MOMENT DE SEMIS PAR CULTURE": 549,
    "AN. AGRICULTURE — NOMBRE DE PIEDS D'ARBRES FRUITIERS PLANTÉS": 573,
    "AO. AGRICULTURE — QUANTITÉ D'INTRANTS APPLIQUÉE": 596,
    "U. AGRICULTURE — RENDEMENTS ANNUELS PAR CULTURE": 604,
    "V. AGRICULTURE — ÉVOLUTION DES RENDEMENTS (5 ANS) PAR CULTURE": 646,
    "AR. AGRICULTURE — FACTEURS D'ÉVOLUTION DES RENDEMENTS": 687,
    "AP. AGRICULTURE — IRRIGATION": 699,
    "W. AGRICULTURE — CIRCONSTANCES DE PERTE DE PRODUCTION PAR CULTURE": 710,
    "X. AGRICULTURE — POURCENTAGE DE PRODUCTION PERDUE PAR CULTURE": 752,
    "Y. PÊCHE — PRATIQUES GÉNÉRALES": 793,
    "Z. PÊCHE — ESPÈCES PÊCHÉES ET ZONE": 816,
    "AA. PÊCHE — MONTANT PAR SORTIE ET PAR ESPÈCE": 844,
    "AB. PÊCHE — MOMENT LE PLUS RENTABLE PAR ESPÈCE": 872,
    "AC. ÉLEVAGE — GÉNÉRALITÉS": 899,
    "AD. ÉLEVAGE — MORTALITÉ": 915,
    "AE. FACTEUR LIMITANT LES BÉNÉFICES (PÊCHE / AGRICULTURE / ÉLEVAGE)": 964,
}

ALL_THEMES_FULL = sorted(ALL_THEMES_FULL, key=lambda t: CATEGORY_COL_ORDER.get(t["category"], 99999))
