from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from kedro.framework.session import KedroSession
from kedro.framework.project import configure_project


class KedroOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        package_name: str,
        pipeline_name: str,
        node_name: str | list[str],
        project_path: str | Path,
        env: str,
        conf_source: str,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.package_name = package_name
        self.pipeline_name = pipeline_name
        self.node_name = node_name
        self.project_path = project_path
        self.env = env
        self.conf_source = conf_source

    def execute(self, context):
        configure_project(self.package_name)
        with KedroSession.create(self.project_path, env=self.env, conf_source=self.conf_source) as session:
            if isinstance(self.node_name, str):
                self.node_name = [self.node_name]
            session.run(self.pipeline_name, node_names=self.node_name)

# Kedro settings required to run your pipeline
env = "airflow"
pipeline_name = "__default__"
project_path = Path.cwd()
package_name = "drugs_data_pipeline"
conf_source = "" or Path.cwd() / "conf"


# Using a DAG context manager, you don't have to specify the dag property of each task
with DAG(
    dag_id="drugs-data-pipeline",
    start_date=datetime(2023,1,1),
    max_active_runs=3,
    # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
    schedule_interval="@once",
    catchup=False,
    # Default settings applied to all tasks
    default_args=dict(
        owner="airflow",
        depends_on_past=False,
        email_on_failure=False,
        email_on_retry=False,
        retries=1,
        retry_delay=timedelta(minutes=5)
    )
) as dag:
    tasks = {
        "clinical-trials-node": KedroOperator(
            task_id="clinical-trials-node",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="clinical_trials_node",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
        "drugs-node": KedroOperator(
            task_id="drugs-node",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="drugs_node",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
        "pubmed-node": KedroOperator(
            task_id="pubmed-node",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="pubmed_node",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
        "transform-to-graph-node": KedroOperator(
            task_id="transform-to-graph-node",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="transform_to_graph_node",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
        "journal-with-most-drugs-node": KedroOperator(
            task_id="journal-with-most-drugs-node",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="journal_with_most_drugs_node",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
        "load-json-node": KedroOperator(
            task_id="load-json-node",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="load_json_node",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
        "adhoc-json-node-1": KedroOperator(
            task_id="adhoc-json-node-1",
            package_name=package_name,
            pipeline_name=pipeline_name,
            node_name="adhoc_json_node_1",
            project_path=project_path,
            env=env,
            conf_source=conf_source,
        ),
    }

    tasks["clinical-trials-node"] >> tasks["transform-to-graph-node"]
    tasks["drugs-node"] >> tasks["transform-to-graph-node"]
    tasks["pubmed-node"] >> tasks["transform-to-graph-node"]
    tasks["transform-to-graph-node"] >> tasks["journal-with-most-drugs-node"]
    tasks["transform-to-graph-node"] >> tasks["load-json-node"]
    tasks["journal-with-most-drugs-node"] >> tasks["adhoc-json-node-1"]
