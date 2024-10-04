# Construction d'un graphe de liaison entre médicaments et journaux à l'aide de Python

## table des matières

### Spécifications Détaillées du Data Pipeline

#### [Description fonctionnelle](#description-fonctionnelle)

#### [Description technique](#description-technique)

### Guide d'Installation et d'Exécution du Data Pipeline

#### [Prérequis](#prérequis)

#### [Étapes à suivre](#étapes-à-suivre)


# Spécifications Détaillées du Data Pipeline

## Description fonctionnelle
### L'objectif principal du projet
Construire un data pipeline qui exploite des sources d'information hétérogènes (fichiers CSV et JSON), pour produire un fichier JSON final. Ce fichier JSON est une représentation d'un graphe de liaison entre les médicaments (drugs) et leurs mentions respectives dans les publications scientifiques (PubMed et essais cliniques), ainsi que dans les journaux associés à ces publications. Le fichier de sortie doit lier :
* Les médicaments (définis dans le fichier drugs.csv)
* Les publications PubMed (pubmed.csv et pubmed.json) et les essais cliniques (clinical_trials.csv)
* Les journaux scientifiques associés à ces publications

### Règles de gestion :
* Un médicament est considéré comme mentionné dans un article PubMed ou un essai clinique s'il est cité dans le titre de la publication.
* Un médicament est considéré comme mentionné par un journal s'il apparaît dans une publication émise par ce journal.

L'objectif final est donc de permettre une visualisation des liens entre les médicaments et les journaux où ils sont mentionnés, en tenant compte des dates de publication. Ensuite, on exploite ce graphe de liaisons, pour pouvoir établir une analyse ad-hoc pour définir le journal qui mentionne le plus de médicaments différents.

## Description technique

### Pipeline de données
Le pipeline de données suit les étapes d'un ETL :
##### Collecte et ingestion des données (Extract)
Récupération des données à partir des fichiers sources (drugs.csv, pubmed.csv, pubmed.json, clinical_trials.csv).
Les données sont standardisées et chargées dans un format unifié : Pandas DataFrame.
##### Nettoyage des données (Preprocess)
Implique des étapes comme :
*  le traitement des valeurs manquantes. Dans mon cas j'ai écarté les lignes comprenant des valeurs vides. Cependant dans un projet où on a des retours client réguliers, il vaut mieux de favoriser un complétude de données et demandé des règles de gestion pour garder lignes de données présentants des valeurs manquantes.
*  La normalisation des formats de date et des types des colonnes (Lire toutes les colonnes en string).
*  Le nettoyage des titres. Par exemple : supprimer les encodages mal formés d'une chaîne de caractères, écarter les titres contenant que des éspaces.
##### Transformation et Consolidation des données (Transform)
* Tokenisation des titres : Identifier les mentions des médicaments dans les titres des publications. Cela nécessite de comparer les titres avec les noms de médicaments pour détecter des correspondances.
* Construction d'une table d'association entre les médicaments, les journaux, les dates et les types de publications (PubMed ou Clinical Trials).
* Création d'un graphe de relations entre médicaments et journaux, avec les dates associées. L'idée est de modéliser les entités (médicaments, publications, journaux) sous forme de nœuds et leurs interactions comme des relations dans le graphe. Pour atteindre cette modélisation, j'ai opté pour une sortie sous forme d'un fichier JSON qui suit une logique de graphe compatible avec Neo4j (un système de gestion de base de données orienté graphes, cf. fichier pdf pour plus de détails sur le fichier JSON de sortie). Le résultat final permet de représenter les relations entre les médicaments et leurs mentions respectives dans les publications scientifiques , ainsi que dans les journaux associés à ces publications.
##### Sortie du fichier final (Load)
Génération d'un fichier JSON qui présente une structure représentant les relations entre les médicaments et leurs mentions dans les publications et les journaux, avec les métadonnées correspondantes (date, type de publication).

### Organisation technique des fichiers du projet
Dans cette partie, on va détailler les dossiers principaux du projet Python qui refléte la logique du pipeline décrite dans la partie précédente, ainsi que les autres éléments nécessaire pour géré le packaging, la dockirisation et l'orchestration du projet Python.
```
my_kedro_project/
├──.vis/
├──conf/
├──dags/
├──data/
   ├──01_raw
   ├──02_intermediate
   ├──03_output
├──dist/
├── notebooks/
├── src/
   ├──drugs_data_pipeline/
      ├──pipelines/
         ├──nodes/
├── Dockerfile
└── requirements.txt
```
#### 1. Répertoire conf/
Ce répertoire contient les fichiers de configuration pour différents environnements (développement, production). Les paramètres liés aux datasets et aux connexions aux différentes sources de données sont définis ici.
Le fichier conf/base/catalog.yml permet la gestion des datasets. Ce fichier définit tous les jeux de données (datasets) que le pipeline va utiliser ou générer au cours de son exécution. Il permet de décrire comment et où les données doivent être chargées (input) et sauvegardées (output), ainsi que les formats et types de fichiers associés.
Par exemple, pour charger le fichier drugs.csv, on définit le format cible pour charger les données drugs, et le chemin du fichier source :
```
drugs:
  type: pandas.CSVDataset
  filepath: data/01_raw/drugs.csv
```

