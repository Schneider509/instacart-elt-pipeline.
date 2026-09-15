# Pipeline ELT Instacart (Snowflake & dbt)


![CI dbt Validation](https://github.com/Schneider509/instacart-elt-pipeline./actions/workflows/ci.yml/badge.svg)

Ce projet met en œuvre un pipeline moderne d'extraction, chargement et transformation (ELT) basé sur le jeu de données public d'Instacart (3 millions de commandes e-commerce). L'objectif est d'ingérer les fichiers sources bruts dans **Snowflake**, puis de modéliser les données à l'aide de **dbt** selon une architecture dimensionnelle en étoile pour alimenter des cas d'usage analytiques et décisionnels.

---

## Architecture globale

```text
Données Kaggle (CSV)
        │
        ▼  [Ingestion optimisée en Python via snowflake-connector]
Snowflake : INSTACART_RAW (Tables brutes)
        │
        ▼  [dbt - Couche Staging (Vues)]
Snowflake : DEV_STAGING (Nettoyage, typage strict, standardisation)
        │
        ▼  [dbt - Couche Marts (Tables)]
Snowflake : DEV_MARTS (Schéma en étoile : faits et dimensions)
```

---

## Modélisation des données

Le projet applique les principes de modélisation dimensionnelle de Kimball au sein du dossier `instacart_dbt/models` :

### 1. Couche Staging (`models/staging/`)
Préparation des tables sources sous forme de vues sans transformation métier lourde :
* `stg_orders` : Historique des commandes (utilisateur, évaluation temporelle, jour et heure).
* `stg_order_products` : Lignes d'articles par commande (ordre d'ajout dans le panier, statut de réachat).
* `stg_products` : Référentiel des articles.
* `stg_aisles` : Référentiel des rayons.
* `stg_departments` : Référentiel des départements.

### 2. Couche Marts (`models/marts/`)
Tables matérialisées optimisées pour les requêtes décisionnelles et les outils de BI :
* **`dim_products` (Dimension)** : Jointure unifiée de l'article, de son département et de son rayon.
* **`fct_orders` (Fait)** : Modélisation granulaire de l'activité d'achat reliant les métriques de commande et le comportement client.

---

## Qualité des données et tests

La robustesse du pipeline est assurée par une série de tests automatisés dbt (`marts.yml` et `sources.yml`) :
* **Unicité (`unique`)** sur les clés primaires (`order_id`, `product_id`).
* **Complétude (`not_null`)** sur l'ensemble des colonnes stratégiques et clés de jointure.
* **Intégrité référentielle (`relationships`)** pour garantir la cohérence des clés étrangères entre faits et dimensions.

---

## Structure du dépôt

```text
instacart_pipeline/
├── ingest_instacart.py       # Script d'ingestion des CSV vers Snowflake
├── requirements.txt          # Dépendances Python du projet
├── .gitignore                # Exclusion des secrets et données volumineuses
├── README.md                 # Documentation du projet
└── instacart_dbt/            # Répertoire principal du projet dbt
    ├── dbt_project.yml       # Configuration du projet dbt
    ├── packages.yml          # Dépendances de packages dbt
    ├── macros/               # Macros dbt personnalisées
    └── models/
        ├── staging/          # Vues de préparation
        └── marts/            # Schéma en étoile (faits et dimensions)
```

---

## Guide de reproduction locale

### 1. Prérequis
* Python 3.10 ou supérieur
* Un compte d'essai actif Snowflake
* Les données sources Kaggle téléchargées localement

### 2. Installation de l'environnement

```bash
# Cloner le dépôt
git clone [https://github.com/Schneider509/instacart-elt-pipeline..git](https://github.com/Schneider509/instacart-elt-pipeline..git)
cd instacart-elt-pipeline.

# Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Ingestion des données brutes dans Snowflake

Configurer vos variables de connexion Snowflake dans votre environnement ou dans le script, puis lancer le chargement des tables sources :

```bash
python ingest_instacart.py
```

### 4. Configuration et exécution de dbt

Assurez-vous que votre fichier `~/.dbt/profiles.yml` contient les identifiants nécessaires pour cibler votre entrepôt et base de données Snowflake :

```bash
cd instacart_dbt

# Installer les dépendances dbt
dbt deps

# Compiler les modèles et exécuter l'ensemble des transformations et tests
dbt build

# Générer et consulter la documentation interactive ainsi que le lignage (DAG)
dbt docs generate
dbt docs serve
```