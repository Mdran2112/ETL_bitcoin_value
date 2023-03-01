from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from plugins.etl_btc_values import TICKERS, today
from plugins.etl_btc_values.extract import run as run_extract
from plugins.etl_btc_values.load import PostgresInsertFromDataFrameOperator
from plugins.etl_btc_values.transform import run as run_transform

DAG_ID = "etl_flow"
TAGS = [""]
default_args = {
    'owner': 'martín D',
    'start_date': datetime(2022, 1, 1),
}

TABLE_NAME = "btc_value"


def extract(ti):
    raw_dfs = run_extract(tickers=TICKERS, current_day=today())
    ti.xcom_push(key="raw_dfs", value=raw_dfs)
    # return raw_dfs


def transform(ti):
    raw_dfs = ti.xcom_pull(key="raw_dfs", task_ids="extract")
    table = run_transform(raw_dfs)
    ti.xcom_push(key="table", value=table)
    # return table


with DAG(
        DAG_ID,
        start_date=datetime(2021, 1, 1),
        schedule=None,#"@daily", # timedelta(seconds=5),
        default_args={"retries": None},
        catchup=False,
        max_active_runs=1
) as dag:
    extract_raw = PythonOperator(task_id="extract", python_callable=extract)
    transform_to_table = PythonOperator(task_id="transform", python_callable=transform)
    load_to_postgres = PostgresInsertFromDataFrameOperator(task_id="load",
                                                           table_name=TABLE_NAME,
                                                           xcom_task_id="transform",
                                                           xcom_task_id_key="table")

    extract_raw >> transform_to_table >> load_to_postgres