##### 2. Répertoire dags/
Le dossier /dags est utilisé pour stocker les DAGs (Directed Acyclic Graphs), c’est-à-dire les définitions des pipelines de tâches (ou "jobs") à exécuter, permettant ainsi l'orchestration et l'exécution automatisée des pipelines de données. On utilise ce fichier dans le projet Airflow sous le dossier airflow-drugs-data-pipeline pour exécuter le pipeline.

##### 3. Répertoire data/
Le dossier /data est subdivisé en plusieurs sous-dossiers, chacun correspondant à un stade particulier dans le cycle de vie des données.
* data/01_raw/ : contient les données brutes d'entrée (non transformées) à ingérez dans le pipeline.
* data/02_intermediate/ : contient les données nettoyées, mais qui ne sont pas encore sous leur forme finale.
* data/03_output/ : contient les données finales qui ont été transformées et sont prêtes à être utilisées dans des analyses. Trois fichiers JSON y sont disponibles :
  - graph_nodes.json : les nœuds du graphe de liaison,
  - graph_relationships.json : les relations entre ces nœuds,
  - traitement_adhoc_1.json : l'analyse ad-hoc pour trouver le journal qui mentionne le plus de médicaments différents.
##### 4. Répertoire dist/
Le dossier /dist est utilisé pour contenir les artefacts du projet, c'est-à-dire le projet sous forme de bibliothèque Python. On y trouve le fichier drugs_data_pipeline-0.1-py3-none-any.whl qui va nous servir par la suite pour déployer le pipeline sous forme d’un package Python réutilisable dans le projet Airflow airflow-drugs-data-pipeline.

##### 5. Répertoire src/
Le dossier /src est dédié au code source du projet. Il contient la logique métier du es pipeline, les interfaces d’entrée et de sortie et le traitement de données.
Il comporte deux éléments principales :
* Les fichiers nodes.py utilisés pour définir les nœuds du pipeline. Les nœuds représentent des unités de traitement distinctes qui effectuent des transformations ou des analyses sur les données.
  - extract_node.py : Extraction et préparation des données.
  - transform_node.py : Tockenisation des titres, construction d'une table d'association entre les médicaments, les journaux et les publications, puis ensuite contruire le graphe de liaison. On a aussi une fonction pour établir une analyse ad-hoc.
  - load_node.py : Chargement des données vers des fichiers JSON.

En définissant des nœuds séparément, on peut réutiliser ces fonctions dans différents pipelines ou d'autres parties du projet. Cela favorise la réutilisabilité et la modularité du code.
* Le fichier pipeline.py intègre les entrées et sorties des nœuds, permettant ainsi de structurer le traitement des données de manière cohérente. Il fait appel aux datasets définits dans le fichier conf/base/catalog.yml pour gérer ces données d'entrée et de sortie.

# Guide d'Installation et d'Exécution du Data Pipeline

## Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés sur votre machine :

1. **Git** :
   - [Installer Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
   
2. **Docker** :
   - [Installer Docker](https://docs.docker.com/get-docker/)

3. **Astronomer (Astro CLI)** :
   - [Installer Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli)

## Étapes à suivre

### 1. Cloner le dépôt Git
Ouvrez un terminal Git Bash, choisissez un emplacement pour mettre le proejt, puis exécutez la commande suivante pour cloner le projet :
```
git clone https://github.com/AnasKezibri/drugs-data-pipeline.git
```

### 2. Accéder au répertoire Airflow du projet
```
cd drugs-data-pipeline/airflow-drugs-data-pipeline
```

### 3. Construire l'image Docker du data pipeline et Airflow
```
astro dev start
```

### 4. Accéder à Airflow
Vous pouvez maintenant accéder à l'interface web d'Airflow à l'adresse suivante : http://localhost:8080 (User : admin, password : admin), puis déclencher le DAG drugs-data-pipeline.

### 5. Accéder aux résultats du data pipeline
Les fichiers JSON de sortie sont disponible dans le conteneur Docker du Scheduler d'Airflow, dans le dossier /data/03_output.
Pour y accéder, lister les conteneur Docker pour récupérer le nom exacte du conteneur ensuite il faut l'ouvrir et lire les fichiers JSON.
Voici la suite des commandes à suivre pour vérifier les fichiers JSON générés après l'exécution du DAG :
```
docker ps
docker exec -it airflow-drugs-data-pipeline_99e5fd-scheduler-1 /bin/bash
cd data/03_output
ls -l
```






