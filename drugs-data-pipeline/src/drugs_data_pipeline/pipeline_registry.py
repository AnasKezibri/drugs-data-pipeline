from kedro.pipeline import Pipeline
from .pipelines.pipeline import create_pipeline

def register_pipelines():
    return {
        "__default__": create_pipeline(),
        "my_pipeline": create_pipeline(),
    }