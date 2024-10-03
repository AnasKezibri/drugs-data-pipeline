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






