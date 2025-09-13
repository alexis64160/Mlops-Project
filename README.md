# Mlops-Project

## Quick start
### Première installation
- Créer un fichier env personalisé:
`cp .env.secrets.template .env.secrets`

- puis éditer le fichier .env
`vim .env.secrets`

- Créer le fichier de configuration:
`cp config.yaml.template config.yaml`

Exécuter le fichier scripts/initialize.sh:
`./scripts/initialize.sh`

### Configuration lors de chaque utilisation
- Configurer l'environnement:
`source ./scripts/configure.sh`

- lancer les services:
`./scripts/start.sh`

- [Optionnel] ajouter les dépendances de développement
`uv pip install pytest ipython`

- [Optionnel] (nécessite d'avoir exécuté la précédente commande optionnelle) lancer les tests:
`pytest tests/test_postgres.py `

### Utilisation
- import liste des documents rvl_cdip:
`python dsdc/data/mock.py`

- import d'un jeu d'images iit_cdip:
`python dsdc/import_iit_files.py`

- preprocessing image



## Conventions:
- Les 4 lettres DSDC (pour DataScientest Document Classification) seront utilisées pour préfixe à chaque fois que nécessaire, par exemple pour définir des variables d'nevironnement, des noms de conteneurs, etc.

### Gestion des variables racines
Les variables `DSDC_DIR` (répertoire du projet) et `DSDC_PYTHON` (exécutable Python) sont initialisées selon la priorité suivante, de la plus élevée à la plus faible :

1. **Arguments en ligne de commande (CLI) :**

   - `--project-dir` ou `-d` pour définir `DSDC_DIR`
   - `--python` ou `-p` pour définir `DSDC_PYTHON`

2. **Variables d’environnement (ENV) :**

   - `DSDC_DIR` via la variable d’environnement `DSDC_DIR`
   - `DSDC_PYTHON` via la variable d’environnement `DSDC_PYTHON`

3. **Fichier de configuration (.env) :**

   - Les variables peuvent être définies dans le fichier de configuration `.env`, situé à la racine du projet

4. **Valeurs par défaut (DEFAULT) :**

   - définition de `DSDC_DIR` par recherche du fichier .dsdc_project_root en "remontant" les répertoires depuis le script exécuté et depuis l'emplacement actuel. 
   - `DSDC_PYTHON` par utilisation de `python3`ou de `python`

---

#### Description détaillée

- Lors du lancement, le script analyse les arguments passés en CLI et initialise les variables si présentes.
- À défaut, le script vérifie la présence des variables d’environnement correspondantes.
- Si les variables ne sont pas définies, le script charge les valeurs configurées dans un fichier de configuration, si celui-ci est présent et lisible.
- Enfin, si aucune valeur n’est fournie par les étapes précédentes, les valeurs par défaut sont affectées.

---

#### Exemple d’utilisation CLI


## Structure du repo:

.
├── config.yaml
├── config.yaml.template
├── data
│   ├── processed
│   │   ├── 0
│   │   ├── 1
│   │   ├── [...]
│   │   └── f
│   ├── raw
│   │   ├── 0
│   │   ├── 1
│   │   ├── [...]
│   │   ├── f
│   │   └── rvl_documents.csv
│   └── to_ingest
├── docs
│   └── db_schema.drawio
├── dsdc
│   ├── __init__.py
│   ├── data
│   │   ├── compute_embeddings.py
│   │   ├── extract_text.py
│   │   ├── ingest.py
│   │   ├── mock.py
│   │   ├── process_image.py
│   │   └── process_text.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── crud
│   │   └── models.py
│   ├── models
│   │   ├── clip_mlp.py
│   │   ├── clip.py
│   │   ├── mlp.py
│   │   └── train.py
│   ├── scripts
│   │   └── download_clip.py
│   └── utils
│       ├── config.py
│       └── project_files.py
├── models
│   ├── clip-vit-base
│   │   ├── config.json
│   │   ├── merges.txt
│   │   ├── preprocessor_config.json
│   │   ├── pytorch_model.bin
│   │   ├── special_tokens_map.json
│   │   ├── tokenizer_config.json
│   │   └── vocab.json
│   └── mlps
│       └── test.keras
├── pyproject.toml
├── README.md
├── scripts
│   ├── configure.sh
│   ├── hard_reset.sh
│   ├── initialize.sh
│   ├── loop.sh
│   ├── start.sh
│   └── utils.sh
├── services
│   └── postgres
│       └── scripts
├── tests
│   ├── test_postgres.py
│   └── test_rvl_csv_import.py
├── tmp
└── uv.lock




## Technologies utilisées:

### Environnemen de production
- python3.13
- tous les tests sont réalisés avec pytest
### Environnement de développement
- Environnement de production + ...
- python3.13
- uv