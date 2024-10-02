import json
import pandas as pd

def load_to_json(output_graph: dict):
	"""Enregistrer le graphe sous forme de fichier JSON."""
	output_filepath = "data/03_output/drugs_journal_liaison_graphe.json"
	with open(output_filepath, 'w') as f:
		json.dump(output_graph, f, ensure_ascii=False, indent=4)
	return output_filepath

def adhoc_to_json(most_mentioned_journal: pd.DataFrame):
    """Retourner les informations du journal qui mentionne le plus de médicaments différents, puis Kedro le charge vers un fichier json"""
    return pd.DataFrame(most_mentioned_journal)