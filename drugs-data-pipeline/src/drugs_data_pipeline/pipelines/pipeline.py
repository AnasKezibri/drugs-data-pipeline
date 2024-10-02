from kedro.pipeline import Pipeline, node, pipeline
from .nodes.extract_node import extract_preprocess_drugs, extract_preprocess_pubmed, extract_preprocess_clinical_trials
from .nodes.transform_node import transform_to_graph, extract_journal_with_most_drugs
from .nodes.load_node import load_to_json, adhoc_to_json

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=extract_preprocess_drugs,
                inputs="drugs",
                outputs="preprocessed_drugs",
                name="drugs_node",
            ),
            node(
                func=extract_preprocess_pubmed,
                inputs=["pubmed_csv", "pubmed_json"],
                outputs="preprocessed_pubmed",
                name="pubmed_node",
            ),
            node(
                func=extract_preprocess_clinical_trials,
                inputs="clinical_trials",
                outputs="preprocessed_clinical_trials",
                name="clinical_trials_node",
            ),
            node(
                func=transform_to_graph,
                inputs=["preprocessed_drugs", "preprocessed_pubmed", "preprocessed_clinical_trials"],
                outputs="output_graph",
                name="transform_to_graph_node",
            ),
            node(
                func=extract_journal_with_most_drugs,
                inputs="output_graph",
                outputs="most_mentioning_journal",
                name="journal_with_most_drugs_node",
            ),
            node(
                func=load_to_json,
                inputs="output_graph",
                outputs="output_filepath",
                name="load_json_node",
            ),
            node(
                func=adhoc_to_json,
                inputs="most_mentioning_journal", 
                outputs="adhoc_json_1",
                name="adhoc_json_node_1",
            )
        ]
    )