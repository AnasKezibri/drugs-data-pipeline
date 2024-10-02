import json
import pandas as pd

def load_to_json(output_graph_nodes: pd.DataFrame, output_graph_relationships: pd.DataFrame):
	"""Enregistrer le graphe sous forme de fichier JSON."""
	return pd.DataFrame(output_graph_nodes), pd.DataFrame(output_graph_relationships)

def adhoc_to_json(most_mentioned_journal: pd.DataFrame):
    """Retourner les informations du journal qui mentionne le plus de médicaments différents, puis Kedro le charge vers un fichier json"""
    return pd.DataFrame(most_mentioned_journal)
