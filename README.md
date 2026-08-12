# Enquête ménage 2024 — mettre l'explorateur en ligne

Ce dossier contient une petite application web qui permet d'explorer les résultats de l'enquête avec des filtres combinables (sexe, catégorie économique, groupe d'âge, paysage, section communale) et d'obtenir, pour n'importe laquelle des 503 questions, un tableau (n et %) et un graphique calculés en direct sur la population filtrée, avec un bouton pour télécharger le résultat en Excel.

Vous n'avez aucune ligne de code à écrire. Tout est déjà prêt dans ce dossier ; il ne reste qu'à le mettre en ligne, ce qui se fait entièrement par des clics. Comptez 15-20 minutes la première fois.

Les données utilisées ici sont une copie **anonymisée** (nom, téléphone, coordonnées GPS et nom de l'enquêteur retirés) — c'est le fichier `data/donnees_anonymisees.csv`, déjà généré, vous n'avez rien à faire dessus.

## Étape 1 — Créer un compte GitHub (gratuit)

GitHub est simplement l'endroit où les fichiers de l'application vont être déposés pour que Streamlit puisse les lire.

1. Allez sur [github.com](https://github.com) et cliquez sur **Sign up**.
2. Suivez les instructions (email, mot de passe, nom d'utilisateur). C'est gratuit.

Si vous avez déjà un compte GitHub, passez directement à l'étape 2.

## Étape 2 — Créer un dépôt et y déposer les fichiers

1. Une fois connecté à GitHub, cliquez sur le bouton **+** en haut à droite, puis **New repository**.
2. Donnez-lui un nom, par exemple `enquete-menage-2024`.
3. Choisissez **Private** (recommandé, vu la nature des données — même anonymisées) plutôt que Public.
4. Cliquez sur **Create repository**.
5. Sur la page qui s'affiche, cliquez sur **uploading an existing file** (ou **Add file → Upload files**).
6. Ouvrez ce dossier sur votre ordinateur et **glissez-déposez tout son contenu** dans la zone de dépôt de GitHub : `app.py`, `compute_banner_data.py`, `dump_theme_data.py`, `requirements.txt`, le dossier `data` (avec les 3 fichiers dedans), et le dossier `.streamlit`.
   - Important : gardez la même organisation de dossiers (le fichier `donnees_anonymisees.csv` doit rester dans un sous-dossier nommé `data`, pas à la racine).
7. En bas de page, cliquez sur **Commit changes** (le message par défaut convient très bien).

## Étape 3 — Créer un compte Streamlit Community Cloud (gratuit)

1. Allez sur [share.streamlit.io](https://share.streamlit.io).
2. Cliquez sur **Sign up** puis choisissez **Continue with GitHub** — ça relie directement votre compte GitHub, pas besoin de créer un mot de passe séparé.
3. Autorisez l'accès quand GitHub vous le demande.

## Étape 4 — Déployer l'application

1. Sur Streamlit Cloud, cliquez sur **Create app** (ou **New app**).
2. Choisissez **Deploy a public app from GitHub** (l'app elle-même peut ensuite être protégée par mot de passe, voir étape 5 — "public" ici veut juste dire "accessible par un lien", pas listée nulle part).
3. Sélectionnez le dépôt que vous venez de créer (`enquete-menage-2024`), la branche `main`, et dans **Main file path** indiquez `app.py`.
4. Cliquez sur **Deploy**.
5. La première mise en ligne prend 2-5 minutes (installation des outils nécessaires). Une page avec une URL du type `https://xxxxx.streamlit.app` apparaît ensuite — c'est le lien de votre application.

## Étape 5 — Ajouter un mot de passe (fortement recommandé)

Vu la nature du sujet (sécurité alimentaire, vulnérabilité des foyers), même sur des données anonymisées, mieux vaut ne pas laisser le lien totalement ouvert à qui le trouverait.

1. Sur la page de votre app dans Streamlit Cloud, cliquez sur les **⋮** (trois points, en bas à droite de la carte de l'app) puis **Settings**.
2. Allez dans l'onglet **Secrets**.
3. Collez ceci dans la zone de texte, en remplaçant `votre-mot-de-passe` par celui de votre choix :

   ```
   APP_PASSWORD = "votre-mot-de-passe"
   ```

4. Cliquez sur **Save**. L'application redémarre automatiquement (quelques secondes) et demande désormais ce mot de passe à l'ouverture.
5. Partagez le lien **et** le mot de passe séparément avec les personnes concernées (par exemple lien par email, mot de passe par message).

## Mettre à jour l'application plus tard

Si vous voulez changer quelque chose (par exemple si je vous envoie une nouvelle version d'`app.py` ou des données mises à jour) :

1. Retournez sur la page du dépôt sur GitHub.
2. Ouvrez le fichier à remplacer, cliquez sur l'icône crayon (ou supprimez-le et re-uploadez la nouvelle version via **Add file → Upload files**).
3. Cliquez sur **Commit changes**.
4. Streamlit Cloud redéploie automatiquement l'application avec la nouvelle version en 1-2 minutes — rien d'autre à faire.

## Bon à savoir

- **Vitesse** : chaque nouvelle combinaison de filtres prend quelques secondes à calculer la première fois (l'app recalcule sur les 1211 réponses) ; la même combinaison redemandée ensuite s'affiche instantanément.
- **Coût** : Streamlit Community Cloud est gratuit pour ce type d'usage (une app privée à faible trafic).
- **Si l'app "s'endort"** : après une période sans visite, une app gratuite Streamlit se met en veille ; la première personne qui rouvre le lien attend ~30 secondes pendant qu'elle se réveille, c'est normal.
