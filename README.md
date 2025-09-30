# Mlops-Project

## 1. Quick start
### Première installation
- Cloner le repository, dans un dossier dédié:
`git clone --depth=1 git@github.com:alexis64160/Mlops-Project.git .`

- Lancer le script prepare.sh
`./scripts/prepare.sh  `

- Configurer les fichiers .secrets et config.yaml:
`vim .secrets`
`vim config.yaml`

- Exécuter le script install.sh:
`./scripts/install.sh`

- Lancer les services:
`./scripts/start.sh`

- Pour couper les services:
`./scripts/stop.sh`

- Pour réinitialiser le dépot dans son état d'oriigne:
ATTENTION: supprime toutes les données du projet
`./scripts/hard-reset.sh`

### Utilisation
Depuis Airflow, utiliser les différents dags.

## 2. Conventions:
- Les 4 lettres DSDC (pour DataScientest Document Classification) seront utilisées pour préfixe à chaque fois que nécessaire, par exemple pour définir des variables d'nevironnement, des noms de conteneurs, etc.

### Gestion des variables racines
La variable `DSDC_DIR` identifie le répertoire racine du projet. Elle est identifié à l'aide d'un fichier marqueur .dsdc_project_root
**Ne jamais supprimer ce fichier.**

### Fichiers de configuration config.yaml:
Il permet de définir la configuration de l'environnement. Ce fichier ne doit pas être synchronisé sur git.

Il est donc inscrit dans le .gitignore et un template est dynamiquement créé lors de l'exécution du script prepare.sh

### Fichiers de credentials .secret:
Il permet de définir tous les credentials de l'environnement. Ce fichier ne doit absolument pas être synchronisé sur git.

Il est donc inscrit dans le .gitignore et un template est dynamiquement créé lors de l'exécution du script prepare.sh

## 3. Description détaillée

### 3.1 Structure du projet

Le projet suit une architecture modulaire bien organisée, conçue pour assurer la **séparation des responsabilités** entre le code métier, les données, les scripts d’automatisation, les tests, et les services.

```
.
├── config.yaml                  # Fichier de configuration principal (non versionné par défaut)
├── data/                        # Répertoire contenant les données du projet
│   ├── raw/                     # Données brutes en attente de traitement
│   ├── processed/               # Données prétraitées, prêtes à être utilisées
│   ├── rejected/                # Données ayant échoué le prétraitement ou validation
│   └── to_ingest/              # Données en attente d'importation
├── docs/                        # Documentation technique et visuelle (diagrammes, stack, etc.)
├── dsdc/                        # Package principal Python (modules métiers)
│   ├── data/                    # Chargement, validation, exportation de données
│   ├── db/                      # Interfaces et requêtes SQL
│   ├── models/                  # Scripts d'entraînement et d'inférence
│   ├── scripts/                 # Scripts d'orchestration pour Airflow
│   └── utils/                   # Fonctions utilitaires diverses
├── logs/                        # Logs générés par les DAGs Airflow
├── models/                      # Répertoire contenant les artefacts ML (MLflow, checkpoints)
├── scripts/                     # Scripts shell pour gérer le projet (install, start, stop, etc.)
├── services/                    # Services conteneurisés (Airflow, MLflow, Streamlit, etc.)
├── tests/                       # Tests unitaires et d’intégration
├── tmp/                         # Fichiers temporaires
├── todo/                        # Notes de travail ou tâches à faire
├── pyproject.toml               # Dépendances et configuration Python
└── README.md                    # Documentation principale
```

Cette structure permet un déploiement en local ou sur un serveur distant de manière fluide via Docker Compose, tout en gardant un haut niveau de maintenabilité.

---

### 3.2 Stack technique

Le projet s'appuie sur un ensemble de technologies modernes et bien intégrées, couvrant le cycle de vie complet d’un projet de machine learning en production (MLOps).

#### Orchestration et automatisation

- **Apache Airflow** : orchestrateur de workflows, utilisé pour gérer les pipelines de traitement, entraînement et déploiement.
- **Docker Compose** : permet de définir et gérer tous les services nécessaires au projet dans un environnement isolé.

#### Backend et traitement

- **PostgreSQL** : base de données relationnelle utilisée pour stocker les documents, métadonnées, textes extraits, embeddings, etc.
- **FastAPI** : framework web léger pour exposer les endpoints de prédiction, d'authentification, ou de services internes.
- **CLIP (OpenAI)** : modèle de vision/texte utilisé pour générer des embeddings de documents.

#### Machine Learning

- **MLflow** : gestion des expériences, suivi des modèles, gestion des artefacts.
- **PyTorch** : utilisé pour l’entraînement des modèles (via `dsdc.models`).
- **Embeddings** : des vecteurs de dimension 1024 sont générés pour les images et les textes, à l’aide de CLIP, et stockés en base.

#### Frontend & UX

- **Streamlit** : application interactive pour tester les prédictions du modèle en temps réel.

#### Monitoring

