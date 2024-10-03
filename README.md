# Guide d'Installation et d'Exécution du Data Pipeline

## Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés sur votre machine :

1. **Docker** :
   - [Installer Docker](https://docs.docker.com/get-docker/)

2. **Astro CLI** :
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

### 3. Construire l'image Docker du data pipeline ainsi que Airflow à l'aide d'Astronomer
```
astro dev start
```

### 4. Accéder à Airflow
Vous pouvez maintenant accéder à l'interface web d'Airflow à l'adresse suivante : http://localhost:8080 (User : admin, password : admin), puis déclencher le DAG drugs-data-pipeline.
Les fichiers json de sortie sont disponible sous le dossier drugs-data-pipeline/airflow-drugs-data-pipeline/data/03_output.






