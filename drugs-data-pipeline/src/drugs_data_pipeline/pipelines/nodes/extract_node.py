import pandas as pd
import numpy as np
import re

def remove_malformed_encoding(text):
    """
    Supprime les encodages mal formés d'une chaîne de caractères.
    
    Arguments:
    text : str
        La chaîne de caractères à traiter.

    Retourne:
    str
        La chaîne de caractères sans les encodages mal formés.
    """
    if isinstance(text, str):
        return re.sub(r'\\x[0-9a-fA-F]{2}', '', text)
    return text

def extract_preprocess_drugs(drugs: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait et prétraite un DataFrame de médicaments.
    
    Arguments:
    drugs : pd.DataFrame
        Le DataFrame contenant les informations sur les médicaments.
    
    Retourne:
    pd.DataFrame
        Le DataFrame nettoyé des médicaments sans valeurs manquantes.
    """
    drugs.replace('', np.nan, inplace=True)
    drugs = drugs.dropna(how='any')

    return drugs

def extract_preprocess_pubmed(pubmed_csv: pd.DataFrame, pubmed_json: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait, concaténe et prétraite des données de PubMed à partir de fichiers CSV et JSON.
    
    Arguments:
    pubmed_csv : pd.DataFrame
        Le DataFrame contenant les données extraites d'un fichier CSV.
    pubmed_json : pd.DataFrame
        Le DataFrame contenant les données extraites d'un fichier JSON.
    
    Retourne:
    pd.DataFrame
        Le DataFrame combiné et nettoyé des données de PubMed.
    """
    pubmed_csv['id'] = pubmed_csv['id'].astype(str)
    pubmed_json['id'] = pubmed_json['id'].astype(str)

    pubmed = pd.concat([pubmed_csv, pubmed_json], ignore_index=True)

    pubmed.replace('', np.nan, inplace=True)
    pubmed = pubmed.dropna(how='any')

    pubmed['date'] = pd.to_datetime(pubmed['date'], dayfirst=True, errors='coerce')

    pubmed['date'] = pubmed['date'].dt.strftime('%d-%m-%Y')

    return pubmed

def extract_preprocess_clinical_trials(clinical_trials: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait et prétraite un DataFrame d'essais cliniques.
    
    Arguments:
    clinical_trials : pd.DataFrame
        Le DataFrame contenant les informations sur les essais cliniques.
    
    Retourne:
    pd.DataFrame
        Le DataFrame nettoyé des essais cliniques, sans valeurs manquantes et avec des dates formatées.
    """
    clinical_trials.replace('', np.nan, inplace=True)
    clinical_trials = clinical_trials.dropna(how='any')

    clinical_trials = clinical_trials[clinical_trials['scientific_title'].str.strip() != '']

    clinical_trials = clinical_trials.applymap(remove_malformed_encoding)
    
    clinical_trials['date'] = pd.to_datetime(clinical_trials['date'], dayfirst=True, errors='coerce')

    clinical_trials['date'] = clinical_trials['date'].dt.strftime('%d-%m-%Y')
    
    return clinical_trials
