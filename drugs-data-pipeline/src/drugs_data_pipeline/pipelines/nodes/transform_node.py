import pandas as pd
import re
from collections import defaultdict

def drug_mentions(title, drugs):
    """
    Construit une liste des médicaments mentionnés dans un titre.
    
    Arguments:
    title : str
        Le titre a verifier.
    drugs : array
        La liste des noms de médicaments a chercher
    
    Retourne:
    La liste des médicaments mentionnés dans un titre
    """
    mentions = []
    title = title.lower()
    for s, d in drugs.iterrows():
        if re.search(rf"\b{d['drug'].lower()}\b", title):
            mentions.append(d['drug'])
    return mentions

def build_graph(drugs, pubmed, clinical_trials):
    """
    Construit le graphe des relations entre médicaments, publications et journaux.

    Arguments:
    drugs : pd.DataFrame
        Le DataFrame contenant les données des médicaments.
    pubmed : pd.DataFrame
        Le DataFrame contenant les données des publications PubMed.
    clinical_trials : pd.DataFrame
        Le DataFrame contenant les données des publications des essais cliniques.

    Retourne une structure JSON compatible avec une logique Neo4j.
    """
    graphe = {
        "nodes": [],
        "relationships": []
    }
    
    # Dictionnaires pour éviter la duplication des nodes
    drugs_nodes = {}
    journals_nodes = {}
    publications_nodes = {}
    
    # Créer les nodes pour les médicaments
    for s, row in drugs.iterrows():
        drug_id = row['atccode']
        if drug_id not in drugs_nodes:
            drug_node = {
                "id": drug_id,
                "label": "Drug",
                "properties": {
                    "name": row['drug']
                }
            }
            drugs_nodes[drug_id] = drug_node
            graphe['nodes'].append(drug_node)
    
    # Traiter les publications PubMed
    for s, row in pubmed.iterrows():
        mentions = drug_mentions(row['title'], drugs)
        pub_id = row['id']
        
        # Créer un node pour chaque publication
        if pub_id not in publications_nodes:
            publication_node = {
                "id": pub_id,
                "label": "Publication",
                "properties": {
                    "title": row['title'],
                    "article_type": "PubMed",
                    "date": row['date']
                }
            }
            publications_nodes[pub_id] = publication_node
            graphe['nodes'].append(publication_node)
        
        # Créer un node pour chaque journal et établir les relations
        journal_id = f"JID_{row['journal'].replace(' ', '_').lower()}"
        if journal_id not in journals_nodes:
            journal_node = {
                "id": journal_id,
                "label": "Journal",
                "properties": {
                    "name": row['journal']
                }
            }
            journals_nodes[journal_id] = journal_node
            graphe['nodes'].append(journal_node)
        
        # Relation entre la publication et le journal (PUBLISHED_IN) avec date
        graphe['relationships'].append({
            "from": pub_id,
            "to": journal_id,
            "type": "PUBLISHED_IN",
            "properties": {
                "publication_date": row['date']
            }
        })
        
        # Relation entre les médicaments mentionnés et la publication (REFERENCE)
        for drug in mentions:
            drug_id = [key for key, val in drugs_nodes.items() if val['properties']['name'] == drug][0]
            graphe['relationships'].append({
                "from": drug_id,
                "to": pub_id,
                "type": "REFERENCE"
            })
            
            # Relation entre les médicaments mentionnés et le journal (MENTIONED_IN) avec la date
            graphe['relationships'].append({
                "from": drug_id,
                "to": journal_id,
                "type": "MENTIONED_IN",
                "properties": {
                    "mention_date": row['date']
                }
            })

    # Traiter les essais cliniques
    for s, row in clinical_trials.iterrows():
        mentions = drug_mentions(row['scientific_title'], drugs)
        pub_id = row['id']
        
        # Créer un node pour chaque essai clinique
        if pub_id not in publications_nodes:
            publication_node = {
                "id": pub_id,
                "label": "Publication",
                "properties": {
                    "title": row['scientific_title'],
                    "article_type": "Clinical Trials",
                    "date": row['date']
                }
            }
            publications_nodes[pub_id] = publication_node
            graphe['nodes'].append(publication_node)
        
        # Créer un node pour chaque journal et établir les relations
        journal_id = row['journal']
        if journal_id not in journals_nodes:
            journal_node = {
                "id": journal_id,
                "label": "Journal",
                "properties": {
                    "name": row['journal']
                }
            }
            journals_nodes[journal_id] = journal_node
            graphe['nodes'].append(journal_node)
        
        # Relation entre la publication et le journal (PUBLISHED_IN) avec date
        graphe['relationships'].append({
            "from": pub_id,
            "to": journal_id,
            "type": "PUBLISHED_IN",
            "properties": {
                "publication_date": row['date']
            }
        })
        
        # Relation entre les médicaments mentionnés et la publication (REFERENCE)
        for drug in mentions:
            drug_id = [key for key, val in drugs_nodes.items() if val['properties']['name'] == drug][0]
            graphe['relationships'].append({
                "from": drug_id,
                "to": pub_id,
                "type": "REFERENCE"
            })
            
            # Relation entre les médicaments mentionnés et le journal (MENTIONED_IN) avec la date
            graphe['relationships'].append({
                "from": drug_id,
                "to": journal_id,
                "type": "MENTIONED_IN",
                "properties": {
                    "mention_date": row['date']
                }
            })

    return graphe



def transform_to_graph(preprocessed_drugs: pd.DataFrame, preprocessed_pubmed: pd.DataFrame, preprocessed_clinical_trials: pd.DataFrame) -> pd.DataFrame:
    """Transforme les données brutes en un graphe"""
    graphe = build_graph(preprocessed_drugs, preprocessed_pubmed, preprocessed_clinical_trials)
    return graphe

def extract_journal_with_most_drugs(json_data):
    from collections import defaultdict
    nodes = json_data['nodes']
    drug_names = {}
    journal_names = {}

    # Créer un dictionnaire pour associer chaque journal à un ensemble de médicaments uniques
    journal_drugs = defaultdict(set)
    
    # Extraire les nœuds pour obtenir les informations sur les médicaments et les journaux
    for node in nodes:
        if node['label'] == "Drug":
            drug_names[node['id']] = node['properties']['name']
        elif node['label'] == "Journal":
            journal_names[node['id']] = node['properties']['name']
    
    # Extraire les relations pour associer les médicaments aux journaux
    relationships = json_data['relationships']
    
    for rs in relationships:
        if rs['type'] == 'MENTIONED_IN':
            drug_id = rs['from']
            journal_id = rs['to']
            
            # Ajouter le médicament à l'ensemble du journal
            if drug_id in drug_names and journal_id in journal_names:
                journal_drugs[journal_names[journal_id]].add(drug_names[drug_id])

    # Trouver le journal avec le maximum de médicaments mentionnés
    most_mentioning_journal = max(journal_drugs.items(), key=lambda item: len(item[1]), default=(None, None))

    # Structurer la sortie pour ne retourner que le journal avec les médicaments mentionnés
    if most_mentioning_journal[0] is not None:
        return [
            {
                "most_mentioning_journal": most_mentioning_journal[0],
                "mentioned_drugs": list(most_mentioning_journal[1])
            }
        ]
    
    return []  # Retourne une liste vide si aucun journal n'est trouvé
