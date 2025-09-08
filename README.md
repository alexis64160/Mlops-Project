# Mlops-Project

## Quick start
### Première installation
- Créer un fichier env personalisé:
`cp .env.template .env`

- puis éditer le fichier .env
`vim .env`

Exécuter le fichier scripts/initialize.sh:
`./scripts/initialize.sh`

### Configuration lors d'une utilisation régulière
Sourcer le fichier setup.sh



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

3. **Fichier de configuration (CONFIG) :**

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

```bash
./initialize.sh --project-dir /path/to/project --python /usr/bin/python3.13



## Technologies utilisées:

### Environnemen de production
- python3.13
- tous les tests sont réalisés avec pytest
### Environnement de développement
- Environnement de production + ...
- python3.13
- uv