- **Prometheus + Grafana** : infrastructure de monitoring des services, de la base de données et des performances.

---

### 3.3 Base de données `dsdc`

La base de données centrale du projet s'appelle `dsdc`. Elle joue un rôle critique dans la traçabilité de bout en bout d’un document : de son importation brute jusqu’à l’inférence du modèle.

> 💡 Le script SQL de création des tables se trouve ici :  
> `services/postgres/init_dbs/init_dsdc.sql`

#### 3.3.1 Vue d'ensemble

La base est structurée de manière **relationnelle** autour de la table `original_documents`, qui sert de point d’entrée pour chaque document.

L’ensemble du pipeline de traitement s'appuie ensuite sur des relations claires entre les différentes entités dérivées du document :

- **Images extraites**
- **Textes bruts et traités**
- **Embeddings**
- **Labels**

---

#### 3.3.2 Description des tables

- **original_documents**  
  Contient les documents bruts importés (PDF, PNG, etc.), leur chemin d'accès, et des métadonnées comme la date d'import.

- **labels**  
  Permet d’associer des annotations humaines ou automatiques à un document. Chaque label est lié à un document via `document_id`.

- **processed_images**  
  Représente les images dérivées des documents (ex : pages d’un PDF converties en PNG). Chaque image est tracée avec le nom du processeur utilisé et la date de traitement.

- **raw_texts**  
  Contient le texte brut extrait d’un document. Le type d’extraction (OCR, parser PDF, etc.) est enregistré.

- **processed_texts**  
  Texte ayant subi un prétraitement (nettoyage, normalisation, etc.) à partir des `raw_texts`.

- **embeddings**  
  Cette table est clé pour les tâches de machine learning. Elle contient les vecteurs numériques (embeddings) associés à une image ou un texte traité. Chaque entrée est associée :
  - à un `processed_image_id` (embedding d’image),
  - ou à un `processed_text_id` (embedding de texte),
  avec la version du modèle CLIP utilisée.

---

#### 3.3.3 Indexation et performance

Des indexes sont définis sur les colonnes les plus couramment utilisées pour les jointures et les requêtes, afin de garantir des performances élevées dans les pipelines et les API.

Par exemple :

- `labels.document_id`  
- `processed_images.document_id`  
- `raw_texts.document_id`  
- `processed_texts.raw_text_id`  
- `embeddings.processed_text_id`  
- `embeddings.processed_image_id`

---

#### 3.3.4 Flux de données dans la base

Voici un exemple de parcours d’un document :

1. Un fichier est placé dans `data/to_ingest/`, puis importé par un DAG Airflow.
2. Il est enregistré dans `original_documents`.
3. Un extracteur génère :
   - des images (enregistrées dans `processed_images`)
   - du texte brut (`raw_texts`)
4. Ce texte est nettoyé et transformé (`processed_texts`).
5. Des embeddings sont calculés (image, texte ou les deux) et stockés dans `embeddings`.
6. Un annotateur (humain ou automatique) fournit des `labels`.

---

#### 3.3.5 Pourquoi une telle structure ?

Cette organisation permet :

- une **traçabilité complète** de chaque étape du pipeline,
- une **modularité** dans les traitements (possibilité de changer de processeur sans casser les relations),
- une **intégration facile avec les modèles ML**, en extrayant à tout moment un batch propre et structuré pour l’entraînement ou la prédiction.

---

#### 3.3.6 Intégration avec MLflow

Les embeddings, labels, et autres métadonnées peuvent être utilisés comme entrées dans un pipeline MLflow pour :

- lancer des expériences,
- tester différents modèles ou prétraitements,
- suivre les performances de manière reproductible.

---

### 3.4 Sécurité et authentification

- Un service **`auth`** basé sur FastAPI permet de gérer les tokens JWT.
- Chaque utilisateur (humain ou service) peut ainsi s’authentifier avant d’accéder à l’API de prédiction.
- La clé secrète JWT est configurable via des variables d’environnement.

---

### 3.5 Déploiement

L’ensemble du projet est conçu pour fonctionner avec :

```bash
./scripts/start.sh
```

Cela lance tous les services via `docker-compose`, monte les volumes nécessaires, initialise la base de données si besoin, et met en route Airflow.

Pour tout redéploiement ou nettoyage :

```bash
./scripts/hard_reset.sh
```

Ce script supprime les conteneurs, volumes temporaires et images Docker locales liées au projet.

---

### 3.6 Observabilité

Un pipeline complet de monitoring est inclus :

- **Prometheus** scrappe les métriques des services et des bases PostgreSQL.
- **Grafana** fournit des dashboards en temps réel.
- Des exporters dédiés permettent de suivre l’usage des bases `dsdc`, `airflow`, et `mlflow`.

---

### 3.7 Environnement de dev

L’environnement Python est défini dans `pyproject.toml`.  
Un environnement virtuel peut être activé avec :

```bash
python -m venv .venv
source .venv/bin/activate
```

Il est recommandé d’utiliser `uv
