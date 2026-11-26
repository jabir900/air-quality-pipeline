from datetime import datetime, timedelta
from pathlib import Path

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_DIR = Path.home() / "air-quality-pipeline"
PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="air_quality_pipeline",
    description="Fetch, clean and store Nigerian air quality data daily",
    start_date=datetime(2026, 11, 25),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["air-quality"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON} extract/fetch_all.py",
    )
    transform = BashOperator(
        task_id="transform",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON} transform/transform_all.py",
    )
    load = BashOperator(
        task_id="load",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON} load/load_postgres.py",
    )

    extract >> transform >> load
